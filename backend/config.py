# d:/SPECTER/phantomshield/backend/config.py
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PhantomShield API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://phantomshield.vercel.app",
    ]

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"

    # Database (Neon PostgreSQL)
    DATABASE_URL: str = ""
    NEON_DATABASE_URL: str = ""
    DB_CONNECT_TIMEOUT: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_PER_HOUR: int = 200

    # ML Model paths
    MODEL_PATH: str = "ml/models"
    RF_MODEL_FILE: str = "random_forest.pkl"
    XGB_MODEL_FILE: str = "xgboost_model.pkl"
    SCALER_FILE: str = "scaler.pkl"

    # Phishing APIs
    PHISHTANK_API_KEY: Optional[str] = None
    VIRUSTOTAL_API_KEY: Optional[str] = None

    # SSL Check timeout
    SSL_CHECK_TIMEOUT: int = 5

    # WHOIS timeout
    WHOIS_TIMEOUT: int = 10

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
