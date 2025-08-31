import asyncio
import os
import time

import pytest

from core.events import TaskStartedEvent
from services.event_bus.bus_inmem import InMemoryEventBus


@pytest.mark.asyncio
async def test_throughput_10k():
    """Test EventBus throughput >= 10k events/sec."""
    if "LUNACORE_PERF" not in os.environ:
        pytest.skip("Performance test skipped, set LUNACORE_PERF=1 to run")

    bus = InMemoryEventBus()
    await bus.start()

    counter = 0

    async def handler(event):
        nonlocal counter
        counter += 1

    bus.subscribe("task.*", handler)

    N = 20000
    start = time.perf_counter()

    for i in range(N):
        event = TaskStartedEvent(task_id=f"task{i}", agent_id="bench")
        await bus.emit(event)

    # Wait for all events to be processed
    while counter < N:
        await asyncio.sleep(0.001)

    end = time.perf_counter()
    duration = end - start
    throughput = N / duration

    print(f"throughput: {throughput:.2f} events/sec")

    await bus.stop()

    assert throughput >= 10000, f"Throughput {throughput:.2f} < 10000 events/sec"
