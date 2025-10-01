#!/usr/bin/env python3
"""
⚡ CORS Middleware Template - Enterprise Security
🏗️ Architecture: iacherie Creator Economy Platform
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

from typing import Dict, List, Optional, Set, Union, Any
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import re
import ipaddress
from urllib.parse import urlparse
import logging
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass, field
from enum import Enum

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + DevOps Engineer
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class CORSPolicy(str, Enum):
    """CORS security policy levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"
    CUSTOM = "custom"


class OriginValidationType(str, Enum):
    """Origin validation methods"""
    EXACT_MATCH = "exact_match"
    REGEX_PATTERN = "regex_pattern"
    DOMAIN_WHITELIST = "domain_whitelist"
    IP_WHITELIST = "ip_whitelist"


@dataclass
class CORSConfig:
    """Enterprise CORS configuration"""
    # Basic CORS settings
    allowed_origins: Set[str] = field(default_factory=set)
    allowed_methods: Set[str] = field(default_factory=lambda: {"GET", "POST", "PUT", "DELETE", "OPTIONS"})
    allowed_headers: Set[str] = field(default_factory=lambda: {"Content-Type", "Authorization", "X-Requested-With"})
    exposed_headers: Set[str] = field(default_factory=set)
    allow_credentials: bool = True
    max_age: int = 86400  # 24 hours
    
    # Security enhancements
    policy_level: CORSPolicy = CORSPolicy.STRICT
    validation_type: OriginValidationType = OriginValidationType.EXACT_MATCH
    origin_patterns: List[str] = field(default_factory=list)
    trusted_domains: Set[str] = field(default_factory=set)
    blocked_origins: Set[str] = field(default_factory=set)
    
    # Advanced features
    enable_preflight_cache: bool = True
    enable_origin_validation: bool = True
    enable_security_headers: bool = True
    enable_audit_logging: bool = True
    
    # Rate limiting per origin
    rate_limit_per_origin: int = 1000  # requests per hour
    rate_limit_window: int = 3600  # 1 hour in seconds
    
    # Monitoring
    enable_metrics: bool = True
    alert_on_blocked_requests: bool = True


