"""Ingestion interfaces: sources produce raw material, the normaliser makes Transcripts.

Design: per-source connectors only *acquire* content (native transcript file, or media
that still needs STT). They never parse into domain models themselves — normalisation
is one shared, well-tested funnel so nothing downstream ever sees a vendor format (FR-1.6).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.models import Transcript, TranscriptSource


@dataclass(frozen=True)
class RawCapture:
    """What a source hands to the normaliser: either transcript text or media to transcribe."""

    org_id: UUID
    meeting_id: UUID
    source: TranscriptSource
    transcript_payload: str | None
    """Native transcript content (VTT/SRT/JSON/plain text), if the source provides one."""
    media_storage_path: str | None
    """Supabase Storage path of an audio/video file needing STT, if no transcript."""


class MeetingSource(ABC):
    """Common interface for all meeting sources (upload, Zoom, Meet, Teams)."""

    @abstractmethod
    async def acquire(self, org_id: UUID, meeting_id: UUID) -> RawCapture:
        """Fetch this meeting's raw content from the source.

        Raises:
            SourceUnavailableError: transient vendor failure (job will retry).
            SourceAuthError: token expired/revoked -> integration parks as needs_reauth.
        """


class SourceUnavailableError(RuntimeError):
    """Transient acquisition failure; safe to retry."""


class SourceAuthError(RuntimeError):
    """Authentication/authorization failure; requires user re-auth, do not retry."""


def normalise(capture: RawCapture, *, stt_text: str | None = None) -> Transcript:
    """Turn a RawCapture (+ STT output when media) into the internal Transcript.

    Includes format detection (VTT/SRT/JSON/plain), speaker labelling, and the
    garbage gate (FR-1.7): empty, non-speech, unsupported language or oversized
    input must raise GarbageTranscriptError with a user-readable reason code
    BEFORE any LLM cost is incurred (ARCH §6 row 1).

    TODO(phase-1): implement parsers + heuristics; property-test on fixture files.
    """
    raise NotImplementedError("TODO(phase-1): transcript normalisation")


class GarbageTranscriptError(ValueError):
    """Raised by normalise(); carries a reason code shown to the user."""

    def __init__(self, reason_code: str, detail: str) -> None:
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")
