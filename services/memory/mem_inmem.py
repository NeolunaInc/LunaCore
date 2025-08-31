from collections.abc import Callable
from typing import Any

from core.artifacts import Artifact
from services.memory.interface import ProjectMemory


class InMemProjectMemory(ProjectMemory):
    """In-memory implementation of ProjectMemory with versioning."""

    def __init__(self, acl_check: Callable[[str, str, str, str], bool] | None = None):
        super().__init__(acl_check)
        self._storage: dict[str, list[Artifact]] = {}

    async def put(
        self,
        key: str,
        data: str | bytes,
        meta: dict[str, Any] | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
        artifact_type: str = "data",
    ) -> Artifact:
        """Store an artifact with versioning."""
        if key not in self._storage:
            self._storage[key] = []

        versions = self._storage[key]
        new_version = len(versions) + 1

        artifact = Artifact(
            key=key,
            data=data,
            meta=meta or {},
            tenant_id=tenant_id,
            project_id=project_id,
            artifact_type=artifact_type,
            version=new_version,
        )

        versions.append(artifact)
        return artifact

    async def get(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> Artifact | None:
        """Retrieve an artifact by key and version."""
        if key not in self._storage:
            return None

        versions = self._storage[key]
        if not versions:
            return None

        if version is None:
            return versions[-1]  # Latest version

        if 1 <= version <= len(versions):
            return versions[version - 1]

        return None

    async def list_versions(
        self,
        key: str,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> list[int]:
        """List all versions for a key."""
        if key not in self._storage:
            return []

        return list(range(1, len(self._storage[key]) + 1))
