"""Upload source: user-provided transcript files or recordings (FR-1.1, FR-1.2).

The browser uploads directly to Supabase Storage via a signed URL; this source
then reads the object and produces a RawCapture (media uploads go through the
configured STT provider first — see stt.py).
"""

from __future__ import annotations

from uuid import UUID

from app.ingestion.base import MeetingSource, RawCapture


class UploadSource(MeetingSource):
    """Reads an uploaded object from org-scoped Supabase Storage."""

    async def acquire(self, org_id: UUID, meeting_id: UUID) -> RawCapture:
        """TODO(phase-1): fetch storage object, sniff type (transcript vs media)."""
        raise NotImplementedError("TODO(phase-1): upload ingestion")
