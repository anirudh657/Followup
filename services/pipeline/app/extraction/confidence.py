"""Confidence scoring: model self-report + heuristics -> final Confidence (FR-2.2).

The bucketing/needs-review rules are pure logic and already implemented on
app.models.Confidence. This module computes the *score* that feeds them, blending:
  - the model's self-reported confidence,
  - heuristic penalties (owner/due inferred, weak source quote overlap with the
    transcript, chunk-boundary items),
  - calibration learned from the labelled eval set (NFR-6).
"""

from __future__ import annotations

from app.extraction.schemas import LlmActionItem
from app.models import Confidence, Transcript


def score_item(item: LlmActionItem, transcript: Transcript) -> Confidence:
    """Compute the calibrated confidence for one extracted item.

    TODO(phase-1): implement blending + calibrate thresholds on the eval set.
    """
    raise NotImplementedError("TODO(phase-1): confidence scoring")
