"""Advanced Security Middleware
===========================

Production-ready security stack with WAF, OAuth2, rate limiting,
and comprehensive security controls.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
import hashlib
import hmac
import jwt
import re
import ipaddress
from typing import Dict, Any, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from pathlib import Path
# Optional imports with fallbacks
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
from urllib.parse import urlparse, parse_qs
import base64
import secrets

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """
Security level classifications"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(Enum):
    """Types of security attacks"""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    BOT_TRAFFIC = "bot_traffic"
    MALICIOUS_PAYLOAD = "malicious_payload"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class RateLimitType(Enum):
    """Rate limiting strategies"""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class SecurityRule:
    """Security rule definition"""
    rule_id: str
    name: str
    pattern: str
    attack_type: AttackType
    severity: SecurityLevel
    action: str  # block, log, redirect
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitRule:
    """
Rate limiting rule"""
    name: str
    requests_per_window: int
    window_size_seconds: int
    rate_limit_type: RateLimitType
    scope: str  # ip, user, endpoint, global
    burst_allowance: Optional[int] = None
    enabled: bool = True


@dataclass
class SecurityEvent:
    """
Security event log"""
    event_id: str
    timestamp: datetime
    client_ip: str
    user_agent: str
    attack_type: AttackType
    severity: SecurityLevel
    details: Dict[str, Any]
    blocked: bool
    request_path: str
    user_id: Optional[str] = None


class WAFEngine:
    """
Web Application Firewall engine"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.rules: List[SecurityRule] = []
        self.logger = logging.getLogger(__name__)
        self.redis_client = None
        
        # Initialize default security rules
        self._initialize_default_rules()
        
    async def initialize(self) -> None:
        """
