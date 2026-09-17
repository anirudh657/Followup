"""Client-facing shareable status page (FR-5.3).

A tokenised, read-only, rate-limited projection of one project, filtered to
client-visible fields only. Tokens are >=128-bit random, stored as revocable rows
(ARCH §5 "Public status pages" — the one deliberate hole in tenancy, kept tiny).
"""

from __future__ import annotations


async def render_status_page(page_token: str) -> dict[str, object]:
    """Resolve a public token to the filtered project projection, or raise.

    Raises:
        StatusPageRevokedError: token unknown or revoked (indistinguishable on purpose).

    TODO(phase-4): implement token store, field filtering, rate limiting.
    """
    raise NotImplementedError("TODO(phase-4): public status page")


class StatusPageRevokedError(LookupError):
    """Token is unknown or has been revoked."""
