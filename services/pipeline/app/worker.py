"""Job-queue worker process entrypoint (``python -m app.worker``).

Claims jobs from the Postgres queue (SELECT ... FOR UPDATE SKIP LOCKED, lease TTL,
dead-lettering — docs/ARCHITECTURE.md §1 and §6) and dispatches them to handlers:
transcribe, extract, sync_push, sync_poll, followup_send, report_generate.

All handlers must be idempotent: a job may run more than once after a crash.
"""

from __future__ import annotations


def main() -> None:
    """Run the worker loop until terminated.

    TODO(phase-1): implement queue claiming, lease renewal, handler dispatch,
    retry with exponential backoff + jitter, and dead-letter routing.
    """
    raise NotImplementedError("TODO(phase-1): job queue worker loop")


if __name__ == "__main__":
    main()
