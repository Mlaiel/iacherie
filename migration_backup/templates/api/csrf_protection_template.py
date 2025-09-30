#!/usr/bin/env python3
"""
⚡ CSRF Protection Template - Enterprise Security
🏗️ Architecture: Ainflue Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
import hmac
import time
import base64
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from urllib.parse import urlparse

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + DevOps Engineer
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class CSRFProtectionLevel(str, Enum):
    """CSRF protection levels"""
    DISABLED = "disabled"
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


class CSRFTokenType(str, Enum):
    """CSRF token types"""
    HEADER_ONLY = "header_only"
    COOKIE_ONLY = "cookie_only"
    DOUBLE_SUBMIT = "double_submit"
    ENCRYPTED_TOKEN = "encrypted_token"
    SYNCHRONIZED_TOKEN = "synchronized_token"


class CSRFValidationMethod(str, Enum):
    """CSRF validation methods"""
    ORIGIN_CHECK = "origin_check"
    REFERER_CHECK = "referer_check"
    TOKEN_VALIDATION = "token_validation"
    COMBINED = "combined"


@dataclass
class CSRFConfig:
    """Enterprise CSRF protection configuration"""
    # Basic settings
    protection_level: CSRFProtectionLevel = CSRFProtectionLevel.STRICT
    token_type: CSRFTokenType = CSRFTokenType.DOUBLE_SUBMIT
    validation_method: CSRFValidationMethod = CSRFValidationMethod.COMBINED
    
    # Token settings
    token_length: int = 32
    token_lifetime: int = 3600  # 1 hour
    secret_key: Optional[str] = None
    
    # HTTP settings
    safe_methods: Set[str] = field(default_factory=lambda: {"GET", "HEAD", "OPTIONS", "TRACE"})
    csrf_header_name: str = "X-CSRF-Token"
    csrf_cookie_name: str = "csrf_token"
    csrf_param_name: str = "csrf_token"
    
    # Cookie settings
    cookie_secure: bool = True
    cookie_httponly: bool = False  # Must be False for JS access
    cookie_samesite: str = "strict"
    cookie_domain: Optional[str] = None
    cookie_path: str = "/"
    
    # Security settings
    require_https: bool = True
    trusted_origins: Set[str] = field(default_factory=set)
    exempted_paths: Set[str] = field(default_factory=set)
    exempted_user_agents: Set[str] = field(default_factory=set)
    
    # Advanced features
    enable_origin_validation: bool = True
    enable_referer_validation: bool = True
    enable_user_agent_validation: bool = True
    enable_rate_limiting: bool = True
    enable_audit_logging: bool = True
    
    # Rate limiting
    max_failures_per_ip: int = 10
    failure_window: int = 300  # 5 minutes
    
    # Monitoring
    enable_metrics: bool = True
    alert_on_attacks: bool = True


@dataclass
class CSRFToken:
    """CSRF token data"""
    value: str
    created_at: datetime
    expires_at: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    origin: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    @property
    def age_seconds(self) -> int:
        return int((datetime.utcnow() - self.created_at).total_seconds())


@dataclass
class CSRFMetrics:
    """CSRF protection metrics"""
    total_requests: int = 0
    protected_requests: int = 0
    blocked_requests: int = 0
    token_generations: int = 0
    validation_failures: int = 0
    origin_failures: int = 0
    referer_failures: int = 0
    token_failures: int = 0
    rate_limit_hits: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.protected_requests == 0:
            return 0.0
        return (self.protected_requests - self.blocked_requests) / self.protected_requests * 100


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise CSRF Protection Middleware
    
    Features:
    - Multiple token types support
    - Origin and referer validation
    - Rate limiting per IP
    - Comprehensive audit logging
    - Real-time metrics collection
    - Attack detection and alerts
    - Creator-specific optimizations
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[CSRFConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or CSRFConfig()
        self.logger = logger or self._setup_logger()
        
        # Generate secret key if not provided
        if not self.config.secret_key:
            self.config.secret_key = secrets.token_urlsafe(32)
        
        # Security state
        self.active_tokens: Dict[str, CSRFToken] = {}
        self.failure_counts: Dict[str, Dict[str, int]] = {}
        self.metrics = CSRFMetrics()
        self.attack_patterns: Dict[str, int] = {}
        
        # Validate configuration
        self._validate_config()
        
        self.logger.info(f"CSRF Protection initialized with level: {self.config.protection_level}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup security audit logger"""
        logger = logging.getLogger("csrf_security")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _validate_config(self):
        """Validate CSRF configuration"""
        if self.config.protection_level == CSRFProtectionLevel.DISABLED:
            self.logger.warning("CSRF protection is DISABLED - security risk!")
        
        if self.config.require_https and not self.config.cookie_secure:
            self.logger.warning("HTTPS required but cookie_secure is False")
        
        if self.config.token_lifetime > 86400:  # 24 hours
            self.logger.warning("Token lifetime > 24 hours may be security risk")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with CSRF protection"""
        start_time = datetime.utcnow()
        client_ip = self._get_client_ip(request)
        
        try:
            self.metrics.total_requests += 1
            
            # Skip protection if disabled
            if self.config.protection_level == CSRFProtectionLevel.DISABLED:
                return await call_next(request)
            
            # Skip safe methods and exempted paths
            if await self._should_skip_protection(request):
                return await call_next(request)
            
            self.metrics.protected_requests += 1
            
            # Rate limiting check
            if not await self._check_rate_limit(client_ip):
                self.metrics.rate_limit_hits += 1
                return await self._create_blocked_response(
                    "Rate limit exceeded", request, "RATE_LIMIT"
                )
            
            # CSRF validation
            validation_result = await self._validate_csrf(request)
            if not validation_result["valid"]:
                self.metrics.blocked_requests += 1
                await self._record_failure(client_ip, validation_result["reason"])
                
                return await self._create_blocked_response(
                    validation_result["reason"], request, "CSRF_VIOLATION"
                )
            
            # Process request
            response = await call_next(request)
            
            # Add/refresh CSRF token in response
            response = await self._add_csrf_token(response, request)
            
            # Audit logging
            if self.config.enable_audit_logging:
                self._log_request(request, "ALLOWED", start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"CSRF middleware error: {e}")
            self.metrics.blocked_requests += 1
            
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers={"X-Content-Type-Options": "nosniff"}
            )
    
    async def _should_skip_protection(self, request: Request) -> bool:
        """Check if request should skip CSRF protection"""
        # Safe methods
        if request.method in self.config.safe_methods:
            return True
        
        # Exempted paths
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.config.exempted_paths):
            return True
        
        # Exempted user agents (e.g., mobile apps, APIs)
        user_agent = request.headers.get("user-agent", "")
        if any(ua in user_agent for ua in self.config.exempted_user_agents):
            return True
        
        # API endpoints (if Content-Type is application/json and no browser headers)
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            # Check if it's likely a browser request
            accept = request.headers.get("accept", "")
            if "text/html" not in accept and "application/xhtml" not in accept:
                return True
        
        return False
    
    async def _validate_csrf(self, request: Request) -> Dict[str, Any]:
        """Comprehensive CSRF validation"""
        validation_methods = []
        
        # Origin validation
        if self.config.enable_origin_validation:
            origin_result = await self._validate_origin(request)
            validation_methods.append(("origin", origin_result))
        
        # Referer validation
        if self.config.enable_referer_validation:
            referer_result = await self._validate_referer(request)
            validation_methods.append(("referer", referer_result))
        
        # Token validation
        if self.config.validation_method in [
            CSRFValidationMethod.TOKEN_VALIDATION, 
            CSRFValidationMethod.COMBINED
        ]:
            token_result = await self._validate_token(request)
            validation_methods.append(("token", token_result))
        
        # Evaluate results based on validation method
        if self.config.validation_method == CSRFValidationMethod.COMBINED:
            # All validations must pass
            for method, result in validation_methods:
                if not result["valid"]:
                    return {"valid": False, "reason": f"{method}_validation_failed", "details": result}
        else:
            # At least one validation must pass
            valid_methods = [result for _, result in validation_methods if result["valid"]]
            if not valid_methods:
                failed_reasons = [result["reason"] for _, result in validation_methods]
                return {"valid": False, "reason": "all_validations_failed", "details": failed_reasons}
        
        return {"valid": True, "reason": "validation_passed"}
    
    async def _validate_origin(self, request: Request) -> Dict[str, Any]:
        """Validate request origin"""
        origin = request.headers.get("origin")
        
        if not origin:
            return {"valid": False, "reason": "missing_origin"}
        
        # Check against trusted origins
        if self.config.trusted_origins:
            if origin not in self.config.trusted_origins:
                return {"valid": False, "reason": "untrusted_origin", "origin": origin}
        else:
            # Validate against request host
            host = request.headers.get("host")
            if host:
                expected_origins = [
                    f"https://{host}",
                    f"http://{host}" if not self.config.require_https else None
                ]
                expected_origins = [o for o in expected_origins if o is not None]
                
                if origin not in expected_origins:
                    return {"valid": False, "reason": "origin_host_mismatch", "origin": origin, "host": host}
        
        self.logger.debug(f"Origin validation passed: {origin}")
        return {"valid": True, "reason": "origin_valid"}
    
    async def _validate_referer(self, request: Request) -> Dict[str, Any]:
        """Validate request referer"""
        referer = request.headers.get("referer")
        
        if not referer:
            return {"valid": False, "reason": "missing_referer"}
        
        try:
            referer_parsed = urlparse(referer)
            host = request.headers.get("host")
            
            if host and referer_parsed.netloc != host:
                return {"valid": False, "reason": "referer_host_mismatch", "referer": referer, "host": host}
            
        except Exception as e:
            return {"valid": False, "reason": "invalid_referer_format", "error": str(e)}
        
        self.logger.debug(f"Referer validation passed: {referer}")
        return {"valid": True, "reason": "referer_valid"}
    
    async def _validate_token(self, request: Request) -> Dict[str, Any]:
        """Validate CSRF token"""
        if self.config.token_type == CSRFTokenType.HEADER_ONLY:
            return await self._validate_header_token(request)
        elif self.config.token_type == CSRFTokenType.COOKIE_ONLY:
            return await self._validate_cookie_token(request)
        elif self.config.token_type == CSRFTokenType.DOUBLE_SUBMIT:
            return await self._validate_double_submit_token(request)
        elif self.config.token_type == CSRFTokenType.ENCRYPTED_TOKEN:
            return await self._validate_encrypted_token(request)
        elif self.config.token_type == CSRFTokenType.SYNCHRONIZED_TOKEN:
            return await self._validate_synchronized_token(request)
        
        return {"valid": False, "reason": "unknown_token_type"}
    
    async def _validate_header_token(self, request: Request) -> Dict[str, Any]:
        """Validate CSRF token from header"""
        token = request.headers.get(self.config.csrf_header_name)
        
        if not token:
            return {"valid": False, "reason": "missing_csrf_header"}
        
        return await self._verify_token(token, request)
    
    async def _validate_cookie_token(self, request: Request) -> Dict[str, Any]:
        """Validate CSRF token from cookie"""
        token = request.cookies.get(self.config.csrf_cookie_name)
        
        if not token:
            return {"valid": False, "reason": "missing_csrf_cookie"}
        
        return await self._verify_token(token, request)
    
    async def _validate_double_submit_token(self, request: Request) -> Dict[str, Any]:
        """Validate double submit CSRF token"""
        header_token = request.headers.get(self.config.csrf_header_name)
        cookie_token = request.cookies.get(self.config.csrf_cookie_name)
        
        if not header_token:
            return {"valid": False, "reason": "missing_csrf_header"}
        
        if not cookie_token:
            return {"valid": False, "reason": "missing_csrf_cookie"}
        
        # Tokens must match
        if not secrets.compare_digest(header_token, cookie_token):
            return {"valid": False, "reason": "token_mismatch"}
        
        return await self._verify_token(header_token, request)
    
    async def _validate_encrypted_token(self, request: Request) -> Dict[str, Any]:
        """Validate encrypted CSRF token"""
        encrypted_token = request.headers.get(self.config.csrf_header_name)
        
        if not encrypted_token:
            return {"valid": False, "reason": "missing_encrypted_token"}
        
        try:
            # Decrypt token
            token = self._decrypt_token(encrypted_token)
            return await self._verify_token(token, request)
        except Exception as e:
            return {"valid": False, "reason": "token_decryption_failed", "error": str(e)}
    
    async def _validate_synchronized_token(self, request: Request) -> Dict[str, Any]:
        """Validate synchronized CSRF token (server-side storage)"""
        token = request.headers.get(self.config.csrf_header_name)
        
        if not token:
            return {"valid": False, "reason": "missing_synchronized_token"}
        
        # Check if token exists in server storage
        if token not in self.active_tokens:
            return {"valid": False, "reason": "token_not_found"}
        
        csrf_token = self.active_tokens[token]
        
        if csrf_token.is_expired:
            del self.active_tokens[token]
            return {"valid": False, "reason": "token_expired"}
        
        return {"valid": True, "reason": "synchronized_token_valid"}
    
    async def _verify_token(self, token: str, request: Request) -> Dict[str, Any]:
        """Verify CSRF token validity"""
        try:
            # Basic format validation
            if len(token) != self.config.token_length * 2:  # hex encoding doubles length
                return {"valid": False, "reason": "invalid_token_format"}
            
            # Verify token signature if using HMAC
            if self.config.protection_level in [CSRFProtectionLevel.STRICT, CSRFProtectionLevel.PARANOID]:
                if not self._verify_token_signature(token, request):
                    return {"valid": False, "reason": "invalid_token_signature"}
            
            return {"valid": True, "reason": "token_valid"}
            
        except Exception as e:
            return {"valid": False, "reason": "token_verification_error", "error": str(e)}
    
    def _verify_token_signature(self, token: str, request: Request) -> bool:
        """Verify token HMAC signature"""
        try:
            # Extract token parts (assumes format: token.timestamp.signature)
            parts = token.split('.')
            if len(parts) != 3:
                return False
            
            token_value, timestamp, signature = parts
            
            # Recreate signature
            message = f"{token_value}.{timestamp}"
            expected_signature = hmac.new(
                self.config.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return secrets.compare_digest(signature, expected_signature)
            
        except Exception:
            return False
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt encrypted CSRF token"""
        # Implement your encryption/decryption logic here
        # This is a simple base64 example - use proper encryption in production
        try:
            return base64.b64decode(encrypted_token).decode()
        except Exception:
            raise ValueError("Token decryption failed")
    
    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Check rate limiting for failed attempts"""
        if not self.config.enable_rate_limiting:
            return True
        
        current_time = int(time.time())
        window_start = current_time - self.config.failure_window
        
        # Clean old entries
        if client_ip in self.failure_counts:
            self.failure_counts[client_ip] = {
                timestamp: count for timestamp, count in self.failure_counts[client_ip].items()
                if int(timestamp) > window_start
            }
        
        # Count recent failures
        recent_failures = sum(
            self.failure_counts.get(client_ip, {}).values()
        )
        
        return recent_failures < self.config.max_failures_per_ip
    
    async def _record_failure(self, client_ip: str, reason: str):
        """Record failed CSRF attempt"""
        current_minute = str(int(time.time()) // 60 * 60)
        
        if client_ip not in self.failure_counts:
            self.failure_counts[client_ip] = {}
        
        self.failure_counts[client_ip][current_minute] = (
            self.failure_counts[client_ip].get(current_minute, 0) + 1
        )
        
        # Update metrics
        self.metrics.validation_failures += 1
        if "origin" in reason:
            self.metrics.origin_failures += 1
        elif "referer" in reason:
            self.metrics.referer_failures += 1
        elif "token" in reason:
            self.metrics.token_failures += 1
        
        # Attack pattern detection
        self.attack_patterns[reason] = self.attack_patterns.get(reason, 0) + 1
        
        self.logger.warning(f"CSRF failure recorded for {client_ip}: {reason}")
        
        # Send alert if configured
        if self.config.alert_on_attacks:
            await self._send_security_alert(client_ip, reason)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check X-Forwarded-For header first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _create_blocked_response(self, reason: str, request: Request, attack_type: str) -> Response:
        """Create response for blocked requests"""
        self.logger.warning(f"CSRF request blocked: {reason} - Path: {request.url.path}")
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "CSRF protection violation",
                "message": "Request blocked by security policy"
            },
            headers={
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
        )
    
    async def _add_csrf_token(self, response: Response, request: Request) -> Response:
        """Add CSRF token to response"""
        # Generate new token
        token = self._generate_csrf_token(request)
        
        if self.config.token_type in [CSRFTokenType.COOKIE_ONLY, CSRFTokenType.DOUBLE_SUBMIT]:
            # Set cookie
            response.set_cookie(
                key=self.config.csrf_cookie_name,
                value=token,
                max_age=self.config.token_lifetime,
                secure=self.config.cookie_secure,
                httponly=self.config.cookie_httponly,
                samesite=self.config.cookie_samesite,
                domain=self.config.cookie_domain,
                path=self.config.cookie_path
            )
        
        if self.config.token_type in [CSRFTokenType.HEADER_ONLY, CSRFTokenType.DOUBLE_SUBMIT]:
            # Set header
            response.headers[self.config.csrf_header_name] = token
        
        return response
    
    def _generate_csrf_token(self, request: Request) -> str:
        """Generate CSRF token"""
        self.metrics.token_generations += 1
        
        if self.config.token_type == CSRFTokenType.SYNCHRONIZED_TOKEN:
            return self._generate_synchronized_token(request)
        elif self.config.token_type == CSRFTokenType.ENCRYPTED_TOKEN:
            return self._generate_encrypted_token(request)
        else:
            return self._generate_signed_token(request)
    
    def _generate_synchronized_token(self, request: Request) -> str:
        """Generate synchronized token (server-side storage)"""
        token_value = secrets.token_urlsafe(self.config.token_length)
        
        csrf_token = CSRFToken(
            value=token_value,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=self.config.token_lifetime),
            origin=request.headers.get("origin"),
            session_id=request.headers.get("x-session-id")  # If you have session management
        )
        
        self.active_tokens[token_value] = csrf_token
        
        # Clean expired tokens
        self._cleanup_expired_tokens()
        
        return token_value
    
    def _generate_encrypted_token(self, request: Request) -> str:
        """Generate encrypted token"""
        token_value = secrets.token_urlsafe(self.config.token_length)
        
        # Simple base64 encryption (use proper encryption in production)
        encrypted = base64.b64encode(token_value.encode()).decode()
        
        return encrypted
    
    def _generate_signed_token(self, request: Request) -> str:
        """Generate HMAC signed token"""
        token_value = secrets.token_urlsafe(self.config.token_length)
        timestamp = str(int(time.time()))
        
        if self.config.protection_level in [CSRFProtectionLevel.STRICT, CSRFProtectionLevel.PARANOID]:
            # Add HMAC signature
            message = f"{token_value}.{timestamp}"
            signature = hmac.new(
                self.config.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return f"{token_value}.{timestamp}.{signature}"
        else:
            return token_value
    
    def _cleanup_expired_tokens(self):
        """Remove expired tokens from storage"""
        current_time = datetime.utcnow()
        expired_tokens = [
            token for token, csrf_token in self.active_tokens.items()
            if csrf_token.expires_at < current_time
        ]
        
        for token in expired_tokens:
            del self.active_tokens[token]
        
        if expired_tokens:
            self.logger.debug(f"Cleaned up {len(expired_tokens)} expired CSRF tokens")
    
    async def _send_security_alert(self, client_ip: str, reason: str):
        """Send security alert for CSRF attacks"""
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "CSRF_ATTACK",
            "client_ip": client_ip,
            "reason": reason,
            "failure_count": sum(self.failure_counts.get(client_ip, {}).values())
        }
        
        # TODO: Implement your alerting mechanism
        self.logger.error(f"CSRF Attack Alert: {alert_data}")
    
    def _log_request(self, request: Request, status: str, start_time: datetime):
        """Log request for audit purposes"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        self.logger.info(
            f"CSRF {status}: {request.method} {request.url.path} "
            f"Duration: {duration:.3f}s IP: {self._get_client_ip(request)}"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current CSRF metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "protected_requests": self.metrics.protected_requests,
            "blocked_requests": self.metrics.blocked_requests,
            "success_rate": self.metrics.success_rate,
            "token_generations": self.metrics.token_generations,
            "validation_failures": self.metrics.validation_failures,
            "origin_failures": self.metrics.origin_failures,
            "referer_failures": self.metrics.referer_failures,
            "token_failures": self.metrics.token_failures,
            "rate_limit_hits": self.metrics.rate_limit_hits,
            "active_tokens": len(self.active_tokens),
            "attack_patterns": self.attack_patterns,
            "failure_counts": len(self.failure_counts)
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = CSRFMetrics()
        self.attack_patterns.clear()
        self.failure_counts.clear()
        self.logger.info("CSRF metrics reset")


