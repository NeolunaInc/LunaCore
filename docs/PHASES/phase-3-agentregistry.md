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
