# MASTER PLAN — Phases 2 → 26

> Roadmap index: [PHASES/INDEX.md](./INDEX.md) | Full roadmap: [PHASES/ROADMAP_FULL.txt](./ROADMAP_FULL.txt)
> Phase 3 delivered via PR #44. Tag v0.3.0 if not done.

---

## Phase 2 — TaskGraph & Décomposition (HAUTE)
- Objectifs
  - Générer un DAG **déterministe** pour un plan d’entrée (YAML/JSON)
  - Types : `generate_code`, `assemble`, `validate`, `test`, `package`, `deploy`
  - **Hash stable** (idempotence) + export JSON + (pré-viz)
- Portée incluse
  - `core/task_graph.py` (Pydantic: `Task`, `Edge`, `Artifact`, `TaskGraph`)
  - `agents/task_decomposer/` (algorithme déterministe)
- Livrables
  - Module + tests complets
  - Exemples `examples/plans/` valides/invalides
- Contrats / I/O
  - Entrée : `PlanSpec` (versionné) ; Sortie : `TaskGraph` (versionné)
- Tests
  - Même entrée ⇒ **même hash**
  - Détection cycles / tâches orphelines / validations strictes
- Observabilité
  - Métriques : nb de nœuds/edges, temps de décomposition, taux d’erreur
- Sécurité
  - Validation stricte des schémas
- Risques & mitigations
  - Ambiguïtés de specs → JSON Schema + examples
- Critères d’acceptation
  - 100% cas déterministes, export JSON, 0 cycle
- Estimation
  - 4 jours

## Phase 3 — AgentRegistry v1 (Local) (HAUTE)
- Objectifs : registre mémoire, interface standardisée, health-check périodique (~30s)
- Livrables : `services/agent_registry/`, `core/agent_types.py`, 3 agents démo
- Contrats : register/unregister + introspection capabilités
- Tests : unitaires + intégration
- Observabilité : métriques HC (succès, latence)
- Sécurité : pas de réseau externe
- Critères : register/unregister dynamiques + HC OK

## Phase 4 — EventBus v1 (In-process) (HAUTE)
- Pub/Sub typé, events `task.started/completed/failed`, wildcard `task.*`, ordre garanti
- Livrables : `services/event_bus/bus_inmem.py`, `core/events.py`

## Phase 5 — ProjectMemoryManager v1 (HAUTE)
- Stockage disque local (baseline), CRUD artifacts, index & métadonnées

## Phase 6 — ExecutionOrchestrator v1 (HAUTE)
- Scheduling séquentiel, reprise sur erreur, retry/backoff, hooks events

## Phase 7 — Agents Cœur v1 (HAUTE)
- CodeGenerator/Validator/Assembly, contrats I/O stables

## Phase 8 — Escalation Chain (Human/AI) (HAUTE)
- Chaîne escalade local → OpenAI → humain, seuils/timeout

## Phase 9 — Logs/Metrics/Tracing v1 (HAUTE)
- Logs JSON (déjà), /metrics Prometheus, traces OTel, correlation_id

## Phase 10 — EventBus v2 (NATS + WAL + DLQ) (HAUTE)
- NATS, persistence WAL, DLQ, rejouabilité

## Phase 11 — PostgreSQL (RLS + chiffrement) (HAUTE)
- Migrations, schéma, RLS par tenant, chiffrement at-rest

## Phase 12 — Audit & Mémoire d’Exécution (HAUTE)
- Journal détaillé, export JSON/CSV

## Phase 13 — Dashboard v1 (React + WS) (HAUTE)
- Vite, WS live, vues status/runs/logs

## Phase 14 — AgentRegistry v2 (Hot-Reload/Remote) (HAUTE)
- Découverte distante, reload sans downtime

## Phase 15 — Security/Gateway (Tokenization/PII) (HAUTE)
- Middlewares sécurité, PII masking, politiques

## Phase 16 — Human-in-the-Loop console (HAUTE)
- UI approbation/feedback + journal interventions

## Phase 17 — Solutions concurrentes & A/B (MOYENNE)
- ≥2 variantes + résolution pondérée, métriques qualité

## Phase 18 — Packaging & Delivery (HAUTE)
- Docker/zip/git, SBOM, manifests K8s/Helm

## Phase 19 — CI/CD & Environnements (HAUTE)
- Build→Test→Scan→Deploy, coverage>80%, rollback auto

## Phase 20 — Multi-tenant strict & RBAC (CRITIQUE)
- RBAC admin/operator/viewer, quotas, isolation

## Phase 21 — Orchestrator v2 (Parallélisme) (HAUTE)
- Worker pool, backpressure, rate limit, perf 10x DAG

## Phase 22 — External Agent Plugin (BASSE)
- Plugins externes, sandbox, iso réseau

## Phase 23 — CreativeEnhancementAgent (BASSE)
- Opt-in, ≤3 variantes, audit trail

## Phase 24 — Observabilité Production (HAUTE)
- Prometheus/Grafana, ELK/OpenSearch, alerting

## Phase 25 — SLOs, KPIs & Costing (BASSE)
- Coûts/SLI/SLO, budgets+alertes

## Phase 26 — Durcissement & Gouvernance (CRITIQUE)
- Signature agents, backup/DR (RTO<1h), chaos, runbooks SRE
