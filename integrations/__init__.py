"""Integrations Module
===================

Complete integration system for external services and platforms.
Supports AI services, cloud providers, payment gateways, social media platforms, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import core integration management
try:
    from .integration_manager import integration_manager
except ImportError:
    integration_manager = None

# Import submodules to make them accessible
from . import ai_services
from . import cloud_providers  
from . import payment_gateways
from . import platforms
from . import social_media
from . import third_party
from . import communication

__all__ = [
    "integration_manager",
    "ai_services",
    "cloud_providers", 
    "payment_gateways",
    "platforms",
    "social_media", 
    "third_party",
    "communication"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
