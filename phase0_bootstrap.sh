#!/usr/bin/env bash
set -euo pipefail

echo "🧰 Creating folders..."
mkdir -p core orchestrator agents services tests .github/workflows

echo "📝 Writing pyproject.toml..."
cat > pyproject.toml <<'PYTOML'
[tool.poetry]
name = "lunacore"
version = "0.1.0"
description = "Orchestrateur multi-agents pour génération automatisée de logiciels"
authors = ["NeoLunaInc"]
readme = "README.md"
packages = [{ include = "core" }, { include = "orchestrator" }, { include = "agents" }, { include = "services" }]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
pydantic = {version="^2.8.0", extras=["dotenv"]}
uvicorn = {version="^0.30.0", extras=["standard"]}
python-json-logger = "^2.0.7"
loguru = "^0.7.2"

[tool.poetry.group.dev.dependencies]
black = "^24.4.2"
ruff = "^0.5.4"
pytest = "^8.3.0"
pytest-cov = "^5.0.0"
mypy = "^1.11.0"
pre-commit = "^3.7.1"

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E","F","I","UP","B","SIM","W"]
ignore = []
fix = true
exclude = ["venv",".venv",".git"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --maxfail=1 --disable-warnings"

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
PYTOML

echo "⚙️ Writing Makefile..."
cat > Makefile <<'MK'
.PHONY: install fmt lint test docker-up docker-down
install:
	poetry install
fmt:
	poetry run black .
lint:
	poetry run ruff check .
test:
	poetry run pytest
docker-up:
	docker compose up -d
docker-down:
	docker compose down -v
MK

echo "🔧 pre-commit config..."
cat > .pre-commit-config.yaml <<'YML'
repos:
- repo: https://github.com/psf/black
  rev: 24.4.2
  hooks: [ { id: black } ]
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.5.4
  hooks: [ { id: ruff, args: ["--fix"] } ]
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.6.0
  hooks:
    - id: check-merge-conflict
    - id: end-of-file-fixer
YML

echo "🧪 smoke test + logging..."
mkdir -p core
cat > core/logging.py <<'PY'
import json, logging, sys
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonFormatter())
logging.basicConfig(handlers=[_handler], level=logging.INFO, force=True)
PY

cat > tests/test_smoke.py <<'PY'
def test_math_works():
    assert 1 + 1 == 2
PY

echo "🐳 docker-compose (PostgreSQL, Redis, Ollama)..."
cat > docker-compose.yml <<'YML'
version: "3.9"
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: lunacore
    ports: ["5432:5432"]
    volumes: [ "db_data:/var/lib/postgresql/data" ]
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: [ "ollama_data:/root/.ollama" ]
volumes:
  db_data: {}
  ollama_data: {}
YML

echo "🤖 GitHub Actions CI..."
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YML'
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Poetry
        run: pipx install poetry
      - name: Install deps
        run: poetry install
      - name: Lint
        run: poetry run ruff check . && poetry run black --check .
      - name: Tests
        run: poetry run pytest -q --maxfail=1 --disable-warnings
YML

echo "📦 init packages..."
touch core/__init__.py orchestrator/__init__.py agents/__init__.py services/__init__.py

echo "✅ Done."
