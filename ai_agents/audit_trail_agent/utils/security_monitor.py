"""
Security Audit Monitor - Advanced Security Event Detection & Analysis

Industrial-grade security monitoring system for real-time threat detection,
security incident response, and advanced threat analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
import hashlib
import ipaddress
from datetime import datetime, timezone, timedelta
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
import json
import re
import numpy as np
from collections import defaultdict, deque
from contextlib import asynccontextmanager

import geoip2.database
import geoip2.errors
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, Gauge

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import SecurityError, AuditError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SecurityError, AuditError = globals().get('SecurityError, AuditError', Exception)
from ...models.security_models import SecurityIncident, ThreatIndicator, SecurityPolicy
from ...security.threat_detection import ThreatDetector
from ...utils.ip_intelligence import IPIntelligence
from ...utils.behavior_analyzer import BehaviorAnalyzer

logger = logging.getLogger(__name__)

class ThreatLevel(IntEnum):
    """Security threat level classification"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class SecurityEventType(Enum):
    """Security event type classification"""
    FAILED_LOGIN = "failed_login"
    BRUTE_FORCE = "brute_force_attack"
    SQL_INJECTION = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach_attempt"
    MALWARE_DETECTION = "malware_detection"
    DDOS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"
    API_ABUSE = "api_abuse"
    ACCOUNT_TAKEOVER = "account_takeover"
    SUSPICIOUS_DOWNLOAD = "suspicious_download"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    COMPLIANCE_VIOLATION = "compliance_violation"

class ResponseAction(Enum):
    """Automated security response actions"""
    LOG_ONLY = "log_only"
    ALERT_ADMIN = "alert_admin"
    BLOCK_IP = "block_ip"
    SUSPEND_ACCOUNT = "suspend_account"
    FORCE_LOGOUT = "force_logout"
    REQUIRE_MFA = "require_mfa"
    QUARANTINE_CONTENT = "quarantine_content"
    ESCALATE_TO_SOC = "escalate_to_soc"

@dataclass
class SecurityConfiguration:
    """Advanced security monitoring configuration"""
    enable_real_time_monitoring: bool = True
    enable_behavioral_analysis: bool = True
    enable_threat_intelligence: bool = True
    enable_automated_response: bool = True
    max_failed_login_attempts: int = 5
    brute_force_window_minutes: int = 15
    anomaly_detection_sensitivity: float = 0.8
    threat_score_threshold: float = 0.7
    auto_block_duration_hours: int = 24
    geo_blocking_enabled: bool = True
    allowed_countries: Set[str] = field(default_factory=lambda: {"DE", "US", "GB", "FR"})

@dataclass
class SecurityMetrics:
    """Comprehensive security metrics tracking"""
    total_threats_detected: int = 0
    threats_by_type: Dict[str, int] = field(default_factory=dict)
    blocked_ips: int = 0
    suspended_accounts: int = 0
    false_positives: int = 0
    mean_detection_time: float = 0.0
    mean_response_time: float = 0.0

