"""
Enterprise Configuration Management Module
==========================================

Ultra-advanced configuration management system for IA Chérie platform.
Provides enterprise-grade configuration loading, validation, hot-reload,
and environment-aware settings management.

⚠️  LEGAL NOTICE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution PROHIBITED without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE LICENSE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team training included

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Any, Dict, Optional, Union, List
import logging

# Core configuration management
from .config_manager import ConfigurationManager
from .environment_loader import EnvironmentLoader
from .validation_schema import ValidationSchema
from .hot_reload_manager import HotReloadManager
from .config_cache import ConfigurationCache
from .default_settings import DefaultSettings
from .override_manager import OverrideManager

# Enterprise configuration suite
from .config_manager import (
    BaseConfigurationManager,
    CreatorEconomyConfigManager,
    EnterpriseConfigurationSuite
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary"

# Configure logging
logger = logging.getLogger(__name__)

# Global configuration instance
_global_config: Optional[ConfigurationManager] = None

def get_config() -> ConfigurationManager:
    """
    Get the global configuration instance.
    
    Returns:
        ConfigurationManager: Global configuration instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigurationManager()
    return _global_config

def load_config(config_path: Optional[str] = None, 
                environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from files.
    
    Args:
        config_path: Path to configuration file
        environment: Environment name (development, staging, production)
        
    Returns:
        Dict containing loaded configuration
    """
    config_manager = get_config()
    return config_manager.load_configuration(config_path, environment)

def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a configuration setting.
    
    Args:
        key: Configuration key (supports dot notation)
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    config_manager = get_config()
    return config_manager.get(key, default)

def set_setting(key: str, value: Any) -> None:
    """
    Set a configuration setting.
    
    Args:
        key: Configuration key (supports dot notation)
        value: Value to set
    """
    config_manager = get_config()
    config_manager.set(key, value)

def reload_config() -> None:
    """Reload configuration from sources."""
    config_manager = get_config()
    config_manager.reload()

# Export all public components
__all__ = [
    # Core classes
    "ConfigurationManager",
    "EnvironmentLoader", 
    "ValidationSchema",
    "HotReloadManager",
    "ConfigurationCache",
    "DefaultSettings",
    "OverrideManager",
    
    # Enterprise suite
    "BaseConfigurationManager",
    "CreatorEconomyConfigManager", 
    "EnterpriseConfigurationSuite",
    
    # Utility functions
    "get_config",
    "load_config",
    "get_setting",
    "set_setting",
    "reload_config",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__copyright__",
    "__license__"
]

# Initialize configuration on import
try:
    _global_config = ConfigurationManager()
    logger.info("Configuration manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize configuration manager: {e}")
    _global_config = None