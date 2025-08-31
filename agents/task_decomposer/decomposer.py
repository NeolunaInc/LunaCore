from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from core.task_graph import Artifact, Task, TaskGraph, _canonical, _sha256_hex

STAGE_ORDER = ["generate_code", "assemble", "validate", "test", "package", "deploy"]


class TaskDecomposerAgent(BaseModel):
    """Deterministic plan → DAG transformation."""

    plan_namespace: str | None = None

    def decompose(self, plan: Any) -> TaskGraph:
        data = self._load_plan(plan)
        plan_id = self.plan_namespace or self._compute_plan_id(data)

        if isinstance(data, dict) and "tasks" in data:
            tasks = self._from_explicit_tasks(data["tasks"])
            g = TaskGraph(plan_id=plan_id, tasks=tasks)
            g.validate_acyclic()
            return g

        components = self._extract_components(data)
        tasks = self._synthesize_tasks(plan_id, components, data)
        g = TaskGraph(plan_id=plan_id, tasks=tasks)
        g.validate_acyclic()
        return g

    # ---------- internals ----------
    def _load_plan(self, plan: Any) -> dict[str, Any]:
        if isinstance(plan, dict):
            return plan
        if isinstance(plan, str):
            p = Path(plan)
            text = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else plan
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return yaml.safe_load(text)
        raise TypeError("Unsupported plan input type")

    def _compute_plan_id(self, data: dict[str, Any]) -> str:
        if isinstance(data, dict):
            for key in ("id", "uuid", "plan_id"):
                if key in data and isinstance(data[key], str) and data[key]:
                    return data[key]
        return _sha256_hex(_canonical(data))[:16]

    def _from_explicit_tasks(self, task_list: list[dict[str, Any]]) -> list[Task]:
        out: list[Task] = []
        for t in task_list:
            out.append(
                Task(
                    id=t.get("id"),
                    name=t.get("name", "task"),
                    type=t.get("type", "custom"),
                    params=t.get("params", {}),
                    inputs=[Artifact(**a) for a in t.get("inputs", [])],
                    outputs=[Artifact(**a) for a in t.get("outputs", [])],
                    depends_on=list(t.get("depends_on", [])),
                )
            )
        out.sort(key=lambda x: (x.id or "", x.name))
        return out

    def _extract_components(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        keys = ("components", "modules", "services", "packages")
        comp = None
        for k in keys:
            if k in data:
                comp = data[k]
                break
        items: list[dict[str, Any]] = []
        if comp is None:
            items = [{"name": data.get("name", "root"), "config": data}]
        elif isinstance(comp, dict):
            for name in sorted(comp.keys()):
                cfg = comp[name]
                items.append({"name": str(name), "config": cfg})
        elif isinstance(comp, list):
            for c in comp:
                if isinstance(c, dict):
                    nm = str(c.get("name") or c.get("id") or c.get("module") or "component")
                    cfg = c.get("config", c)
                    items.append({"name": nm, "config": cfg})
        else:
            items = [{"name": "root", "config": {"raw": comp}}]
        items.sort(key=lambda x: x["name"])
        return items

    def _synthesize_tasks(
        self, plan_id: str, components: list[dict[str, Any]], data: dict[str, Any]
    ) -> list[Task]:
        tasks: list[Task] = []
        stage_flags = {k: True for k in STAGE_ORDER}
        if isinstance(data.get("stages"), dict):
            for k, v in data["stages"].items():
                if k in stage_flags:
                    stage_flags[k] = bool(v)

        for comp in components:
            cname = comp["name"]
            prev_id: str | None = None
            for st in STAGE_ORDER:
                if not stage_flags.get(st, True):
                    continue
                t = Task(
                    name=f"{cname}:{st}",
                    type=st,  # type: ignore
                    params={"component": cname, "stage": st},
                    inputs=[],
                    outputs=[],
                    depends_on=[] if prev_id is None else [prev_id],
                )
                tid = t.compute_id(namespace=plan_id)
                t.id = tid
                tasks.append(t)
                prev_id = tid

        order = data.get("component_order")
        if isinstance(order, list):
            name2first = {}
            name2last = {}
            for cname in [c["name"] for c in components]:
                comp_tasks = [t for t in tasks if t.params.get("component") == cname]
                comp_tasks.sort(key=lambda t: t.name)
                if comp_tasks:
                    name2first[cname] = comp_tasks[0].id
                    name2last[cname] = comp_tasks[-1].id
            for i in range(len(order) - 1):
                a, b = str(order[i]), str(order[i + 1])
                if a in name2last and b in name2first:
                    for t in tasks:
                        if t.id == name2first[b] and name2last[a] not in t.depends_on:
                            t.depends_on.append(name2last[a])

        tasks.sort(key=lambda t: t.id or t.name)
        return tasks
