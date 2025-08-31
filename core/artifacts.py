import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Artifact(BaseModel):
    """Represents a stored artifact with metadata."""

    id: str = str(uuid.uuid4())
    key: str
    data: str | bytes
    meta: dict[str, Any] = {}
    tenant_id: str = "default"
    project_id: str = "default"
    artifact_type: str = "data"
    version: int = 1
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "Artifact":
        """Deserialize from JSON string."""
        return cls.model_validate_json(json_str)

    def meta_merge(self, other_meta: dict[str, Any]) -> None:
        """Merge other_meta into self.meta, with other_meta taking precedence."""
        self.meta.update(other_meta)
        self.updated_at = datetime.utcnow()
