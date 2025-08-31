"""Application settings loaded from environment with sane defaults.
All names and comments are in English to ensure professional consistency.
"""

from functools import lru_cache

from pydantic import BaseSettings, Field, AnyUrl
from typing import List, Optional


class Settings(BaseSettings):
    app_name: str = Field("IA Influencer Agent Backend", alias="APP_NAME")
    environment: str = Field("development", alias="ENVIRONMENT")
    debug: bool = Field(False, alias="DEBUG")
    api_root_prefix: str = Field("/api", alias="API_ROOT_PREFIX")
    api_v1_prefix: str = Field("/v1", alias="API_V1_PREFIX")

    # Security
    secret_key: str = Field("change-this-secret", alias="SECRET_KEY")
    api_keys: List[str] = Field(default_factory=list, alias="API_KEYS")
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_ORIGINS")

    # Database
    database_url: AnyUrl = Field("postgresql+psycopg2://user:pass@localhost:5432/ia_influencer", alias="DATABASE_URL")
    redis_url: AnyUrl = Field("redis://localhost:6379/0", alias="REDIS_URL")

    # Storage
    storage_bucket: Optional[str] = Field(None, alias="STORAGE_BUCKET")

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # cached instance


settings = get_settings()
