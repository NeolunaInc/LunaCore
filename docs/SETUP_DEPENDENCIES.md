# Setup & Dépendances

## OS & paquets système (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y git curl jq make build-essential \
  python3.12 python3.12-venv pipx \
  docker.io docker-compose-plugin
pipx ensurepath

Python & Poetry

Python : 3.12 (runtime unique).

Poetry : pipx install poetry (≥ 1.8).

poetry env use 3.12
poetry install
poetry run pre-commit install

Outils dev

black (formatter), ruff (lint), pytest (tests).

pre-commit hooks (black/ruff/end-of-file/merge-conflict).

Makefile utiles :

make fmt && make lint && make test

make run-api → FastAPI local (Uvicorn 0.30+)

Conteneurs
docker compose up -d db redis
# (Ollama local recommandé sur l’hôte; sinon service ollama du compose)

Variables d’environnement

OLLAMA_BASE_URL (par défaut http://localhost:11434 si installé sur l’hôte).

CI GitHub Actions

Python 3.12.

Étapes : checkout → setup-python → install Poetry → poetry install → lint → tests.

Garde-fou lockfile :

- name: Force Poetry to use runner Python
  run: poetry env use $(python -c "import sys; print(sys.executable)")
- name: Ensure lock matches pyproject
  run: poetry check --lock || poetry lock --no-update
