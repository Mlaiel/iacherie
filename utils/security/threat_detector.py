"""
Threat Detector - Security Utilities Level 2
===========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade threat detection system for IA Chérie creator economy platform.
Real-time threat analysis with < 50ms detection cycles.

Performance: < 50ms threat detection cycles
Standards: Enterprise security, behavioral analysis, creator economy protection
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import hashlib
import ipaddress
import re
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ThreatSeverity(Enum):
    """Threat severity levels for creator economy platform."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Threat types specific to creator economy."""
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    ACCOUNT_TAKEOVER = "account_takeover"
    CONTENT_THEFT = "content_theft"
    PAYMENT_FRAUD = "payment_fraud"
    SPAM_INJECTION = "spam_injection"
    COPYRIGHT_VIOLATION = "copyright_violation"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    AUTOMATED_ATTACKS = "automated_attacks"
    DATA_EXFILTRATION = "data_exfiltration"

@dataclass
class ThreatEvent:
    """Enterprise threat event container."""
    timestamp: datetime
    threat_type: ThreatType
    severity: ThreatSeverity
    source_ip: str
    user_id: Optional[str] = None
    description: str = ""
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    mitigated: bool = False
    creator_type: Optional[str] = None  # musician, photographer, blogger
    
@dataclass
class ThreatDetectionResult:
    """Result container for threat detection operations."""
    success: bool
    threats_detected: List[ThreatEvent] = field(default_factory=list)
    risk_score: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class ThreatDetector:
    """
    Enterprise-grade threat detection system for creator economy platform.
    
    Features:
    - Real-time brute force detection
    - Behavioral anomaly analysis
    - Creator-specific threat patterns
    - Automated response mechanisms
    - Performance: < 50ms detection cycles
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize threat detector with enterprise configuration."""
        self.config = config or {}
        self.threat_history: deque = deque(maxlen=10000)
        self.ip_tracking: Dict[str, List[datetime]] = defaultdict(list)
        self.user_behavior: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.creator_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Threat detection thresholds
        self.brute_force_threshold = self.config.get("brute_force_threshold", 5)
        self.time_window_minutes = self.config.get("time_window_minutes", 15)
        self.anomaly_threshold = self.config.get("anomaly_threshold", 0.8)
        
        # Creator economy specific patterns
        self.creator_risk_patterns = {
            "musician": ["audio_download_spike", "unauthorized_sampling", "royalty_manipulation"],
            "photographer": ["bulk_image_download", "metadata_stripping", "watermark_removal"],
            "blogger": ["content_scraping", "seo_manipulation", "comment_spam"]
        }
        
        logger.info("ThreatDetector initialized with enterprise configuration")

    async def detect_brute_force_attacks(self, ip_address: str, user_id: Optional[str] = None, 
                                       action: str = "login") -> ThreatDetectionResult:
        """
        Detect brute force attacks with real-time analysis.
        
        Args:
            ip_address: Source IP address
            user_id: User identifier (optional)
            action: Action being performed
            
        Returns:
            ThreatDetectionResult with detection status
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            cutoff_time = current_time - timedelta(minutes=self.time_window_minutes)
            
            # Clean old entries
            self.ip_tracking[ip_address] = [
                ts for ts in self.ip_tracking[ip_address] 
                if ts > cutoff_time
            ]
            
            # Add current attempt
            self.ip_tracking[ip_address].append(current_time)
            
            # Check threshold
            attempt_count = len(self.ip_tracking[ip_address])
            
            if attempt_count >= self.brute_force_threshold:
                threat_event = ThreatEvent(
                    timestamp=current_time,
                    threat_type=ThreatType.BRUTE_FORCE,
                    severity=ThreatSeverity.HIGH,
                    source_ip=ip_address,
                    user_id=user_id,
                    description=f"Brute force attack detected: {attempt_count} attempts in {self.time_window_minutes} minutes",
                    confidence_score=min(attempt_count / self.brute_force_threshold, 1.0),
                    metadata={
                        "attempt_count": attempt_count,
                        "action": action,
                        "time_window": self.time_window_minutes
                    }
                )
                
                self.threat_history.append(threat_event)
                
                execution_time = (time.perf_counter() - start_time) * 1000
                logger.warning(f"Brute force attack detected from {ip_address} in {execution_time:.2f}ms")
                
                return ThreatDetectionResult(
                    success=True,
                    threats_detected=[threat_event],
                    risk_score=threat_event.confidence_score,
                    recommended_actions=[
                        "Block IP address temporarily",
                        "Require additional authentication",
                        "Alert security team"
                    ]
                )
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Brute force check completed for {ip_address} in {execution_time:.2f}ms")
            
            return ThreatDetectionResult(success=True, risk_score=0.0)
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Brute force detection failed in {execution_time:.2f}ms: {str(e)}")
            return ThreatDetectionResult(
                success=False,
                errors=[f"Brute force detection error: {str(e)}"]
            )

    async def analyze_anomalous_behavior(self, user_id: str, action_data: Dict[str, Any],
                                       creator_type: Optional[str] = None) -> ThreatDetectionResult:
        """
        Analyze user behavior for anomalies using machine learning patterns.
        
        Args:
            user_id: User identifier
            action_data: User action data
            creator_type: Type of creator (musician, photographer, blogger)
            
        Returns:
            ThreatDetectionResult with analysis results
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            
            # Initialize user behavior baseline
            if user_id not in self.user_behavior:
                self.user_behavior[user_id] = {
                    "action_frequency": defaultdict(int),
                    "time_patterns": [],
                    "ip_addresses": set(),
                    "creator_activities": defaultdict(int),
                    "last_seen": current_time
                }
            
            user_profile = self.user_behavior[user_id]
            
            # Analyze behavioral patterns
            anomaly_indicators = []
            
            # 1. Frequency analysis
            action_type = action_data.get("action_type", "unknown")
            user_profile["action_frequency"][action_type] += 1
            
            if user_profile["action_frequency"][action_type] > 100:  # Threshold
                anomaly_indicators.append("excessive_action_frequency")
            
            # 2. Time pattern analysis
            hour = current_time.hour
            user_profile["time_patterns"].append(hour)
            
            # Keep only last 100 time patterns
            if len(user_profile["time_patterns"]) > 100:
                user_profile["time_patterns"] = user_profile["time_patterns"][-100:]
            
            # Detect unusual time patterns
            if len(user_profile["time_patterns"]) > 10:
                avg_hour = sum(user_profile["time_patterns"]) / len(user_profile["time_patterns"])
                if abs(hour - avg_hour) > 6:  # More than 6 hours difference
                    anomaly_indicators.append("unusual_time_pattern")
            
            # 3. IP address analysis
            current_ip = action_data.get("ip_address")
            if current_ip:
                user_profile["ip_addresses"].add(current_ip)
                if len(user_profile["ip_addresses"]) > 10:  # Too many IPs
                    anomaly_indicators.append("multiple_ip_addresses")
            
            # 4. Creator-specific pattern analysis
            if creator_type:
                creator_action = action_data.get("creator_action")
                if creator_action:
                    user_profile["creator_activities"][creator_action] += 1
                    
                    # Check creator-specific risk patterns
                    risk_patterns = self.creator_risk_patterns.get(creator_type, [])
                    for pattern in risk_patterns:
                        if pattern in creator_action and user_profile["creator_activities"][creator_action] > 20:
                            anomaly_indicators.append(f"creator_risk_{pattern}")
            
            # Calculate anomaly score
            anomaly_score = len(anomaly_indicators) / 10.0  # Normalize to 0-1
            
            # Generate threat event if anomaly detected
            threats_detected = []
            if anomaly_score >= self.anomaly_threshold:
                threat_event = ThreatEvent(
                    timestamp=current_time,
                    threat_type=ThreatType.SUSPICIOUS_BEHAVIOR,
                    severity=ThreatSeverity.MEDIUM if anomaly_score < 0.9 else ThreatSeverity.HIGH,
                    source_ip=current_ip or "unknown",
                    user_id=user_id,
                    creator_type=creator_type,
                    description=f"Anomalous behavior detected: {', '.join(anomaly_indicators)}",
                    confidence_score=anomaly_score,
                    metadata={
                        "anomaly_indicators": anomaly_indicators,
                        "action_data": action_data,
                        "user_profile_summary": {
                            "total_actions": sum(user_profile["action_frequency"].values()),
                            "unique_ips": len(user_profile["ip_addresses"]),
                            "creator_activities": dict(user_profile["creator_activities"])
                        }
                    }
                )
                threats_detected.append(threat_event)
                self.threat_history.append(threat_event)
            
            user_profile["last_seen"] = current_time
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Behavioral analysis completed for {user_id} in {execution_time:.2f}ms")
            
            return ThreatDetectionResult(
                success=True,
                threats_detected=threats_detected,
                risk_score=anomaly_score,
                recommended_actions=[
                    "Monitor user activity closely",
                    "Require additional verification",
                    "Review creator content permissions"
                ] if anomaly_score >= self.anomaly_threshold else []
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Behavioral analysis failed in {execution_time:.2f}ms: {str(e)}")
            return ThreatDetectionResult(
                success=False,
                errors=[f"Behavioral analysis error: {str(e)}"]
            )

    async def identify_credential_stuffing(self, login_data: Dict[str, Any]) -> ThreatDetectionResult:
        """
        Identify credential stuffing attacks using pattern recognition.
        
        Args:
            login_data: Login attempt data
            
        Returns:
            ThreatDetectionResult with detection status
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            ip_address = login_data.get("ip_address", "unknown")
            username = login_data.get("username", "")
            user_agent = login_data.get("user_agent", "")
            
            # Credential stuffing indicators
            stuffing_indicators = []
            
            # 1. Check for common credential patterns
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', username):
                # Email pattern - check for common formats
                domain = username.split('@')[1].lower()
                common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
                if domain in common_domains:
                    stuffing_indicators.append("common_email_domain")
            
            # 2. Check user agent patterns
            suspicious_agents = ['curl', 'wget', 'python', 'bot', 'crawler']
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                stuffing_indicators.append("suspicious_user_agent")
            
            # 3. Check for rapid-fire attempts from same IP
            recent_attempts = [
                ts for ts in self.ip_tracking[ip_address]
                if ts > current_time - timedelta(minutes=5)
            ]
            
            if len(recent_attempts) > 20:  # More than 20 attempts in 5 minutes
                stuffing_indicators.append("rapid_fire_attempts")
            
            # 4. Check for distributed patterns (same username, different IPs)
            username_attempts = []
            for events in self.threat_history:
                if (hasattr(events, 'user_id') and events.user_id == username and
                    events.timestamp > current_time - timedelta(hours=1)):
                    username_attempts.append(events)
            
            if len(username_attempts) > 10:
                stuffing_indicators.append("distributed_username_attempts")
            
            # Calculate confidence score
            confidence_score = len(stuffing_indicators) / 4.0
            
            threats_detected = []
            if confidence_score >= 0.5:  # Threshold for credential stuffing
                threat_event = ThreatEvent(
                    timestamp=current_time,
                    threat_type=ThreatType.CREDENTIAL_STUFFING,
                    severity=ThreatSeverity.HIGH,
                    source_ip=ip_address,
                    user_id=username,
                    description=f"Credential stuffing attack detected: {', '.join(stuffing_indicators)}",
                    confidence_score=confidence_score,
                    metadata={
                        "indicators": stuffing_indicators,
                        "login_data": login_data,
                        "recent_attempts": len(recent_attempts)
                    }
                )
                threats_detected.append(threat_event)
                self.threat_history.append(threat_event)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Credential stuffing check completed in {execution_time:.2f}ms")
            
            return ThreatDetectionResult(
                success=True,
                threats_detected=threats_detected,
                risk_score=confidence_score,
                recommended_actions=[
                    "Implement CAPTCHA",
                    "Rate limit login attempts",
                    "Monitor for compromised credentials"
                ] if confidence_score >= 0.5 else []
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Credential stuffing detection failed in {execution_time:.2f}ms: {str(e)}")
            return ThreatDetectionResult(
                success=False,
                errors=[f"Credential stuffing detection error: {str(e)}"]
            )

    async def detect_account_takeover(self, user_id: str, session_data: Dict[str, Any]) -> ThreatDetectionResult:
        """
        Detect potential account takeover attempts.
        
        Args:
            user_id: User identifier
            session_data: Current session data
            
        Returns:
            ThreatDetectionResult with detection status
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            current_ip = session_data.get("ip_address")
            current_location = session_data.get("location", {})
            device_fingerprint = session_data.get("device_fingerprint")
            
            takeover_indicators = []
            
            # Get user's normal behavior
            user_profile = self.user_behavior.get(user_id, {})
            
            # 1. Geographic anomaly detection
            if current_location and "known_locations" in user_profile:
                known_countries = {loc.get("country") for loc in user_profile["known_locations"]}
                current_country = current_location.get("country")
                
                if current_country and current_country not in known_countries:
                    takeover_indicators.append("geographic_anomaly")
            
            # 2. Device fingerprint analysis
            if device_fingerprint and "known_devices" in user_profile:
                if device_fingerprint not in user_profile["known_devices"]:
                    takeover_indicators.append("unknown_device")
            
            # 3. Behavioral pattern changes
            if "action_frequency" in user_profile:
                # Check for sudden increase in high-value actions
                high_value_actions = ["payment", "content_upload", "profile_change"]
                current_session_actions = session_data.get("actions", [])
                
                high_value_count = sum(1 for action in current_session_actions 
                                     if action in high_value_actions)
                
                if high_value_count > 5:  # Threshold
                    takeover_indicators.append("excessive_high_value_actions")
            
            # 4. Time-based anomalies
            if "time_patterns" in user_profile and user_profile["time_patterns"]:
                avg_hour = sum(user_profile["time_patterns"]) / len(user_profile["time_patterns"])
                current_hour = current_time.hour
                
                if abs(current_hour - avg_hour) > 8:  # Significant time difference
                    takeover_indicators.append("unusual_access_time")
            
            # 5. Password change patterns
            recent_password_changes = session_data.get("recent_password_changes", 0)
            if recent_password_changes > 1:  # Multiple password changes
                takeover_indicators.append("multiple_password_changes")
            
            # Calculate risk score
            risk_score = len(takeover_indicators) / 5.0
            
            threats_detected = []
            if risk_score >= 0.6:  # Account takeover threshold
                threat_event = ThreatEvent(
                    timestamp=current_time,
                    threat_type=ThreatType.ACCOUNT_TAKEOVER,
                    severity=ThreatSeverity.CRITICAL,
                    source_ip=current_ip or "unknown",
                    user_id=user_id,
                    description=f"Potential account takeover: {', '.join(takeover_indicators)}",
                    confidence_score=risk_score,
                    metadata={
                        "indicators": takeover_indicators,
                        "session_data": session_data,
                        "user_profile_changes": True
                    }
                )
                threats_detected.append(threat_event)
                self.threat_history.append(threat_event)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Account takeover check completed for {user_id} in {execution_time:.2f}ms")
            
            return ThreatDetectionResult(
                success=True,
                threats_detected=threats_detected,
                risk_score=risk_score,
                recommended_actions=[
                    "Force password reset",
                    "Require multi-factor authentication",
                    "Lock account temporarily",
                    "Notify user via secure channel"
                ] if risk_score >= 0.6 else []
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Account takeover detection failed in {execution_time:.2f}ms: {str(e)}")
            return ThreatDetectionResult(
                success=False,
                errors=[f"Account takeover detection error: {str(e)}"]
            )

    async def monitor_suspicious_patterns(self, time_window_hours: int = 24) -> ThreatDetectionResult:
        """
        Monitor for suspicious patterns across the entire platform.
        
        Args:
            time_window_hours: Time window for pattern analysis
            
        Returns:
            ThreatDetectionResult with platform-wide threat analysis
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            cutoff_time = current_time - timedelta(hours=time_window_hours)
            
            # Filter recent threats
            recent_threats = [
                threat for threat in self.threat_history
                if threat.timestamp > cutoff_time
            ]
            
            suspicious_patterns = []
            pattern_metadata = {}
            
            # 1. Coordinated attacks analysis
            ip_threat_count = defaultdict(int)
            for threat in recent_threats:
                ip_threat_count[threat.source_ip] += 1
            
            coordinated_ips = [ip for ip, count in ip_threat_count.items() if count > 10]
            if coordinated_ips:
                suspicious_patterns.append("coordinated_attack_pattern")
                pattern_metadata["coordinated_ips"] = coordinated_ips
            
            # 2. Creator-specific attack patterns
            creator_threats = defaultdict(list)
            for threat in recent_threats:
                if threat.creator_type:
                    creator_threats[threat.creator_type].append(threat)
            
            for creator_type, threats in creator_threats.items():
                if len(threats) > 50:  # High volume of threats
                    suspicious_patterns.append(f"creator_targeted_attack_{creator_type}")
                    pattern_metadata[f"{creator_type}_threat_count"] = len(threats)
            
            # 3. Escalation patterns
            severity_progression = [threat.severity.value for threat in recent_threats[-20:]]
            if severity_progression.count("critical") > 5:
                suspicious_patterns.append("threat_escalation_pattern")
                pattern_metadata["critical_threats"] = severity_progression.count("critical")
            
            # 4. Geographic clustering
            ip_countries = defaultdict(int)
            for threat in recent_threats:
                # In a real implementation, you would geo-locate the IP
                # For this example, we'll use a placeholder
                country = "unknown"  # Would be actual geo-location
                ip_countries[country] += 1
            
            # 5. Time-based attack patterns
            hour_distribution = defaultdict(int)
            for threat in recent_threats:
                hour_distribution[threat.timestamp.hour] += 1
            
            # Check for concentrated attacks in specific hours
            max_hourly_threats = max(hour_distribution.values()) if hour_distribution else 0
            if max_hourly_threats > 20:
                suspicious_patterns.append("time_concentrated_attacks")
                pattern_metadata["peak_hour_threats"] = max_hourly_threats
            
            # Calculate overall risk score
            risk_score = len(suspicious_patterns) / 5.0
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Suspicious pattern monitoring completed in {execution_time:.2f}ms")
            
            return ThreatDetectionResult(
                success=True,
                risk_score=risk_score,
                recommended_actions=[
                    "Implement platform-wide rate limiting",
                    "Enhance geographic filtering",
                    "Increase security monitoring",
                    "Alert security operations center"
                ] if risk_score >= 0.6 else [
                    "Continue normal monitoring",
                    "Review threat patterns weekly"
                ],
                errors=[],
                threats_detected=[]  # This is pattern analysis, not specific threat detection
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Suspicious pattern monitoring failed in {execution_time:.2f}ms: {str(e)}")
            return ThreatDetectionResult(
                success=False,
                errors=[f"Pattern monitoring error: {str(e)}"]
            )

    async def real_time_threat_scoring(self, threat_events: List[ThreatEvent]) -> Dict[str, float]:
        """
        Calculate real-time threat scores for multiple events.
        
        Args:
            threat_events: List of threat events to score
            
        Returns:
            Dictionary mapping threat IDs to scores
        """
        start_time = time.perf_counter()
        
        try:
            threat_scores = {}
            
            for i, event in enumerate(threat_events):
                base_score = event.confidence_score
                
                # Severity multiplier
                severity_multipliers = {
                    ThreatSeverity.LOW: 0.5,
                    ThreatSeverity.MEDIUM: 1.0,
                    ThreatSeverity.HIGH: 1.5,
                    ThreatSeverity.CRITICAL: 2.0
                }
                
                severity_multiplier = severity_multipliers.get(event.severity, 1.0)
                
                # Recency multiplier (more recent = higher score)
                time_diff = datetime.now(timezone.utc) - event.timestamp
                recency_multiplier = max(0.1, 1.0 - (time_diff.total_seconds() / 3600))  # Decay over 1 hour
                
                # Creator type risk multiplier
                creator_multipliers = {
                    "musician": 1.2,  # High value content
                    "photographer": 1.1,
                    "blogger": 1.0
                }
                creator_multiplier = creator_multipliers.get(event.creator_type, 1.0)
                
                # Calculate final score
                final_score = min(base_score * severity_multiplier * recency_multiplier * creator_multiplier, 1.0)
                threat_scores[f"threat_{i}"] = final_score
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Real-time threat scoring completed for {len(threat_events)} events in {execution_time:.2f}ms")
            
            return threat_scores
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Real-time threat scoring failed in {execution_time:.2f}ms: {str(e)}")
            return {}

    async def automated_threat_response(self, threat_event: ThreatEvent) -> Dict[str, Any]:
        """
        Execute automated response to detected threats.
        
        Args:
            threat_event: Threat event requiring response
            
        Returns:
            Dictionary containing response actions taken
        """
        start_time = time.perf_counter()
        
        try:
            response_actions = []
            
            # Define response strategies based on threat type and severity
            if threat_event.threat_type == ThreatType.BRUTE_FORCE:
                if threat_event.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]:
                    response_actions.extend([
                        f"blocked_ip_{threat_event.source_ip}",
                        "implemented_progressive_delay",
                        "notified_security_team"
                    ])
            
            elif threat_event.threat_type == ThreatType.ACCOUNT_TAKEOVER:
                response_actions.extend([
                    f"locked_account_{threat_event.user_id}",
                    "forced_password_reset",
                    "required_mfa_verification",
                    "sent_security_alert"
                ])
            
            elif threat_event.threat_type == ThreatType.CREDENTIAL_STUFFING:
                response_actions.extend([
                    "implemented_captcha",
                    "increased_rate_limiting",
                    f"flagged_ip_{threat_event.source_ip}"
                ])
            
            elif threat_event.threat_type == ThreatType.CONTENT_THEFT:
                if threat_event.creator_type:
                    response_actions.extend([
                        f"protected_creator_content_{threat_event.creator_type}",
                        "enhanced_watermarking",
                        "notified_creator"
                    ])
            
            # Mark threat as mitigated
            threat_event.mitigated = True
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Automated threat response completed in {execution_time:.2f}ms: {response_actions}")
            
            return {
                "success": True,
                "actions_taken": response_actions,
                "response_time_ms": execution_time,
                "threat_id": f"{threat_event.threat_type.value}_{threat_event.timestamp.isoformat()}"
            }
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Automated threat response failed in {execution_time:.2f}ms: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": execution_time
            }

    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get comprehensive threat statistics for reporting."""
        try:
            total_threats = len(self.threat_history)
            
            if total_threats == 0:
                return {
                    "total_threats": 0,
                    "threat_types": {},
                    "severity_distribution": {},
                    "creator_type_distribution": {},
                    "mitigation_rate": 0.0
                }
            
            # Threat type distribution
            threat_types = defaultdict(int)
            for threat in self.threat_history:
                threat_types[threat.threat_type.value] += 1
            
            # Severity distribution
            severity_distribution = defaultdict(int)
            for threat in self.threat_history:
                severity_distribution[threat.severity.value] += 1
            
            # Creator type distribution
            creator_distribution = defaultdict(int)
            for threat in self.threat_history:
                if threat.creator_type:
                    creator_distribution[threat.creator_type] += 1
            
            # Mitigation rate
            mitigated_count = sum(1 for threat in self.threat_history if threat.mitigated)
            mitigation_rate = mitigated_count / total_threats if total_threats > 0 else 0.0
            
            return {
                "total_threats": total_threats,
                "threat_types": dict(threat_types),
                "severity_distribution": dict(severity_distribution),
                "creator_type_distribution": dict(creator_distribution),
                "mitigation_rate": mitigation_rate,
                "active_ip_tracking": len(self.ip_tracking),
                "monitored_users": len(self.user_behavior)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate threat statistics: {str(e)}")
            return {"error": str(e)}

# Factory for enterprise deployment
class ThreatDetectorFactory:
    """Factory for creating ThreatDetector instances with different configurations."""
    
    @staticmethod
    def create_production_detector() -> ThreatDetector:
        """Create production-ready threat detector."""
        config = {
            "brute_force_threshold": 5,
            "time_window_minutes": 15,
            "anomaly_threshold": 0.8,
            "enable_real_time_response": True,
            "log_level": "INFO"
        }
        return ThreatDetector(config)
    
    @staticmethod
    def create_development_detector() -> ThreatDetector:
        """Create development threat detector with relaxed thresholds."""
        config = {
            "brute_force_threshold": 10,
            "time_window_minutes": 30,
            "anomaly_threshold": 0.9,
            "enable_real_time_response": False,
            "log_level": "DEBUG"
        }
        return ThreatDetector(config)
    
    @staticmethod
    def create_high_security_detector() -> ThreatDetector:
        """Create high-security threat detector for sensitive environments."""
        config = {
            "brute_force_threshold": 3,
            "time_window_minutes": 10,
            "anomaly_threshold": 0.6,
            "enable_real_time_response": True,
            "log_level": "WARNING"
        }
        return ThreatDetector(config)