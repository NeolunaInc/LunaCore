import hashlib
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from services.memory.interface import ProjectMemory


@dataclass
class AgentVersion:
    """Represents a versioned agent."""

    name: str
    version: str
    code: str
    metadata: dict[str, Any]
    checksum: str
    created_at: datetime
    status: str  # 'testing', 'active', 'deprecated', 'failed'

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


@dataclass
class AgentRegistry:
    """In-memory agent registry with versioning and hot-reload."""

    agents: dict[str, list[AgentVersion]] = field(default_factory=dict)

    def _validate_version_format(self, version: str) -> bool:
        """Validate version format: vX.Y.Z"""
        pattern = r"^v\d+\.\d+\.\d+$"
        return bool(re.match(pattern, version))

    def _calculate_checksum(self, code: str) -> str:
        """Calculate SHA256 checksum of agent code."""
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def register_agent(
        self, name: str, version: str, code: str, metadata: dict[str, Any] | None = None
    ) -> AgentVersion:
        """Register a new agent version."""
        if not self._validate_version_format(version):
            raise ValueError(f"Invalid version format: {version}. Expected: vX.Y.Z")

        checksum = self._calculate_checksum(code)

        # Check if version already exists
        if name in self.agents:
            for existing_version in self.agents[name]:
                if existing_version.version == version:
                    raise ValueError(f"Version {version} already exists for agent {name}")

        agent_version = AgentVersion(
            name=name,
            version=version,
            code=code,
            metadata=metadata or {},
            checksum=checksum,
            created_at=datetime.utcnow(),
            status="testing",
        )

        if name not in self.agents:
            self.agents[name] = []

        self.agents[name].append(agent_version)

        # Sort versions by semantic version (newest first)
        self.agents[name].sort(
            key=lambda v: [int(x) for x in v.version[1:].split(".")], reverse=True
        )

        return agent_version

    def get_agent(self, name: str, version: str | None = None) -> AgentVersion | None:
        """Get agent by name and optional version."""
        if name not in self.agents:
            return None

        versions = self.agents[name]

        if version is None:
            # Return latest active version
            for v in versions:
                if v.status == "active":
                    return v
            # If no active version, return latest
            return versions[0] if versions else None

        # Find specific version
        for v in versions:
            if v.version == version:
                return v

        return None

    def update_agent_status(self, name: str, version: str, status: str) -> bool:
        """Update agent status (for hot-reload)."""
        agent = self.get_agent(name, version)
        if not agent:
            return False

        valid_statuses = ["testing", "active", "deprecated", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        agent.status = status
        return True

    def list_agents(self) -> list[dict[str, Any]]:
        """List all agents with their versions."""
        result = []
        for name, versions in self.agents.items():
            agent_info = {
                "name": name,
                "versions": [v.to_dict() for v in versions],
                "latest_version": versions[0].version if versions else None,
                "active_version": None,
            }

            # Find active version
            for v in versions:
                if v.status == "active":
                    agent_info["active_version"] = v.version
                    break

            result.append(agent_info)

        return result

    def delete_agent_version(self, name: str, version: str) -> bool:
        """Delete a specific agent version."""
        if name not in self.agents:
            return False

        original_length = len(self.agents[name])
        self.agents[name] = [v for v in self.agents[name] if v.version != version]

        return len(self.agents[name]) < original_length

    def get_agent_history(self, name: str) -> list[dict[str, Any]]:
        """Get version history for an agent."""
        if name not in self.agents:
            return []

        return [v.to_dict() for v in self.agents[name]]


class AgentRegistryAPI:
    """REST API for agent registry management."""

    def __init__(self, registry: AgentRegistry, memory: ProjectMemory):
        self.registry = registry
        self.memory = memory
        self.logger = logging.getLogger(__name__)

    async def register_agent_endpoint(
        self, name: str, version: str, code: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """REST endpoint for agent registration."""
        try:
            agent_version = self.registry.register_agent(name, version, code, metadata)

            # Store in persistent memory
            await self.memory.put(
                key=f"agent:{name}:{version}",
                data=code,
                meta={
                    "agent_name": name,
                    "version": version,
                    "checksum": agent_version.checksum,
                    "status": agent_version.status,
                },
                artifact_type="agent_code",
            )

            self.logger.info(f"Agent registered: {name} {version}")
            return {
                "success": True,
                "agent": agent_version.to_dict(),
                "message": f"Agent {name} version {version} registered successfully",
            }

        except Exception as e:
            self.logger.error(f"Failed to register agent {name} {version}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_agent_endpoint(self, name: str, version: str | None = None) -> dict[str, Any]:
        """REST endpoint for retrieving agents."""
        agent = self.registry.get_agent(name, version)

        if not agent:
            return {
                "success": False,
                "error": f'Agent {name} version {version or "latest"} not found',
            }

        return {"success": True, "agent": agent.to_dict()}

    async def update_status_endpoint(self, name: str, version: str, status: str) -> dict[str, Any]:
        """REST endpoint for updating agent status (hot-reload)."""
        try:
            success = self.registry.update_agent_status(name, version, status)

            if success:
                self.logger.info(f"Agent status updated: {name} {version} -> {status}")

                # Update in persistent memory
                await self.memory.put(
                    key=f"agent:{name}:{version}",
                    data="",  # Code already stored
                    meta={
                        "agent_name": name,
                        "version": version,
                        "status": status,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                    artifact_type="agent_status",
                )

                return {
                    "success": True,
                    "message": f"Agent {name} {version} status updated to {status}",
                }
            else:
                return {"success": False, "error": f"Agent {name} {version} not found"}

        except Exception as e:
            self.logger.error(f"Failed to update agent status {name} {version}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def list_agents_endpoint(self) -> dict[str, Any]:
        """REST endpoint for listing all agents."""
        agents = self.registry.list_agents()
        return {"success": True, "agents": agents, "count": len(agents)}

    async def delete_agent_endpoint(self, name: str, version: str) -> dict[str, Any]:
        """REST endpoint for deleting agent versions."""
        try:
            success = self.registry.delete_agent_version(name, version)

            if success:
                self.logger.info(f"Agent deleted: {name} {version}")
                return {"success": True, "message": f"Agent {name} {version} deleted successfully"}
            else:
                return {"success": False, "error": f"Agent {name} {version} not found"}

        except Exception as e:
            self.logger.error(f"Failed to delete agent {name} {version}: {str(e)}")
            return {"success": False, "error": str(e)}
