"""Idempotency keys for sync and webhooks — IMPLEMENTED (pure logic, no I/O).

Two kinds of keys keep the sync path exactly-once in effect (NFR-1):

* push keys: one stable key per (org, action item, destination). Stored on
  external_task_links; a retried/crashed push finds the link row instead of
  creating a duplicate external task (ARCH §4.2 step 2, §6 row "crash mid-job").

* webhook event keys: one stable key per (provider, event id). Unique-indexed in
  webhook_events; duplicate deliveries insert-conflict and are acknowledged
  without processing (ARCH §6 row 4).

Keys are SHA-256 based: fixed length, safe for DB indexes and for embedding in
external tools' custom fields, and never leak raw ids to third parties.
"""

from __future__ import annotations

import hashlib
import unicodedata
from uuid import UUID

_PUSH_PREFIX = "af-push"
_WEBHOOK_PREFIX = "af-hook"


def _digest(*parts: str) -> str:
    joined = "\x1f".join(parts)  # unit separator: unambiguous joining
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:32]


def push_key(org_id: UUID, action_item_id: UUID, destination: str) -> str:
    """Stable idempotency key for pushing one item to one destination.

    Args:
        org_id: owning org (tenancy invariant: keys never collide across orgs).
        action_item_id: the item being pushed.
        destination: adapter tool_name, e.g. "notion", "builtin".

    Returns:
        Key like ``af-push-<32 hex chars>``; identical inputs always produce
        identical keys, any changed input produces a different key.
    """
    dest = normalise_destination(destination)
    return f"{_PUSH_PREFIX}-{_digest(str(org_id), str(action_item_id), dest)}"


def webhook_event_key(provider: str, event_id: str) -> str:
    """Stable dedupe key for one webhook delivery.

    Args:
        provider: e.g. "stripe", "zoom", "linear" (case-insensitive).
        event_id: the provider's event identifier, used verbatim.

    Raises:
        ValueError: if either part is empty — a keyless event must never be
        silently deduped against other keyless events.
    """
    if not provider.strip() or not event_id.strip():
        raise ValueError("provider and event_id must be non-empty")
    return f"{_WEBHOOK_PREFIX}-{_digest(provider.strip().lower(), event_id.strip())}"


def normalise_destination(destination: str) -> str:
    """Canonicalise a destination name so key generation is stable.

    Lowercases, strips whitespace, and NFKC-normalises unicode, so "Notion",
    " notion " and a full-width variant all key identically.

    Raises:
        ValueError: if the result is empty.
    """
    canonical = unicodedata.normalize("NFKC", destination).strip().lower()
    if not canonical:
        raise ValueError("destination must be non-empty")
    return canonical
