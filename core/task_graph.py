from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

TaskType = Literal["generate_code", "assemble", "validate", "test", "package", "deploy", "custom"]


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class Artifact(BaseModel):
    name: str
    kind: Literal["input", "output"] = "output"
    uri: str | None = None
    media_type: str | None = None


class Task(BaseModel):
    name: str
    type: TaskType = "custom"
    params: dict[str, Any] = Field(default_factory=dict)
    inputs: list[Artifact] = Field(default_factory=list)
    outputs: list[Artifact] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    id: str | None = None

    @field_validator("depends_on")
    @classmethod
    def unique_depends(cls, v: list[str]) -> list[str]:
        seen = set()
        out: list[str] = []
        for x in v:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out

    def compute_id(self, namespace: str) -> str:
        if self.id:
            return self.id
        core = {
            "name": self.name,
            "type": self.type,
            "params": self.params,
            "inputs": [a.model_dump() for a in self.inputs],
            "outputs": [a.model_dump() for a in self.outputs],
            "depends_on": sorted(self.depends_on),
        }
        payload = _canonical({"ns": namespace, "task": core})
        return _sha256_hex(payload)[:16]

    def canonical(self, namespace: str) -> dict[str, Any]:
        tid = self.compute_id(namespace)
        return {
            "id": tid,
            "name": self.name,
            "type": self.type,
            "params": self.params,
            "inputs": [a.model_dump() for a in self.inputs],
            "outputs": [a.model_dump() for a in self.outputs],
            "depends_on": sorted(self.depends_on),
        }


class TaskGraph(BaseModel):
    plan_id: str
    tasks: list[Task] = Field(default_factory=list)

    def validate_acyclic(self) -> None:
        ns = self.plan_id
        indeg = defaultdict(int)
        adj = defaultdict(list)
        ids: list[str] = []
        for t in self.tasks:
            tid = t.id or t.compute_id(ns)
            ids.append(tid)
        for t in self.tasks:
            tid = t.id or t.compute_id(ns)
            for dep in t.depends_on:
                indeg[tid] += 1
                adj[dep].append(tid)
        q = deque([tid for tid in ids if indeg[tid] == 0])
        visited = 0
        while q:
            u = q.popleft()
            visited += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if visited != len(ids):
            raise ValueError("TaskGraph has at least one cycle")

    def topological_order(self) -> list[str]:
        ns = self.plan_id
        indeg = defaultdict(int)
        adj = defaultdict(list)
        ids: list[str] = []
        for t in self.tasks:
            tid = t.id or t.compute_id(ns)
            ids.append(tid)
        for t in self.tasks:
            tid = t.id or t.compute_id(ns)
            for dep in t.depends_on:
                indeg[tid] += 1
                adj[dep].append(tid)
        q = deque(sorted([tid for tid in ids if indeg[tid] == 0]))
        order: list[str] = []
        while q:
            u = q.popleft()
            order.append(u)
            for v in sorted(adj[u]):
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(order) != len(ids):
            raise ValueError("TaskGraph has at least one cycle")
        return order

    def stable_hash(self) -> str:
        ns = self.plan_id
        canonical_tasks = [t.canonical(ns) for t in self.tasks]
        canonical_tasks.sort(key=lambda x: (x["id"], x["name"]))
        payload = _canonical({"plan_id": ns, "tasks": canonical_tasks})
        return _sha256_hex(payload)

    def to_json(self) -> str:
        ns = self.plan_id
        data = {"plan_id": self.plan_id, "tasks": [t.canonical(ns) for t in self.tasks]}
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)

    def to_mermaid(self) -> str:
        ns = self.plan_id
        lines = ["graph TD"]
        for t in self.tasks:
            tid = t.id or t.compute_id(ns)
            safe = t.name.replace("[", "(").replace("]", ")")
            lines.append(f"  {tid}[{safe}]")
        for t in self.tasks:
            tid = t.id or t.compute_id(ns)
            for dep in t.depends_on:
                lines.append(f"  {dep} --> {tid}")
        return "\n".join(lines)
