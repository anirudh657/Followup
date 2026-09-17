# Contributing

Two-person team (Anirudh, Vedant). Lightweight process, but real: everything below exists
because it prevents a specific failure, not for ceremony.

## Task ownership

Work is tracked in [TASKS.md](TASKS.md). Tasks are **assigned manually by mutual
agreement** — claim a task by putting your name in the Owner column in a PR (or a direct
commit to TASKS.md only). Never start a task someone else owns without talking first.
Status marks: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked (+ reason in Notes).

## Branches

- `main` is protected: PRs only, 1 approving review (the other person), CI green.
- Branch naming: `<type>/<short-kebab-summary>`, e.g. `feat/extraction-schema`,
  `fix/webhook-dedupe`, `docs/roadmap-phase2`, `chore/ci-cache`.
- Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`.
- Small PRs. If a task needs >~500 changed lines, split it.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <imperative summary ≤ 72 chars>

Optional body: what & why, not how.
```

Scopes: `web`, `pipeline`, `db`, `docs`, `ci`, `repo`. Examples:

- `feat(pipeline): add VTT transcript parser`
- `fix(web): board column order after drag`
- `chore(db): migration for external_task_links`

## PRs

- Fill the template. Link the TASKS.md line and FR/NFR ids where they exist.
- The reviewer actually runs it when the change touches the review UI or sync (our two
  danger zones).
- Squash-merge; the squash message must itself be a valid conventional commit.

## Code standards

- **Web:** TypeScript strict; ESLint + Prettier; components colocated; server components by
  default, client components only when interactive.
- **Pipeline:** Python 3.12; `ruff` (lint + format), `mypy --strict` on `app/`; Pydantic
  models at every boundary (API, LLM, DB rows in/out); no bare `except`.
- Stubs raise `NotImplementedError` with a `TODO(phase-N)` tag — never fake return values.
- Every failure-mode behaviour from [ARCHITECTURE §6](docs/ARCHITECTURE.md) that you touch
  gets a test.

## Environments

- **local** — `docker compose up` + `supabase start`.
- **preview** — Vercel preview deploys per PR (frontend only, pointed at the dev Supabase project).
- **prod** — Vercel + Railway + Supabase cloud. Deploys from `main` only.

## Secrets

Never in git, never in PR descriptions, never in logs. `.env` locally, Vercel/Railway
dashboards in the cloud. If a secret leaks into history: rotate first, clean history second.
