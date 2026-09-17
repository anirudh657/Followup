# ActionFlow — Product Requirements Document

**Status:** Draft v1 · **Owners:** Anirudh, Vedant · **Last updated:** 2026-09-17

---

## 1. Problem

Meetings produce commitments; almost no tooling closes the loop on them. Existing meeting
tools (Otter, Fireflies, tl;dv, built-in Zoom/Meet AI) stop at a summary. The summary is
read once, action items live in a PDF or a Slack message, nobody follows up, and the next
meeting starts with "where are we on X?".

The people who feel this most acutely are those whose income depends on visible follow-through:

- **Freelancers** promise deliverables on client calls and then reconstruct them from memory.
- **Agencies** juggle many clients; dropped action items are churn risk. They also need to
  *show* clients that work is moving.
- **Small product teams** run standups/sprint reviews and re-type outcomes into Linear/Jira
  by hand, or don't, and lose them.

ActionFlow's thesis: **the value is not the summary, it is the executed work.** Meeting →
structured action items → tasks in the tools people already use → gentle follow-up →
status report. The last mile is the product.

## 2. Goals

1. A user can go from a finished meeting (recording, transcript, or connected platform) to
   reviewed, human-approved action items in **under 3 minutes**.
2. One-click sync of approved items into at least one external tool (plus the built-in
   board) with reliable two-way status.
3. Automated, polite follow-ups that collect status without a human chasing people.
4. A weekly/monthly report and a client-shareable status page generated from real task
   state, not from prose.
5. Multi-tenant SaaS with orgs, roles, a free tier, and paid seats — architecture ready
   for billing from day one even if billing ships late.

## 3. Non-goals

- **Not** a transcription company. We consume native transcripts (Zoom/Meet) or third-party
  STT (AssemblyAI/Deepgram/Whisper). We never build our own ASR.
- **Not** a project-management tool competing with Linear/Jira/Notion. The built-in board is
  deliberately minimal — an on-ramp for users who have no PM tool.
- **Not** deep AI research. No model training, no custom memory systems, no agentic
  orchestration frameworks. Well-prompted hosted LLMs + structured output + light RAG only.
- **Not** real-time in-meeting assistance (live agenda nudges, live notes). Post-meeting only, for MVP and the foreseeable roadmap.
- **Not** enterprise (SSO/SAML, audit logs, on-prem) in the first year.

## 4. Users

### 4.1 Freelancer (single seat)
Solo consultant/designer/developer. 3–10 client calls a week. No PM tool or a personal
Notion/Todoist. Wants: never drop a client promise; look professional via the shareable
status page. Price sensitivity: high. Entry point: free tier.

### 4.2 Agency (5–25 seats)
Accounts/PM leads run recurring client check-ins. Multiple clients = multiple projects =
strict isolation of what each client can see. Wants: follow-ups happen without the PM
chasing, and the client-facing status page replaces the weekly status email. Willing to
pay per seat if it demonstrably saves PM hours.

### 4.3 Small product team (3–15 seats)
Runs standups, planning, sprint reviews. Already lives in Linear/Jira + Slack. Wants:
meeting outcomes to appear in their tracker with correct assignees, and status to flow
back so reports write themselves. Adoption blocker: sync must be trustworthy (no dupes,
no zombie tasks).

## 5. Functional requirements

Numbered for traceability from ARCHITECTURE.md, ROADMAP.md and TASKS.md.
Priority: **P0** = core loop / MVP, **P1** = first iteration after MVP, **P2** = later.

### FR-1 Ingestion
- **FR-1.1 (P0)** Upload a transcript file (plain text, VTT, SRT, or JSON from common tools) to a meeting.
- **FR-1.2 (P0)** Upload an audio/video recording; the system obtains a transcript via a
  configured STT provider (AssemblyAI, Deepgram, or self-hosted Whisper).
- **FR-1.3 (P1)** Connect Zoom via OAuth; pull cloud-recording transcripts automatically
  after meetings end (webhook-driven).
