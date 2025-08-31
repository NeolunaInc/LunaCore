# EventBus v1 - In-Process Pub/Sub System

## Overview

The EventBus is LunaCore's in-process publish/subscribe messaging system that enables decoupled communication between components. It supports wildcard pattern matching, guarantees FIFO event ordering, and is built on asyncio for high performance.

## API Reference

### InMemoryEventBus

Main event bus implementation with the following methods:

#### `async def start()`
Starts the event processing loop. Must be called before emitting events.

#### `async def stop()`
Stops the event processing loop and cleans up resources.

#### `def subscribe(pattern: str, handler: Callable[[BaseEvent], Any])`
Subscribes to events matching the pattern. Supports wildcards:
- `*` matches any sequence of characters
- `?` matches any single character

Examples:
- `task.*` matches `task.started`, `task.completed`, etc.
- `escalation.*` matches escalation events

#### `async def emit(event: BaseEvent)`
Emits an event to the bus. Events are processed asynchronously in FIFO order.

## Guarantees & Limitations

### Guarantees
- **FIFO Ordering**: Events are processed in the exact order they are emitted
- **Pattern Matching**: Wildcard support for flexible subscriptions
- **Async Safety**: Thread-safe for concurrent emit operations
- **No Message Loss**: All emitted events are eventually processed

### Limitations
- In-memory only (no persistence)
- Single process (no cross-process communication)
- No backpressure handling (unlimited queue)
- No event filtering beyond patterns

## Usage Example

```python
import asyncio
from services.event_bus import InMemoryEventBus
from core.events import TaskStartedEvent, TaskCompletedEvent

async def main():
    # Create and start bus
    bus = InMemoryEventBus()
    await bus.start()

    # Subscribe to task events
    async def task_handler(event):
        print(f"Task event: {event.type} for {event.task_id}")

    bus.subscribe("task.*", task_handler)

    # Emit events
    await bus.emit(TaskStartedEvent(task_id="task-123", agent_id="agent-1"))
    await bus.emit(TaskCompletedEvent(task_id="task-123", result="success"))

    # Wait for processing
    await asyncio.sleep(0.1)

    # Cleanup
    await bus.stop()

asyncio.run(main())
```

## Performance Benchmark

Benchmark results with 20,000 `task.started` events:

```
throughput: 224842.72 events/sec
```

The EventBus easily exceeds the 10k events/sec requirement for Phase 4 workloads.
