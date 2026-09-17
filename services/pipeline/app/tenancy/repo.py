"""TenantScopedRepo: the only sanctioned way to touch tenant data with service role.

The pipeline uses Supabase's service-role key, which bypasses RLS — so isolation on
this path is structural: every handler builds a TenantScopedRepo from a *verified*
request context (JWT -> user -> org membership), and the repo injects org_id into
every query it issues. Raw service-client usage outside this module is limited to
the job runner and webhook intake, and CI greps enforce that (ARCH §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.models import OrgRole


@dataclass(frozen=True)
class TenantContext:
    """Verified acting identity: produced by app.auth, never constructed from input."""

    user_id: UUID
    org_id: UUID
    role: OrgRole


class TenantScopedRepo:
    """Org-scoped data access. Every method filters by self.ctx.org_id — no exceptions."""

    def __init__(self, ctx: TenantContext) -> None:
        self.ctx = ctx

    async def fetch_meetings(self) -> list[dict[str, object]]:
        """TODO(phase-0): org-scoped reads (validated into domain models)."""
        raise NotImplementedError("TODO(phase-0): tenant-scoped queries")

    def require_role(self, minimum: OrgRole) -> None:
        """Raise if the acting role is below `minimum` (owner > admin > member).

        TODO(phase-0): implement ordering + ForbiddenError.
        """
        raise NotImplementedError("TODO(phase-0): role enforcement")
