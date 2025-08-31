# Phase 2 — TaskGraph & Décomposeur

## 1) Modèles (Pydantic)
```python
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Optional

TaskType = Literal["generate_code","assemble","validate","test","package","deploy"]

class Artifact(BaseModel):
    id: str
    kind: str
    uri: Optional[str] = None
    meta: Dict[str, str] = {}

class Task(BaseModel):
    id: str
    type: TaskType
    inputs: List[str] = []      # artifact ids
    outputs: List[str] = []     # artifact ids
    params: Dict[str, str] = {}
    depends_on: List[str] = []  # task ids

class Edge(BaseModel):
    src: str   # task id
    dst: str   # task id
    reason: Literal["data","order"]="data"

class TaskGraph(BaseModel):
    version: str = "1.0"
    tasks: List[Task]
    edges: List[Edge]
    hash: Optional[str] = None

2) Détermination du hash (idempotence)

Normalisation : tri lexicographique par task.id, puis sérialisation JSON sans espaces, clés triées.

Représentation : {"version":..,"tasks":[..],"edges":[..]} sans hash.

Hash : SHA256 de la représentation → TaskGraph.hash

Invariants : même entrée ⇒ même hash.

3) Règles de validité

Aucun cycle (Kahn/topo). Échec : ValidationError("cycle").

Toutes les références depends_on, inputs/outputs doivent exister.

id uniques (tasks & artifacts).

Taille max (défaut) : 1k tasks (configurable).

4) Exemples JSON
{
  "version":"1.0",
  "tasks":[
    {"id":"t1","type":"generate_code","inputs":[],"outputs":["a1"],"params":{},"depends_on":[]},
    {"id":"t2","type":"validate","inputs":["a1"],"outputs":["a2"],"params":{},"depends_on":["t1"]}
  ],
  "edges":[
    {"src":"t1","dst":"t2","reason":"data"}
  ]
}

5) Plan de tests (pytest)

test_same_input_same_hash() : deux plans identiques ⇒ hash identique.

test_cycle_detected() : graphe cyclique ⇒ exception.

test_missing_artifact_ref() : référence inconnue ⇒ exception.

test_export_json_roundtrip() : export/import préserve l’égalité structurelle.

Bench léger : <100 ms sur 100 tâches (local).

6) Observabilité

Compteurs : taskgraph.tasks.count, taskgraph.edges.count

Timers : taskgraph.decomposition.ms

Erreurs : taskgraph.validation.error_total

7) Livraison

PR 1 : core/task_graph.py + tests

PR 2 : agents/task_decomposer/ + tests

Feature flag : TASKGRAPH_V1=true
