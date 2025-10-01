"""
Artifacts Configs Module - Configuration Management
==================================================

Enterprise configuration management for IA Chéries platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Configuration exports
try:
    from .index import ConfigIndex
    from .technical_specifications import TechnicalSpecs
    from .platform_integrations import PlatformIntegrations
    
    __all__ = [
        "ConfigIndex",
        "TechnicalSpecs", 
        "PlatformIntegrations"
    ]
except ImportError as e:
    print(f"Artifacts configs: Some configurations not available: {e}")
    __all__ = []