#!/usr/bin/env python3
"""
⚙️ Protection Configuration Package
===================================

Configuration modules for protection layer.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Configuration Package
"""

from .crawler_config import (
    CrawlerConfig,
    MarketIntelligenceCrawlerConfig,
    CollaborationCrawlerConfig,
    get_crawler_config
)

# Import from parent protection package config
try:
    import sys
    import os
    # Add parent directory to path for import
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from protection.config import (
        ProtectionConfig,
        get_config as get_protection_config,
        load_config_from_env,
        PROTECTION_VERSION,
        PROTECTION_NAME,
        PROTECTION_AUTHOR
    )
except ImportError:
    # Fallback definitions if import fails
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class ProtectionConfig:
        api_key: Optional[str] = None
        api_url: str = "https://api.protection.local"
    
    def get_protection_config():
        return ProtectionConfig()
    
    def load_config_from_env():
        return ProtectionConfig()
    
    PROTECTION_VERSION = "1.0.0"
    PROTECTION_NAME = "IA Chérie Protection System"
    PROTECTION_AUTHOR = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    # Crawler configurations
    "CrawlerConfig",
    "MarketIntelligenceCrawlerConfig", 
    "CollaborationCrawlerConfig",
    "get_crawler_config",
    
    # Main protection configurations
    "ProtectionConfig",
    "get_protection_config",
    "load_config_from_env",
    
    # Constants
    "PROTECTION_VERSION",
    "PROTECTION_NAME",
    "PROTECTION_AUTHOR"
]