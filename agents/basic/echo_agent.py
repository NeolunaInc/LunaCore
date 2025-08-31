from __future__ import annotations
from typing import Optional, Tuple, List
from core.agent_types import AgentProtocol, AgentSpec

class EchoAgent(AgentProtocol):
    def __init__(self) -> None:
        self.spec = AgentSpec(
            agent_id="echo",
            name="EchoAgent",
            version="0.1.0",
            capabilities=["echo"],
        )

    def health(self) -> Tuple[bool, Optional[str]]:
        return True, "ok"

    # exemple d'API étendue
    def echo(self, text: str) -> str:
        return text