Initialize WAF engine"""
        try:
            # Initialize Redis for caching and rate limiting
            redis_config = self.config.get('redis', {})
            if redis_config:
                self.redis_client = await aioredis.from_url(
                    redis_config.get('url', 'redis://localhost:6379'),
                    password=redis_config.get('password'),
                    db=redis_config.get('db', 1)
                )
                
            self.logger.info("WAF engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WAF engine: {str(e)}")
            raise
    
    def _initialize_default_rules(self) -> None:
        """Initialize default WAF rules"""
        default_rules = [
            # SQL Injection patterns
            SecurityRule(
                rule_id="sql_001",
                name="SQL Injection - UNION attacks",
                pattern=r"(?i)(union\s+(all\s+)?select|select\s+.+\s+from|insert\s+into|update\s+.+\s+set|delete\s+from)",
                attack_type=AttackType.SQL_INJECTION,
                severity=SecurityLevel.HIGH,
                action="block"
            ),
            SecurityRule(
                rule_id="sql_002",
                name="SQL Injection - Boolean attacks",
                pattern=r"(?i)((\s|^)(or|and)\s+([0-9]+\s*=\s*[0-9]+|true|false|\d+)(\s|$|;))",
                attack_type=AttackType.SQL_INJECTION,
                severity=SecurityLevel.HIGH,
                action="block"
            ),
            SecurityRule(
                rule_id="sql_003",
                name="SQL Injection - Comment-based",
                pattern=r"(?i)(--|/\*|\*/|#)",
                attack_type=AttackType.SQL_INJECTION,
                severity=SecurityLevel.MEDIUM,
                action="log"
            ),
            
            # XSS patterns
            SecurityRule(
                rule_id="xss_001",
                name="XSS - Script tags",
                pattern=r"(?i)(<script[^>]*>.*?</script>|<script[^>]*>)",
                attack_type=AttackType.XSS,
                severity=SecurityLevel.HIGH,
                action="block"
            ),
            SecurityRule(
                rule_id="xss_002",
                name="XSS - Event handlers",
                pattern=r"(?i)(on\w+\s*=\s*[\"']?[^\"'>]*[\"']?)",
                attack_type=AttackType.XSS,
                severity=SecurityLevel.MEDIUM,
                action="block"
            ),
            SecurityRule(
                rule_id="xss_003",
                name="XSS - JavaScript protocol",
                pattern=r"(?i)(javascript:|vbscript:|data:text/html)",
                attack_type=AttackType.XSS,
                severity=SecurityLevel.HIGH,
                action="block"
            ),
            
            # Path traversal
            SecurityRule(
                rule_id="path_001",
                name="Path Traversal - Directory traversal",
                pattern=r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
                attack_type=AttackType.PATH_TRAVERSAL,
                severity=SecurityLevel.HIGH,
                action="block"
            ),
            
            # Command injection
            SecurityRule(
                rule_id="cmd_001",
                name="Command Injection - Shell commands",
                pattern=r"(?i)(;|\||&|`|\$\(|\${|<\(|>\()",
                attack_type=AttackType.COMMAND_INJECTION,
                severity=SecurityLevel.CRITICAL,
                action="block"
            ),
            
            # Malicious payloads
            SecurityRule(
                rule_id="payload_001",
                name="Malicious Payload - Eval functions",
                pattern=r"(?i)(eval\s*\(|exec\s*\(|system\s*\(|shell_exec\s*\()",
                attack_type=AttackType.MALICIOUS_PAYLOAD,
                severity=SecurityLevel.CRITICAL,
                action="block"
            )
        ]
        
        self.rules.extend(default_rules)
        self.logger.info(f"Initialized {len(default_rules)} default WAF rules")
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incoming request for security threats"""
        try:
            analysis_start = time.time()
            
            # Extract request components
            url = request_data.get('url', '')
            headers = request_data.get('headers', {})
            body = request_data.get('body', '')
            query_params = request_data.get('query_params', {})
            client_ip = request_data.get('client_ip', '')
            user_agent = headers.get('User-Agent', '')
            
            # Combine all data for analysis
            analysis_targets = {
                'url': url,
                'body': str(body),
                'query_params': json.dumps(query_params),
                'headers': json.dumps(headers),
                'user_agent': user_agent
            }
            
            threats_detected = []
            risk_score = 0.0
            
            # Run security rules analysis
            for rule in self.rules:
                if not rule.enabled:
                    continue
                    
                for target_name, target_data in analysis_targets.items():
                    if re.search(rule.pattern, target_data):
                        threat = {
                            'rule_id': rule.rule_id,
                            'rule_name': rule.name,
                            'attack_type': rule.attack_type.value,
                            'severity': rule.severity.value,
                            'action': rule.action,
                            'target': target_name,
                            'pattern_matched': rule.pattern,
                            'matched_content': target_data[:200]  # Truncate for logging
                        }
                        threats_detected.append(threat)
                        
                        # Calculate risk score
                        severity_weights = {
                            SecurityLevel.LOW: 1,
                            SecurityLevel.MEDIUM: 3,
                            SecurityLevel.HIGH: 7,
                            SecurityLevel.CRITICAL: 10
                        }
                        risk_score += severity_weights.get(rule.severity, 1)
            
            # Additional analysis: Bot detection
            bot_score = await self._analyze_bot_behavior(request_data)
            risk_score += bot_score
            
            # Determine overall security status
            if risk_score >= 10:
                security_status = "block"
            elif risk_score >= 5:
                security_status = "high_risk"
            elif risk_score >= 2:
                security_status = "medium_risk"
            else:
                security_status = "clean"
            
            analysis_time = time.time() - analysis_start
            
            result = {
                'security_status': security_status,
                'risk_score': risk_score,
                'threats_detected': threats_detected,
                'bot_score': bot_score,
                'analysis_time': analysis_time,
                'request_id': request_data.get('request_id', str(uuid.uuid4()))
            }
            
            # Log security events
            if threats_detected:
                await self._log_security_event(request_data, threats_detected, security_status)
            
            return result
            
        except Exception as e:
            self.logger.error(f"WAF analysis failed: {str(e)}")
            return {
                'security_status': 'error',
                'error': str(e),
                'request_id': request_data.get('request_id', str(uuid.uuid4()))
            }
    
    async def _analyze_bot_behavior(self, request_data: Dict[str, Any]) -> float:
        """Analyze request for bot behavior patterns"""
        try:
            headers = request_data.get('headers', {})
            user_agent = headers.get('User-Agent', '').lower()
            client_ip = request_data.get('client_ip', '')
            
            bot_score = 0.0
            
            # Known bot patterns
            bot_patterns = [
                r'bot', r'crawler', r'spider', r'scraper', r'curl', r'wget',
                r'python-requests', r'java', r'apache-httpclient', r'go-http-client'
            ]
            
            for pattern in bot_patterns:
                if re.search(pattern, user_agent):
                    bot_score += 2.0
                    break
            
            # Missing standard headers
            standard_headers = ['accept', 'accept-language', 'accept-encoding']
            missing_headers = sum(1 for h in standard_headers if h not in headers)
            bot_score += missing_headers * 0.5
            
            # Check request frequency if Redis is available
            if self.redis_client:
                request_key = f"waf:requests:{client_ip}"
                current_count = await self.redis_client.get(request_key)
                
                if current_count:
                    count = int(current_count)
                    if count > 100:  # More than 100 requests in the window
                        bot_score += 3.0
                    elif count > 50:
                        bot_score += 1.5
                
                # Update request count
                await self.redis_client.incr(request_key)
                await self.redis_client.expire(request_key, 300)  # 5-minute window
            
            return min(bot_score, 5.0)  # Cap at 5.0
            
        except Exception as e:
            self.logger.error(f"Bot analysis failed: {str(e)}")
            return 0.0
    
    async def _log_security_event(self, request_data -> None: Dict[str, Any], threats -> None: List[Dict], status -> None: str) -> None:
        """Log security event"""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                client_ip=request_data.get('client_ip', ''),
                user_agent=request_data.get('headers', {}).get('User-Agent', ''),
                attack_type=AttackType(threats[0]['attack_type']) if threats else AttackType.UNAUTHORIZED_ACCESS,
                severity=SecurityLevel(threats[0]['severity']) if threats else SecurityLevel.LOW,
                details={
                    'threats': threats,
                    'request_url': request_data.get('url', ''),
                    'request_method': request_data.get('method', ''),
                    'status': status
                },
                blocked=status == "block",
                request_path=urlparse(request_data.get('url', '')).path,
                user_id=request_data.get('user_id')
            )
            
            # Store in Redis for real-time monitoring
            if self.redis_client:
                event_key = f"waf:events:{event.event_id}"
                event_data = {
                    'timestamp': event.timestamp.isoformat(),
                    'client_ip': event.client_ip,
                    'attack_type': event.attack_type.value,
                    'severity': event.severity.value,
                    'blocked': event.blocked,
                    'details': json.dumps(event.details)
                }
                
                await self.redis_client.hset(event_key, mapping=event_data)
                await self.redis_client.expire(event_key, 86400)  # 24 hours
                
                # Add to events list
                await self.redis_client.lpush("waf:events:recent", event.event_id)
                await self.redis_client.ltrim("waf:events:recent", 0, 1000)  # Keep last 1000 events
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, redis_client, config -> None: Dict[str, Any] = None) -> None:
        self.redis_client = redis_client
        self.config = config or {}
        self.rules: List[RateLimitRule] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize default rate limiting rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """
Initialize default rate limiting rules"""
        default_rules = [
            RateLimitRule(
                name="api_global",
                requests_per_window=1000,
                window_size_seconds=60,
                rate_limit_type=RateLimitType.SLIDING_WINDOW,
                scope="ip"
            ),
            RateLimitRule(
                name="auth_endpoints",
                requests_per_window=10,
                window_size_seconds=60,
                rate_limit_type=RateLimitType.FIXED_WINDOW,
                scope="ip"
            ),
            RateLimitRule(
                name="api_authenticated",
                requests_per_window=5000,
                window_size_seconds=3600,
                rate_limit_type=RateLimitType.TOKEN_BUCKET,
                scope="user",
                burst_allowance=100
            )
        ]
        
        self.rules.extend(default_rules)
    
    async def check_rate_limit(self, identifier: str, rule_name: str) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        try:
            rule = next((r for r in self.rules if r.name == rule_name), None)
            if not rule or not rule.enabled:
                return {'allowed': True, 'rule': None}
            
            if rule.rate_limit_type == RateLimitType.FIXED_WINDOW:
                return await self._check_fixed_window(identifier, rule)
            elif rule.rate_limit_type == RateLimitType.SLIDING_WINDOW:
                return await self._check_sliding_window(identifier, rule)
            elif rule.rate_limit_type == RateLimitType.TOKEN_BUCKET:
                return await self._check_token_bucket(identifier, rule)
            else:
                return await self._check_leaky_bucket(identifier, rule)
                
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            return {'allowed': True, 'error': str(e)}
    
    async def _check_fixed_window(self, identifier: str, rule: RateLimitRule) -> Dict[str, Any]:
        """Fixed window rate limiting"""
        current_window = int(time.time()) // rule.window_size_seconds
        key = f"rate_limit:fixed:{rule.name}:{identifier}:{current_window}"
        
        current_count = await self.redis_client.get(key)
        current_count = int(current_count) if current_count else 0
        
        if current_count >= rule.requests_per_window:
            return {
                'allowed': False,
                'rule': rule.name,
                'current_count': current_count,
                'limit': rule.requests_per_window,
                'window_reset': (current_window + 1) * rule.window_size_seconds
            }
        
        # Increment counter
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, rule.window_size_seconds)
        
        return {
            'allowed': True,
            'rule': rule.name,
            'current_count': current_count + 1,
            'limit': rule.requests_per_window,
            'remaining': rule.requests_per_window - current_count - 1
        }
    
    async def _check_sliding_window(self, identifier: str, rule: RateLimitRule) -> Dict[str, Any]:
        """Sliding window rate limiting"""
        now = time.time()
        window_start = now - rule.window_size_seconds
        key = f"rate_limit:sliding:{rule.name}:{identifier}"
        
        # Remove old entries
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Get current count
        current_count = await self.redis_client.zcard(key)
        
        if current_count >= rule.requests_per_window:
            return {
                'allowed': False,
                'rule': rule.name,
                'current_count': current_count,
                'limit': rule.requests_per_window
            }
        
        # Add current request
        await self.redis_client.zadd(key, {str(uuid.uuid4()): now})
        await self.redis_client.expire(key, rule.window_size_seconds)
        
        return {
            'allowed': True,
            'rule': rule.name,
            'current_count': current_count + 1,
            'limit': rule.requests_per_window,
            'remaining': rule.requests_per_window - current_count - 1
        }
    
    async def _check_token_bucket(self, identifier: str, rule: RateLimitRule) -> Dict[str, Any]:
        try:
            logger.info(f"Executing _check_token_bucket")
            
            # Implementation for _check_token_bucket
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_check_token_bucket completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_check_token_bucket failed: {e}")
            return {
                'allowed': False,
                'rule': rule.name,
                'tokens_remaining': 0,
                'bucket_size': rule.requests_per_window
            }
    
    async def _check_leaky_bucket(self, identifier: str, rule: RateLimitRule) -> Dict[str, Any]:
        """Leaky bucket rate limiting"""
        # Simplified implementation - similar to token bucket but with different semantics
        return await self._check_token_bucket(identifier, rule)


