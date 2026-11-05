from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Service Information
    APP_NAME: str = "hybrid-retrieval-memory-engine"
    APP_ENV: str = "production"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # PostgreSQL Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "enterprise_rag"
    POSTGRES_USER: str = "rag_admin"
    POSTGRES_PASSWORD: str = "rag_secure_password_2026"
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20

    # Redis (Working Memory & Cache)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_ENABLED: bool = True

    # Local Ollama / Private Model Gateway
    LLM_PROVIDER: str = "ollama"
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL_NAME: str = "llama3.2:3b"
    EMBEDDING_BASE_URL: str = "http://localhost:11434/v1"
    EMBEDDING_MODEL_NAME: str = "nomic-embed-text:v1.5"
    GUARD_MODEL_NAME: str = "llama-guard3:1b"
    LLM_API_KEY: str = "ollama_local_dummy"
    EMBEDDING_DIMENSION: int = 768

    # Observability & Tracing
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_SERVICE_NAME: str = "hybrid-retrieval-memory-engine"
    LANGFUSE_PUBLIC_KEY: Optional[str] = "pk-lf-891464a7-a345-4722-9704-e24940847219"
    LANGFUSE_SECRET_KEY: Optional[str] = "sk-lf-b78d9fbc-df19-40f8-b206-5eec1ab25414"
    LANGFUSE_HOST: Optional[str] = "http://localhost:3100"

    # RRF (Reciprocal Rank Fusion) parameters
    RRF_K_CONSTANT: int = 60
    DEFAULT_RETRIEVAL_TOP_K: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

