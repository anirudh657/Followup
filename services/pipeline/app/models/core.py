"""Core domain models — IMPLEMENTED.

These Pydantic models are the shared vocabulary of the whole pipeline: ingestion
produces `Transcript`s, extraction produces `ActionItem`s/`Decision`s/`OpenQuestion`s,
sync and reports consume them. They deliberately mirror (but are not coupled to) the
Postgres schema; DB rows are validated into these models at the repository boundary.

Multi-tenancy invariant (docs/ARCHITECTURE.md §5): every tenant-owned model carries a
non-optional ``org_id``.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OrgRole(StrEnum):
    """Membership roles within an org (FR-7.2)."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class MeetingStatus(StrEnum):
    """Lifecycle of a meeting through the ingestion path (ARCH §4.1)."""

    CREATED = "created"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    EXTRACTING = "extracting"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    FAILED = "failed"
    EXTRACTION_FAILED = "extraction_failed"


class TaskStatus(StrEnum):
    """Canonical task states; adapters map external states onto these (FR-3.1)."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class ItemReviewState(StrEnum):
    """Review gate for extracted items (FR-2.4): nothing syncs before APPROVED."""

    SUGGESTED = "suggested"
    APPROVED = "approved"
    REJECTED = "rejected"


class TranscriptSource(StrEnum):
    """Where a transcript came from (FR-1.6)."""

    UPLOAD_TRANSCRIPT = "upload_transcript"
    UPLOAD_RECORDING = "upload_recording"
    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    MS_TEAMS = "ms_teams"


class Utterance(BaseModel):
    """One speaker turn in a normalised transcript."""

    model_config = ConfigDict(frozen=True)

    speaker: str = Field(min_length=1, description="Speaker label as given by the source.")
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def _end_after_start(self) -> Utterance:
        if self.end_ms < self.start_ms:
            raise ValueError("end_ms must be >= start_ms")
        return self


class Transcript(BaseModel):
    """The single internal transcript format every source is normalised into (FR-1.6)."""

    org_id: UUID
    meeting_id: UUID
    source: TranscriptSource
    language: str = Field(default="en", min_length=2, max_length=8)
    duration_ms: int = Field(ge=0)
    utterances: list[Utterance] = Field(min_length=1)

    @property
    def speakers(self) -> list[str]:
        """Distinct speaker labels in order of first appearance."""
        seen: dict[str, None] = {}
        for u in self.utterances:
            seen.setdefault(u.speaker, None)
        return list(seen)

    @property
    def word_count(self) -> int:
        return sum(len(u.text.split()) for u in self.utterances)


class Confidence(BaseModel):
    """Confidence score with the UI bucketing rule in one place (FR-2.2).

    ``needs_review`` is the product behaviour: LOW always flags; MEDIUM flags
    when the owner or due date was inferred rather than stated.
    """

    model_config = ConfigDict(frozen=True)

    score: float = Field(ge=0.0, le=1.0)

    LOW_THRESHOLD: float = 0.5
    HIGH_THRESHOLD: float = 0.8

    @property
    def bucket(self) -> str:
        if self.score < self.LOW_THRESHOLD:
            return "low"
        if self.score < self.HIGH_THRESHOLD:
            return "medium"
        return "high"

    def needs_review(self, *, owner_inferred: bool = False, due_inferred: bool = False) -> bool:
        if self.bucket == "low":
            return True
        return self.bucket == "medium" and (owner_inferred or due_inferred)


class ActionItem(BaseModel):
    """An extracted, reviewable, syncable unit of work (FR-2.1)."""

    id: UUID
    org_id: UUID
    project_id: UUID
    meeting_id: UUID
    title: str = Field(min_length=3, max_length=300)
    description: str = ""
    owner_user_id: UUID | None = Field(
        default=None, description="Mapped org member, when the speaker matched (FR-2.3)."
    )
    owner_freetext: str | None = Field(
        default=None, description="Unmapped owner name from the transcript."
    )
    due_date: date | None = None
    source_quote: str = Field(
        default="", description="Verbatim transcript span the item was derived from."
    )
    source_start_ms: int | None = Field(default=None, ge=0)
    confidence: Confidence
    review_state: ItemReviewState = ItemReviewState.SUGGESTED
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def _title_not_placeholder(cls, v: str) -> str:
        if v.strip().lower() in {"tbd", "todo", "n/a", "action item"}:
            raise ValueError("title must be a real action, not a placeholder")
        return v.strip()

    @property
    def is_syncable(self) -> bool:
        """Only approved items may leave ActionFlow (FR-2.4 / ARCH §4.1 step 5)."""
        return self.review_state is ItemReviewState.APPROVED


class Decision(BaseModel):
    """A decision recorded in a meeting (feeds summaries and reports)."""

    id: UUID
    org_id: UUID
    meeting_id: UUID
    text: str = Field(min_length=3)
    source_quote: str = ""
    confidence: Confidence


class OpenQuestion(BaseModel):
    """An unresolved question raised in a meeting."""

    id: UUID
    org_id: UUID
    meeting_id: UUID
    text: str = Field(min_length=3)
    raised_by: str | None = None
    confidence: Confidence