@dataclass
class OriginMetrics:
    """Origin request metrics"""
    origin: str
    request_count: int = 0
    blocked_count: int = 0
    last_request: Optional[datetime] = None
    first_request: Optional[datetime] = None
    methods_used: Set[str] = field(default_factory=set)
    user_agents: Set[str] = field(default_factory=set)


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise CORS Middleware with Advanced Security
    
    Features:
    - Multi-level security policies
    - Advanced origin validation
    - Rate limiting per origin
    - Security headers injection
    - Comprehensive audit logging
    - Real-time metrics collection
    - Threat detection
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[CORSConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or CORSConfig()
        self.logger = logger or self._setup_logger()
        
        # Security state
        self.origin_metrics: Dict[str, OriginMetrics] = {}
        self.rate_limit_buckets: Dict[str, Dict[str, int]] = {}
        self.security_violations: Dict[str, int] = {}
        
        # Threat detection
        self.suspicious_patterns = [
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'<script',
            r'onerror=',
            r'onload='
        ]
        
        self._compile_patterns()
        self._setup_default_policies()
        
        self.logger.info(f"CORS Security Middleware initialized with policy: {self.config.policy_level}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup security audit logger"""
        logger = logging.getLogger("cors_security")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        self.compiled_patterns = []
        for pattern in self.config.origin_patterns:
            try:
                self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                self.logger.error(f"Invalid regex pattern '{pattern}': {e}")
    
    def _setup_default_policies(self):
        """Setup default security policies"""
        if self.config.policy_level == CORSPolicy.STRICT:
            self.config.allowed_methods = {"GET", "POST", "OPTIONS"}
            self.config.allowed_headers = {"Content-Type", "Authorization"}
            self.config.allow_credentials = False
            self.config.max_age = 300  # 5 minutes
        
        elif self.config.policy_level == CORSPolicy.MODERATE:
            self.config.allowed_methods = {"GET", "POST", "PUT", "DELETE", "OPTIONS"}
            self.config.allowed_headers = {
                "Content-Type", "Authorization", "X-Requested-With", "Accept"
            }
            self.config.allow_credentials = True
            self.config.max_age = 3600  # 1 hour
        
        elif self.config.policy_level == CORSPolicy.PERMISSIVE:
            self.config.allowed_methods = {"*"}
            self.config.allowed_headers = {"*"}
            self.config.allow_credentials = True
            self.config.max_age = 86400  # 24 hours
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with security checks"""
        start_time = datetime.utcnow()
        origin = request.headers.get("origin")
        
        try:
            # Security validation
            security_result = await self._validate_security(request, origin)
            if not security_result["allowed"]:
                return await self._create_blocked_response(
                    security_result["reason"], 
                    origin, 
                    request
                )
            
            # Handle preflight requests
            if request.method == "OPTIONS":
                return await self._handle_preflight(request, origin)
            
            # Process actual request
            response = await call_next(request)
            
            # Add CORS headers to response
            response = await self._add_cors_headers(response, origin, request)
            
            # Update metrics
            await self._update_metrics(origin, request, True)
            
            # Audit logging
            if self.config.enable_audit_logging:
                self._log_request(request, origin, "ALLOWED", start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"CORS middleware error: {e}")
            await self._update_metrics(origin, request, False)
            
            # Return safe error response
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers=self._get_security_headers()
            )
    
    async def _validate_security(self, request: Request, origin: Optional[str]) -> Dict[str, Any]:
        """Comprehensive security validation"""
        # Check if origin is required
        if not origin and self.config.policy_level == CORSPolicy.STRICT:
            return {"allowed": False, "reason": "Missing Origin header"}
        
        if not origin:
            return {"allowed": True, "reason": "No origin validation needed"}
        
        # Rate limiting check
        if not await self._check_rate_limit(origin, request):
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        # Origin validation
        if not await self._validate_origin(origin):
            return {"allowed": False, "reason": "Origin not allowed"}
        
        # Threat detection
        if await self._detect_threats(origin, request):
            return {"allowed": False, "reason": "Security threat detected"}
        
        # IP validation
        if not await self._validate_ip(request):
            return {"allowed": False, "reason": "IP address blocked"}
        
        return {"allowed": True, "reason": "Validation passed"}
    
    async def _validate_origin(self, origin: str) -> bool:
        """Advanced origin validation"""
        if not self.config.enable_origin_validation:
            return True
        
        # Check blocked origins first
        if origin in self.config.blocked_origins:
            return False
        
        # Exact match validation
        if self.config.validation_type == OriginValidationType.EXACT_MATCH:
            return origin in self.config.allowed_origins
        
        # Regex pattern validation
        elif self.config.validation_type == OriginValidationType.REGEX_PATTERN:
            return any(pattern.match(origin) for pattern in self.compiled_patterns)
        
        # Domain whitelist validation
        elif self.config.validation_type == OriginValidationType.DOMAIN_WHITELIST:
            try:
                parsed = urlparse(origin)
                domain = parsed.netloc.lower()
                return any(domain.endswith(trusted) for trusted in self.config.trusted_domains)
            except Exception:
                return False
        
        # IP whitelist validation
        elif self.config.validation_type == OriginValidationType.IP_WHITELIST:
            try:
                parsed = urlparse(origin)
                host = parsed.netloc.split(':')[0]
                ip = ipaddress.ip_address(host)
                return str(ip) in self.config.allowed_origins
            except Exception:
                return False
        
        return False
    
    async def _detect_threats(self, origin: str, request: Request) -> bool:
        """Detect security threats in requests"""
        # Check for suspicious patterns in origin
        for pattern in self.suspicious_patterns:
            if re.search(pattern, origin, re.IGNORECASE):
                self.logger.warning(f"Suspicious pattern detected in origin: {origin}")
                return True
        
        # Check for suspicious headers
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            self.logger.warning(f"Suspicious or missing User-Agent from {origin}")
            return True
        
        # Check for potential XSS in referer
        referer = request.headers.get("referer", "")
        if referer:
            for pattern in self.suspicious_patterns:
                if re.search(pattern, referer, re.IGNORECASE):
                    self.logger.warning(f"Suspicious pattern in referer from {origin}")
                    return True
        
        return False
    
    async def _validate_ip(self, request: Request) -> bool:
        """Validate client IP address"""
        client_ip = self._get_client_ip(request)
        if not client_ip:
            return True
        
        # Check against blocked IPs (this would be loaded from database/config)
        blocked_ips = getattr(self.config, 'blocked_ips', set())
        return client_ip not in blocked_ips
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
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
        
        return None
    
    async def _check_rate_limit(self, origin: str, request: Request) -> bool:
        """Check rate limiting per origin"""
        if not hasattr(self.config, 'rate_limit_per_origin'):
            return True
        
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=self.config.rate_limit_window)
        
        # Initialize bucket if needed
        if origin not in self.rate_limit_buckets:
            self.rate_limit_buckets[origin] = {}
        
        # Clean old entries
        bucket = self.rate_limit_buckets[origin]
        bucket = {
            timestamp: count for timestamp, count in bucket.items()
            if datetime.fromisoformat(timestamp) > window_start
        }
        self.rate_limit_buckets[origin] = bucket
        
        # Count current requests
        current_minute = current_time.replace(second=0, microsecond=0).isoformat()
        current_count = sum(bucket.values())
        
        if current_count >= self.config.rate_limit_per_origin:
            self.logger.warning(f"Rate limit exceeded for origin: {origin}")
            return False
        
        # Update bucket
        bucket[current_minute] = bucket.get(current_minute, 0) + 1
        return True
    
    async def _handle_preflight(self, request: Request, origin: Optional[str]) -> Response:
        """Handle CORS preflight requests"""
        headers = self._get_cors_headers(origin, request)
        
        # Add preflight-specific headers
        if self.config.enable_preflight_cache:
            headers["Access-Control-Max-Age"] = str(self.config.max_age)
        
        # Validate preflight request
        requested_method = request.headers.get("access-control-request-method")
        if requested_method and requested_method not in self.config.allowed_methods:
            if "*" not in self.config.allowed_methods:
                return JSONResponse(
                    status_code=405,
                    content={"error": "Method not allowed"},
                    headers=self._get_security_headers()
                )
        
        requested_headers = request.headers.get("access-control-request-headers", "")
        if requested_headers and "*" not in self.config.allowed_headers:
            requested_header_list = [h.strip().lower() for h in requested_headers.split(",")]
            allowed_header_list = [h.lower() for h in self.config.allowed_headers]
            
            for header in requested_header_list:
                if header not in allowed_header_list:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Header not allowed"},
                        headers=self._get_security_headers()
                    )
        
        return Response(status_code=204, headers=headers)
    
    def _get_cors_headers(self, origin: Optional[str], request: Request) -> Dict[str, str]:
        """Generate CORS headers"""
        headers = {}
        
        # Access-Control-Allow-Origin
        if origin and origin in self.config.allowed_origins:
            headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.config.allowed_origins and not self.config.allow_credentials:
            headers["Access-Control-Allow-Origin"] = "*"
        elif origin and await self._validate_origin(origin):
            headers["Access-Control-Allow-Origin"] = origin
        
        # Access-Control-Allow-Credentials
        if self.config.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        # Access-Control-Allow-Methods
        if self.config.allowed_methods:
            if "*" in self.config.allowed_methods:
                headers["Access-Control-Allow-Methods"] = "*"
            else:
                headers["Access-Control-Allow-Methods"] = ", ".join(self.config.allowed_methods)
        
        # Access-Control-Allow-Headers
        if self.config.allowed_headers:
            if "*" in self.config.allowed_headers:
                headers["Access-Control-Allow-Headers"] = "*"
            else:
                headers["Access-Control-Allow-Headers"] = ", ".join(self.config.allowed_headers)
        
        # Access-Control-Expose-Headers
        if self.config.exposed_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.config.exposed_headers)
        
        # Add security headers
        if self.config.enable_security_headers:
            headers.update(self._get_security_headers())
        
        return headers
    
    def _get_security_headers(self) -> Dict[str, str]:
        """Get additional security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }
    
    async def _add_cors_headers(self, response: Response, origin: Optional[str], request: Request) -> Response:
        """Add CORS headers to response"""
        cors_headers = self._get_cors_headers(origin, request)
        
        for key, value in cors_headers.items():
            response.headers[key] = value
        
        return response
    
    async def _create_blocked_response(self, reason: str, origin: Optional[str], request: Request) -> Response:
        """Create response for blocked requests"""
        self.logger.warning(f"CORS request blocked: {reason} - Origin: {origin}")
        
        # Update security violations counter
        key = f"{origin}:{reason}"
        self.security_violations[key] = self.security_violations.get(key, 0) + 1
        
        # Alert if configured
        if self.config.alert_on_blocked_requests:
            await self._send_security_alert(reason, origin, request)
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "CORS policy violation",
                "message": "Request blocked by security policy"
            },
            headers=self._get_security_headers()
        )
    
    async def _update_metrics(self, origin: Optional[str], request: Request, allowed: bool):
        """Update request metrics"""
        if not origin or not self.config.enable_metrics:
            return
        
        if origin not in self.origin_metrics:
            self.origin_metrics[origin] = OriginMetrics(origin=origin)
        
        metrics = self.origin_metrics[origin]
        metrics.request_count += 1
        metrics.last_request = datetime.utcnow()
        
        if metrics.first_request is None:
            metrics.first_request = metrics.last_request
        
        if not allowed:
            metrics.blocked_count += 1
        
        metrics.methods_used.add(request.method)
        
        user_agent = request.headers.get("user-agent")
        if user_agent:
            metrics.user_agents.add(user_agent[:100])  # Limit length
    
    def _log_request(self, request: Request, origin: Optional[str], status: str, start_time: datetime):
        """Log request for audit purposes"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        self.logger.info(
            f"CORS {status}: {request.method} {request.url.path} "
            f"Origin: {origin} Duration: {duration:.3f}s "
            f"IP: {self._get_client_ip(request)}"
        )
    
    async def _send_security_alert(self, reason: str, origin: Optional[str], request: Request):
        """Send security alert (implement based on your alerting system)"""
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "CORS_VIOLATION",
            "reason": reason,
            "origin": origin,
            "method": request.method,
            "path": str(request.url.path),
            "ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent")
        }
        
        # TODO: Implement your alerting mechanism (e.g., send to monitoring system)
        self.logger.error(f"Security Alert: {alert_data}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "origin_metrics": {
                origin: {
                    "request_count": metrics.request_count,
                    "blocked_count": metrics.blocked_count,
                    "success_rate": (
                        (metrics.request_count - metrics.blocked_count) / metrics.request_count 
                        if metrics.request_count > 0 else 0
                    ),
                    "first_request": metrics.first_request.isoformat() if metrics.first_request else None,
                    "last_request": metrics.last_request.isoformat() if metrics.last_request else None,
                    "methods_used": list(metrics.methods_used),
                    "unique_user_agents": len(metrics.user_agents)
                }
                for origin, metrics in self.origin_metrics.items()
            },
            "security_violations": self.security_violations,
            "total_requests": sum(m.request_count for m in self.origin_metrics.values()),
            "total_blocked": sum(m.blocked_count for m in self.origin_metrics.values())
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.origin_metrics.clear()
        self.rate_limit_buckets.clear()
        self.security_violations.clear()
        self.logger.info("CORS metrics reset")


# Factory function for easy integration
def create_cors_middleware(
    app: FastAPI,
    allowed_origins: Optional[List[str]] = None,
    policy_level: CORSPolicy = CORSPolicy.MODERATE,
    **kwargs
) -> CORSSecurityMiddleware:
    """
    🏭 Factory function to create CORS middleware
    
    Args:
        app: FastAPI application
        allowed_origins: List of allowed origins
        policy_level: Security policy level
        **kwargs: Additional configuration options
    
    Returns:
        Configured CORS middleware instance
    """
    config = CORSConfig(
        allowed_origins=set(allowed_origins or []),
        policy_level=policy_level,
        **kwargs
    )
    
    return CORSSecurityMiddleware(app, config)


# Example usage for creators
def setup_creator_cors(app: FastAPI) -> CORSSecurityMiddleware:
    """
    🎯 Creator-specific CORS setup
    Optimized for content creation platforms
    """
    creator_origins = [
        "https://studio.youtube.com",
        "https://creator.instagram.com",
        "https://ads.tiktok.com",
        "https://creators.spotify.com",
        "https://business.linkedin.com"
    ]
    
    config = CORSConfig(
        allowed_origins=set(creator_origins),
        policy_level=CORSPolicy.MODERATE,
        allowed_methods={"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"},
        allowed_headers={
            "Content-Type", "Authorization", "X-Requested-With", 
            "Accept", "X-Creator-Token", "X-Platform-ID"
        },
        exposed_headers={"X-Rate-Limit-Remaining", "X-Creator-Credits"},
        allow_credentials=True,
        enable_audit_logging=True,
        enable_metrics=True,
        rate_limit_per_origin=5000  # Higher limit for creators
    )
    
    return CORSSecurityMiddleware(app, config)


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI(title="CORS Security Demo")
    
    # Setup CORS middleware
    cors_middleware = create_cors_middleware(
        app,
        allowed_origins=["https://localhost:3000", "https://app.example.com"],
        policy_level=CORSPolicy.STRICT
    )
    
    app.add_middleware(CORSSecurityMiddleware, middleware=cors_middleware)
    
    @app.get("/")
    async def root():
        return {"message": "CORS Security Template Active"}
    
    @app.get("/metrics")
    async def get_metrics():
        return cors_middleware.get_metrics()