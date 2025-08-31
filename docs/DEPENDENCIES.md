# DEPENDENCIES — LunaCore

## Vue d’ensemble (Poetry)
Runtime: **Python 3.12** (unique).  
Gestionnaire: **Poetry**.

### Dépendances principales (extrait)
| Package              | Contrainte `pyproject` | Version testée (lock) | Rôle / où utilisé |
|----------------------|-------------------------|------------------------|-------------------|
| fastapi              | ^0.115.0               | 0.115.14               | API (`orchestrator/app.py`) |
| pydantic (+core)     | ^2.8.0                 | 2.11.7 (core 2.33.2)   | Modèles/validation |
| uvicorn[standard]    | ^0.30.0                | (dans lock)            | Serveur ASGI |
| loguru               | ^0.7.2                 | 0.7.3                  | Logging évolué |
| python-json-logger   | ^2.0.7                 | (dans lock)            | Format JSON logs |
| anyio/h11/starlette  | transitives            | 4.10.0 / 0.16.0 / …    | ASGI stack |

### Dépendances de dev (extrait)
| Package      | Contrainte | Version testée | Rôle |
|--------------|------------|----------------|------|
| black        | ^24.4.2    | 24.10.0        | Formatage |
| ruff         | ^0.5.4     | 0.5.x          | Lint |
| pytest       | ^8.3.0     | 8.3.x          | Tests |
| pytest-cov   | ^5.0.0     | 7.10.6 (cov)   | Couverture |
| mypy         | ^1.11.0    | 1.17.1         | Typage |
| pre-commit   | ^3.7.1     | 3.8.0          | Hooks |
| httpx        | (dev)      | 0.28.1         | Tests d’intégration |

> Les versions “testées” proviennent du `poetry.lock` que tu as partagé.  
> Pour la **liste exhaustive**, utilise le script `scripts/deps_table.sh` (ci-dessous).