- **FR-1.4 (P1)** Connect Google Meet (Google Workspace APIs) and pull transcripts/recordings where the workspace makes them available.
- **FR-1.5 (P2)** Connect Microsoft Teams (Graph API) similarly.
- **FR-1.6 (P0)** Normalise every source into one internal transcript format: ordered
  utterances with speaker label, timestamps, and raw text; store source + language.
- **FR-1.7 (P0)** Detect and reject garbage input early (empty, non-speech, wrong language
  when unsupported, > size limits) with a clear user-facing error state.

### FR-2 Extraction
- **FR-2.1 (P0)** From a normalised transcript, extract: action items (title, description,
  suggested owner, suggested due date, source quote/timestamp), decisions, and open questions,
  using an LLM constrained to a strict JSON schema.
- **FR-2.2 (P0)** Every extracted item carries a confidence score; items below a threshold
  are visually flagged for review.
- **FR-2.3 (P0)** Owner suggestions map speaker names to org members where possible; unmapped
  names remain as free-text "unassigned: <name>".
- **FR-2.4 (P0)** Review UI: the user can edit, merge, delete, add, and reassign items and
  confirm the set before anything syncs. Nothing leaves ActionFlow un-reviewed by default.
- **FR-2.5 (P1)** A meeting summary composed of decisions + open questions + next steps
  (never a wall of prose), regenerable after edits.
- **FR-2.6 (P1)** Re-run extraction with user feedback ("you missed the part about the invoice")
  without losing manual edits (edits are pinned).
- **FR-2.7 (P2)** Light RAG over the org's previous meetings so recurring items ("still waiting
  on staging access") are linked to the earlier occurrence rather than duplicated.

### FR-3 Task sync (integrations)
- **FR-3.1 (P0)** Built-in minimal board (To do / In progress / Done / Blocked) per project.
- **FR-3.2 (P0)** Integration layer with a single common adapter interface; per-tool adapters
  behind it (create task, update task, read status, map users, health-check, OAuth/token refresh).
- **FR-3.3 (P1)** Adapters, in this order: **Notion**, **Linear**, **Todoist**, **Asana**, **Jira**.
  (Order chosen by API friendliness and target-user overlap; revisit after user interviews — see OQ-4.)
- **FR-3.4 (P0)** One-click "push approved items" to the chosen destination; idempotent —
  re-pushing never creates duplicates (external ID mapping stored per item).
- **FR-3.5 (P1)** Status flows back (webhooks where offered, polling elsewhere) so ActionFlow
  knows Done/In-progress without the user re-entering it.
- **FR-3.6 (P0)** Integration failures (expired token, revoked scope, rate limit) degrade
  gracefully: items stay queued, the user is told exactly what to fix, nothing is lost.

### FR-4 Follow-ups
- **FR-4.1 (P1)** Configurable per project: cadence (e.g. 48h before due, on due date, N days
  overdue), channel (email for MVP; Slack later — P2), and tone template.
- **FR-4.2 (P1)** Follow-up messages include the item, its source meeting, and one-click
  status responses (Done / In progress / Blocked + comment) that write back without login.
- **FR-4.3 (P1)** Quiet hours and per-person opt-out; never more than one digest per person per day.
- **FR-4.4 (P2)** Escalation: if an item is N days overdue and unacknowledged, notify the
  project owner instead of re-pinging the assignee.

### FR-5 Reports & status page
- **FR-5.1 (P1)** Weekly/monthly report per project: completed, in progress, blocked (with
  reasons), decisions made, open questions — generated from task state + meeting records.
- **FR-5.2 (P1)** Export as Markdown and PDF; email delivery on a schedule.
- **FR-5.3 (P1)** Client-facing shareable status page: tokenised public URL, read-only,
  scoped to one project, showing only fields the org marks client-visible; revocable.
- **FR-5.4 (P2)** Report tone/branding customisation (logo, intro paragraph) for agencies.

### FR-6 Meeting templates
- **FR-6.1 (P1)** Built-in templates: standup, client check-in, sprint review. A template
  biases extraction (e.g. standup → yesterday/today/blockers) and the summary layout.
- **FR-6.2 (P2)** Custom templates per org.

