"""The common adapter interface every task tool implements (FR-3.2).

Contract rules all adapters must honour:
  * create_task is idempotent from the caller's perspective: the caller supplies an
    idempotency key (see app.sync.idempotency) and stores the returned external id in
    external_task_links; where the tool allows it, the adapter also embeds the key in
    the task so a create-timeout can be reconciled by search.
  * Auth errors raise AdapterAuthError -> the integration parks as needs_reauth and
    queued jobs wait (never dropped) — ARCH §6 row 2.
  * Status mapping is total: every external state maps onto app.models.TaskStatus.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models import ActionItem, TaskStatus


@dataclass(frozen=True)
class ExternalTaskRef:
    """Identity of a task inside the external tool."""

    external_id: str
    url: str


@dataclass(frozen=True)
class ExternalUser:
    """A user inside the external tool, for owner mapping (PRD OQ-3)."""

    external_id: str
    display_name: str
    email: str | None


class TaskToolAdapter(ABC):
    """Interface all per-tool adapters implement. One instance = one org's connection."""

    tool_name: str

    @abstractmethod
    async def health_check(self) -> None:
        """Cheap credential probe; raises AdapterAuthError if re-auth is needed."""

    @abstractmethod
    async def create_task(self, item: ActionItem, *, idempotency_key: str) -> ExternalTaskRef:
        """Create the external task for an approved item (FR-3.4)."""

    @abstractmethod
    async def update_task(self, ref: ExternalTaskRef, item: ActionItem) -> None:
        """Push content changes (title/description/owner/due) outward."""

    @abstractmethod
    async def read_status(self, ref: ExternalTaskRef) -> TaskStatus:
        """Read current status, mapped onto the canonical TaskStatus (FR-3.5 polling)."""

    @abstractmethod
    async def list_users(self) -> list[ExternalUser]:
        """Users available for assignment, for the owner-mapping table."""

    @abstractmethod
    async def refresh_credentials(self) -> None:
        """Refresh OAuth tokens; persists via the encrypted credential store."""


class AdapterAuthError(RuntimeError):
    """Token expired/revoked/insufficient scope -> integration parks (needs_reauth)."""


class AdapterRateLimitedError(RuntimeError):
    """Rate limited; carries retry-after so the job queue backs off correctly."""

    def __init__(self, retry_after_seconds: float) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"rate limited; retry after {retry_after_seconds}s")
