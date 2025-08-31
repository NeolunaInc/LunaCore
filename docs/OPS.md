# OPS / RUNBOOKS — LunaCore

## Raccourcis
- Formatter: `make fmt`
- Linter: `make lint`
- Tests: `make test` (ou `poetry run pytest -q`)
- API dev: `make run-api` → `GET /healthz`
- BDD & Redis: `docker compose up -d db redis`

## Cycle dev standard
1. `git checkout -b feat/…` (ou `chore/…`, `fix/…`)
2. `poetry install && poetry run pre-commit install`
3. Dev → `make fmt && make lint`
4. Tests → `make test`
5. `git add -A && git commit -m "..." && git push`
6. PR vers `main` (labels : `phase:*`, `type:*`, `priority:*`, + `tooling`/`ci` si pertinent)
7. CI verte → merge `squash & merge`

## Conventions Git
- Branch: `feat/phaseN-…`, `chore/…`, `fix/…`
- Message: `Type: objet — détail court` (ex: *Docs: setup & deps*).

## Labels GitHub (doivent exister)
- `phase:*` (foundation / critical-infra / interface / advanced / enterprise)
- `type:*` (feature, bug, documentation, test)
- `priority:*` (critical, high, medium, low)
- **Compléments ajoutés** : `ci`, `tooling` ✅ (cf. `scripts/labels_seed_extra.sh`)

## Release simple
- CI verte, changelog court dans la PR.
- Tagging (optionnel) : `gh release create v0.1.0 -n "Phase 1 Orchestrator"`.

## Artefacts & reset local
- Volumes Docker : `docker compose down -v` pour reset.
- **Ignorer** `export/` (voir `.gitignore`).
- Nettoyage cache : `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`.

## Sécurité & secrets
- Pas de secrets en clair dans Git.
- `.env` local non versionné, secrets GitHub Actions côté repo.

## Observabilité (phase 24 à venir)
- Logs JSON (déjà actifs via `core/logging.py`).
- Slots prévus : `/metrics` Prometheus, OpenTelemetry traces.
