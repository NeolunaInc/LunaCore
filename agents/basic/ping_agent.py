from __future__ import annotations

from core.agent_types import AgentProtocol, AgentSpec


class PingAgent(AgentProtocol):
    def __init__(self) -> None:
        self.spec = AgentSpec(
            agent_id="ping",
            name="PingAgent",
            version="0.1.0",
            capabilities=["ping"],
        )

    def health(self) -> tuple[bool, str | None]:
        return True, "pong"
