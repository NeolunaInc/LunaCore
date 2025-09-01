import asyncio
import time

import pytest

from orchestrator.parallel_executor import ParallelExecutor


async def mock_task(task_data: dict) -> str:
    """Mock task that sleeps for the duration specified in task_data."""
    duration = task_data.get("duration", 0.1)
    await asyncio.sleep(duration)
    return f"Completed {task_data['name']}"


@pytest.mark.asyncio
class TestParallelism:
    async def test_parallel_faster_than_sequential(self):
        executor = ParallelExecutor(max_workers=10)

        # Define a simple DAG: A -> B, A -> C, B -> D, C -> D
        tasks = [
            {"name": "A", "depends_on": [], "duration": 0.1},
            {"name": "B", "depends_on": ["A"], "duration": 0.1},
            {"name": "C", "depends_on": ["A"], "duration": 0.1},
            {"name": "D", "depends_on": ["B", "C"], "duration": 0.1},
        ]

        # Measure parallel execution time
        start = time.time()
        results = await executor.execute_dag(tasks, mock_task)
        parallel_time = time.time() - start

        # Sequential execution for comparison
        start = time.time()
        for task in tasks:
            await mock_task(task)
        sequential_time = time.time() - start

        # Assert parallel is faster
        assert parallel_time < sequential_time
        assert len(results) == 4
        assert "Completed A" in results["A"]

    async def test_no_dependencies(self):
        executor = ParallelExecutor()

        tasks = [
            {"name": "task1", "depends_on": [], "duration": 0.05},
            {"name": "task2", "depends_on": [], "duration": 0.05},
        ]

        results = await executor.execute_dag(tasks, mock_task)
        assert len(results) == 2
        assert "Completed task1" in results["task1"]
        assert "Completed task2" in results["task2"]
