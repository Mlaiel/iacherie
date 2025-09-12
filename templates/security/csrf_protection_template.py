"""{{csrf_name}} CSRF Protection Template for Ainflue Platform
{{csrf_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Security Expert Role: Enterprise CSRF protection with advanced security features
"""

import logging
import secrets
import hashlib
import hmac
import time
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import base64
import json

from fastapi import Request, Response, HTTPException, Depends
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis

from core.config import get_settings
from core.database import get_session
from utils.exceptions import SecurityError

logger = logging.getLogger(__name__)
settings = get_settings()


class CSRFError(SecurityError):
    """CSRF protection error"""
    pass


class CSRFTokenExpiredError(CSRFError):
    """CSRF token expired error"""
    pass


class CSRFTokenInvalidError(CSRFError):
    """CSRF token invalid error"""
    pass


class CSRFConfig:
    """CSRF protection configuration"""
    
    def __init__(
        self,
        secret_key: str,
        token_lifetime: int = 3600,  # 1 hour
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        form_field_name: str = "csrf_token",
        secure_cookie: bool = True,
        same_site: str = "strict",
        domain: Optional[str] = None,
        exempt_methods: List[str] = None,
        exempt_paths: List[str] = None,
        double_submit: bool = True,
        redis_client: Optional[redis.Redis] = None
    ):
        self.secret_key = secret_key
        self.token_lifetime = token_lifetime
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.form_field_name = form_field_name
        self.secure_cookie = secure_cookie
        self.same_site = same_site
        self.domain = domain
        self.exempt_methods = exempt_methods or ["GET", "HEAD", "OPTIONS", "TRACE"]
        self.exempt_paths = exempt_paths or []
        self.double_submit = double_submit
        self.redis_client = redis_client


