"""Ainflue Platform Configuration
Main configuration module that consolidates settings from various sources.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
from typing import Optional
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
    """Application configuration settings"""    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


class Settings:
    """Unified settings class that consolidates configuration from multiple sources"""    
    def __init__(self):
        # Initialize app settings
        self.app = AppConfig()
        
        # Try to load comprehensive settings from simple_config
        if SIMPLE_CONFIG_AVAILABLE:
            try:
                simple_settings = SimpleConfigSettings()
                # Use simple_config settings but keep our app structure
                self.app = simple_settings.app
                self.database = simple_settings.database
                self.security = simple_settings.security
                print("✓ Loaded comprehensive settings from simple_config")
            except Exception as e:
                print(f"⚠️  Could not load simple_config settings: {e}")
                self._load_fallback_settings()
        
        # Try to load core settings as backup
        elif CORE_CONFIG_AVAILABLE:
            try:
                core_settings = get_core_settings()
                # Map core settings to our structure
                self._map_core_settings(core_settings)
                print("✓ Loaded settings from core.config")
            except Exception as e:
                print(f"⚠️  Could not load core settings: {e}")
                self._load_fallback_settings()
        
        else:
            self._load_fallback_settings()
    
    def _load_fallback_settings(self):
        """Load minimal fallback settings"""        print("⚠️  Using minimal fallback configuration")
        # Keep the app config we already have
        # Add minimal database config
        self.database = type('Database', (), {
            'postgres_url': os.getenv('DATABASE_URL', 'postgresql://localhost/ainflue'),
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        })()
        
        # Add minimal security config
        self.security = type('Security', (), {
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production'),
            'jwt_algorithm': 'HS256'
        })()
    
    def _map_core_settings(self, core_settings):
        """Map core settings to our unified structure"""        # Map core settings to our app structure
        self.app.host = getattr(core_settings, 'HOST', self.app.host)
        self.app.port = getattr(core_settings, 'PORT', self.app.port)
        self.app.debug = getattr(core_settings, 'DEBUG', self.app.debug)
        self.app.environment = getattr(core_settings, 'ENVIRONMENT', self.app.environment)
        
        # Create database settings from core
        self.database = type('Database', (), {
            'postgres_url': getattr(core_settings, 'DATABASE_URL', 'postgresql://localhost/ainflue'),
            'redis_url': f"redis://{getattr(core_settings, 'REDIS_HOST', 'localhost')}:{getattr(core_settings, 'REDIS_PORT', 6379)}/0"
        })()
        
        # Create security settings from core
        self.security = type('Security', (), {
            'jwt_secret_key': getattr(core_settings, 'SECRET_KEY', 'dev-secret-key-change-in-production'),
            'jwt_algorithm': 'HS256'
        })()


# Global settings instance
settings = Settings()


def get_settings():
    """Get settings instance for dependency injection."""    return settings