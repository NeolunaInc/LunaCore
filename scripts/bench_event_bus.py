import asyncio
import time

from core.events import TaskStartedEvent
from services.event_bus.bus_inmem import InMemoryEventBus


async def main():
    """Benchmark EventBus throughput with 20k task.started events."""
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


if __name__ == "__main__":
    asyncio.run(main())
