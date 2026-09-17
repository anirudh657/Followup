"""Tests for app.extraction.schemas (implemented module)."""

import pytest
from pydantic import ValidationError

from app.extraction.schemas import LlmActionItem, LlmExtractionResult


def valid_item(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "title": "Email the contract to Priya",
        "owner_name": "Anirudh",
        "owner_inferred": False,
        "due_date_iso": "2026-10-01",
        "due_inferred": False,
        "source_quote": "I'll email the contract to Priya by the 1st.",
        "confidence": 0.92,
    }
    base.update(overrides)
    return base


def test_valid_item_parses() -> None:
    item = LlmActionItem.model_validate(valid_item())
    assert item.due_date_iso == "2026-10-01"


def test_hallucinated_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        LlmActionItem.model_validate(valid_item(priority="urgent"))


def test_bad_date_format_is_rejected() -> None:
    with pytest.raises(ValidationError):
        LlmActionItem.model_validate(valid_item(due_date_iso="next Tuesday"))


def test_confidence_out_of_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        LlmActionItem.model_validate(valid_item(confidence=1.5))


def test_empty_result_is_legal_and_detectable() -> None:
    result = LlmExtractionResult.model_validate({})
    assert result.is_empty() is True


def test_round_trip_through_json() -> None:
    result = LlmExtractionResult(action_items=[LlmActionItem.model_validate(valid_item())])
    again = LlmExtractionResult.model_validate_json(result.model_dump_json())
    assert again == result
    assert again.is_empty() is False
