from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1 import customers, churn, rfm, retention, sentiment, analyst, auth
from backend.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(churn.router, prefix="/api/v1/churn", tags=["churn"])
app.include_router(rfm.router, prefix="/api/v1/rfm", tags=["rfm"])
app.include_router(retention.router, prefix="/api/v1/retention", tags=["retention"])
app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["sentiment"])
app.include_router(analyst.router, prefix="/api/v1/analyst", tags=["analyst"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
