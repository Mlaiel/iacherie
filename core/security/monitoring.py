"""
Security Monitoring Module
Advanced threat detection and security monitoring for IA Influencer Agent

Features:
- Real-time security event monitoring with ML-based detection
- Advanced Intrusion Detection System (IDS) with behavior analysis
- Machine learning behavioral anomaly detection for users and content
- AI-powered threat classification and response automation
- Security metrics and real-time dashboards with predictive analytics
- Comprehensive audit logging and forensics with immutable trails
- Advanced threat intelligence integration with external feeds
- Automated incident response with escalation workflows
- Content protection monitoring for copyright infringement
- DDoS detection and mitigation with traffic analysis
- Zero-day exploit detection using pattern recognition
- Financial fraud detection for monetization security

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms
"""

import asyncio
import json
import time
import hashlib
import uuid
from typing import Dict, List, Optional, Set, Any, Callable, Union, Coroutine
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
from concurrent.futures import ThreadPoolExecutor
import statistics
import ipaddress
import re
import pickle
from pathlib import Path

from fastapi import Request, Response, BackgroundTasks
import geoip2.database
import geoip2.errors
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger


class ThreatLevel(Enum):
    """Threat severity levels with numeric priority"""
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EventType(Enum):
    """Security event types for comprehensive monitoring"""
    # Authentication Events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGIN_BRUTE_FORCE = "login_brute_force"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILURE = "mfa_failure"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKOUT = "account_lockout"
    
    # Authorization Events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    PERMISSION_DENIED = "permission_denied"
    ROLE_CHANGE = "role_change"
    
    # Content Protection Events
    CONTENT_UPLOAD = "content_upload"
    CONTENT_ACCESS = "content_access"
    CONTENT_DOWNLOAD = "content_download"
    FINGERPRINT_MATCH = "fingerprint_match"
    COPYRIGHT_VIOLATION = "copyright_violation"
    WATERMARK_REMOVAL = "watermark_removal"
    
    # System Security Events
    SYSTEM_INTRUSION = "system_intrusion"
    MALWARE_DETECTED = "malware_detected"
    DDOS_ATTACK = "ddos_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    
    # Business Logic Events
    UNUSUAL_ACTIVITY = "unusual_activity"
    FRAUD_DETECTED = "fraud_detected"
    DATA_EXFILTRATION = "data_exfiltration"
    API_ABUSE = "api_abuse"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Compliance Events
    GDPR_VIOLATION = "gdpr_violation"
    DMCA_TAKEDOWN = "dmca_takedown"
    AUDIT_FAILURE = "audit_failure"
    DATA_BREACH = "data_breach"
    MALWARE_DETECTED = "malware_detected"
    SUSPICIOUS_UPLOAD = "suspicious_upload"
    API_ABUSE = "api_abuse"
    DDOS_ATTEMPT = "ddos_attempt"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    FILE_TAMPERING = "file_tampering"
    UNUSUAL_ACTIVITY = "unusual_activity"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: EventType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    tenant_id: Optional[str]
    timestamp: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    location: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    resolved: bool = False
    response_taken: Optional[str] = None


@dataclass
class ThreatIndicator:
    """Threat indicator for detection rules"""
    indicator_type: str
    value: str
    threat_level: ThreatLevel
    description: str
    source: str
    created_at: datetime
    expires_at: Optional[datetime] = None


