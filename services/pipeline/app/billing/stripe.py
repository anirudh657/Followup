"""Stripe integration (FR-8.1, FR-8.3): checkout, portal, webhook-driven entitlements.

Webhook handling follows the standard dedupe pattern (webhook_events insert-first,
ARCH §6 row 4) and drives a local entitlement state machine: free -> pro -> team,
with a grace period on payment failure. Stripe charges per-transaction fees
(README §Costs).
"""

from __future__ import annotations

from uuid import UUID


async def create_checkout_session(org_id: UUID, price_id: str) -> str:
    """Return a Stripe Checkout URL for upgrading this org.

    TODO(phase-4): Stripe client + success/cancel routing.
    """
    raise NotImplementedError("TODO(phase-4): Stripe checkout")


async def handle_webhook_event(payload: bytes, signature_header: str) -> None:
    """Verify, dedupe, and apply one Stripe webhook event to entitlement state.

    TODO(phase-4): signature verification, event dedupe, entitlement transitions,
    payment-failure grace period.
    """
    raise NotImplementedError("TODO(phase-4): Stripe webhook handling")
