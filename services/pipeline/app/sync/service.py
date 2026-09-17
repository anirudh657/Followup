"""Task sync orchestration (FR-3.4, FR-3.5): push jobs out, apply status back.

Conflict rule (ARCH §4.2 step 5): external-wins for status, ActionFlow-wins for
content; every resolution is recorded in sync_audit.
"""

from __future__ import annotations

from uuid import UUID

from app.integrations.base import TaskToolAdapter
from app.models import ActionItem, TaskStatus


async def push_item(item: ActionItem, adapter: TaskToolAdapter) -> None:
    """Push one approved item to one destination, exactly-once in effect.

    Refuses items where ``item.is_syncable`` is False (the review gate, FR-2.4).

    TODO(phase-2): link-row lookup, adapter call with push_key, park-on-auth-error.
    """
    raise NotImplementedError("TODO(phase-2): idempotent push")


async def apply_external_status(
    org_id: UUID, external_id: str, tool_name: str, status: TaskStatus
) -> None:
    """Apply a status change arriving from a webhook or a poll (FR-3.5).

    Must be idempotent: webhooks are deduped upstream, but semantically re-applying
    the same status is also a no-op (defence in depth, ARCH §6 row 4).

    TODO(phase-2): implement with sync_audit records.
    """
    raise NotImplementedError("TODO(phase-2): inbound status application")
