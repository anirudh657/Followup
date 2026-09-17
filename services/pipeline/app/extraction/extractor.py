"""LLM extraction pipeline: chunk -> call -> validate -> repair -> merge (FR-2.1).

Failure chain (ARCH §6 row 3), in order:
  1. validate response against schemas.LlmExtractionResult
  2. one repair pass: send validation errors back to the model
  3. one retry: stricter prompt, lower temperature
  4. fallback model (Settings.llm_fallback_model)
  5. meeting -> EXTRACTION_FAILED; raw response archived for prompt debugging

Cost accounting: every call records tokens per org (NFR-5 / FR-8.2 groundwork).
"""

from __future__ import annotations

from app.extraction.schemas import LlmExtractionResult
from app.models import Transcript


async def extract(transcript: Transcript, *, template: str | None = None) -> LlmExtractionResult:
    """Run structured extraction over a whole transcript.

    Args:
        transcript: normalised transcript (never a raw vendor format).
        template: optional meeting-template id biasing the prompt (FR-6.1).

    Returns:
        Merged, deduplicated extraction result across chunks.

    Raises:
        ExtractionFailedError: after the full repair/retry/fallback chain.

    TODO(phase-1): chunking, provider-agnostic client, validation chain, merge/dedupe.
    """
    raise NotImplementedError("TODO(phase-1): LLM extraction pipeline")


class ExtractionFailedError(RuntimeError):
    """Terminal extraction failure; raw model output has been archived."""
