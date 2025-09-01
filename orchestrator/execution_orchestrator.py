import asyncio
from typing import Any

from agents.resource_allocator.allocator import SimpleAllocator
from core.events import EscalationNeededEvent, TaskCompletedEvent, TaskFailedEvent, TaskStartedEvent
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
        results: list[Any] = []

        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i}")
            callable_func = self.allocator.resolve(step)

            options = step.get("options", {})
            retries = options.get("retries", 0)
            timeout = options.get("timeout", None)
            retry_backoff = options.get("retry_backoff", "fixed")  # 'fixed' | 'exponential'
            backoff_base = options.get("backoff_base", 0.05)
            escalate_on_failure = options.get("escalate_on_failure", False)

            result = None
            success = False

            for attempt in range(retries + 1):
                # Emit task started event for each attempt
                started_event = TaskStartedEvent(task_id=step_id, agent_id="orchestrator")
                await self.bus.emit(started_event)

                try:
                    # Execute the callable with timeout if specified
                    is_async = asyncio.iscoroutinefunction(callable_func) or (
                        callable(callable_func)
                        and asyncio.iscoroutinefunction(getattr(callable_func, "__call__", None))
                    )
                    if timeout is not None:
                        if is_async:
                            result = await asyncio.wait_for(callable_func(), timeout)
                        else:
                            result = await asyncio.wait_for(asyncio.to_thread(callable_func), timeout)
                    else:
                        if is_async:
                            result = await callable_func()
                        else:
                            result = await asyncio.to_thread(callable_func)

                    # Success: store artifact and emit completed
                    await self.memory.put(
                        key=f"task:{step_id}",
                        data=str(result),
                        meta={"step": i, "step_id": step_id, "attempt": attempt},
                        artifact_type="task_result",
                    )
                    completed_event = TaskCompletedEvent(task_id=step_id, result=result)
                    await self.bus.emit(completed_event)
                    success = True
                    break  # Exit retry loop on success

                except Exception as e:
                    error_str = str(e)
                    failed_event = TaskFailedEvent(task_id=step_id, error=error_str)
                    await self.bus.emit(failed_event)

                    if attempt < retries:
                        # Calculate backoff
                        if retry_backoff == "exponential":
                            backoff = backoff_base * (2**attempt)
                        else:
                            backoff = backoff_base
                        await asyncio.sleep(backoff)
                    else:
                        if escalate_on_failure:
                            escalation_event = EscalationNeededEvent(task_id=step_id, reason=error_str)
                            await self.bus.emit(escalation_event)
                        raise  # Stop the plan on final failure

            if success:
                results.append(result)

        return results
