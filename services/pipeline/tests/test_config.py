"""Tests for app.config (implemented module)."""

import pytest

from app.config import AppEnv, Settings, SttProvider


def make_settings(**overrides: object) -> Settings:
    """Settings isolated from the developer's real .env / environment."""
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def test_defaults_are_local_and_safe() -> None:
    s = make_settings()
    assert s.app_env is AppEnv.LOCAL
    assert s.is_production is False
    assert s.stt_provider is SttProvider.ASSEMBLYAI


def test_secrets_do_not_leak_via_repr() -> None:
    s = make_settings(anthropic_api_key="sk-super-secret")
    assert "sk-super-secret" not in repr(s)
    assert s.anthropic_api_key.get_secret_value() == "sk-super-secret"


def test_require_passes_when_set() -> None:
    s = make_settings(stripe_secret_key="sk_test_123", stripe_webhook_secret="whsec_1")
    s.require("stripe_secret_key", "stripe_webhook_secret")  # must not raise


def test_require_names_every_missing_variable() -> None:
    s = make_settings()
    with pytest.raises(RuntimeError) as err:
        s.require("stripe_secret_key", "resend_api_key")
    message = str(err.value)
    assert "STRIPE_SECRET_KEY" in message
    assert "RESEND_API_KEY" in message


def test_env_parsing_of_enum(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.app_env is AppEnv.PRODUCTION
    assert s.is_production is True
