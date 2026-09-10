.PHONY: help dev up down test lint typecheck build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start all services in development mode
	docker compose up -d postgres redis
	@echo "Waiting for database..."
	@sleep 3
	cd services/api && python -m alembic upgrade head 2>/dev/null || true
	cd services/api && uvicorn app.main:app --reload --port 8000 &
	cd apps/web && npm run dev

up: ## Start all services via Docker
	docker compose up -d --build

down: ## Stop all services
	docker compose down

test: ## Run all tests
	cd services/api && python -m pytest --cov=app --cov-report=term-missing
	cd apps/web && npm run lint

lint: ## Lint all code
	cd services/api && ruff check .
	cd services/api && mypy .
	cd apps/web && npm run lint

typecheck: ## Type-check all code
	cd services/api && mypy .
	cd apps/web && npm run typecheck

build: ## Build all packages
	cd apps/web && npm run build
