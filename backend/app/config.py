from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/documind"
    NEXTAUTH_SECRET: str = "change-me"
    OPENAI_API_KEY: str | None = None
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    CHAT_MODEL: str = "gpt-4o-mini"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RRF_K: int = 60
    CONVERSATION_MEMORY_LIMIT: int = 5


settings = Settings()
