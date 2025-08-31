# LunaCore

Socle d’orchestration d’agents (**Runtime unique : Python 3.12** / FastAPI) avec outillage dev (Poetry, pre-commit, black/ruff, pytest).

## Installation rapide
Voir [docs/SETUP.md](docs/SETUP.md) pour le guide complet d'installation.

Voir [docs/OPS.md](docs/OPS.md) pour les opérations courantes.

Voir [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md) pour les dépendances détaillées.

## Démarrage rapide

```bash
# Dépendances Python
poetry install
poetry run pre-commit install

# Qualité & tests
make fmt && make lint && make test

# Services de base
docker compose up -d db redis

# API (dev)
make run-api   # puis GET http://localhost:8000/healthz
```

## Variables d’environnement
- `OLLAMA_BASE_URL` : par défaut http://localhost:11434 (Ollama installé sur l’hôte).
- Pour vérifier : `curl -s http://localhost:11434/api/tags`.

## Structure (extrait)
- `orchestrator/app.py` : FastAPI + /healthz
- `core/logging.py` : config logs JSON à l’import
- `tests/test_healthz.py` : test d’intégration httpx
- `Makefile` : run-api, fmt, lint, test

## Board & workflows (résumé)
Statuts : Backlog, Sprint actuel, En développement, Review/Test, Terminé.

- Item added to project (Issues) → Status=Backlog.
- Item reopened → Status=Backlog.
- Item closed → Status=Terminé.
- Pull request merged → Status=Terminé.
- Auto-add to project : filtre Repo=NeoLunaInc/LunaCore, is:issue (pas PR).
- Auto-close issue : quand Status devient Terminé → Close issue.
- Tri par champ numérique PhaseNo (si présent).

Voir [docs/WORKFLOWS.md](docs/WORKFLOWS.md) pour le détail cliquable.
