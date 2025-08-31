import asyncio
from typing import Any

from agents.resource_allocator.allocator import SimpleAllocator
from core.events import TaskCompletedEvent, TaskStartedEvent
from services.event_bus.bus_inmem import InMemoryEventBus
from services.memory.interface import ProjectMemory


class ExecutionOrchestrator:
    """Sequential execution orchestrator for task plans."""

    def __init__(self, bus: InMemoryEventBus, memory: ProjectMemory, allocator: "SimpleAllocator"):
        self.bus = bus
        self.memory = memory
        self.allocator = allocator

    async def execute_plan(self, steps: list[dict[str, Any]]) -> list[Any]:
        """Execute a plan of steps sequentially.

        Args:
            steps: List of step dictionaries with 'id', 'callable', etc.

        Returns:
            List of results from each step
        """
        results = []

        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i}")
            callable_func = self.allocator.resolve(step)

            # Emit task started event
            started_event = TaskStartedEvent(task_id=step_id, agent_id="orchestrator")
            await self.bus.emit(started_event)

            try:
                # Execute the callable (sync or async)
                if asyncio.iscoroutinefunction(callable_func):
                    result = await callable_func()
                else:
                    result = callable_func()

                # Store result as artifact
                await self.memory.put(
                    key=f"task:{step_id}",
                    data=str(result),
                    meta={"step": i, "step_id": step_id},
                    artifact_type="task_result",
                )

                # Emit task completed event
                completed_event = TaskCompletedEvent(task_id=step_id, result=result)
                await self.bus.emit(completed_event)

                results.append(result)

            except Exception:
                # For now, just re-raise - error handling in next phase
                raise

        return results
