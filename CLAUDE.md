# CLAUDE.md — StayWise Project Memory

> This file is auto-loaded by Claude Code at every session.
> Keep this updated as the project evolves.

---

## What this project is

StayWise is a **production-grade MLOps platform** for **e-commerce customer churn prediction
and retention analytics**. It ingests transactional data via Kafka, engineers RFM features
through Airflow pipelines, scores churn probability using MLflow-tracked models, and surfaces
insights via a Next.js dashboard with an AI-powered analytics chatbot (Ollama + SSE streaming).

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.12) |
| Database | PostgreSQL (star schema, 9+ tables) |
| Cache | Redis |
| Message queue | Kafka |
| Orchestration | Apache Airflow |
| ML tracking | MLflow |
| Model storage | AWS S3 |
| Frontend | Next.js 14 (App Router) + TypeScript |
| UI components | shadcn/ui + Recharts + TanStack Table |
| AI Analyst | Ollama (SSE streaming) |
| NLP | IndoBERT (`mdhugol/indonesia-bert-sentiment-classification`) |
| Containerization | Docker Compose (VPS profile + local profile) |

---

## Project structure (key paths)

```
staywise/
├── backend/
│   ├── api/v1/          # Route handlers only — no business logic here
│   ├── core/            # Config, auth, Depends() injection
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response contracts
│   ├── services/        # ALL business logic lives here
│   ├── workers/         # Kafka consumer, async batch jobs
│   └── db/              # Session, base, Alembic migrations
├── ml/
│   ├── training/        # Feature engineering, churn labeling, model training
│   ├── models/          # Versioned model artifacts
│   ├── evaluation/      # Golden dataset, offline eval, eval results
│   └── prompts/         # AI Analyst prompt templates + registry
├── pipelines/
│   └── dags/            # Airflow DAGs: rfm_feature, churn_labeling, scoring, retention
├── observability/       # Tracer, feedback capture, LLM cost tracker
├── frontend/            # Next.js App Router, shadcn/ui, Recharts, TanStack Table
└── docker/              # docker-compose.yml (prod) + docker-compose.dev.yml (infra only)
```

---

## Key architectural decisions

### Separation of concerns (non-negotiable)
- `models/` (SQLAlchemy ORM) and `schemas/` (Pydantic) are **always separate** — never mix them
- Business logic belongs **exclusively in `services/`** — route handlers only call services
- All config via `core/config.py` (pydantic-settings) — **zero hardcoded values**
- Background/async jobs go in `workers/` — never inline in route handlers

### ML pipeline flow
```
Kafka → workers/kafka_consumer.py
      → PostgreSQL (raw transactions)
      → Airflow rfm_feature_dag (RFM calculation)
      → Airflow churn_labeling_dag (label generation)
      → MLflow training run (XGBoost/LightGBM)
      → Airflow scoring_dag (batch churn scores → DW)
      → FastAPI churn.py endpoint → Next.js dashboard
```

### AI Analyst (Ollama SSE)
- Prompt templates are versioned in `ml/prompts/templates.py`
- Never hardcode prompts in `analyst_service.py` — always import from registry
- SSE streaming via FastAPI `StreamingResponse` — never buffer the full response
- Cost and latency tracked in `observability/cost_tracker.py`

### Docker Compose profiles
- `docker-compose.dev.yml` — infrastructure only (PostgreSQL, Redis, Kafka, Airflow, MLflow)
  App runs locally for faster iteration
- `docker-compose.yml` — full production, all services containerized
  Internal services bound to `127.0.0.1` — never expose DB/Redis ports publicly

### Database (PostgreSQL star schema)
- All tables have `UUID` primary keys, `created_at`, `updated_at`
- Fact tables: `fact_transactions`, `fact_churn_predictions`
- Dimension tables: `dim_customers`, `dim_products`, `dim_date`, `dim_geography`
- Aggregate tables: `agg_rfm_scores`, `agg_customer_segments`
- Migrations managed via Alembic — never alter tables manually

---

## Coding conventions

- Type hints on **all** function signatures
- Docstrings on all service methods
- SQLAlchemy 2.0 style: use `Mapped[]` annotations
- f-strings over `.format()`
- Router prefix defined in the router file, not in `main.py`
- Response models always specified on endpoints
- Commit messages follow **Conventional Commits** spec

### Naming
| Entity | Convention |
|---|---|
| Files | `snake_case` |
| Classes | `PascalCase` |
| Functions/variables | `snake_case` |
| Constants | `UPPER_SNAKE_CASE` |
| DB tables | plural `snake_case` |

---

## Current development phase

**Phase [ ] — [ ]**

- [ ] Phase 1 — Foundation (FastAPI skeleton, DB connection, auth, health check)
- [ ] Phase 2 — Data Layer (Kafka consumer, Airflow DAGs, S3 integration)
- [ ] Phase 3 — ML Layer (feature engineering, MLflow training, batch scoring)
- [ ] Phase 4 — API + UI (all endpoints, Next.js dashboard, AI Analyst)
- [ ] Phase 5 — Production (CI/CD, monitoring, observability, docs)

---

## Do NOT do

- Never put business logic in route handlers (`api/`)
- Never hardcode config values — use `core/config.py`
- Never mix ORM models with Pydantic schemas
- Never commit secrets — always use `.env` (gitignored)
- Never expose PostgreSQL/Redis/Kafka ports to `0.0.0.0` in production
- Never inline prompts in `analyst_service.py` — use `ml/prompts/registry.py`
- Never alter DB tables manually — always use Alembic migrations
- Never buffer SSE responses — stream them

---

## Common commands

```bash
# Dev: start infra only, run app locally
make dev

# Run all migrations
make migrate

# Seed sample e-commerce data
make seed

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint
make lint

# Full production stack
make up

# Tear down
make down

# View logs
make logs SERVICE=backend
```

---

## Environment variables (see .env.example)

Key variables Claude should be aware of:

```
DATABASE_URL          # PostgreSQL connection string
REDIS_URL             # Redis connection
KAFKA_BOOTSTRAP       # Kafka broker address
MLFLOW_TRACKING_URI   # MLflow server URI
AWS_S3_BUCKET         # Model artifact bucket
OLLAMA_BASE_URL       # Ollama server for AI Analyst
JWT_SECRET_KEY        # Auth secret
```
