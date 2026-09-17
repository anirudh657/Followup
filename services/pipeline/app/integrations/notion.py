"""Notion adapter (FR-3.3). Build order is decided by PRD OQ-4 — one adapter ships in MVP."""

from __future__ import annotations

from app.integrations.base import ExternalTaskRef, ExternalUser, TaskToolAdapter
from app.models import ActionItem, TaskStatus


class NotionAdapter(TaskToolAdapter):
    """Notion implementation of the common adapter interface."""

    tool_name = "notion"

    async def health_check(self) -> None:
        """TODO(phase-2): credential probe."""
        raise NotImplementedError("TODO(phase-2): notion health_check")

    async def create_task(self, item: ActionItem, *, idempotency_key: str) -> ExternalTaskRef:
        """TODO(phase-2): idempotent create (embed key where Notion allows)."""
        raise NotImplementedError("TODO(phase-2): notion create_task")

    async def update_task(self, ref: ExternalTaskRef, item: ActionItem) -> None:
        """TODO(phase-2): outward content update."""
        raise NotImplementedError("TODO(phase-2): notion update_task")

    async def read_status(self, ref: ExternalTaskRef) -> TaskStatus:
        """TODO(phase-2): status read + mapping to TaskStatus."""
        raise NotImplementedError("TODO(phase-2): notion read_status")

    async def list_users(self) -> list[ExternalUser]:
        """TODO(phase-2): assignable users for owner mapping."""
        raise NotImplementedError("TODO(phase-2): notion list_users")

    async def refresh_credentials(self) -> None:
        """TODO(phase-2): OAuth refresh via encrypted credential store."""
        raise NotImplementedError("TODO(phase-2): notion refresh_credentials")