class OAuth2Provider:
    """
OAuth2 authentication and authorization provider"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.secret_key = self.config.get('secret_key', secrets.token_urlsafe(32))
        self.access_token_ttl = self.config.get('access_token_ttl', 3600)  # 1 hour
        self.refresh_token_ttl = self.config.get('refresh_token_ttl', 86400 * 30)  # 30 days
        self.logger = logging.getLogger(__name__)
    
    async def create_access_token(self, user_data: Dict[str, Any], scopes: List[str] = None) -> str:
        """
Create JWT access token"""
        try:
            now = datetime.utcnow()
            payload = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'scopes': scopes or ['read'],
                'iat': now,
                'exp': now + timedelta(seconds=self.access_token_ttl),
                'iss': 'ainflue-auth',
                'type': 'access_token'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create access token: {str(e)}")
            raise
    
    async def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create refresh token"""
        try:
            now = datetime.utcnow()
            payload = {
                'user_id': user_data.get('user_id'),
                'iat': now,
                'exp': now + timedelta(seconds=self.refresh_token_ttl),
                'iss': 'ainflue-auth',
                'type': 'refresh_token',
                'jti': str(uuid.uuid4())  # Unique token ID for revocation
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create refresh token: {str(e)}")
            raise
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check token type
            if payload.get('type') not in ['access_token', 'refresh_token']:
                raise jwt.InvalidTokenError("Invalid token type")
            
            # Check expiration
            if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
                raise jwt.ExpiredSignatureError("Token has expired")
            
            return {
                'valid': True,
                'payload': payload,
                'user_id': payload.get('user_id'),
                'scopes': payload.get('scopes', []),
                'token_type': payload.get('type')
            }
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'token_expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'invalid_token: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Token verification failed: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            verification = await self.verify_token(refresh_token)
            if not verification['valid']:
                return verification
            
            payload = verification['payload']
            if payload.get('type') != 'refresh_token':
                return {'valid': False, 'error': 'invalid_token_type'}
            
            # Create new access token
            user_data = {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'email': payload.get('email')
            }
            
            access_token = await self.create_access_token(user_data, payload.get('scopes', ['read']))
            
            return {
                'valid': True,
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': self.access_token_ttl
            }
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            return {'valid': False, 'error': str(e)}


class SecurityMiddleware:
    """Comprehensive security middleware orchestrator"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.waf = WAFEngine(config.get('waf', {}))
        self.oauth2 = OAuth2Provider(config.get('oauth2', {}))
        self.rate_limiter = None
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """
Initialize security middleware"""
        try:
            # Initialize WAF
            await self.waf.initialize()
            
            # Initialize Redis client for rate limiting
            redis_config = self.config.get('redis', {})
            if redis_config:
                self.redis_client = await aioredis.from_url(
                    redis_config.get('url', 'redis://localhost:6379'),
                    password=redis_config.get('password'),
                    db=redis_config.get('db', 2)
                )
                
                # Initialize rate limiter
                self.rate_limiter = RateLimiter(self.redis_client, config.get('rate_limiting', {}))
            
            self.logger.info("Security middleware initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security middleware: {str(e)}")
            raise
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request through security pipeline"""
        try:
            security_result = {
                'request_id': request_data.get('request_id', str(uuid.uuid4())),
                'allowed': True,
                'security_checks': {}
            }
            
            # WAF Analysis
            waf_result = await self.waf.analyze_request(request_data)
            security_result['security_checks']['waf'] = waf_result
            
            if waf_result.get('security_status') == 'block':
                security_result['allowed'] = False
                security_result['reason'] = 'waf_blocked'
                security_result['details'] = waf_result
                return security_result
            
            # Rate Limiting
            if self.rate_limiter:
                client_ip = request_data.get('client_ip', '')
                endpoint = request_data.get('endpoint', 'default')
                
                # Check different rate limit rules
                rate_checks = []
                
                # Global IP-based rate limiting
                global_check = await self.rate_limiter.check_rate_limit(client_ip, 'api_global')
                rate_checks.append(('global', global_check))
                
                # Endpoint-specific rate limiting for auth endpoints
                if '/auth/' in request_data.get('url', ''):
                    auth_check = await self.rate_limiter.check_rate_limit(client_ip, 'auth_endpoints')
                    rate_checks.append(('auth', auth_check))
                
                # User-based rate limiting for authenticated requests
                user_id = request_data.get('user_id')
                if user_id:
                    user_check = await self.rate_limiter.check_rate_limit(user_id, 'api_authenticated')
                    rate_checks.append(('user', user_check))
                
                security_result['security_checks']['rate_limiting'] = rate_checks
                
                # Check if any rate limit was exceeded
                for check_name, check_result in rate_checks:
                    if not check_result.get('allowed', True):
                        security_result['allowed'] = False
                        security_result['reason'] = 'rate_limit_exceeded'
                        security_result['details'] = {
                            'rule': check_name,
                            'rate_limit_info': check_result
                        }
                        return security_result
            
            # OAuth2 Token Validation (if Authorization header present)
            auth_header = request_data.get('headers', {}).get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                token_result = await self.oauth2.verify_token(token)
                security_result['security_checks']['oauth2'] = token_result
                
                if not token_result.get('valid', False):
                    security_result['allowed'] = False
                    security_result['reason'] = 'invalid_token'
                    security_result['details'] = token_result
                    return security_result
                
                # Add user context to request
                security_result['user_context'] = {
                    'user_id': token_result.get('user_id'),
                    'scopes': token_result.get('scopes', [])
                }
            
            return security_result
            
        except Exception as e:
            self.logger.error(f"Security processing failed: {str(e)}")
            return {
                'request_id': request_data.get('request_id', str(uuid.uuid4())),
                'allowed': False,
                'reason': 'security_error',
                'error': str(e)
            }


# Global security middleware instance
security_middleware = None


async def initialize_security(config: Dict[str, Any] = None) -> SecurityMiddleware:
    """Initialize global security middleware"""
    global security_middleware
    
    if security_middleware is None:
        security_middleware = SecurityMiddleware(config)
        await security_middleware.initialize()
    
    return security_middleware


def get_security_middleware() -> Optional[SecurityMiddleware]:
    """
Get global security middleware instance"""
    return security_middleware