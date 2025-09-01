# ProjectMemory Service

The ProjectMemory service provides versioned, persistent storage for LunaCore project artifacts with metadata management and access control.

## Overview

ProjectMemory is an abstract interface that supports multiple backend implementations:

- **InMemProjectMemory**: In-memory storage for fast, temporary data
- **FileProjectMemory**: File-based persistent storage with JSON serialization

## Key Features

- **Versioning**: Automatic version incrementing for each artifact
- **Metadata Merging**: Metadata persists and merges across versions
- **Tenant/Project Isolation**: Multi-tenant support with project-level isolation
- **ACL Stub**: Extensible access control framework
- **Async/Await**: Full asyncio support for concurrent operations
- **Thread Safety**: Lock-protected operations for concurrent access

## API Reference

### ProjectMemory Interface

```python
class ProjectMemory(ABC):
    async def put(
        self,
        key: str,
        data: str | bytes,
        meta: dict[str, Any] | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
        artifact_type: str = "data"
    ) -> Artifact

    async def get(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default"
    ) -> Artifact | None

    async def list_versions(
        self,
        key: str,
        tenant_id: str = "default",
        project_id: str = "default"
    ) -> list[int]

    async def delete(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default"
    ) -> bool
```

### Artifact Model

```python
class Artifact(BaseModel):
    id: str
    type: str
    tenant_id: str
    project_id: str
    key: str
    version: int
    created_at: datetime
    meta: dict[str, Any] = {}
    data: str | bytes
```

## Versioning

Each `put()` operation automatically increments the version number:

```python
# Version 1
await memory.put("config", "data1", meta={"env": "dev"})
# Version 2
await memory.put("config", "data2", meta={"env": "prod"})
# Version 3
await memory.put("config", "data3")

# Get latest
latest = await memory.get("config")  # version 3
# Get specific version
v1 = await memory.get("config", version=1)
```

## Metadata Merging

Metadata is merged across versions, preserving previous values:

```python
# Version 1
await memory.put("model", "weights_v1", meta={"created_by": "alice", "accuracy": 0.85})
# Version 2 (merges meta)
await memory.put("model", "weights_v2", meta={"accuracy": 0.90})
# Result: meta = {"created_by": "alice", "accuracy": 0.90}
```

## ACL Stub

The service includes an ACL framework for access control:

```python
def acl_check(tenant_id: str, project_id: str, key: str, operation: str) -> bool:
    # Stub implementation - always allow
    return True

memory = InMemProjectMemory(acl_check=my_acl_check)
```

## Examples

### In-Memory Backend

```python
from services.memory import InMemProjectMemory

# Create instance
memory = InMemProjectMemory()

# Store artifact
artifact = await memory.put(
    key="user_profile",
    data='{"name": "Alice", "role": "admin"}',
    meta={"source": "api", "version": "1.0"},
    tenant_id="acme",
    project_id="webapp"
)

# Retrieve latest
profile = await memory.get("user_profile", tenant_id="acme", project_id="webapp")
print(profile.data)  # {"name": "Alice", "role": "admin"}

# List versions
versions = await memory.list_versions("user_profile", tenant_id="acme", project_id="webapp")
print(versions)  # [1]
```

### File-Based Backend

```python
from services.memory import FileProjectMemory

# Create instance with persistent storage
memory = FileProjectMemory(root_dir="./data/memory")

# Store binary data
with open("model.pkl", "rb") as f:
    data = f.read()

await memory.put(
    key="ml_model",
    data=data,
    meta={"model_type": "classifier", "framework": "sklearn"},
    artifact_type="binary"
)

# Data persists across restarts
memory2 = FileProjectMemory(root_dir="./data/memory")
model = await memory2.get("ml_model")
```

## Performance Notes

- In-memory backend: Fast for small datasets, limited by RAM
- File-based backend: Persistent but slower due to I/O
- Use `LUNACORE_PERF` environment variable for performance monitoring
- Concurrent operations are thread-safe via asyncio.Lock

## Error Handling

```python
try:
    artifact = await memory.get("nonexistent")
    if artifact is None:
        print("Artifact not found")
except PermissionError:
    print("Access denied")
```
