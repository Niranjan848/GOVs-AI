"""
GOVs-AI Configuration Module
Centralized settings management via Pydantic BaseSettings.
Loads from environment variables with sensible defaults for hackathon MVP.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "GOVs-AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Authentication ───────────────────────────────────────────
    JWT_SECRET: str = "govsai-hackathon-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./govsai.db"

    # ── Gemini AI ────────────────────────────────────────────────
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    USE_MOCK_LLM: bool = False  # Auto-set to True if no API key

    # ── FAISS Vector Store ───────────────────────────────────────
    FAISS_INDEX_PATH: str = "./faiss_index"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    RETRIEVER_TOP_K: int = 5

    # ── File Upload ──────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def should_use_mock(self) -> bool:
        """Determine if we should use mock LLM (no API key provided)."""
        return self.USE_MOCK_LLM or not self.GEMINI_API_KEY


settings = Settings()

# Auto-create directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
