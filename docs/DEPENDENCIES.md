# Dependencies

## Tableau des dépendances Poetry

| Package | Rôle | Où utilisé | Contrainte | Notes compatibilité 3.12 |
|---------|------|------------|------------|--------------------------|
| fastapi | Framework API web | orchestrator/app.py | ^0.115.0 | Testé 0.115.14, ASGI |
| pydantic | Validation schémas | core/, orchestrator/ | ^2.8.0 | Testé 2.11.7, dotenv extra |
| uvicorn | Serveur ASGI | make run-api | ^0.30.0 | Testé 0.30.6, standard extras |
| loguru | Logging structuré | core/logging.py | ^0.7.2 | Testé 0.7.3, compatible 3.12 |
| python-json-logger | Logs JSON | core/logging.py | ^2.0.7 | Testé 2.0.7, format JSON |
| black | Formatage code | CI, dev | ^24.4.2 | Testé 24.10.0, py312 target |
| ruff | Linting + format | CI, dev | ^0.5.4 | Testé 0.5.7, py312 target |
| pytest | Tests unitaires | tests/ | ^8.3.0 | Testé 8.4.1, -q mode |
| pytest-cov | Couverture tests | CI | ^5.0.0 | Testé 5.0.0 |
| mypy | Vérification types | CI, dev | ^1.11.0 | Testé 1.17.1, py312 |
| pre-commit | Hooks git | .pre-commit-config.yaml | ^3.7.1 | Testé 3.8.0 |
| httpx | Client HTTP tests | tests/test_healthz.py | ^0.28.1 | Testé 0.28.1 |

## Dépendances transitives majeures
- annotated-types: Contraintes types
- anyio: Concurrence asyncio
- certifi: Certificats SSL
- click: CLI (black)
- h11: HTTP/1.1
- httptools: HTTP parsing
- idna: Noms domaine
- mypy-extensions: Extensions mypy
- packaging: Gestion versions
- pathspec: Patterns fichiers
- platformdirs: Dirs plateforme
- pluggy: Validation config
- pydantic-core: Core pydantic
- pygments: Coloration syntaxe
- pyyaml: YAML parsing
- sniffio: Détection async
- starlette: Base FastAPI
- typing-extensions: Types avancés
- uvloop: Boucle événementielle
- watchfiles: Surveillance fichiers
- websockets: WebSockets
- python-dotenv: Vars env
