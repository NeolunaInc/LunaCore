import asyncio
from collections.abc import Callable
from typing import Any

from core.events import BaseEvent


class DLQ:
    """Dead Letter Queue for failed events with retry logic."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.failed_events: list[tuple[BaseEvent, int]] = []  # (event, retry_count)
        self.handlers: list[Callable[[BaseEvent], Any]] = []

    def add_handler(self, handler: Callable[[BaseEvent], Any]) -> None:
        """Add a handler for processing events."""
        self.handlers.append(handler)

    def enqueue_failed(self, event: BaseEvent, retry_count: int = 0) -> None:
        """Enqueue a failed event for retry or DLQ."""
        if retry_count < self.max_retries:
            # Schedule retry
            asyncio.create_task(self._retry_event(event, retry_count))
        else:
            # Move to DLQ
            self.failed_events.append((event, retry_count))

    async def _retry_event(self, event: BaseEvent, retry_count: int) -> None:
        """Retry processing the event."""
        await asyncio.sleep(0.1 * (2**retry_count))  # Exponential backoff
        try:
            for handler in self.handlers:
                await handler(event) if asyncio.iscoroutinefunction(handler) else handler(event)
        except Exception:
            # Failed again, enqueue with incremented retry count
            self.enqueue_failed(event, retry_count + 1)

    def get_failed_events(self) -> list[tuple[BaseEvent, int]]:
        """Get all events in the DLQ."""
        return self.failed_events.copy()

    def clear_dlq(self) -> None:
        """Clear the DLQ (for testing)."""
        self.failed_events.clear()
