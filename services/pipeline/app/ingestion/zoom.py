"""Zoom source (FR-1.3): OAuth app + recording.completed webhook -> native transcript.

Requires the meeting host to have cloud recording (paid Zoom plan) — PRD OQ-1.
Webhook intake itself lives in main.py routes; this module fetches the artifacts.
"""

from __future__ import annotations

from uuid import UUID

from app.ingestion.base import MeetingSource, RawCapture


class ZoomSource(MeetingSource):
    """Downloads the native Zoom transcript (preferred) or the recording."""

    async def acquire(self, org_id: UUID, meeting_id: UUID) -> RawCapture:
        """TODO(phase-5): Zoom API download with token refresh via the integration store."""
        raise NotImplementedError("TODO(phase-5): Zoom ingestion")