# Factory functions for easy integration
def create_csrf_middleware(
    app: FastAPI,
    protection_level: CSRFProtectionLevel = CSRFProtectionLevel.STRICT,
    **kwargs
) -> CSRFProtectionMiddleware:
    """
    🏭 Factory function to create CSRF middleware
    
    Args:
        app: FastAPI application
        protection_level: CSRF protection level
        **kwargs: Additional configuration options
    
    Returns:
        Configured CSRF middleware instance
    """
    config = CSRFConfig(
        protection_level=protection_level,
        **kwargs
    )
    
    return CSRFProtectionMiddleware(app, config)


def setup_creator_csrf(app: FastAPI) -> CSRFProtectionMiddleware:
    """
    🎯 Creator-specific CSRF setup
    Optimized for content creation platforms
    """
    creator_config = CSRFConfig(
        protection_level=CSRFProtectionLevel.STRICT,
        token_type=CSRFTokenType.DOUBLE_SUBMIT,
        validation_method=CSRFValidationMethod.COMBINED,
        
        # Creator-specific settings
        trusted_origins={
            "https://studio.youtube.com",
            "https://creator.instagram.com", 
            "https://ads.tiktok.com",
            "https://creators.spotify.com"
        },
        
        exempted_paths={
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/health",
            "/api/v1/webhooks/"  # External platform webhooks
        },
        
        exempted_user_agents={
            "YouTubeCreatorStudio",
            "InstagramCreator",
            "TikTokAds",
            "SpotifyCreator"
        },
        
        # Enhanced security for creators
        enable_audit_logging=True,
        enable_metrics=True,
        alert_on_attacks=True,
        max_failures_per_ip=5,  # Stricter for creator accounts
        token_lifetime=1800  # 30 minutes for creator sessions
    )
    
    return CSRFProtectionMiddleware(app, creator_config)


