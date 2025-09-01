"""Ainflue Platform Configuration
Main configuration module that consolidates settings from various sources.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Optional, List
from dataclasses import dataclass

try:
    # Try to import from simple_config for comprehensive settings
    from simple_config import Settings as SimpleConfigSettings
    SIMPLE_CONFIG_AVAILABLE = True
except ImportError:
    SIMPLE_CONFIG_AVAILABLE = False

try:
    # Try to import from core config for basic settings
    from core.config import Settings as CoreSettings, get_settings as get_core_settings
    CORE_CONFIG_AVAILABLE = True
except ImportError:
    CORE_CONFIG_AVAILABLE = False


@dataclass
class AppConfig:
    """Application configuration settings"""
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    workers: int = int(os.getenv("WORKERS", "1"))


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_user: str = os.getenv("POSTGRES_USER", "ainflue")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "password")
    postgres_db: str = os.getenv("POSTGRES_DB", "ainflue")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE", "3600"))
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "dev-encryption-key-change-in-production")


@dataclass
class CORSConfig:
    """CORS configuration settings"""
    origins: List[str] = None
    methods: List[str] = None
    
    def __post_init__(self):
        if self.origins is None:
            origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
            self.origins = [origin.strip() for origin in origins_str.split(",")]
        
        if self.methods is None:
            methods_str = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS")
            self.methods = [method.strip() for method in methods_str.split(",")]


@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "text")  # text or json
    
    def get_log_level(self) -> int:
        """Get logging level as integer"""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(self.level.upper(), logging.INFO)


class Settings:
    """Unified settings class that consolidates configuration from multiple sources"""
    
    def __init__(self):
        # Initialize all configuration sections
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.cors = CORSConfig()
        self.logging = LoggingConfig()
        
        # Try to load comprehensive settings from simple_config
        if SIMPLE_CONFIG_AVAILABLE:
            try:
                simple_settings = SimpleConfigSettings()
                # Use simple_config settings but keep our structure
                if hasattr(simple_settings, 'app'):
                    self.app = simple_settings.app
                if hasattr(simple_settings, 'database'):
                    self.database = simple_settings.database
                if hasattr(simple_settings, 'security'):
                    self.security = simple_settings.security
                print("✓ Loaded comprehensive settings from simple_config")
            except Exception as e:
                print(f"⚠️  Could not load simple_config settings: {e}")
        
        # Try to load core settings as backup
        elif CORE_CONFIG_AVAILABLE:
            try:
                core_settings = get_core_settings()
                # Map core settings to our structure
                self._map_core_settings(core_settings)
                print("✓ Loaded settings from core.config")
            except Exception as e:
                print(f"⚠️  Could not load core settings: {e}")
        
        # Settings are now initialized with environment variables via dataclasses
        print(f"✓ Unified configuration loaded for environment: {self.app.environment}")
    
    def _map_core_settings(self, core_settings):
        """Map core settings to our unified structure"""
        # Update app settings from core
        if hasattr(core_settings, 'HOST'):
            self.app.host = core_settings.HOST
        if hasattr(core_settings, 'PORT'):
            self.app.port = core_settings.PORT
        if hasattr(core_settings, 'DEBUG'):
            self.app.debug = core_settings.DEBUG
        if hasattr(core_settings, 'ENVIRONMENT'):
            self.app.environment = core_settings.ENVIRONMENT


# Global settings instance
settings = Settings()


def get_settings():
    """Get settings instance for dependency injection."""
    return settings


def setup_logging(config: LoggingConfig):
    """Setup logging configuration based on environment"""
    # Configure root logger
    logging.basicConfig(
        level=config.get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if config.format == 'text' 
               else '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/ainflue.log') if os.path.exists('logs') else None
        ]
    )
    
    # Set specific logger levels for production
    if config.level == "INFO":
        # Reduce noise from external libraries in production
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)