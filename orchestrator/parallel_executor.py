import asyncio
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Any


class ParallelExecutor:
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)

    async def execute_dag(
        self, tasks: list[dict[str, Any]], task_func: Callable[[dict[str, Any]], Any]
    ) -> dict[str, Any]:
        """
        Execute tasks in parallel respecting dependencies.
        tasks: list of task dicts with 'name' and 'depends_on' keys.
        task_func: async function to execute a task.
        """
        # Build graph
        indegree: dict[str, int] = {task["name"]: len(task.get("depends_on", [])) for task in tasks}
        adj_list: dict[str, list[str]] = defaultdict(list)
        for task in tasks:
            for dep in task.get("depends_on", []):
                adj_list[dep].append(task["name"])

        # Queue for tasks with no dependencies
        queue = deque([name for name, deg in indegree.items() if deg == 0])
        results: dict[str, Any] = {}
        running: set[str] = set()

        async def execute_task(task_name: str):
            async with self.semaphore:
                task_data = next(t for t in tasks if t["name"] == task_name)
                result = await task_func(task_data)
                results[task_name] = result
                # Update dependents
                for dependent in adj_list[task_name]:
                    indegree[dependent] -= 1
                    if indegree[dependent] == 0 and dependent not in running:
                        running.add(dependent)
                        asyncio.create_task(execute_task(dependent))
                running.discard(task_name)

        # Start initial tasks
        initial_tasks = []
        for task_name in queue:
            running.add(task_name)
            initial_tasks.append(execute_task(task_name))

        await asyncio.gather(*initial_tasks)

        # Wait for all to complete
        while running:
            await asyncio.sleep(0.01)

        return results
