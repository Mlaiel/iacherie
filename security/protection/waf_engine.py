#!/usr/bin/env python3
"""
🛡️ WAF Engine - Enterprise Security Module
===========================================

Ultra-advanced Web Application Firewall with ML-powered attack detection,
rate limiting, and real-time threat protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + WAF + ML + Performance + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import time
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Callable, Pattern
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, deque

import aioredis

logger = logging.getLogger(__name__)

class SecurityAction(Enum):
    """Security action types"""
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"
    LOG_ONLY = "log_only"
    REDIRECT = "redirect"
    CAPTCHA = "captcha"

class ThreatType(Enum):
    """WAF threat types"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    XXE = "xxe"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    REMOTE_FILE_INCLUSION = "remote_file_inclusion"
    LOCAL_FILE_INCLUSION = "local_file_inclusion"
    LDAP_INJECTION = "ldap_injection"
    NOSQL_INJECTION = "nosql_injection"
    SSRF = "ssrf"
    CSRF = "csrf"
    BRUTE_FORCE = "brute_force"
    BOT_ACTIVITY = "bot_activity"
    DDoS = "ddos"
    SCANNER_ACTIVITY = "scanner_activity"
    MALICIOUS_USER_AGENT = "malicious_user_agent"
    SUSPICIOUS_HEADER = "suspicious_header"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

