from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.services.churn_service import ChurnService
from backend.services.rfm_service import RFMService
from backend.services.retention_service import RetentionService
from backend.services.sentiment_service import SentimentService
from backend.services.analyst_service import AnalystService


def get_churn_service(db: AsyncSession = Depends(get_db)) -> ChurnService:
    return ChurnService(db)


def get_rfm_service(db: AsyncSession = Depends(get_db)) -> RFMService:
    return RFMService(db)


def get_retention_service(db: AsyncSession = Depends(get_db)) -> RetentionService:
    return RetentionService(db)


def get_sentiment_service(db: AsyncSession = Depends(get_db)) -> SentimentService:
    return SentimentService(db)


def get_analyst_service(db: AsyncSession = Depends(get_db)) -> AnalystService:
    return AnalystService(db)
