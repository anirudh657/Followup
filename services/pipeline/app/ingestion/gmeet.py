"""Google Meet source (FR-1.4): Workspace APIs, where the workspace exposes artifacts."""

from __future__ import annotations

from uuid import UUID

from app.ingestion.base import MeetingSource, RawCapture


class GoogleMeetSource(MeetingSource):
    """Pulls Meet transcripts/recordings via Google Workspace APIs."""

    async def acquire(self, org_id: UUID, meeting_id: UUID) -> RawCapture:
        """TODO(phase-5): Google Workspace acquisition."""
        raise NotImplementedError("TODO(phase-5): Google Meet ingestion")
