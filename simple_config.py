"""Ainflue Platform Simple Configuration
Core configuration management for development and testing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class AppSettings(BaseSettings):
    """Application configuration settings"""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Configuration
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    
    class Config:
        env_file = ".env.development"
        env_file_encoding = "utf-8"
        extra = "ignore"  # This allows extra fields without error


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # PostgreSQL Primary Database
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT") 
    postgres_user: str = Field(default="ainflue", env="POSTGRES_USER")
    postgres_password: str = Field(default="password", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="ainflue_development", env="POSTGRES_DB")
    
    # Redis Cache Database
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    class Config:
        env_file = ".env.development"
        env_file_encoding = "utf-8"
        extra = "ignore"


class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    
    # JWT Configuration  
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire: int = Field(default=7200, env="JWT_ACCESS_TOKEN_EXPIRE")
    
    # Encryption
    encryption_key: str = Field(default="dev-encryption-key-change-in-production", env="ENCRYPTION_KEY")
    
    class Config:
        env_file = ".env.development"
        env_file_encoding = "utf-8"
        extra = "ignore"


class Settings:
    """Main settings aggregator"""
    
    def __init__(self):
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.security = SecuritySettings()


# Global settings instance
settings = Settings()


# Compatibility function for dependency injection
def get_settings():
    """Get settings instance for dependency injection."""
    return settings