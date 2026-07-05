# d:/SPECTER/phantomshield/backend/main.py
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config import settings
from routers.analysis import router as analysis_router
from routers.features import router as features_router
from routers import dashboard, education, explain, health, scan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading ML models...")
    from ml.predictor import PhishingPredictor

    _ = PhishingPredictor()
    logger.info("PhantomShield API ready")
    yield
    logger.info("Shutting down PhantomShield API")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Based Phishing Detection + Explanation + Education",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(health.router, tags=["health"])
app.include_router(scan.router, prefix="/api/scan", tags=["scan"])
app.include_router(explain.router, prefix="/api/explain", tags=["explain"])
app.include_router(education.router, prefix="/api/education", tags=["education"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(features_router, prefix="/api/features", tags=["features"])


@app.get("/")
def root():
    return {
        "name": "PhantomShield API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "endpoints": {
            "scan_url": "POST /api/scan/url",
            "scan_email": "POST /api/scan/email",
            "scan_sms": "POST /api/scan/sms",
            "batch_scan": "POST /api/scan/batch",
            "dashboard": "GET  /api/dashboard/{user_id}",
            "docs": "GET  /docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
