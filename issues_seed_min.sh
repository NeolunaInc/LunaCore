#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-NeoLunaInc/LunaCore}"
PROJECT_KEY="${2:-}"   # peut être un titre ("LunaCore Development Tracker") ou un numéro (6)

# Résout le numéro du project depuis un titre si besoin
project_num() {
  local key="$1"
  if [[ -z "$key" ]]; then echo ""; return; fi
  if [[ "$key" =~ ^[0-9]+$ ]]; then echo "$key"; return; fi
  local owner="${REPO%/*}"
  gh project list --owner "$owner" --format json \
    --jq ".[] | select(.title==\"$key\") | .number" | head -n1
}

MS1="MVP Fonctionnel (Phases 0-8)"; MS2="Production Ready (Phases 9-12)"
MS3="Interface Complète (Phases 13-16)"; MS4="Optimisations (Phases 17-21)"
MS5="Enterprise (Phases 22-26)"

phase_label(){ n=$1; if ((n<=8)); then echo phase:foundation; elif ((n<=12)); then echo phase:critical-infra; elif ((n<=16)); then echo phase:interface; elif ((n<=21)); then echo phase:advanced; else echo phase:enterprise; fi; }
phase_milestone(){ n=$1; if ((n<=8)); then echo "$MS1"; elif ((n<=12)); then echo "$MS2"; elif ((n<=16)); then echo "$MS3"; elif ((n<=21)); then echo "$MS4"; else echo "$MS5"; fi; }
phase_priority(){ n=$1; case "$n" in 0|20|26) echo priority:critical;; 17|22|23|25) echo priority:low;;  *) echo priority:high;; esac; }

mk(){ local num="$1"; shift; local title="$1"; shift
  local labels="$(phase_label "$num"),$(phase_priority "$num"),type:feature"
  local ms="$(phase_milestone "$num")"
  local tmp; tmp="$(mktemp)"; cat >"$tmp"
  gh issue create --repo "$REPO" --title "Phase ${num}: ${title}" \
    --label "$labels" --milestone "$ms" --body-file "$tmp" >/dev/null
  local id; id="$(gh issue list --repo "$REPO" --search "Phase ${num}: ${title}" \
    --json number --jq '.[0].number' 2>/dev/null || true)"
  if [[ -n "$id" && -n "$PROJECT_KEY" ]]; then
    local pnum; pnum="$(project_num "$PROJECT_KEY")"; [[ -z "$pnum" ]] && pnum="$PROJECT_KEY"
    gh issue edit "$id" --repo "$REPO" --add-project "$pnum" >/dev/null 2>&1 || true
  fi
  rm -f "$tmp"; echo "✓ Phase $num: $title"
}

