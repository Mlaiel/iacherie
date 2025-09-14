"""{{service_name}} Security Middleware for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable, Set
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json
import uuid
import hashlib
import hmac
import base64
import ipaddress
from urllib.parse import urlparse

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import aioredis
from fastapi import Request, Response, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import bcrypt

from core.config import get_settings
from core.exceptions import SecurityException, AuthenticationException, AuthorizationException
from security.rate_limiter import SecurityRateLimiter
from security.threat_detection import ThreatDetector
from security.audit_logger import SecurityAuditLogger
from monitoring.security_metrics import SecurityMetricsCollector
from utils.ip_utils import IPValidator, GeoLocationService

logger = logging.getLogger(__name__)
settings = get_settings()


class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDoS = "ddos"
    MALWARE = "malware"
    PHISHING = "phishing"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class ActionType(Enum):
    """Security action types"""
    ALLOW = "allow"
    BLOCK = "block"
    MONITOR = "monitor"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"
    QUARANTINE = "quarantine"


class SecurityRule(BaseModel):
    """Security rule model"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    rule_type: str
    conditions: Dict[str, Any] = Field(default_factory=dict)
    action: ActionType
    severity: SecurityLevel
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityEvent(BaseModel):
    """Security event model"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str] = None
    endpoint: str
    user_agent: Optional[str] = None
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    action_taken: ActionType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False


class SecurityContext(BaseModel):
    """Security context for requests"""
    request_id: str
    source_ip: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: str
    method: str
    headers: Dict[str, str] = Field(default_factory=dict)
    threat_score: float = 0.0
    security_level: SecurityLevel = SecurityLevel.LOW
    blocked_reasons: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SecurityConfig(BaseModel):
    """Security middleware configuration"""
    enable_rate_limiting: bool = True
    enable_threat_detection: bool = True
    enable_ip_blocking: bool = True
    enable_geo_blocking: bool = False
    enable_user_agent_filtering: bool = True
    enable_sql_injection_protection: bool = True
    enable_xss_protection: bool = True
    enable_csrf_protection: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    session_timeout: int = 3600  # 1 hour
    jwt_secret: str = settings.jwt_secret
    encryption_key: Optional[str] = None
    allowed_origins: List[str] = Field(default_factory=list)
    blocked_countries: List[str] = Field(default_factory=list)
    trusted_proxies: List[str] = Field(default_factory=list)


class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_sql_injection(query: str) -> bool:
        """Check for SQL injection patterns"""
        sql_patterns = [
            r"(\s*(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+)",
            r"(\s*(or|and)\s+\d+\s*=\s*\d+)",
            r"(\s*'\s*or\s*'\s*=\s*')",
            r"(\s*--|\s*/\*|\*/)",
            r"(\s*;\s*(shutdown|drop|delete))",
            r"(char\(|ascii\(|substring\()",
            r"(information_schema|sysdatabases|sys.tables)"
        ]
        
        query_lower = query.lower()
        for pattern in sql_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def validate_xss(content: str) -> bool:
        """Check for XSS patterns"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"expression\s*\(",
            r"vbscript:",
            r"data:text/html"
        ]
        
        content_lower = content.lower()
        for pattern in xss_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                return False
        
        return True
    
    @staticmethod
    def validate_csrf_token(token: str, secret: str, user_id: str) -> bool:
        """Validate CSRF token"""
        try:
            expected_token = hmac.new(
                secret.encode(),
                f"{user_id}:csrf".encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(token, expected_token)
        except Exception:
            return False
    
    @staticmethod
    def is_safe_user_agent(user_agent: str) -> bool:
        """Check if user agent is safe"""
        if not user_agent:
            return False
        
        # Block known malicious user agents
        malicious_patterns = [
            r"sqlmap",
            r"nikto",
            r"nmap",
            r"masscan",
            r"w3af",
            r"curl.*bot",
            r"python.*requests",
            r"libwww",
            r"wget",
            r"scanner"
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in malicious_patterns:
            if re.search(pattern, user_agent_lower):
                return False
        
        return True


class {{service_class_name}}(BaseHTTPMiddleware):
    """
    Advanced security middleware for Ainflue platform.
    
    Features:
    - Request rate limiting and DDoS protection
    - SQL injection and XSS prevention
    - CSRF token validation
    - IP-based blocking and geo-filtering
    - User agent validation and bot detection
    - Threat scoring and behavioral analysis
    - Real-time security monitoring
    - Audit logging and compliance
    - JWT token validation
    - Content security policy enforcement
    - Request size limiting
    - Session management and timeout
    """
    
    def __init__(
        self,
        app,
        config -> None: Optional[SecurityConfig] = None,
        **kwargs
    ) -> None:
        super().__init__(app)
        self.config = config or SecurityConfig()
        
        # Initialize security components
        self.rate_limiter = SecurityRateLimiter()
        self.threat_detector = ThreatDetector()
        self.audit_logger = SecurityAuditLogger()
        self.ip_validator = IPValidator()
        self.geo_service = GeoLocationService()
        
        # Initialize metrics collector
        self.metrics = SecurityMetricsCollector()
        
        # Security state
        self.blocked_ips: Set[str] = set()
        self.security_rules: Dict[str, SecurityRule] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Redis client for distributed state
        self.redis_client = None
        
        # Initialize encryption
        if self.config.encryption_key:
            self.cipher_suite = Fernet(self.config.encryption_key.encode())
        else:
            self.cipher_suite = Fernet(Fernet.generate_key())
        
        logger.info("Security middleware initialized successfully")

    async def dispatch(self, request -> None: Request, call_next) -> None:
        """Main middleware dispatch method"""
        start_time = datetime.utcnow()
        
        try:
            # Create security context
            security_context = await self._create_security_context(request)
            
            # Pre-request security checks
            security_result = await self._perform_security_checks(
                request, security_context
            )
            
            if security_result['action'] == ActionType.BLOCK:
                return await self._create_blocked_response(
                    security_result['reasons'],
                    security_context
                )
            
            # Add security headers to request
            await self._add_security_context(request, security_context)
            
            # Process request
            response = await call_next(request)
            
            # Post-request security processing
            await self._post_process_security(
                request, response, security_context
            )
            
            # Add security headers to response
            await self._add_security_headers(response, security_context)
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics.record_request_processed(
                security_context.endpoint,
                security_context.security_level.value,
                processing_time
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            
            # Log security incident
            await self.audit_logger.log_security_incident(
                ThreatType.SUSPICIOUS_ACTIVITY,
                SecurityLevel.HIGH,
                f"Middleware error: {str(e)}",
                {"request_path": request.url.path}
            )
            
            # Return secure error response
            return JSONResponse(
                status_code=500,
                content={"error": "Internal security error"}
            )

    async def _create_security_context(self, request: Request) -> SecurityContext:
        """Create security context for the request"""
        try:
            # Extract basic request information
            source_ip = await self._get_real_ip(request)
            user_agent = request.headers.get('user-agent', '')
            endpoint = request.url.path
            method = request.method
            
            # Extract user information if available
            user_id = None
            session_id = None
            
            # Try to extract from JWT token
            auth_header = request.headers.get('authorization')
            if auth_header and auth_header.startswith('Bearer '):
                try:
                    token = auth_header.split(' ')[1]
                    payload = jwt.decode(
                        token,
                        self.config.jwt_secret,
                        algorithms=['HS256']
                    )
                    user_id = payload.get('sub')
                    session_id = payload.get('session_id')
                except jwt.InvalidTokenError:
                    pass
            
            # Create security context
            context = SecurityContext(
                request_id=str(uuid.uuid4()),
                source_ip=source_ip,
                user_id=user_id,
                session_id=session_id,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                headers=dict(request.headers)
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create security context: {str(e)}")
            raise SecurityException(f"Context creation failed: {str(e)}")

    async def _get_real_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers
        forwarded_headers = [
            'x-forwarded-for',
            'x-real-ip',
            'cf-connecting-ip',
            'x-forwarded'
        ]
        
        for header in forwarded_headers:
            if header in request.headers:
                ips = request.headers[header].split(',')
                for ip in ips:
                    ip = ip.strip()
                    try:
                        # Validate IP address
                        ipaddress.ip_address(ip)
                        
                        # Check if it's from trusted proxy
                        if self._is_trusted_proxy(ip):
                            continue
                        
                        return ip
                    except ValueError:
                        continue
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"

    def _is_trusted_proxy(self, ip: str) -> bool:
        """Check if IP is a trusted proxy"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check configured trusted proxies
            for trusted_ip in self.config.trusted_proxies:
                if ip_obj in ipaddress.ip_network(trusted_ip):
                    return True
            
            # Check private networks
            if ip_obj.is_private:
                return True
            
            return False
            
        except ValueError:
            return False

    async def _perform_security_checks(
        self,
        request: Request,
        context: SecurityContext
    ) -> Dict[str, Any]:
        """Perform comprehensive security checks"""
        blocked_reasons = []
        threat_score = 0.0
        
        try:
            # IP-based checks
            if self.config.enable_ip_blocking:
                ip_result = await self._check_ip_security(context)
                if not ip_result['allowed']:
                    blocked_reasons.extend(ip_result['reasons'])
                threat_score += ip_result['threat_score']
            
            # Rate limiting checks
            if self.config.enable_rate_limiting:
                rate_result = await self._check_rate_limits(context)
                if not rate_result['allowed']:
                    blocked_reasons.extend(rate_result['reasons'])
                threat_score += rate_result['threat_score']
            
            # User agent checks
            if self.config.enable_user_agent_filtering:
                ua_result = await self._check_user_agent(context)
                if not ua_result['allowed']:
                    blocked_reasons.extend(ua_result['reasons'])
                threat_score += ua_result['threat_score']
            
            # Content-based checks
            content_result = await self._check_request_content(request, context)
            if not content_result['allowed']:
                blocked_reasons.extend(content_result['reasons'])
            threat_score += content_result['threat_score']
            
            # Geo-location checks
            if self.config.enable_geo_blocking:
                geo_result = await self._check_geo_location(context)
                if not geo_result['allowed']:
                    blocked_reasons.extend(geo_result['reasons'])
                threat_score += geo_result['threat_score']
            
            # Threat detection
            if self.config.enable_threat_detection:
                threat_result = await self.threat_detector.analyze_request(
                    request, context
                )
                threat_score += threat_result['threat_score']
                if threat_result['threats']:
                    blocked_reasons.extend(threat_result['threats'])
            
            # Update context
            context.threat_score = threat_score
            context.blocked_reasons = blocked_reasons
            context.security_level = self._calculate_security_level(threat_score)
            
            # Determine action
            action = ActionType.ALLOW
            if blocked_reasons:
                action = ActionType.BLOCK
            elif threat_score > 0.7:
                action = ActionType.MONITOR
            elif threat_score > 0.5:
                action = ActionType.CHALLENGE
            
            return {
                'action': action,
                'reasons': blocked_reasons,
                'threat_score': threat_score,
                'security_level': context.security_level
            }
            
        except Exception as e:
            logger.error(f"Security checks failed: {str(e)}")
            return {
                'action': ActionType.BLOCK,
                'reasons': ['Security check error'],
                'threat_score': 1.0,
                'security_level': SecurityLevel.CRITICAL
            }

    async def _check_ip_security(self, context: SecurityContext) -> Dict[str, Any]:
        """Check IP-based security"""
        try:
            source_ip = context.source_ip
            
            # Check if IP is blocked
            if source_ip in self.blocked_ips:
                return {
                    'allowed': False,
                    'reasons': ['IP address blocked'],
                    'threat_score': 1.0
                }
            
            # Check IP reputation
            reputation_score = await self.ip_validator.check_reputation(source_ip)
            
            if reputation_score > 0.8:
                return {
                    'allowed': False,
                    'reasons': ['IP address has bad reputation'],
                    'threat_score': reputation_score
                }
            
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': reputation_score
            }
            
        except Exception as e:
            logger.error(f"IP security check failed: {str(e)}")
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }

    async def _check_rate_limits(self, context: SecurityContext) -> Dict[str, Any]:
        """Check rate limiting"""
        try:
            # Check various rate limits
            ip_limit_result = await self.rate_limiter.check_ip_rate_limit(
                context.source_ip
            )
            
            user_limit_result = None
            if context.user_id:
                user_limit_result = await self.rate_limiter.check_user_rate_limit(
                    context.user_id
                )
            
            endpoint_limit_result = await self.rate_limiter.check_endpoint_rate_limit(
                context.endpoint
            )
            
            # Evaluate results
            if not ip_limit_result['allowed']:
                return {
                    'allowed': False,
                    'reasons': ['IP rate limit exceeded'],
                    'threat_score': 0.5
                }
            
            if user_limit_result and not user_limit_result['allowed']:
                return {
                    'allowed': False,
                    'reasons': ['User rate limit exceeded'],
                    'threat_score': 0.3
                }
            
            if not endpoint_limit_result['allowed']:
                return {
                    'allowed': False,
                    'reasons': ['Endpoint rate limit exceeded'],
                    'threat_score': 0.4
                }
            
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }

    async def _check_user_agent(self, context: SecurityContext) -> Dict[str, Any]:
        """Check user agent security"""
        try:
            user_agent = context.user_agent
            
            if not user_agent:
                return {
                    'allowed': False,
                    'reasons': ['Missing user agent'],
                    'threat_score': 0.6
                }
            
            if not SecurityValidator.is_safe_user_agent(user_agent):
                return {
                    'allowed': False,
                    'reasons': ['Malicious user agent detected'],
                    'threat_score': 0.9
                }
            
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }
            
        except Exception as e:
            logger.error(f"User agent check failed: {str(e)}")
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }

    async def _check_request_content(
        self,
        request: Request,
        context: SecurityContext
    ) -> Dict[str, Any]:
        """Check request content for security issues"""
        try:
            blocked_reasons = []
            threat_score = 0.0
            
            # Check request size
            content_length = request.headers.get('content-length')
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.config.max_request_size:
                        blocked_reasons.append('Request size too large')
                        threat_score += 0.4
                except ValueError:
                    pass
            
            # Check query parameters for injection attacks
            if request.query_params:
                for key, value in request.query_params.items():
                    if self.config.enable_sql_injection_protection:
                        if not SecurityValidator.validate_sql_injection(str(value)):
                            blocked_reasons.append('SQL injection detected in query')
                            threat_score += 0.8
                    
                    if self.config.enable_xss_protection:
                        if not SecurityValidator.validate_xss(str(value)):
                            blocked_reasons.append('XSS attempt detected in query')
                            threat_score += 0.7
            
            # Check path parameters
            path = context.endpoint
            if self.config.enable_sql_injection_protection:
                if not SecurityValidator.validate_sql_injection(path):
                    blocked_reasons.append('SQL injection detected in path')
                    threat_score += 0.8
            
            if self.config.enable_xss_protection:
                if not SecurityValidator.validate_xss(path):
                    blocked_reasons.append('XSS attempt detected in path')
                    threat_score += 0.7
            
            # CSRF protection for state-changing operations
            if (context.method in ['POST', 'PUT', 'DELETE', 'PATCH'] and 
                self.config.enable_csrf_protection and context.user_id):
                
                csrf_token = request.headers.get('x-csrf-token')
                if not csrf_token:
                    blocked_reasons.append('Missing CSRF token')
                    threat_score += 0.5
                elif not SecurityValidator.validate_csrf_token(
                    csrf_token, self.config.jwt_secret, context.user_id
                ):
                    blocked_reasons.append('Invalid CSRF token')
                    threat_score += 0.8
            
            return {
                'allowed': len(blocked_reasons) == 0,
                'reasons': blocked_reasons,
                'threat_score': min(threat_score, 1.0)
            }
            
        except Exception as e:
            logger.error(f"Content security check failed: {str(e)}")
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }

    async def _check_geo_location(self, context: SecurityContext) -> Dict[str, Any]:
        """Check geo-location based security"""
        try:
            if not self.config.blocked_countries:
                return {
                    'allowed': True,
                    'reasons': [],
                    'threat_score': 0.0
                }
            
            country = await self.geo_service.get_country(context.source_ip)
            
            if country and country.upper() in self.config.blocked_countries:
                return {
                    'allowed': False,
                    'reasons': [f'Access blocked from country: {country}'],
                    'threat_score': 0.6
                }
            
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }
            
        except Exception as e:
            logger.error(f"Geo-location check failed: {str(e)}")
            return {
                'allowed': True,
                'reasons': [],
                'threat_score': 0.0
            }

    def _calculate_security_level(self, threat_score: float) -> SecurityLevel:
        """Calculate security level based on threat score"""
        if threat_score >= 0.8:
            return SecurityLevel.CRITICAL
        elif threat_score >= 0.6:
            return SecurityLevel.HIGH
        elif threat_score >= 0.3:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW

    async def _create_blocked_response(
        self,
        reasons: List[str],
        context: SecurityContext
    ) -> Response:
        """Create response for blocked requests"""
        try:
            # Log security event
            security_event = SecurityEvent(
                event_type=ThreatType.SUSPICIOUS_ACTIVITY,
                severity=context.security_level,
                source_ip=context.source_ip,
                user_id=context.user_id,
                endpoint=context.endpoint,
                user_agent=context.user_agent,
                description=f"Request blocked: {', '.join(reasons)}",
                evidence={'reasons': reasons, 'threat_score': context.threat_score},
                action_taken=ActionType.BLOCK
            )
            
            await self.audit_logger.log_security_event(security_event)
            
            # Record metrics
            await self.metrics.record_request_blocked(
                context.endpoint,
                context.security_level.value,
                reasons
            )
            
            # Return appropriate response
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Access denied",
                    "message": "Request blocked by security policy",
                    "request_id": context.request_id
                },
                headers={
                    "X-Security-Block": "true",
                    "X-Request-ID": context.request_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create blocked response: {str(e)}")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied"}
            )

    async def _add_security_context(
        self,
        request: Request,
        context: SecurityContext
    ) -> None:
        """Add security context to request"""
        try:
            # Add security context to request state
            request.state.security_context = context
            
            # Add security headers
            request.state.security_headers = {
                "X-Request-ID": context.request_id,
                "X-Security-Level": context.security_level.value,
                "X-Threat-Score": str(context.threat_score)
            }
            
        except Exception as e:
            logger.error(f"Failed to add security context: {str(e)}")

    async def _post_process_security(
        self,
        request: Request,
        response: Response,
        context: SecurityContext
    ) -> None:
        """Post-process security after request"""
        try:
            # Log successful request
            if response.status_code < 400:
                await self.audit_logger.log_request_success(
                    context.endpoint,
                    context.user_id,
                    context.source_ip,
                    response.status_code
                )
            
            # Update session if applicable
            if context.session_id and context.user_id:
                await self._update_session(context)
            
        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")

    async def _add_security_headers(
        self,
        response: Response,
        context: SecurityContext
    ) -> None:
        """Add security headers to response"""
        try:
            # Standard security headers
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
                "X-Request-ID": context.request_id,
                "X-Security-Level": context.security_level.value
            }
            
            # Content Security Policy
            if context.endpoint.startswith('/api/'):
                security_headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none';"
                )
            
            # Add headers to response
            for header, value in security_headers.items():
                response.headers[header] = value
            
        except Exception as e:
            logger.error(f"Failed to add security headers: {str(e)}")

    async def _update_session(self, context: SecurityContext) -> None:
        """Update user session information"""
        try:
            session_key = f"session:{context.session_id}"
            session_data = {
                'user_id': context.user_id,
                'last_activity': datetime.utcnow().isoformat(),
                'ip_address': context.source_ip,
                'user_agent': context.user_agent
            }
            
            if self.redis_client:
                await self.redis_client.setex(
                    session_key,
                    self.config.session_timeout,
                    json.dumps(session_data)
                )
            else:
                self.active_sessions[context.session_id] = session_data
            
        except Exception as e:
            logger.error(f"Session update failed: {str(e)}")

    async def add_security_rule(self, rule: SecurityRule) -> bool:
        """Add a new security rule"""
        try:
            self.security_rules[rule.rule_id] = rule
            
            logger.info(f"Security rule added: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add security rule: {str(e)}")
            return False

    async def block_ip(self, ip_address: str, reason: str) -> bool:
        """Block an IP address"""
        try:
            self.blocked_ips.add(ip_address)
            
            # Log blocking event
            await self.audit_logger.log_ip_blocked(ip_address, reason)
            
            logger.info(f"IP blocked: {ip_address} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to block IP: {str(e)}")
            return False

    async def unblock_ip(self, ip_address: str) -> bool:
        """Unblock an IP address"""
        try:
            self.blocked_ips.discard(ip_address)
            
            # Log unblocking event
            await self.audit_logger.log_ip_unblocked(ip_address)
            
            logger.info(f"IP unblocked: {ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unblock IP: {str(e)}")
            return False

    def get_security_status(self) -> Dict[str, Any]:
        """Get security middleware status"""
        return {
            "blocked_ips_count": len(self.blocked_ips),
            "security_rules_count": len(self.security_rules),
            "active_sessions_count": len(self.active_sessions),
            "rate_limiting_enabled": self.config.enable_rate_limiting,
            "threat_detection_enabled": self.config.enable_threat_detection,
            "ip_blocking_enabled": self.config.enable_ip_blocking,
            "geo_blocking_enabled": self.config.enable_geo_blocking,
            "metrics": self.metrics.get_summary()
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get security capabilities"""
        return {
            "threat_types": [tt.value for tt in ThreatType],
            "security_levels": [sl.value for sl in SecurityLevel],
            "action_types": [at.value for at in ActionType],
            "protections": {
                "rate_limiting": self.config.enable_rate_limiting,
                "threat_detection": self.config.enable_threat_detection,
                "ip_blocking": self.config.enable_ip_blocking,
                "geo_blocking": self.config.enable_geo_blocking,
                "sql_injection_protection": self.config.enable_sql_injection_protection,
                "xss_protection": self.config.enable_xss_protection,
                "csrf_protection": self.config.enable_csrf_protection,
                "user_agent_filtering": self.config.enable_user_agent_filtering
            },
            "features": [
                "real_time_blocking",
                "threat_scoring",
                "audit_logging",
                "session_management",
                "security_headers",
                "content_security_policy",
                "rate_limiting",
                "geo_filtering"
            ]
        }))))

# File has syntax issues - needs manual review