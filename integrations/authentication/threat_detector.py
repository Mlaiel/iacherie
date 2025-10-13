# -*- coding: utf-8 -*-
"""
IA Chérie Platform - Enterprise Threat Detector
Advanced threat detection and security monitoring system
Author: IA Chérie Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import time
import re
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import ipaddress
import hashlib
from collections import defaultdict, deque

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    INSIDER_THREAT = "insider_threat"
    DDoS = "ddos"
    BOTNET = "botnet"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_TAKEOVER = "account_takeover"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatStatus(Enum):
    """Threat status"""
    ACTIVE = "active"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    UNDER_INVESTIGATION = "under_investigation"

@dataclass
class ThreatIndicator:
    """Threat indicator/signature"""
    id: str
    threat_type: ThreatType
    pattern: str
    description: str
    severity: ThreatSeverity
    confidence: float  # 0.0 - 1.0
    is_regex: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    active: bool = True

@dataclass
class ThreatEvent:
    """Detected threat event"""
    id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    source_ip: Optional[str] = None
    target_resource: Optional[str] = None
    user_id: Optional[str] = None
    description: str = ""
    indicators: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    status: ThreatStatus = ThreatStatus.ACTIVE
    detected_at: datetime = field(default_factory=datetime.now)
    mitigated_at: Optional[datetime] = None
    false_positive: bool = False
    correlation_id: Optional[str] = None

@dataclass
class AttackPattern:
    """Attack pattern for detection"""
    name: str
    threat_type: ThreatType
    conditions: List[Dict[str, Any]]
    time_window: timedelta
    threshold: int
    severity: ThreatSeverity
    description: str

class ThreatDetector:
    """Enterprise Threat Detector"""
    
    def __init__(self):
        """Initialize threat detector"""
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.attack_patterns: Dict[str, AttackPattern] = {}
        self.threats: List[ThreatEvent] = []
        self.ip_blacklist: Set[str] = set()
        self.user_sessions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.ip_activity: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.RLock()
        self._threat_counter = 0
        
        # Rate limiting tracking
        self.rate_limits = {
            "failed_logins": defaultdict(lambda: deque(maxlen=10)),
            "api_requests": defaultdict(lambda: deque(maxlen=100)),
            "resource_access": defaultdict(lambda: deque(maxlen=50))
        }
        
        # Initialize threat indicators and patterns
        self._initialize_threat_indicators()
        self._initialize_attack_patterns()
        
        logger.info("🔍 Threat Detector initialized successfully")
    
    def _initialize_threat_indicators(self):
        """Initialize threat detection indicators"""
        indicators = [
            # SQL Injection patterns
            ThreatIndicator(
                id="sql_001",
                threat_type=ThreatType.SQL_INJECTION,
                pattern=r"('|(\-\-)|(\;)|(\||)\|)|(\*|\*))",
                description="SQL injection attempt detected",
                severity=ThreatSeverity.HIGH,
                confidence=0.8,
                is_regex=True
            ),
            ThreatIndicator(
                id="sql_002",
                threat_type=ThreatType.SQL_INJECTION,
                pattern=r"(union|select|insert|delete|update|drop|create|alter)\\s",
                description="SQL keywords in input",
                severity=ThreatSeverity.HIGH,
                confidence=0.7,
                is_regex=True
            ),
            
            # XSS patterns
            ThreatIndicator(
                id="xss_001",
                threat_type=ThreatType.XSS,
                pattern=r"<script[^>]*>.*?</script>",
                description="Script tag injection attempt",
                severity=ThreatSeverity.HIGH,
                confidence=0.9,
                is_regex=True
            ),
            ThreatIndicator(
                id="xss_002",
                threat_type=ThreatType.XSS,
                pattern=r"javascript:|vbscript:|onload=|onerror=|onclick=",
                description="JavaScript event handler injection",
                severity=ThreatSeverity.MEDIUM,
                confidence=0.7,
                is_regex=True
            ),
            
            # Malware patterns
            ThreatIndicator(
                id="malware_001",
                threat_type=ThreatType.MALWARE,
                pattern="eicar",
                description="EICAR test signature detected",
                severity=ThreatSeverity.CRITICAL,
                confidence=1.0
            ),
            
            # Suspicious user agents
            ThreatIndicator(
                id="bot_001",
                threat_type=ThreatType.BOTNET,
                pattern=r"(bot|crawler|spider|scraper)",
                description="Automated bot activity",
                severity=ThreatSeverity.LOW,
                confidence=0.6,
                is_regex=True
            ),
            
            # Directory traversal
            ThreatIndicator(
                id="traversal_001",
                threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                pattern=r"\.\.[\/\\]",
                description="Directory traversal attempt",
                severity=ThreatSeverity.HIGH,
                confidence=0.8,
                is_regex=True
            )
        ]
        
        for indicator in indicators:
            self.indicators[indicator.id] = indicator
        
        logger.info(f"🚨 Initialized {len(indicators)} threat indicators")
    
    def _initialize_attack_patterns(self):
        """Initialize attack pattern detection"""
        patterns = [
            # Brute force detection
            AttackPattern(
                name="brute_force_login",
                threat_type=ThreatType.BRUTE_FORCE,
                conditions=[
                    {"event_type": "failed_login", "threshold": 5}
                ],
                time_window=timedelta(minutes=5),
                threshold=5,
                severity=ThreatSeverity.HIGH,
                description="Multiple failed login attempts from same IP"
            ),
            
            # DDoS detection
            AttackPattern(
                name="ddos_requests",
                threat_type=ThreatType.DDoS,
                conditions=[
                    {"event_type": "api_request", "threshold": 100}
                ],
                time_window=timedelta(minutes=1),
                threshold=100,
                severity=ThreatSeverity.CRITICAL,
                description="Excessive requests indicating DDoS attack"
            ),
            
            # Data exfiltration
            AttackPattern(
                name="data_exfiltration",
                threat_type=ThreatType.DATA_EXFILTRATION,
                conditions=[
                    {"event_type": "large_download", "threshold": 10},
                    {"event_type": "sensitive_access", "threshold": 20}
                ],
                time_window=timedelta(hours=1),
                threshold=1,
                severity=ThreatSeverity.CRITICAL,
                description="Potential data exfiltration activity"
            ),
            
            # Account takeover
            AttackPattern(
                name="account_takeover",
                threat_type=ThreatType.ACCOUNT_TAKEOVER,
                conditions=[
                    {"event_type": "login_new_location", "threshold": 1},
                    {"event_type": "password_change", "threshold": 1},
                    {"event_type": "privilege_change", "threshold": 1}
                ],
                time_window=timedelta(hours=2),
                threshold=2,
                severity=ThreatSeverity.HIGH,
                description="Suspicious account activity indicating takeover"
            )
        ]
        
        for pattern in patterns:
            self.attack_patterns[pattern.name] = pattern
        
        logger.info(f"🕵️‍♂️ Initialized {len(patterns)} attack patterns")
    
    def analyze_request(self, request_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze incoming request for threats"""
        threats = []
        
        try:
            with self._lock:
                # Extract request information
                url = request_data.get("url", "")
                headers = request_data.get("headers", {})
                body = request_data.get("body", "")
                ip_address = request_data.get("ip", "")
                user_agent = headers.get("User-Agent", "")
                user_id = request_data.get("user_id")
                
                # Check IP blacklist
                if ip_address in self.ip_blacklist:
                    threat = self._create_threat(
                        ThreatType.SUSPICIOUS_ACTIVITY,
                        ThreatSeverity.HIGH,
                        f"Request from blacklisted IP: {ip_address}",
                        source_ip=ip_address,
                        raw_data=request_data
                    )
                    threats.append(threat)
                
                # Analyze against threat indicators
                content_to_analyze = f"{url} {body} {user_agent}"
                
                for indicator in self.indicators.values():
                    if not indicator.active:
                        continue
                    
                    match_found = False
                    if indicator.is_regex:
                        match_found = bool(re.search(indicator.pattern, content_to_analyze, re.IGNORECASE))
                    else:
                        match_found = indicator.pattern.lower() in content_to_analyze.lower()
                    
                    if match_found:
                        threat = self._create_threat(
                            indicator.threat_type,
                            indicator.severity,
                            f"{indicator.description} - Pattern: {indicator.pattern}",
                            source_ip=ip_address,
                            user_id=user_id,
                            indicators=[indicator.id],
                            confidence=indicator.confidence,
                            raw_data=request_data
                        )
                        threats.append(threat)
                
                # Track request for pattern analysis
                self._track_activity(ip_address, user_id, request_data)
                
                # Check for attack patterns
                pattern_threats = self._check_attack_patterns(ip_address, user_id)
                threats.extend(pattern_threats)
                
                # Log threats
                for threat in threats:
                    logger.warning(f"⚠️ Threat detected: {threat.threat_type.value} - {threat.description}")
                
                return threats
                
        except Exception as e:
            logger.error(f"❌ Error analyzing request: {str(e)}")
            return []
    
    def _create_threat(self, threat_type: ThreatType, severity: ThreatSeverity,
                      description: str, source_ip: Optional[str] = None,
                      user_id: Optional[str] = None, target_resource: Optional[str] = None,
                      indicators: Optional[List[str]] = None, confidence: float = 0.5,
                      raw_data: Optional[Dict[str, Any]] = None) -> ThreatEvent:
        """Create a new threat event"""
        self._threat_counter += 1
        threat_id = f"threat_{self._threat_counter}_{int(time.time())}"
        
        threat = ThreatEvent(
            id=threat_id,
            threat_type=threat_type,
            severity=severity,
            description=description,
            source_ip=source_ip,
            user_id=user_id,
            target_resource=target_resource,
            indicators=indicators or [],
            confidence=confidence,
            raw_data=raw_data or {}
        )
        
        self.threats.append(threat)
        return threat
    
    def _track_activity(self, ip_address: str, user_id: Optional[str], request_data: Dict[str, Any]):
        """Track activity for pattern detection"""
        timestamp = datetime.now()
        activity_record = {
            "timestamp": timestamp,
            "ip": ip_address,
            "user_id": user_id,
            "event_type": request_data.get("event_type", "request"),
            "data": request_data
        }
        
        # Track by IP
        self.ip_activity[ip_address].append(activity_record)
        
        # Track by user
        if user_id:
            self.user_sessions[user_id].append(activity_record)
        
        # Track specific event types for rate limiting
        event_type = request_data.get("event_type", "api_request")
        if event_type in self.rate_limits:
            self.rate_limits[event_type][ip_address].append(timestamp)
    
    def _check_attack_patterns(self, ip_address: str, user_id: Optional[str]) -> List[ThreatEvent]:
        """Check for attack patterns"""
        threats = []
        
        try:
            current_time = datetime.now()
            
            for pattern_name, pattern in self.attack_patterns.items():
                # Check IP-based patterns
                if self._pattern_matches(ip_address, pattern, current_time, "ip"):
                    threat = self._create_threat(
                        pattern.threat_type,
                        pattern.severity,
                        f"Attack pattern detected: {pattern.description}",
                        source_ip=ip_address,
                        user_id=user_id
                    )
                    threats.append(threat)
                
                # Check user-based patterns
                if user_id and self._pattern_matches(user_id, pattern, current_time, "user"):
                    threat = self._create_threat(
                        pattern.threat_type,
                        pattern.severity,
                        f"User attack pattern detected: {pattern.description}",
                        source_ip=ip_address,
                        user_id=user_id
                    )
                    threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"❌ Error checking attack patterns: {str(e)}")
            return []
    
    def _pattern_matches(self, identifier: str, pattern: AttackPattern, 
                        current_time: datetime, tracking_type: str) -> bool:
        """Check if activity matches an attack pattern"""
        try:
            # Get activity records
            if tracking_type == "ip":
                activities = list(self.ip_activity.get(identifier, []))
            else:
                activities = list(self.user_sessions.get(identifier, []))
            
            # Filter activities within time window
            cutoff_time = current_time - pattern.time_window
            recent_activities = [
                activity for activity in activities
                if activity["timestamp"] >= cutoff_time
            ]
            
            # Count matching conditions
            condition_matches = 0
            
            for condition in pattern.conditions:
                event_type = condition["event_type"]
                threshold = condition["threshold"]
                
                count = sum(1 for activity in recent_activities
                          if activity.get("event_type") == event_type)
                
                if count >= threshold:
                    condition_matches += 1
            
            return condition_matches >= pattern.threshold
            
        except Exception:
            return False
    
    def analyze_user_behavior(self, user_id: str, current_activity: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze user behavior for anomalies"""
        threats = []
        
        try:
            with self._lock:
                user_history = list(self.user_sessions.get(user_id, []))
                
                if len(user_history) < 5:  # Need baseline
                    return threats
                
                # Check for anomalous behavior
                current_ip = current_activity.get("ip")
                current_time = datetime.now()
                
                # Location anomaly detection
                recent_ips = [activity["ip"] for activity in user_history[-10:]
                             if activity.get("ip")]
                
                if current_ip and current_ip not in recent_ips:
                    threat = self._create_threat(
                        ThreatType.ANOMALOUS_BEHAVIOR,
                        ThreatSeverity.MEDIUM,
                        f"User login from new IP address: {current_ip}",
                        source_ip=current_ip,
                        user_id=user_id,
                        confidence=0.6
                    )
                    threats.append(threat)
                
                # Time-based anomaly
                recent_hours = [activity["timestamp"].hour for activity in user_history[-20:]]
                current_hour = current_time.hour
                
                if recent_hours and current_hour not in recent_hours:
                    threat = self._create_threat(
                        ThreatType.ANOMALOUS_BEHAVIOR,
                        ThreatSeverity.LOW,
                        f"User activity at unusual time: {current_hour}:00",
                        source_ip=current_ip,
                        user_id=user_id,
                        confidence=0.4
                    )
                    threats.append(threat)
                
                return threats
                
        except Exception as e:
            logger.error(f"❌ Error analyzing user behavior: {str(e)}")
            return []
    
    def add_to_blacklist(self, ip_address: str) -> bool:
        """Add IP to blacklist"""
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)
            
            with self._lock:
                self.ip_blacklist.add(ip_address)
                logger.info(f"⛔ Added IP to blacklist: {ip_address}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding IP to blacklist: {str(e)}")
            return False
    
    def remove_from_blacklist(self, ip_address: str) -> bool:
        """Remove IP from blacklist"""
        try:
            with self._lock:
                self.ip_blacklist.discard(ip_address)
                logger.info(f"✅ Removed IP from blacklist: {ip_address}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error removing IP from blacklist: {str(e)}")
            return False
    
    def mark_false_positive(self, threat_id: str) -> bool:
        """Mark threat as false positive"""
        try:
            with self._lock:
                for threat in self.threats:
                    if threat.id == threat_id:
                        threat.false_positive = True
                        threat.status = ThreatStatus.FALSE_POSITIVE
                        logger.info(f"✅ Marked threat as false positive: {threat_id}")
                        return True
                
                logger.warning(f"⚠️ Threat not found: {threat_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marking false positive: {str(e)}")
            return False
    
    def mitigate_threat(self, threat_id: str, mitigation_action: str) -> bool:
        """Mark threat as mitigated"""
        try:
            with self._lock:
                for threat in self.threats:
                    if threat.id == threat_id:
                        threat.status = ThreatStatus.MITIGATED
                        threat.mitigated_at = datetime.now()
                        threat.raw_data["mitigation_action"] = mitigation_action
                        logger.info(f"✅ Mitigated threat: {threat_id} - {mitigation_action}")
                        return True
                
                logger.warning(f"⚠️ Threat not found: {threat_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error mitigating threat: {str(e)}")
            return False
    
    def get_active_threats(self, severity_filter: Optional[ThreatSeverity] = None) -> List[ThreatEvent]:
        """Get active threats with optional severity filter"""
        try:
            with self._lock:
                active_threats = [t for t in self.threats 
                                if t.status == ThreatStatus.ACTIVE and not t.false_positive]
                
                if severity_filter:
                    active_threats = [t for t in active_threats if t.severity == severity_filter]
                
                # Sort by severity and detection time
                severity_order = {ThreatSeverity.CRITICAL: 0, ThreatSeverity.HIGH: 1, 
                                ThreatSeverity.MEDIUM: 2, ThreatSeverity.LOW: 3}
                
                active_threats.sort(key=lambda t: (severity_order[t.severity], t.detected_at), reverse=True)
                return active_threats
                
        except Exception as e:
            logger.error(f"❌ Error getting active threats: {str(e)}")
            return []
    
    def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat summary for specified time period"""
        try:
            with self._lock:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                recent_threats = [t for t in self.threats if t.detected_at >= cutoff_time]
                
                # Count by type
                type_counts = {}
                for threat_type in ThreatType:
                    type_counts[threat_type.value] = sum(1 for t in recent_threats 
                                                       if t.threat_type == threat_type)
                
                # Count by severity
                severity_counts = {}
                for severity in ThreatSeverity:
                    severity_counts[severity.value] = sum(1 for t in recent_threats 
                                                         if t.severity == severity)
                
                # Active threats
                active_count = sum(1 for t in recent_threats 
                                 if t.status == ThreatStatus.ACTIVE and not t.false_positive)
                
                return {
                    "period_hours": hours,
                    "total_threats": len(recent_threats),
                    "active_threats": active_count,
                    "threat_types": type_counts,
                    "severity_distribution": severity_counts,
                    "false_positives": sum(1 for t in recent_threats if t.false_positive),
                    "mitigated_threats": sum(1 for t in recent_threats 
                                           if t.status == ThreatStatus.MITIGATED),
                    "blacklisted_ips": len(self.ip_blacklist)
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating threat summary: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old threat data and activity logs"""
        try:
            with self._lock:
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Clean old threats
                initial_count = len(self.threats)
                self.threats = [t for t in self.threats if t.detected_at >= cutoff_time]
                
                # Clean old activity data
                for ip in list(self.ip_activity.keys()):
                    recent_activities = [a for a in self.ip_activity[ip] 
                                       if a["timestamp"] >= cutoff_time]
                    if recent_activities:
                        self.ip_activity[ip] = deque(recent_activities, maxlen=1000)
                    else:
                        del self.ip_activity[ip]
                
                # Clean old user sessions
                for user_id in list(self.user_sessions.keys()):
                    recent_sessions = [s for s in self.user_sessions[user_id] 
                                     if s["timestamp"] >= cutoff_time]
                    if recent_sessions:
                        self.user_sessions[user_id] = deque(recent_sessions, maxlen=100)
                    else:
                        del self.user_sessions[user_id]
                
                cleaned_count = initial_count - len(self.threats)
                if cleaned_count > 0:
                    logger.info(f"🧹 Cleaned up {cleaned_count} old threats (>{days} days)")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {str(e)}")

# Create global instance
threat_detector = ThreatDetector()

# Export main classes and instance
__all__ = [
    'ThreatDetector',
    'ThreatEvent',
    'ThreatIndicator',
    'AttackPattern',
    'ThreatType',
    'ThreatSeverity',
    'ThreatStatus',
    'threat_detector'
]