class CSRFToken:
    """CSRF token management"""
    
    def __init__(self, config: CSRFConfig):
        self.config = config
        self._redis = config.redis_client
    
    def generate_token(
        self,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Generate a secure CSRF token
        
        Creates a token with the following structure:
        - Random value (32 bytes)
        - Timestamp (8 bytes)
        - User ID (16 bytes, optional)
        - Session ID hash (32 bytes, optional)
        - HMAC signature (32 bytes)
        """
        # Generate random value
        random_value = secrets.token_bytes(32)
        
        # Current timestamp
        timestamp = int(time.time()).to_bytes(8, byteorder='big')
        
        # User ID (if provided)
        user_bytes = user_id.bytes if user_id else b'\x00' * 16
        
        # Session ID hash (if provided)
        session_hash = hashlib.sha256(session_id.encode()).digest() if session_id else b'\x00' * 32
        
        # IP address hash (if provided)
        ip_hash = hashlib.sha256(ip_address.encode()).digest()[:16] if ip_address else b'\x00' * 16
        
        # Combine all data
        token_data = random_value + timestamp + user_bytes + session_hash + ip_hash
        
        # Generate HMAC signature
        signature = hmac.new(
            self.config.secret_key.encode(),
            token_data,
            hashlib.sha256
        ).digest()
        
        # Combine token data with signature
        full_token = token_data + signature
        
        # Base64 encode for safe transport
        token_string = base64.urlsafe_b64encode(full_token).decode('ascii')
        
        # Store in Redis if available (for additional validation)
        if self._redis:
            try:
                redis_key = f"csrf_token:{hashlib.sha256(token_string.encode()).hexdigest()}"
                token_info = {
                    'user_id': str(user_id) if user_id else None,
                    'session_id': session_id,
                    'ip_address': ip_address,
                    'created_at': time.time(),
                    'used': False
                }
                self._redis.setex(
                    redis_key,
                    self.config.token_lifetime,
                    json.dumps(token_info)
                )
            except Exception as e:
                logger.warning(f"Failed to store CSRF token in Redis: {e}")
        
        logger.debug(f"Generated CSRF token for user {user_id}")
        return token_string
    
    def validate_token(
        self,
        token: str,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        mark_used: bool = True
    ) -> bool:
        """Validate CSRF token"""
        try:
            # Decode base64
            try:
                token_bytes = base64.urlsafe_b64decode(token.encode('ascii'))
            except Exception:
                raise CSRFTokenInvalidError("Invalid token encoding")
            
            # Check minimum length
            if len(token_bytes) < 88:  # 32+8+16+32+16+32 = 136 bytes minimum
                raise CSRFTokenInvalidError("Token too short")
            
            # Extract components
            random_value = token_bytes[:32]
            timestamp_bytes = token_bytes[32:40]
            user_bytes = token_bytes[40:56]
            session_hash = token_bytes[56:88]
            ip_hash = token_bytes[88:104]
            signature = token_bytes[104:136]
            
            # Verify HMAC signature
            token_data = token_bytes[:104]
            expected_signature = hmac.new(
                self.config.secret_key.encode(),
                token_data,
                hashlib.sha256
            ).digest()
            
            if not hmac.compare_digest(signature, expected_signature):
                raise CSRFTokenInvalidError("Invalid token signature")
            
            # Check timestamp
            timestamp = int.from_bytes(timestamp_bytes, byteorder='big')
            current_time = int(time.time())
            
            if current_time - timestamp > self.config.token_lifetime:
                raise CSRFTokenExpiredError("Token expired")
            
            # Validate user ID if provided
            if user_id:
                expected_user_bytes = user_id.bytes
                if user_bytes != expected_user_bytes:
                    raise CSRFTokenInvalidError("Token user mismatch")
            
            # Validate session ID if provided
            if session_id:
                expected_session_hash = hashlib.sha256(session_id.encode()).digest()
                if session_hash != expected_session_hash:
                    raise CSRFTokenInvalidError("Token session mismatch")
            
            # Validate IP address if provided
            if ip_address:
                expected_ip_hash = hashlib.sha256(ip_address.encode()).digest()[:16]
                if ip_hash != expected_ip_hash:
                    raise CSRFTokenInvalidError("Token IP mismatch")
            
            # Check Redis storage if available
            if self._redis:
                try:
                    redis_key = f"csrf_token:{hashlib.sha256(token.encode()).hexdigest()}"
                    stored_data = self._redis.get(redis_key)
                    
                    if stored_data:
                        token_info = json.loads(stored_data)
                        
                        # Check if already used (one-time use)
                        if token_info.get('used', False):
                            raise CSRFTokenInvalidError("Token already used")
                        
                        # Additional validation against stored data
                        if user_id and token_info.get('user_id') != str(user_id):
                            raise CSRFTokenInvalidError("Token user mismatch in storage")
                        
                        if session_id and token_info.get('session_id') != session_id:
                            raise CSRFTokenInvalidError("Token session mismatch in storage")
                        
                        if ip_address and token_info.get('ip_address') != ip_address:
                            raise CSRFTokenInvalidError("Token IP mismatch in storage")
                        
                        # Mark as used if requested
                        if mark_used:
                            token_info['used'] = True
                            token_info['used_at'] = time.time()
                            self._redis.setex(
                                redis_key,
                                self.config.token_lifetime,
                                json.dumps(token_info)
                            )
                    
                except Exception as e:
                    logger.warning(f"Redis validation failed: {e}")
                    # Continue with cryptographic validation only
            
            logger.debug(f"CSRF token validated successfully for user {user_id}")
            return True
            
        except CSRFError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating CSRF token: {e}")
            raise CSRFTokenInvalidError("Token validation failed")
    
    def invalidate_token(self, token: str) -> bool:
        """Invalidate a specific token"""
        if not self._redis:
            return False
        
        try:
            redis_key = f"csrf_token:{hashlib.sha256(token.encode()).hexdigest()}"
            return bool(self._redis.delete(redis_key))
        except Exception as e:
            logger.error(f"Failed to invalidate CSRF token: {e}")
            return False
    
    def invalidate_user_tokens(self, user_id: UUID) -> int:
        """Invalidate all tokens for a user"""
        if not self._redis:
            return 0
        
        try:
            pattern = f"csrf_token:*"
            invalidated = 0
            
            for key in self._redis.scan_iter(match=pattern):
                try:
                    token_data = self._redis.get(key)
                    if token_data:
                        token_info = json.loads(token_data)
                        if token_info.get('user_id') == str(user_id):
                            self._redis.delete(key)
                            invalidated += 1
                except Exception:
                    continue
            
            return invalidated
            
        except Exception as e:
            logger.error(f"Failed to invalidate user tokens: {e}")
            return 0


class CSRFProtection:
    """Main CSRF protection class"""
    
    def __init__(self, config: CSRFConfig):
        self.config = config
        self.token_manager = CSRFToken(config)
    
    def get_token(
        self,
        request: Request,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Get CSRF token for the current request"""
        ip_address = self._get_client_ip(request)
        
        return self.token_manager.generate_token(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address
        )
    
    def set_token_cookie(
        self,
        response: Response,
        token: str
    ) -> Response:
        """Set CSRF token as HTTP-only cookie"""
        response.set_cookie(
            key=self.config.cookie_name,
            value=token,
            max_age=self.config.token_lifetime,
            secure=self.config.secure_cookie,
            httponly=True,
            samesite=self.config.same_site,
            domain=self.config.domain
        )
        return response
    
    def validate_request(
        self,
        request: Request,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """Validate CSRF protection for request"""
        # Check if method is exempt
        if request.method in self.config.exempt_methods:
            return True
        
        # Check if path is exempt
        request_path = str(request.url.path)
        for exempt_path in self.config.exempt_paths:
            if request_path.startswith(exempt_path):
                return True
        
        # Get token from various sources
        token = self._extract_token(request)
        
        if not token:
            raise CSRFError("CSRF token missing")
        
        # Validate token
        ip_address = self._get_client_ip(request)
        
        return self.token_manager.validate_token(
            token=token,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address
        )
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request"""
        # Try header first
        token = request.headers.get(self.config.header_name)
        if token:
            return token
        
        # Try form data
        if hasattr(request, 'form'):
            try:
                form_data = request.form()
                token = form_data.get(self.config.form_field_name)
                if token:
                    return token
            except Exception:
                pass
        
        # Try JSON body
        if hasattr(request, 'json'):
            try:
                json_data = request.json()
                token = json_data.get(self.config.form_field_name)
                if token:
                    return token
            except Exception:
                pass
        
        # Try cookie (for double-submit pattern)
        if self.config.double_submit:
            token = request.cookies.get(self.config.cookie_name)
            if token:
                return token
        
        return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        # Check forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to client address
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware for FastAPI
    
    Automatically validates CSRF tokens for state-changing requests
    """
    
    def __init__(self, app, config: CSRFConfig):
        super().__init__(app)
        self.csrf = CSRFProtection(config)
        self.config = config
    
    async def dispatch(self, request: Request, call_next):
        """Process request with CSRF protection"""
        try:
            # Skip CSRF check for exempt methods and paths
            if (request.method in self.config.exempt_methods or
                any(str(request.url.path).startswith(path) for path in self.config.exempt_paths)):
                response = await call_next(request)
                return response
            
            # Get user context (implement based on your auth system)
            user_id, session_id = await self._get_user_context(request)
            
            # Validate CSRF token
            try:
                self.csrf.validate_request(request, user_id, session_id)
            except CSRFError as e:
                logger.warning(f"CSRF validation failed: {e}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "CSRF validation failed",
                        "message": str(e),
                        "code": "CSRF_ERROR"
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add CSRF token to response for GET requests
            if request.method == "GET":
                token = self.csrf.get_token(request, user_id, session_id)
                response = self.csrf.set_token_cookie(response, token)
                # Also add to response headers for JS access
                response.headers[self.config.header_name] = token
            
            return response
            
        except Exception as e:
            logger.error(f"CSRF middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "Request processing failed"
                }
            )
    
    async def _get_user_context(self, request: Request) -> tuple:
        """Get user and session context from request
        
        This should be implemented based on your authentication system
        """
        # Example implementation - replace with your auth logic
        user_id = None
        session_id = None
        
        # Try to get from JWT token, session, etc.
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Extract user info from JWT or other auth mechanism
            pass
        
        # Try to get session ID from cookie
        session_id = request.cookies.get("session_id")
        
        return user_id, session_id


# FastAPI dependencies

def get_csrf_config() -> CSRFConfig:
    """Get CSRF configuration from settings"""
    return CSRFConfig(
        secret_key=settings.SECRET_KEY,
        token_lifetime=getattr(settings, 'CSRF_TOKEN_LIFETIME', 3600),
        secure_cookie=getattr(settings, 'CSRF_SECURE_COOKIE', True),
        same_site=getattr(settings, 'CSRF_SAME_SITE', 'strict'),
        domain=getattr(settings, 'CSRF_DOMAIN', None),
        exempt_paths=getattr(settings, 'CSRF_EXEMPT_PATHS', ['/api/health', '/api/metrics']),
        redis_client=None  # Initialize Redis client here if needed
    )


def get_csrf_protection(config: CSRFConfig = Depends(get_csrf_config)) -> CSRFProtection:
    """Get CSRF protection instance"""
    return CSRFProtection(config)


def require_csrf_token(
    request: Request,
    csrf: CSRFProtection = Depends(get_csrf_protection),
    user_id: Optional[UUID] = None
):
    """FastAPI dependency to require CSRF token"""
    try:
        csrf.validate_request(request, user_id)
    except CSRFError as e:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "CSRF validation failed",
                "message": str(e),
                "code": "CSRF_ERROR"
            }
        )


