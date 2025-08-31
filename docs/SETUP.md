# Setup Guide

## Prérequis OS
- **Ubuntu 22.04/24.04 LTS** (recommandé)
- **WSL2 (Ubuntu)** (Windows)
- **macOS 13+** (optionnel, via Homebrew)

## Ressources système
- **CPU**: 4+ cœurs
- **RAM**: 8 Go+ (16 Go recommandé si Ollama)
- **Disque**: 10 Go+ SSD

## Outils système (installer via sudo apt)
```bash
sudo apt update
sudo apt install -y build-essential git curl make jq unzip
sudo apt install -y docker.io docker-compose-v2  # ou Docker Engine officiel
sudo apt install -y gh  # GitHub CLI
sudo apt install -y libpq-dev pkg-config  # pour clients Postgres
```

## Python (option 1: pyenv recommandé)
```bash
curl https://pyenv.run | bash
# Ajouter à ~/.bashrc : export PATH="$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init -)"
pyenv install 3.12.7  # version testée
pyenv global 3.12.7
```

## Python (option 2: PPA deadsnakes)
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv
```

## Outils applicatifs
- **Poetry** (>= 1.7): `pipx install poetry`
- **Ollama** (hôte): Télécharger depuis ollama.ai, port 11434
- **Postgres/Redis**: Via docker compose

## Versions minimales et testées
| Package | Rôle | Contrainte min | Version testée |
|---------|------|----------------|----------------|
| fastapi | API web | ^0.115.0 | 0.115.14 |
| pydantic | Schémas/validation | ^2.8.0 | 2.11.7 |
| uvicorn | Serveur ASGI | ^0.30.0 | 0.30.6 |
| loguru | Logging | ^0.7.2 | 0.7.3 |
| python-json-logger | Logs JSON | ^2.0.7 | 2.0.7 |
| black | Formatage | ^24.4.2 | 24.10.0 |
| ruff | Linting | ^0.5.4 | 0.5.7 |
| pytest | Tests | ^8.3.0 | 8.4.1 |
| mypy | Typage | ^1.11.0 | 1.17.1 |
| pre-commit | Hooks | ^3.7.1 | 3.8.0 |

## Variables d’environnement
- `OLLAMA_BASE_URL`: http://localhost:11434 (défaut)
- *(Réservé phases futures: DB_URL, REDIS_URL)*

## Étapes d’installation (sans sudo)
```bash
poetry install
poetry run pre-commit install
make run-api  # puis curl http://localhost:8000/healthz
make fmt && make lint && make test
```

## Docker Compose
Services: db (Postgres), redis, ollama (volumes persistants, ports exposés).

```bash
docker compose up -d db redis
# Vérifier Ollama: curl -s http://localhost:11434/api/tags
```

## CI
- Python 3.12 only (`.github/workflows/ci.yml`)
- Outils: ruff, black, pytest

## Troubleshooting
- **Ports occupés**: `lsof -i :8000` ou `netstat -tulpn`
- **Droits Docker**: `sudo usermod -aG docker $USER`
- **pyenv shims**: `pyenv rehash`
- **Proxy**: Configurer `http_proxy`/`https_proxy`
