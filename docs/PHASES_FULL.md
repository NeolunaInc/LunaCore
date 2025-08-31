# Roadmap Phases (0 → 26)

> Statuts indicatifs : Phase 0 (socle) et Phase 1 (orchestrator minimal) : **Terminées**. Les suivantes sont **à planifier/exécuter**.

## Phase 0 — Bootstrap & Socle d'Ingénierie (TERMINÉE)
**Objectifs**: Poetry, lint/format/tests + pre-commit, docker-compose (PG/Redis/Ollama).  
**Livrables**: pyproject; Makefile; CI; docker-compose; logging JSON; tests; arbo.  
**Critères**: CI verte; docker OK; make install/test/lint OK; logs JSON; pre-commit actif.

## Phase 1 — Orchestrator minimal /healthz (TERMINÉE)
**Objectifs**: FastAPI + `/healthz`, test httpx, run-api.  
**Livrables**: endpoint, tests, doc.  
**Critères**: `pytest -q` OK; `GET /healthz` renvoie `{"status":"ok"}`.

---

## Phase 2 — Modélisation TaskGraph & Décomposition
**Objectifs**: DAG déterministe; types d’étapes `{generate_code, assemble, validate, test, package, deploy}`; hash stable.  
**Livrables**: `core/task_graph.py`; `agents/task_decomposer/`; export JSON + viz; idempotence.  
**Critères**: même plan ⇒ même hash; export sans cycles.

## Phase 3 — AgentRegistry v1 (Local)
**Objectifs**: registre mémoire; interface standard; health-check périodique.  
**Livrables**: `services/agent_registry/`; `core/agent_types.py`; 3 agents locaux (CodeGenerator, Validator, Assembly).  
**Critères**: register/unregister dyn; HC ~30s; I/O validées.

## Phase 4 — EventBus v1 (In-Process)
**Objectifs**: pub/sub typé; events `task.*`; handlers async, ordre garanti.  
**Livrables**: `services/event_bus/bus_inmem.py`; `core/events.py`; tests d’ordre.  
**Critères**: wildcards; pas de pertes.

## Phase 5 — ProjectMemoryManager v1 (Baseline)
**Objectifs**: API mémoire artifacts; stockage disque; ACL logique.  
**Livrables**: `services/memory/`; CRUD; index & métadonnées; tests intégration.  
**Critères**: persistance OK; ACL OK.

## Phase 6 — ExecutionOrchestrator v1
**Objectifs**: scheduling séquentiel; reprise sur erreur; hooks événements.  
**Livrables**: `orchestrator/executor_v1.py`; policies retry/backoff; tests intégration.  
**Critères**: exécutions reproductibles; journal d’exécution complet.

## Phase 7 — Agents Cœur v1
**Objectifs**: génération/validation/assemblage; contrats stables.  
**Livrables**: `agents/code_generator/`, `agents/validator/`, `agents/assembly/`; tests.  
**Critères**: contrats respectés; tests verts.

## Phase 8 — Escalation Chain (Human/AI)
**Objectifs**: chaîne local → OpenAI → humain; seuils/timeout.  
**Livrables**: `services/escalation/`; policies; tests E2E.  
**Critères**: déclenchement correct; traçabilité.

## Phase 9 — Logs/Metrics/Tracing v1
**Objectifs**: logs JSON; Prometheus; OpenTelemetry.  
**Livrables**: logging; `/metrics`; traces.  
**Critères**: `correlation_id`; métriques visibles.

## Phase 10 — EventBus v2 (NATS + WAL + DLQ)
**Objectifs**: fiabilité + persistence + DLQ.  
**Livrables**: `services/event_bus/nats_*`; tests de fiabilité.  
**Critères**: pas de perte; rejouable.

## Phase 11 — PostgreSQL (RLS + Chiffrement)
**Objectifs**: RLS par tenant; chiffrement at-rest.  
**Livrables**: migrations, schéma; intégrations avec memory/registry.  
**Critères**: RLS testé; intégrations OK.

