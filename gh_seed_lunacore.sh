#!/usr/bin/env bash
# gh_seed_lunacore.sh — Seed labels, milestones, and 26 issues for LunaCore
# Usage: ./gh_seed_lunacore.sh [owner/repo] ["LunaCore Development Tracker"]
# Requires: GitHub CLI (gh) authenticated with repo scope.
set -euo pipefail

REPO="${1:-NeoLunaInc/LunaCore}"
PROJECT_NAME="${2:-LunaCore Development Tracker}"

echo "🔐 Checking GitHub CLI auth..."
gh auth status >/dev/null

echo "📦 Target repo: $REPO"
echo "🗂  Target project: $PROJECT_NAME (optional link step)"

# ---------- Labels ----------
echo "🏷️  Creating/refreshing labels..."
# phase labels
gh label create "phase:foundation"      --repo "$REPO" --color "0969da" --description "Phases 0-8: Core du système" || gh label edit "phase:foundation" --repo "$REPO" --color "0969da" --description "Phases 0-8: Core du système"
gh label create "phase:critical-infra"  --repo "$REPO" --color "d73a49" --description "Phases 9-12: Infrastructure critique" || gh label edit "phase:critical-infra" --repo "$REPO" --color "d73a49" --description "Phases 9-12: Infrastructure critique"
gh label create "phase:interface"       --repo "$REPO" --color "0e8a16" --description "Phases 13-16: Interfaces utilisateur" || gh label edit "phase:interface" --repo "$REPO" --color "0e8a16" --description "Phases 13-16: Interfaces utilisateur"
gh label create "phase:advanced"        --repo "$REPO" --color "fbca04" --description "Phases 17-21: Avancées & perfs" || gh label edit "phase:advanced" --repo "$REPO" --color "fbca04" --description "Phases 17-21: Avancées & perfs"
gh label create "phase:enterprise"      --repo "$REPO" --color "a371f7" --description "Phases 22-26: Enterprise & polish" || gh label edit "phase:enterprise" --repo "$REPO" --color "a371f7" --description "Phases 22-26: Enterprise & polish"
# priority labels
gh label create "priority:critical"     --repo "$REPO" --color "b60205" --description "Bloquant - À faire immédiatement" || gh label edit "priority:critical" --repo "$REPO" --color "b60205" --description "Bloquant - À faire immédiatement"
gh label create "priority:high"         --repo "$REPO" --color "ff9800" --description "Important - Sprint en cours" || gh label edit "priority:high" --repo "$REPO" --color "ff9800" --description "Important - Sprint en cours"
gh label create "priority:medium"       --repo "$REPO" --color "fbca04" --description "Moyen - À planifier" || gh label edit "priority:medium" --repo "$REPO" --color "fbca04" --description "Moyen - À planifier"
gh label create "priority:low"          --repo "$REPO" --color "d4c5f9" --description "Faible - Backlog" || gh label edit "priority:low" --repo "$REPO" --color "d4c5f9" --description "Faible - Backlog"
# type labels
gh label create "type:feature"          --repo "$REPO" --color "a2eeef" --description "Nouvelle fonctionnalité" || gh label edit "type:feature" --repo "$REPO" --color "a2eeef" --description "Nouvelle fonctionnalité"
gh label create "type:bug"              --repo "$REPO" --color "d73a4a" --description "Bug à corriger" || gh label edit "type:bug" --repo "$REPO" --color "d73a4a" --description "Bug à corriger"
gh label create "type:documentation"    --repo "$REPO" --color "0075ca" --description "Docs & guides" || gh label edit "type:documentation" --repo "$REPO" --color "0075ca" --description "Docs & guides"
gh label create "type:test"             --repo "$REPO" --color "c5def5" --description "Tests & QA" || gh label edit "type:test" --repo "$REPO" --color "c5def5" --description "Tests & QA"

# ---------- Milestones ----------
echo "🎯 Creating/refreshing milestones..."
ms1="MVP Fonctionnel (Phases 0-8)"
ms2="Production Ready (Phases 9-12)"
ms3="Interface Complète (Phases 13-16)"
ms4="Optimisations (Phases 17-21)"
ms5="Enterprise (Phases 22-26)"

for ms in "$ms1" "$ms2" "$ms3" "$ms4" "$ms5"; do
  if gh api -H "Accept: application/vnd.github+json" "/repos/${REPO}/milestones?state=all" | jq -e ".[] | select(.title==\"${ms}\")" >/dev/null 2>&1; then
    echo "Milestone '${ms}' already exists."
  else
    gh milestone create --repo "$REPO" --title "${ms}" --description "${ms}"
  fi
