"""
Mobile API Module - Ainflue Platform
Production-ready mobile backend services for content creators.

© 2025 Fahed Mlaiel. All rights reserved.
Lead Developer: Fahed Mlaiel (mlaiel@live.de)

This module provides specialized API endpoints and services for mobile applications,
optimized for touch interfaces, offline capabilities, and mobile-specific features.
"""

from .mobile_api_gateway import MobileAPIGateway
from .mobile_auth_service import MobileAuthService
from .mobile_session_manager import MobileSessionManager
from .mobile_repository import MobileRepository

__all__ = [
    "MobileAPIGateway",
    "MobileAuthService", 
    "MobileSessionManager",
    "MobileRepository"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"