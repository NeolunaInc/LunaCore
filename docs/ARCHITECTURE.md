
Architecture (aperçu)
FastAPI Orchestrator (orchestrator/app.py) : Endpoints, health, wiring services.

Core logging (core/logging.py) : configuration logs JSON à l’import.

Tests (tests/) : Pytest, intégration via httpx.

Futur :

services/ : adaptateurs et appels modèles (Ollama), patterns ports/adapters.

Observabilité : métriques, traces (Phase 24).

Packaging & Delivery : images, versioning, CD (Phase 18).

Contrats
Réponses JSON stables (champ status, message, data).

Journalisation corrélée (trace_id) à introduire en Phase 2/24.
