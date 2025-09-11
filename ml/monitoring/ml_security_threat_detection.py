#!/usr/bin/env python3
"""
🛡️ ML Security Threat Detection System
Sécurité Implementation - Advanced ML Infrastructure Protection

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

Enterprise-grade security monitoring and threat detection for ML infrastructure
with real-time anomaly detection, attack prevention, and security compliance.
"""

import asyncio
import logging
import json
import hashlib
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import re
from pathlib import Path
import psutil
import base64
from cryptography.fernet import Fernet
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import socket
import subprocess
import sqlite3
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    MODEL_POISONING = "model_poisoning"
    DATA_EXFILTRATION = "data_exfiltration"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RESOURCE_ABUSE = "resource_abuse"
    INJECTION_ATTACK = "injection_attack"
    DDoS = "ddos"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMPLIANCE_VIOLATION = "compliance_violation"

class SecurityEventType(Enum):
    """Types of security events"""
    LOGIN_ATTEMPT = "login_attempt"
    MODEL_ACCESS = "model_access"
    DATA_ACCESS = "data_access"
    INFERENCE_REQUEST = "inference_request"
    ADMIN_ACTION = "admin_action"
    SYSTEM_CHANGE = "system_change"
    NETWORK_ACCESS = "network_access"
    FILE_ACCESS = "file_access"

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:16])
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: SecurityEventType = SecurityEventType.INFERENCE_REQUEST
    source_ip: str = ""
    user_id: str = ""
    resource: str = ""
    action: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    anomaly_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for analysis"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'resource': self.resource,
            'action': self.action,
            'details': self.details,
            'risk_score': self.risk_score,
            'anomaly_score': self.anomaly_score
        }

@dataclass
class ThreatAlert:
    """Security threat alert"""
    alert_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:16])
    timestamp: datetime = field(default_factory=datetime.utcnow)
    threat_type: ThreatType = ThreatType.SUSPICIOUS_ACTIVITY
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    description: str = ""
    affected_resources: List[str] = field(default_factory=list)
    source_events: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    mitigation_actions: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'threat_type': self.threat_type.value,
            'threat_level': self.threat_level.value,
            'description': self.description,
            'affected_resources': self.affected_resources,
            'source_events': self.source_events,
            'evidence': self.evidence,
            'mitigation_actions': self.mitigation_actions,
            'resolved': self.resolved,
            'resolution_notes': self.resolution_notes
        }

@dataclass
class SecurityConfig:
    """Security monitoring configuration"""
    enable_realtime_monitoring: bool = True
    enable_anomaly_detection: bool = True
    enable_behavioral_analysis: bool = True
    anomaly_threshold: float = 0.7
    max_login_attempts: int = 5
    session_timeout_minutes: int = 30
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 100
    enable_encryption: bool = True
    enable_audit_logging: bool = True
    blocked_ips: List[str] = field(default_factory=list)
    allowed_countries: List[str] = field(default_factory=lambda: ["US", "CA", "GB", "DE", "FR"])
    enable_geo_blocking: bool = True
    database_path: str = "security_monitoring.db"

