from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from core.artifacts import Artifact


class ProjectMemory(ABC):
    """Abstract base class for project memory management."""

    def __init__(self, acl_check: Callable[[str, str, str, str], bool] | None = None):
        """Initialize with optional ACL check function.

        Args:
            acl_check: Function(tenant_id, project_id, key, operation) -> bool
                      Defaults to lambda: True
        """
        self.acl_check = acl_check or (lambda *args: True)

    @abstractmethod
    async def put(
        self,
        key: str,
        data: str | bytes,
        meta: dict[str, Any] | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
        artifact_type: str = "data",
    ) -> Artifact:
        """Store an artifact and return it with generated metadata."""

    @abstractmethod
    async def get(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> Artifact | None:
        """Retrieve an artifact by key and optional version."""

    @abstractmethod
    async def list_versions(
        self,
        key: str,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> list[int]:
        """List all versions for a given key."""

    @abstractmethod
    async def delete(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> bool:
        """Delete an artifact or all versions of a key."""
