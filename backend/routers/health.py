# d:/SPECTER/phantomshield/backend/routers/health.py
# Health endpoint.

from datetime import datetime

from fastapi import APIRouter

from config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }
