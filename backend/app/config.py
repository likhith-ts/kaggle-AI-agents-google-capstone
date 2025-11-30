"""
Configuration management for the backend application.

Loads environment variables and provides typed configuration objects.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine environment and find the appropriate .env file
_backend_dir = Path(__file__).resolve().parent.parent
_root_dir = _backend_dir.parent
_app_env = os.getenv("APP_ENV", "development")

# Priority for env file loading:
# 1. backend/.env.{APP_ENV} (e.g., .env.development, .env.production)
# 2. backend/.env
# 3. root/.env
def _find_env_file() -> Optional[Path]:
    """Find the appropriate .env file based on environment."""
    candidates = [
        _backend_dir / f".env.{_app_env}",  # .env.development or .env.production
        _backend_dir / ".env",               # backend/.env
        _root_dir / ".env",                  # root/.env
    ]
    for path in candidates:
        if path.exists():
            return path
    return None

_env_file = _find_env_file()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Security Incident Triage Agent"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Frontend CORS
    frontend_url: str = "http://localhost:3000"

    # Google Cloud / Vertex AI
    google_cloud_project: Optional[str] = None
    google_cloud_location: str = "us-central1"
    vertex_ai_location: str = "global"  # For Gemini models (gemini-3-pro-preview is global-only)
    vertex_ai_model: str = "gemini-3-pro-preview"
    vertex_embedding_model: str = "text-embedding-004"

    # Database (Neon PostgreSQL with pgvector)
    neon_database_url: Optional[str] = None

    # Redis (Upstash)
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None

    # Feature flags
    use_stub_llm: bool = True  # Use stub responses when LLM keys are missing
    enable_tracing: bool = True

    model_config = SettingsConfigDict(
        env_file=str(_env_file) if _env_file else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars not defined in Settings
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    if _env_file:
        print(f"[config] Loaded settings from: {_env_file}")
    else:
        print("[config] No .env file found, using environment variables only")
    return settings


def is_llm_available() -> bool:
    """Check if LLM credentials are configured."""
    settings = get_settings()
    return settings.google_cloud_project is not None and not settings.use_stub_llm


def is_db_available() -> bool:
    """Check if database is configured."""
    settings = get_settings()
    return settings.neon_database_url is not None


def is_redis_available() -> bool:
    """Check if Redis is configured."""
    settings = get_settings()
    return settings.upstash_redis_rest_url is not None
