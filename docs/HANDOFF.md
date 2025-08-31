# HANDOFF — Reprise de flambeau

## État au {DATE_ISO}
- Langage/runtime : **Python 3.12 only**
- CI : GitHub Actions, job unique 3.12 (ruff, black, pytest)
- Branches récentes aperçues pendant la session :
  - `chore/py312-ci-matrix` (export précédent)
  - `chore/phase1-polish-py312-ci` (PR visible dans la session, ex. #33)
- Écart remarqué : ajout de labels `ci`/`tooling` échouait car inexistants → corrigé par script d’amorçage (voir `scripts/labels_seed_extra.sh`).

## Architecture (Phase 1)
- `orchestrator/app.py` : FastAPI + `GET /healthz` → `{"status":"ok"}`
- `core/logging.py` : logs JSON au chargement (stdout)
- `docker-compose.yml` : services `db` (Postgres), `redis`, `ollama` (optionnel)
- `tests/test_healthz.py` : test d’intégration (httpx/pytest)
- Makefile : `run-api`, `fmt`, `lint`, `test`

## Environnements
- `OLLAMA_BASE_URL` (défaut `http://localhost:11434`) — **recommandé** : Ollama sur l’hôte.
- Ports :
  - API dev : `8000` (uvicorn)
  - Postgres : `5432` ; Redis : `6379` ; Ollama : `11434`

## Qualité
- pre-commit: black, ruff, end-of-file, merge-conflict
- `make fmt && make lint && make test`

## Liens docs
- `docs/SETUP.md` — setup poste & services
- `docs/OPS.md` — runbooks dev/QA
- `docs/DEPENDENCIES.md` — dépendances & script d’export
- `docs/PHASES/MASTER_PLAN.md` — phases 2→26
- `docs/PHASES/phase-2-taskgraph.md` — design exécutable phase 2

## Checklist prise en main (30 minutes)
1. Cloner le repo, créer branche `feat/...`
2. Installer Python 3.12 (pyenv), Poetry
3. `poetry install && poetry run pre-commit install`
4. `docker compose up -d db redis`
5. (Optionnel) installer Ollama hôte, vérifier `11434`
6. `make run-api` → `GET /healthz` OK
7. `make fmt && make lint && make test`
8. Dev feature, commit, push
9. `gh pr create --fill -B main` + labels (`phase:*`, `type:*`, `tooling/ci` si besoin)
10. Attendre CI verte → merge
