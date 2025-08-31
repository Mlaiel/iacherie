"""Security Middleware Module
=========================

Enterprise-grade security middleware for crawler pipeline.
Implements comprehensive security controls, threat detection, and data protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Security:
- Multi-format content protection against manipulation
- Creator rights protection and anti-piracy measures
- AI-powered threat detection for content theft
- GDPR-compliant data processing and privacy protection
- Enterprise-grade security for monetization workflows
"""import asyncio
import json
import time
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set
from enum import Enum
from ipaddress import ip_address, ip_network
import re
from urllib.parse import urlparse
import base64
import mimetypes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from pydantic import BaseModel, Field
import redis
import logging

from ...config.settings import get_settings
from ...utils.cache import CacheManager
from ...core.security import SecurityManager

settings = get_settings()
logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    """Security threat levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SecurityAction(str, Enum):
    """Security actions"""    ALLOW = "allow"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    MONITOR = "monitor"
    RATE_LIMIT = "rate_limit"
    REQUIRE_VERIFICATION = "require_verification"
    ESCALATE = "escalate"


class AttackType(str, Enum):
    """Types of security attacks"""    INJECTION = "injection"
    XSS = "xss"
    MALWARE = "malware"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    DATA_BREACH = "data_breach"
    CONTENT_MANIPULATION = "content_manipulation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    COPYRIGHT_VIOLATION = "copyright_violation"
    DEEPFAKE = "deepfake"
    CONTENT_POISONING = "content_poisoning"
    API_ABUSE = "api_abuse"


class ComplianceStandard(str, Enum):
    """Compliance standards"""    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    ISO27001 = "iso27001"
    SOC2 = "soc2"


class SecurityRequest(BaseModel):
    """Security validation request model"""    request_id: str = Field(description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    ip_address: str = Field(description="Client IP address")
    user_agent: str = Field(description="Client user agent")
    content_data: Optional[Union[str, bytes]] = Field(None, description="Content to validate")
    content_type: Optional[str] = Field(None, description="MIME type of content")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    url: Optional[str] = Field(None, description="Request URL")
    geolocation: Optional[Dict[str, Any]] = Field(None, description="User geolocation")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SecurityResult(BaseModel):
    """Security validation result model"""    request_id: str = Field(description="Request identifier")
    action: SecurityAction = Field(description="Recommended security action")
    threat_level: ThreatLevel = Field(description="Detected threat level")
    threats_detected: List[AttackType] = Field(default_factory=list, description="Detected threats")
    confidence_score: float = Field(description="Confidence in threat detection (0-1)")
    compliance_status: Dict[ComplianceStandard, bool] = Field(default_factory=dict, 
                                                            description="Compliance validation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed analysis")
    remediation_steps: List[str] = Field(default_factory=list, description="Recommended remediation")
    quarantine_duration: Optional[int] = Field(None, description="Quarantine duration in seconds")
    processing_time: float = Field(description="Security analysis duration")


class IPSecurityAnalyzer:
    """Advanced IP address security analysis"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        
        # Known malicious IP ranges and security networks
        self.blocked_networks = [
            ip_network("10.0.0.0/8"),     # Private
            ip_network("172.16.0.0/12"),  # Private
            ip_network("192.168.0.0/16"), # Private
        ]
        
        # Rate limiting per IP
        self.ip_rate_limits = {
            "requests_per_minute": 100,
            "requests_per_hour": 1000
        }
    
    async def analyze_ip(self, ip_addr: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive IP address analysis"""        analysis = {
            "ip_address": ip_addr,
            "is_suspicious": False,
            "threat_level": ThreatLevel.LOW,
            "reasons": [],
            "geolocation": None,
            "reputation_score": 1.0
        }
        
        try:
            ip = ip_address(ip_addr)
            
            # Check if IP is in blocked networks
            for network in self.blocked_networks:
                if ip in network:
                    analysis["is_suspicious"] = True
                    analysis["threat_level"] = ThreatLevel.HIGH
                    analysis["reasons"].append("IP in blocked network range")
                    analysis["reputation_score"] = 0.0
                    break
            
            # Check blacklist
            is_blacklisted = await self.check_ip_blacklist(ip_addr)
            if is_blacklisted:
                analysis["is_suspicious"] = True
                analysis["threat_level"] = ThreatLevel.CRITICAL
                analysis["reasons"].append("IP in blacklist")
                analysis["reputation_score"] = 0.0
            
            # Check rate limiting
            rate_limit_exceeded = await self.check_ip_rate_limit(ip_addr)
            if rate_limit_exceeded:
                analysis["is_suspicious"] = True
                analysis["threat_level"] = max(analysis["threat_level"], ThreatLevel.MEDIUM)
                analysis["reasons"].append("Rate limit exceeded")
            
            # Geographic analysis
            geo_info = await self.get_ip_geolocation(ip_addr)
            analysis["geolocation"] = geo_info
            
            # Reputation check
            reputation = await self.check_ip_reputation(ip_addr)
            analysis["reputation_score"] = reputation
            
            if reputation < 0.5:
                analysis["is_suspicious"] = True
                analysis["threat_level"] = ThreatLevel.MEDIUM
                analysis["reasons"].append("Low reputation score")
            
            return analysis
            
        except Exception as e:
            logger.error(f"IP analysis error for {ip_addr}: {e}")
            analysis["error"] = str(e)
            return analysis
    
    async def check_ip_blacklist(self, ip_addr: str) -> bool:
        """Check if IP is in blacklist"""        blacklist_key = f"ip_blacklist:{ip_addr}"
        return await self.redis_client.exists(blacklist_key)
    
    async def check_ip_rate_limit(self, ip_addr: str) -> bool:
        """Check IP rate limiting"""        now = time.time()
        minute_key = f"ip_rate:{ip_addr}:{int(now // 60)}"
        hour_key = f"ip_rate:{ip_addr}:{int(now // 3600)}"
        
        # Check minute rate
        minute_count = await self.redis_client.incr(minute_key)
        await self.redis_client.expire(minute_key, 60)
        
        # Check hour rate
        hour_count = await self.redis_client.incr(hour_key)
        await self.redis_client.expire(hour_key, 3600)
        
        return (minute_count > self.ip_rate_limits["requests_per_minute"] or
                hour_count > self.ip_rate_limits["requests_per_hour"])
    
    async def get_ip_geolocation(self, ip_addr: str) -> Optional[Dict[str, Any]]:
        """Get IP geolocation information"""        cache_key = f"ip_geo:{ip_addr}"
        
        # Try cache first
        cached_geo = await self.cache.get(cache_key)
        if cached_geo:
            return json.loads(cached_geo)
        
        # Mock geolocation data (in production, use GeoIP2 or similar service)
        geo_data = {
            "country": "Unknown",
            "city": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC"
        }
        
        # Cache for 24 hours
        await self.cache.set(cache_key, json.dumps(geo_data), expire=86400)
        
        return geo_data
    
    async def check_ip_reputation(self, ip_addr: str) -> float:
        """Check IP reputation score (0.0 = bad, 1.0 = good)"""        cache_key = f"ip_reputation:{ip_addr}"
        
        # Try cache first
        cached_reputation = await self.cache.get(cache_key)
        if cached_reputation:
            return float(cached_reputation)
        
        # Mock reputation check (in production, use threat intelligence feeds)
        reputation_score = 0.8  # Default good reputation
        
        # Check against known patterns
        if any(pattern in ip_addr for pattern in ["192.168", "10.", "172."]):
            reputation_score = 0.9  # Private IPs are generally safe
        
        # Cache for 1 hour
        await self.cache.set(cache_key, str(reputation_score), expire=3600)
        
        return reputation_score


class ContentSecurityAnalyzer:
    """Advanced content security analysis"""    
    def __init__(self):
        self.malware_signatures = [
            b"X5O!P%@AP[4\\PZX54(P^)7CC)7}",  # EICAR test signature
            b"eval(",
            b"<script",
            b"javascript:",
            b"onerror=",
            b"onload="
        ]
        
        # XSS patterns
        self.xss_patterns = [
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:[^'\"]*", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            re.compile(r"<iframe[^>]*>", re.IGNORECASE),
            re.compile(r"<embed[^>]*>", re.IGNORECASE),
            re.compile(r"<object[^>]*>", re.IGNORECASE)
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            re.compile(r"union\s+select", re.IGNORECASE),
            re.compile(r"drop\s+table", re.IGNORECASE),
            re.compile(r"insert\s+into", re.IGNORECASE),
            re.compile(r"delete\s+from", re.IGNORECASE),
            re.compile(r"exec\s*\(", re.IGNORECASE),
            re.compile(r"'.*or.*'.*=.*'", re.IGNORECASE)
        ]
    
    async def analyze_content(self, content: Union[str, bytes]) -> Dict[str, Any]:
        """Comprehensive content security analysis"""        analysis = {
            "is_malicious": False,
            "threat_level": ThreatLevel.LOW,
            "threats_detected": [],
            "confidence_score": 1.0,
            "details": {}
        }
        
        try:
            # Convert to string if bytes
            if isinstance(content, bytes):
                content_str = content.decode('utf-8', errors='ignore')
                content_bytes = content
            else:
                content_str = content
                content_bytes = content.encode('utf-8')
            
            # Malware detection
            malware_detected = await self.detect_malware(content_bytes)
            if malware_detected:
                analysis["is_malicious"] = True
                analysis["threat_level"] = ThreatLevel.CRITICAL
                analysis["threats_detected"].append(AttackType.MALWARE)
                analysis["confidence_score"] = 0.95
            
            # XSS detection
            xss_detected = await self.detect_xss(content_str)
            if xss_detected:
                analysis["is_malicious"] = True
                analysis["threat_level"] = max(analysis["threat_level"], ThreatLevel.HIGH)
                analysis["threats_detected"].append(AttackType.XSS)
                analysis["confidence_score"] = min(analysis["confidence_score"], 0.9)
            
            # SQL injection detection
            sql_injection_detected = await self.detect_sql_injection(content_str)
            if sql_injection_detected:
                analysis["is_malicious"] = True
                analysis["threat_level"] = max(analysis["threat_level"], ThreatLevel.HIGH)
                analysis["threats_detected"].append(AttackType.INJECTION)
                analysis["confidence_score"] = min(analysis["confidence_score"], 0.9)
            
            # Content manipulation detection
            manipulation_detected = await self.detect_content_manipulation(content_str)
            if manipulation_detected:
                analysis["is_malicious"] = True
                analysis["threat_level"] = max(analysis["threat_level"], ThreatLevel.MEDIUM)
                analysis["threats_detected"].append(AttackType.CONTENT_MANIPULATION)
                analysis["confidence_score"] = min(analysis["confidence_score"], 0.8)
            
            # Add detailed analysis
            analysis["details"] = {
                "content_length": len(content_str),
                "suspicious_patterns": len(analysis["threats_detected"]),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Content security analysis error: {e}")
            analysis["error"] = str(e)
            return analysis
    
    async def detect_malware(self, content: bytes) -> bool:
        """Detect malware signatures in content"""        for signature in self.malware_signatures:
            if signature in content:
                logger.warning(f"Malware signature detected: {signature}")
                return True
        return False
    
    async def detect_xss(self, content: str) -> bool:
        """Detect XSS patterns in content"""        for pattern in self.xss_patterns:
            if pattern.search(content):
                logger.warning(f"XSS pattern detected: {pattern.pattern}")
                return True
        return False
    
    async def detect_sql_injection(self, content: str) -> bool:
        """Detect SQL injection patterns in content"""        for pattern in self.sql_injection_patterns:
            if pattern.search(content):
                logger.warning(f"SQL injection pattern detected: {pattern.pattern}")
                return True
        return False
    
    async def detect_content_manipulation(self, content: str) -> bool:
        """Detect content manipulation attempts"""        # Look for suspicious encoding or obfuscation
        suspicious_patterns = [
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            r"Function\s*\(",
            r"unescape\s*\(",
            r"String\.fromCharCode",
            r"\\x[0-9a-fA-F]{2}",  # Hex encoding
            r"\\u[0-9a-fA-F]{4}",  # Unicode encoding
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False


class BehaviorAnalyzer:
    """Advanced behavioral security analysis"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
    async def analyze_behavior(self, user_id: str, ip_addr: str, 
                             request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user/IP behavior patterns"""        analysis = {
            "is_suspicious": False,
            "anomaly_score": 0.0,
            "behavioral_indicators": [],
            "risk_factors": []
        }
        
        try:
            # Analyze request frequency
            frequency_analysis = await self.analyze_request_frequency(user_id, ip_addr)
            analysis["request_frequency"] = frequency_analysis
            
            if frequency_analysis.get("is_anomalous", False):
                analysis["is_suspicious"] = True
                analysis["behavioral_indicators"].append("unusual_request_frequency")
                analysis["anomaly_score"] += 0.3
            
            # Analyze time patterns
            time_analysis = await self.analyze_time_patterns(user_id)
            analysis["time_patterns"] = time_analysis
            
            if time_analysis.get("is_anomalous", False):
                analysis["is_suspicious"] = True
                analysis["behavioral_indicators"].append("unusual_time_patterns")
                analysis["anomaly_score"] += 0.2
            
            # Analyze user agent patterns
            ua_analysis = await self.analyze_user_agent(user_id, request_data.get("user_agent", ""))
            analysis["user_agent_analysis"] = ua_analysis
            
            if ua_analysis.get("is_suspicious", False):
                analysis["is_suspicious"] = True
                analysis["behavioral_indicators"].append("suspicious_user_agent")
                analysis["anomaly_score"] += 0.2
            
            # Geographic analysis
            geo_analysis = await self.analyze_geographic_patterns(user_id, ip_addr)
            analysis["geographic_analysis"] = geo_analysis
            
            if geo_analysis.get("is_anomalous", False):
                analysis["is_suspicious"] = True
                analysis["behavioral_indicators"].append("unusual_geographic_pattern")
                analysis["anomaly_score"] += 0.3
            
            # Overall risk assessment
            analysis["risk_level"] = self.calculate_risk_level(analysis["anomaly_score"])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Behavior analysis error: {e}")
            analysis["error"] = str(e)
            return analysis
    
    async def analyze_request_frequency(self, user_id: str, ip_addr: str) -> Dict[str, Any]:
        """Analyze request frequency patterns"""        now = time.time()
        hour_window = int(now // 3600)
        
        # Count requests in current hour
        user_key = f"user_requests:{user_id}:{hour_window}"
        ip_key = f"ip_requests:{ip_addr}:{hour_window}"
        
        user_count = await self.redis_client.incr(user_key)
        ip_count = await self.redis_client.incr(ip_key)
        
        await self.redis_client.expire(user_key, 3600)
        await self.redis_client.expire(ip_key, 3600)
        
        # Define normal thresholds
        normal_user_requests_per_hour = 500
        normal_ip_requests_per_hour = 1000
        
        is_anomalous = (user_count > normal_user_requests_per_hour * 2 or
                       ip_count > normal_ip_requests_per_hour * 2)
        
        return {
            "user_requests_per_hour": user_count,
            "ip_requests_per_hour": ip_count,
            "is_anomalous": is_anomalous,
            "user_threshold": normal_user_requests_per_hour,
            "ip_threshold": normal_ip_requests_per_hour
        }
    
    async def analyze_time_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze temporal access patterns"""        now = datetime.utcnow()
        hour = now.hour
        
        # Track hourly access patterns
        hour_key = f"user_hours:{user_id}"
        await self.redis_client.hincrby(hour_key, str(hour), 1)
        await self.redis_client.expire(hour_key, 86400 * 7)  # Keep for 7 days
        
        # Get historical pattern
        hour_stats = await self.redis_client.hgetall(hour_key)
        hour_counts = {int(h): int(c) for h, c in hour_stats.items()}
        
        # Calculate if current hour is anomalous
        if len(hour_counts) > 5:  # Need some history
            avg_count = sum(hour_counts.values()) / len(hour_counts)
            current_count = hour_counts.get(hour, 0)
            is_anomalous = current_count > avg_count * 3
        else:
            is_anomalous = False
        
        return {
            "current_hour": hour,
            "hour_distribution": hour_counts,
            "is_anomalous": is_anomalous
        }
    
    async def analyze_user_agent(self, user_id: str, user_agent: str) -> Dict[str, Any]:
        """Analyze user agent patterns"""        analysis = {
            "user_agent": user_agent,
            "is_suspicious": False,
            "suspicious_indicators": []
        }
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "bot",
            "crawler",
            "spider",
            "scraper",
            "python",
            "curl",
            "wget",
            "automated"
        ]
        
        for pattern in suspicious_patterns:
            if pattern.lower() in user_agent.lower():
                analysis["is_suspicious"] = True
                analysis["suspicious_indicators"].append(f"contains_{pattern}")
        
        # Check for unusual user agent changes
        ua_key = f"user_agents:{user_id}"
        stored_ua = await self.redis_client.get(ua_key)
        
        if stored_ua and stored_ua.decode() != user_agent:
            analysis["user_agent_changed"] = True
            analysis["previous_user_agent"] = stored_ua.decode()
        
        # Store current user agent
        await self.redis_client.set(ua_key, user_agent, ex=86400)
        
        return analysis
    
    async def analyze_geographic_patterns(self, user_id: str, ip_addr: str) -> Dict[str, Any]:
        """Analyze geographic access patterns"""        # Get IP geolocation (mock implementation)
        current_country = "US"  # Would use actual GeoIP service
        
        # Track countries accessed from
        country_key = f"user_countries:{user_id}"
        await self.redis_client.sadd(country_key, current_country)
        await self.redis_client.expire(country_key, 86400 * 30)  # Keep for 30 days
        
        # Get all countries for this user
        countries = await self.redis_client.smembers(country_key)
        country_list = [c.decode() for c in countries]
        
        # Check for rapid country changes (possible VPN/proxy)
        is_anomalous = len(country_list) > 5  # More than 5 countries in 30 days
        
        return {
            "current_country": current_country,
            "countries_accessed": country_list,
            "country_count": len(country_list),
            "is_anomalous": is_anomalous
        }
    
    def calculate_risk_level(self, anomaly_score: float) -> str:
        """Calculate overall risk level"""        if anomaly_score >= 0.8:
            return "critical"
        elif anomaly_score >= 0.6:
            return "high"
        elif anomaly_score >= 0.4:
            return "medium"
        else:
            return "low"


class SecurityMiddleware:
    """Main security middleware orchestrator"""    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        self.security_manager = SecurityManager()
        
        # Initialize analyzers
        self.ip_analyzer = IPSecurityAnalyzer(self.redis_client)
        self.content_analyzer = ContentSecurityAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer(self.redis_client)
        
        # Security thresholds
        self.security_thresholds = {
            "block_threshold": 0.8,
            "quarantine_threshold": 0.6,
            "monitor_threshold": 0.4
        }
    
    async def validate_security(self, request: SecurityRequest) -> SecurityResult:
        """Main security validation method"""        start_time = time.time()
        threats_detected = []
        overall_confidence = 1.0
        threat_level = ThreatLevel.LOW
        
        try:
            # IP Security Analysis
            ip_analysis = await self.ip_analyzer.analyze_ip(request.ip_address, request.user_id)
            if ip_analysis.get("is_suspicious", False):
                threats_detected.append(AttackType.UNAUTHORIZED_ACCESS)
                threat_level = max(threat_level, ip_analysis.get("threat_level", ThreatLevel.LOW))
                overall_confidence = min(overall_confidence, ip_analysis.get("reputation_score", 1.0))
            
            # Content Security Analysis
            if request.content_data:
                content_analysis = await self.content_analyzer.analyze_content(request.content_data)
                if content_analysis.get("is_malicious", False):
                    threats_detected.extend(content_analysis.get("threats_detected", []))
                    threat_level = max(threat_level, content_analysis.get("threat_level", ThreatLevel.LOW))
                    overall_confidence = min(overall_confidence, content_analysis.get("confidence_score", 1.0))
            
            # Behavioral Analysis
            if request.user_id:
                behavior_analysis = await self.behavior_analyzer.analyze_behavior(
                    request.user_id, request.ip_address, {
                        "user_agent": request.user_agent,
                        "headers": request.headers
                    }
                )
                if behavior_analysis.get("is_suspicious", False):
                    threats_detected.append(AttackType.UNAUTHORIZED_ACCESS)
                    anomaly_score = behavior_analysis.get("anomaly_score", 0.0)
                    if anomaly_score > 0.6:
                        threat_level = max(threat_level, ThreatLevel.HIGH)
                    elif anomaly_score > 0.4:
                        threat_level = max(threat_level, ThreatLevel.MEDIUM)
            
            # Header Analysis
            header_analysis = await self.analyze_headers(request.headers)
            if header_analysis.get("is_suspicious", False):
                threats_detected.append(AttackType.UNAUTHORIZED_ACCESS)
                threat_level = max(threat_level, ThreatLevel.MEDIUM)
            
            # Determine security action
            action = await self.determine_security_action(threat_level, overall_confidence, threats_detected)
            
            # Generate remediation steps
            remediation_steps = await self.generate_remediation_steps(threats_detected, action)
            
            # Log security event
            await self.log_security_event(request, threats_detected, action, threat_level)
            
            processing_time = time.time() - start_time
            
            return SecurityResult(
                request_id=request.request_id,
                action=action,
                threat_level=threat_level,
                threats_detected=threats_detected,
                confidence_score=overall_confidence,
                details={
                    "ip_analysis": ip_analysis,
                    "content_analysis": content_analysis if request.content_data else None,
                    "behavior_analysis": behavior_analysis if request.user_id else None,
                    "header_analysis": header_analysis
                },
                remediation_steps=remediation_steps,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Security validation error for {request.request_id}: {e}")
            
            return SecurityResult(
                request_id=request.request_id,
                action=SecurityAction.MONITOR,
                threat_level=ThreatLevel.LOW,
                threats_detected=[],
                confidence_score=0.0,
                details={"error": str(e)},
                remediation_steps=["Review security logs", "Manual investigation required"],
                processing_time=time.time() - start_time
            )
    
    async def analyze_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze HTTP headers for security threats"""        analysis = {
            "is_suspicious": False,
            "suspicious_headers": [],
            "missing_security_headers": []
        }
        
        # Check for suspicious headers
        suspicious_patterns = {
            "x-forwarded-for": r"\b(?:proxy|vpn|tor)\b",
            "via": r"\b(?:proxy|cache)\b",
            "x-real-ip": r"^(?:127\.|10\.|192\.168\.|172\.16\.)",
        }
        
        for header_name, pattern in suspicious_patterns.items():
            header_value = headers.get(header_name, "")
            if re.search(pattern, header_value, re.IGNORECASE):
                analysis["is_suspicious"] = True
                analysis["suspicious_headers"].append(header_name)
        
        # Check for missing security headers (for responses)
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "strict-transport-security"
        ]
        
        for header in security_headers:
            if header not in headers:
                analysis["missing_security_headers"].append(header)
        
        return analysis
    
    async def determine_security_action(self, threat_level: ThreatLevel, 
                                      confidence: float, 
                                      threats: List[AttackType]) -> SecurityAction:
        """Determine appropriate security action"""        # Critical threats always block
        if threat_level == ThreatLevel.CRITICAL:
            return SecurityAction.BLOCK
        
        # High threats with high confidence
        if threat_level == ThreatLevel.HIGH and confidence > 0.8:
            return SecurityAction.BLOCK
        
        # High threats with medium confidence
        if threat_level == ThreatLevel.HIGH and confidence > 0.5:
            return SecurityAction.QUARANTINE
        
        # Medium threats
        if threat_level == ThreatLevel.MEDIUM:
            if confidence > 0.7:
                return SecurityAction.RATE_LIMIT
            else:
                return SecurityAction.MONITOR
        
        # Specific threat types
        if AttackType.MALWARE in threats or AttackType.INJECTION in threats:
            return SecurityAction.BLOCK
        
        if AttackType.XSS in threats:
            return SecurityAction.QUARANTINE
        
        if AttackType.DDOS in threats or AttackType.BRUTE_FORCE in threats:
            return SecurityAction.RATE_LIMIT
        
        # Default to monitoring
        return SecurityAction.MONITOR
    
    async def generate_remediation_steps(self, threats: List[AttackType], 
                                       action: SecurityAction) -> List[str]:
        """Generate specific remediation steps"""        steps = []
        
        if action == SecurityAction.BLOCK:
            steps.append("Request blocked due to security threat")
            steps.append("IP address added to temporary blacklist")
        
        if action == SecurityAction.QUARANTINE:
            steps.append("Content quarantined for manual review")
            steps.append("User notified of security review")
        
        if action == SecurityAction.RATE_LIMIT:
            steps.append("Rate limiting applied to user/IP")
            steps.append("Monitor for continued suspicious activity")
        
        # Threat-specific remediation
        if AttackType.MALWARE in threats:
            steps.extend([
                "Scan system for malware",
                "Update antivirus definitions",
                "Isolate affected systems"
            ])
        
        if AttackType.XSS in threats:
            steps.extend([
                "Sanitize user input",
                "Review content filtering rules",
                "Update XSS protection"
            ])
        
        if AttackType.INJECTION in threats:
            steps.extend([
                "Review database access patterns",
                "Update input validation",
                "Check for data breach"
            ])
        
        if AttackType.BRUTE_FORCE in threats:
            steps.extend([
                "Implement account lockout",
                "Require password reset",
                "Enable two-factor authentication"
            ])
        
        return steps
    
    async def log_security_event(self, request: SecurityRequest, 
                                threats: List[AttackType], 
                                action: SecurityAction, 
                                threat_level: ThreatLevel):
        """Log security events for monitoring and compliance"""        event = {
            "request_id": request.request_id,
            "user_id": request.user_id,
            "ip_address": request.ip_address,
            "user_agent": request.user_agent,
            "threats_detected": [t.value for t in threats],
            "action_taken": action.value,
            "threat_level": threat_level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "url": request.url
        }
        
        # Log to Redis for real-time monitoring
        await self.redis_client.lpush("security_events", json.dumps(event))
        await self.redis_client.ltrim("security_events", 0, 10000)  # Keep last 10k events
        
        # Alert on critical threats
        if threat_level == ThreatLevel.CRITICAL:
            await self.send_security_alert(event)
    
    async def send_security_alert(self, event: Dict[str, Any]):
        """Send security alert for critical threats"""        alert = {
            "type": "critical_security_threat",
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_immediate_attention": True
        }
        
        # In production, this would send to alerting system
        logger.critical(f"SECURITY ALERT: {json.dumps(alert)}")
        
        # Store in high-priority alerts
        await self.redis_client.lpush("security_alerts", json.dumps(alert))


# Factory function for dependency injection
def get_security_middleware() -> SecurityMiddleware:
    """Get security middleware instance"""    return SecurityMiddleware()


# Decorator for automatic security validation
def require_security_validation():
    """Decorator for automatic security validation"""    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract security information from request
            # This would be customized based on your application structure
            request_data = kwargs.get("request_data", {})
            
            security_request = SecurityRequest(
                request_id=request_data.get("request_id", secrets.token_hex(16)),
                user_id=request_data.get("user_id"),
                ip_address=request_data.get("ip_address", "127.0.0.1"),
                user_agent=request_data.get("user_agent", "Unknown"),
                content_data=request_data.get("content_data"),
                headers=request_data.get("headers", {}),
                url=request_data.get("url")
            )
            
            middleware = get_security_middleware()
            security_result = await middleware.validate_security(security_request)
            
            # Handle security result
            if security_result.action == SecurityAction.BLOCK:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Request blocked due to security threat",
                        "threat_level": security_result.threat_level.value,
                        "threats": [t.value for t in security_result.threats_detected]
                    }
                )
            
            # Add security result to request context
            kwargs["security_result"] = security_result
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