# CSRF Token dependency for FastAPI
def get_csrf_token(request: Request) -> str:
    """
    🔑 FastAPI dependency to get CSRF token
    Use with Depends() in your endpoints
    """
    csrf_middleware = None
    
    # Find CSRF middleware in app middleware stack
    for middleware in request.app.middleware_stack:
        if isinstance(middleware, CSRFProtectionMiddleware):
            csrf_middleware = middleware
            break
    
    if not csrf_middleware:
        raise HTTPException(status_code=500, detail="CSRF middleware not found")
    
    # Generate token for the request
    return csrf_middleware._generate_csrf_token(request)


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI, Depends
    
    app = FastAPI(title="CSRF Protection Demo")
    
    # Setup CSRF middleware
    csrf_middleware = create_csrf_middleware(
        app,
        protection_level=CSRFProtectionLevel.STRICT
    )
    
    app.add_middleware(CSRFProtectionMiddleware, middleware=csrf_middleware)
    
    @app.get("/")
    async def root():
        return {"message": "CSRF Protection Template Active"}
    
    @app.get("/csrf-token")
    async def get_token(csrf_token: str = Depends(get_csrf_token)):
        return {"csrf_token": csrf_token}
    
    @app.post("/secure-action")
    async def secure_action(data: dict):
        return {"message": "Secure action completed", "data": data}
    
    @app.get("/metrics")
    async def get_metrics():
        return csrf_middleware.get_metrics()