"""Infrastructure API Module - IA-Influencer-Agent Platform
==========================================================
API routing and management for infrastructure services

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module provides API routing and management:
- FastAPI router configuration
- Infrastructure endpoint management
- API middleware and authentication
"""

# Import router module (commented out due to syntax issues)
# try:
#     from .router import *
# except ImportError:
#     pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from router submodule
__all__ = []

# Router module temporarily disabled due to syntax issues
# try:
#     from . import router
#     if hasattr(router, '__all__'):
#         __all__.extend(router.__all__)
# except ImportError:
#     pass