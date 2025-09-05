"""
API Package for Ainflue Platform
===============================

This package contains all API-related modules including:
- FastAPI application configuration (asgi.py)
- Main application entry point (main.py)
- API route definitions (api.py)
- Route modules (routes/)
- Specialized endpoints (validation_endpoints.py, enterprise_monetization_api.py, intelligent_alerts.py)

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Import main components with error handling
try:
    from .api import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import api_router: {e}")
    API_ROUTER_AVAILABLE = False

try:
    from .asgi import app
    ASGI_APP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ASGI app: {e}")
    ASGI_APP_AVAILABLE = False

# Export main components
__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "API_ROUTER_AVAILABLE",
    "ASGI_APP_AVAILABLE"
]

# Conditionally add to exports if available
if API_ROUTER_AVAILABLE:
    __all__.append("api_router")
    
if ASGI_APP_AVAILABLE:
    __all__.append("app")