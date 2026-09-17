"""Tests for app.sync.idempotency (implemented module)."""

from uuid import uuid4

import pytest

from app.sync.idempotency import normalise_destination, push_key, webhook_event_key


class TestPushKey:
    def test_deterministic(self) -> None:
        org, item = uuid4(), uuid4()
        assert push_key(org, item, "notion") == push_key(org, item, "notion")

    def test_changes_with_every_input(self) -> None:
        org, item = uuid4(), uuid4()
        base = push_key(org, item, "notion")
        assert push_key(uuid4(), item, "notion") != base  # org isolation
        assert push_key(org, uuid4(), "notion") != base
        assert push_key(org, item, "linear") != base

    def test_destination_is_canonicalised(self) -> None:
        org, item = uuid4(), uuid4()
        assert push_key(org, item, " Notion ") == push_key(org, item, "notion")

    def test_shape_is_index_and_embed_friendly(self) -> None:
        key = push_key(uuid4(), uuid4(), "jira")
        assert key.startswith("af-push-")
        assert len(key) == len("af-push-") + 32


class TestWebhookEventKey:
    def test_deterministic_and_provider_case_insensitive(self) -> None:
        assert webhook_event_key("Stripe", "evt_123") == webhook_event_key("stripe", "evt_123")

    def test_distinct_across_providers_and_events(self) -> None:
        a = webhook_event_key("stripe", "evt_1")
        assert webhook_event_key("zoom", "evt_1") != a
        assert webhook_event_key("stripe", "evt_2") != a

    def test_event_id_is_case_sensitive(self) -> None:
        assert webhook_event_key("stripe", "EVT_1") != webhook_event_key("stripe", "evt_1")

    @pytest.mark.parametrize(("provider", "event_id"), [("", "evt"), ("stripe", ""), (" ", " ")])
    def test_empty_parts_rejected(self, provider: str, event_id: str) -> None:
        with pytest.raises(ValueError):
            webhook_event_key(provider, event_id)


class TestNormaliseDestination:
    def test_unicode_nfkc(self) -> None:
        assert normalise_destination("ｎｏｔｉｏｎ") == "notion"  # full-width -> ascii

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError):
            normalise_destination("   ")
