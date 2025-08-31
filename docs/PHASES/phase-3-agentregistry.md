# Phase 3 — AgentRegistry v1 (Local)

## Objectifs
- Registre d'agents en mémoire (register/unregister/list/get)
- Interface standard (Protocol) et modèles (Pydantic v2)
- Health-check périodique (30s configurable) + `tick()` pour tests
- Schémas JSON exportés (AgentSpec/Status/Record)
- 3 agents de base (echo, ping, counter)
- Tests d’intégration (pytest)

## Livrables
- `services/agent_registry/` (registry + health monitor)
- `core/agent_types.py` (specs + protocol)
- `agents/basic/` (3 agents)
- `schemas/agent_registry.schema.json`
- `tests/test_agent_registry.py`, `tests/test_agent_schema.py`

## Critères d’acceptation
- [x] Register/unregister dynamique
- [x] Health-check périodique (30s par défaut) & `tick()` manuel
- [x] Schémas Pydantic JSON générés et versionnés
- [x] Tests d’intégration verts (CI)

### Vérification rapide (local)

```bash
python scripts/gen_agent_schema.py
pytest -q tests/test_agent_registry.py tests/test_agent_schema.py
```

scripts/gen_agent_schema.py écrit schemas/agent_registry.schema.json.

Les tests couvrent registre/health et la stabilité du schéma.

### Notes de release (préparation v0.3.0)

Nouveau : AgentRegistry v1 (registre en mémoire), HealthMonitor (tick + thread), 3 agents (echo/ping/counter)

Schemas : schemas/agent_registry.schema.json généré depuis Pydantic

Tests : intégration (registre/health/schéma)

CI : lint + tests, Phase 2 + 3
