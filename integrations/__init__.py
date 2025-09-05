"""Integrations Module
===================

Complete integration system for external services and platforms.
Supports AI services, cloud providers, payment gateways, social media platforms, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import submodules to make them accessible
from . import ai_services
from . import cloud_providers  
from . import payment_gateways
from . import platforms
from . import social_media
from . import spotify
from . import third_party

__all__ = [
    "ai_services",
    "cloud_providers", 
    "payment_gateways",
    "platforms",
    "social_media", 
    "spotify",
    "third_party"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
