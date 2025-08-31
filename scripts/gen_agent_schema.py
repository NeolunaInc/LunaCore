from __future__ import annotations
import json, pathlib
from core.agent_types import AgentSpec, AgentStatus, AgentRecord

def main() -> None:
    out = {
        "AgentSpec": AgentSpec.model_json_schema(),
        "AgentStatus": AgentStatus.model_json_schema(),
        "AgentRecord": AgentRecord.model_json_schema(),
    }
    p = pathlib.Path("schemas/agent_registry.schema.json")
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {p}")

if __name__ == "__main__":
    main()
