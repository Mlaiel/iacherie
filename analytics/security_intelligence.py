"""Security Intelligence
===================

Advanced platform security analytics and threat detection system.
Monitors security threats, compliance, and audit trail analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import hashlib
import ipaddress
import redis
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


class ThreatLevel(Enum):
    """Security threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    MALWARE_UPLOAD = "malware_upload"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    PHISHING_ATTEMPT = "phishing_attempt"
    INSIDER_THREAT = "insider_threat"
    API_ABUSE = "api_abuse"
    ACCOUNT_TAKEOVER = "account_takeover"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMPLIANCE_VIOLATION = "compliance_violation"
    FRAUDULENT_CONTENT = "fraudulent_content"


class SecurityEventType(Enum):
    """Types of security events"""
    LOGIN_ATTEMPT = "login_attempt"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    FILE_UPLOAD = "file_upload"
    API_REQUEST = "api_request"
    ADMIN_ACTION = "admin_action"
    CONFIGURATION_CHANGE = "configuration_change"
    AUDIT_LOG_ACCESS = "audit_log_access"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_CREATION = "account_creation"
    ACCOUNT_DELETION = "account_deletion"
    PAYMENT_TRANSACTION = "payment_transaction"
    CONTENT_MODERATION = "content_moderation"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    NIST = "nist"
    COPPA = "coppa"
    FERPA = "ferpa"


@dataclass
class SecurityEvent:
    """Individual security event"""
    event_id: str
    event_type: SecurityEventType
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    endpoint: str
    status_code: int
    timestamp: datetime
    session_id: Optional[str] = None
    risk_score: float = 0.0
    geolocation: Dict[str, str] = field(default_factory=dict)
    request_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatEvent:
    """Security threat detection event"""
    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    target_resource: str
    description: str
    evidence: Dict[str, Any]
    affected_users: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)
    resolved: bool = False
    false_positive: bool = False
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    analyst_notes: str = ""


@dataclass
class ComplianceEvent:
    """Compliance monitoring event"""
    compliance_id: str
    framework: ComplianceFramework
    requirement: str
    status: str  # "compliant", "non_compliant", "warning"
    violation_details: Optional[str] = None
    remediation_steps: List[str] = field(default_factory=list)
    responsible_party: str = ""
    due_date: Optional[datetime] = None
    assessed_at: datetime = field(default_factory=datetime.now)
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityMetrics:
    """Comprehensive security analytics metrics"""
    time_period: Tuple[datetime, datetime]
    total_security_events: int = 0
    total_threats_detected: int = 0
    threats_by_type: Dict[str, int] = field(default_factory=dict)
    threats_by_level: Dict[str, int] = field(default_factory=dict)
    false_positive_rate: float = 0.0
    mean_time_to_detection: float = 0.0  # hours
    mean_time_to_response: float = 0.0   # hours
    successful_attacks: int = 0
    blocked_attacks: int = 0
    attack_success_rate: float = 0.0
    top_attack_sources: List[Dict[str, Any]] = field(default_factory=list)
    compliance_score: float = 0.0
    audit_findings: Dict[str, int] = field(default_factory=dict)
    user_risk_distribution: Dict[str, int] = field(default_factory=dict)
    security_incidents: List[Dict[str, Any]] = field(default_factory=list)


