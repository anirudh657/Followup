# ActionFlow

**Meetings → executed work.** ActionFlow ingests a meeting (recording, transcript, or a
connected Zoom/Meet/Teams account), extracts clean action items, owners, deadlines and
decisions with confidence scores, lets a human review them in seconds, pushes them
one-click into the tools teams already use (Notion, Linear, Jira, Asana, Todoist, or a
built-in board), then closes the loop with gentle automated follow-ups and generated
weekly/monthly status reports — including a client-shareable status page.

Most meeting tools stop at the summary. ActionFlow is built for the last mile.

**Docs:** [PRD](docs/PRD.md) · [Architecture](docs/ARCHITECTURE.md) ·
[Roadmap](docs/ROADMAP.md) · [Tasks](TASKS.md) · [Contributing](CONTRIBUTING.md)

---

## Repo layout

Monorepo, two independently deployed services side by side:

```
actionflow/
├── apps/
│   └── web/                  # Next.js 14 + Tailwind + shadcn/ui (Vercel)
│       ├── app/              #   App Router pages/layouts
│       ├── components/       #   UI components (shadcn/ui lives here)
│       └── lib/              #   supabase client, pipeline API client, generated types
├── services/
│   └── pipeline/             # Python 3.12 FastAPI service (Railway)
│       ├── app/
│       │   ├── main.py       #   FastAPI app + routes
│       │   ├── config.py     #   settings (implemented)
│       │   ├── models/       #   domain models (implemented)
│       │   ├── ingestion/    #   upload/Zoom/Meet/Teams → normalised transcript (stubs)
│       │   ├── extraction/   #   LLM structured extraction + confidence (schemas implemented, pipeline stubbed)
│       │   ├── integrations/ #   common adapter interface + per-tool adapters (stubs)
│       │   ├── sync/         #   idempotent task push/pull (idempotency keys implemented, sync stubbed)
│       │   ├── followups/    #   follow-up scheduling (stubs)
│       │   ├── reports/      #   report + status page generation (stubs)
│       │   ├── tenancy/      #   org-scoped repository guard (stubs)
│       │   ├── auth/         #   Supabase JWT verification (stubs)
│       │   └── billing/      #   Stripe subscriptions/metering (stubs)
│       └── tests/            #   pytest (runs in CI; implemented modules are tested)
├── docs/                     # PRD, architecture, roadmap
├── .github/                  # CI, PR + issue templates
├── docker-compose.yml        # local stack
└── .env.example              # every env var, commented
```

The boundary rule (see [Architecture §3](docs/ARCHITECTURE.md)): **anything touching an
LLM, a transcript, or an external tool API lives in `services/pipeline`.** Next.js is UI
plus thin proxy routes only.

Stubs are honest stubs: typed signatures + docstrings, raising `NotImplementedError` with
a `TODO(phase-N)` tag matching the [roadmap](docs/ROADMAP.md). No fake implementations.

## Quickstart