class {{csrf_name}}CSRFProtection(CSRFProtection):
    """{{csrf_description}}
    
    Specialized CSRF protection for {{model_name}} with business-specific rules
    """
    
    def __init__(self, config: CSRFConfig):
        super().__init__(config)
    
    async def validate_business_context(
        self,
        request: Request,
        operation: str,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None
    ) -> bool:
        """Validate business-specific CSRF context"""
        # Additional business logic validation
        
        # Example: Check if user has permission for this operation
        if operation in ['delete', 'modify'] and not user_id:
            raise CSRFError("Authentication required for this operation")
        
        # Example: Check resource ownership for sensitive operations
        if resource_id and operation in ['delete', 'transfer']:
            # Implement ownership check
            pass
        
        # Example: Rate limiting for sensitive operations
        if operation in ['bulk_delete', 'bulk_modify']:
            # Implement rate limiting
            pass
        
        return True
    
    def generate_operation_token(
        self,
        request: Request,
        operation: str,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None
    ) -> str:
        """Generate operation-specific CSRF token"""
        # Create operation-specific session ID
        operation_data = {
            'operation': operation,
            'resource_id': str(resource_id) if resource_id else None,
            'timestamp': time.time()
        }
        
        operation_session = hashlib.sha256(
            json.dumps(operation_data, sort_keys=True).encode()
        ).hexdigest()
        
        return self.get_token(request, user_id, operation_session)


# Utility functions

def create_csrf_middleware(app, config: Optional[CSRFConfig] = None) -> CSRFMiddleware:
    """Create and configure CSRF middleware"""
    if config is None:
        config = get_csrf_config()
    
    return CSRFMiddleware(app, config)


def setup_csrf_protection(app, redis_client: Optional[redis.Redis] = None):
    """Setup CSRF protection for FastAPI application"""
    config = get_csrf_config()
    if redis_client:
        config.redis_client = redis_client
    
    middleware = create_csrf_middleware(app, config)
    app.add_middleware(CSRFMiddleware, config=config)
    
    return middleware


# Export classes and functions
__all__ = [
    'CSRFError',
    'CSRFTokenExpiredError', 
    'CSRFTokenInvalidError',
    'CSRFConfig',
    'CSRFToken',
    'CSRFProtection',
    'CSRFMiddleware',
    '{{csrf_name}}CSRFProtection',
    'get_csrf_config',
    'get_csrf_protection',
    'require_csrf_token',
    'create_csrf_middleware',
    'setup_csrf_protection'
]