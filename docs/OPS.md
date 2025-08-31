# Operations Guide

## Commandes fréquentes
- **API dev**: `make run-api` (port 8000)
- **Services**: `docker compose up -d db redis`
- **Tests**: `poetry run pytest -q`
- **Lint**: `poetry run ruff check .`
- **Format**: `poetry run black .`
- **Pre-commit**: `poetry run pre-commit run --all-files`

## Checklist release
- [ ] CI verte (Python 3.12)
- [ ] `make fmt && make lint && make test`
- [ ] Bump version (pyproject.toml)
- [ ] Tag: `git tag v0.2.0`
- [ ] Push: `git push origin v0.2.0`
- [ ] Changelog court
- [ ] Artefacts ignorés (.gitignore)

## Sauvegardes et volumes
- **Postgres**: Volume `lunacore_db_data`
- **Redis**: Volume `lunacore_redis_data`
- **Ollama**: Volume `ollama_data` (modèles)

## Reset local
```bash
docker compose down -v  # Supprime volumes
rm -rf .venv poetry.lock
poetry install
```

## Monitoring
- Health: `GET /healthz`
- Logs: JSON format (loguru + python-json-logger)
- Ollama: `curl http://localhost:11434/api/tags`
