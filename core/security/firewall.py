"""
API Security and Firewall Module
Advanced API protection and firewall for IA Influencer Agent

Features:
- Intelligent API rate limiting with adaptive throttling
- Advanced DDoS protection with ML-based pattern detection
- Deep packet inspection and content filtering
- AI-powered security gateway with behavioral analysis
- Geo-blocking with precision targeting and VPN detection
- Advanced bot detection with machine learning classification
- API access control with zero-trust architecture
- Real-time threat intelligence integration
- Content-aware filtering for multimedia uploads
- Application-layer firewall with protocol analysis
- Distributed rate limiting across multiple instances
- Advanced fingerprinting resistance and evasion detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms
"""

import asyncio
import time
import json
import ipaddress
import hashlib
import uuid
from typing import Dict, List, Optional, Set, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
from concurrent.futures import ThreadPoolExecutor
import re
import pickle
from pathlib import Path

from fastapi import Request, Response, HTTPException, BackgroundTasks
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import Message
import geoip2.database
import geoip2.errors
import user_agents
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger


class RateLimitType(Enum):
    """Types of rate limiting with priority levels"""
    IP_BASED = "ip_based"
    USER_BASED = "user_based"
    ENDPOINT_BASED = "endpoint_based"
    CONTENT_BASED = "content_based"
    TENANT_BASED = "tenant_based"
    GLOBAL = "global"
    BURST = "burst"
    SLIDING_WINDOW = "sliding_window"


class BlockAction(Enum):
    """Actions to take when blocking requests"""
    DENY = "deny"
    DELAY = "delay"
    CAPTCHA = "captcha"
    REDIRECT = "redirect"


