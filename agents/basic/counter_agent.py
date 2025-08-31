from __future__ import annotations

from core.agent_types import AgentProtocol, AgentSpec


class CounterAgent(AgentProtocol):
    def __init__(self) -> None:
        self.spec = AgentSpec(
            agent_id="counter",
            name="CounterAgent",
            version="0.1.0",
            capabilities=["count"],
        )

    def health(self) -> tuple[bool, str | None]:
        self._count += 1
        return True, f"count={self._count}"
