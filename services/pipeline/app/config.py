"""Application configuration — IMPLEMENTED.

All environment access happens here and only here; the rest of the codebase imports
`Settings` (usually via `get_settings()`). Every variable is documented in the repo-root
`.env.example`. Secrets are typed as `SecretStr` so they can't leak via repr/logging.

Phase gating: variables needed by later phases (Stripe, Resend, OAuth apps) are optional
at startup; the modules that need them call `Settings.require(...)` so a misconfigured
deploy fails loudly at the point of use with a message naming the missing variable.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    """Deployment environment; switches logging and safety rails."""

    LOCAL = "local"
    PREVIEW = "preview"
    PRODUCTION = "production"


class SttProvider(StrEnum):
    """Speech-to-text provider selection (PRD OQ-6)."""

    ASSEMBLYAI = "assemblyai"
    DEEPGRAM = "deepgram"
    WHISPER_LOCAL = "whisper_local"


class Settings(BaseSettings):
    """Typed view of the process environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Core wiring ────────────────────────────────────────────────────────
    app_env: AppEnv = AppEnv.LOCAL
    log_level: str = "INFO"
    app_base_url: str = "http://localhost:3000"

    # ── Supabase ───────────────────────────────────────────────────────────
    next_public_supabase_url: str = Field(default="", alias="NEXT_PUBLIC_SUPABASE_URL")
    supabase_service_role_key: SecretStr = SecretStr("")
    database_url: SecretStr = SecretStr("")
    supabase_jwt_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"

    # ── LLM ────────────────────────────────────────────────────────────────
    anthropic_api_key: SecretStr = SecretStr("")
    openai_api_key: SecretStr = SecretStr("")
    groq_api_key: SecretStr = SecretStr("")
    llm_primary_model: str = ""
    llm_fallback_model: str = ""
    llm_org_monthly_token_cap: int = 2_000_000

    # ── STT ────────────────────────────────────────────────────────────────
    stt_provider: SttProvider = SttProvider.ASSEMBLYAI
    assemblyai_api_key: SecretStr = SecretStr("")
    deepgram_api_key: SecretStr = SecretStr("")

    # ── Security ───────────────────────────────────────────────────────────
    token_encryption_key: SecretStr = SecretStr("")

    # ── Email (phase 3) ────────────────────────────────────────────────────
    resend_api_key: SecretStr = SecretStr("")
    followup_from_email: str = ""

    # ── Stripe (phase 4) ───────────────────────────────────────────────────
    stripe_secret_key: SecretStr = SecretStr("")
    stripe_webhook_secret: SecretStr = SecretStr("")
    stripe_price_pro_seat: str = ""
    stripe_price_team_seat: str = ""

    # ── Meeting platforms / tool OAuth (phase 2/5) ─────────────────────────
    zoom_client_id: str = ""
    zoom_client_secret: SecretStr = SecretStr("")
    zoom_webhook_secret_token: SecretStr = SecretStr("")
    google_oauth_client_id: str = ""
    google_oauth_client_secret: SecretStr = SecretStr("")
    notion_client_id: str = ""
    notion_client_secret: SecretStr = SecretStr("")
    linear_client_id: str = ""
    linear_client_secret: SecretStr = SecretStr("")

    # ── Observability ──────────────────────────────────────────────────────
    sentry_dsn_pipeline: str = ""

    def require(self, *field_names: str) -> None:
        """Assert that the named settings are non-empty.

        Called by phase-gated modules at their entry points so a missing variable
        fails with an actionable message instead of a downstream 401 from a vendor.

        Raises:
            RuntimeError: naming every missing variable.
        """
        missing: list[str] = []
        for name in field_names:
            value = getattr(self, name)
            raw = value.get_secret_value() if isinstance(value, SecretStr) else value
            if raw in ("", None):
                missing.append(name.upper())
        if missing:
            raise RuntimeError(
                "Missing required configuration: "
                + ", ".join(missing)
                + " (see .env.example at the repo root)"
            )

    @property
    def is_production(self) -> bool:
        return self.app_env is AppEnv.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings singleton (cached; tests construct Settings directly)."""
    return Settings()
