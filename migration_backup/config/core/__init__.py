"""Ainflue Core Infrastructure Configuration
==========================================

Core infrastructure configurations for database, Redis, Celery,
security, API gateway, monitoring, performance, logging, and caching.

Enterprise-grade configuration management for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

# Core infrastructure imports
from .database import DatabaseConfiguration
from .redis import RedisConfiguration  
from .celery import CeleryConfiguration

logger = logging.getLogger(__name__)

class CoreConfigurationLevel(str, Enum):
    """Core configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class CoreConfigurationManager:
    """Core infrastructure configuration manager"""
    
    def __init__(self, level: CoreConfigurationLevel = CoreConfigurationLevel.ENTERPRISE):
        self.level = level
        self.configurations = {}
        self._initialize_core_configs()
    
    def _initialize_core_configs(self):
        """Initialize all core configurations"""
        self.configurations = {
            "database": DatabaseConfiguration(level=self.level),
            "redis": RedisConfiguration(level=self.level),
            "celery": CeleryConfiguration(level=self.level)
        }
        
        logger.info(f"🔧 Core configurations initialized - Level: {self.level.value}")
    
    def get_config(self, config_name: str) -> Optional[Any]:
        """Get specific core configuration"""
        return self.configurations.get(config_name)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all core configurations"""
        return self.configurations.copy()

# Global core configuration manager
core_config_manager = CoreConfigurationManager()

# Module exports
__all__ = [
    "DatabaseConfiguration",
    "RedisConfiguration", 
    "CeleryConfiguration",
    "CoreConfigurationManager",
    "CoreConfigurationLevel",
    "core_config_manager"
]

logger.info("🔧 Ainflue Core Infrastructure Configuration Module loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
