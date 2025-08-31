#!/usr/bin/env bash
set -euo pipefail
echo "== LunaCore bootstrap (read-only guidance) =="
echo "Sections:"
cat <<'TXT'
1) Ubuntu/WSL packages (sudo):
   sudo apt-get update
   sudo apt-get install -y \
     build-essential git curl make jq unzip ca-certificates gnupg lsb-release \
     pkg-config libpq-dev software-properties-common
   # Docker, gh: voir docs/SETUP.md

2) Python 3.12 via pyenv:
   curl https://pyenv.run | bash
   pyenv install 3.12.5 && pyenv local 3.12.5

3) Poetry:
   pip install -U pip pipx && pipx ensurepath && pipx install poetry

4) Projet:
   poetry install && poetry run pre-commit install
   docker compose up -d db redis
   make run-api   # GET /healthz

5) Qualité:
   make fmt && make lint && make test
TXT
