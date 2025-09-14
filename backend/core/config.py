"""Backend Core Configuration

Minimal configuration to support backend imports.
Author: Fahed Mlaiel <mlaiel@live.de>
"""

from typing import Dict, Any
import os


class BackendConfig:
    """Backend configuration settings"""
    
    def __init__(self) -> None:
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///ainflue.db')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'
        
    def get_settings(self) -> Dict[str, Any]:
        """Get configuration settings"""
        return {
            'database_url': self.database_url,
            'redis_url': self.redis_url,
            'environment': self.environment,
            'debug': self.debug
        }


def get_backend_settings() -> Dict[str, Any]:
    """Get backend settings"""
    config = BackendConfig()
    return config.get_settings()


# Global config instance
backend_config = BackendConfig()