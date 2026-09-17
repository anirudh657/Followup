"""Follow-up scheduling (FR-4.1–4.3): who gets nudged, about what, when.

Rules engine over task state: cadence relative to due dates, quiet hours,
max one digest per person per day, per-person opt-out. Produces followup_send
jobs; delivery itself lives in email.py. Escalations (FR-4.4) are deferred.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID


def compute_due_followups(org_id: UUID, now: datetime) -> list[UUID]:
    """Return action_item ids that should receive a follow-up at `now`.

    Pure over its inputs once task/rule state is passed in — designed to be
    property-tested (never two digests to one person in one day, never inside
    quiet hours, never for opted-out users).

    TODO(phase-3): implement rules engine.
    """
    raise NotImplementedError("TODO(phase-3): follow-up scheduling rules")
