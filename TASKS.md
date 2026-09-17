# ActionFlow — Task Board

**Conventions**

| Mark | Meaning |
|---|---|
| `[ ]` | not started |
| `[~]` | in progress |
| `[x]` | done |
| `[!]` | blocked — always add the reason in the Notes column |

The **Owner** column is intentionally blank everywhere. Anirudh and Vedant assign tasks
manually once full scope is visible; a task without an owner is unclaimed, not forgotten.
FR/NFR references point into [docs/PRD.md](docs/PRD.md).

---

## Phase 0 — Foundations

| St | Task | Owner | Notes |
|---|---|---|---|
| [ ] | Create private GitHub repo, protect `main`, require PR + 1 review | | Commands in README §Repo setup |
| [ ] | Create Supabase project (free tier); note URL, anon key, service key | | |
| [ ] | Write initial SQL migration: `orgs`, `org_members`, `projects`, `profiles` | | Migrations in `supabase/migrations/` via Supabase CLI |
| [ ] | Enable + write RLS policies for the above tables (member-read, role-gated write) | | FR-7.5 |
| [ ] | Two-org RLS isolation test (SQL-level) wired into CI | | The Phase 0 exit gate |
| [ ] | Supabase Auth: magic link + Google OAuth in `apps/web` | | FR-7.1 |
| [ ] | Org create/switch UI + `org_members` bootstrap on signup | | FR-7.2 |
| [ ] | Pipeline: FastAPI skeleton, `/healthz`, structured logging | | |
| [ ] | Pipeline: Supabase JWT verification middleware (JWKS) + org-membership resolution | | ARCH §3 |
| [ ] | Next.js API route proxy → pipeline with JWT forwarding | | ARCH §3 |
| [ ] | `docker-compose up` gives a full local stack (web, pipeline, supabase local) | | |
| [ ] | CI: lint + type-check + test for both services on every PR | | Workflow exists; make it pass on real code |
| [ ] | Deploy `apps/web` to Vercel (hobby) with env vars | | ⚠ Vercel hobby is non-commercial; see README §Costs |
| [ ] | Deploy `services/pipeline` to Railway with env vars | | ⚠ Railway trial credit is limited; see README §Costs |
| [ ] | Sentry (free) wired into both services | | NFR-7 |
| [ ] | Decide + document environments (local / preview / prod) in CONTRIBUTING | | |

## Phase 1 — Core loop, single-player

| St | Task | Owner | Notes |
|---|---|---|---|
| [ ] | Schema migration: `meetings`, `transcripts`, `utterances`, `action_items`, `decisions`, `open_questions`, `jobs`, `jobs_dead_letter` (+ RLS) | | |
| [ ] | Signed-URL upload flow (browser → Supabase Storage) with org-scoped paths | | ARCH §5 layer 3 |
| [ ] | Transcript file parsers: plain text, VTT, SRT, common JSON exports | | FR-1.1 |
| [ ] | Normaliser → internal `Transcript`/`Utterance` model | | FR-1.6; model is implemented, wire it |
| [ ] | Garbage detection (empty / no-speech / language / size) with reason codes | | FR-1.7, failure table row 1 |
| [ ] | Job queue on Postgres (`SKIP LOCKED`, lease TTL, dead letter) + worker loop | | ARCH §1 |
| [ ] | STT interface + one provider (decide OQ-6: AssemblyAI vs Deepgram vs Whisper) | | FR-1.2 ⚠ free credits are capped |
| [ ] | Benchmark STT candidates on 5 real recordings, record decision in PRD OQ-6 | | |
| [ ] | LLM client wrapper: provider-agnostic, structured-output mode, token/cost accounting per org | | NFR-5 |
| [ ] | Extraction prompt + strict schema (items, owners, dates, decisions, open questions, per-item confidence + source quote) | | FR-2.1, FR-2.2 |
| [ ] | Validation → repair pass → retry → fallback model → `extraction_failed` chain | | Failure table row 3 |
| [ ] | Chunking for long transcripts + merge/dedupe of chunk results | | |
| [ ] | Speaker → org-member owner suggestion (exact/fuzzy name match, else free-text) | | FR-2.3 |
| [ ] | Confidence thresholds → review flags (tune on eval set) | | FR-2.2 |
| [ ] | Build labelled eval set: ≥ 25 real transcripts with human-marked items | | NFR-6; use our own meetings + public data |
| [ ] | Eval harness: precision/recall vs eval set, runs on demand + weekly in CI | | Gate for phase exit |
| [ ] | Review UI: list, edit, merge, delete, add, reassign, approve-all | | FR-2.4; keyboard-first (NFR-8) |
| [ ] | Meeting status timeline UI (uploaded → transcribing → extracting → review → done/failed) via Realtime | | NFR-2: async, no spinners |
| [ ] | Built-in board (To do / In progress / Done / Blocked) per project | | FR-3.1 |
| [ ] | Dogfood ritual: run every one of our own meetings through the tool; file issues | | Phase exit depends on this |

