"""
Simple configuration module for Ainflue platform.

This provides a basic configuration when the complex config module is not available.
"""

import os
from typing import Dict, Any, Optional


class Settings:
    """Basic application settings"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'
        self.host = os.getenv('HOST', '127.0.0.1')
        self.port = int(os.getenv('PORT', 8000))
        
        # API settings
        self.api_title = "Ainflue AI Platform"
        self.api_description = "AI-Powered Content Protection & Monetization Platform"
        self.api_version = "1.0.0"
        
        # Auth settings
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 30
        self.allowed_user_roles = [
            "guest", "creator", "brand", "agency", "moderator", "admin"
        ]
        
        # Database settings
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./ainflue.db')
        
        # Redis settings
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""



    return settings


def get_config() -> Dict[str, Any]:
    """Get configuration as dictionary"""



    return {
        'environment': settings.environment,
        'debug': settings.debug,
        'host': settings.host,
        'port': settings.port,
        'api_title': settings.api_title,
        'api_description': settings.api_description,
        'api_version': settings.api_version,
        'access_token_expire_minutes': settings.access_token_expire_minutes,
        'refresh_token_expire_days': settings.refresh_token_expire_days,
        'allowed_user_roles': settings.allowed_user_roles,
        'database_url': settings.database_url,
        'redis_url': settings.redis_url
    }


# For compatibility with existing imports
API_CONFIG = get_config()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
ALLOWED_USER_ROLES = settings.allowed_user_roles


# Try to import the complex config module if available
try:
    from config import master_config as _master_config
    COMPLEX_CONFIG_AVAILABLE = True
except ImportError:
    COMPLEX_CONFIG_AVAILABLE = False


async def initialize_configuration() -> bool:
    """Initialize configuration system"""
    if COMPLEX_CONFIG_AVAILABLE:
        try:
            from config import initialize_configuration as init_complex
            return await init_complex()
        except Exception as e:
            print(f"Warning: Complex configuration failed, using simple config: {e}")
    
    # Simple configuration always succeeds
    print(" Simple configuration initialized")
    return True


__all__ = [
    'settings',
    'get_settings', 
    'get_config',
    'API_CONFIG',
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    'ALLOWED_USER_ROLES',
    'initialize_configuration'
]