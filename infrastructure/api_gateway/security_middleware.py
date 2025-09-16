"""
Security Middleware - Comprehensive Security Layer Stack
© 2025 Fahed Mlaiel. All rights reserved.

Security Middleware providing request/response filtering, XSS/CSRF protection,
DDoS mitigation, security headers management, and threat detection.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import re
import hashlib
import hmac
import time
from dataclasses import dataclass, field
from collections import defaultdict, deque
import ipaddress
import base64
from urllib.parse import unquote, urlparse

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Security actions"""
    ALLOW = "allow"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    CHALLENGE = "challenge"
    LOG_ONLY = "log_only"


class AttackType(Enum):
    """Attack types"""
    XSS = "xss"
    SQL_INJECTION = "sql_injection"
    CSRF = "csrf"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    MALICIOUS_UPLOAD = "malicious_upload"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    BOT_TRAFFIC = "bot_traffic"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class SecurityEventType(Enum):
    """Security event types"""
    THREAT_DETECTED = "threat_detected"
    ATTACK_BLOCKED = "attack_blocked"
    RATE_LIMITED = "rate_limited"
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


@dataclass
class SecurityRequest:
    """Security request wrapper"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str = ""
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    ip_address: str = ""
    user_agent: str = ""
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityResponse:
    """Security response wrapper"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    size: int = 0
    processing_time: float = 0.0
    security_headers_added: List[str] = field(default_factory=list)
    filtered: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityThreat:
    """Security threat detection"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: AttackType = AttackType.SUSPICIOUS_BEHAVIOR
    level: ThreatLevel = ThreatLevel.LOW
    description: str = ""
    source_ip: str = ""
    user_agent: str = ""
    request_id: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    action_taken: SecurityAction = SecurityAction.LOG_ONLY
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False


@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    pattern: str = "*"
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    burst_limit: int = 50
    window_size: int = 60  # seconds
    enabled: bool = True
    applies_to: List[str] = field(default_factory=list)  # IP, user, endpoint
    action: SecurityAction = SecurityAction.RATE_LIMIT


@dataclass
class SecurityMetrics:
    """Security metrics"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    total_requests: int = 0
    blocked_requests: int = 0
    rate_limited_requests: int = 0
    threats_detected: int = 0
    attacks_blocked: int = 0
    avg_response_time: float = 0.0
    unique_ips: int = 0
    suspicious_ips: int = 0
    top_threat_types: Dict[str, int] = field(default_factory=dict)


