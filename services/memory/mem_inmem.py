import asyncio
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from core.artifacts import Artifact
from services.memory.interface import ProjectMemory


class InMemProjectMemory(ProjectMemory):
    """In-memory implementation of ProjectMemory with versioning."""

    def __init__(self, acl_check: Callable[[str, str, str, str], bool] | None = None):
        super().__init__(acl_check)
        self._store: dict[tuple[str, str, str], dict[int, Artifact]] = {}
        self._versions: dict[tuple[str, str, str], int] = {}
        self._lock = asyncio.Lock()

    async def put(
        self,
        key: str,
        data: str | bytes,
        meta: dict[str, Any] | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
        artifact_type: str = "data",
    ) -> Artifact:
        """Store an artifact in memory."""
        if not self.acl_check(tenant_id, project_id, key, "write"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        async with self._lock:
            store_key = (tenant_id, project_id, key)
            if store_key not in self._versions:
                self._versions[store_key] = 0
                self._store[store_key] = {}

            version = self._versions[store_key] + 1
            self._versions[store_key] = version

            # Merge meta from previous version
            new_meta = {}
            if self._store[store_key]:
                latest_version = max(self._store[store_key].keys())
                prev_art = self._store[store_key][latest_version]
                new_meta.update(prev_art.meta)
            if meta:
                new_meta.update(meta)

            artifact = Artifact(
                id=str(uuid.uuid4()),
                type=artifact_type,
                tenant_id=tenant_id,
                project_id=project_id,
                key=key,
                version=version,
                created_at=datetime.utcnow(),
                meta=new_meta,
                data=data,
            )

            self._store[store_key][version] = artifact
            return artifact

    async def get(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> Artifact | None:
        """Retrieve an artifact from memory."""
        if not self.acl_check(tenant_id, project_id, key, "read"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        store_key = (tenant_id, project_id, key)
        if store_key not in self._store:
            return None

        if version is None:
            # Get latest version
            version = max(self._store[store_key].keys())

        return self._store[store_key].get(version)

    async def list_versions(
        self, key: str, tenant_id: str = "default", project_id: str = "default"
    ) -> list[int]:
        """List all versions for a key."""
        if not self.acl_check(tenant_id, project_id, key, "list"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        store_key = (tenant_id, project_id, key)
        if store_key not in self._store:
            return []
        return sorted(self._store[store_key].keys())

    async def delete(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> bool:
        """Delete an artifact or all versions."""
        if not self.acl_check(tenant_id, project_id, key, "delete"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        async with self._lock:
            store_key = (tenant_id, project_id, key)
            if store_key not in self._store:
                return False

            if version is None:
                # Delete all versions
                del self._store[store_key]
                del self._versions[store_key]
                return True
            else:
                # Delete specific version
                if version in self._store[store_key]:
                    del self._store[store_key][version]
                    # If no versions left, clean up
                    if not self._store[store_key]:
                        del self._store[store_key]
                        del self._versions[store_key]
                    return True
                return False
