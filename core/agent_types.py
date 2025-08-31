from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Literal, Optional, Protocol, Tuple
from pydantic import AnyUrl, BaseModel, ConfigDict, Field

class AgentSpec(BaseModel):
    """Spécification d'un agent IA local."""
    model_config = ConfigDict(extra="forbid")
    agent_id: str = Field(..., pattern=r"^[A-Za-z0-9._-]{3,64}$")
    name: str
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$")
    capabilities: List[str] = Field(default_factory=list)
    endpoint: Optional[AnyUrl] = None  # optionnel (local/no-http)

class AgentStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    healthy: Literal["healthy", "unhealthy", "unknown"] = "unknown"
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[str] = None

class AgentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    spec: AgentSpec
    status: AgentStatus = Field(default_factory=AgentStatus)

class AgentProtocol(Protocol):
    """Interface minimale d'un agent."""
    spec: AgentSpec
    def health(self) -> Tuple[bool, Optional[str]]:
        ...
