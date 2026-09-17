"""Microsoft Teams source (FR-1.5) — explicitly deferred (see ROADMAP)."""

from __future__ import annotations

from uuid import UUID

from app.ingestion.base import MeetingSource, RawCapture


class TeamsSource(MeetingSource):
    """Pulls Teams artifacts via Microsoft Graph."""

    async def acquire(self, org_id: UUID, meeting_id: UUID) -> RawCapture:
        """TODO(phase-5): deferred until a design partner needs Teams."""
        raise NotImplementedError("TODO(phase-5): Teams ingestion (deferred)")
