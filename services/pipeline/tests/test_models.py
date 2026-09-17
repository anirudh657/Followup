"""Tests for app.models.core (implemented module)."""

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models import (
    ActionItem,
    Confidence,
    ItemReviewState,
    TaskStatus,
    Transcript,
    TranscriptSource,
    Utterance,
)


def utterance(speaker: str = "Anirudh", start: int = 0, end: int = 1000) -> Utterance:
    return Utterance(speaker=speaker, start_ms=start, end_ms=end, text="Let us ship it")


def make_item(**overrides: object) -> ActionItem:
    base: dict[str, object] = {
        "id": uuid4(),
        "org_id": uuid4(),
        "project_id": uuid4(),
        "meeting_id": uuid4(),
        "title": "Send the revised proposal to the client",
        "confidence": Confidence(score=0.9),
    }
    base.update(overrides)
    return ActionItem.model_validate(base)


class TestUtterance:
    def test_rejects_end_before_start(self) -> None:
        with pytest.raises(ValidationError):
            Utterance(speaker="A", start_ms=500, end_ms=100, text="hi")

    def test_is_frozen(self) -> None:
        u = utterance()
        with pytest.raises(ValidationError):
            u.text = "changed"  # type: ignore[misc]


class TestTranscript:
    def test_speakers_in_order_of_first_appearance(self) -> None:
        t = Transcript(
            org_id=uuid4(),
            meeting_id=uuid4(),
            source=TranscriptSource.UPLOAD_TRANSCRIPT,
            duration_ms=60_000,
            utterances=[
                utterance("Vedant", 0, 100),
                utterance("Anirudh", 100, 200),
                utterance("Vedant", 200, 300),
            ],
        )
        assert t.speakers == ["Vedant", "Anirudh"]

    def test_requires_at_least_one_utterance(self) -> None:
        with pytest.raises(ValidationError):
            Transcript(
                org_id=uuid4(),
                meeting_id=uuid4(),
                source=TranscriptSource.ZOOM,
                duration_ms=0,
                utterances=[],
            )

    def test_word_count(self) -> None:
        t = Transcript(
            org_id=uuid4(),
            meeting_id=uuid4(),
            source=TranscriptSource.UPLOAD_TRANSCRIPT,
            duration_ms=1000,
            utterances=[utterance(), utterance()],
        )
        assert t.word_count == 8  # "Let us ship it" x 2


class TestConfidence:
    @pytest.mark.parametrize(
        ("score", "bucket"),
        [
            (0.0, "low"),
            (0.49, "low"),
            (0.5, "medium"),
            (0.79, "medium"),
            (0.8, "high"),
            (1.0, "high"),
        ],
    )
    def test_buckets(self, score: float, bucket: str) -> None:
        assert Confidence(score=score).bucket == bucket

    def test_low_always_needs_review(self) -> None:
        assert Confidence(score=0.2).needs_review() is True

    def test_medium_needs_review_only_when_inferred(self) -> None:
        c = Confidence(score=0.6)
        assert c.needs_review() is False
        assert c.needs_review(owner_inferred=True) is True
        assert c.needs_review(due_inferred=True) is True

    def test_high_never_needs_review(self) -> None:
        assert Confidence(score=0.95).needs_review(owner_inferred=True) is False

    def test_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Confidence(score=1.2)


class TestActionItem:
    def test_review_gate_controls_syncability(self) -> None:
        item = make_item()
        assert item.review_state is ItemReviewState.SUGGESTED
        assert item.is_syncable is False
        approved = item.model_copy(update={"review_state": ItemReviewState.APPROVED})
        assert approved.is_syncable is True

    def test_placeholder_titles_rejected(self) -> None:
        with pytest.raises(ValidationError):
            make_item(title="TBD")

    def test_defaults(self) -> None:
        item = make_item()
        assert item.status is TaskStatus.TODO
        assert item.due_date is None

    def test_accepts_real_due_date(self) -> None:
        item = make_item(due_date=date(2026, 10, 1))
        assert item.due_date == date(2026, 10, 1)
