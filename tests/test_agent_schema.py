from __future__ import annotations

import json
import pathlib

import pytest
from pydantic import ValidationError

from core.agent_types import AgentSpec


def test_agent_spec_validation_and_schema():
    with pytest.raises(ValidationError):
        AgentSpec(agent_id="??", name="x", version="0.1.0")

    schema = json.loads(
        pathlib.Path("schemas/agent_registry.schema.json").read_text(encoding="utf-8")
    )
    assert "AgentSpec" in schema and "AgentRecord" in schema
    assert "properties" in schema["AgentSpec"]
