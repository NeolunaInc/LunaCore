# LunaCore – Feuille de route des phases
> Version détaillée : [ROADMAP_FULL.txt](./ROADMAP_FULL.txt)

Statuts : ✅ Terminé · 🔄 En revue/PR · ⏳ À faire

| Phase | Titre | Statut | Livrables clés |
|-----:|-------|:------:|----------------|
| 0 | Bootstrap & Socle d’Ingénierie | ✅ | CI, pre-commit, docker-compose, make, README |
| 1 | Ingestion du Plan & Schémas | ✅ | `schemas/plan.schema.json`, validator, exemples |
| 2 | Modélisation TaskGraph & Décomposition | ✅ | `core/task_graph.py`, `agents/task_decomposer/`, schéma + tests |
| 3 | AgentRegistry v1 (Local) | 🔄 | `core/agent_types.py`, `services/agent_registry/`, 3 agents + schéma + tests |
| 4+ | Voir backlog ci-dessous | ⏳ | Execution Engine, Orchestrateur, Persistance, CLI/Visualisation, etc. |

## Backlog (extrait automatique des issues GitHub)

> Généré par `scripts/build_phase_index.py` via `gh` CLI.


### Backlog (issues ouvertes)

| # | Titre | Labels | Lien |
|---:|---|---|---|
| 42 | Phase 3: CLI & Visualisation du DAG | Statut:Backlog,type:docs,priority:P3 | https://github.com/NeolunaInc/LunaCore/issues/42 |
| 41 | Phase 3: Persistance & Reprise (state store) | type:feature,Statut:Backlog,priority:P2 | https://github.com/NeolunaInc/LunaCore/issues/41 |
| 40 | Phase 3: Orchestrateur Runtime (scheduler + workers) | type:feature,Statut:Backlog,priority:P1 | https://github.com/NeolunaInc/LunaCore/issues/40 |
| 39 | Phase 3: Execution Engine (TaskRunner + Executor) | type:feature,Statut:Backlog,priority:P1 | https://github.com/NeolunaInc/LunaCore/issues/39 |
| 27 | Phase 26: Durcissement Production & Gouvernance | phase:enterprise,priority:critical,type:feature | https://github.com/NeolunaInc/LunaCore/issues/27 |
| 26 | Phase 25: SLOs, KPIs & Costing | phase:enterprise,priority:low,type:feature | https://github.com/NeolunaInc/LunaCore/issues/26 |
| 25 | Phase 24: Observabilité Production | phase:enterprise,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/25 |
| 24 | Phase 23: CreativeEnhancementAgent | phase:enterprise,priority:low,type:feature | https://github.com/NeolunaInc/LunaCore/issues/24 |
| 23 | Phase 22: External Agent Plugin | phase:enterprise,priority:low,type:feature | https://github.com/NeolunaInc/LunaCore/issues/23 |
| 22 | Phase 21: Orchestrator v2 (Parallélisme) | phase:advanced,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/22 |
| 21 | Phase 20: Multi-tenancy Stricte & RBAC | phase:advanced,priority:critical,type:feature | https://github.com/NeolunaInc/LunaCore/issues/21 |
| 20 | Phase 19: CI/CD & Environnements | phase:advanced,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/20 |
| 19 | Phase 18: Packaging & Delivery | phase:advanced,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/19 |
| 18 | Phase 17: Solutions Concurrentes & A/B | phase:advanced,priority:low,type:feature | https://github.com/NeolunaInc/LunaCore/issues/18 |
| 17 | Phase 16: Human-in-the-Loop Console | phase:interface,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/17 |
| 16 | Phase 15: Security/Gateway (Tokenization/PII) | phase:interface,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/16 |
| 15 | Phase 14: AgentRegistry v2 (Hot-Reload, Remote) | phase:interface,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/15 |
| 14 | Phase 13: Dashboard v1 (React + WS) | phase:interface,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/14 |
| 13 | Phase 12: Audit & Mémoire d’Exécution | phase:critical-infra,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/13 |
| 12 | Phase 11: PostgreSQL (RLS + Chiffrement) | phase:critical-infra,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/12 |
| 11 | Phase 10: EventBus v2 (NATS + WAL + DLQ) | phase:critical-infra,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/11 |
| 10 | Phase 9: Logs/Metrics/Tracing v1 | phase:critical-infra,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/10 |
| 9 | Phase 8: Escalation Chain (Human/AI) | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/9 |
| 8 | Phase 7: Agents Cœur v1 | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/8 |
| 7 | Phase 6: ExecutionOrchestrator v1 | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/7 |
| 6 | Phase 5: ProjectMemoryManager v1 (Baseline) | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/6 |
| 5 | Phase 4: EventBus v1 (In-Process) | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/5 |
| 4 | Phase 3: AgentRegistry v1 (Local) | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/4 |
| 2 | Phase 1: Ingestion du Plan Détaillé & Schémas | phase:foundation,priority:high,type:feature | https://github.com/NeolunaInc/LunaCore/issues/2 |
