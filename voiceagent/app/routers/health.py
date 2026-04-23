# voiceagent/app/routers/health.py
import logging
from fastapi import APIRouter
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "services": {
            "acs": "configured" if settings.ACS_CONNECTION_STRING else "not configured",
            "openai": "configured" if settings.AZURE_OPENAI_API_KEY else "not configured",
            "storage": "configured" if settings.AZURE_STORAGE_CONNECTION_STRING else "not configured",
        }
    }