# ExecutionOrchestrator Service

The ExecutionOrchestrator service provides sequential execution of task plans with event-driven monitoring and artifact storage.

## Overview

ExecutionOrchestrator is the core component for running task plans in LunaCore. It executes steps sequentially, emits lifecycle events, and stores results as artifacts.

## Key Features

- **Sequential Execution**: Tasks run one after another in FIFO order
- **Event-Driven**: Real-time task lifecycle events (started/completed)
- **Artifact Storage**: Automatic persistence of task results
- **Async Support**: Handles both synchronous and asynchronous callables
- **Resource Allocation**: Pluggable allocator for callable resolution
- **Error Propagation**: Clean exception handling (ready for retry logic)

## Architecture

```
ExecutionOrchestrator
├── EventBus (InMemoryEventBus) - Event emission
├── ProjectMemory (InMemProjectMemory) - Artifact storage
└── SimpleAllocator - Callable resolution
```

## API Reference

### ExecutionOrchestrator

```python
class ExecutionOrchestrator:
    def __init__(
        self,
        bus: InMemoryEventBus,
        memory: ProjectMemory,
        allocator: SimpleAllocator
    )

    async def execute_plan(self, steps: list[dict[str, Any]]) -> list[Any]
```

#### execute_plan(steps)

Execute a sequence of steps and return their results.

**Parameters:**
- `steps`: List of step dictionaries containing:
  - `id`: Unique step identifier
  - `callable`: Function to execute (sync or async)

**Returns:**
- `list[Any]`: Results from each step in execution order

**Raises:**
- `ValueError`: If a step is missing a callable
- Any exception from step execution (for now)

## Events

The orchestrator emits events throughout task execution:

### TaskStartedEvent
```python
TaskStartedEvent(
    type="task.started",
    task_id="step_0",
    agent_id="orchestrator"
)
```

### TaskCompletedEvent
```python
TaskCompletedEvent(
    type="task.completed",
    task_id="step_0",
    result="execution_result"
)
```

## Artifacts

Task results are automatically stored as artifacts:

### Artifact Key Format
```
task:{step_id}
```

### Artifact Metadata
```python
{
    "step": 0,           # Step index in plan
    "step_id": "task1"   # Original step identifier
}
```

### Artifact Data
- Stored as string representation of the result
- `artifact_type="task_result"`

## SimpleAllocator

```python
class SimpleAllocator:
    def resolve(self, step: dict[str, Any]) -> Any
```

Resolves the callable from a step dictionary.

**Raises:**
- `ValueError`: If `callable` key is missing from step

## Usage Examples

### Basic Sequential Execution

```python
from orchestrator import ExecutionOrchestrator
from services.event_bus.bus_inmem import InMemoryEventBus
from services.memory.mem_inmem import InMemProjectMemory
from agents.resource_allocator.allocator import SimpleAllocator

# Setup components
bus = InMemoryEventBus()
memory = InMemProjectMemory()
allocator = SimpleAllocator()

orchestrator = ExecutionOrchestrator(bus, memory, allocator)

# Start event processing
await bus.start()

# Define execution plan
def process_data():
    return "processed_data"

async def fetch_remote():
    await asyncio.sleep(0.1)
    return "remote_data"

steps = [
    {"id": "process", "callable": process_data},
    {"id": "fetch", "callable": fetch_remote}
]

# Execute plan
results = await orchestrator.execute_plan(steps)
print(results)  # ["processed_data", "remote_data"]
```

### Event Monitoring

```python
# Subscribe to task events
async def event_handler(event):
    print(f"Event: {event.type} for {event.task_id}")

bus.subscribe("task.*", event_handler)

# Events will be printed:
# Event: task.started for process
# Event: task.completed for process
# Event: task.started for fetch
# Event: task.completed for fetch
```

### Artifact Retrieval

```python
# Get stored results
artifact = await memory.get("task:process")
print(artifact.data)  # "processed_data"
print(artifact.meta)  # {"step": 0, "step_id": "process"}
```

## Integration with LunaCore

### With EventBus
- Events are emitted to the shared event bus
- Other components can subscribe to `task.*` patterns
- Enables real-time monitoring and orchestration

### With ProjectMemory
- Results persist across executions
- Metadata tracks execution context
- Supports versioning for result history

### With ResourceAllocator
- Pluggable allocation strategy
- Can be extended for complex resolution logic
- Ready for dependency injection patterns

## Performance Considerations

- **Sequential**: No parallelism - suitable for dependent tasks
- **Event Overhead**: Minimal impact on execution time
- **Memory Usage**: Artifacts stored in configured memory backend
- **Async Ready**: Prepared for concurrent execution in future phases

## Error Handling

Current implementation provides basic error propagation:

```python
try:
    results = await orchestrator.execute_plan(steps)
except ValueError as e:
    print(f"Allocation error: {e}")
except Exception as e:
    print(f"Execution error: {e}")
```

Future phases will add:
- Retry logic with exponential backoff
- Timeout handling
- Partial failure recovery
- Circuit breaker patterns

## Testing

The orchestrator includes comprehensive tests:

```bash
poetry run pytest tests/test_execution_orchestrator.py -v
```

Tests cover:
- Sequential execution order
- Event emission and handling
- Artifact storage and retrieval
- Async/sync callable support
- Error conditions
