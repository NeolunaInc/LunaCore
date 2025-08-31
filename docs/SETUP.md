# SETUP — LunaCore (Python 3.12 only / FastAPI)

Ce document décrit l’installation **poste dev** et les prérequis d’exécution locale.

## 1) Plateformes supportées
- Ubuntu 22.04 / 24.04 LTS (✅ recommandé)
- WSL2 (Ubuntu) sous Windows 11 (✅)
- macOS 13+ (Apple Silicon/Intel) (✅)

**Ressources minimales** : CPU 4 vCPU, RAM 8 Go (16 Go si usage Ollama), disque 10 Go+.  
**Réseau** : accès GitHub, registries Docker.

## 2) Outils & paquets système

### Ubuntu/WSL (à exécuter avec `sudo`)
```bash
apt-get update
apt-get install -y --no-install-recommends \
  build-essential git curl make jq unzip ca-certificates gnupg lsb-release \
  pkg-config libpq-dev software-properties-common
# Docker Engine + Compose v2 (méthode officielle conseillée)
# Voir: https://docs.docker.com/engine/install/ubuntu/ (ajout du repo Docker)
# Ou, simple (moins “prod”):
# curl -fsSL https://get.docker.com | sh
# Ajout groupe docker (relogin nécessaire)
usermod -aG docker "$USER" || true
# GitHub CLI (gh)
type -p apt-add-repository >/dev/null || apt-get install -y software-properties-common
apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0 || true
apt-add-repository -y ppa:github-cli/ppa && apt-get update
apt-get install -y gh

macOS (Homebrew)
xcode-select --install || true
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git curl jq coreutils docker gh
# Docker Desktop conseillé pour macOS

Python (3.12.x)

Option 1 — pyenv (recommandé) :

curl https://pyenv.run | bash
# Ajouter à ton shell (~/.bashrc ou ~/.zshrc) :
# export PATH="$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"
pyenv install 3.12.5
pyenv local 3.12.5


Option 2 — PPA deadsnakes (Ubuntu) :

add-apt-repository -y ppa:deadsnakes/ppa && apt-get update
apt-get install -y python3.12 python3.12-venv python3.12-dev

Poetry & utilitaires
pip install -U pip pipx
pipx ensurepath
pipx install poetry

3) Dépendances applicatives (Services)

PostgreSQL et Redis : via docker compose (fourni).

Ollama : par défaut sur l’hôte (port 11434).

Vérifier : curl -s http://localhost:11434/api/tags.

4) Variables d’environnement

OLLAMA_BASE_URL (défaut: http://localhost:11434)

Slots futurs : DATABASE_URL (Postgres), REDIS_URL

Ajouter dans .env à la racine :

echo 'OLLAMA_BASE_URL=http://localhost:11434' >> .env

5) Installation projet
poetry install
poetry run pre-commit install
make fmt && make lint && make test
make run-api     # → GET http://localhost:8000/healthz doit renvoyer {"status":"ok"}

6) Docker compose (db/redis)
docker compose up -d db redis
docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'
# db → 5432/tcp ; redis → 6379/tcp

7) Problèmes fréquents

Permission Docker : exécute sudo usermod -aG docker $USER puis relogin.

Port occupé : ss -ltnp | grep :5432 (ou 6379/11434).

WSL horloge/FS : wsl --shutdown puis relancer.

Proxy : configurer HTTP(S)_PROXY + pip config set global.proxy ....

8) CI & Qualité

Runtime unique : Python 3.12 (CI GitHub Actions).

Outils : ruff, black, pytest, pre-commit.

Avant PR : make fmt && make lint && make test.
