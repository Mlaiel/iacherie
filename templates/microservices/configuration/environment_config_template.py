#!/usr/bin/env python3
"""
🌐 ENVIRONMENT CONFIG TEMPLATE - MULTI-ENVIRONMENT CONFIGURATION
================================================================

Environment-specific configuration management with validation,
hot reloading, and secure secret handling.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class EnvironmentConfig:
    """Environment configuration"""
    environment: Environment
    database_url: str
    redis_url: str
    api_base_url: str
    debug_mode: bool = False
    log_level: str = "INFO"
    secret_key: str = ""

class EnvironmentConfigTemplate:
    """
    🚀 ENTERPRISE ENVIRONMENT CONFIG TEMPLATE
    
    Multi-environment configuration with validation and hot reloading.
    """
    
    def __init__(self, env: Environment = Environment.DEVELOPMENT):
        """Initialize environment configuration"""
        self.environment = env
        self.config = self._load_config()
    
    def _load_config(self) -> EnvironmentConfig:
        """Load configuration for environment"""
        config_map = {
            Environment.DEVELOPMENT: EnvironmentConfig(
                environment=Environment.DEVELOPMENT,
                database_url=os.getenv("DEV_DATABASE_URL", "postgresql://dev:dev@localhost:5432/dev_db"),
                redis_url=os.getenv("DEV_REDIS_URL", "redis://localhost:6379/0"),
                api_base_url=os.getenv("DEV_API_URL", "http://localhost:8080"),
                debug_mode=True,
                log_level="DEBUG"
            ),
            Environment.PRODUCTION: EnvironmentConfig(
                environment=Environment.PRODUCTION,
                database_url=os.getenv("PROD_DATABASE_URL", ""),
                redis_url=os.getenv("PROD_REDIS_URL", ""),
                api_base_url=os.getenv("PROD_API_URL", ""),
                debug_mode=False,
                log_level="WARNING",
                secret_key=os.getenv("SECRET_KEY", "")
            )
        }
        
        return config_map.get(self.environment, config_map[Environment.DEVELOPMENT])
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_fields = ["database_url", "redis_url", "api_base_url"]
        
        for field in required_fields:
            if not getattr(self.config, field):
                return False
        
        if self.environment == Environment.PRODUCTION and not self.config.secret_key:
            return False
        
        return True
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            "environment": self.config.environment.value,
            "database_url": self.config.database_url,
            "redis_url": self.config.redis_url,
            "api_base_url": self.config.api_base_url,
            "debug_mode": self.config.debug_mode,
            "log_level": self.config.log_level
        }