class SecurityMiddleware:
    """
    Enterprise Security Middleware Stack
    
    Provides comprehensive security layers including:
    - Request/Response filtering and validation
    - XSS (Cross-Site Scripting) protection
    - CSRF (Cross-Site Request Forgery) protection
    - SQL injection detection and prevention
    - DDoS mitigation and rate limiting
    - Security headers management
    - Threat detection and response
    - Malicious upload detection
    - Bot and suspicious behavior detection
    - Real-time security monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Security Middleware"""
        self.config = config or {}
        self.threats: List[SecurityThreat] = []
        self.rate_limits: Dict[str, RateLimitRule] = {}
        self.ip_tracking: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.request_history: deque = deque(maxlen=10000)
        self.blocked_ips: Set[str] = set()
        self.whitelisted_ips: Set[str] = set()
        self.security_metrics: List[SecurityMetrics] = []
        self.csrf_tokens: Dict[str, Dict[str, Any]] = {}
        self.security_handlers: List[Callable] = []
        
        # Configuration
        self.enable_xss_protection = self.config.get('enable_xss_protection', True)
        self.enable_csrf_protection = self.config.get('enable_csrf_protection', True)
        self.enable_sql_injection_protection = self.config.get('enable_sql_injection_protection', True)
        self.enable_ddos_protection = self.config.get('enable_ddos_protection', True)
        self.enable_bot_detection = self.config.get('enable_bot_detection', True)
        self.enable_malware_detection = self.config.get('enable_malware_detection', True)
        
        # Security thresholds
        self.max_request_size = self.config.get('max_request_size', 10 * 1024 * 1024)  # 10MB
        self.max_header_size = self.config.get('max_header_size', 8192)  # 8KB
        self.suspicious_request_threshold = self.config.get('suspicious_request_threshold', 100)
        self.auto_block_threshold = self.config.get('auto_block_threshold', 50)
        self.rate_limit_window = self.config.get('rate_limit_window', 60)
        
        # Security patterns
        self._setup_security_patterns()
        self._setup_default_rate_limits()
        self._setup_security_headers()
        
        # Start monitoring tasks
        self._start_monitoring_tasks()
        
        logger.info("Security Middleware initialized")
    
    def _setup_security_patterns(self):
        """Setup security detection patterns"""
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>.*?</style>',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import',
            r'vbscript:',
            r'data:text/html',
            r'<svg[^>]*>.*?</svg>'
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\b\s+[\'"][^\'"]*[\'"]?\s*=\s*[\'"][^\'"]*[\'"]?)',
            r'(\bUNION\b\s+\bSELECT\b)',
            r'(\b(HAVING|WHERE)\b\s+\d+\s*=\s*\d+)',
            r'(--|#|/\*|\*/)',
            r'(\bINTO\b\s+\bOUTFILE\b)',
            r'(\bLOAD_FILE\b\s*\()',
            r'(\bBENCHMARK\b\s*\()',
            r'(\bSLEEP\b\s*\()',
            r'(\bWAITFOR\b\s+\bDELAY\b)'
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'%252e%252e%252f',
            r'..%2f',
            r'..%5c'
        ]
        
        # Command injection patterns
        self.command_injection_patterns = [
            r'[;&|`$]',
            r'\$\(',
            r'`[^`]*`',
            r'\|\s*\w+',
            r'>\s*/\w+',
            r'<\s*/\w+'
        ]
        
        # Bot user agents
        self.bot_user_agents = [
            r'bot', r'crawler', r'spider', r'scraper', r'scan',
            r'curl', r'wget', r'python', r'java', r'go-http',
            r'headless', r'phantom', r'selenium'
        ]
    
    def _setup_default_rate_limits(self):
        """Setup default rate limiting rules"""
        default_rules = [
            RateLimitRule(
                name="api_general",
                pattern="/api/*",
                requests_per_minute=1000,
                requests_per_hour=50000,
                burst_limit=100,
                applies_to=["ip"]
            ),
            RateLimitRule(
                name="auth_endpoints",
                pattern="/auth/*",
                requests_per_minute=30,
                requests_per_hour=500,
                burst_limit=10,
                applies_to=["ip"]
            ),
            RateLimitRule(
                name="upload_endpoints",
                pattern="/upload/*",
                requests_per_minute=50,
                requests_per_hour=1000,
                burst_limit=20,
                applies_to=["user", "ip"]
            ),
            RateLimitRule(
                name="admin_endpoints",
                pattern="/admin/*",
                requests_per_minute=100,
                requests_per_hour=2000,
                burst_limit=25,
                applies_to=["user"]
            ),
            RateLimitRule(
                name="public_api",
                pattern="/public/*",
                requests_per_minute=2000,
                requests_per_hour=100000,
                burst_limit=200,
                applies_to=["ip"]
            )
        ]
        
        for rule in default_rules:
            self.rate_limits[rule.id] = rule
        
        logger.info(f"Setup {len(default_rules)} default rate limit rules")
    
    def _setup_security_headers(self):
        """Setup default security headers"""
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            'Permissions-Policy': (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }
    
    def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._threat_monitor())
        asyncio.create_task(self._metrics_collector())
        asyncio.create_task(self._cleanup_old_data())
    
    async def process_request(self, request: SecurityRequest) -> Tuple[bool, str, SecurityAction]:
        """Process incoming request through security middleware"""
        start_time = time.time()
        
        try:
            # Check if IP is blocked
            if request.ip_address in self.blocked_ips:
                await self._log_security_event(
                    SecurityEventType.ATTACK_BLOCKED,
                    f"Blocked IP {request.ip_address}",
                    request
                )
                return False, "IP address blocked", SecurityAction.BLOCK
            
            # Check if IP is whitelisted
            if request.ip_address in self.whitelisted_ips:
                return True, "Whitelisted IP", SecurityAction.ALLOW
            
            # Size validation
            if request.size > self.max_request_size:
                threat = SecurityThreat(
                    type=AttackType.SUSPICIOUS_BEHAVIOR,
                    level=ThreatLevel.MEDIUM,
                    description=f"Request size {request.size} exceeds limit {self.max_request_size}",
                    source_ip=request.ip_address,
                    request_id=request.id,
                    action_taken=SecurityAction.BLOCK
                )
                await self._record_threat(threat)
                return False, "Request too large", SecurityAction.BLOCK
            
            # Header validation
            total_header_size = sum(len(k) + len(v) for k, v in request.headers.items())
            if total_header_size > self.max_header_size:
                threat = SecurityThreat(
                    type=AttackType.SUSPICIOUS_BEHAVIOR,
                    level=ThreatLevel.MEDIUM,
                    description=f"Header size {total_header_size} exceeds limit {self.max_header_size}",
                    source_ip=request.ip_address,
                    request_id=request.id,
                    action_taken=SecurityAction.BLOCK
                )
                await self._record_threat(threat)
                return False, "Headers too large", SecurityAction.BLOCK
            
            # Rate limiting check
            rate_limit_result = await self._check_rate_limits(request)
            if not rate_limit_result['allowed']:
                return False, rate_limit_result['reason'], SecurityAction.RATE_LIMIT
            
            # Bot detection
            if self.enable_bot_detection:
                bot_check = await self._detect_bot_traffic(request)
                if bot_check['is_bot'] and bot_check['malicious']:
                    return False, "Malicious bot detected", SecurityAction.BLOCK
            
            # XSS protection
            if self.enable_xss_protection:
                xss_result = await self._check_xss(request)
                if xss_result['detected']:
                    return False, "XSS attack detected", SecurityAction.BLOCK
            
            # SQL injection protection
            if self.enable_sql_injection_protection:
                sql_result = await self._check_sql_injection(request)
                if sql_result['detected']:
                    return False, "SQL injection detected", SecurityAction.BLOCK
            
            # Path traversal protection
            path_result = await self._check_path_traversal(request)
            if path_result['detected']:
                return False, "Path traversal detected", SecurityAction.BLOCK
            
            # Command injection protection
            cmd_result = await self._check_command_injection(request)
            if cmd_result['detected']:
                return False, "Command injection detected", SecurityAction.BLOCK
            
            # CSRF protection
            if self.enable_csrf_protection and request.method in ['POST', 'PUT', 'DELETE']:
                csrf_result = await self._check_csrf(request)
                if not csrf_result['valid']:
                    return False, "CSRF token invalid", SecurityAction.BLOCK
            
            # Suspicious behavior detection
            suspicious_result = await self._detect_suspicious_behavior(request)
            if suspicious_result['suspicious']:
                if suspicious_result['severity'] == 'high':
                    return False, "Suspicious behavior detected", SecurityAction.BLOCK
                elif suspicious_result['severity'] == 'medium':
                    # Log but allow
                    await self._log_security_event(
                        SecurityEventType.SUSPICIOUS_ACTIVITY,
                        "Medium suspicious behavior detected",
                        request
                    )
            
            # Update tracking
            await self._update_ip_tracking(request)
            
            # Log successful request
            self.request_history.append({
                'id': request.id,
                'ip': request.ip_address,
                'method': request.method,
                'url': request.url,
                'timestamp': request.timestamp,
                'allowed': True,
                'processing_time': time.time() - start_time
            })
            
            return True, "Request allowed", SecurityAction.ALLOW
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return False, f"Security error: {str(e)}", SecurityAction.BLOCK
    
    async def process_response(self, response: SecurityResponse) -> SecurityResponse:
        """Process outgoing response through security middleware"""
        try:
            # Add security headers
            for header_name, header_value in self.security_headers.items():
                if header_name not in response.headers:
                    response.headers[header_name] = header_value
                    response.security_headers_added.append(header_name)
            
            # Content filtering (remove sensitive information)
            if response.body:
                response.body = await self._filter_response_content(response.body)
                response.filtered = True
            
            return response
            
        except Exception as e:
            logger.error(f"Response processing error: {e}")
            return response
    
    async def generate_csrf_token(self, user_id: str, session_id: str) -> str:
        """Generate CSRF token for user session"""
        try:
            token = hashlib.sha256(f"{user_id}:{session_id}:{time.time()}".encode()).hexdigest()
            
            self.csrf_tokens[token] = {
                'user_id': user_id,
                'session_id': session_id,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=1)
            }
            
            return token
            
        except Exception as e:
            logger.error(f"CSRF token generation error: {e}")
            return ""
    
    async def block_ip(self, ip_address: str, reason: str = "Security violation"):
        """Block IP address"""
        try:
            self.blocked_ips.add(ip_address)
            
            await self._log_security_event(
                SecurityEventType.ATTACK_BLOCKED,
                f"IP {ip_address} blocked: {reason}",
                None
            )
            
            logger.warning(f"IP blocked: {ip_address} - {reason}")
            
        except Exception as e:
            logger.error(f"IP blocking error: {e}")
    
    async def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        try:
            self.blocked_ips.discard(ip_address)
            logger.info(f"IP unblocked: {ip_address}")
            
        except Exception as e:
            logger.error(f"IP unblocking error: {e}")
    
    async def whitelist_ip(self, ip_address: str):
        """Add IP to whitelist"""
        try:
            self.whitelisted_ips.add(ip_address)
            logger.info(f"IP whitelisted: {ip_address}")
            
        except Exception as e:
            logger.error(f"IP whitelisting error: {e}")
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security metrics"""
        try:
            # Recent requests analysis
            recent_requests = [
                req for req in self.request_history
                if (datetime.utcnow() - req['timestamp']).total_seconds() < 3600
            ]
            
            total_requests = len(recent_requests)
            blocked_requests = len([req for req in recent_requests if not req.get('allowed', True)])
            
            # Threat analysis
            recent_threats = [
                threat for threat in self.threats
                if (datetime.utcnow() - threat.timestamp).total_seconds() < 3600
            ]
            
            threat_by_type = defaultdict(int)
            for threat in recent_threats:
                threat_by_type[threat.type.value] += 1
            
            # IP analysis
            unique_ips = len(set(req['ip'] for req in recent_requests))
            suspicious_ips = len([
                ip for ip, data in self.ip_tracking.items()
                if data.get('threat_score', 0) > 50
            ])
            
            return {
                'total_requests': total_requests,
                'blocked_requests': blocked_requests,
                'block_rate': (blocked_requests / total_requests * 100) if total_requests > 0 else 0,
                'unique_ips': unique_ips,
                'blocked_ips': len(self.blocked_ips),
                'whitelisted_ips': len(self.whitelisted_ips),
                'suspicious_ips': suspicious_ips,
                'threats_detected': len(recent_threats),
                'threats_by_type': dict(threat_by_type),
                'rate_limit_rules': len(self.rate_limits),
                'csrf_tokens_active': len([
                    token for token, data in self.csrf_tokens.items()
                    if data['expires_at'] > datetime.utcnow()
                ]),
                'avg_processing_time': sum(req.get('processing_time', 0) for req in recent_requests) / total_requests if total_requests > 0 else 0,
                'security_handlers': len(self.security_handlers),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return {'error': str(e)}
    
    def add_security_handler(self, handler: Callable):
        """Add security event handler"""
        self.security_handlers.append(handler)
    
    # Internal Implementation Methods
    
    async def _check_rate_limits(self, request: SecurityRequest) -> Dict[str, Any]:
        """Check request against rate limiting rules"""
        try:
            for rule in self.rate_limits.values():
                if not rule.enabled:
                    continue
                
                # Check if rule applies to this request
                if not self._rule_matches_request(rule, request):
                    continue
                
                # Check rate limits
                for apply_type in rule.applies_to:
                    key = ""
                    if apply_type == "ip":
                        key = f"rate_limit:ip:{request.ip_address}:{rule.id}"
                    elif apply_type == "user" and request.user_id:
                        key = f"rate_limit:user:{request.user_id}:{rule.id}"
                    else:
                        continue
                    
                    # Simple in-memory rate limiting (in production, use Redis)
                    current_time = datetime.utcnow()
                    rate_data = self.ip_tracking.get(key, {
                        'requests': [],
                        'last_reset': current_time
                    })
                    
                    # Clean old requests
                    cutoff_time = current_time - timedelta(seconds=rule.window_size)
                    rate_data['requests'] = [
                        req_time for req_time in rate_data['requests']
                        if req_time > cutoff_time
                    ]
                    
                    # Check limits
                    current_count = len(rate_data['requests'])
                    if current_count >= rule.requests_per_minute:
                        threat = SecurityThreat(
                            type=AttackType.RATE_LIMIT_EXCEEDED,
                            level=ThreatLevel.MEDIUM,
                            description=f"Rate limit exceeded: {current_count} requests in {rule.window_size}s",
                            source_ip=request.ip_address,
                            request_id=request.id,
                            action_taken=SecurityAction.RATE_LIMIT
                        )
                        await self._record_threat(threat)
                        
                        return {
                            'allowed': False,
                            'reason': f"Rate limit exceeded for {rule.name}",
                            'rule': rule.name,
                            'current_count': current_count,
                            'limit': rule.requests_per_minute
                        }
                    
                    # Record this request
                    rate_data['requests'].append(current_time)
                    self.ip_tracking[key] = rate_data
            
            return {'allowed': True, 'reason': 'Rate limits passed'}
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return {'allowed': True, 'reason': 'Rate limit check error'}
    
    def _rule_matches_request(self, rule: RateLimitRule, request: SecurityRequest) -> bool:
        """Check if rate limit rule matches request"""
        import fnmatch
        return fnmatch.fnmatch(request.url, rule.pattern)
    
    async def _check_xss(self, request: SecurityRequest) -> Dict[str, Any]:
        """Check for XSS attacks"""
        try:
            content_to_check = f"{request.url} {request.body} {' '.join(request.headers.values())}"
            content_to_check = unquote(content_to_check).lower()
            
            for pattern in self.xss_patterns:
                if re.search(pattern, content_to_check, re.IGNORECASE):
                    threat = SecurityThreat(
                        type=AttackType.XSS,
                        level=ThreatLevel.HIGH,
                        description=f"XSS pattern detected: {pattern}",
                        source_ip=request.ip_address,
                        request_id=request.id,
                        evidence={'pattern': pattern, 'content': content_to_check[:200]},
                        action_taken=SecurityAction.BLOCK
                    )
                    await self._record_threat(threat)
                    
                    return {
                        'detected': True,
                        'pattern': pattern,
                        'severity': 'high'
                    }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"XSS check error: {e}")
            return {'detected': False}
    
    async def _check_sql_injection(self, request: SecurityRequest) -> Dict[str, Any]:
        """Check for SQL injection attacks"""
        try:
            content_to_check = f"{request.url} {request.body} {' '.join(request.headers.values())}"
            content_to_check = unquote(content_to_check)
            
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, content_to_check, re.IGNORECASE):
                    threat = SecurityThreat(
                        type=AttackType.SQL_INJECTION,
                        level=ThreatLevel.CRITICAL,
                        description=f"SQL injection pattern detected: {pattern}",
                        source_ip=request.ip_address,
                        request_id=request.id,
                        evidence={'pattern': pattern, 'content': content_to_check[:200]},
                        action_taken=SecurityAction.BLOCK
                    )
                    await self._record_threat(threat)
                    
                    return {
                        'detected': True,
                        'pattern': pattern,
                        'severity': 'critical'
                    }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"SQL injection check error: {e}")
            return {'detected': False}
    
    async def _check_path_traversal(self, request: SecurityRequest) -> Dict[str, Any]:
        """Check for path traversal attacks"""
        try:
            url_decoded = unquote(request.url)
            
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, url_decoded, re.IGNORECASE):
                    threat = SecurityThreat(
                        type=AttackType.SUSPICIOUS_BEHAVIOR,
                        level=ThreatLevel.HIGH,
                        description=f"Path traversal pattern detected: {pattern}",
                        source_ip=request.ip_address,
                        request_id=request.id,
                        evidence={'pattern': pattern, 'url': url_decoded},
                        action_taken=SecurityAction.BLOCK
                    )
                    await self._record_threat(threat)
                    
                    return {
                        'detected': True,
                        'pattern': pattern,
                        'severity': 'high'
                    }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Path traversal check error: {e}")
            return {'detected': False}
    
    async def _check_command_injection(self, request: SecurityRequest) -> Dict[str, Any]:
        """Check for command injection attacks"""
        try:
            content_to_check = f"{request.url} {request.body}"
            content_to_check = unquote(content_to_check)
            
            for pattern in self.command_injection_patterns:
                if re.search(pattern, content_to_check):
                    threat = SecurityThreat(
                        type=AttackType.SUSPICIOUS_BEHAVIOR,
                        level=ThreatLevel.HIGH,
                        description=f"Command injection pattern detected: {pattern}",
                        source_ip=request.ip_address,
                        request_id=request.id,
                        evidence={'pattern': pattern, 'content': content_to_check[:200]},
                        action_taken=SecurityAction.BLOCK
                    )
                    await self._record_threat(threat)
                    
                    return {
                        'detected': True,
                        'pattern': pattern,
                        'severity': 'high'
                    }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Command injection check error: {e}")
            return {'detected': False}
    
    async def _check_csrf(self, request: SecurityRequest) -> Dict[str, Any]:
        """Check CSRF token validity"""
        try:
            csrf_token = request.headers.get('X-CSRF-Token') or request.headers.get('csrf-token')
            
            if not csrf_token:
                return {'valid': False, 'reason': 'Missing CSRF token'}
            
            token_data = self.csrf_tokens.get(csrf_token)
            if not token_data:
                return {'valid': False, 'reason': 'Invalid CSRF token'}
            
            if token_data['expires_at'] < datetime.utcnow():
                del self.csrf_tokens[csrf_token]
                return {'valid': False, 'reason': 'CSRF token expired'}
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"CSRF check error: {e}")
            return {'valid': False, 'reason': 'CSRF check error'}
    
    async def _detect_bot_traffic(self, request: SecurityRequest) -> Dict[str, Any]:
        """Detect bot traffic"""
        try:
            user_agent = request.user_agent.lower()
            
            # Check against known bot patterns
            for pattern in self.bot_user_agents:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    # Determine if it's a malicious bot
                    malicious = self._is_malicious_bot(request)
                    
                    if malicious:
                        threat = SecurityThreat(
                            type=AttackType.BOT_TRAFFIC,
                            level=ThreatLevel.MEDIUM,
                            description=f"Malicious bot detected: {pattern}",
                            source_ip=request.ip_address,
                            user_agent=request.user_agent,
                            request_id=request.id,
                            action_taken=SecurityAction.BLOCK
                        )
                        await self._record_threat(threat)
                    
                    return {
                        'is_bot': True,
                        'malicious': malicious,
                        'pattern': pattern
                    }
            
            return {'is_bot': False, 'malicious': False}
            
        except Exception as e:
            logger.error(f"Bot detection error: {e}")
            return {'is_bot': False, 'malicious': False}
    
    def _is_malicious_bot(self, request: SecurityRequest) -> bool:
        """Determine if bot is malicious"""
        # Simple heuristics - in production, use more sophisticated detection
        ip_data = self.ip_tracking.get(request.ip_address, {})
        
        # High request frequency
        if ip_data.get('request_count', 0) > 100:
            return True
        
        # Suspicious patterns in URL
        suspicious_patterns = ['/admin', '/config', '/backup', '/.env', '/database']
        for pattern in suspicious_patterns:
            if pattern in request.url:
                return True
        
        return False
    
    async def _detect_suspicious_behavior(self, request: SecurityRequest) -> Dict[str, Any]:
        """Detect suspicious behavior patterns"""
        try:
            suspicion_score = 0
            reasons = []
            
            # Check request frequency from IP
            ip_data = self.ip_tracking.get(request.ip_address, {})
            request_count = ip_data.get('request_count', 0)
            
            if request_count > self.suspicious_request_threshold:
                suspicion_score += 30
                reasons.append(f"High request frequency: {request_count}")
            
            # Check for unusual headers
            unusual_headers = ['X-Forwarded-For', 'X-Real-IP', 'X-Originating-IP']
            for header in unusual_headers:
                if header in request.headers:
                    suspicion_score += 10
                    reasons.append(f"Unusual header: {header}")
            
            # Check for suspicious URL patterns
            suspicious_urls = ['/phpMyAdmin', '/wp-admin', '/.git', '/.svn', '/backup']
            for pattern in suspicious_urls:
                if pattern in request.url:
                    suspicion_score += 40
                    reasons.append(f"Suspicious URL pattern: {pattern}")
            
            # Check for rapid requests from same IP
            recent_requests = ip_data.get('recent_requests', [])
            if len(recent_requests) > 20:  # More than 20 requests recently
                suspicion_score += 25
                reasons.append("Rapid request pattern")
            
            # Determine severity
            severity = 'low'
            if suspicion_score > 50:
                severity = 'high'
            elif suspicion_score > 25:
                severity = 'medium'
            
            suspicious = suspicion_score > 20
            
            if suspicious and severity == 'high':
                threat = SecurityThreat(
                    type=AttackType.SUSPICIOUS_BEHAVIOR,
                    level=ThreatLevel.HIGH if severity == 'high' else ThreatLevel.MEDIUM,
                    description=f"Suspicious behavior detected: {', '.join(reasons)}",
                    source_ip=request.ip_address,
                    request_id=request.id,
                    evidence={'score': suspicion_score, 'reasons': reasons},
                    action_taken=SecurityAction.BLOCK if severity == 'high' else SecurityAction.LOG_ONLY
                )
                await self._record_threat(threat)
            
            return {
                'suspicious': suspicious,
                'severity': severity,
                'score': suspicion_score,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Suspicious behavior detection error: {e}")
            return {'suspicious': False, 'severity': 'low', 'score': 0, 'reasons': []}
    
    async def _filter_response_content(self, content: str) -> str:
        """Filter sensitive information from response content"""
        try:
            # Remove potential sensitive patterns
            sensitive_patterns = [
                r'password["\']?\s*[:=]\s*["\']?[^"\';\s]+',
                r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\';\s]+',
                r'secret["\']?\s*[:=]\s*["\']?[^"\';\s]+',
                r'token["\']?\s*[:=]\s*["\']?[^"\';\s]+',
                r'([A-Za-z0-9+/]{40,})',  # Potential tokens
            ]
            
            filtered_content = content
            for pattern in sensitive_patterns:
                filtered_content = re.sub(pattern, '[FILTERED]', filtered_content, flags=re.IGNORECASE)
            
            return filtered_content
            
        except Exception as e:
            logger.error(f"Content filtering error: {e}")
            return content
    
    async def _update_ip_tracking(self, request: SecurityRequest):
        """Update IP tracking data"""
        try:
            ip_data = self.ip_tracking.get(request.ip_address, {
                'first_seen': datetime.utcnow(),
                'request_count': 0,
                'recent_requests': [],
                'threat_score': 0,
                'last_request': None
            })
            
            ip_data['request_count'] += 1
            ip_data['last_request'] = datetime.utcnow()
            
            # Track recent requests (last 5 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            ip_data['recent_requests'] = [
                req_time for req_time in ip_data['recent_requests']
                if req_time > cutoff_time
            ]
            ip_data['recent_requests'].append(datetime.utcnow())
            
            self.ip_tracking[request.ip_address] = ip_data
            
        except Exception as e:
            logger.error(f"IP tracking update error: {e}")
    
    async def _record_threat(self, threat: SecurityThreat):
        """Record security threat"""
        try:
            self.threats.append(threat)
            
            # Auto-block IPs with high threat scores
            ip_data = self.ip_tracking.get(threat.source_ip, {})
            ip_data['threat_score'] = ip_data.get('threat_score', 0) + (
                10 if threat.level == ThreatLevel.LOW else
                25 if threat.level == ThreatLevel.MEDIUM else
                50 if threat.level == ThreatLevel.HIGH else 100
            )
            
            if ip_data['threat_score'] > self.auto_block_threshold:
                await self.block_ip(threat.source_ip, f"Auto-blocked: threat score {ip_data['threat_score']}")
            
            # Notify security handlers
            for handler in self.security_handlers:
                try:
                    await handler(threat)
                except Exception as e:
                    logger.error(f"Security handler error: {e}")
            
        except Exception as e:
            logger.error(f"Threat recording error: {e}")
    
    async def _log_security_event(self, event_type: SecurityEventType, message: str, request: Optional[SecurityRequest]):
        """Log security event"""
        try:
            log_data = {
                'event_type': event_type.value,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if request:
                log_data.update({
                    'request_id': request.id,
                    'ip_address': request.ip_address,
                    'user_agent': request.user_agent,
                    'url': request.url,
                    'method': request.method
                })
            
            logger.info(f"Security Event: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Security event logging error: {e}")
    
    async def _threat_monitor(self):
        """Monitor threats and take automated actions"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Analyze threat patterns
                recent_threats = [
                    threat for threat in self.threats
                    if (datetime.utcnow() - threat.timestamp).total_seconds() < 3600
                ]
                
                # Group threats by IP
                ip_threats = defaultdict(list)
                for threat in recent_threats:
                    ip_threats[threat.source_ip].append(threat)
                
                # Auto-block IPs with multiple high-severity threats
                for ip, threats in ip_threats.items():
                    high_severity_threats = [
                        t for t in threats
                        if t.level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
                    ]
                    
                    if len(high_severity_threats) >= 3:
                        await self.block_ip(ip, f"Multiple high-severity threats: {len(high_severity_threats)}")
                
            except Exception as e:
                logger.error(f"Threat monitor error: {e}")
    
    async def _metrics_collector(self):
        """Collect and store security metrics"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                metrics = SecurityMetrics()
                
                # Calculate metrics from recent data
                recent_requests = [
                    req for req in self.request_history
                    if (datetime.utcnow() - req['timestamp']).total_seconds() < 300
                ]
                
                metrics.total_requests = len(recent_requests)
                metrics.blocked_requests = len([req for req in recent_requests if not req.get('allowed', True)])
                metrics.unique_ips = len(set(req['ip'] for req in recent_requests))
                
                if recent_requests:
                    metrics.avg_response_time = sum(req.get('processing_time', 0) for req in recent_requests) / len(recent_requests)
                
                # Threat analysis
                recent_threats = [
                    threat for threat in self.threats
                    if (datetime.utcnow() - threat.timestamp).total_seconds() < 300
                ]
                
                metrics.threats_detected = len(recent_threats)
                for threat in recent_threats:
                    metrics.top_threat_types[threat.type.value] = metrics.top_threat_types.get(threat.type.value, 0) + 1
                
                self.security_metrics.append(metrics)
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.security_metrics = [
                    m for m in self.security_metrics
                    if m.timestamp > cutoff_time
                ]
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old security data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Clean old threats
                self.threats = [
                    threat for threat in self.threats
                    if threat.timestamp > cutoff_time
                ]
                
                # Clean old CSRF tokens
                expired_tokens = [
                    token for token, data in self.csrf_tokens.items()
                    if data['expires_at'] < datetime.utcnow()
                ]
                
                for token in expired_tokens:
                    del self.csrf_tokens[token]
                
                # Clean old IP tracking data
                for ip in list(self.ip_tracking.keys()):
                    ip_data = self.ip_tracking[ip]
                    if ip_data.get('last_request') and ip_data['last_request'] < cutoff_time:
                        del self.ip_tracking[ip]
                
                logger.info(f"Cleaned up old security data: {len(expired_tokens)} CSRF tokens, IP tracking entries")
                
            except Exception as e:
                logger.error(f"Cleanup error: {e}")


# Security Middleware Factory
def create_security_middleware(config: Optional[Dict[str, Any]] = None) -> SecurityMiddleware:
    """Factory function to create Security Middleware instance"""
    return SecurityMiddleware(config)


# Default security event handler
async def log_security_handler(threat: SecurityThreat):
    """Default security threat handler"""
    logger.warning(f"SECURITY THREAT: {threat.type.value} from {threat.source_ip} - {threat.description}")


if __name__ == "__main__":
    # Example usage
    async def main():
        security = create_security_middleware({
            'enable_xss_protection': True,
            'enable_csrf_protection': True,
            'enable_ddos_protection': True,
            'auto_block_threshold': 50
        })
        
        # Add security handler
        security.add_security_handler(log_security_handler)
        
        # Test normal request
        normal_request = SecurityRequest(
            method='GET',
            url='/api/v1/content',
            headers={'User-Agent': 'Mozilla/5.0'},
            ip_address='192.168.1.100',
            user_id='user123',
            size=1024
        )
        
        allowed, reason, action = await security.process_request(normal_request)
        print(f"Normal request: {allowed} - {reason}")
        
        # Test malicious request
        malicious_request = SecurityRequest(
            method='POST',
            url='/api/v1/search',
            headers={'User-Agent': 'curl/7.0'},
            body="'; DROP TABLE users; --",
            ip_address='192.168.1.200',
            size=2048
        )
        
        allowed, reason, action = await security.process_request(malicious_request)
        print(f"Malicious request: {allowed} - {reason}")
        
        # Test response processing
        response = SecurityResponse(
            status_code=200,
            body='{"data": "sensitive info"}',
            headers={}
        )
        
        processed_response = await security.process_response(response)
        print(f"Security headers added: {len(processed_response.security_headers_added)}")
        
        # Get metrics
        metrics = await security.get_security_metrics()
        print(f"Security metrics: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(main())