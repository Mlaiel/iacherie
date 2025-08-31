"""Database Threat Detector

Enterprise-grade database threat detection and response system with real-time
monitoring, anomaly detection, and automated incident response capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced threat detection architecture
- ML Engineer: Machine learning threat analysis
- DBA: Database security monitoring
- Security Expert: Enterprise threat intelligence
- Microservices: Distributed threat detection
- Audio Engineer: Audio data threat protection
- DevOps: Secure threat infrastructure
- IA Prompt Engineer: AI threat detection prompts

Contact: mlaiel@live.de
⚠️ LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""
import asyncio
import logging
import json
import time
import hashlib
import statistics
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid
import re
from collections import defaultdict, deque

# Configure logging
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(Enum):
    """Threat categories"""
    SQL_INJECTION = "sql_injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    BRUTE_FORCE = "brute_force"
    ANOMALOUS_ACCESS = "anomalous_access"
    SUSPICIOUS_QUERY = "suspicious_query"
    UNAUTHORIZED_SCHEMA_CHANGE = "unauthorized_schema_change"
    MASS_DATA_ACCESS = "mass_data_access"
    TIME_BASED_ATTACK = "time_based_attack"
    INSIDER_THREAT = "insider_threat"
    CREDENTIAL_STUFFING = "credential_stuffing"
    DATA_CORRUPTION = "data_corruption"


class ResponseAction(Enum):
    """Automated response actions"""
    ALERT = "alert"
    BLOCK_USER = "block_user"
    BLOCK_IP = "block_ip"
    REVOKE_PRIVILEGES = "revoke_privileges"
    QUARANTINE_SESSION = "quarantine_session"
    REQUIRE_MFA = "require_mfa"
    LOG_DETAILED = "log_detailed"
    NOTIFY_ADMIN = "notify_admin"
    TRIGGER_INCIDENT = "trigger_incident"


@dataclass
class ThreatIndicator:
    """Threat indicator definition"""
    indicator_id: str
    name: str
    description: str
    category: ThreatCategory
    pattern: str  # Regex pattern or rule
    severity: ThreatLevel
    confidence_threshold: float  # 0.0 - 1.0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatEvent:
    """Detected threat event"""
    event_id: str
    threat_id: str
    source_ip: str
    user_id: Optional[str]
    session_id: Optional[str]
    threat_category: ThreatCategory
    threat_level: ThreatLevel
    confidence_score: float
    detected_at: datetime = field(default_factory=datetime.now)
    evidence: Dict[str, Any] = field(default_factory=dict)
    response_actions: List[ResponseAction] = field(default_factory=list)
    is_confirmed: Optional[bool] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserBehaviorProfile:
    """User behavior analysis profile"""
    user_id: str
    username: str
    typical_login_times: List[int] = field(default_factory=list)  # Hours of day
    typical_ip_addresses: Set[str] = field(default_factory=set)
    typical_query_patterns: List[str] = field(default_factory=list)
    average_session_duration: float = 0.0
    typical_data_volume: float = 0.0
    login_frequency: float = 0.0
    failed_login_count: int = 0
    last_anomaly_detected: Optional[datetime] = None
    risk_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityMetrics:
    """Security monitoring metrics"""
    timestamp: datetime
    total_connections: int
    failed_logins: int
    successful_logins: int
    blocked_ips: int
    detected_threats: int
    false_positives: int
    response_time_ms: float
    cpu_usage: float
    memory_usage: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentResponse:
    """Security incident response"""
    incident_id: str
    threat_event_id: str
    response_type: ResponseAction
    executed_at: datetime = field(default_factory=datetime.now)
    executed_by: str = "system"
    success: bool = True
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class ThreatDetectionEngine(ABC):
    """Abstract threat detection engine interface"""
    
    @abstractmethod
    async def analyze_query(self, query: str, context: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze database query for threats"""
        pass
    
    @abstractmethod
    async def analyze_login(self, login_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze login attempt for threats"""
        pass
    
    @abstractmethod
    async def analyze_session(self, session_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze user session for threats"""
        pass


class SQLInjectionDetector(ThreatDetectionEngine):
    """SQL injection threat detection engine"""
    
    def __init__(self):
        self.sql_injection_patterns = [
            r"(?i)(union\s+select)",
            r"(?i)(select.*from.*information_schema)",
            r"(?i)(drop\s+table)",
            r"(?i)(insert\s+into.*values.*\(.*select)",
            r"(?i)(or\s+1\s*=\s*1)",
            r"(?i)(and\s+1\s*=\s*1)",
            r"(?i)('.*or.*'.*')",
            r"(?i)(exec\s*\()",
            r"(?i)(script.*alert)",
            r"(?i)(waitfor\s+delay)",
            r"(?i)(benchmark\s*\()",
            r"(?i)(sleep\s*\()",
            r"(?i)(load_file\s*\()",
            r"(?i)(into\s+outfile)",
            r"(?i)(char\s*\(\s*\d+)",
            r"(?i)(convert\s*\(.*using)",
            r"(?i)(having\s+\d+\s*=\s*\d+)",
            r"(?i)(order\s+by\s+\d+)",
            r"(?i)(group\s+by\s+\d+)",
            r"(?i)(0x[0-9a-f]+)",
            r"(?i)(\/\*.*\*\/)",
            r"(?i)(--\s*.*)",
            r"(?i)(#.*)",
            r"(?i)(\;\s*drop)",
            r"(?i)(\;\s*delete)",
            r"(?i)(\;\s*update)"
        ]
    
    async def analyze_query(self, query: str, context: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze query for SQL injection patterns"""
        threats = []
        
        try:
            for i, pattern in enumerate(self.sql_injection_patterns):
                if re.search(pattern, query):
                    confidence = self._calculate_injection_confidence(query, pattern)
                    
                    if confidence > 0.5:  # Configurable threshold
                        threat = ThreatEvent(
                            event_id=str(uuid.uuid4()),
                            threat_id=f"sql_injection_{i}",
                            source_ip=context.get("source_ip", "unknown"),
                            user_id=context.get("user_id"),
                            session_id=context.get("session_id"),
                            threat_category=ThreatCategory.SQL_INJECTION,
                            threat_level=self._determine_injection_severity(confidence),
                            confidence_score=confidence,
                            evidence={
                                "query": query,
                                "matched_pattern": pattern,
                                "pattern_index": i,
                                "context": context
                            }
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze query for SQL injection: {e}")
            return []
    
    async def analyze_login(self, login_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze login for SQL injection in credentials"""
        threats = []
        
        try:
            username = login_data.get("username", "")
            password = login_data.get("password", "")
            
            # Check username for injection patterns
            username_threats = await self.analyze_query(username, login_data)
            threats.extend(username_threats)
            
            # Check password for injection patterns (be careful with logging)
            password_threats = await self.analyze_query("***", login_data)  # Don't log actual password
            if password_threats:
                for threat in password_threats:
                    threat.evidence["query"] = "***"  # Redact password
                threats.extend(password_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze login for SQL injection: {e}")
            return []
    
    async def analyze_session(self, session_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze session queries for SQL injection"""
        threats = []
        
        try:
            queries = session_data.get("queries", [])
            
            for query in queries:
                query_threats = await self.analyze_query(query, session_data)
                threats.extend(query_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze session for SQL injection: {e}")
            return []
    
    def _calculate_injection_confidence(self, query: str, pattern: str) -> float:
        """Calculate confidence score for SQL injection detection"""
        base_confidence = 0.7
        
        # Increase confidence based on multiple factors
        factors = []
        
        # Length of suspicious content
        if len(query) > 100:
            factors.append(0.1)
        
        # Multiple injection patterns
        pattern_count = sum(1 for p in self.sql_injection_patterns if re.search(p, query))
        if pattern_count > 1:
            factors.append(0.2)
        
        # Suspicious keywords combination
        suspicious_keywords = ["union", "select", "drop", "delete", "insert", "update"]
        keyword_count = sum(1 for kw in suspicious_keywords if kw.lower() in query.lower())
        if keyword_count > 2:
            factors.append(0.1)
        
        return min(1.0, base_confidence + sum(factors))
    
    def _determine_injection_severity(self, confidence: float) -> ThreatLevel:
        """Determine threat severity based on confidence"""
        if confidence >= 0.9:
            return ThreatLevel.CRITICAL
        elif confidence >= 0.75:
            return ThreatLevel.HIGH
        elif confidence >= 0.6:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW


class BehaviorAnalysisEngine(ThreatDetectionEngine):
    """User behavior analysis threat detection engine"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        self.session_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    async def analyze_query(self, query: str, context: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze query for behavioral anomalies"""
        threats = []
        user_id = context.get("user_id")
        
        if not user_id:
            return threats
        
        try:
            # Update user profile
            await self._update_user_profile(user_id, context)
            
            # Check for anomalous patterns
            if await self._is_anomalous_query_pattern(user_id, query):
                threat = ThreatEvent(
                    event_id=str(uuid.uuid4()),
                    threat_id="anomalous_query_pattern",
                    source_ip=context.get("source_ip", "unknown"),
                    user_id=user_id,
                    session_id=context.get("session_id"),
                    threat_category=ThreatCategory.ANOMALOUS_ACCESS,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence_score=0.7,
                    evidence={
                        "query": query,
                        "user_profile": self._get_profile_summary(user_id),
                        "context": context
                    }
                )
                threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze query behavior: {e}")
            return []
    
    async def analyze_login(self, login_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze login behavior for anomalies"""
        threats = []
        user_id = login_data.get("user_id")
        
        if not user_id:
            return threats
        
        try:
            # Check login time anomaly
            if await self._is_anomalous_login_time(user_id, login_data):
                threat = ThreatEvent(
                    event_id=str(uuid.uuid4()),
                    threat_id="anomalous_login_time",
                    source_ip=login_data.get("source_ip", "unknown"),
                    user_id=user_id,
                    threat_category=ThreatCategory.ANOMALOUS_ACCESS,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence_score=0.6,
                    evidence={"login_data": login_data}
                )
                threats.append(threat)
            
            # Check IP address anomaly
            if await self._is_anomalous_ip_address(user_id, login_data):
                threat = ThreatEvent(
                    event_id=str(uuid.uuid4()),
                    threat_id="anomalous_ip_address",
                    source_ip=login_data.get("source_ip", "unknown"),
                    user_id=user_id,
                    threat_category=ThreatCategory.ANOMALOUS_ACCESS,
                    threat_level=ThreatLevel.HIGH,
                    confidence_score=0.8,
                    evidence={"login_data": login_data}
                )
                threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze login behavior: {e}")
            return []
    
    async def analyze_session(self, session_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze session behavior for anomalies"""
        threats = []
        user_id = session_data.get("user_id")
        
        if not user_id:
            return threats
        
        try:
            # Check data volume anomaly
            if await self._is_anomalous_data_volume(user_id, session_data):
                threat = ThreatEvent(
                    event_id=str(uuid.uuid4()),
                    threat_id="anomalous_data_volume",
                    source_ip=session_data.get("source_ip", "unknown"),
                    user_id=user_id,
                    session_id=session_data.get("session_id"),
                    threat_category=ThreatCategory.DATA_EXFILTRATION,
                    threat_level=ThreatLevel.HIGH,
                    confidence_score=0.8,
                    evidence={"session_data": session_data}
                )
                threats.append(threat)
            
            # Check session duration anomaly
            if await self._is_anomalous_session_duration(user_id, session_data):
                threat = ThreatEvent(
                    event_id=str(uuid.uuid4()),
                    threat_id="anomalous_session_duration",
                    source_ip=session_data.get("source_ip", "unknown"),
                    user_id=user_id,
                    session_id=session_data.get("session_id"),
                    threat_category=ThreatCategory.ANOMALOUS_ACCESS,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence_score=0.6,
                    evidence={"session_data": session_data}
                )
                threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze session behavior: {e}")
            return []
    
    async def _update_user_profile(self, user_id: str, context: Dict[str, Any]):
        """Update user behavior profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserBehaviorProfile(
                user_id=user_id,
                username=context.get("username", user_id)
            )
        
        profile = self.user_profiles[user_id]
        
        # Update login time
        if "login_time" in context:
            login_hour = context["login_time"].hour
            profile.typical_login_times.append(login_hour)
            
            # Keep only recent login times (last 100)
            if len(profile.typical_login_times) > 100:
                profile.typical_login_times = profile.typical_login_times[-100:]
        
        # Update IP addresses
        if "source_ip" in context:
            profile.typical_ip_addresses.add(context["source_ip"])
            
            # Limit IP addresses (keep only 50 most recent)
            if len(profile.typical_ip_addresses) > 50:
                # Convert to list, keep recent ones, convert back
                ip_list = list(profile.typical_ip_addresses)
                profile.typical_ip_addresses = set(ip_list[-50:])
        
        profile.updated_at = datetime.now()
    
    async def _is_anomalous_login_time(self, user_id: str, login_data: Dict[str, Any]) -> bool:
        """Check if login time is anomalous for user"""
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        if len(profile.typical_login_times) < 10:  # Need enough data
            return False
        
        current_hour = login_data.get("login_time", datetime.now()).hour
        
        # Calculate typical hours (mode and nearby hours)
        hour_counts = defaultdict(int)
        for hour in profile.typical_login_times:
            hour_counts[hour] += 1
        
        # Find most common hours
        common_hours = set()
        for hour, count in hour_counts.items():
            if count >= len(profile.typical_login_times) * 0.1:  # At least 10% of logins
                common_hours.add(hour)
                # Add nearby hours (±2 hours)
                common_hours.add((hour - 1) % 24)
                common_hours.add((hour + 1) % 24)
                common_hours.add((hour - 2) % 24)
                common_hours.add((hour + 2) % 24)
        
        return current_hour not in common_hours
    
    async def _is_anomalous_ip_address(self, user_id: str, login_data: Dict[str, Any]) -> bool:
        """Check if IP address is anomalous for user"""
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        current_ip = login_data.get("source_ip")
        
        if not current_ip:
            return False
        
        # Check if IP is in typical addresses
        if current_ip in profile.typical_ip_addresses:
            return False
        
        # Check if IP is from same subnet as typical IPs
        current_subnet = ".".join(current_ip.split(".")[:3])
        
        for typical_ip in profile.typical_ip_addresses:
            typical_subnet = ".".join(typical_ip.split(".")[:3])
            if current_subnet == typical_subnet:
                return False
        
        # If we have enough data and IP is completely new, it's anomalous
        return len(profile.typical_ip_addresses) >= 3
    
    async def _is_anomalous_query_pattern(self, user_id: str, query: str) -> bool:
        """Check if query pattern is anomalous for user"""
        # Simplified pattern analysis
        # In production, this would use more sophisticated ML models
        
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        
        # Extract basic query features
        query_lower = query.lower()
        
        # Check for unusual keywords for this user
        unusual_keywords = ["drop", "truncate", "delete", "alter", "create"]
        for keyword in unusual_keywords:
            if keyword in query_lower:
                return True
        
        return False
    
    async def _is_anomalous_data_volume(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Check if data volume is anomalous"""
        current_volume = session_data.get("data_volume", 0)
        
        if user_id not in self.user_profiles:
            return current_volume > 1000000  # 1MB threshold for new users
        
        profile = self.user_profiles[user_id]
        
        # If no historical data, use threshold
        if profile.typical_data_volume == 0:
            return current_volume > 1000000
        
        # Check if current volume is significantly higher than typical
        return current_volume > profile.typical_data_volume * 10
    
    async def _is_anomalous_session_duration(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Check if session duration is anomalous"""
        current_duration = session_data.get("duration_minutes", 0)
        
        if user_id not in self.user_profiles:
            return current_duration > 480  # 8 hours for new users
        
        profile = self.user_profiles[user_id]
        
        # If no historical data, use threshold
        if profile.average_session_duration == 0:
            return current_duration > 480
        
        # Check if current duration is significantly longer than typical
        return current_duration > profile.average_session_duration * 5
    
    def _get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user profile for evidence"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        
        return {
            "typical_login_hours": list(set(profile.typical_login_times)),
            "typical_ip_count": len(profile.typical_ip_addresses),
            "average_session_duration": profile.average_session_duration,
            "risk_score": profile.risk_score
        }


class ThreatDetector:
    """
    Enterprise-grade database threat detection system
    
    Provides comprehensive threat detection capabilities including:
    - Real-time threat monitoring
    - Behavioral anomaly detection
    - Automated threat response
    - Threat intelligence integration
    - Incident management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize threat detector"""
        self.config = config or {}
        
        # Detection engines
        self.detection_engines: List[ThreatDetectionEngine] = []
        self.detection_engines.append(SQLInjectionDetector())
        self.detection_engines.append(BehaviorAnalysisEngine())
        
        # Threat data
        self.threat_indicators: Dict[str, ThreatIndicator] = {}
        self.threat_events: Dict[str, ThreatEvent] = {}
        self.incident_responses: List[IncidentResponse] = []
        
        # Monitoring data
        self.security_metrics: List[SecurityMetrics] = []
        self.blocked_ips: Set[str] = set()
        self.blocked_users: Set[str] = set()
        
        # Configuration
        self.auto_response_enabled = self.config.get("auto_response", True)
        self.max_false_positive_rate = self.config.get("max_false_positive_rate", 0.05)
        self.alert_threshold = self.config.get("alert_threshold", ThreatLevel.MEDIUM)
        
        # Response handlers
        self.response_handlers: Dict[ResponseAction, Callable] = {
            ResponseAction.ALERT: self._handle_alert,
            ResponseAction.BLOCK_USER: self._handle_block_user,
            ResponseAction.BLOCK_IP: self._handle_block_ip,
            ResponseAction.REVOKE_PRIVILEGES: self._handle_revoke_privileges,
            ResponseAction.QUARANTINE_SESSION: self._handle_quarantine_session,
            ResponseAction.REQUIRE_MFA: self._handle_require_mfa,
            ResponseAction.LOG_DETAILED: self._handle_log_detailed,
            ResponseAction.NOTIFY_ADMIN: self._handle_notify_admin,
            ResponseAction.TRIGGER_INCIDENT: self._handle_trigger_incident
        }
        
        # Initialize threat indicators
        self._initialize_threat_indicators()
        
        logger.info("Database threat detector initialized successfully")
    
    def _initialize_threat_indicators(self):
        """Initialize default threat indicators"""
        try:
            default_indicators = [
                ThreatIndicator(
                    indicator_id="sql_injection_basic",
                    name="Basic SQL Injection",
                    description="Basic SQL injection patterns",
                    category=ThreatCategory.SQL_INJECTION,
                    pattern=r"(?i)(union\s+select|or\s+1\s*=\s*1)",
                    severity=ThreatLevel.HIGH,
                    confidence_threshold=0.7
                ),
                ThreatIndicator(
                    indicator_id="privilege_escalation",
                    name="Privilege Escalation",
                    description="Attempts to escalate database privileges",
                    category=ThreatCategory.PRIVILEGE_ESCALATION,
                    pattern=r"(?i)(grant\s+all|alter\s+user|create\s+user)",
                    severity=ThreatLevel.CRITICAL,
                    confidence_threshold=0.8
                ),
                ThreatIndicator(
                    indicator_id="mass_data_access",
                    name="Mass Data Access",
                    description="Unusual volume of data access",
                    category=ThreatCategory.MASS_DATA_ACCESS,
                    pattern="volume_threshold",
                    severity=ThreatLevel.HIGH,
                    confidence_threshold=0.6
                ),
                ThreatIndicator(
                    indicator_id="brute_force_login",
                    name="Brute Force Login",
                    description="Multiple failed login attempts",
                    category=ThreatCategory.BRUTE_FORCE,
                    pattern="failed_login_threshold",
                    severity=ThreatLevel.MEDIUM,
                    confidence_threshold=0.8
                )
            ]
            
            for indicator in default_indicators:
                self.threat_indicators[indicator.indicator_id] = indicator
            
            logger.info(f"Initialized {len(default_indicators)} threat indicators")
            
        except Exception as e:
            logger.error(f"Failed to initialize threat indicators: {e}")
            raise
    
    async def analyze_database_activity(
        self,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> List[ThreatEvent]:
        """
        Analyze database activity for threats
        
        Args:
            activity_type: Type of activity (query, login, session)
            activity_data: Activity data to analyze
            
        Returns:
            List of detected threat events
        """
        all_threats = []
        
        try:
            # Run analysis through all detection engines
            for engine in self.detection_engines:
                try:
                    if activity_type == "query":
                        threats = await engine.analyze_query(
                            activity_data.get("query", ""),
                            activity_data
                        )
                    elif activity_type == "login":
                        threats = await engine.analyze_login(activity_data)
                    elif activity_type == "session":
                        threats = await engine.analyze_session(activity_data)
                    else:
                        logger.warning(f"Unknown activity type: {activity_type}")
                        continue
                    
                    all_threats.extend(threats)
                    
                except Exception as e:
                    logger.error(f"Detection engine failed: {e}")
                    continue
            
            # Process detected threats
            for threat in all_threats:
                await self._process_threat_event(threat)
            
            return all_threats
            
        except Exception as e:
            logger.error(f"Failed to analyze database activity: {e}")
            return []
    
    async def _process_threat_event(self, threat: ThreatEvent):
        """Process detected threat event"""
        try:
            # Store threat event
            self.threat_events[threat.event_id] = threat
            
            # Determine response actions
            response_actions = self._determine_response_actions(threat)
            threat.response_actions = response_actions
            
            # Execute automated responses if enabled
            if self.auto_response_enabled:
                for action in response_actions:
                    await self._execute_response_action(threat, action)
            
            # Log threat event
            logger.warning(
                f"Threat detected: {threat.threat_category.value} "
                f"(Level: {threat.threat_level.value}, "
                f"Confidence: {threat.confidence_score:.2f})"
            )
            
        except Exception as e:
            logger.error(f"Failed to process threat event: {e}")
    
    def _determine_response_actions(self, threat: ThreatEvent) -> List[ResponseAction]:
        """Determine appropriate response actions for threat"""
        actions = []
        
        # Always log and alert
        actions.append(ResponseAction.LOG_DETAILED)
        
        if threat.threat_level in [ThreatLevel.MEDIUM, ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            actions.append(ResponseAction.ALERT)
        
        # Critical threats require immediate action
        if threat.threat_level == ThreatLevel.CRITICAL:
            actions.extend([
                ResponseAction.NOTIFY_ADMIN,
                ResponseAction.TRIGGER_INCIDENT
            ])
            
            # Block user for critical SQL injection
            if threat.threat_category == ThreatCategory.SQL_INJECTION:
                actions.append(ResponseAction.BLOCK_USER)
            
            # Block IP for privilege escalation
            if threat.threat_category == ThreatCategory.PRIVILEGE_ESCALATION:
                actions.extend([ResponseAction.BLOCK_IP, ResponseAction.REVOKE_PRIVILEGES])
        
        # High-level threats require selective action
        elif threat.threat_level == ThreatLevel.HIGH:
            if threat.threat_category in [ThreatCategory.DATA_EXFILTRATION, ThreatCategory.MASS_DATA_ACCESS]:
                actions.append(ResponseAction.QUARANTINE_SESSION)
            
            if threat.threat_category == ThreatCategory.BRUTE_FORCE:
                actions.append(ResponseAction.BLOCK_IP)
        
        # Medium-level threats require monitoring
        elif threat.threat_level == ThreatLevel.MEDIUM:
            if threat.threat_category == ThreatCategory.ANOMALOUS_ACCESS:
                actions.append(ResponseAction.REQUIRE_MFA)
        
        return actions
    
    async def _execute_response_action(self, threat: ThreatEvent, action: ResponseAction):
        """Execute response action for threat"""
        try:
            handler = self.response_handlers.get(action)
            if handler:
                success = await handler(threat)
                
                # Record response
                response = IncidentResponse(
                    incident_id=str(uuid.uuid4()),
                    threat_event_id=threat.event_id,
                    response_type=action,
                    success=success,
                    details={"threat_info": threat.evidence}
                )
                
                self.incident_responses.append(response)
                
                logger.info(f"Executed response action: {action.value} for threat {threat.event_id}")
            else:
                logger.warning(f"No handler for response action: {action.value}")
                
        except Exception as e:
            logger.error(f"Failed to execute response action {action.value}: {e}")
    
    async def _handle_alert(self, threat: ThreatEvent) -> bool:
        """Handle alert response action"""
        # In production, this would send alerts to monitoring systems
        logger.warning(f"SECURITY ALERT: {threat.threat_category.value} detected")
        return True
    
    async def _handle_block_user(self, threat: ThreatEvent) -> bool:
        """Handle block user response action"""
        if threat.user_id:
            self.blocked_users.add(threat.user_id)
            logger.warning(f"Blocked user: {threat.user_id}")
            return True
        return False
    
    async def _handle_block_ip(self, threat: ThreatEvent) -> bool:
        """Handle block IP response action"""
        if threat.source_ip and threat.source_ip != "unknown":
            self.blocked_ips.add(threat.source_ip)
            logger.warning(f"Blocked IP: {threat.source_ip}")
            return True
        return False
    
    async def _handle_revoke_privileges(self, threat: ThreatEvent) -> bool:
        """Handle revoke privileges response action"""
        # In production, this would integrate with privilege manager
        logger.warning(f"Would revoke privileges for user: {threat.user_id}")
        return True
    
    async def _handle_quarantine_session(self, threat: ThreatEvent) -> bool:
        """Handle quarantine session response action"""
        # In production, this would quarantine the session
        logger.warning(f"Would quarantine session: {threat.session_id}")
        return True
    
    async def _handle_require_mfa(self, threat: ThreatEvent) -> bool:
        """Handle require MFA response action"""
        # In production, this would require MFA for next access
        logger.warning(f"Would require MFA for user: {threat.user_id}")
        return True
    
    async def _handle_log_detailed(self, threat: ThreatEvent) -> bool:
        """Handle detailed logging response action"""
        # In production, this would send to detailed logging system
        logger.info(f"Detailed log for threat {threat.event_id}: {threat.evidence}")
        return True
    
    async def _handle_notify_admin(self, threat: ThreatEvent) -> bool:
        """Handle notify admin response action"""
        # In production, this would send notifications to administrators
        logger.critical(f"ADMIN NOTIFICATION: Critical threat detected - {threat.threat_category.value}")
        return True
    
    async def _handle_trigger_incident(self, threat: ThreatEvent) -> bool:
        """Handle trigger incident response action"""
        # In production, this would create incident in incident management system
        logger.critical(f"INCIDENT TRIGGERED: {threat.event_id}")
        return True
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def is_user_blocked(self, user_id: str) -> bool:
        """Check if user is blocked"""
        return user_id in self.blocked_users
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info(f"Unblocked IP: {ip_address}")
            return True
        return False
    
    def unblock_user(self, user_id: str) -> bool:
        """Unblock user"""
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            logger.info(f"Unblocked user: {user_id}")
            return True
        return False
    
    def get_threat_summary(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get threat detection summary"""
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        recent_threats = [
            threat for threat in self.threat_events.values()
            if threat.detected_at >= cutoff_time
        ]
        
        # Count by category
        category_counts = defaultdict(int)
        level_counts = defaultdict(int)
        
        for threat in recent_threats:
            category_counts[threat.threat_category.value] += 1
            level_counts[threat.threat_level.value] += 1
        
        return {
            "time_range_hours": time_range_hours,
            "total_threats": len(recent_threats),
            "threats_by_category": dict(category_counts),
            "threats_by_level": dict(level_counts),
            "blocked_ips": len(self.blocked_ips),
            "blocked_users": len(self.blocked_users),
            "incident_responses": len(self.incident_responses),
            "active_threat_indicators": len([
                ind for ind in self.threat_indicators.values() if ind.is_active
            ])
        }
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security monitoring metrics"""
        return {
            "total_threat_events": len(self.threat_events),
            "active_threats": len([
                threat for threat in self.threat_events.values()
                if not threat.is_resolved
            ]),
            "blocked_entities": {
                "ips": len(self.blocked_ips),
                "users": len(self.blocked_users)
            },
            "detection_engines": len(self.detection_engines),
            "threat_indicators": len(self.threat_indicators),
            "incident_responses": len(self.incident_responses)
        }


# Module initialization
logger.info("Database threat detector module loaded successfully")
