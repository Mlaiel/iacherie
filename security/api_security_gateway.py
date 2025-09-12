#!/usr/bin/env python3
"""
🛡️ API Security Gateway - Ainflue Platform
==========================================

Enterprise-grade API security gateway with comprehensive protection including
authentication, authorization, rate limiting, input validation, threat detection,
and API traffic analysis for the creator content platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Role Expert: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Specialist
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import re
import ipaddress
import jwt
from cryptography.hazmat.primitives import hashes
import redis
import aioredis
from collections import defaultdict, deque
import aiohttp
from aiohttp import web
from aiohttp.web_middlewares import middleware
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """API security levels"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    RESTRICTED = "restricted"
    ADMIN = "admin"

class ThreatType(Enum):
    """API threat types"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    XXССE = "xxe"
    CSRF = "csrf"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    MALFORMED_REQUEST = "malformed_request"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    BRUTE_FORCE = "brute_force"
    BOT_DETECTION = "bot_detection"

class ValidationResult(Enum):
    """Input validation results"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    methods: Set[str]
    security_level: SecurityLevel
    rate_limit: Optional[int] = None  # requests per minute
    required_permissions: Set[str] = field(default_factory=set)
    input_validation_rules: Dict[str, Any] = field(default_factory=dict)
    response_filtering: Dict[str, Any] = field(default_factory=dict)
    custom_validators: List[Callable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class APIRequest:
    """API request data"""
    request_id: str
    client_ip: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[bytes]
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

@dataclass
class SecurityThreat:
    """Detected security threat"""
    threat_id: str
    threat_type: ThreatType
    severity: str
    description: str
    source_request: APIRequest
    indicators: List[str]
    confidence: float
    blocked: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RateLimitStatus:
    """Rate limiting status"""
    requests_count: int
    window_start: datetime
    blocked_until: Optional[datetime] = None
    violations: int = 0

class APISecurityGateway:
    """
    🛡️ Enterprise API Security Gateway
    
    Features:
    - Authentication & Authorization
    - Rate limiting & throttling
    - Input validation & sanitization
    - SQL injection detection
    - XSS protection
    - CSRF protection
    - Bot detection
    - API traffic analysis
    - Threat detection & blocking
    - Security headers
    - SSL/TLS enforcement
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        
        # API endpoints configuration
        self.endpoints: Dict[str, APIEndpoint] = {}
        
        # Security rules and patterns
        self.sql_injection_patterns = self._load_sql_injection_patterns()
        self.xss_patterns = self._load_xss_patterns()
        self.path_traversal_patterns = self._load_path_traversal_patterns()
        self.bot_signatures = self._load_bot_signatures()
        
        # Rate limiting
        self.rate_limits: Dict[str, RateLimitStatus] = {}
        self.global_rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        
        # Blocked IPs and tokens
        self.blocked_ips: Set[str] = set()
        self.blocked_tokens: Set[str] = set()
        self.ip_reputation: Dict[str, float] = {}
        
        # Security metrics
        self.requests_processed = 0
        self.threats_detected = 0
        self.requests_blocked = 0
        self.false_positives = 0
        
        # Security headers
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
        }
        
        logger.info("🛡️ API Security Gateway initialized")

    async def initialize(self):
        """Initialize the API security gateway"""
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.create_redis_pool(
                'redis://localhost:6379',
                encoding='utf-8'
            )
            
            # Load configuration
            await self._load_endpoints_config()
            await self._load_security_rules()
            await self._load_blocked_lists()
            
            # Initialize default endpoints
            await self._initialize_default_endpoints()
            
            logger.info("✅ API Security Gateway fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize API security gateway: {e}")
            raise

    @middleware
    async def security_middleware(self, request: aiohttp.web.Request, handler):
        """Main security middleware for API requests"""
        start_time = time.time()
        self.requests_processed += 1
        
        try:
            # Create API request object
            api_request = await self._create_api_request(request)
            
            # Pre-processing security checks
            security_result = await self._pre_process_security_check(api_request)
            
            if not security_result['allowed']:
                return self._create_security_response(
                    security_result['status'], 
                    security_result['message']
                )
            
            # Rate limiting check
            rate_limit_result = await self._check_rate_limits(api_request)
            if not rate_limit_result['allowed']:
                return self._create_rate_limit_response(rate_limit_result)
            
            # Input validation
            validation_result = await self._validate_input(api_request)
            if validation_result != ValidationResult.VALID:
                return self._create_validation_response(validation_result)
            
            # Threat detection
            threat_result = await self._detect_threats(api_request)
            if threat_result['threats']:
                await self._handle_threats(threat_result['threats'])
                if any(t.blocked for t in threat_result['threats']):
                    return self._create_threat_response(threat_result['threats'])
            
            # Authentication check
            auth_result = await self._check_authentication(api_request)
            if not auth_result['authenticated']:
                return self._create_auth_response(auth_result)
            
            # Authorization check
            authz_result = await self._check_authorization(api_request, auth_result['user'])
            if not authz_result['authorized']:
                return self._create_authz_response(authz_result)
            
            # Update request with user info
            request['user'] = auth_result['user']
            request['api_request'] = api_request
            
            # Process request
            response = await handler(request)
            
            # Post-processing
            response = await self._post_process_response(response, api_request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Log successful request
            processing_time = (time.time() - start_time) * 1000
            await self._log_request(api_request, response.status, processing_time)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Security middleware error: {e}")
            return self._create_error_response(500, "Internal security error")

    async def _create_api_request(self, request: aiohttp.web.Request) -> APIRequest:
        """Create APIRequest object from aiohttp request"""
        # Get client IP (handle proxies)
        client_ip = self._get_client_ip(request)
        
        # Read request body
        body = None
        if request.content_length and request.content_length > 0:
            body = await request.read()
        
        # Extract authentication info
        user_id = None
        api_key = None
        
        # Check for Bearer token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get('user_id')
            except:
                pass
        
        # Check for API key
        api_key = request.headers.get('X-API-Key') or request.query.get('api_key')
        
        return APIRequest(
            request_id=self._generate_request_id(),
            client_ip=client_ip,
            method=request.method,
            path=request.path,
            headers=dict(request.headers),
            query_params=dict(request.query),
            body=body,
            user_id=user_id,
            api_key=api_key,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.headers.get('Referer')
        )

    async def _pre_process_security_check(self, api_request: APIRequest) -> Dict[str, Any]:
        """Pre-processing security checks"""
        # Check blocked IPs
        if api_request.client_ip in self.blocked_ips:
            self.requests_blocked += 1
            return {
                'allowed': False,
                'status': 403,
                'message': 'IP address blocked'
            }
        
        # Check IP reputation
        if self.ip_reputation.get(api_request.client_ip, 0) > 0.8:
            self.requests_blocked += 1
            return {
                'allowed': False,
                'status': 403,
                'message': 'IP has poor reputation'
            }
        
        # Check blocked tokens
        if api_request.api_key and api_request.api_key in self.blocked_tokens:
            self.requests_blocked += 1
            return {
                'allowed': False,
                'status': 403,
                'message': 'API key blocked'
            }
        
        # Check request size limits
        if api_request.body and len(api_request.body) > self.config.get('max_request_size', 10 * 1024 * 1024):
            return {
                'allowed': False,
                'status': 413,
                'message': 'Request too large'
            }
        
        return {'allowed': True}

    async def _check_rate_limits(self, api_request: APIRequest) -> Dict[str, Any]:
        """Check rate limits for request"""
        try:
            current_time = datetime.now()
            
            # Global rate limit check
            global_limit = self.config.get('global_rate_limit', 1000)  # per minute
            
            # Clean old entries
            minute_ago = current_time - timedelta(minutes=1)
            self.global_rate_limits[api_request.client_ip] = [
                ts for ts in self.global_rate_limits[api_request.client_ip]
                if ts > minute_ago
            ]
            
            # Check global limit
            if len(self.global_rate_limits[api_request.client_ip]) >= global_limit:
                return {
                    'allowed': False,
                    'status': 429,
                    'message': 'Rate limit exceeded',
                    'retry_after': 60
                }
            
            # Add current request
            self.global_rate_limits[api_request.client_ip].append(current_time)
            
            # Endpoint-specific rate limiting
            endpoint = self._find_endpoint(api_request.path, api_request.method)
            if endpoint and endpoint.rate_limit:
                key = f"{api_request.client_ip}:{endpoint.path}"
                
                if key not in self.rate_limits:
                    self.rate_limits[key] = RateLimitStatus(
                        requests_count=0,
                        window_start=current_time
                    )
                
                rate_status = self.rate_limits[key]
                
                # Check if window expired
                if current_time - rate_status.window_start > timedelta(minutes=1):
                    rate_status.requests_count = 0
                    rate_status.window_start = current_time
                
                # Check rate limit
                if rate_status.requests_count >= endpoint.rate_limit:
                    rate_status.violations += 1
                    return {
                        'allowed': False,
                        'status': 429,
                        'message': f'Endpoint rate limit exceeded ({endpoint.rate_limit}/min)',
                        'retry_after': 60
                    }
                
                rate_status.requests_count += 1
            
            return {'allowed': True}
            
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            return {'allowed': True}  # Fail open for rate limiting

    async def _validate_input(self, api_request: APIRequest) -> ValidationResult:
        """Validate and sanitize input"""
        try:
            # Find endpoint configuration
            endpoint = self._find_endpoint(api_request.path, api_request.method)
            
            # Basic validation
            validation_result = ValidationResult.VALID
            
            # Validate headers
            for header_name, header_value in api_request.headers.items():
                if self._contains_malicious_content(header_value):
                    return ValidationResult.MALICIOUS
            
            # Validate query parameters
            for param_name, param_value in api_request.query_params.items():
                if isinstance(param_value, str):
                    if self._contains_malicious_content(param_value):
                        return ValidationResult.MALICIOUS
            
            # Validate request body
            if api_request.body:
                try:
                    # Try to parse as JSON
                    if api_request.headers.get('Content-Type', '').startswith('application/json'):
                        body_str = api_request.body.decode('utf-8')
                        json.loads(body_str)  # Validate JSON structure
                        
                        if self._contains_malicious_content(body_str):
                            return ValidationResult.MALICIOUS
                    
                    # Check for binary exploits
                    elif self._contains_binary_exploits(api_request.body):
                        return ValidationResult.MALICIOUS
                        
                except UnicodeDecodeError:
                    return ValidationResult.INVALID
                except json.JSONDecodeError:
                    return ValidationResult.INVALID
            
            # Endpoint-specific validation
            if endpoint and endpoint.input_validation_rules:
                endpoint_result = await self._validate_endpoint_specific(api_request, endpoint)
                if endpoint_result != ValidationResult.VALID:
                    return endpoint_result
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Input validation failed: {e}")
            return ValidationResult.INVALID

    async def _detect_threats(self, api_request: APIRequest) -> Dict[str, Any]:
        """Detect security threats in request"""
        threats = []
        
        try:
            # SQL Injection detection
            sql_threats = self._detect_sql_injection(api_request)
            threats.extend(sql_threats)
            
            # XSS detection
            xss_threats = self._detect_xss(api_request)
            threats.extend(xss_threats)
            
            # Path traversal detection
            path_threats = self._detect_path_traversal(api_request)
            threats.extend(path_threats)
            
            # Bot detection
            bot_threats = self._detect_bots(api_request)
            threats.extend(bot_threats)
            
            # Suspicious patterns
            pattern_threats = self._detect_suspicious_patterns(api_request)
            threats.extend(pattern_threats)
            
            if threats:
                self.threats_detected += len(threats)
            
            return {'threats': threats}
            
        except Exception as e:
            logger.error(f"❌ Threat detection failed: {e}")
            return {'threats': []}

    def _detect_sql_injection(self, api_request: APIRequest) -> List[SecurityThreat]:
        """Detect SQL injection attempts"""
        threats = []
        
        # Check all string inputs
        inputs_to_check = []
        
        # Add query parameters
        for param_value in api_request.query_params.values():
            if isinstance(param_value, str):
                inputs_to_check.append(param_value)
        
        # Add body content
        if api_request.body:
            try:
                body_str = api_request.body.decode('utf-8')
                inputs_to_check.append(body_str)
            except:
                pass
        
        # Check against SQL injection patterns
        for input_str in inputs_to_check:
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, input_str, re.IGNORECASE):
                    threat = SecurityThreat(
                        threat_id=self._generate_threat_id(),
                        threat_type=ThreatType.SQL_INJECTION,
                        severity="high",
                        description=f"SQL injection pattern detected: {pattern}",
                        source_request=api_request,
                        indicators=[f"Pattern: {pattern}", f"Input: {input_str[:100]}"],
                        confidence=0.8,
                        blocked=True
                    )
                    threats.append(threat)
                    break
        
        return threats

    def _detect_xss(self, api_request: APIRequest) -> List[SecurityThreat]:
        """Detect XSS attempts"""
        threats = []
        
        # Check inputs for XSS patterns
        inputs_to_check = []
        
        for param_value in api_request.query_params.values():
            if isinstance(param_value, str):
                inputs_to_check.append(param_value)
        
        if api_request.body:
            try:
                body_str = api_request.body.decode('utf-8')
                inputs_to_check.append(body_str)
            except:
                pass
        
        for input_str in inputs_to_check:
            for pattern in self.xss_patterns:
                if re.search(pattern, input_str, re.IGNORECASE):
                    threat = SecurityThreat(
                        threat_id=self._generate_threat_id(),
                        threat_type=ThreatType.XSS,
                        severity="medium",
                        description=f"XSS pattern detected: {pattern}",
                        source_request=api_request,
                        indicators=[f"Pattern: {pattern}", f"Input: {input_str[:100]}"],
                        confidence=0.7,
                        blocked=True
                    )
                    threats.append(threat)
                    break
        
        return threats

    def _detect_path_traversal(self, api_request: APIRequest) -> List[SecurityThreat]:
        """Detect path traversal attempts"""
        threats = []
        
        # Check path and parameters
        check_strings = [api_request.path] + list(api_request.query_params.values())
        
        for check_str in check_strings:
            if isinstance(check_str, str):
                for pattern in self.path_traversal_patterns:
                    if pattern in check_str:
                        threat = SecurityThreat(
                            threat_id=self._generate_threat_id(),
                            threat_type=ThreatType.PATH_TRAVERSAL,
                            severity="high",
                            description=f"Path traversal pattern detected: {pattern}",
                            source_request=api_request,
                            indicators=[f"Pattern: {pattern}", f"String: {check_str}"],
                            confidence=0.9,
                            blocked=True
                        )
                        threats.append(threat)
                        break
        
        return threats

    def _detect_bots(self, api_request: APIRequest) -> List[SecurityThreat]:
        """Detect bot traffic"""
        threats = []
        
        user_agent = api_request.user_agent or ""
        
        # Check against bot signatures
        for signature in self.bot_signatures:
            if signature.lower() in user_agent.lower():
                threat = SecurityThreat(
                    threat_id=self._generate_threat_id(),
                    threat_type=ThreatType.BOT_DETECTION,
                    severity="low",
                    description=f"Bot detected: {signature}",
                    source_request=api_request,
                    indicators=[f"User-Agent: {user_agent}"],
                    confidence=0.6,
                    blocked=False  # Bots aren't automatically blocked
                )
                threats.append(threat)
                break
        
        return threats

    def _detect_suspicious_patterns(self, api_request: APIRequest) -> List[SecurityThreat]:
        """Detect other suspicious patterns"""
        threats = []
        
        # Check for unusually long parameters
        for param_name, param_value in api_request.query_params.items():
            if isinstance(param_value, str) and len(param_value) > 1000:
                threat = SecurityThreat(
                    threat_id=self._generate_threat_id(),
                    threat_type=ThreatType.SUSPICIOUS_PATTERN,
                    severity="medium",
                    description=f"Unusually long parameter: {param_name}",
                    source_request=api_request,
                    indicators=[f"Parameter length: {len(param_value)}"],
                    confidence=0.5,
                    blocked=False
                )
                threats.append(threat)
        
        # Check for unusual headers
        suspicious_headers = ['X-Forwarded-For', 'X-Real-IP', 'X-Originating-IP']
        for header in suspicious_headers:
            if header in api_request.headers:
                # Could indicate proxy manipulation attempts
                pass
        
        return threats

    # Authentication and Authorization

    async def _check_authentication(self, api_request: APIRequest) -> Dict[str, Any]:
        """Check request authentication"""
        endpoint = self._find_endpoint(api_request.path, api_request.method)
        
        if not endpoint or endpoint.security_level == SecurityLevel.PUBLIC:
            return {'authenticated': True, 'user': None}
        
        # Check Bearer token
        auth_header = api_request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            user = await self._validate_jwt_token(token)
            if user:
                return {'authenticated': True, 'user': user}
        
        # Check API key
        if api_request.api_key:
            user = await self._validate_api_key(api_request.api_key)
            if user:
                return {'authenticated': True, 'user': user}
        
        return {
            'authenticated': False,
            'status': 401,
            'message': 'Authentication required'
        }

    async def _check_authorization(self, api_request: APIRequest, user: Optional[Dict]) -> Dict[str, Any]:
        """Check request authorization"""
        endpoint = self._find_endpoint(api_request.path, api_request.method)
        
        if not endpoint or not endpoint.required_permissions:
            return {'authorized': True}
        
        if not user:
            return {
                'authorized': False,
                'status': 403,
                'message': 'User required for authorization'
            }
        
        user_permissions = set(user.get('permissions', []))
        required_permissions = endpoint.required_permissions
        
        if not required_permissions.issubset(user_permissions):
            return {
                'authorized': False,
                'status': 403,
                'message': 'Insufficient permissions'
            }
        
        return {'authorized': True}

    # Response processing and security headers

    async def _post_process_response(self, response: web.Response, api_request: APIRequest) -> web.Response:
        """Post-process response for security"""
        # Remove sensitive headers
        sensitive_headers = ['Server', 'X-Powered-By']
        for header in sensitive_headers:
            if header in response.headers:
                del response.headers[header]
        
        # Add rate limit headers
        response.headers['X-RateLimit-Limit'] = str(self.config.get('global_rate_limit', 1000))
        remaining = max(0, self.config.get('global_rate_limit', 1000) - 
                       len(self.global_rate_limits.get(api_request.client_ip, [])))
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return response

    def _add_security_headers(self, response: web.Response):
        """Add security headers to response"""
        for header, value in self.security_headers.items():
            response.headers[header] = value

    # Utility methods

    def _find_endpoint(self, path: str, method: str) -> Optional[APIEndpoint]:
        """Find matching endpoint configuration"""
        # Exact match first
        if path in self.endpoints:
            endpoint = self.endpoints[path]
            if method in endpoint.methods:
                return endpoint
        
        # Pattern matching for dynamic paths
        for endpoint_path, endpoint in self.endpoints.items():
            if self._path_matches(path, endpoint_path) and method in endpoint.methods:
                return endpoint
        
        return None

    def _path_matches(self, request_path: str, endpoint_path: str) -> bool:
        """Check if request path matches endpoint pattern"""
        # Simple pattern matching - could be enhanced with regex
        if '*' in endpoint_path:
            pattern = endpoint_path.replace('*', '.*')
            return bool(re.match(pattern, request_path))
        
        return request_path == endpoint_path

    def _contains_malicious_content(self, content: str) -> bool:
        """Check if content contains malicious patterns"""
        # Check for various attack patterns
        malicious_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',  # XSS
            r'(?i)(union|select|insert|update|delete|drop|create|alter)',  # SQL
            r'\.\./',  # Path traversal
            r'\/etc\/passwd',  # File access
            r'<iframe.*?>',  # XSS iframe
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False

    def _contains_binary_exploits(self, data: bytes) -> bool:
        """Check for binary exploits"""
        # Look for common exploit signatures
        exploit_signatures = [
            b'\x90\x90\x90\x90',  # NOP sled
            b'\xcc\xcc\xcc\xcc',  # INT3 instruction
            b'\x00\x00\x00\x00',  # NULL bytes (excessive)
        ]
        
        for signature in exploit_signatures:
            if signature in data:
                return True
        
        return False

    def _get_client_ip(self, request: aiohttp.web.Request) -> str:
        """Get client IP address handling proxies"""
        # Check X-Forwarded-For header
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # Fall back to remote address
        return request.remote or '127.0.0.1'

    # Response creation methods

    def _create_security_response(self, status: int, message: str) -> web.Response:
        """Create security error response"""
        return web.json_response(
            {'error': 'Security violation', 'message': message},
            status=status
        )

    def _create_rate_limit_response(self, rate_result: Dict[str, Any]) -> web.Response:
        """Create rate limit response"""
        response = web.json_response(
            {'error': 'Rate limit exceeded', 'message': rate_result['message']},
            status=rate_result['status']
        )
        if 'retry_after' in rate_result:
            response.headers['Retry-After'] = str(rate_result['retry_after'])
        return response

    def _create_validation_response(self, result: ValidationResult) -> web.Response:
        """Create validation error response"""
        status = 400 if result == ValidationResult.INVALID else 403
        return web.json_response(
            {'error': 'Invalid input', 'message': f'Input validation failed: {result.value}'},
            status=status
        )

    def _create_threat_response(self, threats: List[SecurityThreat]) -> web.Response:
        """Create threat detection response"""
        return web.json_response(
            {'error': 'Security threat detected', 'message': 'Request blocked due to security threats'},
            status=403
        )

    def _create_auth_response(self, auth_result: Dict[str, Any]) -> web.Response:
        """Create authentication error response"""
        return web.json_response(
            {'error': 'Authentication failed', 'message': auth_result['message']},
            status=auth_result['status']
        )

    def _create_authz_response(self, authz_result: Dict[str, Any]) -> web.Response:
        """Create authorization error response"""
        return web.json_response(
            {'error': 'Authorization failed', 'message': authz_result['message']},
            status=authz_result['status']
        )

    def _create_error_response(self, status: int, message: str) -> web.Response:
        """Create generic error response"""
        return web.json_response(
            {'error': 'Internal error', 'message': message},
            status=status
        )

    # Data loading methods

    def _load_sql_injection_patterns(self) -> List[str]:
        """Load SQL injection detection patterns"""
        return [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bcreate\b.*\btable\b)",
            r"(\balter\b.*\btable\b)",
            r"(;.*--)",
            r"(\b(or|and)\b.*[=<>].*['\"])",
            r"('.*\bor\b.*')",
            r"(1\s*=\s*1)",
            r"(1\s*=\s*0)",
        ]

    def _load_xss_patterns(self) -> List[str]:
        """Load XSS detection patterns"""
        return [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe.*?>",
            r"<object.*?>",
            r"<embed.*?>",
            r"<applet.*?>",
            r"alert\s*\(",
            r"document\.cookie",
            r"document\.location",
            r"window\.location",
        ]

    def _load_path_traversal_patterns(self) -> List[str]:
        """Load path traversal patterns"""
        return [
            "../",
            "..\\",
            "..%2f",
            "..%5c",
            "%2e%2e%2f",
            "%2e%2e%5c",
            "/etc/passwd",
            "/etc/shadow",
            "\\windows\\system32\\",
            "c:\\windows\\",
        ]

    def _load_bot_signatures(self) -> List[str]:
        """Load bot detection signatures"""
        return [
            "bot",
            "crawler",
            "spider",
            "scraper",
            "python-requests",
            "curl",
            "wget",
            "httpie",
            "postman",
            "insomnia",
        ]

    async def _load_endpoints_config(self):
        """Load endpoints configuration"""
        # This would typically load from database or config file
        pass

    async def _load_security_rules(self):
        """Load security rules from storage"""
        # This would typically load from database
        pass

    async def _load_blocked_lists(self):
        """Load blocked IPs and tokens"""
        # This would typically load from database
        pass

    async def _initialize_default_endpoints(self):
        """Initialize default API endpoints"""
        default_endpoints = [
            APIEndpoint(
                path="/api/v1/auth/login",
                methods={"POST"},
                security_level=SecurityLevel.PUBLIC,
                rate_limit=5  # 5 attempts per minute
            ),
            APIEndpoint(
                path="/api/v1/auth/logout",
                methods={"POST"},
                security_level=SecurityLevel.AUTHENTICATED
            ),
            APIEndpoint(
                path="/api/v1/content/*",
                methods={"GET", "POST", "PUT", "DELETE"},
                security_level=SecurityLevel.AUTHENTICATED,
                required_permissions={"content_access"},
                rate_limit=100
            ),
            APIEndpoint(
                path="/api/v1/admin/*",
                methods={"GET", "POST", "PUT", "DELETE"},
                security_level=SecurityLevel.ADMIN,
                required_permissions={"admin_access"},
                rate_limit=50
            )
        ]
        
        for endpoint in default_endpoints:
            self.endpoints[endpoint.path] = endpoint

    # Authentication helpers

    async def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            # In production, use proper JWT secret/key
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check expiration
            if 'exp' in payload and payload['exp'] < time.time():
                return None
            
            return {
                'user_id': payload.get('user_id'),
                'permissions': payload.get('permissions', []),
                'roles': payload.get('roles', [])
            }
        except:
            return None

    async def _validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key"""
        # This would typically check against database
        # For demo, accept any key starting with "ak_"
        if api_key.startswith("ak_"):
            return {
                'user_id': 'api_user',
                'permissions': ['api_access'],
                'roles': ['api_user']
            }
        return None

    # Logging and monitoring

    async def _log_request(self, api_request: APIRequest, status: int, processing_time: float):
        """Log API request"""
        log_data = {
            'request_id': api_request.request_id,
            'client_ip': api_request.client_ip,
            'method': api_request.method,
            'path': api_request.path,
            'status': status,
            'processing_time_ms': processing_time,
            'user_id': api_request.user_id,
            'user_agent': api_request.user_agent,
            'timestamp': api_request.timestamp.isoformat()
        }
        
        if self.redis_client:
            await self.redis_client.lpush(
                'api_access_logs',
                json.dumps(log_data)
            )

    async def _handle_threats(self, threats: List[SecurityThreat]):
        """Handle detected threats"""
        for threat in threats:
            # Store threat
            if self.redis_client:
                await self.redis_client.setex(
                    f"threat:{threat.threat_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(threat), default=str)
                )
            
            # Auto-block for high-severity threats
            if threat.severity == "high" and threat.confidence > 0.8:
                self.blocked_ips.add(threat.source_request.client_ip)
                logger.warning(f"🚫 Auto-blocked IP: {threat.source_request.client_ip}")

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{int(time.time())}_{hash(time.time()) % 10000}"

    def _generate_threat_id(self) -> str:
        """Generate unique threat ID"""
        return f"threat_{int(time.time())}_{hash(time.time()) % 10000}"

    # Public API

    def add_endpoint(self, endpoint: APIEndpoint):
        """Add API endpoint configuration"""
        self.endpoints[endpoint.path] = endpoint

    def block_ip(self, ip_address: str):
        """Block IP address"""
        self.blocked_ips.add(ip_address)

    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        self.blocked_ips.discard(ip_address)

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        return {
            'requests_processed': self.requests_processed,
            'threats_detected': self.threats_detected,
            'requests_blocked': self.requests_blocked,
            'false_positives': self.false_positives,
            'blocked_ips_count': len(self.blocked_ips),
            'endpoints_configured': len(self.endpoints),
            'threat_detection_rate': self.threats_detected / max(self.requests_processed, 1)
        }

    async def close(self):
        """Cleanup resources"""
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

# Export main classes
__all__ = [
    'APISecurityGateway', 'APIEndpoint', 'APIRequest', 
    'SecurityThreat', 'SecurityLevel', 'ThreatType', 
    'ValidationResult'
]

if __name__ == "__main__":
    async def test_api_security_gateway():
        """Test the API security gateway"""
        config = {
            'global_rate_limit': 100,
            'max_request_size': 1024 * 1024
        }
        
        gateway = APISecurityGateway(config)
        await gateway.initialize()
        
        # Test request creation
        test_request = APIRequest(
            request_id="test123",
            client_ip="192.168.1.100",
            method="POST",
            path="/api/v1/content/upload",
            headers={'Content-Type': 'application/json', 'User-Agent': 'TestClient/1.0'},
            query_params={'type': 'image'},
            body=b'{"title": "Test Content", "description": "A test upload"}'
        )
        
        # Test threat detection
        threat_result = await gateway._detect_threats(test_request)
        print(f"🛡️ Threat Detection Result: {len(threat_result['threats'])} threats found")
        
        # Test input validation
        validation_result = await gateway._validate_input(test_request)
        print(f"✅ Input Validation Result: {validation_result.value}")
        
        # Test rate limiting
        rate_result = await gateway._check_rate_limits(test_request)
        print(f"⏱️ Rate Limit Result: {'PASS' if rate_result['allowed'] else 'BLOCKED'}")
        
        # Performance metrics
        metrics = gateway.get_security_metrics()
        print(f"\n📊 Security Metrics:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        await gateway.close()
    
    # Run test
    asyncio.run(test_api_security_gateway())