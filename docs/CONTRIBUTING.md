# Contributing

## Branches & PR
- Créez une branche descriptive : `feat/...`, `chore/...`, `fix/...`.
- Ouvrez une PR vers `main`. Labels : `phase:*`, `type:*` (si existants).
- **Interdit** : merger soi-même vers `main` si la CI n’est pas verte.

## Qualité
```bash
make fmt && make lint && make test
poetry run pre-commit install

Dépendances

Runtime : Python 3.12.

Si pyproject.toml change, mettez à jour poetry.lock :

poetry lock --no-update
poetry install
git add poetry.lock

CI

Actions: checkout → setup-python (3.12) → poetry install → lint → tests.

Garde-fou :

poetry check --lock || poetry lock --no-update