## Phase 12 — Audit & Mémoire d’Exécution
**Objectifs**: journal détaillé des actions; export.  
**Livrables**: `services/audit/`; API de requête; export JSON/CSV.  
**Critères**: traçabilité complète.

## Phase 13 — Dashboard v1 (React + WebSocket)
**Objectifs**: UI runtime; updates temps réel.  
**Livrables**: `dashboard/`; vues status/runs/logs; WS.  
**Critères**: navigation fluide; tests UI de base.

## Phase 14 — AgentRegistry v2 (Hot-Reload, Remote)
**Objectifs**: découverte distante; reload sans downtime.  
**Livrables**: extensions registry; tests.  
**Critères**: reload transparent.

## Phase 15 — Security/Gateway (Tokenization/PII)
**Objectifs**: masking PII; tokenization; middlewares.  
**Livrables**: policies & middlewares; tests.  
**Critères**: aucune PII en clair.

## Phase 16 — Human-in-the-Loop Console
**Objectifs**: approbation/feedback humain.  
**Livrables**: UI HIL; journal des interventions.  
**Critères**: interventions tracées.

## Phase 17 — Solutions Concurrentes & A/B
**Objectifs**: ≥2 variantes; sélection pondérée; A/B.  
**Livrables**: `orchestrator/solution_resolver.py`; métriques qualité.  
**Critères**: sélection reproductible; coûts maîtrisés.

## Phase 18 — Packaging & Delivery
**Objectifs**: docker/zip/git; SBOM; manifests K8s/Helm.  
**Livrables**: `agents/packaging/`, `infra/helm/`; SBOM.  
**Critères**: image dispo; SBOM complet.

## Phase 19 — CI/CD & Environnements
**Objectifs**: Build→Test→Scan→Deploy; env dev/stage/prod.  
**Livrables**: workflows étendus; scripts; docs.  
**Critères**: coverage > 80%; rollback auto.

## Phase 20 — Multi-tenancy Stricte & RBAC
**Objectifs**: RBAC; isolation tenant/project; quotas.  
**Livrables**: `services/authz/rbac.py`; middlewares; policies EventBus/Memory.  
**Critères**: zéro cross-tenant; audit accès.

## Phase 21 — Orchestrator v2 (Parallélisme)
**Objectifs**: worker pool; backpressure; rate limiting.  
**Livrables**: `orchestrator/parallel_executor.py`; perf monitoring.  
**Critères**: 10× sur gros DAG; stress 100+ tâches.

## Phase 22 — External Agent Plugin
**Objectifs**: sandbox plugins externes; isolation réseau.  
**Livrables**: `services/agent_registry/plugins.py`; `services/network/policies.yaml`; onboarding.  
**Critères**: discovery OK; policies appliquées.

## Phase 23 — CreativeEnhancementAgent
**Objectifs**: amélioration créative **opt-in**, ≤3 variantes; audit trail.  
**Livrables**: `agents/creative_enhancement/`; policies.  
**Critères**: traçabilité stricte.

## Phase 24 — Observabilité Production
**Objectifs**: Prometheus/Grafana; ELK/OpenSearch; alerting.  
**Livrables**: `infra/observability/`; dashboards JSON; alert rules.  
**Critères**: SLO/SLI; alertes critiques.

## Phase 25 — SLOs, KPIs & Costing
**Objectifs**: SLO/KPI; costing; budgets + alertes.  
**Livrables**: `services/metrics/kpis.py`; `services/costing/tracker.py`; rapports.  
**Critères**: coûts tracés; budgets enforce.

## Phase 26 — Durcissement Production & Gouvernance
**Objectifs**: signature agents; backups/DR; chaos; runbooks.  
**Livrables**: `docs/governance.md`; `services/agent_registry/signing.py`; runbooks SRE; chaos tests.  
**Critères**: agents signés; RTO < 1h; game day OK.
