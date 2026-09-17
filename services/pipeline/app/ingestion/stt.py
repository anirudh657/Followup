"""Speech-to-text provider interface (FR-1.2, provider choice = PRD OQ-6).

One interface, three planned implementations (AssemblyAI, Deepgram, local Whisper),
selected by Settings.stt_provider. Free credits on the hosted providers are capped —
cost flags live in README §Costs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class SttProviderClient(ABC):
    """Transcribes a stored media file into raw provider output text."""

    @abstractmethod
    async def transcribe(self, media_storage_path: str, *, language_hint: str | None) -> str:
        """Return the provider's transcript text for later normalisation.

        Raises:
            SttQuotaExceededError: free credits exhausted (surfaces as a cost flag).
        """


class SttQuotaExceededError(RuntimeError):
    """Provider quota/credits exhausted; job parks rather than burning retries."""


def get_stt_client() -> SttProviderClient:
    """Factory selecting the provider from settings.

    TODO(phase-1): implement AssemblyAI + one alternative after the OQ-6 benchmark.
    """
    raise NotImplementedError("TODO(phase-1): STT provider factory")
