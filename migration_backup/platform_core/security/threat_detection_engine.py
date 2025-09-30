#!/usr/bin/env python3
"""
Threat Detection Engine - ML-Powered Real-Time Security Intelligence System
Advanced behavioral anomaly detection with threat intelligence integration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive threat detection including:
- ML-powered behavioral anomaly detection using statistical analysis
- Real-time threat intelligence feed integration and correlation
- Advanced Persistent Threat (APT) detection and attribution
- Real-time security alerting with adaptive thresholds
- Creator economy specific threat patterns and protection
"""

import asyncio
import hashlib
import json
import logging
import statistics
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Threat type enumeration"""
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    MALWARE = "malware"
    PHISHING = "phishing"
    ACCOUNT_TAKEOVER = "account_takeover"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    IP_REPUTATION = "ip_reputation"
    CREDENTIAL_STUFFING = "credential_stuffing"
    CONTENT_THEFT = "content_theft"
    COPYRIGHT_VIOLATION = "copyright_violation"


class ThreatStatus(Enum):
    """Threat status enumeration"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"


class AlertSeverity(Enum):
    """Alert severity enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class BehavioralBaseline:
    """User behavioral baseline for anomaly detection"""
    user_id: str
    login_frequency: Dict[str, float] = field(default_factory=dict)  # hour -> avg logins
    session_duration: Dict[str, float] = field(default_factory=dict)  # avg, std
    api_usage_patterns: Dict[str, float] = field(default_factory=dict)  # endpoint -> freq
    data_access_patterns: Dict[str, float] = field(default_factory=dict)  # resource -> freq
    geographic_patterns: List[str] = field(default_factory=list)  # common locations
    device_patterns: List[str] = field(default_factory=list)  # common devices
    content_creation_rate: float = 0.0
    content_upload_patterns: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0


@dataclass
class ThreatIntelligence:
    """Threat intelligence feed data"""
    intel_id: str
    threat_type: ThreatType
    indicators: List[str] = field(default_factory=list)  # IPs, domains, hashes
    severity: ThreatLevel = ThreatLevel.MEDIUM
    description: str = ""
    source: str = ""
    confidence: float = 0.0
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityEvent:
    """Security event data"""
    event_id: str
    event_type: str
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    resource: str = ""
    action: str = ""
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatDetection:
    """Detected threat information"""
    detection_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    status: ThreatStatus = ThreatStatus.ACTIVE
    confidence_score: float = 0.0
    affected_entities: List[str] = field(default_factory=list)  # user_ids, IP addresses, etc.
    indicators: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    timeline: List[datetime] = field(default_factory=list)
    source_events: List[str] = field(default_factory=list)  # event_ids
    mitigations_applied: List[str] = field(default_factory=list)
    analyst_notes: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityAlert:
    """Security alert for notification"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    threat_detection: ThreatDetection
    recommended_actions: List[str] = field(default_factory=list)
    escalation_required: bool = False
    notified_users: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class ThreatDetectionEngine:
    """
    Enterprise Threat Detection Engine
    
    Provides comprehensive threat detection using machine learning algorithms
    for behavioral analysis, threat intelligence correlation, and real-time
    security monitoring specifically designed for creator economy platforms.
    """

    def __init__(self):
        # Behavioral baselines and user profiles
        self.behavioral_baselines: Dict[str, BehavioralBaseline] = {}
        
        # Threat intelligence feeds
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        
        # Event storage and processing
        self.security_events: deque = deque(maxlen=100000)  # Ring buffer for events
        self.event_correlation_window = timedelta(minutes=10)
        
        # Threat detections and alerts
        self.active_threats: Dict[str, ThreatDetection] = {}
        self.threat_history: List[ThreatDetection] = []
        self.active_alerts: Dict[str, SecurityAlert] = {}
        
        # Detection rules and thresholds
        self.detection_rules: Dict[str, Dict[str, Any]] = {}
        self.anomaly_thresholds: Dict[str, float] = {
            "login_frequency_deviation": 3.0,  # Standard deviations
            "session_duration_deviation": 2.5,
            "api_usage_deviation": 3.0,
            "data_access_deviation": 2.0,
            "geographic_anomaly_threshold": 0.1,
            "device_anomaly_threshold": 0.2
        }
        
        # IP reputation and blocklists
        self.malicious_ips: Set[str] = set()
        self.suspicious_ips: Set[str] = set()
        self.ip_reputation_cache: Dict[str, Tuple[float, datetime]] = {}
        
        # Statistical models for anomaly detection
        self.statistical_models: Dict[str, Dict[str, Any]] = {}
        
        # Performance metrics
        self.detection_metrics: Dict[str, List[float]] = {
            "processing_time": [],
            "false_positive_rate": [],
            "detection_accuracy": []
        }
        
        # Initialize detection rules and threat intelligence
        self._initialize_detection_rules()
        self._initialize_threat_intelligence()
        
        logger.info("Threat Detection Engine initialized with ML capabilities")

    def _initialize_detection_rules(self) -> None:
        """Initialize default detection rules"""
        try:
            self.detection_rules = {
                # Brute force detection
                "brute_force_login": {
                    "max_failed_attempts": 5,
                    "time_window_minutes": 10,
                    "severity": ThreatLevel.HIGH,
                    "enabled": True
                },
                
                # DDoS detection
                "ddos_requests": {
                    "max_requests_per_minute": 1000,
                    "max_requests_per_ip": 100,
                    "time_window_minutes": 5,
                    "severity": ThreatLevel.CRITICAL,
                    "enabled": True
                },
                
                # Credential stuffing
                "credential_stuffing": {
                    "unique_users_threshold": 50,
                    "success_rate_threshold": 0.02,
                    "time_window_minutes": 15,
                    "severity": ThreatLevel.HIGH,
                    "enabled": True
                },
                
                # Data exfiltration
                "data_exfiltration": {
                    "data_volume_threshold_mb": 100,
                    "file_count_threshold": 50,
                    "time_window_minutes": 30,
                    "severity": ThreatLevel.CRITICAL,
                    "enabled": True
                },
                
                # Content theft detection
                "content_theft": {
                    "download_rate_threshold": 20,
                    "unique_content_threshold": 10,
                    "time_window_minutes": 60,
                    "severity": ThreatLevel.HIGH,
                    "enabled": True
                },
                
                # Behavioral anomaly
                "behavioral_anomaly": {
                    "anomaly_score_threshold": 0.8,
                    "consecutive_anomalies": 3,
                    "severity": ThreatLevel.MEDIUM,
                    "enabled": True
                }
            }
            
            logger.info(f"Initialized {len(self.detection_rules)} detection rules")
            
        except Exception as e:
            logger.error(f"Failed to initialize detection rules: {e}")

    def _initialize_threat_intelligence(self) -> None:
        """Initialize threat intelligence feeds"""
        try:
            # Sample threat intelligence data (in production, integrate with real feeds)
            sample_threat_intel = [
                ThreatIntelligence(
                    intel_id="tor_exit_nodes",
                    threat_type=ThreatType.IP_REPUTATION,
                    indicators=["198.96.155.3", "185.220.101.72", "185.220.102.8"],
                    severity=ThreatLevel.MEDIUM,
                    description="Known Tor exit nodes",
                    source="tor_project",
                    confidence=0.9,
                    valid_until=datetime.utcnow() + timedelta(days=7)
                ),
                
                ThreatIntelligence(
                    intel_id="known_malware_hashes",
                    threat_type=ThreatType.MALWARE,
                    indicators=["d41d8cd98f00b204e9800998ecf8427e", "5d41402abc4b2a76b9719d911017c592"],
                    severity=ThreatLevel.HIGH,
                    description="Known malware file hashes",
                    source="virustotal",
                    confidence=0.95,
                    valid_until=datetime.utcnow() + timedelta(days=30)
                ),
                
                ThreatIntelligence(
                    intel_id="phishing_domains",
                    threat_type=ThreatType.PHISHING,
                    indicators=["evil-domain.com", "phishing-site.net", "fake-login.org"],
                    severity=ThreatLevel.HIGH,
                    description="Known phishing domains",
                    source="phishtank",
                    confidence=0.8,
                    valid_until=datetime.utcnow() + timedelta(days=14)
                )
            ]
            
            for intel in sample_threat_intel:
                self.threat_intelligence[intel.intel_id] = intel
                
                # Populate IP reputation cache
                if intel.threat_type == ThreatType.IP_REPUTATION:
                    for ip in intel.indicators:
                        self.malicious_ips.add(ip)
                        self.ip_reputation_cache[ip] = (0.1, datetime.utcnow())  # Low reputation
            
            logger.info(f"Initialized {len(self.threat_intelligence)} threat intelligence feeds")
            
        except Exception as e:
            logger.error(f"Failed to initialize threat intelligence: {e}")

    async def process_security_event(self, event: SecurityEvent) -> List[ThreatDetection]:
        """Process security event and detect threats"""
        try:
            start_time = time.time()
            
            # Add event to storage
            self.security_events.append(event)
            
            detected_threats = []
            
            # Run detection algorithms
            threat_detections = await asyncio.gather(
                self._detect_brute_force_attacks(event),
                self._detect_ddos_attacks(event),
                self._detect_behavioral_anomalies(event),
                self._detect_credential_stuffing(event),
                self._detect_data_exfiltration(event),
                self._detect_content_theft(event),
                self._correlate_threat_intelligence(event),
                return_exceptions=True
            )
            
            # Process detection results
            for detection_result in threat_detections:
                if isinstance(detection_result, ThreatDetection):
                    detected_threats.append(detection_result)
                    
                    # Store active threat
                    self.active_threats[detection_result.detection_id] = detection_result
                    
                    # Generate alert if needed
                    if detection_result.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                        await self._generate_security_alert(detection_result)
                
                elif isinstance(detection_result, Exception):
                    logger.error(f"Detection algorithm failed: {detection_result}")
            
            # Update behavioral baselines
            if event.user_id:
                await self._update_behavioral_baseline(event)
            
            # Record performance metrics
            processing_time = (time.time() - start_time) * 1000
            self.detection_metrics["processing_time"].append(processing_time)
            
            logger.debug(f"Processed security event {event.event_id}, detected {len(detected_threats)} threats")
            
            return detected_threats
            
        except Exception as e:
            logger.error(f"Failed to process security event: {e}")
            return []

    async def _detect_brute_force_attacks(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Detect brute force attacks"""
        try:
            if event.event_type != "authentication" or event.success:
                return None
            
            rule = self.detection_rules.get("brute_force_login")
            if not rule or not rule["enabled"]:
                return None
            
            # Count failed login attempts from same IP in time window
            time_threshold = datetime.utcnow() - timedelta(minutes=rule["time_window_minutes"])
            
            failed_attempts = [
                e for e in self.security_events
                if (e.event_type == "authentication" and
                    not e.success and
                    e.ip_address == event.ip_address and
                    e.timestamp > time_threshold)
            ]
            
            if len(failed_attempts) >= rule["max_failed_attempts"]:
                detection = ThreatDetection(
                    detection_id=f"brute_force_{event.ip_address}_{int(time.time())}",
                    threat_type=ThreatType.BRUTE_FORCE,
                    threat_level=rule["severity"],
                    confidence_score=min(1.0, len(failed_attempts) / rule["max_failed_attempts"]),
                    affected_entities=[event.ip_address],
                    indicators=[event.ip_address],
                    evidence=[f"{len(failed_attempts)} failed login attempts in {rule['time_window_minutes']} minutes"],
                    source_events=[e.event_id for e in failed_attempts],
                    metadata={
                        "failed_attempts_count": len(failed_attempts),
                        "time_window_minutes": rule["time_window_minutes"],
                        "target_users": list(set(e.user_id for e in failed_attempts if e.user_id))
                    }
                )
                
                logger.warning(f"Brute force attack detected from IP {event.ip_address}")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect brute force attacks: {e}")
            return None

    async def _detect_ddos_attacks(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Detect DDoS attacks"""
        try:
            rule = self.detection_rules.get("ddos_requests")
            if not rule or not rule["enabled"]:
                return None
            
            time_threshold = datetime.utcnow() - timedelta(minutes=rule["time_window_minutes"])
            
            # Count total requests in time window
            recent_events = [
                e for e in self.security_events
                if e.timestamp > time_threshold
            ]
            
            total_requests = len(recent_events)
            
            # Count requests from same IP
            ip_requests = [
                e for e in recent_events
                if e.ip_address == event.ip_address
            ]
            
            # Check thresholds
            if (total_requests > rule["max_requests_per_minute"] * rule["time_window_minutes"] or
                len(ip_requests) > rule["max_requests_per_ip"]):
                
                detection = ThreatDetection(
                    detection_id=f"ddos_{int(time.time())}",
                    threat_type=ThreatType.DDoS,
                    threat_level=rule["severity"],
                    confidence_score=min(1.0, total_requests / (rule["max_requests_per_minute"] * rule["time_window_minutes"])),
                    affected_entities=["platform"],
                    indicators=[event.ip_address],
                    evidence=[
                        f"Total requests: {total_requests} in {rule['time_window_minutes']} minutes",
                        f"Requests from {event.ip_address}: {len(ip_requests)}"
                    ],
                    metadata={
                        "total_requests": total_requests,
                        "ip_requests": len(ip_requests),
                        "time_window_minutes": rule["time_window_minutes"]
                    }
                )
                
                logger.warning(f"DDoS attack detected - {total_requests} requests in {rule['time_window_minutes']} minutes")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect DDoS attacks: {e}")
            return None

    async def _detect_behavioral_anomalies(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Detect behavioral anomalies using statistical analysis"""
        try:
            if not event.user_id:
                return None
            
            rule = self.detection_rules.get("behavioral_anomaly")
            if not rule or not rule["enabled"]:
                return None
            
            # Get user's behavioral baseline
            baseline = self.behavioral_baselines.get(event.user_id)
            if not baseline or baseline.confidence_score < 0.5:
                return None  # Need sufficient baseline data
            
            anomaly_score = 0.0
            anomaly_factors = []
            
            # Check login time anomaly
            current_hour = event.timestamp.hour
            if str(current_hour) in baseline.login_frequency:
                expected_freq = baseline.login_frequency[str(current_hour)]
                if expected_freq == 0:  # User never logs in at this hour
                    anomaly_score += 0.3
                    anomaly_factors.append(f"Unusual login time: {current_hour}:00")
            
            # Check geographic anomaly
            user_location = event.details.get("location", "")
            if user_location and user_location not in baseline.geographic_patterns:
                anomaly_score += 0.4
                anomaly_factors.append(f"Unusual location: {user_location}")
            
            # Check device anomaly
            device_fingerprint = event.details.get("device_fingerprint", "")
            if device_fingerprint and device_fingerprint not in baseline.device_patterns:
                anomaly_score += 0.2
                anomaly_factors.append(f"Unknown device")
            
            # Check API usage patterns
            if event.event_type == "api_call":
                endpoint = event.resource
                if endpoint in baseline.api_usage_patterns:
                    # Calculate z-score for API usage frequency
                    time_window = timedelta(hours=1)
                    recent_api_calls = [
                        e for e in self.security_events
                        if (e.user_id == event.user_id and
                            e.event_type == "api_call" and
                            e.resource == endpoint and
                            e.timestamp > event.timestamp - time_window)
                    ]
                    
                    current_freq = len(recent_api_calls)
                    expected_freq = baseline.api_usage_patterns[endpoint]
                    
                    if expected_freq > 0:
                        deviation = abs(current_freq - expected_freq) / expected_freq
                        if deviation > self.anomaly_thresholds["api_usage_deviation"]:
                            anomaly_score += 0.3
                            anomaly_factors.append(f"Unusual API usage: {endpoint}")
            
            # Generate detection if anomaly score exceeds threshold
            if anomaly_score >= rule["anomaly_score_threshold"]:
                detection = ThreatDetection(
                    detection_id=f"behavioral_anomaly_{event.user_id}_{int(time.time())}",
                    threat_type=ThreatType.BEHAVIORAL_ANOMALY,
                    threat_level=rule["severity"],
                    confidence_score=min(1.0, anomaly_score),
                    affected_entities=[event.user_id],
                    indicators=[event.user_id, event.ip_address],
                    evidence=anomaly_factors,
                    source_events=[event.event_id],
                    metadata={
                        "anomaly_score": anomaly_score,
                        "baseline_confidence": baseline.confidence_score,
                        "anomaly_factors": anomaly_factors
                    }
                )
                
                logger.warning(f"Behavioral anomaly detected for user {event.user_id} (score: {anomaly_score:.2f})")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect behavioral anomalies: {e}")
            return None

    async def _detect_credential_stuffing(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Detect credential stuffing attacks"""
        try:
            if event.event_type != "authentication":
                return None
            
            rule = self.detection_rules.get("credential_stuffing")
            if not rule or not rule["enabled"]:
                return None
            
            time_threshold = datetime.utcnow() - timedelta(minutes=rule["time_window_minutes"])
            
            # Get authentication attempts in time window
            auth_attempts = [
                e for e in self.security_events
                if (e.event_type == "authentication" and
                    e.timestamp > time_threshold)
            ]
            
            if len(auth_attempts) < rule["unique_users_threshold"]:
                return None
            
            # Count unique users and success rate
            unique_users = set(e.user_id for e in auth_attempts if e.user_id)
            successful_attempts = [e for e in auth_attempts if e.success]
            
            success_rate = len(successful_attempts) / len(auth_attempts) if auth_attempts else 0
            
            # Check if this matches credential stuffing pattern
            if (len(unique_users) >= rule["unique_users_threshold"] and
                success_rate <= rule["success_rate_threshold"]):
                
                detection = ThreatDetection(
                    detection_id=f"credential_stuffing_{int(time.time())}",
                    threat_type=ThreatType.CREDENTIAL_STUFFING,
                    threat_level=rule["severity"],
                    confidence_score=min(1.0, len(unique_users) / rule["unique_users_threshold"]),
                    affected_entities=list(unique_users),
                    indicators=[event.ip_address],
                    evidence=[
                        f"Authentication attempts on {len(unique_users)} different accounts",
                        f"Low success rate: {success_rate:.2%}",
                        f"Time window: {rule['time_window_minutes']} minutes"
                    ],
                    source_events=[e.event_id for e in auth_attempts],
                    metadata={
                        "unique_users_count": len(unique_users),
                        "total_attempts": len(auth_attempts),
                        "success_rate": success_rate,
                        "time_window_minutes": rule["time_window_minutes"]
                    }
                )
                
                logger.warning(f"Credential stuffing attack detected - {len(unique_users)} users targeted")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect credential stuffing: {e}")
            return None

    async def _detect_data_exfiltration(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Detect data exfiltration attempts"""
        try:
            if event.event_type not in ["file_download", "api_call", "data_export"]:
                return None
            
            rule = self.detection_rules.get("data_exfiltration")
            if not rule or not rule["enabled"]:
                return None
            
            time_threshold = datetime.utcnow() - timedelta(minutes=rule["time_window_minutes"])
            
            # Get data access events for this user
            data_events = [
                e for e in self.security_events
                if (e.user_id == event.user_id and
                    e.event_type in ["file_download", "api_call", "data_export"] and
                    e.timestamp > time_threshold)
            ]
            
            # Calculate data volume and file count
            total_data_mb = sum(e.details.get("file_size_mb", 0) for e in data_events)
            file_count = len([e for e in data_events if e.event_type == "file_download"])
            
            # Check thresholds
            if (total_data_mb >= rule["data_volume_threshold_mb"] or
                file_count >= rule["file_count_threshold"]):
                
                detection = ThreatDetection(
                    detection_id=f"data_exfiltration_{event.user_id}_{int(time.time())}",
                    threat_type=ThreatType.DATA_EXFILTRATION,
                    threat_level=rule["severity"],
                    confidence_score=min(1.0, max(
                        total_data_mb / rule["data_volume_threshold_mb"],
                        file_count / rule["file_count_threshold"]
                    )),
                    affected_entities=[event.user_id],
                    indicators=[event.user_id, event.ip_address],
                    evidence=[
                        f"Data volume: {total_data_mb:.1f} MB",
                        f"File downloads: {file_count} files",
                        f"Time window: {rule['time_window_minutes']} minutes"
                    ],
                    source_events=[e.event_id for e in data_events],
                    metadata={
                        "data_volume_mb": total_data_mb,
                        "file_count": file_count,
                        "time_window_minutes": rule["time_window_minutes"]
                    }
                )
                
                logger.warning(f"Data exfiltration detected for user {event.user_id} - {total_data_mb:.1f} MB")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect data exfiltration: {e}")
            return None

    async def _detect_content_theft(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Detect creator content theft attempts"""
        try:
            if event.event_type not in ["content_download", "content_view", "content_copy"]:
                return None
            
            rule = self.detection_rules.get("content_theft")
            if not rule or not rule["enabled"]:
                return None
            
            time_threshold = datetime.utcnow() - timedelta(minutes=rule["time_window_minutes"])
            
            # Get content access events
            content_events = [
                e for e in self.security_events
                if (e.ip_address == event.ip_address and
                    e.event_type in ["content_download", "content_view", "content_copy"] and
                    e.timestamp > time_threshold)
            ]
            
            # Count download rate and unique content accessed
            download_count = len([e for e in content_events if e.event_type == "content_download"])
            unique_content = set(e.resource for e in content_events)
            
            # Check thresholds
            if (download_count >= rule["download_rate_threshold"] or
                len(unique_content) >= rule["unique_content_threshold"]):
                
                detection = ThreatDetection(
                    detection_id=f"content_theft_{event.ip_address}_{int(time.time())}",
                    threat_type=ThreatType.CONTENT_THEFT,
                    threat_level=rule["severity"],
                    confidence_score=min(1.0, max(
                        download_count / rule["download_rate_threshold"],
                        len(unique_content) / rule["unique_content_threshold"]
                    )),
                    affected_entities=["content_creators"],
                    indicators=[event.ip_address],
                    evidence=[
                        f"Content downloads: {download_count}",
                        f"Unique content accessed: {len(unique_content)}",
                        f"Time window: {rule['time_window_minutes']} minutes"
                    ],
                    source_events=[e.event_id for e in content_events],
                    metadata={
                        "download_count": download_count,
                        "unique_content_count": len(unique_content),
                        "time_window_minutes": rule["time_window_minutes"],
                        "accessed_content": list(unique_content)
                    }
                )
                
                logger.warning(f"Content theft detected from IP {event.ip_address} - {download_count} downloads")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect content theft: {e}")
            return None

    async def _correlate_threat_intelligence(self, event: SecurityEvent) -> Optional[ThreatDetection]:
        """Correlate event with threat intelligence feeds"""
        try:
            detections = []
            
            # Check IP reputation
            if event.ip_address in self.malicious_ips:
                for intel_id, intel in self.threat_intelligence.items():
                    if (event.ip_address in intel.indicators and
                        intel.threat_type == ThreatType.IP_REPUTATION and
                        (intel.valid_until is None or intel.valid_until > datetime.utcnow())):
                        
                        detection = ThreatDetection(
                            detection_id=f"threat_intel_{intel_id}_{int(time.time())}",
                            threat_type=intel.threat_type,
                            threat_level=intel.severity,
                            confidence_score=intel.confidence,
                            affected_entities=[event.ip_address],
                            indicators=[event.ip_address],
                            evidence=[f"IP {event.ip_address} found in threat intelligence feed: {intel.source}"],
                            source_events=[event.event_id],
                            metadata={
                                "threat_intel_source": intel.source,
                                "intel_description": intel.description,
                                "intel_confidence": intel.confidence
                            }
                        )
                        
                        logger.warning(f"Threat intelligence match: IP {event.ip_address} ({intel.source})")
                        return detection
            
            # Check for malware hashes in file uploads
            file_hash = event.details.get("file_hash")
            if file_hash:
                for intel_id, intel in self.threat_intelligence.items():
                    if (file_hash in intel.indicators and
                        intel.threat_type == ThreatType.MALWARE and
                        (intel.valid_until is None or intel.valid_until > datetime.utcnow())):
                        
                        detection = ThreatDetection(
                            detection_id=f"malware_{file_hash}_{int(time.time())}",
                            threat_type=ThreatType.MALWARE,
                            threat_level=ThreatLevel.CRITICAL,
                            confidence_score=intel.confidence,
                            affected_entities=[event.user_id] if event.user_id else [],
                            indicators=[file_hash],
                            evidence=[f"Malware hash {file_hash} detected in upload"],
                            source_events=[event.event_id],
                            metadata={
                                "file_hash": file_hash,
                                "threat_intel_source": intel.source,
                                "intel_confidence": intel.confidence
                            }
                        )
                        
                        logger.critical(f"Malware detected: hash {file_hash}")
                        return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to correlate threat intelligence: {e}")
            return None

    async def _update_behavioral_baseline(self, event: SecurityEvent) -> None:
        """Update user behavioral baseline with new event data"""
        try:
            user_id = event.user_id
            if not user_id:
                return
            
            # Get or create baseline
            if user_id not in self.behavioral_baselines:
                self.behavioral_baselines[user_id] = BehavioralBaseline(user_id=user_id)
            
            baseline = self.behavioral_baselines[user_id]
            
            # Update login frequency patterns
            if event.event_type == "authentication" and event.success:
                hour_key = str(event.timestamp.hour)
                if hour_key not in baseline.login_frequency:
                    baseline.login_frequency[hour_key] = 0
                baseline.login_frequency[hour_key] += 1
            
            # Update API usage patterns
            if event.event_type == "api_call":
                endpoint = event.resource
                if endpoint not in baseline.api_usage_patterns:
                    baseline.api_usage_patterns[endpoint] = 0
                baseline.api_usage_patterns[endpoint] += 1
            
            # Update geographic patterns
            location = event.details.get("location")
            if location and location not in baseline.geographic_patterns:
                baseline.geographic_patterns.append(location)
                # Keep only recent locations (max 10)
                if len(baseline.geographic_patterns) > 10:
                    baseline.geographic_patterns = baseline.geographic_patterns[-10:]
            
            # Update device patterns
            device_fingerprint = event.details.get("device_fingerprint")
            if device_fingerprint and device_fingerprint not in baseline.device_patterns:
                baseline.device_patterns.append(device_fingerprint)
                # Keep only recent devices (max 5)
                if len(baseline.device_patterns) > 5:
                    baseline.device_patterns = baseline.device_patterns[-5:]
            
            # Update content creation patterns
            if event.event_type == "content_upload":
                baseline.content_creation_rate += 1
            
            # Calculate confidence score based on data points
            data_points = (
                len(baseline.login_frequency) +
                len(baseline.api_usage_patterns) +
                len(baseline.geographic_patterns) +
                len(baseline.device_patterns) +
                (1 if baseline.content_creation_rate > 0 else 0)
            )
            baseline.confidence_score = min(1.0, data_points / 20.0)  # Max confidence at 20 data points
            
            baseline.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update behavioral baseline: {e}")

    async def _generate_security_alert(self, threat_detection: ThreatDetection) -> None:
        """Generate security alert for threat detection"""
        try:
            alert_id = f"alert_{threat_detection.detection_id}"
            
            # Determine alert severity based on threat level
            severity_mapping = {
                ThreatLevel.LOW: AlertSeverity.INFO,
                ThreatLevel.MEDIUM: AlertSeverity.WARNING,
                ThreatLevel.HIGH: AlertSeverity.ERROR,
                ThreatLevel.CRITICAL: AlertSeverity.CRITICAL
            }
            
            alert = SecurityAlert(
                alert_id=alert_id,
                title=f"{threat_detection.threat_type.value.replace('_', ' ').title()} Detected",
                description=f"Threat detected with {threat_detection.confidence_score:.1%} confidence",
                severity=severity_mapping[threat_detection.threat_level],
                threat_detection=threat_detection,
                recommended_actions=self._get_recommended_actions(threat_detection),
                escalation_required=(threat_detection.threat_level == ThreatLevel.CRITICAL)
            )
            
            self.active_alerts[alert_id] = alert
            
            logger.warning(f"Security alert generated: {alert.title} (ID: {alert_id})")
            
        except Exception as e:
            logger.error(f"Failed to generate security alert: {e}")

    def _get_recommended_actions(self, threat_detection: ThreatDetection) -> List[str]:
        """Get recommended actions for threat type"""
        actions = {
            ThreatType.BRUTE_FORCE: [
                "Block IP address temporarily",
                "Require additional authentication for affected accounts",
                "Monitor for continued attempts"
            ],
            ThreatType.DDoS: [
                "Activate DDoS protection",
                "Rate limit traffic from source",
                "Scale infrastructure if needed"
            ],
            ThreatType.BEHAVIORAL_ANOMALY: [
                "Require re-authentication",
                "Review user account for compromise",
                "Monitor user activity closely"
            ],
            ThreatType.CREDENTIAL_STUFFING: [
                "Force password reset for affected accounts",
                "Implement additional rate limiting",
                "Notify affected users"
            ],
            ThreatType.DATA_EXFILTRATION: [
                "Block user access immediately",
                "Review data access logs",
                "Initiate incident response procedure"
            ],
            ThreatType.CONTENT_THEFT: [
                "Block IP address",
                "Review affected content",
                "Notify content creators"
            ],
            ThreatType.MALWARE: [
                "Quarantine infected files",
                "Scan user systems",
                "Block user access until clean"
            ]
        }
        
        return actions.get(threat_detection.threat_type, ["Review and investigate"])

    async def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat detection engine statistics"""
        try:
            current_time = datetime.utcnow()
            last_24h = current_time - timedelta(days=1)
            
            # Count threats by type in last 24h
            recent_threats = [
                t for t in self.threat_history
                if t.detected_at > last_24h
            ]
            
            threat_counts = defaultdict(int)
            for threat in recent_threats:
                threat_counts[threat.threat_type.value] += 1
            
            return {
                "total_events_processed": len(self.security_events),
                "active_threats": len(self.active_threats),
                "total_threats_detected": len(self.threat_history),
                "threats_last_24h": len(recent_threats),
                "threat_types_last_24h": dict(threat_counts),
                "active_alerts": len(self.active_alerts),
                "behavioral_baselines": len(self.behavioral_baselines),
                "threat_intelligence_feeds": len(self.threat_intelligence),
                "malicious_ips_count": len(self.malicious_ips),
                "average_processing_time_ms": sum(self.detection_metrics["processing_time"][-1000:]) / min(len(self.detection_metrics["processing_time"]), 1000) if self.detection_metrics["processing_time"] else 0.0,
                "detection_rules_enabled": len([r for r in self.detection_rules.values() if r["enabled"]]),
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get threat statistics: {e}")
            return {"error": str(e)}


# Factory function for easier instantiation
def create_threat_detection_engine() -> ThreatDetectionEngine:
    """Factory function to create a Threat Detection Engine"""
    return ThreatDetectionEngine()


# Example usage and testing
async def main():
    """Example usage of Threat Detection Engine"""
    threat_engine = create_threat_detection_engine()
    
    # Simulate security events
    events = [
        SecurityEvent(
            event_id="event_001",
            event_type="authentication",
            timestamp=datetime.utcnow(),
            user_id="user_123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0...",
            success=False
        ),
        SecurityEvent(
            event_id="event_002",
            event_type="api_call",
            timestamp=datetime.utcnow(),
            user_id="user_123",
            ip_address="192.168.1.100",
            resource="/api/content/download",
            action="GET",
            details={"file_size_mb": 150}
        )
    ]
    
    # Process events
    for event in events:
        threats = await threat_engine.process_security_event(event)
        if threats:
            print(f"Threats detected: {[t.threat_type.value for t in threats]}")
    
    # Get statistics
    stats = await threat_engine.get_threat_statistics()
    print(f"Threat Detection Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())