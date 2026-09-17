"""Supabase JWT verification (ARCH §3): the pipeline trusts no caller, only tokens.

Every non-webhook request carries the user's Supabase access token; this module
verifies signature (JWKS from the Supabase project), issuer, audience, and expiry,
resolves the user's membership + role in the org claimed by the X-Org-Id header,
and produces the TenantContext everything downstream requires. Webhook routes use
per-provider signature verification instead (in main.py routes).
"""

from __future__ import annotations

from app.tenancy.repo import TenantContext


async def verify_request_token(authorization_header: str, org_id_header: str) -> TenantContext:
    """Verify a bearer token and org claim; return the acting TenantContext.

    Raises:
        AuthError: bad/expired token, or the user is not a member of the org.

    TODO(phase-0): JWKS fetch+cache, verification, membership lookup.
    """
    raise NotImplementedError("TODO(phase-0): Supabase JWT verification")


class AuthError(RuntimeError):
    """Authentication or org-membership failure (maps to HTTP 401/403)."""
