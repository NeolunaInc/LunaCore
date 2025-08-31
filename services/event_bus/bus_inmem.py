import asyncio
import contextlib
import fnmatch
from collections.abc import Callable
from typing import Any

from core.events import BaseEvent


class InMemoryEventBus:
    """In-memory event bus with pub/sub pattern matching and FIFO queue."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start the event bus processing."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._process_queue())

    async def stop(self):
        """Stop the event bus processing."""
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    def subscribe(self, pattern: str, handler: Callable[[BaseEvent], Any]):
        """Subscribe to events matching the pattern (supports wildcards)."""
        if pattern not in self._subscribers:
            self._subscribers[pattern] = []
        self._subscribers[pattern].append(handler)

    async def emit(self, event: BaseEvent):
        """Emit an event to the bus."""
        await self._queue.put(event)

    async def _process_queue(self):
        """Process events from the queue in FIFO order."""
        while self._running:
            try:
                event = await self._queue.get()
                await self._handle_event(event)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error, but continue processing
                print(f"Error processing event: {e}")

    async def _handle_event(self, event: BaseEvent):
        """Handle a single event by calling matching subscribers."""
        for pattern, handlers in self._subscribers.items():
            if fnmatch.fnmatch(event.type, pattern):
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            # Run sync handler in thread pool
                            await asyncio.get_event_loop().run_in_executor(None, handler, event)
                    except Exception as e:
                        print(f"Error in handler for {pattern}: {e}")
