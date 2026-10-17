"""App settings loaded from .env (pydantic-settings)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # OpenAI (falls back to the OPENAI_API_KEY environment variable when unset)
    openai_api_key: str | None = None
    llm_model: str = "gpt-5.4-mini"
    embedding_model: str = "text-embedding-3-small"

    # Neo4j (see docker-compose.yml)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""

    # Ingestion
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    chunk_size: int = 1000
    chunk_overlap: int = 100

    # Agent
    max_retries: int = 2
    vector_top_k: int = 4

    # React dev server (dev) or nginx container (Docker)
    cors_origins: list[str] = ["http://localhost:5174", "http://localhost"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