### FR-7 Accounts, orgs, permissions
- **FR-7.1 (P0)** Auth via Supabase (email magic link + Google OAuth).
- **FR-7.2 (P0)** Orgs with roles: **owner**, **admin**, **member**. Projects belong to an org;
  meetings/tasks belong to a project. All data is org-scoped (see ARCHITECTURE §5).
- **FR-7.3 (P0)** Invitations by email; a user can belong to multiple orgs.
- **FR-7.4 (P1)** Per-project membership within an org (an agency PM sees only their clients' projects if restricted).
- **FR-7.5 (P0)** Hard tenant isolation: no query path may return another org's data
  (enforced in the database with RLS, not only in application code).

### FR-8 Billing
- **FR-8.1 (P1)** Stripe subscriptions: Free (1 seat, N meetings/month, built-in board only),
  Pro (per seat, all integrations, follow-ups, reports), Team/Agency (higher limits, status
  pages, branding). Exact limits: OQ-5.
- **FR-8.2 (P1)** Metering: meetings processed and LLM tokens per org per month; soft warnings
  at 80 %, hard stop at limit on Free.
- **FR-8.3 (P1)** Webhook-driven entitlement state (subscription created/updated/cancelled),
  idempotent, with a grace period on payment failure.

## 6. Non-functional requirements

- **NFR-1 Reliability of sync.** Task creation is at-least-once with idempotency keys; visible
  end state is exactly-once. Webhook handlers tolerate duplicates and out-of-order delivery.
- **NFR-2 Extraction latency.** Transcript-in to reviewable items: ≤ 60 s for a 60-minute
  meeting (p90). Async with progress state, never a blocking spinner.
- **NFR-3 Privacy.** Transcripts are sensitive. Encrypted at rest (Supabase default) and in
  transit; raw recordings deleted after transcription unless the org opts to keep them; org
  data export + delete-my-org supported before public launch (GDPR-ish hygiene even pre-EU-focus).
- **NFR-4 Security.** All integration tokens encrypted at rest (app-layer encryption, key
  outside the DB); tokenised public status pages use ≥ 128-bit random tokens; rate limiting
  on public endpoints.
- **NFR-5 Cost ceiling.** Runs on free tiers during development (see README "Costs"). LLM
  cost per meeting is tracked from day one so pricing can be grounded in unit economics.
- **NFR-6 Quality bar for extraction.** On our own labelled test set of ≥ 25 real transcripts:
  ≥ 90 % of human-judged action items captured, ≤ 10 % hallucinated items, before we call
  the MVP done. (Set built during Phase 1 from our own meetings + public transcripts.)
- **NFR-7 Operability.** Structured logs, error tracking (Sentry free tier), and a dead-letter
  queue for failed jobs from the first deploy.
- **NFR-8 Accessibility & UX.** Review UI fully keyboard-operable (it's the daily-use surface);
  mobile-readable status pages and reports.

## 7. Open questions

- **OQ-1** Zoom transcript access requires the host to have cloud recording (paid Zoom plan).
  Do enough target users have it, or is upload-first (FR-1.1/1.2) the real MVP path? Validate
  in first 10 user interviews.
- **OQ-2** Follow-up channel: is email enough for v1, or is Slack table-stakes for the product-team persona? (Slack app review adds scope.)
- **OQ-3** Owner mapping across tools (transcript speaker → ActionFlow user → Linear/Notion user)
  is fuzzy. Manual mapping table per integration, or LLM-assisted suggestions? Start manual.
- **OQ-4** Adapter order (FR-3.3) is a guess. Re-rank after interviews; build exactly one
  external adapter in MVP.
- **OQ-5** Free-tier limits and price points — decide after we know LLM cost per meeting (NFR-5).
- **OQ-6** Which STT for uploads: AssemblyAI vs Deepgram free credits vs self-hosted Whisper
  on Railway (compute cost vs API cost). Benchmark on 5 real recordings in Phase 1.
- **OQ-7** Data residency / retention promises for agency clients ("delete after 90 days"?) —
  needed before charging agencies, not before MVP.
- **OQ-8** Do we need per-project client *logins* for the status page, or is a secret URL
  acceptable at agency scale? Secret URL for v1; revisit on first enterprise-ish request.
