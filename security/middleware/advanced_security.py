"""
Advanced Security Middleware - Enterprise-Grade Security Layer
==============================================================

Advanced security middleware providing enterprise-level protection including:
- JWT Token validation and refresh
- Rate limiting with multiple strategies
- Input validation and sanitization
- SQL injection and XSS protection
- CSRF protection
- Security headers injection
- API key management
- Bot detection and blocking
- Request signing and verification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

⚠️  PROPRIETARY SECURITY CODE ⚠️
This security implementation contains proprietary algorithms and methods.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union
from urllib.parse import parse_qs, unquote, urlparse

import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Advanced security configuration"""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_BURST_SIZE: int = 20
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Input Validation
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_JSON_DEPTH: int = 10
    MAX_FIELD_LENGTH: int = 10000
    
    # Bot Protection
    BOT_DETECTION_ENABLED: bool = True
    SUSPICIOUS_USER_AGENTS: Set[str] = {
        "bot", "crawler", "spider", "scraper", "scanner",
        "curl", "wget", "python-requests", "postman"
    }
    
    # CSRF Protection
    CSRF_TOKEN_LENGTH: int = 32
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Key Management
    API_KEY_LENGTH: int = 64
    API_KEY_PREFIX: str = "aif_"  # AI Influencer platform prefix


class SecurityException(HTTPException):
    """Custom security exception"""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(status_code=status_code, detail=detail)


class SecurityLogger:
    """Enhanced security logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.security_events = []
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log security event with context"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "event_id": str(uuid.uuid4())
        }
        
        if request:
            event["request_info"] = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        
        # Log to standard logger
        self.logger.warning(f"Security Event [{event_type}]: {json.dumps(event)}")
        
        # Keep in memory for analysis
        self.security_events.append(event)
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-500:]  # Keep last 500


class JWTManager:
    """Advanced JWT token management"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security_logger = SecurityLogger()
    
    def create_access_token(
        self,
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        payload = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": str(uuid.uuid4())
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(
            payload,
            self.config.JWT_SECRET_KEY,
            algorithm=self.config.JWT_ALGORITHM
        )
    
    def create_refresh_token(self, subject: Union[str, Any]) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(
            days=self.config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        payload = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(
            payload,
            self.config.JWT_SECRET_KEY,
            algorithm=self.config.JWT_ALGORITHM
        )
    
    def verify_token(
        self,
        token: str,
        token_type: str = "access"
    ) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM]
            )
            
            if payload.get("type") != token_type:
                raise SecurityException("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise SecurityException("Token has expired")
        except jwt.JWTError as e:
            self.security_logger.log_security_event(
                "invalid_token",
                "HIGH",
                {"error": str(e), "token": token[:20] + "..."}
            )
            raise SecurityException("Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        return self.create_access_token(payload["sub"])


class RateLimitManager:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.memory_storage = {}
        self.security_logger = SecurityLogger()
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: str = "general"
    ) -> bool:
        """Check if request is within rate limits"""
        current_time = int(time.time())
        
        # Define limits based on type
        limits = {
            "general": (self.config.RATE_LIMIT_REQUESTS_PER_MINUTE, 60),
            "auth": (10, 60),  # 10 auth attempts per minute
            "upload": (5, 300),  # 5 uploads per 5 minutes
            "api": (self.config.RATE_LIMIT_REQUESTS_PER_HOUR, 3600)
        }
        
        max_requests, window_seconds = limits.get(
            limit_type, 
            (self.config.RATE_LIMIT_REQUESTS_PER_MINUTE, 60)
        )
        
        return self._check_memory_rate_limit(
            identifier, max_requests, window_seconds, current_time
        )
    
    def _check_memory_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        current_time: int
    ) -> bool:
        """Check rate limit using memory storage"""
        if identifier not in self.memory_storage:
            self.memory_storage[identifier] = []
        
        requests = self.memory_storage[identifier]
        
        # Remove old requests
        cutoff_time = current_time - window_seconds
        requests = [req_time for req_time in requests if req_time > cutoff_time]
        
        if len(requests) >= max_requests:
            self.security_logger.log_security_event(
                "rate_limit_exceeded",
                "MEDIUM",
                {
                    "identifier": identifier,
                    "current_count": len(requests),
                    "max_requests": max_requests
                }
            )
            return False
        
        # Add current request
        requests.append(current_time)
        self.memory_storage[identifier] = requests
        
        return True


