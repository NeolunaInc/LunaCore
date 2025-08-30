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

.PHONY: run-api
run-api:
	poetry run uvicorn orchestrator.app:app --host 0.0.0.0 --port 8000 --reload
