"""Infrastructure Security Module - IA-Influencer-Agent Platform
===============================================================
Security services and authentication for infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module provides security services:
- Authentication and authorization
- Certificate management
- Vault integration
- Security policies and compliance
"""

# Import security modules
try:
    from .auth import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from auth submodule
__all__ = []

try:
    from . import auth
    if hasattr(auth, '__all__'):
        __all__.extend(auth.__all__)
except ImportError:
    pass