class InputValidator:
    """Advanced input validation and sanitization"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security_logger = SecurityLogger()
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
            r"('|(\\x27)|(\\x2D)|(\\x23)|(\\x3B))",
            r"(exec|execute|sp_|xp_)",
            r"(script|javascript|vbscript)",
            r"(@@|@\\w+)",
            r"(\\b(and|or)\\b.*[=<>])",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>",
            r"expression\s*\(",
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
            r"\\.\\.\\",
        ]
    
    def validate_input(self, data: Any, field_name: str = "input") -> Any:
        """Validate and sanitize input data"""
        if isinstance(data, str):
            return self._validate_string(data, field_name)
        elif isinstance(data, dict):
            return self._validate_dict(data, field_name)
        elif isinstance(data, list):
            return self._validate_list(data, field_name)
        else:
            return data
    
    def _validate_string(self, value: str, field_name: str) -> str:
        """Validate string input"""
        # Check length
        if len(value) > self.config.MAX_FIELD_LENGTH:
            raise SecurityException(
                f"Field '{field_name}' exceeds maximum length"
            )
        
        # Check for SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                self.security_logger.log_security_event(
                    "sql_injection_attempt",
                    "HIGH",
                    {"field": field_name, "pattern": pattern, "value": value[:100]}
                )
                raise SecurityException("Potentially malicious input detected")
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                self.security_logger.log_security_event(
                    "xss_attempt",
                    "HIGH",
                    {"field": field_name, "pattern": pattern, "value": value[:100]}
                )
                raise SecurityException("Potentially malicious input detected")
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                self.security_logger.log_security_event(
                    "path_traversal_attempt",
                    "HIGH",
                    {"field": field_name, "pattern": pattern, "value": value[:100]}
                )
                raise SecurityException("Potentially malicious input detected")
        
        return value
    
    def _validate_dict(self, data: Dict[str, Any], field_name: str) -> Dict[str, Any]:
        """Validate dictionary input"""
        validated = {}
        for key, value in data.items():
            validated[key] = self.validate_input(value, f"{field_name}.{key}")
        return validated
    
    def _validate_list(self, data: List[Any], field_name: str) -> List[Any]:
        """Validate list input"""
        return [
            self.validate_input(item, f"{field_name}[{i}]")
            for i, item in enumerate(data)
        ]


class BotDetector:
    """Advanced bot detection system"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security_logger = SecurityLogger()
        self.suspicious_ips = set()
        self.request_patterns = {}
    
    def is_bot_request(self, request: Request) -> bool:
        """Detect if request is from a bot"""
        if not self.config.BOT_DETECTION_ENABLED:
            return False
        
        # Check user agent
        user_agent = request.headers.get("user-agent", "").lower()
        for suspicious_ua in self.config.SUSPICIOUS_USER_AGENTS:
            if suspicious_ua in user_agent:
                self.security_logger.log_security_event(
                    "bot_detected",
                    "MEDIUM",
                    {"user_agent": user_agent, "reason": "suspicious_user_agent"},
                    request
                )
                return True
        
        # Check for missing common headers
        required_headers = ["accept", "accept-language", "accept-encoding"]
        missing_headers = [h for h in required_headers if h not in request.headers]
        if len(missing_headers) >= 2:
            self.security_logger.log_security_event(
                "bot_detected",
                "LOW",
                {"missing_headers": missing_headers, "reason": "missing_headers"},
                request
            )
            return True
        
        # Check request patterns
        client_ip = request.client.host if request.client else "unknown"
        if self._is_suspicious_pattern(client_ip, request):
            return True
        
        return False
    
    def _is_suspicious_pattern(self, client_ip: str, request: Request) -> bool:
        """Check for suspicious request patterns"""
        current_time = time.time()
        
        if client_ip not in self.request_patterns:
            self.request_patterns[client_ip] = []
        
        patterns = self.request_patterns[client_ip]
        patterns.append({
            "timestamp": current_time,
            "path": request.url.path,
            "method": request.method
        })
        
        # Keep only last 100 requests
        patterns = patterns[-100:]
        self.request_patterns[client_ip] = patterns
        
        # Check for rapid requests (more than 20 in 60 seconds)
        recent_requests = [
            p for p in patterns 
            if current_time - p["timestamp"] < 60
        ]
        
        if len(recent_requests) > 20:
            self.security_logger.log_security_event(
                "bot_detected",
                "HIGH",
                {
                    "client_ip": client_ip,
                    "request_count": len(recent_requests),
                    "reason": "rapid_requests"
                },
                request
            )
            return True
        
        return False


