"""
Configuration Management for IA Chérie Platform
Centralized settings and environment variable management
"""
import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """
        Application settings"""
    
    # Basic settings
    app_name: str = "IA Chérie Platform"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings (placeholders)
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(2000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    
    # Security settings
    secret_key: str = Field("dev-secret-key", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = [".env", ".env.local", ".env.openai"]

        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

# Export for use in other modules
__all__ = ["settings", "Settings"]