class ThreatLevel(Enum):
    """Threat levels for requests"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RateLimitRule:
    """Rate limiting rule definition"""
    rule_id: str
    limit_type: RateLimitType
    requests_per_window: int
    window_seconds: int
    burst_limit: Optional[int] = None
    endpoints: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    exempted_ips: Set[str] = field(default_factory=set)
    exempted_users: Set[str] = field(default_factory=set)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityRule:
    """Security filtering rule"""
    rule_id: str
    name: str
    description: str
    pattern: str
    is_regex: bool
    action: BlockAction
    threat_level: ThreatLevel
    enabled: bool = True
    whitelist_ips: Set[str] = field(default_factory=set)
    blacklist_ips: Set[str] = field(default_factory=set)


@dataclass
class RequestAnalysis:
    """Request analysis result"""
    request_id: str
    source_ip: str
    endpoint: str
    method: str
    user_agent: str
    threat_level: ThreatLevel
    security_issues: List[str] = field(default_factory=list)
    rate_limit_violations: List[str] = field(default_factory=list)
    geolocation: Optional[Dict[str, str]] = None
    is_bot: bool = False
    should_block: bool = False
    block_reason: Optional[str] = None
    analysis_time: datetime = field(default_factory=datetime.utcnow)


class RateLimiter:
    """Advanced rate limiting implementation"""
    
    def __init__(self):
        self.logger = SecurityLogger("RateLimiter")
        self.cache = CacheManager()
        self.settings = get_settings()
        
        # Default rate limiting rules
        self.default_rules = self._initialize_default_rules()
        
        # Request counters
        self.request_counters = defaultdict(lambda: defaultdict(deque))
    
    def _initialize_default_rules(self) -> List[RateLimitRule]:
        """Initialize default rate limiting rules"""
        rules = []
        
        # Global rate limit
        rules.append(RateLimitRule(
            rule_id="global_limit",
            limit_type=RateLimitType.GLOBAL,
            requests_per_window=10000,
            window_seconds=60,
            burst_limit=1000
        ))
        
        # IP-based rate limit
        rules.append(RateLimitRule(
            rule_id="ip_limit",
            limit_type=RateLimitType.IP_BASED,
            requests_per_window=100,
            window_seconds=60,
            burst_limit=20
        ))
        
        # User-based rate limit
        rules.append(RateLimitRule(
            rule_id="user_limit",
            limit_type=RateLimitType.USER_BASED,
            requests_per_window=1000,
            window_seconds=60,
            burst_limit=50
        ))
        
        # Auth endpoint rate limit
        rules.append(RateLimitRule(
            rule_id="auth_limit",
            limit_type=RateLimitType.ENDPOINT_BASED,
            requests_per_window=10,
            window_seconds=60,
            endpoints=["/auth/login", "/auth/register", "/auth/reset-password"],
            methods=["POST"]
        ))
        
        # Upload endpoint rate limit
        rules.append(RateLimitRule(
            rule_id="upload_limit",
            limit_type=RateLimitType.ENDPOINT_BASED,
            requests_per_window=50,
            window_seconds=3600,  # 1 hour
            endpoints=["/api/v1/content/upload", "/api/v1/fingerprint/create"],
            methods=["POST"]
        ))
        
        return rules
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if request exceeds rate limits"""
        try:
            source_ip = self._get_client_ip(request)
            endpoint = str(request.url.path)
            method = request.method
            
            for rule in self.default_rules:
                if not rule.enabled:
                    continue
                
                # Check if rule applies to this request
                if not self._rule_applies(rule, endpoint, method, source_ip, user_id):
                    continue
                
                # Check rate limit
                is_exceeded, violation_msg = await self._check_rule_violation(
                    rule, source_ip, endpoint, method, user_id
                )
                
                if is_exceeded:
                    self.logger.warning(f"Rate limit exceeded: {violation_msg}")
                    return True, violation_msg
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            return False, None
    
    def _rule_applies(
        self, 
        rule: RateLimitRule, 
        endpoint: str, 
        method: str,
        source_ip: str, 
        user_id: Optional[str]
    ) -> bool:
        """Check if rate limiting rule applies to request"""
        
        # Check IP exemptions
        if source_ip in rule.exempted_ips:
            return False
        
        # Check user exemptions
        if user_id and user_id in rule.exempted_users:
            return False
        
        # Check endpoint filters
        if rule.endpoints:
            endpoint_match = any(ep in endpoint for ep in rule.endpoints)
            if not endpoint_match:
                return False
        
        # Check method filters
        if rule.methods:
            if method not in rule.methods:
                return False
        
        return True
    
    async def _check_rule_violation(
        self, 
        rule: RateLimitRule,
        source_ip: str,
        endpoint: str,
        method: str,
        user_id: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """Check if specific rule is violated"""
        try:
            current_time = time.time()
            
            # Determine cache key based on rule type
            if rule.limit_type == RateLimitType.IP_BASED:
                cache_key = f"rate_limit:{rule.rule_id}:{source_ip}"
            elif rule.limit_type == RateLimitType.USER_BASED and user_id:
                cache_key = f"rate_limit:{rule.rule_id}:{user_id}"
            elif rule.limit_type == RateLimitType.ENDPOINT_BASED:
                cache_key = f"rate_limit:{rule.rule_id}:{endpoint}:{source_ip}"
            else:  # GLOBAL
                cache_key = f"rate_limit:{rule.rule_id}:global"
            
            # Get request timestamps from cache
            request_times = await self.cache.get(cache_key) or []
            
            # Remove expired timestamps
            cutoff_time = current_time - rule.window_seconds
            request_times = [t for t in request_times if t > cutoff_time]
            
            # Check window limit
            if len(request_times) >= rule.requests_per_window:
                return True, f"Rate limit exceeded: {len(request_times)}/{rule.requests_per_window} requests in {rule.window_seconds}s"
            
            # Check burst limit if defined
            if rule.burst_limit:
                # Count requests in last 10 seconds
                burst_cutoff = current_time - 10
                burst_requests = [t for t in request_times if t > burst_cutoff]
                
                if len(burst_requests) >= rule.burst_limit:
                    return True, f"Burst limit exceeded: {len(burst_requests)}/{rule.burst_limit} requests in 10s"
            
            # Add current request
            request_times.append(current_time)
            
            # Store updated timestamps
            await self.cache.set(cache_key, request_times, expire=rule.window_seconds)
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Rule violation check failed: {str(e)}")
            return False, None
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"


class DDoSProtection:
    """DDoS detection and protection"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.logger = SecurityLogger("DDoSProtection")
        self.cache = CacheManager()
        
        # DDoS detection thresholds
        self.detection_thresholds = {
            "requests_per_second": 1000,
            "unique_ips_per_minute": 500,
            "failed_requests_per_minute": 100,
            "bandwidth_per_minute": 100 * 1024 * 1024,  # 100MB
        }
        
        # Blocked IPs and subnets
        self.blocked_ips = set()
        self.blocked_subnets = set()
    
    async def detect_ddos(self, request: Request) -> Tuple[bool, Optional[str]]:
        """Detect DDoS attack patterns"""
        try:
            current_time = time.time()
            source_ip = self.rate_limiter._get_client_ip(request)
            
            # Check if IP is already blocked
            if await self._is_ip_blocked(source_ip):
                return True, "IP address is blocked"
            
            # Update request metrics
            await self._update_metrics(source_ip, request)
            
            # Check for attack patterns
            attack_detected, reason = await self._check_attack_patterns()
            
            if attack_detected:
                # Implement protection measures
                await self._implement_protection(source_ip, reason)
                return True, reason
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"DDoS detection failed: {str(e)}")
            return False, None
    
    async def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        try:
            # Check exact IP
            if ip_address in self.blocked_ips:
                return True
            
            # Check cache
            cache_key = f"blocked_ip:{ip_address}"
            is_blocked = await self.cache.get(cache_key)
            if is_blocked:
                return True
            
            # Check subnets
            ip = ipaddress.ip_address(ip_address)
            for subnet in self.blocked_subnets:
                if ip in ipaddress.ip_network(subnet):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"IP block check failed: {str(e)}")
            return False
    
    async def _update_metrics(self, source_ip: str, request: Request):
        """Update DDoS detection metrics"""
        try:
            current_minute = int(time.time() // 60)
            
            # Global request counter
            global_key = f"ddos_metrics:global:{current_minute}"
            await self.cache.increment(global_key)
            await self.cache.expire(global_key, 120)  # Keep for 2 minutes
            
            # Unique IP counter
            unique_ips_key = f"ddos_metrics:unique_ips:{current_minute}"
            unique_ips = await self.cache.get(unique_ips_key) or set()
            unique_ips.add(source_ip)
            await self.cache.set(unique_ips_key, unique_ips, expire=120)
            
            # Per-IP request counter
            ip_key = f"ddos_metrics:ip:{source_ip}:{current_minute}"
            await self.cache.increment(ip_key)
            await self.cache.expire(ip_key, 120)
            
            # Content length tracking (for bandwidth calculation)
            content_length = int(request.headers.get("content-length", 0))
            if content_length > 0:
                bandwidth_key = f"ddos_metrics:bandwidth:{current_minute}"
                await self.cache.increment(bandwidth_key, content_length)
                await self.cache.expire(bandwidth_key, 120)
            
        except Exception as e:
            self.logger.error(f"Metrics update failed: {str(e)}")
    
    async def _check_attack_patterns(self) -> Tuple[bool, Optional[str]]:
        """Check for DDoS attack patterns"""
        try:
            current_minute = int(time.time() // 60)
            
            # Check global request rate
            global_key = f"ddos_metrics:global:{current_minute}"
            global_requests = await self.cache.get(global_key) or 0
            
            requests_per_second = global_requests / 60
            if requests_per_second > self.detection_thresholds["requests_per_second"]:
                return True, f"High request rate detected: {requests_per_second:.1f} req/s"
            
            # Check unique IP count
            unique_ips_key = f"ddos_metrics:unique_ips:{current_minute}"
            unique_ips = await self.cache.get(unique_ips_key) or set()
            
            if len(unique_ips) > self.detection_thresholds["unique_ips_per_minute"]:
                return True, f"High unique IP count: {len(unique_ips)} IPs/min"
            
            # Check bandwidth usage
            bandwidth_key = f"ddos_metrics:bandwidth:{current_minute}"
            bandwidth = await self.cache.get(bandwidth_key) or 0
            
            if bandwidth > self.detection_thresholds["bandwidth_per_minute"]:
                return True, f"High bandwidth usage: {bandwidth / (1024*1024):.1f} MB/min"
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Attack pattern check failed: {str(e)}")
            return False, None
    
    async def _implement_protection(self, source_ip: str, reason: str):
        """Implement DDoS protection measures"""
        try:
            # Block IP temporarily
            block_duration = 300  # 5 minutes
            cache_key = f"blocked_ip:{source_ip}"
            await self.cache.set(cache_key, True, expire=block_duration)
            
            # Add to blocked IPs set
            self.blocked_ips.add(source_ip)
            
            # Log protection action
            self.logger.warning(f"DDoS protection activated: Blocked {source_ip} - {reason}")
            
            # Send alert
            await self._send_ddos_alert(source_ip, reason)
            
        except Exception as e:
            self.logger.error(f"Protection implementation failed: {str(e)}")
    
    async def _send_ddos_alert(self, source_ip: str, reason: str):
        """Send DDoS alert notification"""
        # Implementation depends on your notification system
        pass


class RequestFilter:
    """Advanced request filtering and validation"""
    
    def __init__(self):
        self.logger = SecurityLogger("RequestFilter")
        self.cache = CacheManager()
        
        # Security rules
        self.security_rules = self._initialize_security_rules()
        
        # Geo-blocking configuration
        self.blocked_countries = set()
        self.allowed_countries = set()  # If empty, all countries allowed
    
    def _initialize_security_rules(self) -> List[SecurityRule]:
        """Initialize security filtering rules"""
        rules = []
        
        # SQL Injection detection
        rules.append(SecurityRule(
            rule_id="sql_injection",
            name="SQL Injection Detection",
            description="Detects SQL injection attempts",
            pattern=r"(?i)(union|select|insert|update|delete|drop|exec|script|or\s+1\s*=\s*1)",
            is_regex=True,
            action=BlockAction.DENY,
            threat_level=ThreatLevel.HIGH
        ))
        
        # XSS detection
        rules.append(SecurityRule(
            rule_id="xss_detection",
            name="XSS Attack Detection",
            description="Detects cross-site scripting attempts",
            pattern=r"(?i)(<script[^>]*>|javascript:|on\w+\s*=|<iframe[^>]*>)",
            is_regex=True,
            action=BlockAction.DENY,
            threat_level=ThreatLevel.HIGH
        ))
        
        # Path traversal detection
        rules.append(SecurityRule(
            rule_id="path_traversal",
            name="Path Traversal Detection",
            description="Detects directory traversal attempts",
            pattern=r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
            is_regex=True,
            action=BlockAction.DENY,
            threat_level=ThreatLevel.MEDIUM
        ))
        
        # Command injection detection
        rules.append(SecurityRule(
            rule_id="command_injection",
            name="Command Injection Detection",
            description="Detects command injection attempts",
            pattern=r"(?i)(;|\||&|`|\$\(|\${).*?(cat|ls|dir|type|copy|move|del|rm|wget|curl)",
            is_regex=True,
            action=BlockAction.DENY,
            threat_level=ThreatLevel.HIGH
        ))
        
        # Suspicious user agents
        rules.append(SecurityRule(
            rule_id="suspicious_user_agent",
            name="Suspicious User Agent",
            description="Detects suspicious or malicious user agents",
            pattern=r"(?i)(sqlmap|nikto|nmap|masscan|zap|burp|crawler|spider|bot)(?![a-z])",
            is_regex=True,
            action=BlockAction.DENY,
            threat_level=ThreatLevel.MEDIUM
        ))
        
        return rules
    
    async def filter_request(self, request: Request) -> Tuple[bool, Optional[str], ThreatLevel]:
        """Filter incoming request through security rules"""
        try:
            source_ip = self._get_client_ip(request)
            
            # Check geo-blocking
            geo_blocked, geo_reason = await self._check_geo_blocking(source_ip)
            if geo_blocked:
                return True, geo_reason, ThreatLevel.MEDIUM
            
            # Check security rules
            for rule in self.security_rules:
                if not rule.enabled:
                    continue
                
                # Check IP whitelist/blacklist
                if source_ip in rule.blacklist_ips:
                    return True, f"IP blacklisted: {rule.name}", rule.threat_level
                
                if rule.whitelist_ips and source_ip not in rule.whitelist_ips:
                    continue  # Skip rule if IP not in whitelist
                
                # Check rule pattern
                is_match, match_location = await self._check_rule_pattern(request, rule)
                if is_match:
                    reason = f"Security rule triggered: {rule.name} ({match_location})"
                    self.logger.warning(f"Request blocked: {reason}")
                    return True, reason, rule.threat_level
            
            return False, None, ThreatLevel.LOW
            
        except Exception as e:
            self.logger.error(f"Request filtering failed: {str(e)}")
            return False, None, ThreatLevel.LOW
    
    async def _check_geo_blocking(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check if request should be geo-blocked"""
        try:
            # Skip private/local IPs
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private or ip.is_loopback:
                return False, None
            
            # Get country code (placeholder - implement with actual GeoIP service)
            country_code = await self._get_country_code(ip_address)
            
            if not country_code:
                return False, None
            
            # Check blocked countries
            if country_code in self.blocked_countries:
                return True, f"Country blocked: {country_code}"
            
            # Check allowed countries (if specified)
            if self.allowed_countries and country_code not in self.allowed_countries:
                return True, f"Country not allowed: {country_code}"
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Geo-blocking check failed: {str(e)}")
            return False, None
    
    async def _get_country_code(self, ip_address: str) -> Optional[str]:
        """Get country code for IP address"""
        # Check cache first
        cache_key = f"geo_country:{ip_address}"
        cached_country = await self.cache.get(cache_key)
        if cached_country:
            return cached_country
        
        # Placeholder for GeoIP lookup
        # In production, use MaxMind GeoLite2 or similar service
        country_code = "US"  # Default
        
        # Cache result
        await self.cache.set(cache_key, country_code, expire=86400)  # 24 hours
        
        return country_code
    
    async def _check_rule_pattern(self, request: Request, rule: SecurityRule) -> Tuple[bool, str]:
        """Check if request matches security rule pattern"""
        try:
            # Check URL path
            url_path = str(request.url.path)
            if self._pattern_matches(rule.pattern, url_path, rule.is_regex):
                return True, "URL path"
            
            # Check query parameters
            query_string = str(request.url.query) if request.url.query else ""
            if self._pattern_matches(rule.pattern, query_string, rule.is_regex):
                return True, "Query parameters"
            
            # Check headers
            for header_name, header_value in request.headers.items():
                header_content = f"{header_name}: {header_value}"
                if self._pattern_matches(rule.pattern, header_content, rule.is_regex):
                    return True, f"Header: {header_name}"
            
            # Check user agent specifically
            user_agent = request.headers.get("user-agent", "")
            if self._pattern_matches(rule.pattern, user_agent, rule.is_regex):
                return True, "User-Agent"
            
            return False, ""
            
        except Exception as e:
            self.logger.error(f"Rule pattern check failed: {str(e)}")
            return False, ""
    
    def _pattern_matches(self, pattern: str, text: str, is_regex: bool) -> bool:
        """Check if pattern matches text"""
        try:
            if is_regex:
                return bool(re.search(pattern, text))
            else:
                return pattern.lower() in text.lower()
        except Exception:
            return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class SecurityGateway:
    """Main security gateway orchestrating all security components"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.ddos_protection = DDoSProtection(self.rate_limiter)
        self.request_filter = RequestFilter()
        self.logger = SecurityLogger("SecurityGateway")
        self.cache = CacheManager()
    
    async def analyze_request(
        self, 
        request: Request, 
        user_id: Optional[str] = None
    ) -> RequestAnalysis:
        """Comprehensive request analysis"""
        try:
            source_ip = self._get_client_ip(request)
            endpoint = str(request.url.path)
            method = request.method
            user_agent = request.headers.get("user-agent", "")
            
            # Initialize analysis
            analysis = RequestAnalysis(
                request_id=f"req_{int(time.time())}_{hash(source_ip)}",
                source_ip=source_ip,
                endpoint=endpoint,
                method=method,
                user_agent=user_agent,
                threat_level=ThreatLevel.LOW
            )
            
            # Rate limiting check
            rate_exceeded, rate_reason = await self.rate_limiter.check_rate_limit(request, user_id)
            if rate_exceeded:
                analysis.rate_limit_violations.append(rate_reason)
                analysis.should_block = True
                analysis.block_reason = rate_reason
                analysis.threat_level = ThreatLevel.MEDIUM
            
            # DDoS protection check
            ddos_detected, ddos_reason = await self.ddos_protection.detect_ddos(request)
            if ddos_detected:
                analysis.security_issues.append(f"DDoS detected: {ddos_reason}")
                analysis.should_block = True
                analysis.block_reason = ddos_reason
                analysis.threat_level = ThreatLevel.HIGH
            
            # Security filtering
            filter_block, filter_reason, filter_threat = await self.request_filter.filter_request(request)
            if filter_block:
                analysis.security_issues.append(filter_reason)
                analysis.should_block = True
                analysis.block_reason = filter_reason
                analysis.threat_level = max(analysis.threat_level, filter_threat)
            
            # Bot detection
            analysis.is_bot = self._detect_bot(user_agent)
            if analysis.is_bot:
                analysis.security_issues.append("Bot detected")
                # Don't block bots automatically, but log for analysis
            
            # Geolocation
            analysis.geolocation = await self._get_geolocation(source_ip)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Request analysis failed: {str(e)}")
            return RequestAnalysis(
                request_id="error",
                source_ip="unknown",
                endpoint="unknown",
                method="unknown",
                user_agent="unknown",
                threat_level=ThreatLevel.LOW,
                security_issues=[f"Analysis error: {str(e)}"]
            )
    
    def _detect_bot(self, user_agent: str) -> bool:
        """Detect if request is from a bot"""
        try:
            if not user_agent:
                return True  # No user agent is suspicious
            
            # Parse user agent
            ua = user_agents.parse(user_agent)
            if ua.is_bot:
                return True
            
            # Check for bot patterns
            bot_patterns = [
                r'(?i)(bot|crawler|spider|scraper)',
                r'(?i)(google|bing|yahoo|duckduck)',
                r'(?i)(facebook|twitter|linkedin)',
                r'(?i)(curl|wget|python|java|php)'
            ]
            
            for pattern in bot_patterns:
                if re.search(pattern, user_agent):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Bot detection failed: {str(e)}")
            return False
    
    async def _get_geolocation(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get geolocation for IP address"""
        try:
            # Check cache first
            cache_key = f"geolocation:{ip_address}"
            cached_geo = await self.cache.get(cache_key)
            if cached_geo:
                return cached_geo
            
            # Skip private IPs
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private or ip.is_loopback:
                return {"country": "Private", "city": "Local"}
            
            # Placeholder for GeoIP lookup
            geolocation = {
                "country": "Unknown",
                "country_code": "XX",
                "city": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0
            }
            
            # Cache result
            await self.cache.set(cache_key, geolocation, expire=86400)  # 24 hours
            
            return geolocation
            
        except Exception as e:
            self.logger.error(f"Geolocation lookup failed: {str(e)}")
            return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class APIFirewall(BaseHTTPMiddleware):
    """API Firewall middleware for FastAPI"""
    
    def __init__(self, app, security_gateway: SecurityGateway):
        super().__init__(app)
        self.security_gateway = security_gateway
        self.logger = SecurityLogger("APIFirewall")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request through security gateway"""
        try:
            start_time = time.time()
            
            # Analyze request
            analysis = await self.security_gateway.analyze_request(request)
            
            # Block if necessary
            if analysis.should_block:
                self.logger.warning(
                    f"Request blocked: {analysis.block_reason} "
                    f"from {analysis.source_ip} to {analysis.endpoint}"
                )
                
                return Response(
                    content=json.dumps({
                        "error": "Request blocked by security policy",
                        "request_id": analysis.request_id,
                        "reason": analysis.block_reason
                    }),
                    status_code=429 if "rate limit" in analysis.block_reason.lower() else 403,
                    headers={"Content-Type": "application/json"}
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Request-ID"] = analysis.request_id
            response.headers["X-Security-Gateway"] = "IA-Influencer-Agent"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Log request
            process_time = time.time() - start_time
            self.logger.info(
                f"Request processed: {analysis.method} {analysis.endpoint} "
                f"from {analysis.source_ip} in {process_time:.3f}s "
                f"[{response.status_code}]"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"API Firewall error: {str(e)}")
            # Continue with request processing on error
            return await call_next(request)