class SecurityIntelligenceEngine:
    """
    Advanced security intelligence and threat detection analytics engine.
    
    Provides comprehensive security monitoring, threat detection,
    compliance tracking, and audit trail analytics.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.security_events = deque(maxlen=1000000)  # Large capacity for security events
        self.threat_events = deque(maxlen=100000)
        self.compliance_events = deque(maxlen=50000)
        self.metrics_history = deque(maxlen=1000)
        
        # Threat detection models
        self.anomaly_detector = None
        self.threat_classifier = None
        self.risk_scorer = None
        
        # Redis for real-time security monitoring
        self.redis_client = None
        self._initialize_redis()
        
        # Security baselines and thresholds
        self.security_thresholds = {
            "max_failed_logins": 5,
            "max_requests_per_minute": 100,
            "suspicious_locations": ["TOR", "VPN"],
            "high_risk_countries": ["CN", "RU", "IR", "KP"],
            "max_session_duration": 24,  # hours
            "anomaly_threshold": 0.95,
            "risk_score_threshold": 0.8
        }
        
        # Known malicious patterns
        self.malicious_patterns = {
            "sql_injection": [
                "' OR '1'='1",
                "UNION SELECT",
                "DROP TABLE",
                "INSERT INTO",
                "DELETE FROM"
            ],
            "xss_patterns": [
                "<script>",
                "javascript:",
                "onerror=",
                "onload=",
                "eval("
            ],
            "path_traversal": [
                "../",
                "..\\",
                "/etc/passwd",
                "/etc/shadow",
                "C:\\Windows\\System32"
            ]
        }
        
        # Compliance requirements mapping
        self.compliance_requirements = {
            ComplianceFramework.GDPR: {
                "data_encryption": "Data must be encrypted in transit and at rest",
                "consent_management": "User consent must be documented and manageable",
                "data_retention": "Data retention policies must be enforced",
                "breach_notification": "Breaches must be reported within 72 hours",
                "right_to_deletion": "Users must be able to request data deletion"
            },
            ComplianceFramework.PCI_DSS: {
                "payment_encryption": "Payment data must be encrypted",
                "access_control": "Strict access controls for payment systems",
                "network_security": "Secure network architecture required",
                "regular_testing": "Regular security testing mandatory",
                "security_monitoring": "Continuous monitoring required"
            }
        }
        
        # Initialize ML models
        self._ml_models_initialized = False
    
    def _initialize_redis(self):
        """Initialize Redis connection for real-time security monitoring"""
        try:
            redis_host = self.config.get("redis_host", "localhost")
            redis_port = self.config.get("redis_port", 6379)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for security analytics"""
        try:
            if self._ml_models_initialized:
                return
            
            # Anomaly detection for unusual behavior
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Threat classification
            self.threat_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            
            # Clustering for behavioral analysis
            self.behavior_clusterer = DBSCAN(
                eps=0.3,
                min_samples=5
            )
            
            self._ml_models_initialized = True
            self.logger.info("Security ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    async def log_security_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        endpoint: str,
        status_code: int,
        session_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecurityEvent:
        """Log a security event for monitoring and analysis"""
        try:
            event_id = f"sec_{int(datetime.now().timestamp())}_{hash(f'{user_id}{ip_address}') % 100000}"
            
            # Get geolocation for IP
            geolocation = await self._get_ip_geolocation(ip_address)
            
            # Calculate initial risk score
            risk_score = await self._calculate_event_risk_score(
                event_type, user_id, ip_address, endpoint, status_code
            )
            
            event = SecurityEvent(
                event_id=event_id,
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                status_code=status_code,
                timestamp=datetime.now(),
                session_id=session_id,
                risk_score=risk_score,
                geolocation=geolocation,
                request_data=request_data or {},
                response_data=response_data or {},
                metadata=metadata or {}
            )
            
            # Store event
            self.security_events.append(event)
            
            # Cache in Redis for real-time monitoring
            if self.redis_client:
                await self._cache_security_event(event)
            
            # Check for threats in real-time
            await self._check_for_threats(event)
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
            raise
    
    async def _get_ip_geolocation(self, ip_address: str) -> Dict[str, str]:
        """Get geolocation information for IP address"""
        try:
            # Check if IP is private/local
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private or ip.is_loopback:
                return {"country": "LOCAL", "city": "LOCAL", "region": "LOCAL"}
            
            # In production, would use actual geolocation service
            # For simulation, return mock data
            return {
                "country": "US",
                "city": "San Francisco",
                "region": "California",
                "latitude": "37.7749",
                "longitude": "-122.4194"
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting geolocation for {ip_address}: {e}")
            return {"country": "UNKNOWN", "city": "UNKNOWN", "region": "UNKNOWN"}
    
    async def _calculate_event_risk_score(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str],
        ip_address: str,
        endpoint: str,
        status_code: int
    ) -> float:
        """Calculate risk score for security event"""
        try:
            risk_score = 0.0
            
            # Base risk by event type
            event_risks = {
                SecurityEventType.LOGIN_ATTEMPT: 0.2,
                SecurityEventType.ACCESS_DENIED: 0.6,
                SecurityEventType.PERMISSION_CHANGE: 0.8,
                SecurityEventType.ADMIN_ACTION: 0.7,
                SecurityEventType.CONFIGURATION_CHANGE: 0.9,
                SecurityEventType.FILE_UPLOAD: 0.4,
                SecurityEventType.API_REQUEST: 0.1
            }
            
            risk_score += event_risks.get(event_type, 0.3)
            
            # IP-based risk factors
            if await self._is_suspicious_ip(ip_address):
                risk_score += 0.5
            
            # Status code risk
            if status_code >= 400:
                risk_score += 0.3
            if status_code >= 500:
                risk_score += 0.2
            
            # Endpoint risk
            if any(pattern in endpoint.lower() for pattern in ['/admin', '/api/internal', '/config']):
                risk_score += 0.4
            
            # User behavior risk (if user identified)
            if user_id:
                user_risk = await self._calculate_user_risk(user_id)
                risk_score += user_risk * 0.3
            
            # Anonymous access risk
            if not user_id and event_type not in [SecurityEventType.LOGIN_ATTEMPT]:
                risk_score += 0.2
            
            return min(1.0, risk_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 0.5  # Default moderate risk
    
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            # Check against known bad IP ranges (simplified)
            suspicious_ranges = [
                "10.0.0.0/8",    # Often used in attacks
                "192.168.0.0/16" # Sometimes suspicious depending on context
            ]
            
            ip = ipaddress.ip_address(ip_address)
            
            # Check if IP is in suspicious ranges
            for range_str in suspicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
            
            # Check geolocation for high-risk countries
            geolocation = await self._get_ip_geolocation(ip_address)
            if geolocation.get("country") in self.security_thresholds["high_risk_countries"]:
                return True
            
            # Check for TOR/VPN indicators
            if geolocation.get("city") in self.security_thresholds["suspicious_locations"]:
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking suspicious IP {ip_address}: {e}")
            return False
    
    async def _calculate_user_risk(self, user_id: str) -> float:
        """Calculate risk score for specific user"""
        try:
            # Get recent user events
            user_events = [
                event for event in list(self.security_events)[-1000:]  # Last 1000 events
                if event.user_id == user_id
                and (datetime.now() - event.timestamp).days <= 7  # Last 7 days
            ]
            
            if not user_events:
                return 0.3  # Default risk for unknown users
            
            risk_factors = 0.0
            
            # Failed login attempts
            failed_logins = len([e for e in user_events 
                               if e.event_type == SecurityEventType.LOGIN_ATTEMPT 
                               and e.status_code >= 400])
            
            if failed_logins > self.security_thresholds["max_failed_logins"]:
                risk_factors += 0.4
            
            # Multiple IP addresses
            user_ips = set(e.ip_address for e in user_events)
            if len(user_ips) > 5:  # More than 5 IPs in 7 days
                risk_factors += 0.3
            
            # High frequency of requests
            requests_per_day = len(user_events) / 7
            if requests_per_day > 1000:  # Very high activity
                risk_factors += 0.2
            
            # Access denied events
            denied_events = len([e for e in user_events if e.status_code == 403])
            if denied_events > 10:
                risk_factors += 0.3
            
            return min(1.0, risk_factors)
            
        except Exception as e:
            self.logger.error(f"Error calculating user risk for {user_id}: {e}")
            return 0.5
    
    async def _check_for_threats(self, event: SecurityEvent):
        """Check if security event indicates a potential threat"""
        try:
            threats_detected = []
            
            # Check for brute force attacks
            if await self._detect_brute_force(event):
                threats_detected.append(ThreatType.BRUTE_FORCE_ATTACK)
            
            # Check for SQL injection
            if await self._detect_sql_injection(event):
                threats_detected.append(ThreatType.SQL_INJECTION)
            
            # Check for XSS attacks
            if await self._detect_xss_attack(event):
                threats_detected.append(ThreatType.XSS_ATTACK)
            
            # Check for API abuse
            if await self._detect_api_abuse(event):
                threats_detected.append(ThreatType.API_ABUSE)
            
            # Check for unauthorized access
            if await self._detect_unauthorized_access(event):
                threats_detected.append(ThreatType.UNAUTHORIZED_ACCESS)
            
            # Create threat events for detected threats
            for threat_type in threats_detected:
                await self._create_threat_event(threat_type, event)
            
        except Exception as e:
            self.logger.error(f"Error checking for threats: {e}")
    
    async def _detect_brute_force(self, event: SecurityEvent) -> bool:
        """Detect brute force attack patterns"""
        if event.event_type != SecurityEventType.LOGIN_ATTEMPT or event.status_code < 400:
            return False
        
        # Check for multiple failed logins from same IP
        recent_events = [
            e for e in list(self.security_events)[-100:]  # Last 100 events
            if e.ip_address == event.ip_address
            and e.event_type == SecurityEventType.LOGIN_ATTEMPT
            and e.status_code >= 400
            and (datetime.now() - e.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        return len(recent_events) >= self.security_thresholds["max_failed_logins"]
    
    async def _detect_sql_injection(self, event: SecurityEvent) -> bool:
        """Detect SQL injection attack patterns"""
        request_data = json.dumps(event.request_data).lower()
        
        # Check for SQL injection patterns
        for pattern in self.malicious_patterns["sql_injection"]:
            if pattern.lower() in request_data:
                return True
        
        # Check endpoint for SQL injection
        if any(pattern.lower() in event.endpoint.lower() 
               for pattern in self.malicious_patterns["sql_injection"]):
            return True
        
        return False
    
    async def _detect_xss_attack(self, event: SecurityEvent) -> bool:
        """Detect XSS attack patterns"""
        request_data = json.dumps(event.request_data).lower()
        
        # Check for XSS patterns
        for pattern in self.malicious_patterns["xss_patterns"]:
            if pattern.lower() in request_data:
                return True
        
        return False
    
    async def _detect_api_abuse(self, event: SecurityEvent) -> bool:
        """Detect API abuse patterns"""
        if not event.endpoint.startswith('/api/'):
            return False
        
        # Check for high frequency requests from same IP
        recent_api_requests = [
            e for e in list(self.security_events)[-1000:]
            if e.ip_address == event.ip_address
            and e.endpoint.startswith('/api/')
            and (datetime.now() - e.timestamp).total_seconds() < 60  # Last minute
        ]
        
        return len(recent_api_requests) > self.security_thresholds["max_requests_per_minute"]
    
    async def _detect_unauthorized_access(self, event: SecurityEvent) -> bool:
        """Detect unauthorized access attempts"""
        # Access denied to sensitive endpoints
        sensitive_endpoints = ['/admin', '/config', '/api/internal', '/dashboard/admin']
        
        return (event.status_code == 403 and 
                any(endpoint in event.endpoint for endpoint in sensitive_endpoints) and
                event.risk_score > 0.7)
    
    async def _create_threat_event(self, threat_type: ThreatType, triggering_event: SecurityEvent):
        """Create a threat event for detected threat"""
        try:
            threat_id = f"threat_{int(datetime.now().timestamp())}_{hash(f'{threat_type.value}{triggering_event.ip_address}') % 10000}"
            
            # Determine threat level
            threat_level = self._determine_threat_level(threat_type, triggering_event)
            
            # Gather evidence
            evidence = await self._gather_threat_evidence(threat_type, triggering_event)
            
            # Determine affected users
            affected_users = await self._identify_affected_users(threat_type, triggering_event)
            
            # Generate mitigation actions
            mitigation_actions = self._generate_mitigation_actions(threat_type, threat_level)
            
            threat_event = ThreatEvent(
                threat_id=threat_id,
                threat_type=threat_type,
                threat_level=threat_level,
                source_ip=triggering_event.ip_address,
                target_resource=triggering_event.endpoint,
                description=self._generate_threat_description(threat_type, triggering_event),
                evidence=evidence,
                affected_users=affected_users,
                mitigation_actions=mitigation_actions
            )
            
            self.threat_events.append(threat_event)
            
            # Cache in Redis for real-time alerts
            if self.redis_client:
                await self._cache_threat_event(threat_event)
            
            # Send alert for critical/high threats
            if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                await self._send_security_alert(threat_event)
            
            self.logger.warning(f"Threat detected: {threat_type.value} from {triggering_event.ip_address}")
            
        except Exception as e:
            self.logger.error(f"Error creating threat event: {e}")
    
    def _determine_threat_level(self, threat_type: ThreatType, event: SecurityEvent) -> ThreatLevel:
        """Determine severity level of threat"""
        # Base threat levels by type
        threat_levels = {
            ThreatType.SQL_INJECTION: ThreatLevel.CRITICAL,
            ThreatType.XSS_ATTACK: ThreatLevel.HIGH,
            ThreatType.BRUTE_FORCE_ATTACK: ThreatLevel.HIGH,
            ThreatType.UNAUTHORIZED_ACCESS: ThreatLevel.MEDIUM,
            ThreatType.API_ABUSE: ThreatLevel.MEDIUM,
            ThreatType.DDOS_ATTACK: ThreatLevel.CRITICAL,
            ThreatType.DATA_BREACH: ThreatLevel.CRITICAL,
            ThreatType.MALWARE_UPLOAD: ThreatLevel.CRITICAL
        }
        
        base_level = threat_levels.get(threat_type, ThreatLevel.MEDIUM)
        
        # Adjust based on risk score
        if event.risk_score > 0.9:
            if base_level == ThreatLevel.MEDIUM:
                return ThreatLevel.HIGH
            elif base_level == ThreatLevel.HIGH:
                return ThreatLevel.CRITICAL
        
        return base_level
    
    async def _gather_threat_evidence(self, threat_type: ThreatType, event: SecurityEvent) -> Dict[str, Any]:
        """Gather evidence for threat event"""
        evidence = {
            "triggering_event_id": event.event_id,
            "source_ip": event.ip_address,
            "user_agent": event.user_agent,
            "timestamp": event.timestamp.isoformat(),
            "geolocation": event.geolocation,
            "risk_score": event.risk_score
        }
        
        # Add threat-specific evidence
        if threat_type == ThreatType.BRUTE_FORCE_ATTACK:
            # Count recent failed attempts
            recent_failures = len([
                e for e in list(self.security_events)[-100:]
                if e.ip_address == event.ip_address
                and e.event_type == SecurityEventType.LOGIN_ATTEMPT
                and e.status_code >= 400
                and (datetime.now() - e.timestamp).total_seconds() < 3600
            ])
            evidence["failed_login_attempts"] = recent_failures
        
        elif threat_type == ThreatType.SQL_INJECTION:
            evidence["malicious_patterns"] = [
                pattern for pattern in self.malicious_patterns["sql_injection"]
                if pattern.lower() in json.dumps(event.request_data).lower()
            ]
        
        elif threat_type == ThreatType.API_ABUSE:
            # Count recent API requests
            recent_requests = len([
                e for e in list(self.security_events)[-1000:]
                if e.ip_address == event.ip_address
                and e.endpoint.startswith('/api/')
                and (datetime.now() - e.timestamp).total_seconds() < 60
            ])
            evidence["requests_per_minute"] = recent_requests
        
        return evidence
    
    async def _identify_affected_users(self, threat_type: ThreatType, event: SecurityEvent) -> List[str]:
        """Identify users potentially affected by threat"""
        affected = []
        
        if event.user_id:
            affected.append(event.user_id)
        
        # For certain threat types, check for other affected users
        if threat_type in [ThreatType.DATA_BREACH, ThreatType.UNAUTHORIZED_ACCESS]:
            # Get users who accessed same resource recently
            recent_users = [
                e.user_id for e in list(self.security_events)[-1000:]
                if e.endpoint == event.endpoint
                and e.user_id
                and (datetime.now() - e.timestamp).total_seconds() < 3600
            ]
            affected.extend(recent_users)
        
        return list(set(affected))  # Remove duplicates
    
    def _generate_mitigation_actions(self, threat_type: ThreatType, threat_level: ThreatLevel) -> List[str]:
        """Generate recommended mitigation actions"""
        actions = []
        
        # Common actions for all threats
        actions.append("Monitor threat source for continued activity")
        actions.append("Review logs for additional indicators")
        
        # Threat-specific actions
        if threat_type == ThreatType.BRUTE_FORCE_ATTACK:
            actions.extend([
                "Block source IP address",
                "Implement rate limiting",
                "Enable account lockout policies",
                "Require stronger authentication"
            ])
        
        elif threat_type == ThreatType.SQL_INJECTION:
            actions.extend([
                "Block malicious requests",
                "Review input validation",
                "Update WAF rules",
                "Patch vulnerable endpoints"
            ])
        
        elif threat_type == ThreatType.UNAUTHORIZED_ACCESS:
            actions.extend([
                "Review access permissions",
                "Audit user accounts",
                "Strengthen authentication",
                "Monitor privileged accounts"
            ])
        
        elif threat_type == ThreatType.API_ABUSE:
            actions.extend([
                "Implement API rate limiting",
                "Review API authentication",
                "Block abusive sources",
                "Monitor API usage patterns"
            ])
        
        # Critical threat actions
        if threat_level == ThreatLevel.CRITICAL:
            actions.extend([
                "Escalate to security team immediately",
                "Consider system isolation",
                "Initiate incident response plan",
                "Notify stakeholders"
            ])
        
        return actions
    
    def _generate_threat_description(self, threat_type: ThreatType, event: SecurityEvent) -> str:
        """Generate human-readable threat description"""
        descriptions = {
            ThreatType.BRUTE_FORCE_ATTACK: f"Brute force attack detected from {event.ip_address} with multiple failed login attempts",
            ThreatType.SQL_INJECTION: f"SQL injection attempt detected in request to {event.endpoint}",
            ThreatType.XSS_ATTACK: f"Cross-site scripting attack detected in request data",
            ThreatType.UNAUTHORIZED_ACCESS: f"Unauthorized access attempt to {event.endpoint} from {event.ip_address}",
            ThreatType.API_ABUSE: f"API abuse detected with excessive requests from {event.ip_address}",
            ThreatType.SUSPICIOUS_ACTIVITY: f"Suspicious activity detected from {event.ip_address}"
        }
        
        return descriptions.get(threat_type, f"Security threat of type {threat_type.value} detected")
    
    async def monitor_compliance(
        self,
        framework: ComplianceFramework,
        requirements: Optional[List[str]] = None
    ) -> List[ComplianceEvent]:
        """Monitor compliance with security frameworks"""
        try:
            compliance_events = []
            
            # Get requirements to check
            framework_requirements = self.compliance_requirements.get(framework, {})
            requirements_to_check = requirements or list(framework_requirements.keys())
            
            for requirement in requirements_to_check:
                if requirement in framework_requirements:
                    compliance_status = await self._check_compliance_requirement(
                        framework, requirement
                    )
                    
                    compliance_id = f"comp_{int(datetime.now().timestamp())}_{framework.value}_{requirement}"
                    
                    event = ComplianceEvent(
                        compliance_id=compliance_id,
                        framework=framework,
                        requirement=requirement,
                        status=compliance_status["status"],
                        violation_details=compliance_status.get("violation_details"),
                        remediation_steps=compliance_status.get("remediation_steps", []),
                        responsible_party=compliance_status.get("responsible_party", "Security Team"),
                        evidence=compliance_status.get("evidence", {})
                    )
                    
                    compliance_events.append(event)
                    self.compliance_events.append(event)
            
            return compliance_events
            
        except Exception as e:
            self.logger.error(f"Error monitoring compliance: {e}")
            return []
    
    async def _check_compliance_requirement(
        self,
        framework: ComplianceFramework,
        requirement: str
    ) -> Dict[str, Any]:
        """Check specific compliance requirement"""
        try:
            # Simplified compliance checking
            # In production, would integrate with actual compliance monitoring systems
            
            if framework == ComplianceFramework.GDPR:
                if requirement == "data_encryption":
                    # Check if encryption is enabled
                    encryption_enabled = True  # Would check actual encryption status
                    return {
                        "status": "compliant" if encryption_enabled else "non_compliant",
                        "evidence": {"encryption_algorithm": "AES-256", "tls_version": "1.3"},
                        "responsible_party": "Infrastructure Team"
                    }
                
                elif requirement == "breach_notification":
                    # Check breach notification procedures
                    return {
                        "status": "compliant",
                        "evidence": {"notification_process": "automated", "max_time": "24 hours"},
                        "responsible_party": "Security Team"
                    }
            
            elif framework == ComplianceFramework.PCI_DSS:
                if requirement == "payment_encryption":
                    return {
                        "status": "compliant",
                        "evidence": {"encryption_method": "tokenization", "compliance_level": "Level 1"},
                        "responsible_party": "Payment Team"
                    }
            
            # Default compliance status
            return {
                "status": "compliant",
                "evidence": {"last_reviewed": datetime.now().isoformat()},
                "responsible_party": "Security Team"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking compliance requirement: {e}")
            return {
                "status": "unknown",
                "violation_details": f"Error checking requirement: {e}",
                "responsible_party": "Security Team"
            }
    
    async def analyze_security_metrics(
        self,
        time_range: Tuple[datetime, datetime]
    ) -> SecurityMetrics:
        """Analyze comprehensive security metrics"""
        try:
            start_time, end_time = time_range
            
            # Filter events by time range
            filtered_security_events = [
                event for event in self.security_events
                if start_time <= event.timestamp <= end_time
            ]
            
            filtered_threat_events = [
                event for event in self.threat_events
                if start_time <= event.detected_at <= end_time
            ]
            
            # Basic metrics
            total_security_events = len(filtered_security_events)
            total_threats = len(filtered_threat_events)
            
            # Threat analysis
            threats_by_type = defaultdict(int)
            threats_by_level = defaultdict(int)
            
            for threat in filtered_threat_events:
                threats_by_type[threat.threat_type.value] += 1
                threats_by_level[threat.threat_level.value] += 1
            
            # False positive rate
            false_positives = len([t for t in filtered_threat_events if t.false_positive])
            false_positive_rate = false_positives / total_threats if total_threats > 0 else 0.0
            
            # Response time metrics
            resolved_threats = [t for t in filtered_threat_events if t.resolved and t.resolved_at]
            
            detection_times = []
            response_times = []
            
            for threat in resolved_threats:
                # Detection time (simplified - would calculate from first indicator)
                detection_times.append(1.0)  # Assume 1 hour average detection
                
                # Response time
                response_time = (threat.resolved_at - threat.detected_at).total_seconds() / 3600
                response_times.append(response_time)
            
            mean_detection_time = statistics.mean(detection_times) if detection_times else 0.0
            mean_response_time = statistics.mean(response_times) if response_times else 0.0
            
            # Attack success analysis
            successful_attacks = len([
                t for t in filtered_threat_events 
                if t.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH] and not t.resolved
            ])
            
            blocked_attacks = len([
                t for t in filtered_threat_events 
                if t.resolved and (datetime.now() - t.detected_at).total_seconds() < 3600  # Resolved quickly
            ])
            
            attack_success_rate = successful_attacks / (successful_attacks + blocked_attacks) if (successful_attacks + blocked_attacks) > 0 else 0.0
            
            # Top attack sources
            source_counts = defaultdict(int)
            for threat in filtered_threat_events:
                source_counts[threat.source_ip] += 1
            
            top_sources = [
                {"ip": ip, "threat_count": count, "geolocation": await self._get_ip_geolocation(ip)}
                for ip, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Compliance score
            compliance_score = await self._calculate_compliance_score()
            
            # Audit findings
            audit_findings = await self._analyze_audit_findings(filtered_security_events)
            
            # User risk distribution
            user_risk_dist = await self._analyze_user_risk_distribution(filtered_security_events)
            
            # Security incidents
            incidents = await self._compile_security_incidents(filtered_threat_events)
            
            metrics = SecurityMetrics(
                time_period=time_range,
                total_security_events=total_security_events,
                total_threats_detected=total_threats,
                threats_by_type=dict(threats_by_type),
                threats_by_level=dict(threats_by_level),
                false_positive_rate=false_positive_rate,
                mean_time_to_detection=mean_detection_time,
                mean_time_to_response=mean_response_time,
                successful_attacks=successful_attacks,
                blocked_attacks=blocked_attacks,
                attack_success_rate=attack_success_rate,
                top_attack_sources=top_sources,
                compliance_score=compliance_score,
                audit_findings=audit_findings,
                user_risk_distribution=user_risk_dist,
                security_incidents=incidents
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing security metrics: {e}")
            return SecurityMetrics(time_period=time_range)
    
    async def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        try:
            recent_compliance_events = [
                event for event in self.compliance_events
                if (datetime.now() - event.assessed_at).days <= 30  # Last 30 days
            ]
            
            if not recent_compliance_events:
                return 85.0  # Default score
            
            compliant_events = len([e for e in recent_compliance_events if e.status == "compliant"])
            total_events = len(recent_compliance_events)
            
            return (compliant_events / total_events) * 100 if total_events > 0 else 85.0
            
        except Exception as e:
            self.logger.error(f"Error calculating compliance score: {e}")
            return 0.0
    
    async def _analyze_audit_findings(self, security_events: List[SecurityEvent]) -> Dict[str, int]:
        """Analyze audit findings from security events"""
        findings = {
            "failed_authentications": 0,
            "unauthorized_access_attempts": 0,
            "privilege_escalations": 0,
            "suspicious_activities": 0,
            "policy_violations": 0
        }
        
        for event in security_events:
            if event.event_type == SecurityEventType.LOGIN_ATTEMPT and event.status_code >= 400:
                findings["failed_authentications"] += 1
            
            elif event.status_code == 403:
                findings["unauthorized_access_attempts"] += 1
            
            elif event.risk_score > 0.7:
                findings["suspicious_activities"] += 1
            
            elif event.event_type == SecurityEventType.PERMISSION_CHANGE:
                findings["privilege_escalations"] += 1
        
        return findings
    
    async def _analyze_user_risk_distribution(self, security_events: List[SecurityEvent]) -> Dict[str, int]:
        """Analyze distribution of user risk levels"""
        user_risks = {}
        
        # Calculate risk for each user
        for event in security_events:
            if event.user_id and event.user_id not in user_risks:
                user_risks[event.user_id] = await self._calculate_user_risk(event.user_id)
        
        # Categorize risks
        distribution = {
            "low_risk": 0,      # 0.0 - 0.3
            "medium_risk": 0,   # 0.3 - 0.6
            "high_risk": 0,     # 0.6 - 0.8
            "critical_risk": 0  # 0.8 - 1.0
        }
        
        for risk_score in user_risks.values():
            if risk_score < 0.3:
                distribution["low_risk"] += 1
            elif risk_score < 0.6:
                distribution["medium_risk"] += 1
            elif risk_score < 0.8:
                distribution["high_risk"] += 1
            else:
                distribution["critical_risk"] += 1
        
        return distribution
    
    async def _compile_security_incidents(self, threat_events: List[ThreatEvent]) -> List[Dict[str, Any]]:
        """Compile major security incidents"""
        incidents = []
        
        # High and critical threats are considered incidents
        major_threats = [
            threat for threat in threat_events
            if threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]
        ]
        
        for threat in major_threats[:10]:  # Top 10 incidents
            incidents.append({
                "incident_id": threat.threat_id,
                "type": threat.threat_type.value,
                "severity": threat.threat_level.value,
                "source": threat.source_ip,
                "detected_at": threat.detected_at.isoformat(),
                "resolved": threat.resolved,
                "affected_users": len(threat.affected_users),
                "description": threat.description
            })
        
        return incidents
    
    async def _send_security_alert(self, threat_event: ThreatEvent):
        """Send security alert for critical threats"""
        try:
            alert = {
                "alert_type": "security_threat",
                "threat_id": threat_event.threat_id,
                "threat_type": threat_event.threat_type.value,
                "threat_level": threat_event.threat_level.value,
                "source_ip": threat_event.source_ip,
                "description": threat_event.description,
                "mitigation_actions": threat_event.mitigation_actions,
                "timestamp": threat_event.detected_at.isoformat()
            }
            
            # Send to Redis for real-time monitoring
            if self.redis_client:
                self.redis_client.lpush("security_alerts", json.dumps(alert))
                self.redis_client.ltrim("security_alerts", 0, 1000)  # Keep last 1000 alerts
            
            # Log critical alert
            self.logger.critical(f"SECURITY ALERT: {threat_event.threat_type.value} from {threat_event.source_ip}")
            
        except Exception as e:
            self.logger.error(f"Error sending security alert: {e}")
    
    # Redis caching methods
    async def _cache_security_event(self, event: SecurityEvent):
        """Cache security event in Redis"""
        if self.redis_client:
            try:
                key = f"sec_event:{event.event_id}"
                data = {
                    "event_type": event.event_type.value,
                    "user_id": event.user_id or "anonymous",
                    "ip_address": event.ip_address,
                    "endpoint": event.endpoint,
                    "status_code": event.status_code,
                    "risk_score": event.risk_score,
                    "timestamp": event.timestamp.isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 86400)  # 24 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_threat_event(self, threat: ThreatEvent):
        """Cache threat event in Redis"""
        if self.redis_client:
            try:
                key = f"threat:{threat.threat_id}"
                data = {
                    "threat_type": threat.threat_type.value,
                    "threat_level": threat.threat_level.value,
                    "source_ip": threat.source_ip,
                    "target_resource": threat.target_resource,
                    "resolved": threat.resolved,
                    "detected_at": threat.detected_at.isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get summary of security intelligence system"""
        try:
            total_events = len(self.security_events)
            total_threats = len(self.threat_events)
            total_compliance_events = len(self.compliance_events)
            
            # Recent activity (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_events = len([e for e in self.security_events if e.timestamp >= recent_cutoff])
            recent_threats = len([t for t in self.threat_events if t.detected_at >= recent_cutoff])
            
            # Threat statistics
            unresolved_threats = len([t for t in self.threat_events if not t.resolved])
            critical_threats = len([t for t in self.threat_events if t.threat_level == ThreatLevel.CRITICAL])
            
            return {
                "system_stats": {
                    "total_security_events": total_events,
                    "total_threats_detected": total_threats,
                    "unresolved_threats": unresolved_threats,
                    "critical_threats": critical_threats,
                    "compliance_events": total_compliance_events
                },
                "performance_metrics": {
                    "ml_models_initialized": self._ml_models_initialized,
                    "redis_connected": self.redis_client is not None,
                    "threat_detection_rate": round((total_threats / total_events * 100), 2) if total_events > 0 else 0
                },
                "recent_activity": {
                    "events_last_24h": recent_events,
                    "threats_last_24h": recent_threats,
                    "active_monitoring": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security summary: {e}")
            return {"error": str(e)}