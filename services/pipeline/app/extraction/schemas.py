"""LLM structured-output schemas — IMPLEMENTED (pure Pydantic, no I/O).

These are the contract between us and the model: the extraction prompt instructs the
LLM to emit exactly this JSON shape (via the provider's structured-output/tool-use
mode), and every response is validated against these models before anything else
touches it (ARCH §6 row 3 — malformed output is a first-class failure mode).

They are deliberately separate from the domain models in app.models: the LLM never
sees or produces UUIDs, org ids, or review state. Mapping LLM output -> domain
objects happens in extractor.py after validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LlmActionItem(BaseModel):
    """One action item as the model must emit it."""

    model_config = ConfigDict(extra="forbid")  # hallucinated fields = validation error

    title: str = Field(min_length=3, max_length=300, description="Imperative, specific.")
    description: str = Field(default="", max_length=2000)
    owner_name: str | None = Field(
        default=None, description="Speaker name as heard; null if genuinely unowned."
    )
    owner_inferred: bool = Field(
        description="True if the owner was implied rather than explicitly stated."
    )
    due_date_iso: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="ISO date if a deadline was stated or clearly implied, else null.",
    )
    due_inferred: bool = Field(description="True if the date was implied, not stated.")
    source_quote: str = Field(
        min_length=1, max_length=1000, description="Verbatim span supporting this item."
    )
    confidence: float = Field(ge=0.0, le=1.0)


class LlmDecision(BaseModel):
    """A decision the group made."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=3, max_length=1000)
    source_quote: str = Field(min_length=1, max_length=1000)
    confidence: float = Field(ge=0.0, le=1.0)


class LlmOpenQuestion(BaseModel):
    """A question raised and not resolved in the meeting."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=3, max_length=1000)
    raised_by: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class LlmExtractionResult(BaseModel):
    """Top-level object the model must return for one transcript chunk."""

    model_config = ConfigDict(extra="forbid")

    action_items: list[LlmActionItem] = Field(default_factory=list)
    decisions: list[LlmDecision] = Field(default_factory=list)
    open_questions: list[LlmOpenQuestion] = Field(default_factory=list)

    def is_empty(self) -> bool:
        """True when the model found nothing — legal for e.g. a social call."""
        return not (self.action_items or self.decisions or self.open_questions)
