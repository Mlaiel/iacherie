"""
Database Configuration
Database connection and settings configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database-specific settings"""
    
    # Database Settings
    database_url: Optional[str] = None
    postgres_user: str = "ainflue"
    postgres_password: str = "ainflue_secure"
    postgres_db: str = "ainflue_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Connection Pool Settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # Database Options
    db_echo: bool = False
    db_autocommit: bool = False
    db_autoflush: bool = True
    
    @property
    def database_dsn(self) -> str:
        """Get database connection string"""
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        extra = "allow"


# Database configuration functions
def get_database_url() -> str:
    """Get the database URL for connections"""
    settings = DatabaseSettings()
    return settings.database_dsn


def get_database_config() -> dict:
    """Get database configuration as dictionary"""
    settings = DatabaseSettings()
    return {
        "url": settings.database_dsn,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
        "pool_recycle": settings.db_pool_recycle,
        "echo": settings.db_echo,
        "autocommit": settings.db_autocommit,
        "autoflush": settings.db_autoflush,
    }


# Database settings instance
db_settings = DatabaseSettings()

__all__ = [
    "DatabaseSettings", 
    "db_settings", 
    "get_database_url", 
    "get_database_config"
]