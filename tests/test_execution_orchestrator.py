import asyncio

import pytest

from agents.resource_allocator.allocator import SimpleAllocator
from core.events import TaskCompletedEvent, TaskStartedEvent
from orchestrator.execution_orchestrator import ExecutionOrchestrator
from services.event_bus.bus_inmem import InMemoryEventBus
from services.memory.mem_inmem import InMemProjectMemory


@pytest.mark.asyncio
async def test_execution_orchestrator_sequential():
    """Test sequential execution of a plan with event emission and artifact storage."""

    # Setup components
    bus = InMemoryEventBus()
    memory = InMemProjectMemory()
    allocator = SimpleAllocator()

    orchestrator = ExecutionOrchestrator(bus, memory, allocator)

    # Start the event bus
    await bus.start()

    # Track events
    events_received = []

    async def event_handler(event):
        events_received.append(event)

    # Subscribe to task events
    bus.subscribe("task.*", event_handler)

    # Define fake steps
    def step1():
        return "result1"

    async def step2():
        await asyncio.sleep(0.01)  # Simulate async work
        return "result2"

    def step3():
        return "result3"

    steps = [
        {"id": "task1", "callable": step1},
        {"id": "task2", "callable": step2},
        {"id": "task3", "callable": step3},
    ]

    # Execute the plan
    results = await orchestrator.execute_plan(steps)

    # Wait for event processing to complete
    await asyncio.sleep(0.1)

    # Verify results
    assert results == ["result1", "result2", "result3"]

    # Verify events (should be in FIFO order)
    expected_events = [
        TaskStartedEvent(task_id="task1", agent_id="orchestrator"),
        TaskCompletedEvent(task_id="task1", result="result1"),
        TaskStartedEvent(task_id="task2", agent_id="orchestrator"),
        TaskCompletedEvent(task_id="task2", result="result2"),
        TaskStartedEvent(task_id="task3", agent_id="orchestrator"),
        TaskCompletedEvent(task_id="task3", result="result3"),
    ]

    assert len(events_received) == 6
    for i, expected in enumerate(expected_events):
        assert events_received[i].type == expected.type
        assert events_received[i].task_id == expected.task_id
        if hasattr(expected, "result"):
            assert events_received[i].result == expected.result

    # Verify artifacts in memory
    versions = await memory.list_versions("task:task1")
    assert versions == [1]

    artifact = await memory.get("task:task1")
    assert artifact is not None
    assert artifact.data == "result1"
    assert artifact.meta["step"] == 0
    assert artifact.meta["step_id"] == "task1"

    artifact2 = await memory.get("task:task2")
    assert artifact2 is not None
    assert artifact2.data == "result2"
    assert artifact2.meta["step"] == 1

    artifact3 = await memory.get("task:task3")
    assert artifact3 is not None
    assert artifact3.data == "result3"
    assert artifact3.meta["step"] == 2

    # Stop the bus
    await bus.stop()


@pytest.mark.asyncio
async def test_allocator_resolve():
    """Test the SimpleAllocator resolve method."""
    allocator = SimpleAllocator()

    # Valid step
    step = {"id": "test", "callable": lambda: "test"}
    callable_func = allocator.resolve(step)
    assert callable_func() == "test"

    # Invalid step
    with pytest.raises(ValueError, match="No callable found"):
        allocator.resolve({"id": "invalid"})