Prereqs: Node 20+, pnpm 9+, Python 3.12+, Docker, [Supabase CLI](https://supabase.com/docs/guides/cli).

```bash
git clone git@github.com:anirudh657/actionflow.git && cd actionflow
cp .env.example .env          # fill in values (see comments in the file)
```

### Frontend (`apps/web`)

```bash
cd apps/web
pnpm install
pnpm dev                      # http://localhost:3000
```

### Pipeline (`services/pipeline`)

```bash
cd services/pipeline
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000    # http://localhost:8000/healthz
pytest                        # run the test suite
```

### Full local stack

```bash
supabase start                # local Supabase (Postgres/Auth/Storage) on Docker
docker compose up             # web + pipeline containers, pointed at local Supabase
```

## Environment variables

Every variable is defined and commented in [.env.example](.env.example). Never commit
`.env`. Summary of where each lives:

| Prefix / var | Used by | Set in |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_*` | web (browser-safe) | Vercel + local |
| `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_*` | pipeline only — never the frontend | Railway + local |
| `DATABASE_URL` | pipeline (direct Postgres for the job queue) | Railway + local |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GROQ_API_KEY` | pipeline LLM client (any one is enough to start) | Railway + local |
| `ASSEMBLYAI_API_KEY` / `DEEPGRAM_API_KEY` | pipeline STT (optional until Phase 1 STT task) | Railway + local |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | pipeline billing (Phase 4) | Railway |
| `RESEND_API_KEY` | pipeline follow-up email (Phase 3) | Railway |
| `TOKEN_ENCRYPTION_KEY` | pipeline — Fernet key for integration tokens | Railway + local |
| `ZOOM_*`, `GOOGLE_*`, `NOTION_*`, `LINEAR_*`, … | pipeline OAuth apps (per phase) | Railway |

## Common commands

| Command | Where | What |
|---|---|---|
| `pnpm dev` / `pnpm build` / `pnpm lint` / `pnpm typecheck` / `pnpm test` | `apps/web` | dev server / prod build / ESLint / `tsc --noEmit` / vitest |
| `uvicorn app.main:app --reload` | `services/pipeline` | dev server |
| `pytest` · `pytest -k name` | `services/pipeline` | tests |
| `ruff check . && ruff format --check .` | `services/pipeline` | lint + format check |
| `mypy app` | `services/pipeline` | type check |
| `supabase db diff -f <name>` / `supabase db push` | repo root | create / apply migrations |
| `docker compose up --build` | repo root | full local stack |

## Costs on the "free" tiers ⚠

Flagging everything that can cost money, per the project constraints:

- **LLM APIs (Anthropic/OpenAI):** *not free* — pay-per-token from the first call. Groq /
  Together free tiers exist but are rate-limited and model-restricted; treat free LLM
  capacity as a development convenience, not a plan. Per-org token accounting (NFR-5) exists
  precisely so we know real unit cost. Check current pricing at https://docs.claude.com/en/docs/about-claude/pricing before choosing models.
- **Zoom ingestion:** cloud recording/transcripts require the *host's* paid Zoom plan — a
  cost on the **user's** side that shapes adoption (PRD OQ-1).
- **STT:** AssemblyAI and Deepgram give limited free credits; they run out. Self-hosted
  Whisper shifts cost to Railway compute.
- **Railway:** trial credit only, then usage-billed. This will likely be the **first real
  bill** — a always-on Python worker doesn't fit "scale to zero".
- **Vercel:** Hobby tier is free but licensed for **non-commercial** use; the moment we
  charge customers we need Vercel Pro (per seat) or to move the frontend.
- **Supabase:** free tier includes Postgres/Auth/Storage with quotas; projects **pause after
  1 week of inactivity** (fine in dev, unacceptable in prod → paid tier eventually).
- **Resend (email):** free tier caps monthly sends; follow-ups at scale exceed it.
- **Stripe:** no monthly fee, but per-transaction fees on every payment we take.
- **Sentry:** free tier caps events/month.
- Domain name: a few dollars/year, whenever we buy one.

## Creating the private repo & first push

Using [GitHub CLI](https://cli.github.com/) as `anirudh657` (Vedant is added as a collaborator; replace `VEDANT_GITHUB` with his username):

```bash
cd actionflow
git init -b main
git add .
git commit -m "chore: initial repo scaffold (docs, plumbing, service skeletons)"
gh auth login
gh repo create actionflow --private --source=. --description "Meetings → executed work" --push
gh repo edit anirudh657/actionflow --enable-issues --enable-wiki=false
gh api -X PUT repos/anirudh657/actionflow/collaborators/VEDANT_GITHUB -f permission=admin
# branch protection: PRs only, 1 review (see CONTRIBUTING.md)
gh api -X PUT repos/anirudh657/actionflow/branches/main/protection \
  -F required_pull_request_reviews[required_approving_review_count]=1 \
  -F enforce_admins=false -F required_status_checks[strict]=true \
  -F "required_status_checks[contexts][]=web" \
  -F "required_status_checks[contexts][]=pipeline" \
  -F restrictions=
```

Without `gh`: create the private repo in the GitHub UI, then

```bash
git init -b main && git add . && git commit -m "chore: initial repo scaffold"
git remote add origin git@github.com:anirudh657/actionflow.git
git push -u origin main
```

## License

[MIT](LICENSE) © Anirudh Arora
