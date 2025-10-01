#!/usr/bin/env python3
"""
⚙️ Protection Configuration Module
==================================

Configuration settings for protection layer.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Configuration Module
"""

from typing import Dict, Any, Optional
import os
from dataclasses import dataclass

@dataclass
class ProtectionConfig:
    """Protection system configuration."""
    
    # API Configuration
    api_key: Optional[str] = None
    api_url: str = "https://api.protection.local"
    api_timeout: int = 30
    
    # Security Configuration
    encryption_key: Optional[str] = None
    hash_algorithm: str = "sha256"
    
    # Database Configuration
    database_url: Optional[str] = None
    database_timeout: int = 30
    
    # Cache Configuration
    cache_ttl: int = 3600
    cache_prefix: str = "protection"
    
    # Notification Configuration
    notifications_enabled: bool = True
    email_enabled: bool = True
    webhook_enabled: bool = True

# Default configuration instance
default_config = ProtectionConfig()

def get_config() -> ProtectionConfig:
    """Get protection configuration."""
    return default_config

def load_config_from_env() -> ProtectionConfig:
    """Load configuration from environment variables."""
    config = ProtectionConfig()
    
    # Load from environment variables
    config.api_key = os.getenv("PROTECTION_API_KEY")
    config.api_url = os.getenv("PROTECTION_API_URL", config.api_url)
    config.encryption_key = os.getenv("PROTECTION_ENCRYPTION_KEY")
    config.database_url = os.getenv("PROTECTION_DATABASE_URL")
    
    return config

# Configuration constants
PROTECTION_VERSION = "1.0.0"
PROTECTION_NAME = "IA Chéries Protection System"
PROTECTION_AUTHOR = "Fahed Mlaiel <mlaiel@live.de>"

# Export configuration
__all__ = [
    "ProtectionConfig",
    "default_config", 
    "get_config",
    "load_config_from_env",
    "PROTECTION_VERSION",
    "PROTECTION_NAME", 
    "PROTECTION_AUTHOR"
]