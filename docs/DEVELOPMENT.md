
Guide Développement
Prérequis
Python 3.12, Poetry, Docker, Docker Compose.

Outils : black, ruff, pytest, pre-commit.

Installation
bash
Copier le code
poetry install
poetry run pre-commit install
Lancer l’API
bash
Copier le code
make run-api
# puis GET http://localhost:8000/healthz
Qualité & tests
bash
Copier le code
# Optional Poetry setup
poetry install  # or use .venv with pip
# Run pre-commit lint locally
pre-commit run -a
# Regenerate agent schema
python scripts/gen_agent_schema.py
# Run tests for Phase 2+3
PYTHONPATH="$(pwd)" pytest -q tests/test_task_graph.py tests/test_task_decomposer.py tests/test_agent_registry.py tests/test_agent_schema.py
# Note: CI sets PYTHONPATH automatically
Services de base
bash
Copier le code
docker compose up -d db redis
Ollama (modèle local)
Par défaut nous utilisons Ollama sur l’hôte (port 11434).

Déclarer: echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env

Vérifier: curl -s http://localhost:11434/api/tags

Stratégie Git
Branches par phase/feature: feat/phaseN-…

PR avec label phase:N, squash & merge.

Hooks pre-commit actifs (black/ruff/end-of-file/merge-conflicts).
