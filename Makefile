.PHONY: help dev up down logs lint test test-cov migrate seed format

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Infrastructure ───────────────────────────────────

dev: ## Start infra only (DB, Redis, Kafka, Airflow, MLflow) — app runs locally
	docker compose -f docker/docker-compose.dev.yml up -d

up: ## Start full production stack
	docker compose -f docker/docker-compose.yml up -d

down: ## Stop all services
	docker compose -f docker/docker-compose.yml down

logs: ## Tail logs for a service (make logs SERVICE=backend)
	docker compose -f docker/docker-compose.yml logs -f $(SERVICE)

# ─── Backend ──────────────────────────────────────────

run: ## Run FastAPI locally (dev mode)
	cd backend && uvicorn main:app --reload --port 8000

migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration (make migrate-create MSG="add rfm table")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed sample e-commerce data
	python scripts/seed.py

# ─── ML ───────────────────────────────────────────────

train: ## Run churn model training
	python ml/training/train_churn.py

eval: ## Run offline evaluation against golden dataset
	python ml/evaluation/offline_eval.py

# ─── Frontend ─────────────────────────────────────────

frontend-dev: ## Run Next.js dev server
	cd frontend && npm run dev

frontend-build: ## Build Next.js for production
	cd frontend && npm run build

# ─── Code Quality ─────────────────────────────────────

lint: ## Run ruff linter
	ruff check backend/ ml/ pipelines/ observability/

format: ## Run ruff formatter
	ruff format backend/ ml/ pipelines/ observability/

typecheck: ## Run mypy type checker
	mypy backend/

# ─── Testing ──────────────────────────────────────────

test: ## Run all tests
	pytest tests/

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=backend --cov-report=term-missing --cov-report=html

test-unit: ## Run unit tests only
	pytest tests/unit/

test-integration: ## Run integration tests only
	pytest tests/integration/

# ─── Maintenance ──────────────────────────────────────

backup: ## Backup PostgreSQL to S3
	bash scripts/backup.sh
