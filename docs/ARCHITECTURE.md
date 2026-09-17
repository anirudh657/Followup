# ActionFlow — Architecture

**Status:** Draft v1 · **Owners:** Anirudh, Vedant · **Last updated:** 2026-09-17

---

## 1. Components at a glance

| Component | Tech | Hosted on | Responsibility |
|---|---|---|---|
| `apps/web` | Next.js + Tailwind + shadcn/ui | Vercel | All UI; thin API routes (session-scoped reads, signed-URL issuance, proxying to the pipeline with the user's JWT). **No LLM, transcript, or integration logic.** |
| `services/pipeline` | Python / FastAPI | Railway | Everything heavy: ingestion, STT, LLM extraction, integration adapters, sync, follow-up scheduling, report generation, Stripe webhooks. |
| Database + Auth + Storage | Supabase (Postgres, GoTrue, Storage) | Supabase | Single source of truth. Auth (magic link + Google), Postgres with **RLS**, file storage for uploads. |
| Job queue | Postgres tables (`jobs`, `jobs_dead_letter`) polled by the pipeline worker | Supabase + Railway | Async work: transcription, extraction, sync pushes, follow-ups, reports. No Redis/Celery on the free tier — plain Postgres `SELECT … FOR UPDATE SKIP LOCKED`. |
| External | Zoom / Google / Teams, Notion / Linear / Jira / Asana / Todoist, AssemblyAI / Deepgram, Anthropic / OpenAI / Groq, Stripe, email (Resend free tier) | — | Sources, destinations, models, money, messages. |

Monorepo layout is described in the README; the two deployables are `apps/web` and
`services/pipeline`, deployed independently.

## 2. System diagram

```
                 ┌────────────────────────────────────────────────────────────┐
                 │                        Browser                             │
                 └───────────────┬────────────────────────────────────────────┘
                                 │ HTTPS (Supabase JWT in Authorization header)
                 ┌───────────────▼───────────────┐
                 │        apps/web (Vercel)      │
                 │  Next.js UI + thin API routes │
                 └──────┬──────────────┬─────────┘
        supabase-js     │              │  REST, forwards user JWT
        (reads via RLS) │              │
     ┌──────────────────▼───┐   ┌──────▼──────────────────────────────┐
     │  Supabase            │   │   services/pipeline (Railway)       │
     │  ┌────────────────┐  │   │   FastAPI  +  worker process        │
     │  │ Postgres (RLS) │◄─┼───┼── service-role client (writes,      │
     │  ├────────────────┤  │   │   job claiming, cross-row work)     │
     │  │ Auth (GoTrue)  │  │   │                                     │
     │  ├────────────────┤  │   │  ingestion → extraction → sync      │
     │  │ Storage        │◄─┼───┼─ followups • reports • billing      │
     │  └────────────────┘  │   └──┬────────┬─────────┬──────────┬────┘
     └──────────────────────┘      │        │         │          │
                                   ▼        ▼         ▼          ▼
                              STT APIs   LLM APIs  Tool APIs   Stripe
                             (Assembly/ (Claude/  (Notion,     (billing
                              Deepgram/  GPT/      Linear,      webhooks)
                              Whisper)   Groq)     Jira, …)
                                   ▲                   ▲
                                   │ webhooks          │ webhooks
                              Zoom/Meet/Teams     status changes
```

## 3. The Next.js ↔ Python boundary

**Rule: if it touches an LLM, a transcript, or an external tool API, it lives in the
Python service.** Next.js renders UI and performs only session-scoped reads/writes that
RLS can fully protect.

Concretely:

- The browser talks to Supabase directly (via `supabase-js`) for **reads** of its own
  org's data — meetings list, task board, report list. RLS makes this safe.
- Anything that *does work* — "process this upload", "re-run extraction", "push to Linear",
  "send follow-ups now" — goes `browser → Next.js API route → pipeline REST endpoint`.
  The API route is a thin proxy: it attaches the user's Supabase JWT and the target org id,
  and never contains business logic. (Proxying rather than calling Railway from the browser
  keeps the pipeline URL non-public and lets us swap hosts without a frontend deploy.)
- The pipeline **verifies the Supabase JWT** (JWKS from the Supabase project) on every
  request, resolves the caller's membership/role in the claimed org, and only then acts.
  It uses the service-role key for DB access, so *it* is responsible for scoping every
  query by `org_id` — see §5.
- External webhooks (Zoom, Stripe, Linear, …) land **directly on the pipeline**
  (`/webhooks/*`), never on Next.js. Each is signature-verified per provider and recorded
  in `webhook_events` for idempotency (§6).
- Long work is asynchronous: the HTTP endpoint validates, enqueues a job, returns `202`
  with a job id; the UI subscribes to job/meeting status via Supabase Realtime. No request
  ever blocks on an LLM call.

Shared contract: the pipeline's OpenAPI schema is exported to
`apps/web/lib/pipeline-types.ts` by a codegen script (`make types`), so the two sides
can't silently drift.

## 4. The two core paths

### 4.1 Ingestion path (recording/transcript → reviewed action items)

1. **Acquire.** One of:
   - Upload: browser gets a signed Storage URL from a Next.js route, uploads directly to
     Supabase Storage, then notifies the pipeline (`POST /meetings/{id}/ingest`).
   - Platform webhook: Zoom `recording.completed` (etc.) hits `/webhooks/zoom`; the pipeline
     downloads the native transcript (preferred) or the media file.
2. **Transcribe if needed.** Media without a transcript goes to the configured STT provider
   (job type `transcribe`). Native transcripts skip this.
3. **Normalise.** Every source becomes the internal `Transcript` model: ordered `Utterance`s
   (speaker, start/end ms, text) + metadata (source, language, duration). Garbage detection
   (FR-1.7) happens here: too short, no speech, unsupported language → meeting enters
   `failed` state with a user-readable reason. **Nothing downstream ever sees a raw vendor format.**
4. **Extract.** Job type `extract`: chunk the transcript (long meetings), call the LLM with
   a strict JSON schema (tool-use / structured output mode), validate the response against
   the same Pydantic schema, repair-or-retry on validation failure (§6), merge chunk results,
   dedupe, score confidence.
5. **Review.** Items land as `status=suggested`. The user edits/merges/approves in the UI
   (writes via Next.js routes → pipeline, which enforces role ≥ member). Approval is the
   gate to the sync path — un-reviewed items never leave ActionFlow.

### 4.2 Sync path (approved items ⇄ external tools)

Outbound:
1. User picks a destination (built-in board or a connected integration) and clicks push.
2. Pipeline enqueues one `sync_push` job per item with an **idempotency key**
   `(org_id, action_item_id, destination)` — stored in `external_task_links`.
3. The adapter (common interface, per-tool implementation — `integrations/base.py`) creates
   the external task, and the external id + URL are stored on the link row. A retry after a
   crash finds the link row (or, on create-timeout, searches by the idempotency marker the
   adapter embeds where the tool allows it) instead of creating a duplicate.

Inbound:
4. Status comes back via provider webhooks where offered (Linear, Asana), else scheduled
   polling (job type `sync_poll`, per-integration interval, batched).
5. Inbound changes update the ActionFlow task; conflicts (edited both sides) resolve
   **external-wins for status, ActionFlow-wins for content**, recorded in `sync_audit` —
   rationale: the external tool is where execution happens; ActionFlow is where meaning was defined.
6. Follow-ups and reports read only ActionFlow's task state, so they work identically for
   built-in-board users and integration users.

## 5. Multi-tenancy & per-org isolation

- **Tenant model:** `orgs → org_members (user_id, role) → projects → meetings / action_items /
  integrations / reports / status_pages`. Every tenant-owned table carries a **non-null
  `org_id`** (denormalised even where derivable, so RLS never needs joins).
- **Layer 1 — Postgres RLS (browser path).** RLS is enabled on every tenant table. The
  policy pattern: `org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())`,
  with write policies additionally checking role. The browser only ever holds an anon/JWT
  client, so even a frontend bug cannot cross tenants.
- **Layer 2 — service scoping (pipeline path).** The pipeline uses the service-role key
  (bypasses RLS by design — it must claim jobs across orgs). Discipline is structural, not
  by convention: all DB access goes through a `TenantScopedRepo` constructed from the
  verified request context; raw-client access outside it is confined to the job runner and
  webhook intake. CI greps for naked service-client usage outside those modules.
- **Layer 3 — storage.** Storage objects live under `org/{org_id}/…` with Storage RLS
  policies mirroring the table policies; the pipeline issues only short-lived signed URLs.
- **Secrets.** Integration OAuth tokens are encrypted app-side (Fernet, key in Railway env,
  not in the DB) before insert; the browser can never read the `integrations.credentials`
  column (column-level privilege revoked from `anon`/`authenticated`).
- **Public status pages** are the one deliberate hole: a tokenised endpoint on the pipeline
  serves a read-only, field-filtered projection for exactly one project; tokens are random
  (≥128-bit), revocable rows, rate-limited.
- **Tests:** a standing integration test suite creates two orgs and asserts every list/read/
  write endpoint and every RLS policy returns nothing across the boundary. Runs in CI.

## 6. Failure modes

| Failure | Detection | Behaviour | User sees | Ops sees |
|---|---|---|---|---|
| **Garbage transcript** (empty, music-only, wrong language, OCR junk) | Normalisation heuristics: min utterance count, speech-ratio, language id | Meeting → `failed(reason)`. No LLM call is made (cost guard). Upload retained so the user can retry with a different file. | "We couldn't find usable speech in this recording" + specific reason + retry/upload-again | Counter metric per reason; spike alerts |
| **Expired / revoked integration token** | Adapter health-check before batch; 401/403 on call; refresh-token failure | Integration → `needs_reauth`. Pending sync jobs for it are **parked** (not failed, not retried) and auto-resume after re-auth. Nothing is dropped. | Banner + email: "Reconnect Linear to resume syncing 4 queued items", one-click re-auth | Parked-job gauge per integration |
| **Malformed LLM output** (invalid JSON, schema violation, hallucinated fields) | Pydantic validation of every response; never parsed by hand | (1) one repair pass (send validation errors back to the model), (2) one retry with stricter prompt + lower temperature, (3) fall back to secondary model, (4) meeting → `extraction_failed`, raw response archived for prompt debugging | Rare: "Extraction hit a snag, we've retried — tap to run again" | Validation-failure rate per model/prompt version; the archived payloads feed the eval set |
| **Duplicate webhook delivery** (all providers redeliver; Stripe and Zoom explicitly) | `webhook_events` table keyed on `(provider, event_id)` unique index; insert-first, process-second | Insert conflict → acknowledge `200` immediately, do nothing. Handlers are also *semantically* idempotent (upserts keyed on external ids) as defence in depth for providers with unstable event ids. | Nothing (that's the point) | Dupe-rate metric per provider |
| **LLM/STT provider outage or rate limit** (bonus) | Timeouts, 429/5xx | Exponential backoff with jitter; job returns to queue with attempt count; after N attempts → dead letter + alert | Meeting stays "processing" with an honest "taking longer than usual" state | Dead-letter depth alert |
| **Pipeline crash mid-job** (bonus) | Job lease timeout (`claimed_at` + TTL) | `SKIP LOCKED` claiming + lease expiry returns the job to the queue; all job handlers are written to be re-runnable (idempotency keys as in §4.2) | Nothing | Lease-expiry counter |

## 7. Deliberate choices & trade-offs

- **Postgres-as-queue** instead of Redis/Celery: one less service, free, transactional with
  our data. Revisit only if job throughput or scheduling precision demands it.
- **One external adapter in MVP** (plus built-in board): breadth of integrations is the #1
  scope risk; the adapter interface is the investment, tool N is repetition.
- **Pipeline verifies JWTs itself** rather than trusting Next.js: the pipeline is reachable
  by webhooks anyway, so it must have its own auth story; two trust domains, one enforcement point each.
- **Denormalised `org_id` everywhere**: minor write-side redundancy for radically simpler
  RLS and audits.
