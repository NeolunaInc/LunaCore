import base64
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ArtifactId(BaseModel):
    """Unique identifier for an artifact."""
    tenant_id: str
    project_id: str
    key: str
    version: int


class Artifact(BaseModel):
    """Represents a stored artifact with metadata."""
    id: str  # Unique artifact ID
    type: str  # Artifact type (e.g., "document", "model", "config")
    tenant_id: str
    project_id: str
    key: str  # User-defined key
    version: int
    created_at: datetime
    meta: dict[str, Any] = {}  # Additional metadata
    data: str | bytes  # The actual data

    def to_json(self) -> dict:
        """Convert to JSON-serializable dict with base64 encoding for bytes."""
        data = self.data
        if isinstance(data, bytes):
            data = base64.b64encode(data).decode("utf-8")
            data_type = "bytes"
        else:
            data_type = "str"

        return {
            "id": self.id,
            "type": self.type,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "key": self.key,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "meta": self.meta,
            "data": data,
            "data_type": data_type,
        }

    @classmethod
    def from_json(cls, data: dict) -> "Artifact":
        """Create Artifact from JSON dict with base64 decoding."""
        artifact_data = data["data"]
        if data.get("data_type") == "bytes":
            artifact_data = base64.b64decode(artifact_data)

        return cls(
            id=data["id"],
            type=data["type"],
            tenant_id=data["tenant_id"],
            project_id=data["project_id"],
            key=data["key"],
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            meta=data.get("meta", {}),
            data=artifact_data,
        )