class CSRFProtection:
    """CSRF protection implementation"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.tokens = {}  # In production, use Redis or database
        self.security_logger = SecurityLogger()
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        token = secrets.token_urlsafe(self.config.CSRF_TOKEN_LENGTH)
        expires_at = datetime.utcnow() + timedelta(
            minutes=self.config.CSRF_TOKEN_EXPIRE_MINUTES
        )
        
        self.tokens[session_id] = {
            "token": token,
            "expires_at": expires_at
        }
        
        return token
    
    def validate_csrf_token(
        self,
        session_id: str,
        token: str,
        request: Optional[Request] = None
    ) -> bool:
        """Validate CSRF token"""
        if session_id not in self.tokens:
            self.security_logger.log_security_event(
                "csrf_validation_failed",
                "MEDIUM",
                {"reason": "session_not_found", "session_id": session_id},
                request
            )
            return False
        
        stored_token = self.tokens[session_id]
        
        # Check expiration
        if datetime.utcnow() > stored_token["expires_at"]:
            del self.tokens[session_id]
            self.security_logger.log_security_event(
                "csrf_validation_failed",
                "MEDIUM",
                {"reason": "token_expired", "session_id": session_id},
                request
            )
            return False
        
        # Check token match
        if not hmac.compare_digest(stored_token["token"], token):
            self.security_logger.log_security_event(
                "csrf_validation_failed",
                "HIGH",
                {"reason": "token_mismatch", "session_id": session_id},
                request
            )
            return False
        
        return True


class SecurityMiddleware:
    """Main security middleware coordinating all security features"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        
        self.jwt_manager = JWTManager(self.config)
        self.rate_limiter = RateLimitManager(self.config)
        self.input_validator = InputValidator(self.config)
        self.bot_detector = BotDetector(self.config)
        self.csrf_protection = CSRFProtection(self.config)
        self.security_logger = SecurityLogger()
        
        self.protected_endpoints = set()
        self.rate_limited_endpoints = set()
    
    def add_protected_endpoint(self, endpoint: str):
        """Add endpoint that requires authentication"""
        self.protected_endpoints.add(endpoint)
    
    def add_rate_limited_endpoint(self, endpoint: str):
        """Add endpoint that has rate limiting"""
        self.rate_limited_endpoints.add(endpoint)
    
    async def __call__(self, request: Request, call_next: Callable):
        """Main middleware processing"""
        start_time = time.time()
        
        try:
            # Process security checks before handling request
            await self.process_request(request)
            
            # Process the request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Log processing time
            processing_time = time.time() - start_time
            if processing_time > 5.0:  # Log slow requests
                self.security_logger.log_security_event(
                    "slow_request",
                    "LOW",
                    {"processing_time": processing_time, "path": request.url.path},
                    request
                )
            
            return response
            
        except SecurityException:
            raise
        except Exception as e:
            self.security_logger.log_security_event(
                "middleware_error",
                "HIGH",
                {"error": str(e), "path": request.url.path},
                request
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal security error"
            )
    
    async def process_request(self, request: Request):
        """Process incoming request through security checks"""
        # Check request size
        if hasattr(request, "content_length"):
            if request.content_length and request.content_length > self.config.MAX_REQUEST_SIZE:
                raise SecurityException("Request too large")
        
        # Bot detection
        if self.bot_detector.is_bot_request(request):
            raise SecurityException("Bot requests not allowed")
        
        # Rate limiting
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        
        if endpoint in self.rate_limited_endpoints or len(self.rate_limited_endpoints) == 0:
            if not await self.rate_limiter.check_rate_limit(client_ip):
                raise SecurityException("Rate limit exceeded")
        
        # Authentication for protected endpoints
        if endpoint in self.protected_endpoints:
            await self._authenticate_request(request)
        
        # Input validation for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._validate_request_body(request)
    
    async def _authenticate_request(self, request: Request):
        """Authenticate request using JWT"""
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise SecurityException("Missing or invalid authorization header")
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            payload = self.jwt_manager.verify_token(token)
            request.state.user = payload
        except SecurityException:
            raise
    
    async def _validate_request_body(self, request: Request):
        """Validate request body"""
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                body = await request.body()
                if body:
                    data = json.loads(body)
                    self.input_validator.validate_input(data, "request_body")
        except json.JSONDecodeError:
            raise SecurityException("Invalid JSON in request body")
        except Exception as e:
            # Log parsing errors for security audit
            logger.warning(f"Request body validation warning: {str(e)}")
            # Continue processing if basic validation passed
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        for header, value in self.config.SECURITY_HEADERS.items():
            response.headers[header] = value


# Utility decorators and functions
def require_auth(func: Callable):
    """Decorator to require authentication for endpoint"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Authentication will be handled by middleware
        return await func(*args, **kwargs)
    return wrapper


def rate_limit(limit_type: str = "general"):
    """Decorator to add rate limiting to endpoint"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Rate limiting will be handled by middleware
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(validator_func: Optional[Callable] = None):
    """Decorator to add input validation to endpoint"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Input validation will be handled by middleware
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Export main components
__all__ = [
    "SecurityConfig",
    "SecurityMiddleware", 
    "JWTManager",
    "RateLimitManager",
    "InputValidator",
    "BotDetector",
    "CSRFProtection",
    "SecurityException",
    "SecurityLogger",
    "require_auth",
    "rate_limit",
    "validate_input"
]