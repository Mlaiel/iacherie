"""
Guardian Middleware Package
Authentication and request processing middleware

Author: Fahed Mlaiel
Created: 2025-10-14

Note: Imports are lazy-loaded to avoid circular dependencies.
Use: from middleware.auth_middleware import get_current_user
"""

__all__ = [
    'auth_middleware',
]

__version__ = '1.0.0'
__author__ = 'Fahed Mlaiel'

# Lazy imports - middleware components are imported when needed
# This prevents circular imports and ensures sys.path is configured first


