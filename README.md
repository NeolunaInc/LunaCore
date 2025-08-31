# LunaCore

Socle d’orchestration d’agents (Python 3.12 uniquement / FastAPI) avec outillage dev (Poetry, pre-commit, black/ruff, pytest).

## Sommaire

- [Démarrage rapide](#démarrage-rapide)
- [Qualité & tests](#qualité--tests)
- [Services de base](#services-de-base)
- [API](#api)
- [Variables d’environnement](#variables-denvironnement)

## Démarrage rapide

```bash
# Dépendances Python
poetry install
poetry run pre-commit install
```

## Qualité & tests

```bash
make fmt && make lint && make test
```

## Services de base

```bash
docker compose up -d db redis
```

## API

```bash
make run-api   # puis GET http://localhost:8000/healthz
```

## Variables d’environnement

- OLLAMA_BASE_URL (défaut http://localhost:11434)
- Commande de vérif: `curl -s http://localhost:11434/api/tags`

## Structure (extrait)

- orchestrator/
  - app.py            # FastAPI + /healthz
- core/
  - logging.py        # config logs JSON à l’import
- tests/
  - test_healthz.py   # test d’intégration httpx
- Makefile            # run-api, fmt, lint, test

## Board & workflows (résumé)

Statuts : Backlog, Sprint actuel, En développement, Review/Test, Terminé.

Item added to project (Issues) → Status=Backlog.

Item reopened → Status=Backlog.

Item closed → Status=Terminé.

Pull request merged → Status=Terminé.

Auto-add to project : filtre Repo=NeoLunaInc/LunaCore, is:issue (pas PR).

Auto-close issue : quand Status devient Terminé → Close issue.

Tri par champ numérique PhaseNo (si présent).

Voir docs/WORKFLOWS.md pour le détail cliquable.
