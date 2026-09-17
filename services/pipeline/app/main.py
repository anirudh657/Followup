"""FastAPI application entrypoint.

Routes are intentionally minimal at scaffold stage: a health check (implemented,
used by docker-compose and Railway) and the route groups that phases 0-2 will fill
in. Webhook routes live here too — external providers call the pipeline directly,
never the Next.js app (docs/ARCHITECTURE.md §3).
"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.config import get_settings

app = FastAPI(title="ActionFlow pipeline", version="0.1.0")


class HealthResponse(BaseModel):
    status: Literal["ok"]
    env: str


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    """Liveness probe; also verifies settings parse at boot."""
    return HealthResponse(status="ok", env=get_settings().app_env.value)


# TODO(phase-0): auth middleware (app.auth.jwt), /orgs bootstrap routes.
# TODO(phase-1): /meetings/{id}/ingest, /meetings/{id}/items review routes.
# TODO(phase-2): /integrations connect/callback routes, /webhooks/{provider}.
# TODO(phase-3): /followups/respond/{token} (one-click status, no login).
# TODO(phase-4): /webhooks/stripe, /status/{page_token} public status page.
