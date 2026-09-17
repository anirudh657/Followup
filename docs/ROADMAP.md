# ActionFlow — Roadmap

**Status:** Draft v1 · **Owners:** Anirudh, Vedant · **Last updated:** 2026-09-17

Ordering principle: **the core loop (transcript → reviewed items → synced tasks) must work
end-to-end before any surrounding SaaS features are built.** Each phase has a single,
testable exit criterion. Durations assume two people, part-time-friendly, no deadline
pressure; they are sequencing guides, not commitments. Task-level breakdown lives in
[TASKS.md](../TASKS.md).

---

## Phase 0 — Foundations (≈ 2 weeks)

Repo, environments, and the walking skeleton: both services deployed, talking to each other
and to Supabase, with auth and CI green.

Scope: monorepo plumbing, Supabase project + initial schema + RLS on `orgs`/`org_members`/
`projects`, Supabase auth in the web app, pipeline JWT verification, health endpoints,
Vercel + Railway deploys, CI (lint/type/test both services), local `docker-compose`.

**Exit criterion:** a user can sign up, create an org, and hit a protected pipeline endpoint
from the deployed frontend; a second user cannot read the first org's rows (RLS test in CI proves it).

## Phase 1 — Core loop, single-player (≈ 4–6 weeks)

Upload-first ingestion (OQ-1 says don't bet MVP on Zoom), extraction, review UI, built-in board.

Scope: transcript upload + normalisation (FR-1.1, 1.6, 1.7), recording upload + one STT
provider behind an interface (FR-1.2, decide OQ-6 here), job queue, LLM extraction with
strict schema + validation/repair/retry + confidence (FR-2.1–2.3), the review UI
(FR-2.4 — this is the daily-use surface, budget real UX time), built-in board (FR-3.1),
extraction eval set ≥ 25 transcripts (NFR-6).

**Exit criterion:** we run our own real meetings through it weekly. A 60-min transcript
becomes reviewable items in ≤ 60 s (p90), extraction clears the NFR-6 quality bar on the
eval set, and approved items land on the built-in board.

## Phase 2 — Close the loop outward (≈ 4 weeks)

First external integration and the sync machinery, because "tasks in the tools people
already use" is the product's reason to exist.

Scope: adapter interface + external link table + idempotent push (FR-3.2, 3.4), **one**
adapter end-to-end including status-back (FR-3.3 subset, 3.5) — pick per OQ-4 after user
interviews, default Notion — token encryption + `needs_reauth` parking (FR-3.6),
two-org isolation test suite extended to integrations.

**Exit criterion:** approved items push to the external tool with zero duplicates across
forced retries/crashes (chaos test in CI), status changes in the external tool appear in
ActionFlow within the polling interval, and killing the token mid-sync parks and then
resumes the queue after re-auth.

## Phase 3 — Follow-ups & reports (≈ 3–4 weeks)

The differentiating "last mile": nobody chases anybody, and the report writes itself.

Scope: follow-up scheduling + email via Resend + one-click no-login status responses
(FR-4.1–4.3), weekly report generation from task state (FR-5.1) with Markdown + PDF export
and scheduled email (FR-5.2), meeting summaries (FR-2.5), meeting templates v1 (FR-6.1).

**Exit criterion:** for one of our real projects, a full week passes in which every status
update arrives via a follow-up click (no manual chasing) and Monday's report is generated,
accurate, and sent without human editing.

## Phase 4 — Multi-player SaaS (≈ 4 weeks)

Turn the working tool into a product other people can pay for.

Scope: invitations + roles enforced everywhere (FR-7.3, 7.4), client-facing status pages
(FR-5.3), Stripe subscriptions + metering + entitlements (FR-8.1–8.3, decide OQ-5 with
real LLM cost data), onboarding flow, data export/delete (NFR-3), Sentry + dead-letter
alerting hardening (NFR-7).

**Exit criterion:** a stranger can sign up, invite a teammate, run the whole loop, hit the
free-tier limit, pay, and get entitlements — with no founder intervention; a revoked status
page link stops working immediately.

## Phase 5 — Beta: connect the meeting platforms + widen (ongoing)

Only now the "automatic" ingestion, because it multiplies value but not learning.

Scope: Zoom OAuth + webhook ingestion (FR-1.3), Google Meet (FR-1.4), adapters #2–3
(FR-3.3), re-extraction with pinned edits (FR-2.6), recurring-meeting RAG linking (FR-2.7),
Slack follow-ups (FR-4.1 P2 part), 5–10 design-partner orgs.

**Exit criterion:** ≥ 5 external orgs each process ≥ 4 meetings/month for a full month,
with ≥ 50 % of their action items flowing through follow-ups to Done — the retention
signal that justifies building further (Teams, escalations, branding, custom templates).

---

## Explicitly deferred (no phase)

Teams integration (FR-1.5), escalations (FR-4.4), report branding (FR-5.4), custom
templates (FR-6.2) — pulled in only when a design partner asks and Phase 5's criterion holds.