done

# Helper: map phase -> milestone & labels
phase_label() {
  local n=$1
  if   (( n <= 8 ));  then echo "phase:foundation"
  elif (( n <= 12 )); then echo "phase:critical-infra"
  elif (( n <= 16 )); then echo "phase:interface"
  elif (( n <= 21 )); then echo "phase:advanced"
  else                    echo "phase:enterprise"
  fi
}
phase_milestone() {
  local n=$1
  if   (( n <= 8 ));  then echo "$ms1"
  elif (( n <= 12 )); then echo "$ms2"
  elif (( n <= 16 )); then echo "$ms3"
  elif (( n <= 21 )); then echo "$ms4"
  else                    echo "$ms5"
  fi
}
phase_priority() {
  local n=$1
  case "$n" in
    0) echo "priority:critical" ;;
    1|2|3|4|5|6|7) echo "priority:high" ;;
    8) echo "priority:high" ;;
    9|10|11|12) echo "priority:high" ;;
    13|14|15|16) echo "priority:high" ;;
    17) echo "priority:medium" ;;
    18|19|21|24) echo "priority:high" ;;
    20|26) echo "priority:critical" ;;
    22|23|25) echo "priority:low" ;;
    *) echo "priority:medium" ;;
  esac
}

# ---------- Issues ----------
echo "📝 Creating 26 issues..."

issue() {
  local num="$1"
  local title="$2"
  local body="$3"
  local labels
  labels="$(phase_label "$num"),$(phase_priority "$num"),type:feature"
  local milestone
  milestone="$(phase_milestone "$num")"

  echo "… Issue Phase $num: $title"
  gh issue create --repo "$REPO" \
    --title "Phase ${num}: ${title}" \
    --body "$body" \
    --label "$labels" \
    --milestone "$milestone" >/dev/null

  # Optional: add to repository project (uncomment if using Projects v2 under the same owner)
  # last_issue=$(gh issue list --repo "$REPO" --search "Phase ${num}: ${title}" --limit 1 --json number --jq '.[0].number')
  # gh issue edit "$last_issue" --repo "$REPO" --add-project "$PROJECT_NAME"
}

# Bodies
b0=$'# Durée: 2-3 jours
# Priorité: CRITIQUE

## Objectifs
- Mono-repo Python (Poetry)
- Outillage qualité (lint/format/tests, pre-commit)
- Docker-compose (PostgreSQL, Redis, Ollama)

## Livrables
- [ ] pyproject.toml (dépendances core)
- [ ] Makefile (install/test/lint/docker-up/down)
- [ ] .github/workflows/ci.yml
- [ ] docker-compose.yml (PostgreSQL, Redis, Ollama)
- [ ] Structure: core/, orchestrator/, agents/, services/
- [ ] Logging JSON structuré
- [ ] Tests \"hello world\"

## Critères d\'acceptation
- [ ] Pipeline CI/CD vert sur GitHub Actions
- [ ] Docker-compose démarre sans erreur
- [ ] make install/test/lint fonctionnent
- [ ] Logs au format JSON
- [ ] pre-commit hooks actifs'acceptation
- [ ] Pipeline GitHub Actions vert
- [ ] docker-compose up OK
- [ ] make install/test/lint OK
- [ ] Logs JSON visibles
- [ ] pre-commit hooks actifs'acceptation\n- [ ] CI/CD vert sur GitHub Actions\n- [ ] docker-compose up démarre sans erreur\n- [ ] make install/test/lint fonctionnent\n- [ ] Logs en JSON\n- [ ] Pre-commit hooks actifs'
b1=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 0\n\n## Objectifs\n- Format d’entrée des plans (YAML/JSON)\n- JSON Schema strict\n- PlanValidatorAgent\n\n## Livrables\n- [ ] schemas/plan.schema.json\n- [ ] examples/plans/ (≥10 – valides & invalides)\n- [ ] core/plan_types.py\n- [ ] agents/plan_validator/\n- [ ] Documentation format de plan\n\n## Critères d\'acceptation\n- [ ] Détecte 100% des plans incomplets\n- [ ] Messages d’erreur clairs\n- [ ] Tests cas limites\n- [ ] Validation < 100ms'
b2=$'# Durée: 4 jours
# Priorité: HAUTE
# Prérequis: Phase 1

## Objectifs
- TaskDecomposerAgent → DAG déterministe
- Types: generate_code, assemble, validate, test, package, deploy
- Dépendances et hash stable

## Livrables
- [ ] core/task_graph.py (Task/Edge/Artifacts)
- [ ] agents/task_decomposer/
- [ ] Export JSON + visualisation DAG
- [ ] Hash stable pour idempotence