class SecurityAuditMonitor:
    """
    Enterprise Security Audit Monitor
    
    Advanced security monitoring system providing:
    - Real-time threat detection
    - Behavioral anomaly analysis
    - Automated incident response
    - Threat intelligence integration
    - Geographic access control
    - Advanced attack pattern recognition
    """

    def __init__(self, config: Optional[SecurityConfiguration] = None):
        self.config = config or SecurityConfiguration()
        self.metrics = SecurityMetrics()
        
        # Threat detection components
        self.threat_detector = ThreatDetector()
        self.ip_intelligence = IPIntelligence()
        self.behavior_analyzer = BehaviorAnalyzer()
        
        # Real-time monitoring state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.failed_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns: Dict[str, List[Dict]] = defaultdict(list)
        
        # Performance metrics
        self.threat_counter = Counter('security_threats_total', 'Total security threats detected', ['threat_type', 'severity'])
        self.detection_time = Histogram('security_detection_seconds', 'Threat detection time')
        self.response_time = Histogram('security_response_seconds', 'Security response time')
        self.active_threats = Gauge('security_active_threats', 'Currently active security threats')
        
        # GeoIP database for location analysis
        try:
            self.geoip_reader = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-Country.mmdb')
        except Exception:
            logger.warning("GeoIP database not available, geographic analysis disabled")
            self.geoip_reader = None

        logger.info("SecurityAuditMonitor initialized with advanced threat detection")

    async def monitor_security_event(
        self,
        event_type: SecurityEventType,
        source_ip: str,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Monitor and analyze security event with comprehensive threat assessment
        
        Args:
            event_type: Type of security event
            source_ip: Source IP address
            user_id: User identifier (if applicable)
            user_agent: User agent string
            request_data: Additional request data
            timestamp: Event timestamp
            
        Returns:
            Security analysis results with recommended actions
        """
        start_time = time.time()
        
        try:
            if not timestamp:
                timestamp = datetime.now(timezone.utc)
            
            # Validate IP address
            try:
                ip_obj = ipaddress.ip_address(source_ip)
            except ValueError:
                raise SecurityError(f"Invalid IP address: {source_ip}")
            
            # Initialize threat analysis context
            threat_context = {
                "event_type": event_type.value,
                "source_ip": source_ip,
                "user_id": user_id,
                "user_agent": user_agent,
                "timestamp": timestamp.isoformat(),
                "threat_score": 0.0,
                "threat_indicators": [],
                "recommended_actions": []
            }
            
            # Geographic analysis
            geo_analysis = await self._analyze_geographic_context(source_ip)
            threat_context["geographic_info"] = geo_analysis
            
            # IP reputation analysis
            ip_reputation = await self.ip_intelligence.analyze_ip(source_ip)
            threat_context["ip_reputation"] = ip_reputation
            
            # Behavioral analysis
            if user_id:
                behavior_analysis = await self._analyze_user_behavior(user_id, event_type, timestamp)
                threat_context["behavior_analysis"] = behavior_analysis
            
            # Pattern analysis
            pattern_analysis = await self._analyze_attack_patterns(event_type, source_ip, request_data)
            threat_context["pattern_analysis"] = pattern_analysis
            
            # Calculate composite threat score
            threat_score = await self._calculate_threat_score(threat_context)
            threat_context["threat_score"] = threat_score
            
            # Determine threat level
            threat_level = self._determine_threat_level(threat_score)
            threat_context["threat_level"] = threat_level.name
            
            # Generate security incident if threat level is significant
            if threat_level >= ThreatLevel.MEDIUM:
                incident_id = await self._create_security_incident(threat_context, threat_level)
                threat_context["incident_id"] = incident_id
            
            # Determine automated response actions
            response_actions = await self._determine_response_actions(threat_context, threat_level)
            threat_context["recommended_actions"] = response_actions
            
            # Execute automated responses if enabled
            if self.config.enable_automated_response:
                executed_actions = await self._execute_response_actions(response_actions, threat_context)
                threat_context["executed_actions"] = executed_actions
            
            # Update tracking state
            await self._update_tracking_state(source_ip, user_id, event_type, threat_level)
            
            # Update metrics
            self.threat_counter.labels(
                threat_type=event_type.value,
                severity=threat_level.name
            ).inc()
            self.detection_time.observe(time.time() - start_time)
            self.metrics.total_threats_detected += 1
            self.metrics.threats_by_type[event_type.value] = self.metrics.threats_by_type.get(event_type.value, 0) + 1
            
            logger.info(f"Security event analyzed: {event_type.value} from {source_ip} (threat_score: {threat_score})")
            return threat_context
            
        except Exception as e:
            logger.error(f"Security event monitoring failed: {str(e)}")
            raise SecurityError(f"Security monitoring failed: {str(e)}")

    async def detect_brute_force_attack(
        self,
        source_ip: str,
        user_id: Optional[str] = None,
        time_window: timedelta = timedelta(minutes=15)
    ) -> Dict[str, Any]:
        """
        Advanced brute force attack detection with pattern analysis
        
        Args:
            source_ip: Source IP address
            user_id: Target user ID (if known)
            time_window: Time window for analysis
            
        Returns:
            Brute force detection results
        """
        try:
            current_time = datetime.now(timezone.utc)
            window_start = current_time - time_window
            
            # Analyze failed login attempts from IP
            ip_attempts = self.failed_attempts.get(source_ip, deque())
            recent_attempts = [
                attempt for attempt in ip_attempts
                if attempt['timestamp'] >= window_start
            ]
            
            # Analyze attempts targeting specific user
            user_targeted_attempts = 0
            if user_id:
                user_targeted_attempts = len([
                    attempt for attempt in recent_attempts
                    if attempt.get('user_id') == user_id
                ])
            
            # Detect distributed brute force (multiple IPs targeting single user)
            distributed_attack = False
            if user_id:
                distributed_attack = await self._detect_distributed_brute_force(user_id, time_window)
            
            # Calculate brute force indicators
            attempt_frequency = len(recent_attempts) / max(time_window.total_seconds() / 60, 1)
            
            brute_force_detected = (
                len(recent_attempts) >= self.config.max_failed_login_attempts or
                attempt_frequency > 10 or  # More than 10 attempts per minute
                distributed_attack
            )
            
            detection_result = {
                "brute_force_detected": brute_force_detected,
                "source_ip": source_ip,
                "target_user": user_id,
                "time_window": time_window.total_seconds(),
                "total_attempts": len(recent_attempts),
                "user_targeted_attempts": user_targeted_attempts,
                "attempt_frequency_per_minute": round(attempt_frequency, 2),
                "distributed_attack": distributed_attack,
                "threat_score": min(len(recent_attempts) / self.config.max_failed_login_attempts, 1.0),
                "analysis_timestamp": current_time.isoformat()
            }
            
            # If brute force detected, trigger security response
            if brute_force_detected:
                await self.monitor_security_event(
                    SecurityEventType.BRUTE_FORCE,
                    source_ip,
                    user_id,
                    request_data=detection_result
                )
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Brute force detection failed: {str(e)}")
            raise SecurityError(f"Brute force detection failed: {str(e)}")

    async def analyze_api_abuse(
        self,
        api_endpoint: str,
        source_ip: str,
        user_id: Optional[str] = None,
        request_count: int = 1,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Detect and analyze API abuse patterns and rate limiting violations
        
        Args:
            api_endpoint: API endpoint being accessed
            source_ip: Source IP address
            user_id: User making requests (if authenticated)
            request_count: Number of requests in this batch
            time_window: Time window for analysis
            
        Returns:
            API abuse analysis results
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Track API usage patterns
            usage_key = f"{api_endpoint}:{source_ip}:{user_id or 'anonymous'}"
            
            # Analyze request patterns
            abuse_indicators = await self._analyze_api_patterns(
                api_endpoint, source_ip, user_id, request_count, time_window
            )
            
            # Detect rapid-fire requests
            rapid_fire_detected = abuse_indicators.get('rapid_fire_requests', False)
            
            # Detect resource exhaustion attempts
            resource_exhaustion = abuse_indicators.get('resource_exhaustion_attempt', False)
            
            # Detect scraping behavior
            scraping_detected = abuse_indicators.get('scraping_behavior', False)
            
            # Calculate abuse score
            abuse_score = (
                (0.4 if rapid_fire_detected else 0) +
                (0.3 if resource_exhaustion else 0) +
                (0.3 if scraping_detected else 0)
            )
            
            analysis_result = {
                "api_abuse_detected": abuse_score >= 0.5,
                "abuse_score": abuse_score,
                "api_endpoint": api_endpoint,
                "source_ip": source_ip,
                "user_id": user_id,
                "indicators": abuse_indicators,
                "rapid_fire_requests": rapid_fire_detected,
                "resource_exhaustion": resource_exhaustion,
                "scraping_behavior": scraping_detected,
                "analysis_timestamp": current_time.isoformat()
            }
            
            # If API abuse detected, trigger security response
            if analysis_result["api_abuse_detected"]:
                await self.monitor_security_event(
                    SecurityEventType.API_ABUSE,
                    source_ip,
                    user_id,
                    request_data=analysis_result
                )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"API abuse analysis failed: {str(e)}")
            raise SecurityError(f"API abuse analysis failed: {str(e)}")

    async def detect_insider_threat(
        self,
        user_id: str,
        action: str,
        resource_accessed: Optional[str] = None,
        time_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advanced insider threat detection using behavioral analytics
        
        Args:
            user_id: User performing the action
            action: Action being performed
            resource_accessed: Resource being accessed
            time_context: Temporal context (time of day, day of week, etc.)
            
        Returns:
            Insider threat analysis results
        """
        try:
            # Analyze user behavior patterns
            behavior_baseline = await self.behavior_analyzer.get_user_baseline(user_id)
            current_behavior = await self.behavior_analyzer.analyze_current_session(user_id)
            
            # Detect anomalous access patterns
            access_anomalies = await self._detect_access_anomalies(
                user_id, action, resource_accessed, behavior_baseline
            )
            
            # Analyze temporal anomalies
            temporal_anomalies = await self._detect_temporal_anomalies(
                user_id, action, time_context, behavior_baseline
            )
            
            # Check for privilege escalation attempts
            privilege_escalation = await self._detect_privilege_escalation(user_id, action, resource_accessed)
            
            # Analyze data exfiltration indicators
            data_exfiltration_risk = await self._analyze_data_exfiltration_risk(
                user_id, action, resource_accessed
            )
            
            # Calculate insider threat score
            threat_score = (
                access_anomalies.get('anomaly_score', 0) * 0.3 +
                temporal_anomalies.get('anomaly_score', 0) * 0.2 +
                (0.4 if privilege_escalation else 0) +
                data_exfiltration_risk.get('risk_score', 0) * 0.1
            )
            
            threat_result = {
                "insider_threat_detected": threat_score >= 0.6,
                "threat_score": threat_score,
                "user_id": user_id,
                "action": action,
                "resource_accessed": resource_accessed,
                "access_anomalies": access_anomalies,
                "temporal_anomalies": temporal_anomalies,
                "privilege_escalation": privilege_escalation,
                "data_exfiltration_risk": data_exfiltration_risk,
                "behavior_deviation": current_behavior.get('deviation_score', 0),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # If insider threat detected, trigger security response
            if threat_result["insider_threat_detected"]:
                await self.monitor_security_event(
                    SecurityEventType.INSIDER_THREAT,
                    current_behavior.get('source_ip', '127.0.0.1'),
                    user_id,
                    request_data=threat_result
                )
            
            return threat_result
            
        except Exception as e:
            logger.error(f"Insider threat detection failed: {str(e)}")
            raise SecurityError(f"Insider threat detection failed: {str(e)}")

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive security monitoring dashboard data
        
        Returns:
            Security dashboard data with real-time metrics
        """
        try:
            current_time = datetime.now(timezone.utc)
            last_24h = current_time - timedelta(hours=24)
            
            # Get recent security incidents
            async with get_db_session() as session:
                recent_incidents = session.query(SecurityIncident).filter(
                    SecurityIncident.created_at >= last_24h
                ).all()
            
            # Analyze threat landscape
            threat_landscape = await self._analyze_threat_landscape(recent_incidents)
            
            # Get top attacked resources
            top_targets = await self._get_top_attack_targets(recent_incidents)
            
            # Get geographic attack distribution
            geo_distribution = await self._get_geographic_attack_distribution(recent_incidents)
            
            # Calculate security scores
            security_scores = await self._calculate_security_scores()
            
            dashboard_data = {
                "timestamp": current_time.isoformat(),
                "summary": {
                    "total_incidents_24h": len(recent_incidents),
                    "critical_incidents": len([i for i in recent_incidents if i.threat_level == ThreatLevel.CRITICAL]),
                    "blocked_ips": len(self.blocked_ips),
                    "active_threats": self.active_threats._value.get(),
                    "overall_security_score": security_scores.get('overall', 0.8)
                },
                "threat_landscape": threat_landscape,
                "top_attack_targets": top_targets,
                "geographic_distribution": geo_distribution,
                "security_metrics": self.metrics.__dict__,
                "recent_incidents": [
                    {
                        "id": incident.id,
                        "type": incident.event_type,
                        "threat_level": incident.threat_level,
                        "source_ip": incident.source_ip,
                        "created_at": incident.created_at.isoformat(),
                        "status": incident.status
                    }
                    for incident in recent_incidents[-10:]  # Last 10 incidents
                ]
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Security dashboard generation failed: {str(e)}")
            raise SecurityError(f"Dashboard generation failed: {str(e)}")

    # Private helper methods
    async def _analyze_geographic_context(self, ip_address: str) -> Dict[str, Any]:
        """Analyze geographic context of IP address"""
        geo_info = {
            "country": "Unknown",
            "is_allowed_country": True,
            "is_suspicious_location": False,
            "vpn_detected": False
        }
        
        if self.geoip_reader:
            try:
                response = self.geoip_reader.country(ip_address)
                country_code = response.country.iso_code
                geo_info["country"] = country_code
                geo_info["is_allowed_country"] = country_code in self.config.allowed_countries
                
                # Additional geographic risk analysis
                geo_info["is_suspicious_location"] = await self._is_suspicious_location(country_code)
                
            except geoip2.errors.AddressNotFoundError:
                geo_info["is_suspicious_location"] = True
                
        return geo_info

    async def _analyze_user_behavior(
        self,
        user_id: str,
        event_type: SecurityEventType,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Analyze user behavioral patterns for anomaly detection"""
        baseline = await self.behavior_analyzer.get_user_baseline(user_id)
        current_session = await self.behavior_analyzer.analyze_current_session(user_id)
        
        # Compare current behavior with baseline
        deviation_score = await self.behavior_analyzer.calculate_deviation_score(
            baseline, current_session
        )
        
        return {
            "deviation_score": deviation_score,
            "is_anomalous": deviation_score > 0.7,
            "behavior_indicators": current_session.get('indicators', []),
            "baseline_deviation": {
                "login_time": abs((timestamp.hour - baseline.get('typical_login_hour', 12)) / 12),
                "session_duration": current_session.get('session_duration_minutes', 0) / 60,
                "access_patterns": current_session.get('access_pattern_score', 0)
            }
        }

    async def _analyze_attack_patterns(
        self,
        event_type: SecurityEventType,
        source_ip: str,
        request_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze attack patterns and signatures"""
        patterns = {
            "sql_injection_detected": False,
            "xss_detected": False,
            "command_injection_detected": False,
            "path_traversal_detected": False,
            "pattern_confidence": 0.0
        }
        
        if request_data:
            # SQL injection pattern detection
            sql_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                r"(\b(UNION|OR|AND)\s+\d+=\d+)",
                r"('|(\\x27)|(\\x2D)|(\\x5C))"
            ]
            
            request_string = json.dumps(request_data).lower()
            
            for pattern in sql_patterns:
                if re.search(pattern, request_string, re.IGNORECASE):
                    patterns["sql_injection_detected"] = True
                    patterns["pattern_confidence"] += 0.25
            
            # XSS pattern detection
            xss_patterns = [
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe.*?>"
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, request_string, re.IGNORECASE):
                    patterns["xss_detected"] = True
                    patterns["pattern_confidence"] += 0.25
        
        return patterns

    async def _calculate_threat_score(self, threat_context: Dict[str, Any]) -> float:
        """Calculate composite threat score from multiple indicators"""
        score = 0.0
        
        # IP reputation score
        ip_rep = threat_context.get('ip_reputation', {})
        if ip_rep.get('is_malicious', False):
            score += 0.4
        elif ip_rep.get('is_suspicious', False):
            score += 0.2
        
        # Geographic score
        geo_info = threat_context.get('geographic_info', {})
        if not geo_info.get('is_allowed_country', True):
            score += 0.2
        if geo_info.get('is_suspicious_location', False):
            score += 0.1
        
        # Behavioral score
        behavior = threat_context.get('behavior_analysis', {})
        if behavior.get('is_anomalous', False):
            score += 0.3
        
        # Pattern analysis score
        patterns = threat_context.get('pattern_analysis', {})
        score += patterns.get('pattern_confidence', 0.0)
        
        return min(score, 1.0)

    def _determine_threat_level(self, threat_score: float) -> ThreatLevel:
        """Determine threat level based on composite score"""
        if threat_score >= 0.9:
            return ThreatLevel.EMERGENCY
        elif threat_score >= 0.7:
            return ThreatLevel.CRITICAL
        elif threat_score >= 0.5:
            return ThreatLevel.HIGH
        elif threat_score >= 0.3:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    async def _determine_response_actions(
        self,
        threat_context: Dict[str, Any],
        threat_level: ThreatLevel
    ) -> List[ResponseAction]:
        """Determine appropriate automated response actions"""
        actions = [ResponseAction.LOG_ONLY]
        
        if threat_level >= ThreatLevel.MEDIUM:
            actions.append(ResponseAction.ALERT_ADMIN)
        
        if threat_level >= ThreatLevel.HIGH:
            actions.extend([
                ResponseAction.BLOCK_IP,
                ResponseAction.REQUIRE_MFA
            ])
        
        if threat_level >= ThreatLevel.CRITICAL:
            actions.extend([
                ResponseAction.SUSPEND_ACCOUNT,
                ResponseAction.FORCE_LOGOUT,
                ResponseAction.ESCALATE_TO_SOC
            ])
        
        return actions

    async def _execute_response_actions(
        self,
        actions: List[ResponseAction],
        threat_context: Dict[str, Any]
    ) -> List[str]:
        """Execute automated security response actions"""
        executed = []
        
        for action in actions:
            try:
                if action == ResponseAction.BLOCK_IP:
                    await self._block_ip_address(threat_context['source_ip'])
                    executed.append(f"IP {threat_context['source_ip']} blocked")
                
                elif action == ResponseAction.SUSPEND_ACCOUNT and threat_context.get('user_id'):
                    await self._suspend_user_account(threat_context['user_id'])
                    executed.append(f"Account {threat_context['user_id']} suspended")
                
                elif action == ResponseAction.ALERT_ADMIN:
                    await self._send_security_alert(threat_context)
                    executed.append("Security team alerted")
                
                # Add other response actions as needed
                
            except Exception as e:
                logger.error(f"Failed to execute response action {action}: {str(e)}")
        
        return executed

    # Additional helper methods would be implemented here for completeness...
    
    async def _create_security_incident(
        self,
        threat_context: Dict[str, Any],
        threat_level: ThreatLevel
    ) -> str:
        """Create security incident record"""
        incident_id = str(uuid.uuid4())
        
        try:
            async with get_db_session() as session:
                incident = SecurityIncident(
                    incident_id=incident_id,
                    event_type=threat_context['event_type'],
                    threat_level=threat_level.value,
                    source_ip=threat_context['source_ip'],
                    user_id=threat_context.get('user_id'),
                    threat_score=threat_context['threat_score'],
                    details=json.dumps(threat_context),
                    status='OPEN',
                    created_at=datetime.now(timezone.utc)
                )
                session.add(incident)
                await session.commit()
                
            return incident_id
            
        except Exception as e:
            logger.error(f"Failed to create security incident: {str(e)}")
            return incident_id

    async def _update_tracking_state(
        self,
        source_ip: str,
        user_id: Optional[str],
        event_type: SecurityEventType,
        threat_level: ThreatLevel
    ) -> None:
        """Update internal tracking state for ongoing monitoring"""
        # Update failed attempt tracking
        if event_type == SecurityEventType.FAILED_LOGIN:
            self.failed_attempts[source_ip].append({
                'timestamp': datetime.now(timezone.utc),
                'user_id': user_id,
                'threat_level': threat_level.value
            })
        
        # Update active threat gauge
        if threat_level >= ThreatLevel.HIGH:
            self.active_threats.inc()
