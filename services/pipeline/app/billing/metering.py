"""Usage metering (FR-8.2): meetings + LLM tokens per org per month.

Counters power the free-tier limits (80% soft warning, hard stop) and — before any
pricing decision — tell us the real unit cost per meeting (NFR-5, PRD OQ-5).
"""

from __future__ import annotations

from uuid import UUID


async def record_llm_usage(org_id: UUID, input_tokens: int, output_tokens: int) -> None:
    """Add token usage to the org's current-month counters.

    TODO(phase-4): implement counters (called from phase 1's LLM client wrapper,
    writing to a plain table until real billing exists).
    """
    raise NotImplementedError("TODO(phase-4): usage metering")


async def check_meeting_quota(org_id: UUID) -> None:
    """Raise QuotaExceededError if the org's plan disallows processing another meeting.

    TODO(phase-4): entitlement lookup + counters.
    """
    raise NotImplementedError("TODO(phase-4): quota enforcement")


class QuotaExceededError(RuntimeError):
    """Org hit its plan limit; surfaces as an upgrade prompt, never a silent drop."""
