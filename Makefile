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
