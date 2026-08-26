from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_key: str = "dev-key"
    jwt_secret: str = "change-me"
    database_url: str = "sqlite+aiosqlite:///./enterprise_ai.db"
    redis_url: str = "redis://localhost:6379/0"
    vector_db_url: str = "http://localhost:6333"
    vector_backend: str = "local"
    llm_provider: str = "deterministic"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    github_token: str | None = None
    github_webhook_secret: str = "dev-webhook-secret"
    github_write_enabled: bool = False
    n8n_webhook_url: str | None = None
    langsmith_api_key: str | None = None
    langsmith_tracing: bool = False
    max_workflow_steps: int = 24
    max_solution_retries: int = 2
    rerank_enabled: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