## Phase 2 — Close the loop outward

| St | Task | Owner | Notes |
|---|---|---|---|
| [ ] | 5–10 user interviews (freelancer/agency/team) → decide first adapter (OQ-4) + Zoom reality check (OQ-1) | | Do this before building the adapter |
| [ ] | Schema: `integrations`, `external_task_links`, `sync_audit`, `webhook_events` (+ RLS) | | |
| [ ] | Adapter interface finalised (create/update/read status/map users/health/refresh) | | FR-3.2; stub exists in `integrations/base.py` |
| [ ] | App-layer token encryption (Fernet, key in Railway env) + column privileges revoked | | ARCH §5 Secrets |
| [ ] | OAuth connect flow for adapter #1 (UI + pipeline callback) | | |
| [ ] | Adapter #1: create task, idempotent via `external_task_links` | | FR-3.4 |
| [ ] | Push UI: choose destination, push approved, per-item result states | | |
| [ ] | Status-back: webhook receiver (if offered) + polling fallback, conflict rule (external-wins-status) | | FR-3.5, ARCH §4.2 |
| [ ] | `needs_reauth` parking: park queued jobs, banner + email, auto-resume on re-auth | | FR-3.6, failure table row 2 |
| [ ] | Webhook idempotency: `webhook_events` unique-key insert-first pattern | | Failure table row 4 |
| [ ] | Chaos test in CI: kill worker mid-push, force retries, assert zero duplicate external tasks | | Phase exit gate |
| [ ] | Extend two-org isolation suite to integrations + links | | |

## Phase 3 — Follow-ups & reports

| St | Task | Owner | Notes |
|---|---|---|---|
| [ ] | Schema: `followup_rules`, `followup_sends`, `report_schedules`, `reports` (+ RLS) | | |
| [ ] | Scheduler: due-date driven follow-up computation (cadence rules, quiet hours, 1 digest/person/day) | | FR-4.1, FR-4.3 |
| [ ] | Email via Resend free tier; templates with item + meeting context | | ⚠ Resend free tier caps sends/month |
| [ ] | One-click tokenised status response (Done / In progress / Blocked + comment), no login | | FR-4.2 |
| [ ] | Per-person opt-out + per-project follow-up settings UI | | FR-4.3 |
| [ ] | Report generator: completed / in-progress / blocked / decisions / open questions from task state | | FR-5.1 |
| [ ] | Markdown + PDF export, scheduled email delivery | | FR-5.2 |
| [ ] | Meeting summary (decisions + open questions + next steps), regenerable, edits pinned | | FR-2.5 |
| [ ] | Meeting templates v1: standup / client check-in / sprint review biasing extraction + summary | | FR-6.1 |
| [ ] | Dogfood: one full week, zero manual chasing, Monday report needs no edits | | Phase exit gate |

## Phase 4 — Multi-player SaaS

| St | Task | Owner | Notes |
|---|---|---|---|
| [ ] | Email invitations + role management UI (owner/admin/member) | | FR-7.3 |
| [ ] | Per-project membership + enforcement across every endpoint | | FR-7.4 |
| [ ] | Client status page: tokenised route on pipeline, field filtering, revocation, rate limit | | FR-5.3, ARCH §5 |
| [ ] | Stripe products/prices; checkout + customer portal | | FR-8.1 ⚠ Stripe takes per-transaction fees |
| [ ] | Stripe webhooks → entitlement state, idempotent, payment-failure grace period | | FR-8.3, failure table row 4 |
| [ ] | Metering: meetings + LLM tokens per org/month, 80 % warning, free-tier hard stop | | FR-8.2 |
| [ ] | Decide pricing + free-tier limits from real cost data (OQ-5) | | Needs NFR-5 accounting live |
| [ ] | Onboarding flow (first org → first meeting → first push) | | |
| [ ] | Org data export + delete-my-org | | NFR-3 |
| [ ] | Alerting: dead-letter depth, parked jobs, webhook dupes → email/Slack | | NFR-7 |
| [ ] | Stranger test: an outsider completes signup → pay with zero founder help | | Phase exit gate |

## Phase 5 — Beta: platforms + widen

| St | Task | Owner | Notes |
|---|---|---|---|
| [ ] | Zoom OAuth app + `recording.completed` webhook ingestion | | FR-1.3 ⚠ requires host's paid Zoom plan (OQ-1) |
| [ ] | Zoom marketplace app review submission | | Lead time: weeks; start early |
| [ ] | Google Meet ingestion via Workspace APIs | | FR-1.4 |
| [ ] | Adapter #2 and #3 (order per interviews) | | FR-3.3 |
| [ ] | Re-extraction with pinned manual edits | | FR-2.6 |
| [ ] | RAG linking of recurring items across meetings (embeddings in pgvector) | | FR-2.7; pgvector is in Supabase free tier |
| [ ] | Slack follow-up channel + Slack app review | | FR-4.1/OQ-2 |
| [ ] | Recruit 5–10 design-partner orgs; monthly retention dashboard | | Phase exit gate |
