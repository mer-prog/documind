import secrets
import warnings

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/documind"
    NEXTAUTH_SECRET: str = ""
    OPENAI_API_KEY: str | None = None
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    CHAT_MODEL: str = "gpt-4o-mini"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RRF_K: int = 60
    CONVERSATION_MEMORY_LIMIT: int = 5
    MAX_UPLOAD_SIZE_MB: int = 20


settings = Settings()

if not settings.NEXTAUTH_SECRET or settings.NEXTAUTH_SECRET in ("change-me", ""):
    warnings.warn(
        "NEXTAUTH_SECRET is not set. A random secret has been generated for this session. "
        "Set NEXTAUTH_SECRET in your .env file for production use.",
        stacklevel=2,
    )
    settings.NEXTAUTH_SECRET = secrets.token_urlsafe(32)
