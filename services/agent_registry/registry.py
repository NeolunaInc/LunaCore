from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from core.agent_types import AgentProtocol, AgentRecord, AgentSpec, AgentStatus


class AgentRegistry:
    """Registre en mémoire d'agents IA."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentProtocol] = {}
        self._records: dict[str, AgentRecord] = {}

    # CRUD
    def register(self, agent: AgentProtocol) -> AgentRecord:
        spec: AgentSpec = agent.spec
        rec = AgentRecord(spec=spec, status=AgentStatus())
        self._agents[spec.agent_id] = agent
        self._records[spec.agent_id] = rec
        return rec

    def unregister(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)
        self._records.pop(agent_id, None)

    def get(self, agent_id: str) -> AgentRecord | None:
        return self._records.get(agent_id)

    def list(self) -> Iterable[AgentRecord]:
        return list(self._records.values())

    # Health
    def health_tick(self) -> None:
        """Exécute un cycle de health check synchrone sur tous les agents."""
        now = datetime.now(UTC)
        for agent_id, agent in list(self._agents.items()):
            try:
                ok, details = agent.health()
            except Exception as exc:  # pragma: no cover
                ok, details = False, f"exception: {exc!r}"

            status = self._records[agent_id].status
            status.healthy = "healthy" if ok else "unhealthy"
            status.details = details
            status.last_seen = now
