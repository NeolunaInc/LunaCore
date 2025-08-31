import asyncio

import pytest

from core.events import BaseEvent, TaskCompletedEvent, TaskStartedEvent
from services.event_bus.bus_inmem import InMemoryEventBus


@pytest.mark.asyncio
async def test_basic_subscribe_emit():
    """Test basic subscribe and emit functionality."""
    bus = InMemoryEventBus()
    await bus.start()

    events_received = []

    async def handler(event):
        events_received.append(event)

    bus.subscribe("test.event", handler)

    event = BaseEvent(type="test.event", data="test data")
    await bus.emit(event)

    # Wait for event processing
    await asyncio.sleep(0.01)

    assert len(events_received) == 1
    assert events_received[0].type == "test.event"
    assert events_received[0].data == "test data"

    await bus.stop()


@pytest.mark.asyncio
async def test_wildcard_matching():
    """Test wildcard pattern matching."""
    bus = InMemoryEventBus()
    await bus.start()

    events_received = []

    async def handler(event):
        events_received.append(event)

    bus.subscribe("task.*", handler)

    # Emit different task events
    started_event = TaskStartedEvent(task_id="task1", agent_id="agent1")
    completed_event = TaskCompletedEvent(task_id="task1", result="success")

    await bus.emit(started_event)
    await bus.emit(completed_event)

    # Emit non-matching event
    other_event = BaseEvent(type="other.event")
    await bus.emit(other_event)

    await asyncio.sleep(0.01)

    assert len(events_received) == 2
    assert events_received[0].type == "task.started"
    assert events_received[1].type == "task.completed"

    await bus.stop()


@pytest.mark.asyncio
async def test_fifo_order():
    """Test that events are processed in FIFO order."""
    bus = InMemoryEventBus()
    await bus.start()

    events_received = []

    async def handler(event):
        events_received.append(event.data)

    bus.subscribe("test.*", handler)

    # Emit events in order
    await bus.emit(BaseEvent(type="test.event", data=1))
    await bus.emit(BaseEvent(type="test.event", data=2))
    await bus.emit(BaseEvent(type="test.event", data=3))

    await asyncio.sleep(0.01)

    assert events_received == [1, 2, 3]

    await bus.stop()


@pytest.mark.asyncio
async def test_concurrent_emit():
    """Test concurrent emission of events."""
    bus = InMemoryEventBus()
    await bus.start()

    events_received = []

    async def handler(event):
        events_received.append(event.data)

    bus.subscribe("test.event", handler)

    async def emit_event(data):
        await bus.emit(BaseEvent(type="test.event", data=data))

    # Emit concurrently
    await asyncio.gather(emit_event("A"), emit_event("B"), emit_event("C"))

    await asyncio.sleep(0.01)

    # All events should be received (order may vary due to concurrency)
    assert len(events_received) == 3
    assert set(events_received) == {"A", "B", "C"}

    await bus.stop()


@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test multiple subscribers to the same pattern."""
    bus = InMemoryEventBus()
    await bus.start()

    events1 = []
    events2 = []

    async def handler1(event):
        events1.append(event)

    async def handler2(event):
        events2.append(event)

    bus.subscribe("test.event", handler1)
    bus.subscribe("test.event", handler2)

    event = BaseEvent(type="test.event", data="test")
    await bus.emit(event)

    await asyncio.sleep(0.01)

    assert len(events1) == 1
    assert len(events2) == 1
    assert events1[0] == events2[0] == event

    await bus.stop()
