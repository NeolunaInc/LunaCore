import asyncio
from typing import Any

import pytest

from agents.resource_allocator.allocator import SimpleAllocator
from core.events import EscalationNeededEvent, TaskCompletedEvent, TaskFailedEvent, TaskStartedEvent
from orchestrator.execution_orchestrator import ExecutionOrchestrator
from services.event_bus.bus_inmem import InMemoryEventBus
from services.memory.mem_inmem import InMemProjectMemory


class SlowCallable:
    async def __call__(self):
        await asyncio.sleep(0.2)
        return "slow_result"


class FailingCallable:
    def __init__(self, fail_count: int):
        self.fail_count = fail_count
        self.attempts = 0

    async def __call__(self):
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise ValueError("simulated failure")
        return "ok"


class AlwaysFailCallable:
    async def __call__(self):
        raise ValueError("always fail")


@pytest.mark.asyncio
async def test_timeout_emits_failed_and_no_artifact():
    bus = InMemoryEventBus()
    memory = InMemProjectMemory()
    allocator = SimpleAllocator()

    orchestrator = ExecutionOrchestrator(bus, memory, allocator)

    events: list[Any] = []

    async def event_handler(event):
        events.append(event)

    await bus.start()
    bus.subscribe("task.*", event_handler)
    bus.subscribe("escalation.*", event_handler)

    steps = [{"id": "slow_step", "callable": SlowCallable(), "options": {"timeout": 0.05}}]

    with pytest.raises(asyncio.TimeoutError):
        await orchestrator.execute_plan(steps)

    await asyncio.sleep(0.1)  # Wait for events to process

    # Check events
    started_events = [e for e in events if isinstance(e, TaskStartedEvent)]
    failed_events = [e for e in events if isinstance(e, TaskFailedEvent)]
    completed_events = [e for e in events if isinstance(e, TaskCompletedEvent)]

    assert len(started_events) == 1
    assert len(failed_events) == 1
    assert len(completed_events) == 0

    # Check no artifact
    artifact = await memory.get("task:slow_step")
    assert artifact is None


@pytest.mark.asyncio
async def test_retries_then_success():
    bus = InMemoryEventBus()
    memory = InMemProjectMemory()
    allocator = SimpleAllocator()

    orchestrator = ExecutionOrchestrator(bus, memory, allocator)

    events: list[Any] = []

    async def event_handler(event):
        events.append(event)

    await bus.start()
    bus.subscribe("task.*", event_handler)

    failing_callable = FailingCallable(fail_count=2)

    steps = [{"id": "retry_step", "callable": failing_callable, "options": {"retries": 2}}]

    results = await orchestrator.execute_plan(steps)

    await asyncio.sleep(0.1)  # Wait for events to process

    # Check results
    assert len(results) == 1
    assert results[0] == "ok"

    # Check events
    started_events = [e for e in events if isinstance(e, TaskStartedEvent)]
    failed_events = [e for e in events if isinstance(e, TaskFailedEvent)]
    completed_events = [e for e in events if isinstance(e, TaskCompletedEvent)]

    assert len(started_events) == 3  # 3 attempts
    assert len(failed_events) == 2  # 2 failures
    assert len(completed_events) == 1  # 1 success

    # Check artifact
    artifact = await memory.get("task:retry_step")
    assert artifact is not None
    assert artifact.data == "ok"
    assert artifact.version == 1


@pytest.mark.asyncio
async def test_escalation_on_final_failure():
    bus = InMemoryEventBus()
    memory = InMemProjectMemory()
    allocator = SimpleAllocator()

    orchestrator = ExecutionOrchestrator(bus, memory, allocator)

    events: list[Any] = []

    async def event_handler(event):
        events.append(event)

    await bus.start()
    bus.subscribe("task.*", event_handler)
    bus.subscribe("escalation.*", event_handler)

    steps = [
        {
            "id": "fail_step",
            "callable": AlwaysFailCallable(),
            "options": {"retries": 1, "escalate_on_failure": True},
        }
    ]

    with pytest.raises(ValueError):
        await orchestrator.execute_plan(steps)

    await asyncio.sleep(0.1)  # Wait for events to process

    # Check events
    started_events = [e for e in events if isinstance(e, TaskStartedEvent)]
    failed_events = [e for e in events if isinstance(e, TaskFailedEvent)]
    escalation_events = [e for e in events if isinstance(e, EscalationNeededEvent)]

    assert len(started_events) == 2  # 2 attempts
    assert len(failed_events) == 2  # 2 failures
    assert len(escalation_events) == 1  # 1 escalation
