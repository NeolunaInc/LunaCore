
Phase 1 — Orchestrator minimal
Livrables
Endpoint GET /healthz → {"status":"ok"}

Test d’intégration httpx

Cible make run-api

Vérification
bash
Copier le code
poetry run pytest -q      # 1 passed
make run-api              # → http://localhost:8000/healthz
Notes
Logs JSON via core/logging (activé à l’import).

OLLAMA_BASE_URL défini côté hôte pour les phases suivantes.