## Critères d\'acceptation
- [ ] Même plan → même DAG (hash identique)
- [ ] DAG pour CRUD REST ≈ 30–50 tâches
- [ ] Export JSON du graphe
- [ ] Pas de cycles dans le graphe'acceptation
- [ ] Même plan → même DAG (hash identique)
- [ ] CRUD REST ≈ 30–50 tâches
- [ ] Export JSON du graphe
- [ ] Aucun cycle'acceptation\n- [ ] Même plan → même DAG (hash identique)\n- [ ] CRUD REST ≈ 30–50 tâches\n- [ ] Export JSON du graphe\n- [ ] Aucun cycle'
b3=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 2\n\n## Objectifs\n- Registre d’agents en mémoire\n- Interface standardisée + métadonnées\n- Health-check périodique\n\n## Livrables\n- [ ] services/agent_registry/\n- [ ] core/agent_types.py\n- [ ] 3 agents locaux (CodeGenerator, Validator, Assembly)\n- [ ] Health-check par agent\n\n## Critères d\'acceptation\n- [ ] Register/unregister dynamiques\n- [ ] Health-check ~30s\n- [ ] Schemas I/O validés'
b4=$'# Durée: 2 jours\n# Priorité: HAUTE\n# Prérequis: Phase 3\n\n## Objectifs\n- Pub/Sub in-process typé\n- Événements: task.started/completed/failed, escalation.needed\n- Handlers asynchrones, ordre garanti\n\n## Livrables\n- [ ] services/event_bus/bus_inmem.py\n- [ ] core/events.py\n- [ ] Pattern-matching\n- [ ] Tests de livraison ordonnée\n\n## Critères d\'acceptation\n- [ ] Subscribe wildcards (task.*)\n- [ ] Émission async\n- [ ] Pas de perte d’événements'
b5=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 4\n\n## Objectifs\n- API mémoire projet (artifacts)\n- Stockage local/disk (baseline)\n- ACL logique (prépare multi-tenant)\n\n## Livrables\n- [ ] services/memory/\n- [ ] APIs CRUD artifacts\n- [ ] Index & métadonnées\n- [ ] Tests intégration\n\n## Critères d\'acceptation\n- [ ] Artifacts persistés & listables\n- [ ] ACLs respectées'
b6=$'# Durée: 5 jours\n# Priorité: HAUTE\n# Prérequis: Phase 5\n\n## Objectifs\n- Orchestrateur d’exécution v1\n- Scheduling séquentiel, reprise sur erreur\n- Hooks événements\n\n## Livrables\n- [ ] orchestrator/executor_v1.py\n- [ ] Policies retry/backoff\n- [ ] Tests d’intégration\n\n## Critères d\'acceptation\n- [ ] Exécutions reproductibles\n- [ ] Journal d’exécution complet'
b7=$'# Durée: 5 jours\n# Priorité: HAUTE\n# Prérequis: Phase 6\n\n## Objectifs\n- Agents cœur v1 (génération, validation, assemblage)\n- Contrats d’interface stables\n\n## Livrables\n- [ ] agents/code_generator/\n- [ ] agents/validator/\n- [ ] agents/assembly/\n- [ ] Tests unitaires\n\n## Critères d\'acceptation\n- [ ] Contrats respectés\n- [ ] Tests verts'
b8=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 7\n\n## Objectifs\n- Chaîne d’escalade (local → OpenAI → human)\n- Politique de seuils/timeout\n\n## Livrables\n- [ ] services/escalation/\n- [ ] Config chain & policies\n- [ ] Tests E2E happy path / fallback\n\n## Critères d\'acceptation\n- [ ] Escalade déclenchée selon règles\n- [ ] Traçabilité complète'
b9=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 8\n\n## Objectifs\n- Logs JSON, métriques Prometheus, traces OpenTelemetry\n\n## Livrables\n- [ ] Logging JSON structuré\n- [ ] /metrics exposé\n- [ ] Traces de bout-en-bout\n\n## Critères d\'acceptation\n- [ ] Corrélation (correlation_id)\n- [ ] Métriques visibles'
b10=$'# Durée: 4 jours\n# Priorité: HAUTE\n# Prérequis: Phase 9\n\n## Objectifs\n- EventBus v2 (NATS + WAL + DLQ)\n\n## Livrables\n- [ ] services/event_bus/nats_*\n- [ ] Persistence + DLQ\n- [ ] Tests de fiabilité\n\n## Critères d\'acceptation\n- [ ] Pas de perte d’événements\n- [ ] Rejouabilité'
b11=$'# Durée: 4 jours\n# Priorité: HAUTE\n# Prérequis: Phase 10\n\n## Objectifs\n- PostgreSQL (RLS + chiffrement)\n\n## Livrables\n- [ ] migrations & schéma\n- [ ] RLS par tenant\n- [ ] Chiffrement au repos\n\n## Critères d\'acceptation\n- [ ] RLS vérifié par tests\n- [ ] Intégration memory/registry'
b12=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 11\n\n## Objectifs\n- Audit & mémoire d’exécution\n\n## Livrables\n- [ ] services/audit/\n- [ ] Journal détaillé des actions\n- [ ] Requête et export audit\n\n## Critères d\'acceptation\n- [ ] Traçabilité complète\n- [ ] Export JSON/CSV'
b13=$'# Durée: 5 jours\n# Priorité: HAUTE\n# Prérequis: Phase 12\n\n## Objectifs\n- Dashboard React + Vite + WebSocket\n\n## Livrables\n- [ ] dashboard/\n- [ ] Views: status, runs, logs\n- [ ] WS live updates\n\n## Critères d\'acceptation\n- [ ] Navigation fluide\n- [ ] Tests UI de base'
b14=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 13\n\n## Objectifs\n- AgentRegistry v2 (hot-reload, remote)\n\n## Livrables\n- [ ] Hot-reload / remote discovery\n- [ ] Tests\n\n## Critères d\'acceptation\n- [ ] Reload sans downtime'
b15=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 14\n\n## Objectifs\n- Sécurité/Gateway: tokenization, PII masking\n\n## Livrables\n- [ ] Middlewares sécurité\n- [ ] Policies de tokenization\n- [ ] Tests\n\n## Critères d\'acceptation\n- [ ] Aucune PII en clair'
b16=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 15\n\n## Objectifs\n- Human-in-the-Loop console\n\n## Livrables\n- [ ] UI approbation/feedback\n- [ ] Journal des interventions\n\n## Critères d\'acceptation\n- [ ] Interventions tracées'
b17=$'# Durée: 4 jours\n# Priorité: MOYENNE\n# Prérequis: Phase 16\n\n## Objectifs\n- Générer 2-3 variantes + résolution pondérée\n- A/B testing avec métriques\n\n## Livrables\n- [ ] orchestrator/solution_resolver.py\n- [ ] Métriques de qualité\n- [ ] Sandbox de comparaison\n\n## Critères d\'acceptation\n- [ ] ≥2 variantes\n- [ ] Sélection reproductible\n- [ ] Coûts maîtrisés'
b18=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 17\n\n## Objectifs\n- Packaging (docker/zip/git) + SBOM + manifests K8s\n\n## Livrables\n- [ ] agents/packaging/\n- [ ] infra/helm/\n- [ ] SBOM generation\n\n## Critères d\'acceptation\n- [ ] Image docker construite\n- [ ] SBOM complet\n- [ ] Artifacts téléchargeables'
b19=$'# Durée: 3 jours\n# Priorité: HAUTE\n# Prérequis: Phase 18\n\n## Objectifs\n- CI/CD complet + environnements dev/staging/prod\n\n## Livrables\n- [ ] .github/workflows/ étendus\n- [ ] scripts/ci/\n- [ ] docs/ci.md\n\n## Critères d\'acceptation\n- [ ] Build→Test→Scan→Deploy\n- [ ] Coverage > 80%\n- [ ] Rollback auto'
b20=$'# Durée: 4 jours\n# Priorité: CRITIQUE\n# Prérequis: Phase 19\n\n## Objectifs\n- RBAC (admin/operator/viewer)\n- Isolation tenant/project\n- Quotas & limites\n\n## Livrables\n- [ ] services/authz/rbac.py\n- [ ] Middlewares globaux\n- [ ] Policies EventBus/Memory\n- [ ] Tests d’étanchéité\n\n## Critères d\'acceptation\n- [ ] Zéro cross-tenant access\n- [ ] Quotas enforced\n- [ ] Audit des accès'
b21=$'# Durée: 5 jours\n# Priorité: HAUTE\n# Prérequis: Phase 20\n\n## Objectifs\n- Exécution parallèle par batch\n- Worker pool + backpressure + rate limiting\n\n## Livrables\n- [ ] orchestrator/parallel_executor.py\n- [ ] Worker pool mgmt\n- [ ] Resource allocation policies\n- [ ] Perf monitoring\n\n## Critères d\'acceptation\n- [ ] 10x sur gros DAG\n- [ ] Pas de starvation\n- [ ] Tests stress 100+ tâches'
b22=$'# Durée: 3 jours\n# Priorité: BASSE\n# Prérequis: Phase 21\n\n## Objectifs\n- Plugins agents externes (discovery, sandbox, isolation réseau)\n\n## Livrables\n- [ ] services/agent_registry/plugins.py\n- [ ] services/network/policies.yaml\n- [ ] Onboarding workflow\n\n## Critères d\'acceptation\n- [ ] Discovery endpoint\n- [ ] Network policies appliquées'
b23=$'# Durée: 2 jours\n# Priorité: BASSE\n# Prérequis: Phase 22\n\n## Objectifs\n- CreativeEnhancementAgent (opt-in, jamais remplacer specs)\n\n## Livrables\n- [ ] agents/creative_enhancement/\n- [ ] Policies opt-in + traçabilité\n\n## Critères d\'acceptation\n- [ ] ≤3 variantes\n- [ ] Audit trail'
b24=$'# Durée: 4 jours\n# Priorité: HAUTE\n# Prérequis: Phase 23\n\n## Objectifs\n- Observabilité prod (Prometheus, Grafana, ELK/OpenSearch, alerting)\n\n## Livrables\n- [ ] infra/observability/\n- [ ] Dashboards JSON\n- [ ] Alert rules\n- [ ] docs/observability.md\n\n## Critères d\'acceptation\n- [ ] Métriques exposées\n- [ ] Dashboards SLO/SLI\n- [ ] Alertes critiques'
b25=$'# Durée: 3 jours\n# Priorité: BASSE\n# Prérequis: Phase 24\n\n## Objectifs\n- SLOs/KPIs & costing (budget caps + alertes)\n\n## Livrables\n- [ ] services/metrics/kpis.py\n- [ ] services/costing/tracker.py\n- [ ] Rapports périodiques\n\n## Critères d\'acceptation\n- [ ] Coût par appel tracé\n- [ ] Budget enforced\n- [ ] Rapports CSV/JSON\n- [ ] Alertes dépassement'
b26=$'# Durée: 5 jours\n# Priorité: CRITIQUE\n# Prérequis: Phase 25\n\n## Objectifs\n- Durcissement production & gouvernance (signature agents, backups, DR, chaos)\n\n## Livrables\n- [ ] docs/governance.md\n- [ ] services/agent_registry/signing.py\n- [ ] Runbooks SRE\n- [ ] Chaos tests\n\n## Critères d\'acceptation\n- [ ] Agents signés obligatoires\n- [ ] Backup+restore testés (RTO < 1h)\n- [ ] Game day réussi'

