# AGENTS.md — Agent Behavior Rules for StayWise

> This file defines how AI coding agents (Claude Code, Cursor, Copilot, etc.)
> should behave when working on this codebase. Read this before making any changes.

---

## Core mandate

You are assisting with a **production MLOps codebase** for e-commerce churn prediction.
Every decision should optimize for: **correctness > maintainability > performance**.
Never sacrifice correctness for speed. Never take shortcuts that create hidden state.

---

## Before you write any code

1. **Read `CLAUDE.md`** — understand the project, stack, and architecture decisions
2. **Read `.claude/rules/code-style.md`** — understand naming and style conventions
3. **Read `.claude/rules/testing.md`** — understand how to write tests for this codebase
4. **Check existing patterns** — before adding a new service, look at an existing one
5. **Ask before opinionated decisions** — explain the tradeoff first, then wait for confirmation

---

## Layer rules (strictly enforced)

### `api/v1/*.py` — route handlers
- **Only allowed**: receive request, call one service method, return response
- **Never allowed**: database queries, business logic, ML inference, external API calls
- Every endpoint must declare a `response_model` from `schemas/`
- Dependencies injected via `Depends()` from `core/deps.py`

```python
# CORRECT
@router.get("/customers/{customer_id}/churn", response_model=ChurnPredictionResponse)
async def get_churn_prediction(
    customer_id: UUID,
    service: ChurnService = Depends(get_churn_service),
) -> ChurnPredictionResponse:
    return await service.get_prediction(customer_id)

# WRONG — business logic in route handler
@router.get("/customers/{customer_id}/churn")
async def get_churn_prediction(customer_id: UUID, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    score = model.predict(customer.features)  # never do this here
    return {"score": score}
```

### `services/*.py` — business logic
- All domain logic lives here, nowhere else
- Services receive typed inputs (Pydantic schemas or primitives), return typed outputs
- Services should be testable in isolation — injectable dependencies only
- One service per domain: `churn_service.py`, `rfm_service.py`, etc.

### `models/*.py` — ORM only
- SQLAlchemy 2.0 syntax with `Mapped[]` type annotations
- No Pydantic validators, no computed properties that hit the DB
- Every model: `UUID` PK, `created_at`, `updated_at`

```python
# CORRECT — SQLAlchemy 2.0 style
class Customer(Base):
    __tablename__ = "dim_customers"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
```

### `schemas/*.py` — Pydantic contracts
- Request and response models only — no ORM imports
- Use `model_config = ConfigDict(from_attributes=True)` for ORM→schema conversion
- Separate `Request` and `Response` schemas even if they look similar

### `workers/*.py` — async background jobs
- Kafka consumer, batch scoring, report generation
- Never called directly from route handlers
- Log everything — failures here are silent without it

---

## ML-specific rules

### Prompt management (AI Analyst)
- **Never** hardcode prompts in `analyst_service.py`
- Always import from `ml/prompts/registry.py`
- When modifying a prompt, create a new version — never edit in place

```python
# CORRECT
from ml.prompts.registry import get_prompt

prompt = get_prompt("churn_analysis", version="v2")

# WRONG
prompt = "Analyze the following churn data and provide insights..."
```

### MLflow tracking
- Every training run must log: parameters, metrics, model artifact, feature importance
- Never load a model by path — always use `mlflow.pyfunc.load_model(model_uri)`
- Model URI format: `models:/ChurnPredictor/Production`

### Feature engineering (RFM)
- RFM calculation logic lives in `ml/training/feature_engineering.py`
- The same logic must be used in both training (`ml/`) and inference (`services/rfm_service.py`)
- If you change RFM calculation, you must update both — and retrain the model

### Evaluation
- Any model change must be validated against `ml/evaluation/golden_dataset.json`
- Run `python ml/evaluation/offline_eval.py` before proposing a model update
- Do not propose deploying a model with lower AUC than the current production model

---

## Database rules

- **Never alter tables manually** — always use Alembic: `make migrate`
- **Never use `db.execute(raw_sql)`** for write operations — use ORM
- Raw SQL is acceptable for complex read-only analytics queries — comment why
- Every new table needs a migration file — no model without a migration
- Check constraint: all FK columns must be indexed

---

## SSE streaming (AI Analyst)

```python
# CORRECT — stream, never buffer
async def stream_analysis(query: str) -> AsyncGenerator[str, None]:
    async for chunk in ollama_client.stream(prompt):
        yield f"data: {chunk}\n\n"

# WRONG — buffers entire response, defeats the purpose
response = await ollama_client.complete(prompt)
return response.text
```

---

## Security rules

- Never log secrets, tokens, or PII (emails, customer IDs in plain text)
- Internal services (PostgreSQL, Redis, Kafka) bind to `127.0.0.1` in production Docker
- JWT secrets come from `core/config.py` — never from environment directly in route files
- Validate all UUID inputs with Pydantic — never trust raw string IDs

---

## Testing rules

### When adding a new service method
You must add:
1. A unit test in `tests/unit/test_{service_name}.py` — mock the DB
2. An integration test in `tests/integration/` for the happy path

### Minimum test coverage per endpoint
- Happy path (200)
- Auth failure (401/403)
- Validation failure (422)
- Not found (404) where applicable

### Never test implementation details
Test behavior, not internals. If a test breaks because you renamed a private method, the test was wrong.

---

## Git and commit rules

Follow **Conventional Commits**:

```
feat(churn): add confidence interval to churn predictions
fix(rfm): correct recency calculation for timezone-naive datetimes
perf(scoring): batch MLflow inference calls to reduce latency
refactor(api): move retention logic from route handler to service
test(sentiment): add integration test for IndoBERT pipeline
docs(claude): update current phase to Phase 3
chore(deps): bump mlflow to 2.11.0
```

### Scope reference
| Scope | Covers |
|---|---|
| `churn` | Churn prediction service + model |
| `rfm` | RFM feature engineering |
| `retention` | Retention actions pipeline |
| `sentiment` | IndoBERT sentiment analysis |
| `analyst` | AI Analyst / Ollama SSE |
| `pipeline` | Airflow DAGs |
| `api` | FastAPI routes |
| `db` | Migrations, models |
| `frontend` | Next.js dashboard |
| `infra` | Docker, CI/CD |

---

## What to do when uncertain

1. **Check existing code first** — there's probably an established pattern
2. **Read the relevant service** before touching it
3. **Do not guess at domain logic** (RFM windows, churn thresholds, segment boundaries)
   — ask explicitly. These have business implications.
4. **Do not rename things silently** — breaking changes to schemas affect the frontend
5. **Do not delete files** without confirming — some files look unused but are imported dynamically

---

## End-of-task checklist

After completing any meaningful change:

- [ ] Tests pass: `make test`
- [ ] Linting clean: `make lint`
- [ ] If DB schema changed: migration created and applied
- [ ] If prompt changed: new version registered in `ml/prompts/registry.py`
- [ ] `CLAUDE.md` current phase updated if phase milestone reached
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] Commit with conventional commit message
