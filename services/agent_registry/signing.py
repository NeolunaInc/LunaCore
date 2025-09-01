import hashlib
import hmac
from typing import Any


class AgentSigner:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def sign_agent(self, agent_data: dict[str, Any]) -> str:
        """
        Generate a signature for the agent data.
        """
        # Create a canonical representation
        canonical = self._canonicalize(agent_data)
        # Generate HMAC signature
        signature = hmac.new(self.secret_key, canonical.encode(), hashlib.sha256).hexdigest()
        return signature

    def verify_agent(self, agent_data: dict[str, Any], signature: str) -> bool:
        """
        Verify the signature of the agent data.
        """
        expected_signature = self.sign_agent(agent_data)
        return hmac.compare_digest(expected_signature, signature)

    def _canonicalize(self, data: dict[str, Any]) -> str:
        """
        Create a canonical string representation of the data.
        """
        # Simple canonicalization: sort keys and join
        items = []
        for key in sorted(data.keys()):
            value = data[key]
            if isinstance(value, dict):
                value = self._canonicalize(value)
            items.append(f"{key}:{value}")
        return "|".join(items)


class AgentRegistry:
    def __init__(self, signer: AgentSigner):
        self.signer = signer
        self.agents: dict[str, dict[str, Any]] = {}

    def register_agent(self, agent_id: str, agent_data: dict[str, Any]) -> None:
        """
        Register an agent with signature.
        """
        signature = self.signer.sign_agent(agent_data)
        agent_data["signature"] = signature
        self.agents[agent_id] = agent_data

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        """
        Get an agent if signature is valid.
        """
        agent_data = self.agents.get(agent_id)
        if agent_data:
            signature = agent_data.pop("signature", "")
            if self.signer.verify_agent(agent_data, signature):
                return agent_data
            else:
                raise ValueError(f"Agent {agent_id} has invalid signature")
        return None
