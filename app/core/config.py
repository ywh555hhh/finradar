from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "FinRadar"
    version: str = "0.1.0"
    debug: bool = False

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/finradar"
    redis_url: str = "redis://localhost:6380/0"

    qdrant_url: str = "http://localhost:6335"
    qdrant_collection: str = "finradar_docs"
    qdrant_api_key: str = ""

    sec_user_agent: str = "FinRadar contact@finradar.ai"
    alpha_vantage_key: str = ""
    fred_api_key: str = ""
    news_api_key: str = ""

    crunchbase_api_key: str = ""

    daily_report_time: str = "09:00"
    weekly_scan_day: str = "MONDAY"
    scan_interval_hours: int = 24

    slack_webhook_url: str = ""
    email_sender: str = ""
    email_password: str = ""

    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_key: str = ""

    dspy_lm_model: str = "openai/gpt-4o-mini"
    dspy_lm_temperature: float = 0.0

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    prefect_api_url: str = "http://localhost:4200/api"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
