# LunaCore — Statut Phase 1 (FAIT)

## Résumé
- **Runtime unique**: Python **3.12** (Poetry).
- **Orchestrator minimal**: FastAPI `/healthz` → `{"status": "ok"}`.
- **Qualité**: black, ruff, pytest, pre-commit.
- **CI GitHub Actions**: build sur Python 3.12, `poetry install`, lint, tests.
- **Conteneurs de base**: docker-compose (PostgreSQL, Redis, Ollama).
- **Logging**: JSON via `core/logging.py` (formatter custom).

## Détails livrés
- Arborescence: `core/`, `orchestrator/`, `agents/`, `services/`, `tests/`, `docs/`, `.github/workflows/`.
- Endpoint: `orchestrator/app.py` (FastAPI, `/healthz`).
- Tests: `tests/test_healthz.py`, `tests/test_smoke.py`.
- Outils: `.pre-commit-config.yaml`, `Makefile` (`fmt`, `lint`, `test`, `run-api`), `docker-compose.yml`.
- CI: `.github/workflows/ci.yml` (Python 3.12 only).
- Scripts d’environnement: `phase0_bootstrap.sh` (historique).
- Seed tooling (optionnel): `gh_seed_lunacore.sh`, `issues_seed_min.sh`.

## État des tests/CI
- Local: `pytest -q` → **OK**.
- CI: **OK** si `poetry.lock` est régénéré après modif Python (voir CONTRIBUTING).

## Points d’attention (résolus)
- **Poetry lock**: après passage à 3.12, régénérer `poetry.lock` (`poetry lock --no-update`).
- **awk/printf**: dans scripts d’export, éviter `in` comme variable awk et toujours citer les variables dans `printf`.

## Prochain jalon
- Lancer **Phase 2** (squelette `services/` + stub `/v1/generate` + traces corrélées).
