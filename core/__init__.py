"""
Core module for Ainflue platform  
Contains essential utilities for logging, middleware, security, and authentication
"""

from .logging import logger, get_logger, set_log_level
from .middleware import (
    RequestLoggingMiddleware, CORSMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware,
    create_logging_middleware, create_cors_middleware, create_rate_limit_middleware, create_security_headers_middleware
)
from .security import (
    SecurityManager, TokenManager, SecurityValidator,
    create_security_manager, create_token_manager, create_security_validator
)
from .auth import (
    User, AuthenticationManager, AuthorizationManager,
    create_authentication_manager, create_authorization_manager, create_auth_system
)

__all__ = [
    # Logging
    "logger",
    "get_logger", 
    "set_log_level",
    
    # Middleware
    "RequestLoggingMiddleware",
    "CORSMiddleware", 
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    "create_logging_middleware",
    "create_cors_middleware",
    "create_rate_limit_middleware",
    "create_security_headers_middleware",
    
    # Security
    "SecurityManager",
    "TokenManager", 
    "SecurityValidator",
    "create_security_manager",
    "create_token_manager",
    "create_security_validator",
    
    # Authentication
    "User",
    "AuthenticationManager",
    "AuthorizationManager",
    "create_authentication_manager",
    "create_authorization_manager",
    "create_auth_system"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