class AnomalyDetector:
    """ML-based anomaly detection for security events"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'hour_of_day', 'day_of_week', 'request_rate', 'unique_ips',
            'failed_requests', 'data_volume', 'session_duration'
        ]
    
    def extract_features(self, events: List[SecurityEvent]) -> np.ndarray:
        """Extract features from security events for anomaly detection"""
        if not events:
            return np.array([[]])
        
        # Group events by hour
        hourly_stats = defaultdict(lambda: {
            'request_count': 0,
            'unique_ips': set(),
            'failed_requests': 0,
            'data_volume': 0,
            'session_durations': []
        })
        
        for event in events:
            hour_key = event.timestamp.replace(minute=0, second=0, microsecond=0)
            stats = hourly_stats[hour_key]
            
            stats['request_count'] += 1
            stats['unique_ips'].add(event.source_ip)
            
            if event.details.get('success', True) is False:
                stats['failed_requests'] += 1
            
            if 'data_size' in event.details:
                stats['data_volume'] += event.details['data_size']
            
            if 'session_duration' in event.details:
                stats['session_durations'].append(event.details['session_duration'])
        
        # Convert to feature matrix
        features = []
        for hour_key, stats in hourly_stats.items():
            feature_row = [
                hour_key.hour,  # hour_of_day
                hour_key.weekday(),  # day_of_week
                stats['request_count'],  # request_rate
                len(stats['unique_ips']),  # unique_ips
                stats['failed_requests'],  # failed_requests
                stats['data_volume'],  # data_volume
                np.mean(stats['session_durations']) if stats['session_durations'] else 0  # avg_session_duration
            ]
            features.append(feature_row)
        
        return np.array(features)
    
    def train(self, training_events: List[SecurityEvent]):
        """Train anomaly detection model"""
        features = self.extract_features(training_events)
        
        if features.size == 0:
            logger.warning("⚠️ No features extracted for training")
            return
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Train isolation forest
        self.isolation_forest.fit(scaled_features)
        self.is_trained = True
        
        logger.info(f"✅ Anomaly detector trained on {len(features)} samples")
    
    def detect_anomalies(self, events: List[SecurityEvent]) -> List[Tuple[SecurityEvent, float]]:
        """Detect anomalies in security events"""
        if not self.is_trained:
            logger.warning("⚠️ Anomaly detector not trained")
            return []
        
        features = self.extract_features(events)
        
        if features.size == 0:
            return []
        
        # Scale features
        scaled_features = self.scaler.transform(features)
        
        # Get anomaly scores
        anomaly_scores = self.isolation_forest.decision_function(scaled_features)
        predictions = self.isolation_forest.predict(scaled_features)
        
        # Return anomalous events with scores
        anomalous_events = []
        for i, (event, score, prediction) in enumerate(zip(events, anomaly_scores, predictions)):
            if prediction == -1:  # Anomaly
                # Convert decision function score to probability-like score
                anomaly_probability = 1 / (1 + np.exp(score))
                anomalous_events.append((event, anomaly_probability))
        
        return anomalous_events

class BehavioralAnalyzer:
    """User behavioral analysis for threat detection"""
    
    def __init__(self):
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.baseline_period_days = 7
    
    def update_user_profile(self, event: SecurityEvent):
        """Update user behavioral profile"""
        user_id = event.user_id
        if not user_id:
            return
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'first_seen': event.timestamp,
                'last_seen': event.timestamp,
                'login_times': [],
                'source_ips': set(),
                'resources_accessed': set(),
                'actions_performed': defaultdict(int),
                'request_patterns': deque(maxlen=100),
                'anomaly_scores': deque(maxlen=50)
            }
        
        profile = self.user_profiles[user_id]
        profile['last_seen'] = event.timestamp
        
        if event.event_type == SecurityEventType.LOGIN_ATTEMPT:
            profile['login_times'].append(event.timestamp)
        
        profile['source_ips'].add(event.source_ip)
        profile['resources_accessed'].add(event.resource)
        profile['actions_performed'][event.action] += 1
        
        # Store request timing pattern
        profile['request_patterns'].append(event.timestamp.timestamp())
        profile['anomaly_scores'].append(event.anomaly_score)
    
    def analyze_user_behavior(self, user_id: str, current_event: SecurityEvent) -> Dict[str, Any]:
        """Analyze user behavior for anomalies"""
        if user_id not in self.user_profiles:
            return {'risk_score': 0.5, 'anomalies': ['new_user']}
        
        profile = self.user_profiles[user_id]
        anomalies = []
        risk_factors = []
        
        # Check for unusual login times
        current_hour = current_event.timestamp.hour
        historical_hours = [t.hour for t in profile['login_times'][-20:]]  # Last 20 logins
        
        if historical_hours and current_hour not in historical_hours:
            anomalies.append('unusual_login_time')
            risk_factors.append(0.3)
        
        # Check for new IP address
        if current_event.source_ip not in profile['source_ips']:
            if len(profile['source_ips']) > 3:  # User has established IP pattern
                anomalies.append('new_ip_address')
                risk_factors.append(0.4)
        
        # Check for unusual resource access
        if (current_event.resource not in profile['resources_accessed'] and
            len(profile['resources_accessed']) > 5):
            anomalies.append('new_resource_access')
            risk_factors.append(0.2)
        
        # Check for rapid requests (possible automation)
        if len(profile['request_patterns']) > 1:
            recent_requests = list(profile['request_patterns'])[-10:]
            if len(recent_requests) >= 5:
                intervals = [recent_requests[i] - recent_requests[i-1] 
                           for i in range(1, len(recent_requests))]
                avg_interval = np.mean(intervals)
                
                if avg_interval < 1.0:  # Less than 1 second between requests
                    anomalies.append('rapid_requests')
                    risk_factors.append(0.5)
        
        # Check for elevated anomaly scores
        if profile['anomaly_scores']:
            avg_anomaly_score = np.mean(profile['anomaly_scores'])
            if avg_anomaly_score > 0.7:
                anomalies.append('high_anomaly_pattern')
                risk_factors.append(0.6)
        
        # Calculate overall risk score
        risk_score = min(1.0, sum(risk_factors)) if risk_factors else 0.1
        
        return {
            'risk_score': risk_score,
            'anomalies': anomalies,
            'profile_stats': {
                'days_active': (current_event.timestamp - profile['first_seen']).days,
                'unique_ips': len(profile['source_ips']),
                'resources_accessed': len(profile['resources_accessed']),
                'total_actions': sum(profile['actions_performed'].values())
            }
        }

class MLSecurityThreatDetection:
    """
    🛡️ ML Security Threat Detection System
    
    Advanced security monitoring for ML infrastructure with real-time threat
    detection, behavioral analysis, and automated response capabilities.
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.events: deque = deque(maxlen=10000)  # Keep last 10k events
        self.alerts: List[ThreatAlert] = []
        self.anomaly_detector = AnomalyDetector()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.blocked_ips: set = set(config.blocked_ips)
        self.session_store: Dict[str, Dict[str, Any]] = {}
        self.locks = {
            'events': threading.Lock(),
            'alerts': threading.Lock(),
            'sessions': threading.Lock()
        }
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
        # Start background monitoring
        if config.enable_realtime_monitoring:
            asyncio.create_task(self._realtime_monitoring_loop())
        
        # Start maintenance tasks
        asyncio.create_task(self._background_maintenance())
        
        logger.info(f"🛡️ ML Security Threat Detection System initialized")
    
    async def _initialize_database(self):
        """Initialize security monitoring database"""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                
                # Security events table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS security_events (
                        event_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        source_ip TEXT,
                        user_id TEXT,
                        resource TEXT,
                        action TEXT,
                        details TEXT,
                        risk_score REAL,
                        anomaly_score REAL
                    )
                """)
                
                # Threat alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS threat_alerts (
                        alert_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        threat_type TEXT NOT NULL,
                        threat_level TEXT NOT NULL,
                        description TEXT,
                        affected_resources TEXT,
                        source_events TEXT,
                        evidence TEXT,
                        mitigation_actions TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        resolution_notes TEXT
                    )
                """)
                
                # Blocked IPs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS blocked_ips (
                        ip_address TEXT PRIMARY KEY,
                        blocked_at TEXT NOT NULL,
                        reason TEXT,
                        expires_at TEXT
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_source_ip ON security_events(source_ip)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON security_events(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON threat_alerts(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_threat_level ON threat_alerts(threat_level)")
                
                conn.commit()
                
            logger.info("✅ Security database initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize security database: {str(e)}")
            raise
    
    async def log_security_event(
        self,
        event_type: SecurityEventType,
        source_ip: str = "",
        user_id: str = "",
        resource: str = "",
        action: str = "",
        details: Dict[str, Any] = None
    ) -> SecurityEvent:
        """
        Log a security event for monitoring
        
        Args:
            event_type: Type of security event
            source_ip: Source IP address
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed
            details: Additional event details
            
        Returns:
            Created SecurityEvent
        """
        event = SecurityEvent(
            event_type=event_type,
            source_ip=source_ip,
            user_id=user_id,
            resource=resource,
            action=action,
            details=details or {}
        )
        
        # Perform real-time security checks
        await self._perform_security_checks(event)
        
        # Store event
        with self.locks['events']:
            self.events.append(event)
        
        # Update behavioral profiles
        if user_id:
            self.behavioral_analyzer.update_user_profile(event)
        
        # Persist to database
        await self._persist_security_event(event)
        
        logger.debug(f"🔍 Security event logged: {event_type.value} from {source_ip}")
        return event
    
    async def _perform_security_checks(self, event: SecurityEvent):
        """Perform real-time security checks on event"""
        threats_detected = []
        
        # Check IP blocking
        if event.source_ip in self.blocked_ips:
            threats_detected.append(ThreatType.UNAUTHORIZED_ACCESS)
        
        # Check rate limiting
        if self.config.enable_rate_limiting:
            rate_limit_exceeded = await self._check_rate_limiting(event)
            if rate_limit_exceeded:
                threats_detected.append(ThreatType.RESOURCE_ABUSE)
        
        # Check for injection attacks
        injection_detected = await self._check_injection_attacks(event)
        if injection_detected:
            threats_detected.append(ThreatType.INJECTION_ATTACK)
        
        # Check geographic restrictions
        if self.config.enable_geo_blocking:
            geo_violation = await self._check_geographic_restrictions(event)
            if geo_violation:
                threats_detected.append(ThreatType.UNAUTHORIZED_ACCESS)
        
        # Behavioral analysis
        if event.user_id:
            behavioral_analysis = self.behavioral_analyzer.analyze_user_behavior(
                event.user_id, event
            )
            event.risk_score = behavioral_analysis['risk_score']
            
            if behavioral_analysis['risk_score'] > 0.7:
                threats_detected.append(ThreatType.SUSPICIOUS_ACTIVITY)
        
        # Generate alerts for detected threats
        for threat_type in threats_detected:
            await self._generate_threat_alert(threat_type, event)
    
    async def _check_rate_limiting(self, event: SecurityEvent) -> bool:
        """Check if rate limiting is exceeded"""
        identifier = f"{event.source_ip}:{event.user_id}"
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        rate_limiter = self.rate_limiters[identifier]
        while rate_limiter and current_time - rate_limiter[0] > 60:
            rate_limiter.popleft()
        
        # Add current request
        rate_limiter.append(current_time)
        
        # Check if limit exceeded
        if len(rate_limiter) > self.config.max_requests_per_minute:
            logger.warning(f"⚠️ Rate limit exceeded for {identifier}: {len(rate_limiter)} requests/min")
            return True
        
        return False
    
    async def _check_injection_attacks(self, event: SecurityEvent) -> bool:
        """Check for injection attack patterns"""
        # Common injection patterns
        injection_patterns = [
            r"(\bSELECT\b|\bUNION\b|\bINSERT\b|\bDELETE\b|\bDROP\b)",  # SQL injection
            r"(<script|<iframe|<object|javascript:|vbscript:)",  # XSS
            r"(\.\./|\.\.\\\|/etc/passwd|/bin/sh)",  # Path traversal
            r"(__import__|exec\(|eval\(|compile\()",  # Python injection
        ]
        
        # Check request details for injection patterns
        text_to_check = " ".join([
            str(event.details.get('request_body', '')),
            str(event.details.get('query_params', '')),
            str(event.details.get('headers', '')),
            event.resource,
            event.action
        ]).lower()
        
        for pattern in injection_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                logger.warning(f"⚠️ Injection pattern detected: {pattern} in request from {event.source_ip}")
                return True
        
        return False
    
    async def _check_geographic_restrictions(self, event: SecurityEvent) -> bool:
        """Check geographic access restrictions"""
        try:
            # Mock geolocation check (in production, use actual geo IP service)
            ip = ipaddress.ip_address(event.source_ip)
            
            # Skip private/local IPs
            if ip.is_private or ip.is_loopback:
                return False
            
            # Mock country detection (replace with actual service)
            # For demo purposes, randomly assign countries
            import random
            mock_countries = ["US", "CA", "GB", "DE", "FR", "CN", "RU", "IN"]
            detected_country = random.choice(mock_countries)
            
            if detected_country not in self.config.allowed_countries:
                logger.warning(f"⚠️ Access from restricted country: {detected_country} ({event.source_ip})")
                return True
            
        except (ValueError, AttributeError):
            # Invalid IP address
            logger.warning(f"⚠️ Invalid IP address: {event.source_ip}")
            return True
        
        return False
    
    async def _generate_threat_alert(self, threat_type: ThreatType, event: SecurityEvent):
        """Generate threat alert"""
        # Determine threat level based on type and context
        threat_level = self._determine_threat_level(threat_type, event)
        
        # Create alert
        alert = ThreatAlert(
            threat_type=threat_type,
            threat_level=threat_level,
            description=self._generate_threat_description(threat_type, event),
            affected_resources=[event.resource] if event.resource else [],
            source_events=[event.event_id],
            evidence={
                'source_ip': event.source_ip,
                'user_id': event.user_id,
                'timestamp': event.timestamp.isoformat(),
                'event_details': event.details,
                'risk_score': event.risk_score
            },
            mitigation_actions=self._get_mitigation_actions(threat_type)
        )
        
        # Store alert
        with self.locks['alerts']:
            self.alerts.append(alert)
        
        # Execute immediate response actions
        await self._execute_immediate_response(alert, event)
        
        # Persist alert
        await self._persist_threat_alert(alert)
        
        logger.warning(f"🚨 Threat alert generated: {threat_type.value} ({threat_level.value}) from {event.source_ip}")
    
    def _determine_threat_level(self, threat_type: ThreatType, event: SecurityEvent) -> ThreatLevel:
        """Determine threat severity level"""
        base_levels = {
            ThreatType.MODEL_POISONING: ThreatLevel.CRITICAL,
            ThreatType.DATA_EXFILTRATION: ThreatLevel.CRITICAL,
            ThreatType.ADVERSARIAL_ATTACK: ThreatLevel.HIGH,
            ThreatType.UNAUTHORIZED_ACCESS: ThreatLevel.HIGH,
            ThreatType.RESOURCE_ABUSE: ThreatLevel.MEDIUM,
            ThreatType.INJECTION_ATTACK: ThreatLevel.HIGH,
            ThreatType.DDoS: ThreatLevel.HIGH,
            ThreatType.PRIVILEGE_ESCALATION: ThreatLevel.CRITICAL,
            ThreatType.SUSPICIOUS_ACTIVITY: ThreatLevel.MEDIUM,
            ThreatType.COMPLIANCE_VIOLATION: ThreatLevel.MEDIUM
        }
        
        base_level = base_levels.get(threat_type, ThreatLevel.MEDIUM)
        
        # Escalate based on risk score
        if event.risk_score > 0.9:
            if base_level == ThreatLevel.MEDIUM:
                return ThreatLevel.HIGH
            elif base_level == ThreatLevel.HIGH:
                return ThreatLevel.CRITICAL
        
        return base_level
    
    def _generate_threat_description(self, threat_type: ThreatType, event: SecurityEvent) -> str:
        """Generate human-readable threat description"""
        descriptions = {
            ThreatType.MODEL_POISONING: f"Potential model poisoning attempt detected from {event.source_ip}",
            ThreatType.DATA_EXFILTRATION: f"Suspicious data access pattern detected for user {event.user_id}",
            ThreatType.ADVERSARIAL_ATTACK: f"Adversarial attack pattern detected in inference requests",
            ThreatType.UNAUTHORIZED_ACCESS: f"Unauthorized access attempt from {event.source_ip}",
            ThreatType.RESOURCE_ABUSE: f"Resource abuse detected: excessive requests from {event.source_ip}",
            ThreatType.INJECTION_ATTACK: f"Injection attack detected in request from {event.source_ip}",
            ThreatType.DDoS: f"Potential DDoS attack detected from {event.source_ip}",
            ThreatType.PRIVILEGE_ESCALATION: f"Privilege escalation attempt by user {event.user_id}",
            ThreatType.SUSPICIOUS_ACTIVITY: f"Suspicious behavioral pattern detected for user {event.user_id}",
            ThreatType.COMPLIANCE_VIOLATION: f"Compliance violation detected in {event.resource} access"
        }
        
        return descriptions.get(threat_type, f"Security threat detected: {threat_type.value}")
    
    def _get_mitigation_actions(self, threat_type: ThreatType) -> List[str]:
        """Get recommended mitigation actions"""
        mitigations = {
            ThreatType.MODEL_POISONING: [
                "Isolate affected models",
                "Validate training data integrity",
                "Implement model versioning rollback",
                "Review data sources"
            ],
            ThreatType.DATA_EXFILTRATION: [
                "Block suspicious IP addresses",
                "Revoke user access tokens",
                "Enable additional data access monitoring",
                "Notify data protection officer"
            ],
            ThreatType.ADVERSARIAL_ATTACK: [
                "Enable adversarial detection filters",
                "Implement input validation",
                "Log attack patterns for analysis",
                "Update model robustness"
            ],
            ThreatType.UNAUTHORIZED_ACCESS: [
                "Block source IP address",
                "Force password reset for affected accounts",
                "Enable multi-factor authentication",
                "Review access logs"
            ],
            ThreatType.RESOURCE_ABUSE: [
                "Implement rate limiting",
                "Block abusive IP addresses",
                "Monitor resource usage patterns",
                "Scale infrastructure if needed"
            ],
            ThreatType.INJECTION_ATTACK: [
                "Block malicious requests",
                "Update input validation rules",
                "Scan for vulnerabilities",
                "Monitor for data corruption"
            ]
        }
        
        return mitigations.get(threat_type, ["Investigate threat", "Monitor for escalation"])
    
    async def _execute_immediate_response(self, alert: ThreatAlert, event: SecurityEvent):
        """Execute immediate response actions"""
        if alert.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            # Auto-block IP for high/critical threats
            if event.source_ip and event.source_ip not in self.blocked_ips:
                await self.block_ip_address(
                    event.source_ip,
                    reason=f"Auto-blocked due to {alert.threat_type.value}",
                    duration_hours=24
                )
        
        if alert.threat_type == ThreatType.RESOURCE_ABUSE:
            # Implement temporary rate limiting
            identifier = f"{event.source_ip}:{event.user_id}"
            self.rate_limiters[identifier] = deque(maxlen=10)  # Reduce limit
        
        if alert.threat_level == ThreatLevel.CRITICAL:
            # Log critical alerts immediately
            logger.critical(f"🚨 CRITICAL THREAT: {alert.description}")
    
    async def block_ip_address(
        self,
        ip_address: str,
        reason: str = "Security violation",
        duration_hours: int = 24
    ):
        """Block IP address for security reasons"""
        self.blocked_ips.add(ip_address)
        
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        # Persist to database
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO blocked_ips 
                    (ip_address, blocked_at, reason, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    ip_address,
                    datetime.utcnow().isoformat(),
                    reason,
                    expires_at.isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to persist IP block: {str(e)}")
        
        logger.warning(f"🚫 Blocked IP address: {ip_address} (reason: {reason})")
    
    async def unblock_ip_address(self, ip_address: str):
        """Unblock IP address"""
        self.blocked_ips.discard(ip_address)
        
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM blocked_ips WHERE ip_address = ?", (ip_address,))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to remove IP block: {str(e)}")
        
        logger.info(f"✅ Unblocked IP address: {ip_address}")
    
    async def analyze_attack_patterns(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze attack patterns over time window"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Filter recent events
        recent_events = [
            event for event in self.events
            if event.timestamp > cutoff_time
        ]
        
        # Filter recent alerts
        recent_alerts = [
            alert for alert in self.alerts
            if alert.timestamp > cutoff_time
        ]
        
        # Analyze patterns
        attack_analysis = {
            'time_window_hours': time_window_hours,
            'total_events': len(recent_events),
            'total_alerts': len(recent_alerts),
            'threat_type_distribution': {},
            'threat_level_distribution': {},
            'top_attacking_ips': {},
            'top_targeted_resources': {},
            'attack_timeline': [],
            'geographical_distribution': {},
            'user_risk_analysis': {}
        }
        
        # Threat type distribution
        for alert in recent_alerts:
            threat_type = alert.threat_type.value
            attack_analysis['threat_type_distribution'][threat_type] = \
                attack_analysis['threat_type_distribution'].get(threat_type, 0) + 1
        
        # Threat level distribution
        for alert in recent_alerts:
            threat_level = alert.threat_level.value
            attack_analysis['threat_level_distribution'][threat_level] = \
                attack_analysis['threat_level_distribution'].get(threat_level, 0) + 1
        
        # Top attacking IPs
        ip_counts = defaultdict(int)
        for event in recent_events:
            if event.risk_score > 0.5:
                ip_counts[event.source_ip] += 1
        
        attack_analysis['top_attacking_ips'] = dict(
            sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Top targeted resources
        resource_counts = defaultdict(int)
        for event in recent_events:
            if event.resource:
                resource_counts[event.resource] += 1
        
        attack_analysis['top_targeted_resources'] = dict(
            sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Attack timeline (hourly)
        hourly_attacks = defaultdict(int)
        for alert in recent_alerts:
            hour_key = alert.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_attacks[hour_key.isoformat()] += 1
        
        attack_analysis['attack_timeline'] = dict(hourly_attacks)
        
        # User risk analysis
        user_risks = {}
        for user_id, profile in self.behavioral_analyzer.user_profiles.items():
            if profile['anomaly_scores']:
                avg_risk = np.mean(profile['anomaly_scores'])
                user_risks[user_id] = {
                    'average_risk_score': avg_risk,
                    'unique_ips': len(profile['source_ips']),
                    'total_actions': sum(profile['actions_performed'].values())
                }
        
        # Sort by risk score
        attack_analysis['user_risk_analysis'] = dict(
            sorted(user_risks.items(), key=lambda x: x[1]['average_risk_score'], reverse=True)[:10]
        )
        
        return attack_analysis
    
    async def _realtime_monitoring_loop(self):
        """Real-time monitoring background task"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Run anomaly detection on recent events
                if self.config.enable_anomaly_detection:
                    await self._run_anomaly_detection()
                
                # Check for attack patterns
                await self._check_attack_patterns()
                
            except Exception as e:
                logger.error(f"❌ Real-time monitoring error: {str(e)}")
    
    async def _run_anomaly_detection(self):
        """Run anomaly detection on recent events"""
        if len(self.events) < 100:  # Need sufficient data
            return
        
        recent_events = list(self.events)[-1000:]  # Last 1000 events
        
        # Train if not trained yet
        if not self.anomaly_detector.is_trained:
            training_events = recent_events[:500]  # Use first 500 for training
            self.anomaly_detector.train(training_events)
        
        # Detect anomalies in recent events
        test_events = recent_events[-100:]  # Test on last 100 events
        anomalous_events = self.anomaly_detector.detect_anomalies(test_events)
        
        # Generate alerts for high-anomaly events
        for event, anomaly_score in anomalous_events:
            event.anomaly_score = anomaly_score
            
            if anomaly_score > self.config.anomaly_threshold:
                await self._generate_threat_alert(ThreatType.SUSPICIOUS_ACTIVITY, event)
    
    async def _check_attack_patterns(self):
        """Check for coordinated attack patterns"""
        recent_events = [
            event for event in self.events
            if (datetime.utcnow() - event.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        # Check for DDoS patterns
        ip_request_counts = defaultdict(int)
        for event in recent_events:
            ip_request_counts[event.source_ip] += 1
        
        # Alert if any IP has excessive requests
        for ip, count in ip_request_counts.items():
            if count > 500:  # More than 500 requests per hour
                # Create synthetic event for alert
                ddos_event = SecurityEvent(
                    event_type=SecurityEventType.NETWORK_ACCESS,
                    source_ip=ip,
                    action="excessive_requests",
                    details={'request_count': count, 'time_window': 'last_hour'}
                )
                await self._generate_threat_alert(ThreatType.DDoS, ddos_event)
    
    async def _background_maintenance(self):
        """Background maintenance tasks"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Unblock expired IP addresses
                await self._cleanup_expired_blocks()
                
                # Clean old events and alerts
                await self._cleanup_old_data()
                
                # Update anomaly detection model
                if len(self.events) > 1000:
                    await self._retrain_anomaly_detector()
                
            except Exception as e:
                logger.error(f"❌ Background maintenance error: {str(e)}")
    
    async def _cleanup_expired_blocks(self):
        """Remove expired IP blocks"""
        current_time = datetime.utcnow()
        
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                
                # Get expired blocks
                cursor.execute("""
                    SELECT ip_address FROM blocked_ips 
                    WHERE expires_at < ?
                """, (current_time.isoformat(),))
                
                expired_ips = [row[0] for row in cursor.fetchall()]
                
                # Remove from memory and database
                for ip in expired_ips:
                    self.blocked_ips.discard(ip)
                
                cursor.execute("DELETE FROM blocked_ips WHERE expires_at < ?", 
                              (current_time.isoformat(),))
                conn.commit()
                
                if expired_ips:
                    logger.info(f"🧹 Cleaned up {len(expired_ips)} expired IP blocks")
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired blocks: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old events and alerts"""
        cutoff_time = datetime.utcnow() - timedelta(days=30)  # Keep 30 days
        
        # Clean events in memory
        with self.locks['events']:
            self.events = deque(
                (event for event in self.events if event.timestamp > cutoff_time),
                maxlen=self.events.maxlen
            )
        
        # Clean alerts in memory
        with self.locks['alerts']:
            self.alerts = [
                alert for alert in self.alerts
                if alert.timestamp > cutoff_time
            ]
        
        # Clean database
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM security_events WHERE timestamp < ?",
                              (cutoff_time.isoformat(),))
                cursor.execute("DELETE FROM threat_alerts WHERE timestamp < ?",
                              (cutoff_time.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {str(e)}")
    
    async def _retrain_anomaly_detector(self):
        """Retrain anomaly detection model with recent data"""
        recent_events = list(self.events)[-2000:]  # Use last 2000 events
        self.anomaly_detector.train(recent_events)
        logger.info("🔄 Retrained anomaly detection model")
    
    async def _persist_security_event(self, event: SecurityEvent):
        """Persist security event to database"""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO security_events 
                    (event_id, timestamp, event_type, source_ip, user_id, resource, 
                     action, details, risk_score, anomaly_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    event.source_ip,
                    event.user_id,
                    event.resource,
                    event.action,
                    json.dumps(event.details),
                    event.risk_score,
                    event.anomaly_score
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to persist security event: {str(e)}")
    
    async def _persist_threat_alert(self, alert: ThreatAlert):
        """Persist threat alert to database"""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO threat_alerts 
                    (alert_id, timestamp, threat_type, threat_level, description,
                     affected_resources, source_events, evidence, mitigation_actions,
                     resolved, resolution_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp.isoformat(),
                    alert.threat_type.value,
                    alert.threat_level.value,
                    alert.description,
                    json.dumps(alert.affected_resources),
                    json.dumps(alert.source_events),
                    json.dumps(alert.evidence),
                    json.dumps(alert.mitigation_actions),
                    alert.resolved,
                    alert.resolution_notes
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to persist threat alert: {str(e)}")
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        recent_time = datetime.utcnow() - timedelta(hours=24)
        
        recent_events = [
            event for event in self.events
            if event.timestamp > recent_time
        ]
        
        recent_alerts = [
            alert for alert in self.alerts
            if alert.timestamp > recent_time
        ]
        
        dashboard = {
            "security_status": "active",
            "last_updated": datetime.utcnow().isoformat(),
            "statistics_24h": {
                "total_events": len(recent_events),
                "total_alerts": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a.threat_level == ThreatLevel.CRITICAL]),
                "high_alerts": len([a for a in recent_alerts if a.threat_level == ThreatLevel.HIGH]),
                "blocked_ips": len(self.blocked_ips),
                "unique_users": len(set(e.user_id for e in recent_events if e.user_id)),
                "unique_source_ips": len(set(e.source_ip for e in recent_events if e.source_ip))
            },
            "top_threats": {
                threat_type.value: len([
                    a for a in recent_alerts 
                    if a.threat_type == threat_type
                ])
                for threat_type in ThreatType
            },
            "recent_critical_alerts": [
                alert.to_dict() for alert in recent_alerts
                if alert.threat_level == ThreatLevel.CRITICAL
            ][:5],
            "system_health": {
                "anomaly_detector_trained": self.anomaly_detector.is_trained,
                "active_sessions": len(self.session_store),
                "rate_limiters_active": len(self.rate_limiters),
                "database_connected": True  # Simplified check
            }
        }
        
        return dashboard

async def main():
    """Example usage of ML Security Threat Detection System"""
    # Initialize security system
    config = SecurityConfig(
        enable_realtime_monitoring=True,
        enable_anomaly_detection=True,
        enable_behavioral_analysis=True,
        max_requests_per_minute=50,
        database_path="/tmp/security_monitoring.db"
    )
    
    security_system = MLSecurityThreatDetection(config)
    
    # Simulate security events
    await security_system.log_security_event(
        event_type=SecurityEventType.LOGIN_ATTEMPT,
        source_ip="192.168.1.100",
        user_id="musician_123",
        action="login",
        details={"success": True, "user_agent": "Mozilla/5.0"}
    )
    
    # Simulate suspicious activity
    await security_system.log_security_event(
        event_type=SecurityEventType.MODEL_ACCESS,
        source_ip="10.0.0.50",
        user_id="unknown_user",
        resource="production_model_v2",
        action="download",
        details={"model_size_mb": 500, "success": False}
    )
    
    # Analyze attack patterns
    attack_analysis = await security_system.analyze_attack_patterns(time_window_hours=1)
    print(f"🔍 Attack Analysis: {json.dumps(attack_analysis, indent=2)}")
    
    # Get security dashboard
    dashboard = security_system.get_security_dashboard()
    print(f"🛡️ Security Dashboard: {json.dumps(dashboard, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())