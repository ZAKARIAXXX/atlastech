.PHONY: help dev up down test lint typecheck build install clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd services/api && pip install -e ".[dev]"
	cd apps/web && npm install
	cd packages/schemas && npm install

dev: ## Start all services in development mode
	docker compose up -d postgres redis
	@echo "Waiting for database..."
	@docker compose exec -T postgres sh -c 'until pg_isready -U atlastech; do sleep 1; done'
	cd services/api && python -m alembic upgrade head 2>/dev/null || true
	cd services/api && uvicorn app.main:app --reload --port 8000 &
	cd apps/web && npm run dev

up: ## Start all services via Docker
	docker compose up -d --build

down: ## Stop all services
	docker compose down

test: ## Run all tests
	cd services/api && python -m pytest --cov=app --cov-report=term-missing
	cd packages/schemas && npm run typecheck

lint: ## Lint all code
	cd services/api && ruff check .
	cd services/api && ruff format --check .
	cd apps/web && npm run lint

typecheck: ## Type-check all code
	cd services/api && mypy .
	cd apps/web && npm run typecheck
	cd packages/schemas && npm run typecheck

build: ## Build all packages
	cd apps/web && npm run build

clean: ## Remove build artifacts and caches
	rm -rf apps/web/.next apps/web/out
	rm -rf services/api/dist services/api/build services/api/*.egg-info
	rm -rf packages/schemas/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -prune -o -type f -name "*.pyc" -delete 2>/dev/null || true
