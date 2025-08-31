import asyncio
import json
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from core.artifacts import Artifact
from services.memory.interface import ProjectMemory


class FileProjectMemory(ProjectMemory):
    """File-based implementation of ProjectMemory with persistence."""

    def __init__(
        self,
        root_dir: str | Path = ".lunacore/memory",
        acl_check: Callable[[str, str, str, str], bool] | None = None,
    ):
        super().__init__(acl_check)
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._index: dict[tuple[str, str, str], dict[int, Path]] = {}
        self._load_index()

    def _load_index(self):
        """Load the index of all stored artifacts."""
        self._index = {}
        for tenant_dir in self.root_dir.iterdir():
            if not tenant_dir.is_dir():
                continue
            tenant_id = tenant_dir.name
            for project_dir in tenant_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                project_id = project_dir.name
                for key_dir in project_dir.iterdir():
                    if not key_dir.is_dir():
                        continue
                    key = key_dir.name
                    store_key = (tenant_id, project_id, key)
                    self._index[store_key] = {}
                    for version_file in key_dir.glob("*.json"):
                        try:
                            version = int(version_file.stem)
                            self._index[store_key][version] = version_file
                        except ValueError:
                            continue

    def _get_artifact_path(self, tenant_id: str, project_id: str, key: str, version: int) -> Path:
        """Get the file path for an artifact."""
        return self.root_dir / tenant_id / project_id / key / f"{version}.json"

    async def put(
        self,
        key: str,
        data: str | bytes,
        meta: dict[str, Any] | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
        artifact_type: str = "data",
    ) -> Artifact:
        """Store an artifact to file."""
        if not self.acl_check(tenant_id, project_id, key, "write"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        async with self._lock:
            store_key = (tenant_id, project_id, key)
            if store_key not in self._index:
                self._index[store_key] = {}

            # Get next version
            existing_versions = list(self._index[store_key].keys())
            version = max(existing_versions) + 1 if existing_versions else 1

            # Merge meta from previous version
            new_meta = {}
            if existing_versions:
                latest_version = max(existing_versions)
                latest_path = self._index[store_key][latest_version]
                with open(latest_path, encoding="utf-8") as f:
                    prev_data = json.load(f)
                prev_meta = prev_data.get("meta", {})
                new_meta.update(prev_meta)
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

            # Save to file
            artifact_path = self._get_artifact_path(tenant_id, project_id, key, version)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)

            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(artifact.to_json(), f, indent=2, ensure_ascii=False)

            # Update index
            self._index[store_key][version] = artifact_path
            return artifact

    async def get(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> Artifact | None:
        """Retrieve an artifact from file."""
        if not self.acl_check(tenant_id, project_id, key, "read"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        store_key = (tenant_id, project_id, key)
        if store_key not in self._index:
            return None

        if version is None:
            # Get latest version
            version = max(self._index[store_key].keys())

        artifact_path = self._index[store_key].get(version)
        if not artifact_path or not artifact_path.exists():
            return None

        with open(artifact_path, encoding="utf-8") as f:
            data = json.load(f)

        return Artifact.from_json(data)

    async def list_versions(
        self, key: str, tenant_id: str = "default", project_id: str = "default"
    ) -> list[int]:
        """List all versions for a key."""
        if not self.acl_check(tenant_id, project_id, key, "list"):
            raise PermissionError(f"Access denied for {tenant_id}/{project_id}/{key}")

        store_key = (tenant_id, project_id, key)
        if store_key not in self._index:
            return []
        return sorted(self._index[store_key].keys())

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
            if store_key not in self._index:
                return False

            if version is None:
                # Delete all versions
                for artifact_path in self._index[store_key].values():
                    if artifact_path.exists():
                        artifact_path.unlink()
                    # Remove empty directories
                    for parent in artifact_path.parents:
                        if parent != self.root_dir and not list(parent.iterdir()):
                            parent.rmdir()
                del self._index[store_key]
                return True
            else:
                # Delete specific version
                artifact_path = self._index[store_key].get(version)
                if artifact_path and artifact_path.exists():
                    artifact_path.unlink()
                    del self._index[store_key][version]
                    # Clean up empty directories
                    for parent in artifact_path.parents:
                        if parent != self.root_dir and not list(parent.iterdir()):
                            parent.rmdir()
                    return True
                return False
