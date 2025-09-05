"""Infrastructure API Module - IA-Influencer-Agent Platform
===========================================================
API routing and management functionality

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module handles API routing and management:
- Router configuration and management
- API endpoint handling
- Request/response processing
"""

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Import API modules with error handling
import logging

logger = logging.getLogger(__name__)

# Import router module with graceful error handling
try:
    from .router import *
except ImportError as e:
    logger.warning(f"Failed to import router: {e}")

__all__ = [
    # Router functionality
    "APIRouter",
    "RouteManager",
    "EndpointHandler",
    "RequestProcessor",
    "ResponseFormatter"
]