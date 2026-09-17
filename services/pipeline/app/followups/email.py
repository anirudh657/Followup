"""Follow-up delivery via email (Resend) with one-click status responses (FR-4.2).

Each message embeds tokenised links (Done / In progress / Blocked + comment) that
hit /followups/respond/{token} on the pipeline — status flows back with no login.
Resend free tier caps monthly sends (README §Costs).
"""

from __future__ import annotations

from uuid import UUID


async def send_followup(action_item_id: UUID) -> None:
    """Render and send one follow-up email, recording it in followup_sends.

    TODO(phase-3): Resend client, templates, response tokens (>=128-bit, single-use).
    """
    raise NotImplementedError("TODO(phase-3): follow-up email delivery")