class RuleSeverity(Enum):
    """Rule severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityRule:
    """WAF security rule definition"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    threat_type: ThreatType = ThreatType.SQL_INJECTION
    severity: RuleSeverity = RuleSeverity.MEDIUM
    pattern: str = ""
    compiled_pattern: Optional[Pattern] = None
    action: SecurityAction = SecurityAction.BLOCK
    enabled: bool = True
    confidence: float = 0.8
    false_positive_rate: float = 0.1
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RequestContext:
    """HTTP request context for WAF analysis"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    ip_address: str = "unknown"
    user_agent: str = ""
    content_type: str = ""
    content_length: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityDetection:
    """Security detection result"""
    detection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    threat_type: ThreatType = ThreatType.SQL_INJECTION
    severity: RuleSeverity = RuleSeverity.MEDIUM
    confidence: float = 0.8
    matched_pattern: str = ""
    matched_location: str = ""  # header, query, body, etc.
    matched_value: str = ""
    action_taken: SecurityAction = SecurityAction.BLOCK
    request_context: Optional[RequestContext] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

class RateLimiter:
    """
    Advanced rate limiting with multiple algorithms.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        
        # Rate limiting rules
        self.rate_limits = {
            "global": {"requests": 1000, "window": 60},  # 1000 req/min globally
            "per_ip": {"requests": 100, "window": 60},   # 100 req/min per IP
            "per_user": {"requests": 200, "window": 60}, # 200 req/min per user
            "login": {"requests": 5, "window": 300},     # 5 login attempts per 5 min
            "api": {"requests": 50, "window": 60}        # 50 API calls per min
        }
        
    async def initialize(self) -> None:
        """Initialize rate limiter"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Rate limiter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter: {e}")
            raise

    async def check_rate_limit(
        self,
        key: str,
        limit_type: str = "per_ip",
        custom_limit: Optional[Dict[str, int]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request exceeds rate limit"""
        try:
            # Use custom limit or default
            limit_config = custom_limit or self.rate_limits.get(limit_type, self.rate_limits["per_ip"])
            
            max_requests = limit_config["requests"]
            window_seconds = limit_config["window"]
            
            # Use sliding window algorithm
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Redis key for this limit
            redis_key = f"rate_limit:{limit_type}:{key}"
            
            # Use Redis pipeline for atomic operations
            pipeline = self.redis.pipeline()
            
            # Remove old entries
            pipeline.zremrangebyscore(redis_key, 0, window_start)
            
            # Count current requests
            pipeline.zcard(redis_key)
            
            # Add current request
            pipeline.zadd(redis_key, {str(current_time): current_time})
            
            # Set expiry
            pipeline.expire(redis_key, window_seconds + 10)
            
            # Execute pipeline
            results = await pipeline.execute()
            current_count = results[1]
            
            # Check if limit exceeded
            limit_exceeded = current_count >= max_requests
            
            # Calculate reset time
            reset_time = current_time + window_seconds
            
            return limit_exceeded, {
                "limit_exceeded": limit_exceeded,
                "current_count": current_count,
                "max_requests": max_requests,
                "window_seconds": window_seconds,
                "reset_time": reset_time,
                "retry_after": window_seconds if limit_exceeded else 0
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return False, {"error": str(e)}

    async def get_rate_limit_status(self, key: str, limit_type: str = "per_ip") -> Dict[str, Any]:
        """Get current rate limit status"""
        try:
            limit_config = self.rate_limits.get(limit_type, self.rate_limits["per_ip"])
            redis_key = f"rate_limit:{limit_type}:{key}"
            
            current_time = int(time.time())
            window_start = current_time - limit_config["window"]
            
            # Get current count
            current_count = await self.redis.zcount(redis_key, window_start, current_time)
            
            return {
                "current_count": current_count,
                "max_requests": limit_config["requests"],
                "window_seconds": limit_config["window"],
                "remaining": max(0, limit_config["requests"] - current_count)
            }
            
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class AttackDetector:
    """
    ML-powered attack detection engine.
    """
    
    def __init__(self):
        self.attack_patterns = self._load_attack_patterns()
        self.anomaly_detector = None
        self.behavioral_profiles = defaultdict(dict)
        
    def _load_attack_patterns(self) -> Dict[ThreatType, List[str]]:
        """Load attack detection patterns"""
        return {
            ThreatType.SQL_INJECTION: [
                r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
                r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
                r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
                r"((\%27)|(\'))union",
                r"exec(\s|\+)+(s|x)p\w+",
                r"union(.|\n)*select",
                r"(select|insert|update|delete|drop|create|alter|exec|execute|declare|show)\s",
                r"((\%27)|(\'))\s*((\%6F)|o|(\%4F))((\%72)|r|(\%52))\s*(((\%27)|(\'))|(\s))",
            ],
            ThreatType.XSS: [
                r"<\s*script[^>]*>.*?</\s*script\s*>",
                r"javascript\s*:",
                r"on\w+\s*=",
                r"<\s*iframe[^>]*>.*?</\s*iframe\s*>",
                r"<\s*object[^>]*>.*?</\s*object\s*>",
                r"<\s*embed[^>]*>",
                r"<\s*link[^>]*>",
                r"<\s*meta[^>]*>",
                r"<\s*img[^>]*onerror[^>]*>",
                r"alert\s*\(",
                r"confirm\s*\(",
                r"prompt\s*\(",
                r"document\.(cookie|domain|location)",
                r"window\.(location|open)",
                r"eval\s*\(",
                r"setTimeout\s*\(",
                r"setInterval\s*\(",
            ],
            ThreatType.COMMAND_INJECTION: [
                r"(;|\||&|`|\$\(|\$\{)",
                r"(cat|ls|ps|uname|id|pwd|whoami|nc|netcat|wget|curl)\s",
                r"(\.\./){2,}",
                r"/etc/(passwd|shadow|hosts|hostname)",
                r"/proc/",
                r"/bin/(sh|bash|csh|tcsh|zsh)",
                r"cmd(\.exe)?",
                r"powershell",
                r"wscript",
                r"cscript",
            ],
            ThreatType.PATH_TRAVERSAL: [
                r"(\.\./){2,}",
                r"\.\.[\\/]",
                r"[\\/]\.\.[\\/]",
                r"%2e%2e%2f",
                r"%2e%2e/",
                r"..%2f",
                r"%2e%2e%5c",
                r"..%5c",
                r"\.\.%5c",
            ],
            ThreatType.XXE: [
                r"<!ENTITY",
                r"SYSTEM\s+[\"'][^\"']*[\"']",
                r"PUBLIC\s+[\"'][^\"']*[\"']\s+[\"'][^\"']*[\"']",
                r"<!DOCTYPE[^>]+SYSTEM",
                r"&\w+;",
                r"file://",
                r"http://.*\.dtd",
                r"<!ELEMENT",
                r"<!ATTLIST",
            ],
            ThreatType.LDAP_INJECTION: [
                r"\*\)\(.*=",
                r"\)\(.*\*",
                r"\(\|\(",
                r"\)&\(",
                r"\(\&\(",
                r"\(\!\(",
                r"=\*\)",
                r">=\*\)",
                r"<=\*\)",
            ],
            ThreatType.NOSQL_INJECTION: [
                r"\$where",
                r"\$ne",
                r"\$gt",
                r"\$lt",
                r"\$gte",
                r"\$lte",
                r"\$exists",
                r"\$regex",
                r"\$or",
                r"\$and",
                r"\$not",
                r"\$nor",
                r"\$in",
                r"\$nin",
                r"javascript:",
                r"sleep\s*\(",
                r"benchmark\s*\(",
            ],
            ThreatType.SSRF: [
                r"(http|https|ftp|gopher|dict|file|ldap)://",
                r"(localhost|127\.0\.0\.1|0\.0\.0\.0|::1)",
                r"192\.168\.\d+\.\d+",
                r"10\.\d+\.\d+\.\d+",
                r"172\.(1[6-9]|2\d|3[01])\.\d+\.\d+",
                r"169\.254\.\d+\.\d+",
                r"metadata\.google\.internal",
                r"169\.254\.169\.254",
                r"@[^/]+",
            ],
        }

    async def analyze_request(self, request: RequestContext) -> List[SecurityDetection]:
        """Analyze request for security threats"""
        try:
            detections = []
            
            # Pattern-based detection
            pattern_detections = await self._pattern_based_detection(request)
            detections.extend(pattern_detections)
            
            # Behavioral analysis
            behavioral_detections = await self._behavioral_analysis(request)
            detections.extend(behavioral_detections)
            
            # Anomaly detection
            anomaly_detections = await self._anomaly_detection(request)
            detections.extend(anomaly_detections)
            
            return detections
            
        except Exception as e:
            logger.error(f"Request analysis failed: {e}")
            return []

    async def _pattern_based_detection(self, request: RequestContext) -> List[SecurityDetection]:
        """Pattern-based threat detection"""
        detections = []
        
        try:
            # Analyze different parts of the request
            analysis_targets = {
                "query_params": " ".join(f"{k}={v}" for k, v in request.query_params.items()),
                "headers": " ".join(f"{k}: {v}" for k, v in request.headers.items()),
                "body": request.body,
                "url": request.url,
                "user_agent": request.user_agent
            }
            
            for threat_type, patterns in self.attack_patterns.items():
                for pattern in patterns:
                    try:
                        compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                        
                        for location, content in analysis_targets.items():
                            if content:
                                matches = compiled_pattern.findall(content)
                                if matches:
                                    detection = SecurityDetection(
                                        threat_type=threat_type,
                                        severity=self._get_threat_severity(threat_type),
                                        confidence=0.8,
                                        matched_pattern=pattern,
                                        matched_location=location,
                                        matched_value=str(matches[0]) if matches else "",
                                        action_taken=self._get_default_action(threat_type),
                                        request_context=request
                                    )
                                    detections.append(detection)
                                    
                    except re.error as e:
                        logger.error(f"Invalid regex pattern: {pattern} - {e}")
                        continue
            
            return detections
            
        except Exception as e:
            logger.error(f"Pattern-based detection failed: {e}")
            return []

    async def _behavioral_analysis(self, request: RequestContext) -> List[SecurityDetection]:
        """Behavioral analysis for anomaly detection"""
        detections = []
        
        try:
            # User agent analysis
            if request.user_agent:
                ua_detections = await self._analyze_user_agent(request)
                detections.extend(ua_detections)
            
            # Request frequency analysis
            freq_detections = await self._analyze_request_frequency(request)
            detections.extend(freq_detections)
            
            # Parameter analysis
            param_detections = await self._analyze_parameters(request)
            detections.extend(param_detections)
            
            return detections
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
            return []

    async def _analyze_user_agent(self, request: RequestContext) -> List[SecurityDetection]:
        """Analyze user agent for suspicious patterns"""
        detections = []
        
        try:
            suspicious_agents = [
                "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
                "acunetix", "nessus", "openvas", "w3af", "skipfish",
                "dirb", "dirbuster", "gobuster", "wfuzz", "ffuf",
                "crawler", "spider", "bot", "scanner", "test"
            ]
            
            user_agent_lower = request.user_agent.lower()
            
            for suspicious in suspicious_agents:
                if suspicious in user_agent_lower:
                    detection = SecurityDetection(
                        threat_type=ThreatType.SCANNER_ACTIVITY,
                        severity=RuleSeverity.MEDIUM,
                        confidence=0.7,
                        matched_pattern=suspicious,
                        matched_location="user_agent",
                        matched_value=request.user_agent,
                        action_taken=SecurityAction.BLOCK,
                        request_context=request
                    )
                    detections.append(detection)
                    break
            
            # Check for empty or very short user agents
            if len(request.user_agent) < 10:
                detection = SecurityDetection(
                    threat_type=ThreatType.BOT_ACTIVITY,
                    severity=RuleSeverity.LOW,
                    confidence=0.5,
                    matched_pattern="short_user_agent",
                    matched_location="user_agent",
                    matched_value=request.user_agent,
                    action_taken=SecurityAction.CHALLENGE,
                    request_context=request
                )
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"User agent analysis failed: {e}")
            return []

    async def _analyze_request_frequency(self, request: RequestContext) -> List[SecurityDetection]:
        """Analyze request frequency for abuse detection"""
        detections = []
        
        try:
            # This would typically use historical data
            # For now, return empty list as placeholder
            return detections
            
        except Exception as e:
            logger.error(f"Request frequency analysis failed: {e}")
            return []

    async def _analyze_parameters(self, request: RequestContext) -> List[SecurityDetection]:
        """Analyze request parameters for suspicious content"""
        detections = []
        
        try:
            # Check for excessive parameter count
            total_params = len(request.query_params) + len(request.headers)
            
            if total_params > 50:  # Arbitrary threshold
                detection = SecurityDetection(
                    threat_type=ThreatType.BOT_ACTIVITY,
                    severity=RuleSeverity.LOW,
                    confidence=0.6,
                    matched_pattern="excessive_parameters",
                    matched_location="parameters",
                    matched_value=f"{total_params} parameters",
                    action_taken=SecurityAction.LOG_ONLY,
                    request_context=request
                )
                detections.append(detection)
            
            # Check for very long parameter values
            for key, value in request.query_params.items():
                if len(value) > 1000:  # Very long parameter value
                    detection = SecurityDetection(
                        threat_type=ThreatType.BOT_ACTIVITY,
                        severity=RuleSeverity.MEDIUM,
                        confidence=0.7,
                        matched_pattern="long_parameter_value",
                        matched_location="query_params",
                        matched_value=f"{key}={value[:100]}...",
                        action_taken=SecurityAction.BLOCK,
                        request_context=request
                    )
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Parameter analysis failed: {e}")
            return []

    async def _anomaly_detection(self, request: RequestContext) -> List[SecurityDetection]:
        """ML-based anomaly detection"""
        detections = []
        
        try:
            # Extract features for ML analysis
            features = self._extract_request_features(request)
            
            # Use simple heuristics for now (would use trained ML model in production)
            anomaly_score = await self._calculate_anomaly_score(features)
            
            if anomaly_score > 0.8:  # High anomaly score
                detection = SecurityDetection(
                    threat_type=ThreatType.BOT_ACTIVITY,
                    severity=RuleSeverity.MEDIUM,
                    confidence=anomaly_score,
                    matched_pattern="ml_anomaly",
                    matched_location="request",
                    matched_value=f"anomaly_score={anomaly_score:.2f}",
                    action_taken=SecurityAction.CHALLENGE,
                    request_context=request,
                    metadata={"features": features}
                )
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []

    def _extract_request_features(self, request: RequestContext) -> Dict[str, float]:
        """Extract numerical features from request for ML analysis"""
        try:
            features = {
                "url_length": len(request.url),
                "query_param_count": len(request.query_params),
                "header_count": len(request.headers),
                "body_length": len(request.body),
                "user_agent_length": len(request.user_agent),
                "hour_of_day": request.timestamp.hour,
                "is_post": 1.0 if request.method == "POST" else 0.0,
                "has_body": 1.0 if request.body else 0.0,
                "special_chars_in_url": len(re.findall(r'[<>"\';]', request.url)),
                "numeric_ratio_in_params": self._calculate_numeric_ratio(request.query_params)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}

    def _calculate_numeric_ratio(self, params: Dict[str, str]) -> float:
        """Calculate ratio of numeric characters in parameters"""
        try:
            if not params:
                return 0.0
            
            total_chars = 0
            numeric_chars = 0
            
            for value in params.values():
                total_chars += len(value)
                numeric_chars += sum(1 for c in value if c.isdigit())
            
            return numeric_chars / max(1, total_chars)
            
        except Exception:
            return 0.0

    async def _calculate_anomaly_score(self, features: Dict[str, float]) -> float:
        """Calculate anomaly score based on features"""
        try:
            # Simple heuristic scoring (would use trained ML model in production)
            score = 0.0
            
            # Long URLs are suspicious
            if features.get("url_length", 0) > 500:
                score += 0.3
            
            # Many parameters can be suspicious
            if features.get("query_param_count", 0) > 20:
                score += 0.2
            
            # Special characters in URL
            if features.get("special_chars_in_url", 0) > 5:
                score += 0.4
            
            # High numeric ratio might indicate injection attempts
            if features.get("numeric_ratio_in_params", 0) > 0.5:
                score += 0.2
            
            # Off-hours access (simplified)
            hour = features.get("hour_of_day", 12)
            if hour < 6 or hour > 22:  # Outside business hours
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Anomaly score calculation failed: {e}")
            return 0.0

    def _get_threat_severity(self, threat_type: ThreatType) -> RuleSeverity:
        """Get default severity for threat type"""
        severity_mapping = {
            ThreatType.SQL_INJECTION: RuleSeverity.CRITICAL,
            ThreatType.XSS: RuleSeverity.HIGH,
            ThreatType.COMMAND_INJECTION: RuleSeverity.CRITICAL,
            ThreatType.XXE: RuleSeverity.HIGH,
            ThreatType.PATH_TRAVERSAL: RuleSeverity.HIGH,
            ThreatType.SSRF: RuleSeverity.HIGH,
            ThreatType.LDAP_INJECTION: RuleSeverity.HIGH,
            ThreatType.NOSQL_INJECTION: RuleSeverity.HIGH,
            ThreatType.BRUTE_FORCE: RuleSeverity.MEDIUM,
            ThreatType.BOT_ACTIVITY: RuleSeverity.LOW,
            ThreatType.SCANNER_ACTIVITY: RuleSeverity.MEDIUM,
        }
        
        return severity_mapping.get(threat_type, RuleSeverity.MEDIUM)

    def _get_default_action(self, threat_type: ThreatType) -> SecurityAction:
        """Get default action for threat type"""
        action_mapping = {
            ThreatType.SQL_INJECTION: SecurityAction.BLOCK,
            ThreatType.XSS: SecurityAction.BLOCK,
            ThreatType.COMMAND_INJECTION: SecurityAction.BLOCK,
            ThreatType.XXE: SecurityAction.BLOCK,
            ThreatType.PATH_TRAVERSAL: SecurityAction.BLOCK,
            ThreatType.SSRF: SecurityAction.BLOCK,
            ThreatType.LDAP_INJECTION: SecurityAction.BLOCK,
            ThreatType.NOSQL_INJECTION: SecurityAction.BLOCK,
            ThreatType.BRUTE_FORCE: SecurityAction.RATE_LIMIT,
            ThreatType.BOT_ACTIVITY: SecurityAction.CHALLENGE,
            ThreatType.SCANNER_ACTIVITY: SecurityAction.BLOCK,
        }
        
        return action_mapping.get(threat_type, SecurityAction.LOG_ONLY)

