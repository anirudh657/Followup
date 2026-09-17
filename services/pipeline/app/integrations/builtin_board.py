"""Built-in minimal board (FR-3.1): the zero-setup destination.

Implemented as an adapter so the sync path treats it identically to external tools —
follow-ups and reports then work for users with no PM tool at all. It writes to our
own tasks tables, so it has no auth failure modes.
"""

from __future__ import annotations

from app.integrations.base import ExternalTaskRef, ExternalUser, TaskToolAdapter
from app.models import ActionItem, TaskStatus


class BuiltinBoardAdapter(TaskToolAdapter):
    """Adapter over ActionFlow's own board tables."""

    tool_name = "builtin"

    async def health_check(self) -> None:
        """No external credentials; always healthy. TODO(phase-1): DB reachability."""
        raise NotImplementedError("TODO(phase-1): builtin board health_check")

    async def create_task(self, item: ActionItem, *, idempotency_key: str) -> ExternalTaskRef:
        """TODO(phase-1): upsert board task keyed on the idempotency key."""
        raise NotImplementedError("TODO(phase-1): builtin board create_task")

    async def update_task(self, ref: ExternalTaskRef, item: ActionItem) -> None:
        """TODO(phase-1): update board task content."""
        raise NotImplementedError("TODO(phase-1): builtin board update_task")

    async def read_status(self, ref: ExternalTaskRef) -> TaskStatus:
        """TODO(phase-1): read board task status."""
        raise NotImplementedError("TODO(phase-1): builtin board read_status")

    async def list_users(self) -> list[ExternalUser]:
        """TODO(phase-1): org members as assignable users."""
        raise NotImplementedError("TODO(phase-1): builtin board list_users")

    async def refresh_credentials(self) -> None:
        """No credentials to refresh; no-op by design. TODO(phase-1): make no-op."""
        raise NotImplementedError("TODO(phase-1): builtin board refresh_credentials no-op")
