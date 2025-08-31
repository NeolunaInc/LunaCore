from __future__ import annotations

from core.agent_types import AgentProtocol, AgentSpec


class EchoAgent(AgentProtocol):
    def __init__(self) -> None:
        self.spec = AgentSpec(
            agent_id="echo",
            name="EchoAgent",
            version="0.1.0",
            capabilities=["echo"],
        )

    def health(self) -> tuple[bool, str | None]:
        return True, "ok"

    # exemple d'API étendue
    def echo(self, text: str) -> str:
        return text