class SecurityGateway:
    """
    Security gateway for processing requests through WAF rules.
    """
    
    def __init__(self):
        self.custom_rules: List[SecurityRule] = []
        self.rule_cache: Dict[str, SecurityRule] = {}
        
    async def add_rule(self, rule: SecurityRule) -> None:
        """Add custom security rule"""
        try:
            # Compile regex pattern
            if rule.pattern:
                rule.compiled_pattern = re.compile(rule.pattern, re.IGNORECASE | re.MULTILINE)
            
            self.custom_rules.append(rule)
            self.rule_cache[rule.rule_id] = rule
            
            logger.info(f"Added security rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Failed to add security rule: {e}")
            raise

    async def evaluate_rules(self, request: RequestContext) -> List[SecurityDetection]:
        """Evaluate custom security rules against request"""
        detections = []
        
        try:
            for rule in self.custom_rules:
                if not rule.enabled:
                    continue
                
                detection = await self._evaluate_rule(rule, request)
                if detection:
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Rule evaluation failed: {e}")
            return []

    async def _evaluate_rule(self, rule: SecurityRule, request: RequestContext) -> Optional[SecurityDetection]:
        """Evaluate single rule against request"""
        try:
            if not rule.compiled_pattern:
                return None
            
            # Check different parts of the request
            check_targets = {
                "url": request.url,
                "headers": " ".join(f"{k}: {v}" for k, v in request.headers.items()),
                "query_params": " ".join(f"{k}={v}" for k, v in request.query_params.items()),
                "body": request.body,
                "user_agent": request.user_agent
            }
            
            for location, content in check_targets.items():
                if content and rule.compiled_pattern.search(content):
                    match = rule.compiled_pattern.search(content)
                    matched_value = match.group(0) if match else ""
                    
                    return SecurityDetection(
                        rule_id=rule.rule_id,
                        threat_type=rule.threat_type,
                        severity=rule.severity,
                        confidence=rule.confidence,
                        matched_pattern=rule.pattern,
                        matched_location=location,
                        matched_value=matched_value,
                        action_taken=rule.action,
                        request_context=request,
                        metadata={"rule_name": rule.name, "rule_tags": rule.tags}
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Rule evaluation failed: {e}")
            return None

class WAFEngine:
    """
    Main WAF engine coordinating all security components.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379"
    ):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        
        # Initialize components
        self.rate_limiter = RateLimiter(redis_url)
        self.attack_detector = AttackDetector()
        self.security_gateway = SecurityGateway()
        
        # Request processing
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.blocked_ips: Set[str] = set()
        self.allowed_ips: Set[str] = set()
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "allowed_requests": 0,
            "rate_limited_requests": 0,
            "challenged_requests": 0,
            "detections_by_type": defaultdict(int),
            "processing_time_ms": deque(maxlen=1000)
        }
        
        # Configuration
        self.config = {
            "enable_rate_limiting": True,
            "enable_attack_detection": True,
            "enable_custom_rules": True,
            "enable_ip_filtering": True,
            "enable_geo_blocking": False,
            "challenge_timeout": 300,  # 5 minutes
            "block_duration": 3600,   # 1 hour
            "log_all_requests": False,
            "log_blocked_requests": True
        }

    async def initialize(self) -> None:
        """Initialize WAF engine"""
        try:
            # Initialize Redis connection
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Initialize components
            await self.rate_limiter.initialize()
            
            # Load IP filters
            await self._load_ip_filters()
            
            # Start background tasks
            asyncio.create_task(self._request_processor())
            asyncio.create_task(self._cleanup_task())
            
            logger.info("WAF engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WAF engine: {e}")
            raise

    async def process_request(self, request: RequestContext) -> Tuple[SecurityAction, List[SecurityDetection]]:
        """Process HTTP request through WAF"""
        try:
            start_time = time.time()
            self.stats["total_requests"] += 1
            
            detections = []
            action = SecurityAction.ALLOW
            
            # IP filtering
            if self.config["enable_ip_filtering"]:
                ip_action = await self._check_ip_filters(request.ip_address)
                if ip_action != SecurityAction.ALLOW:
                    action = ip_action
                    self._update_stats(action)
                    return action, detections
            
            # Rate limiting
            if self.config["enable_rate_limiting"]:
                rate_limit_action, rate_detections = await self._check_rate_limits(request)
                if rate_limit_action != SecurityAction.ALLOW:
                    action = rate_limit_action
                    detections.extend(rate_detections)
                    self._update_stats(action)
                    return action, detections
            
            # Attack detection
            if self.config["enable_attack_detection"]:
                attack_detections = await self.attack_detector.analyze_request(request)
                detections.extend(attack_detections)
            
            # Custom rules
            if self.config["enable_custom_rules"]:
                rule_detections = await self.security_gateway.evaluate_rules(request)
                detections.extend(rule_detections)
            
            # Determine final action based on detections
            if detections:
                action = self._determine_action(detections)
            
            # Log request if configured
            if self.config["log_all_requests"] or (self.config["log_blocked_requests"] and action == SecurityAction.BLOCK):
                await self._log_request(request, action, detections)
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self.stats["processing_time_ms"].append(processing_time)
            self._update_stats(action)
            
            for detection in detections:
                self.stats["detections_by_type"][detection.threat_type.value] += 1
            
            return action, detections
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return SecurityAction.ALLOW, []

    async def _check_ip_filters(self, ip_address: str) -> SecurityAction:
        """Check IP against allow/block lists"""
        try:
            # Check blocked IPs
            if ip_address in self.blocked_ips:
                return SecurityAction.BLOCK
            
            # Check if IP is temporarily blocked
            blocked_key = f"blocked_ip:{ip_address}"
            if await self.redis.exists(blocked_key):
                return SecurityAction.BLOCK
            
            # Check allowed IPs (if whitelist mode)
            if self.allowed_ips and ip_address not in self.allowed_ips:
                return SecurityAction.BLOCK
            
            return SecurityAction.ALLOW
            
        except Exception as e:
            logger.error(f"IP filter check failed: {e}")
            return SecurityAction.ALLOW

    async def _check_rate_limits(self, request: RequestContext) -> Tuple[SecurityAction, List[SecurityDetection]]:
        """Check request against rate limits"""
        try:
            detections = []
            
            # Check different rate limit types
            rate_checks = []
            
            # Per-IP rate limit
            ip_exceeded, ip_info = await self.rate_limiter.check_rate_limit(
                request.ip_address, "per_ip"
            )
            rate_checks.append(("per_ip", ip_exceeded, ip_info))
            
            # Per-user rate limit (if user is authenticated)
            if request.user_id:
                user_exceeded, user_info = await self.rate_limiter.check_rate_limit(
                    request.user_id, "per_user"
                )
                rate_checks.append(("per_user", user_exceeded, user_info))
            
            # API rate limit for API endpoints
            if "/api/" in request.url:
                api_key = request.user_id or request.ip_address
                api_exceeded, api_info = await self.rate_limiter.check_rate_limit(
                    api_key, "api"
                )
                rate_checks.append(("api", api_exceeded, api_info))
            
            # Check if any rate limit is exceeded
            for limit_type, exceeded, info in rate_checks:
                if exceeded:
                    detection = SecurityDetection(
                        threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
                        severity=RuleSeverity.MEDIUM,
                        confidence=1.0,
                        matched_pattern=f"{limit_type}_rate_limit",
                        matched_location="rate_limiter",
                        matched_value=f"limit_exceeded:{info.get('current_count', 0)}",
                        action_taken=SecurityAction.RATE_LIMIT,
                        request_context=request,
                        metadata={"rate_limit_info": info, "limit_type": limit_type}
                    )
                    detections.append(detection)
                    
                    return SecurityAction.RATE_LIMIT, detections
            
            return SecurityAction.ALLOW, detections
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return SecurityAction.ALLOW, []

    def _determine_action(self, detections: List[SecurityDetection]) -> SecurityAction:
        """Determine security action based on detections"""
        try:
            if not detections:
                return SecurityAction.ALLOW
            
            # Sort by severity (highest first)
            severity_order = [
                RuleSeverity.CRITICAL,
                RuleSeverity.HIGH,
                RuleSeverity.MEDIUM,
                RuleSeverity.LOW,
                RuleSeverity.INFO
            ]
            
            sorted_detections = sorted(
                detections,
                key=lambda d: severity_order.index(d.severity)
            )
            
            # Use action from highest severity detection
            highest_severity_detection = sorted_detections[0]
            
            # Override based on severity and confidence
            if (highest_severity_detection.severity == RuleSeverity.CRITICAL and
                highest_severity_detection.confidence >= 0.7):
                return SecurityAction.BLOCK
            elif (highest_severity_detection.severity == RuleSeverity.HIGH and
                  highest_severity_detection.confidence >= 0.8):
                return SecurityAction.BLOCK
            elif (highest_severity_detection.severity == RuleSeverity.MEDIUM and
                  highest_severity_detection.confidence >= 0.9):
                return SecurityAction.CHALLENGE
            else:
                return SecurityAction.LOG_ONLY
                
        except Exception as e:
            logger.error(f"Action determination failed: {e}")
            return SecurityAction.ALLOW

    async def _log_request(
        self,
        request: RequestContext,
        action: SecurityAction,
        detections: List[SecurityDetection]
    ) -> None:
        """Log request and security decision"""
        try:
            log_entry = {
                "request_id": request.request_id,
                "timestamp": request.timestamp.isoformat(),
                "method": request.method,
                "url": request.url,
                "ip_address": request.ip_address,
                "user_agent": request.user_agent,
                "action": action.value,
                "detections": [
                    {
                        "threat_type": d.threat_type.value,
                        "severity": d.severity.value,
                        "confidence": d.confidence,
                        "matched_pattern": d.matched_pattern,
                        "matched_location": d.matched_location
                    }
                    for d in detections
                ],
                "user_id": request.user_id,
                "session_id": request.session_id
            }
            
            # Store in Redis
            await self.redis.setex(
                f"waf_log:{request.request_id}",
                86400 * 7,  # Keep for 7 days
                json.dumps(log_entry, default=str)
            )
            
        except Exception as e:
            logger.error(f"Request logging failed: {e}")

    def _update_stats(self, action: SecurityAction) -> None:
        """Update WAF statistics"""
        try:
            if action == SecurityAction.ALLOW:
                self.stats["allowed_requests"] += 1
            elif action == SecurityAction.BLOCK:
                self.stats["blocked_requests"] += 1
            elif action == SecurityAction.RATE_LIMIT:
                self.stats["rate_limited_requests"] += 1
            elif action == SecurityAction.CHALLENGE:
                self.stats["challenged_requests"] += 1
                
        except Exception as e:
            logger.error(f"Stats update failed: {e}")

    async def _load_ip_filters(self) -> None:
        """Load IP allow/block lists"""
        try:
            # Load from Redis or configuration
            # This is a placeholder - in production, load from external sources
            
            # Example blocked IPs
            self.blocked_ips = set([
                "127.0.0.1",  # Placeholder - never actually block localhost
            ])
            
            # Example allowed IPs (empty means allow all)
            self.allowed_ips = set()
            
            logger.info(f"Loaded {len(self.blocked_ips)} blocked IPs")
            
        except Exception as e:
            logger.error(f"Failed to load IP filters: {e}")

    async def _request_processor(self) -> None:
        """Background request processor"""
        try:
            while True:
                try:
                    # Wait for requests in queue
                    request = await asyncio.wait_for(self.request_queue.get(), timeout=1.0)
                    
                    # Process request
                    await self.process_request(request)
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Request processing error: {e}")
                    
        except Exception as e:
            logger.error(f"Request processor failed: {e}")

    async def _cleanup_task(self) -> None:
        """Background cleanup task"""
        try:
            while True:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up old logs
                await self._cleanup_old_logs()
                
                # Clean up temporary blocks
                await self._cleanup_temporary_blocks()
                
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")

    async def _cleanup_old_logs(self) -> None:
        """Clean up old WAF logs"""
        try:
            # This would clean up logs older than retention period
            # Placeholder implementation
            pass
        except Exception as e:
            logger.error(f"Log cleanup failed: {e}")

    async def _cleanup_temporary_blocks(self) -> None:
        """Clean up expired temporary blocks"""
        try:
            # This would clean up expired temporary IP blocks
            # Placeholder implementation
            pass
        except Exception as e:
            logger.error(f"Temporary block cleanup failed: {e}")

    async def block_ip(self, ip_address: str, duration: int = 3600) -> None:
        """Temporarily block an IP address"""
        try:
            await self.redis.setex(f"blocked_ip:{ip_address}", duration, "waf_block")
            logger.info(f"Blocked IP {ip_address} for {duration} seconds")
        except Exception as e:
            logger.error(f"Failed to block IP {ip_address}: {e}")

    async def unblock_ip(self, ip_address: str) -> None:
        """Unblock an IP address"""
        try:
            await self.redis.delete(f"blocked_ip:{ip_address}")
            logger.info(f"Unblocked IP {ip_address}")
        except Exception as e:
            logger.error(f"Failed to unblock IP {ip_address}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get WAF statistics"""
        avg_processing_time = (
            sum(self.stats["processing_time_ms"]) / len(self.stats["processing_time_ms"])
            if self.stats["processing_time_ms"] else 0.0
        )
        
        total_processed = (
            self.stats["allowed_requests"] +
            self.stats["blocked_requests"] +
            self.stats["rate_limited_requests"] +
            self.stats["challenged_requests"]
        )
        
        return {
            "total_requests": self.stats["total_requests"],
            "allowed_requests": self.stats["allowed_requests"],
            "blocked_requests": self.stats["blocked_requests"],
            "rate_limited_requests": self.stats["rate_limited_requests"],
            "challenged_requests": self.stats["challenged_requests"],
            "block_rate": (
                self.stats["blocked_requests"] / max(1, total_processed)
            ),
            "average_processing_time_ms": avg_processing_time,
            "detections_by_type": dict(self.stats["detections_by_type"]),
            "blocked_ips_count": len(self.blocked_ips),
            "allowed_ips_count": len(self.allowed_ips),
            "queue_size": self.request_queue.qsize()
        }

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()
        await self.rate_limiter.cleanup()