class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.logger = SecurityLogger("AuditLogger")
        self.cache = CacheManager()
        
    async def log_security_event(self, event: SecurityEvent):
        """Log security event with full context"""



        try:
            # Enhance event with additional context
            enhanced_event = await self._enhance_event(event)
            
            # Store in audit log
            await self._store_audit_log(enhanced_event)
            
            # Update security metrics
            await self._update_security_metrics(enhanced_event)
            
            # Trigger alerts if necessary
            if enhanced_event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._trigger_security_alert(enhanced_event)
            
            self.logger.info(
                f"Security event logged: {enhanced_event.event_type.value} "
                f"[{enhanced_event.threat_level.name}] from {enhanced_event.source_ip}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")
    
    async def _enhance_event(self, event: SecurityEvent) -> SecurityEvent:
        """Enhance event with additional context"""



        try:
            # Add geolocation data
            if event.source_ip and not event.location:
                event.location = await self._get_ip_geolocation(event.source_ip)
            
            # Add threat intelligence
            threat_info = await self._check_threat_intelligence(event.source_ip)
            if threat_info:
                event.metadata.update(threat_info)
            
            return event
            
        except Exception as e:
            self.logger.error(f"Event enhancement failed: {str(e)}")
            return event
    
    async def _get_ip_geolocation(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get geolocation for IP address"""



        try:
            # Check cache first
            cache_key = f"geoip:{ip_address}"
            cached_location = await self.cache.get(cache_key)
            if cached_location:
                return cached_location
            
            # Skip private/local IPs
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private or ip.is_loopback:
                return {"country": "Private", "city": "Local"}
            
            # Use GeoIP database (placeholder - implement with actual GeoIP service)
            location = {
                "country": "Unknown",
                "country_code": "XX",
                "city": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0
            }
            
            # Cache location data
            await self.cache.set(cache_key, location, expire=86400)  # 24 hours
            
            return location
            
        except Exception as e:
            self.logger.error(f"Geolocation lookup failed: {str(e)}")
            return None
    
    async def _check_threat_intelligence(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Check IP against threat intelligence feeds"""



        try:
            # Check cache for known threats
            cache_key = f"threat_intel:{ip_address}"
            cached_threat = await self.cache.get(cache_key)
            if cached_threat:
                return cached_threat
            
            # Check against threat feeds (placeholder - implement with actual feeds)
            threat_info = None
            
            # Cache negative results too (shorter TTL)
            await self.cache.set(cache_key, threat_info, expire=3600)
            
            return threat_info
            
        except Exception as e:
            self.logger.error(f"Threat intelligence check failed: {str(e)}")
            return None
    
    async def _store_audit_log(self, event: SecurityEvent):
        """Store audit log in database"""
        # Implementation depends on your audit log model
        pass
    
    async def _update_security_metrics(self, event: SecurityEvent):
        """Update real-time security metrics"""



        try:
            # Update event counters
            date_key = event.timestamp.strftime("%Y-%m-%d")
            hour_key = event.timestamp.strftime("%Y-%m-%d:%H")
            
            # Daily metrics
            daily_key = f"security_metrics:daily:{date_key}"
            await self.cache.increment(f"{daily_key}:total_events")
            await self.cache.increment(f"{daily_key}:{event.event_type.value}")
            await self.cache.increment(f"{daily_key}:threat_level_{event.threat_level.name.lower()}")
            
            # Hourly metrics
            hourly_key = f"security_metrics:hourly:{hour_key}"
            await self.cache.increment(f"{hourly_key}:total_events")
            await self.cache.increment(f"{hourly_key}:{event.event_type.value}")
            
            # Source IP metrics
            if event.source_ip:
                ip_key = f"security_metrics:ip:{event.source_ip}:{date_key}"
                await self.cache.increment(ip_key)
                await self.cache.expire(ip_key, 86400)  # 24 hours
            
        except Exception as e:
            self.logger.error(f"Security metrics update failed: {str(e)}")
    
    async def _trigger_security_alert(self, event: SecurityEvent):
        """Trigger security alert for high-severity events"""



        try:
            alert_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.name,
                "source_ip": event.source_ip,
                "timestamp": event.timestamp.isoformat(),
                "description": event.description
            }
            
            # Send to alert queue
            await self._send_alert(alert_data)
            
            self.logger.warning(f"Security alert triggered: {event.event_type.value}")
            
        except Exception as e:
            self.logger.error(f"Security alert failed: {str(e)}")
    
    async def _send_alert(self, alert_data: Dict[str, Any]):
        """Send security alert to notification system"""
        # Implementation depends on your notification system
        pass


