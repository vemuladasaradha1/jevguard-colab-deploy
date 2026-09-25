
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    typesafe_api_key: str = ""
    groq_api_key: str = ""
    langsmith_api_key: str = ""
    langsmith_tracing: bool = False
    langsmith_project: str = "jevguard-production"

    jev_model: str = "jev-1.13.0"
    groq_model: str = "openai/gpt-oss-20b"

    tool_threshold: float = 0.70
    more_tool_threshold: float = 0.80
    max_tool_rounds: int = 2
    request_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