# Create issues
issue 0  "Bootstrap & Socle d'Ingénierie"          "$b0"
issue 1  "Ingestion du Plan Détaillé & Schémas"    "$b1"
issue 2  "Modélisation TaskGraph & Décomposition"  "$b2"
issue 3  "AgentRegistry v1 (Local)"                "$b3"
issue 4  "EventBus v1 (In-Process)"                "$b4"
issue 5  "ProjectMemoryManager v1 (Baseline)"      "$b5"
issue 6  "ExecutionOrchestrator v1"                "$b6"
issue 7  "Agents Cœur v1"                          "$b7"
issue 8  "Escalation Chain (Human/AI)"             "$b8"
issue 9  "Logs/Metrics/Tracing v1"                 "$b9"
issue 10 "EventBus v2 (NATS + WAL + DLQ)"          "$b10"
issue 11 "PostgreSQL (RLS + Chiffrement)"          "$b11"
issue 12 "Audit & Mémoire d’Exécution"             "$b12"
issue 13 "Dashboard v1 (React + WS)"               "$b13"
issue 14 "AgentRegistry v2 (Hot-Reload, Remote)"   "$b14"
issue 15 "Security/Gateway (Tokenization/PII)"     "$b15"
issue 16 "Human-in-the-Loop Console"               "$b16"
issue 17 "Solutions Concurrentes & A/B"            "$b17"
issue 18 "Packaging & Delivery"                    "$b18"
issue 19 "CI/CD & Environnements"                  "$b19"
issue 20 "Multi-tenancy Stricte & RBAC"            "$b20"
issue 21 "Orchestrator v2 (Parallélisme)"          "$b21"
issue 22 "External Agent Plugin"                   "$b22"
issue 23 "CreativeEnhancementAgent"                "$b23"
issue 24 "Observabilité Production"                "$b24"
issue 25 "SLOs, KPIs & Costing"                    "$b25"
issue 26 "Durcissement Production & Gouvernance"   "$b26"

echo "✅ Done. Issues, labels, and milestones created for $REPO."