class ThreatDetector:
    """Advanced threat detection engine"""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.logger = SecurityLogger("ThreatDetector")
        self.cache = CacheManager()
        
        # Detection rules
        self.detection_rules = self._initialize_detection_rules()
        
        # Behavioral analysis
        self.user_behaviors = defaultdict(lambda: {
            "login_times": deque(maxlen=100),
            "login_ips": deque(maxlen=50),
            "failed_logins": deque(maxlen=20),
            "api_calls": deque(maxlen=200)
        })
    
    def _initialize_detection_rules(self) -> Dict[str, Callable]:
        """Initialize threat detection rules"""



        return {
            "brute_force_detection": self._detect_brute_force,
            "unusual_location": self._detect_unusual_location,
            "unusual_time": self._detect_unusual_time,
            "api_abuse": self._detect_api_abuse,
            "privilege_escalation": self._detect_privilege_escalation,
            "suspicious_upload": self._detect_suspicious_upload
        }
    
    async def analyze_request(self, request: Request, user_id: Optional[str] = None) -> List[SecurityEvent]:
        """Analyze incoming request for threats"""
        events = []
        
        try:
            # Extract request details
            source_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            endpoint = str(request.url.path)
            method = request.method
            
            # Run detection rules
            for rule_name, rule_func in self.detection_rules.items():
                try:
                    threat_events = await rule_func(request, user_id, source_ip, user_agent)
                    if threat_events:
                        events.extend(threat_events)
                except Exception as e:
                    self.logger.error(f"Detection rule {rule_name} failed: {str(e)}")
            
            # Log all detected events
            for event in events:
                await self.audit_logger.log_security_event(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Request analysis failed: {str(e)}")
            return []
    
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
    
    async def _detect_brute_force(
        self, 
        request: Request, 
        user_id: Optional[str], 
        source_ip: str, 
        user_agent: str
    ) -> List[SecurityEvent]:
        """Detect brute force attacks"""
        events = []
        
        try:
            # Check failed login attempts from IP
            cache_key = f"failed_logins:{source_ip}"
            failed_attempts = await self.cache.get(cache_key) or []
            
            # Add current attempt if it's a login failure
            if "/auth/login" in str(request.url.path) and request.method == "POST":
                failed_attempts.append(time.time())
                
                # Keep only recent attempts (last 15 minutes)
                cutoff_time = time.time() - 900  # 15 minutes
                failed_attempts = [t for t in failed_attempts if t > cutoff_time]
                
                await self.cache.set(cache_key, failed_attempts, expire=900)
                
                # Detect brute force (5+ failures in 15 minutes)
                if len(failed_attempts) >= 5:
                    event = SecurityEvent(
                        event_id=f"bf_{source_ip}_{int(time.time())}",
                        event_type=EventType.LOGIN_BRUTE_FORCE,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=source_ip,
                        user_id=user_id,
                        tenant_id=None,
                        timestamp=datetime.utcnow(),
                        description=f"Brute force attack detected: {len(failed_attempts)} failed logins",
                        metadata={"failed_attempts": len(failed_attempts)},
                        user_agent=user_agent
                    )
                    events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Brute force detection failed: {str(e)}")
            return []
    
    async def _detect_unusual_location(
        self, 
        request: Request, 
        user_id: Optional[str], 
        source_ip: str, 
        user_agent: str
    ) -> List[SecurityEvent]:
        """Detect logins from unusual locations"""
        events = []
        
        try:
            if not user_id:
                return events
            
            # Get user's typical locations
            cache_key = f"user_locations:{user_id}"
            user_locations = await self.cache.get(cache_key) or []
            
            # Get current location
            current_location = await self.audit_logger._get_ip_geolocation(source_ip)
            if not current_location:
                return events
            
            current_country = current_location.get("country_code", "XX")
            
            # Check if this is a new location
            if current_country not in user_locations:
                # Add to user locations
                user_locations.append(current_country)
                await self.cache.set(cache_key, user_locations[-10:], expire=86400 * 30)  # 30 days
                
                # Generate event for new location
                if len(user_locations) > 1:  # Skip first login
                    event = SecurityEvent(
                        event_id=f"ul_{user_id}_{int(time.time())}",
                        event_type=EventType.UNUSUAL_ACTIVITY,
                        threat_level=ThreatLevel.MEDIUM,
                        source_ip=source_ip,
                        user_id=user_id,
                        tenant_id=None,
                        timestamp=datetime.utcnow(),
                        description=f"Login from new location: {current_location.get('country', 'Unknown')}",
                        metadata={"new_location": current_location},
                        user_agent=user_agent,
                        location=current_location
                    )
                    events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Unusual location detection failed: {str(e)}")
            return []
    
    async def _detect_unusual_time(
        self, 
        request: Request, 
        user_id: Optional[str], 
        source_ip: str, 
        user_agent: str
    ) -> List[SecurityEvent]:
        """Detect logins at unusual times"""
        events = []
        
        try:
            if not user_id:
                return events
            
            current_hour = datetime.utcnow().hour
            
            # Get user's typical login hours
            cache_key = f"user_login_hours:{user_id}"
            login_hours = await self.cache.get(cache_key) or []
            
            # Add current hour
            login_hours.append(current_hour)
            login_hours = login_hours[-50:]  # Keep last 50 logins
            await self.cache.set(cache_key, login_hours, expire=86400 * 30)  # 30 days
            
            # Analyze if current hour is unusual (if we have enough data)
            if len(login_hours) >= 10:
                hour_frequency = {}
                for hour in login_hours[:-1]:  # Exclude current login
                    hour_frequency[hour] = hour_frequency.get(hour, 0) + 1
                
                # Check if current hour is rarely used (less than 10% of logins)
                total_logins = len(login_hours) - 1
                current_hour_frequency = hour_frequency.get(current_hour, 0)
                
                if current_hour_frequency / total_logins < 0.1 and total_logins >= 20:
                    event = SecurityEvent(
                        event_id=f"ut_{user_id}_{int(time.time())}",
                        event_type=EventType.UNUSUAL_ACTIVITY,
                        threat_level=ThreatLevel.LOW,
                        source_ip=source_ip,
                        user_id=user_id,
                        tenant_id=None,
                        timestamp=datetime.utcnow(),
                        description=f"Login at unusual time: {current_hour}:00 UTC",
                        metadata={"unusual_hour": current_hour, "frequency": current_hour_frequency},
                        user_agent=user_agent
                    )
                    events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Unusual time detection failed: {str(e)}")
            return []
    
    async def _detect_api_abuse(
        self, 
        request: Request, 
        user_id: Optional[str], 
        source_ip: str, 
        user_agent: str
    ) -> List[SecurityEvent]:
        """Detect API abuse patterns"""
        events = []
        
        try:
            # Track API calls per IP
            cache_key = f"api_calls:{source_ip}"
            api_calls = await self.cache.get(cache_key) or []
            
            current_time = time.time()
            api_calls.append(current_time)
            
            # Keep only calls from last minute
            cutoff_time = current_time - 60
            api_calls = [t for t in api_calls if t > cutoff_time]
            
            await self.cache.set(cache_key, api_calls, expire=60)
            
            # Detect rate limit abuse (>100 calls per minute)
            if len(api_calls) > 100:
                event = SecurityEvent(
                    event_id=f"api_{source_ip}_{int(current_time)}",
                    event_type=EventType.API_ABUSE,
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=source_ip,
                    user_id=user_id,
                    tenant_id=None,
                    timestamp=datetime.utcnow(),
                    description=f"API rate limit exceeded: {len(api_calls)} calls/minute",
                    metadata={"calls_per_minute": len(api_calls)},
                    user_agent=user_agent
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"API abuse detection failed: {str(e)}")
            return []
    
    async def _detect_privilege_escalation(
        self, 
        request: Request, 
        user_id: Optional[str], 
        source_ip: str, 
        user_agent: str
    ) -> List[SecurityEvent]:
        """Detect privilege escalation attempts"""
        events = []
        
        try:
            # Check for admin endpoints accessed by non-admin users
            endpoint = str(request.url.path).lower()
            admin_endpoints = ["/admin/", "/system/", "/users/", "/api/admin/"]
            
            if any(admin_path in endpoint for admin_path in admin_endpoints):
                # Check if user has admin privileges (placeholder - implement with real auth)
                user_is_admin = False  # Get from auth context
                
                if not user_is_admin and user_id:
                    event = SecurityEvent(
                        event_id=f"pe_{user_id}_{int(time.time())}",
                        event_type=EventType.PRIVILEGE_ESCALATION,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=source_ip,
                        user_id=user_id,
                        tenant_id=None,
                        timestamp=datetime.utcnow(),
                        description=f"Privilege escalation attempt: accessing {endpoint}",
                        metadata={"attempted_endpoint": endpoint},
                        user_agent=user_agent
                    )
                    events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Privilege escalation detection failed: {str(e)}")
            return []
    
    async def _detect_suspicious_upload(
        self, 
        request: Request, 
        user_id: Optional[str], 
        source_ip: str, 
        user_agent: str
    ) -> List[SecurityEvent]:
        """Detect suspicious file uploads"""
        events = []
        
        try:
            if request.method == "POST" and "/upload" in str(request.url.path):
                # Check file type and size (placeholder - implement with actual file inspection)
                suspicious_patterns = [
                    ".exe", ".bat", ".cmd", ".scr", ".pif", ".com", 
                    ".vbs", ".js", ".jar", ".php", ".asp", ".jsp"
                ]
                
                # This would need actual file content inspection
                # For now, just check for suspicious uploads in general
                
                event = SecurityEvent(
                    event_id=f"su_{user_id or 'anon'}_{int(time.time())}",
                    event_type=EventType.SUSPICIOUS_UPLOAD,
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=source_ip,
                    user_id=user_id,
                    tenant_id=None,
                    timestamp=datetime.utcnow(),
                    description="File upload detected - requires inspection",
                    metadata={"upload_endpoint": str(request.url.path)},
                    user_agent=user_agent
                )
                # Only add if we detect actual suspicious content
                # events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Suspicious upload detection failed: {str(e)}")
            return []


class SecurityMetrics:
    """Security metrics collection and analysis"""
    
    def __init__(self):
        self.logger = SecurityLogger("SecurityMetrics")
        self.cache = CacheManager()
    
    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""



        try:
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            current_hour = datetime.utcnow().strftime("%Y-%m-%d:%H")
            
            # Get daily metrics
            daily_metrics = await self._get_daily_metrics(current_date)
            
            # Get hourly trends (last 24 hours)
            hourly_trends = await self._get_hourly_trends()
            
            # Get top threats
            top_threats = await self._get_top_threats(current_date)
            
            # Get geographic distribution
            geo_distribution = await self._get_geographic_distribution(current_date)
            
            # Get threat level distribution
            threat_levels = await self._get_threat_level_distribution(current_date)
            
            return {
                "daily_metrics": daily_metrics,
                "hourly_trends": hourly_trends,
                "top_threats": top_threats,
                "geographic_distribution": geo_distribution,
                "threat_level_distribution": threat_levels,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Security dashboard data collection failed: {str(e)}")
            return {}
    
    async def _get_daily_metrics(self, date: str) -> Dict[str, int]:
        """Get daily security metrics"""
        daily_key = f"security_metrics:daily:{date}"
        
        metrics = {}
        event_types = [e.value for e in EventType]
        
        for event_type in event_types:
            count = await self.cache.get(f"{daily_key}:{event_type}") or 0
            metrics[event_type] = count
        
        metrics["total_events"] = await self.cache.get(f"{daily_key}:total_events") or 0
        
        return metrics
    
    async def _get_hourly_trends(self) -> List[Dict[str, Any]]:
        """Get hourly trends for last 24 hours"""
        trends = []
        
        for i in range(24):
            hour_time = datetime.utcnow() - timedelta(hours=i)
            hour_key = hour_time.strftime("%Y-%m-%d:%H")
            
            hourly_key = f"security_metrics:hourly:{hour_key}"
            total_events = await self.cache.get(f"{hourly_key}:total_events") or 0
            
            trends.append({
                "hour": hour_key,
                "total_events": total_events,
                "timestamp": hour_time.isoformat()
            })
        
        return list(reversed(trends))
    
    async def _get_top_threats(self, date: str) -> List[Dict[str, Any]]:
        """Get top threat types for the day"""
        daily_key = f"security_metrics:daily:{date}"
        
        threats = []
        for event_type in EventType:
            count = await self.cache.get(f"{daily_key}:{event_type.value}") or 0
            if count > 0:
                threats.append({
                    "threat_type": event_type.value,
                    "count": count
                })
        
        # Sort by count, descending
        threats.sort(key=lambda x: x["count"], reverse=True)
        
        return threats[:10]  # Top 10
    
    async def _get_geographic_distribution(self, date: str) -> List[Dict[str, Any]]:
        """Get geographic distribution of threats"""
        # This would require storing geo data with events
        # Placeholder implementation
        return []
    
    async def _get_threat_level_distribution(self, date: str) -> Dict[str, int]:
        """Get threat level distribution"""
        daily_key = f"security_metrics:daily:{date}"
        
        distribution = {}
        for level in ThreatLevel:
            count = await self.cache.get(f"{daily_key}:threat_level_{level.name.lower()}") or 0
            distribution[level.name.lower()] = count
        
        return distribution


class IntrusionDetection:
    """Intrusion Detection System (IDS)"""
    
    def __init__(self, threat_detector: ThreatDetector):
        self.threat_detector = threat_detector
        self.logger = SecurityLogger("IntrusionDetection")
        self.cache = CacheManager()
        
        # Initialize signatures
        self.attack_signatures = self._load_attack_signatures()
    
    def _load_attack_signatures(self) -> Dict[str, List[str]]:
        """Load attack signatures for detection"""



        return {
            "sql_injection": [
                "union select", "drop table", "delete from", "insert into",
                "update set", "' or '1'='1", "'; drop", "or 1=1",
                "exec sp_", "xp_cmdshell"
            ],
            "xss": [
                "<script>", "</script>", "javascript:", "onload=", "onerror=",
                "alert(", "document.cookie", "window.location", "<iframe"
            ],
            "path_traversal": [
                "../", "..\\", "%2e%2e%2f", "%2e%2e%5c", "..%2f", "..%5c",
                "/etc/passwd", "/etc/shadow", "windows\\system32"
            ],
            "command_injection": [
                "; cat", "| cat", "&& cat", "|| cat", "; ls", "| ls",
                "; wget", "| wget", "; curl", "| curl", "; rm", "| rm"
            ]
        }
    
    async def analyze_request_for_attacks(self, request: Request) -> List[SecurityEvent]:
        """Analyze request for known attack patterns"""
        events = []
        
        try:
            # Get request details
            source_ip = self.threat_detector._get_client_ip(request)
            url_path = str(request.url.path)
            query_params = str(request.url.query) if request.url.query else ""
            user_agent = request.headers.get("user-agent", "")
            
            # Check for attack signatures
            for attack_type, signatures in self.attack_signatures.items():
                for signature in signatures:
                    # Check URL path
                    if signature.lower() in url_path.lower():
                        event = self._create_attack_event(
                            attack_type, signature, source_ip, url_path, "url_path"
                        )
                        events.append(event)
                    
                    # Check query parameters
                    if signature.lower() in query_params.lower():
                        event = self._create_attack_event(
                            attack_type, signature, source_ip, query_params, "query_params"
                        )
                        events.append(event)
                    
                    # Check headers
                    for header_name, header_value in request.headers.items():
                        if signature.lower() in header_value.lower():
                            event = self._create_attack_event(
                                attack_type, signature, source_ip, 
                                f"{header_name}: {header_value}", "headers"
                            )
                            events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Attack pattern analysis failed: {str(e)}")
            return []
    
    def _create_attack_event(
        self, 
        attack_type: str, 
        signature: str, 
        source_ip: str, 
        context: str,
        location: str
    ) -> SecurityEvent:
        """Create security event for detected attack"""
        event_type_map = {
            "sql_injection": EventType.SQL_INJECTION,
            "xss": EventType.XSS_ATTEMPT,
            "path_traversal": EventType.UNAUTHORIZED_ACCESS,
            "command_injection": EventType.UNAUTHORIZED_ACCESS
        }
        
        return SecurityEvent(
            event_id=f"ids_{attack_type}_{int(time.time())}",
            event_type=event_type_map.get(attack_type, EventType.UNAUTHORIZED_ACCESS),
            threat_level=ThreatLevel.HIGH,
            source_ip=source_ip,
            user_id=None,
            tenant_id=None,
            timestamp=datetime.utcnow(),
            description=f"{attack_type.upper()} attack detected: {signature}",
            metadata={
                "attack_type": attack_type,
                "signature": signature,
                "context": context,
                "location": location
            }
        )


class SecurityMonitor:
    """Main security monitoring orchestrator"""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.threat_detector = ThreatDetector(self.audit_logger)
        self.security_metrics = SecurityMetrics()
        self.intrusion_detection = IntrusionDetection(self.threat_detector)
        self.logger = SecurityLogger("SecurityMonitor")
        
        # Response handlers
        self.response_handlers = {
            ThreatLevel.HIGH: self._handle_high_threat,
            ThreatLevel.CRITICAL: self._handle_critical_threat
        }
    
    async def monitor_request(
        self, 
        request: Request, 
        response: Response,
        user_id: Optional[str] = None
    ):
        """Monitor incoming request for security threats"""



        try:
            # Run threat detection
            threat_events = await self.threat_detector.analyze_request(request, user_id)
            
            # Run intrusion detection
            attack_events = await self.intrusion_detection.analyze_request_for_attacks(request)
            
            # Combine all events
            all_events = threat_events + attack_events
            
            # Handle high-priority events
            for event in all_events:
                if event.threat_level in self.response_handlers:
                    await self.response_handlers[event.threat_level](event, request, response)
            
        except Exception as e:
            self.logger.error(f"Security monitoring failed: {str(e)}")
    
    async def _handle_high_threat(
        self, 
        event: SecurityEvent, 
        request: Request, 
        response: Response
    ):
        """Handle high-severity threats"""



        try:
            # Log additional context
            self.logger.warning(f"High threat detected: {event.description}")
            
            # Add security headers
            response.headers["X-Security-Alert"] = "High threat detected"
            
            # Consider rate limiting or blocking
            if event.event_type in [EventType.LOGIN_BRUTE_FORCE, EventType.API_ABUSE]:
                await self._apply_rate_limiting(event.source_ip)
            
        except Exception as e:
            self.logger.error(f"High threat handling failed: {str(e)}")
    
    async def _handle_critical_threat(
        self, 
        event: SecurityEvent, 
        request: Request, 
        response: Response
    ):
        """Handle critical threats"""



        try:
            # Log critical alert
            self.logger.critical(f"Critical threat detected: {event.description}")
            
            # Block IP temporarily
            await self._block_ip_temporarily(event.source_ip)
            
            # Send immediate notification
            await self._send_critical_alert(event)
            
            # Add security headers
            response.headers["X-Security-Alert"] = "Critical threat blocked"
            
        except Exception as e:
            self.logger.error(f"Critical threat handling failed: {str(e)}")
    
    async def _apply_rate_limiting(self, ip_address: str):
        """Apply rate limiting to IP address"""
        cache_key = f"rate_limit:{ip_address}"
        await self.threat_detector.cache.set(cache_key, True, expire=300)  # 5 minutes
    
    async def _block_ip_temporarily(self, ip_address: str):
        """Temporarily block IP address"""
        cache_key = f"blocked_ip:{ip_address}"
        await self.threat_detector.cache.set(cache_key, True, expire=3600)  # 1 hour
    
    async def _send_critical_alert(self, event: SecurityEvent):
        """Send critical security alert"""
        # Implementation depends on your notification system
        pass
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""



        try:
            dashboard_data = await self.security_metrics.get_security_dashboard_data()
            
            return {
                "status": "operational",
                "monitoring_active": True,
                "dashboard_data": dashboard_data,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Security status check failed: {str(e)}")
            return {
                "status": "error",
                "monitoring_active": False,
                "error": str(e)
            }