# ---- 26 issues (corps condensés, stables) ----
mk 0  "Bootstrap & Socle d'Ingénierie" <<'EOF'
Objectifs: Poetry mono-repo; lint/format/tests + pre-commit; docker-compose (PostgreSQL/Redis/Ollama)
Livrables: pyproject; Makefile; CI; docker-compose; arbo; logging JSON; tests hello
Critères: CI verte; docker OK; make install/test/lint OK; logs JSON; pre-commit actif
EOF
mk 1  "Ingestion du Plan Détaillé & Schémas" <<'EOF'
Objectifs: format YAML/JSON; JSON Schema strict; PlanValidatorAgent
Livrables: schema; exemples valides/invalides; types; agent; doc
Critères: détecte incomplets; messages clairs; tests; <100ms
EOF
mk 2  "Modélisation TaskGraph & Décomposition" <<'EOF'
Objectifs: DAG déterministe; étapes {generate_code,assemble,validate,test,package,deploy}; hash stable
Livrables: core/task_graph; agent; export JSON+viz; idempotence
Critères: même plan=>même hash; export sans cycles
EOF
mk 3  "AgentRegistry v1 (Local)" <<'EOF'
Objectifs: registre mémoire; interface standard; health-check périodique
Livrables: service; types; 3 agents; HC
Critères: register/unregister dyn; HC ~30s; I/O validés
EOF
mk 4  "EventBus v1 (In-Process)" <<'EOF'
Objectifs: pub/sub typé; events task.*; handlers async, ordre garanti
Livrables: bus_inmem; events; pattern-matching; tests
Critères: wildcards; pas de pertes
EOF
mk 5  "ProjectMemoryManager v1 (Baseline)" <<'EOF'
Objectifs: API mémoire artifacts; stockage disque; ACL logique
Livrables: service; CRUD; index; tests
Critères: persistance OK; ACL OK
EOF
mk 6  "ExecutionOrchestrator v1" <<'EOF'
Objectifs: scheduling séquentiel; reprise erreur; hooks events
Livrables: executor_v1; retry/backoff; tests intégration
Critères: exécutions reproductibles; journal complet
EOF
mk 7  "Agents Cœur v1" <<'EOF'
Objectifs: génération/validation/assemblage; contrats stables
Livrables: 3 agents + tests
Critères: contrats respectés; tests verts
EOF
mk 8  "Escalation Chain (Human/AI)" <<'EOF'
Objectifs: chaîne local→OpenAI→humain; seuils/timeout
Livrables: service; policies; tests E2E
Critères: déclenchement correct; traçabilité
EOF
mk 9  "Logs/Metrics/Tracing v1" <<'EOF'
Objectifs: logs JSON; Prometheus; OpenTelemetry
Livrables: logging; /metrics; traces
Critères: correlation_id; métriques visibles
EOF
mk 10 "EventBus v2 (NATS + WAL + DLQ)" <<'EOF'
Objectifs: NATS + WAL + DLQ
Livrables: nats_*; persistence; DLQ; tests fiabilité
Critères: pas de pertes; rejouable
EOF
mk 11 "PostgreSQL (RLS + Chiffrement)" <<'EOF'
Objectifs: RLS par tenant; chiffrement at-rest
Livrables: migrations; schéma; intégrations
Critères: RLS testé; intégration OK
EOF
mk 12 "Audit & Mémoire d’Exécution" <<'EOF'
Objectifs: audit détaillé des exécutions
Livrables: service audit; journal; export
Critères: traçabilité complète
EOF
mk 13 "Dashboard v1 (React + WS)" <<'EOF'
Objectifs: React+Vite; WebSocket live
Livrables: dashboard; vues; WS updates
Critères: UI fluide; tests de base
EOF
mk 14 "AgentRegistry v2 (Hot-Reload, Remote)" <<'EOF'
Objectifs: hot-reload; remote discovery
Livrables: impl + tests
Critères: reload sans downtime
EOF
mk 15 "Security/Gateway (Tokenization/PII)" <<'EOF'
Objectifs: tokenization; PII masking
Livrables: middlewares; policies; tests
Critères: aucune PII en clair
EOF
mk 16 "Human-in-the-Loop Console" <<'EOF'
Objectifs: UI approbation/feedback
Livrables: UI; journal interventions
Critères: interventions tracées
EOF
mk 17 "Solutions Concurrentes & A/B" <<'EOF'
Objectifs: variantes multiples; sélection pondérée; A/B
Livrables: resolver; métriques qualité; sandbox
Critères: ≥2 variantes; coûts maîtrisés
EOF
mk 18 "Packaging & Delivery" <<'EOF'
Objectifs: docker/zip/git; SBOM; K8s
Livrables: packaging; helm; SBOM
Critères: image dispo; SBOM complet
EOF
mk 19 "CI/CD & Environnements" <<'EOF'
Objectifs: Build→Test→Scan→Deploy; env dev/stage/prod
Livrables: workflows; scripts; docs
Critères: coverage >80%; rollback auto
EOF
mk 20 "Multi-tenancy Stricte & RBAC" <<'EOF'
Objectifs: RBAC; isolation tenant/project; quotas
Livrables: authz/rbac; middlewares; policies
Critères: zéro cross-tenant; audit accès
EOF
mk 21 "Orchestrator v2 (Parallélisme)" <<'EOF'
Objectifs: worker pool; backpressure; rate limit
Livrables: parallel_executor; policies; perf
Critères: 10x gros DAG; stress 100+
EOF
mk 22 "External Agent Plugin" <<'EOF'
Objectifs: plugins externes; sandbox; iso réseau
Livrables: plugins.py; policies.yaml; onboarding
Critères: discovery OK; policies appliquées
EOF
mk 23 "CreativeEnhancementAgent" <<'EOF'
Objectifs: amélioration créative opt-in
Livrables: agent; policies; traçabilité
Critères: ≤3 variantes; audit trail
EOF
mk 24 "Observabilité Production" <<'EOF'
Objectifs: Prometheus/Grafana; ELK/OpenSearch; alerting
Livrables: observability/; dashboards; alert rules
Critères: SLO/SLI; alertes critiques
EOF
mk 25 "SLOs, KPIs & Costing" <<'EOF'
Objectifs: SLO/KPI; costing; budgets+alertes
Livrables: kpis.py; costing/tracker.py; rapports
Critères: coûts tracés; budgets enforce
EOF
mk 26 "Durcissement Production & Gouvernance" <<'EOF'
Objectifs: signature agents; backups/DR; chaos; runbooks
Livrables: governance.md; signing.py; runbooks; chaos tests
Critères: agents signés; RTO<1h; game day OK
EOF
