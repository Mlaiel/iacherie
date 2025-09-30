#!/usr/bin/env python3
"""
🚨 Threat Detector - Enterprise Security Module
===============================================

Ultra-advanced threat detection with ML-powered analysis,
real-time monitoring, and automated incident response.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + ML + AI + DevOps + Backend
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, deque

import redis
import numpy as np
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatCategory(Enum):
    """Categories of security threats"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    DDOS = "ddos"
    INJECTION = "injection"
    XSS = "xss"
    CSRF = "csrf"
    BRUTE_FORCE = "brute_force"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    INSIDER_THREAT = "insider_threat"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_NETWORK = "suspicious_network"
    BOT_ACTIVITY = "bot_activity"
    ACCOUNT_TAKEOVER = "account_takeover"

class EventType(Enum):
    """Types of security events"""
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    FILE_UPLOAD = "file_upload"
    API_REQUEST = "api_request"
    SYSTEM_CHANGE = "system_change"
    NETWORK_CONNECTION = "network_connection"
    ERROR_OCCURRENCE = "error_occurrence"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class ResponseAction(Enum):
    """Automated response actions"""
    LOG_ONLY = "log_only"
    ALERT = "alert"
    BLOCK_IP = "block_ip"
    SUSPEND_USER = "suspend_user"
    FORCE_LOGOUT = "force_logout"
    INCREASE_MONITORING = "increase_monitoring"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SUSPICIOUS_ACTIVITY
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: str = "unknown"
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    success: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    geographic_location: Optional[Dict[str, str]] = None
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThreatEvent:
    """Detected threat event"""
    threat_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    threat_category: ThreatCategory = ThreatCategory.SUSPICIOUS_NETWORK
    confidence_score: float = 0.0
    source_events: List[SecurityEvent] = field(default_factory=list)
    affected_users: Set[str] = field(default_factory=set)
    affected_resources: Set[str] = field(default_factory=set)
    attack_vector: Optional[str] = None
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    mitigation_actions: List[ResponseAction] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    status: str = "active"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityAlert:
    """Security alert for notifications"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    threat_event: ThreatEvent = field(default_factory=ThreatEvent)
    alert_level: ThreatLevel = ThreatLevel.MEDIUM
    recipients: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)  # email, slack, sms, webhook
    message: str = ""
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ThreatIntelligence:
    """
    Threat intelligence system for enriching threat detection.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.intelligence_feeds = {}
        self.indicators_cache = {}
        
    async def initialize(self) -> None:
        """Initialize threat intelligence system"""
        try:
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Load threat intelligence feeds
            await self._load_threat_feeds()
            
            logger.info("Threat intelligence system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize threat intelligence: {e}")
            raise

    async def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Check IP address reputation"""
        try:
            # Check local cache first
            if ip_address in self.indicators_cache:
                return self.indicators_cache[ip_address]
            
            # Check Redis cache
            reputation_data = await self.redis.get(f"ip_reputation:{ip_address}")
            if reputation_data:
                reputation = json.loads(reputation_data)
                self.indicators_cache[ip_address] = reputation
                return reputation
            
            # Query threat intelligence feeds (placeholder)
            reputation = await self._query_ip_reputation(ip_address)
            
            # Cache result
            await self.redis.setex(
                f"ip_reputation:{ip_address}",
                3600,  # 1 hour
                json.dumps(reputation, default=str)
            )
            
            self.indicators_cache[ip_address] = reputation
            return reputation
            
        except Exception as e:
            logger.error(f"IP reputation check failed: {e}")
            return {"risk_score": 0.0, "categories": [], "last_seen": None}

    async def _load_threat_feeds(self) -> None:
        """Load threat intelligence feeds"""
        try:
            # Load known malicious IPs, domains, etc.
            # In production, this would integrate with commercial threat feeds
            self.intelligence_feeds = {
                "malicious_ips": set(),
                "suspicious_domains": set(),
                "known_malware_hashes": set(),
                "botnet_c2_servers": set()
            }
            
            logger.info("Threat intelligence feeds loaded")
            
        except Exception as e:
            logger.error(f"Failed to load threat feeds: {e}")

    async def _query_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Query external threat intelligence for IP reputation"""
        try:
            # Placeholder for actual threat intelligence API calls
            # In production, integrate with services like VirusTotal, AbuseIPDB, etc.
            
            reputation = {
                "ip_address": ip_address,
                "risk_score": 0.0,
                "categories": [],
                "last_seen": None,
                "source": "local_analysis"
            }
            
            # Simple local analysis
            if ip_address in self.intelligence_feeds.get("malicious_ips", set()):
                reputation["risk_score"] = 0.9
                reputation["categories"] = ["malware", "botnet"]
            
            return reputation
            
        except Exception as e:
            logger.error(f"IP reputation query failed: {e}")
            return {"risk_score": 0.0, "categories": [], "last_seen": None}

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class MLThreatAnalyzer:
    """
    Machine Learning-powered threat analysis engine.
    """
    
    def __init__(self):
        self.models = {}
        self.feature_extractors = {}
        self.training_data = defaultdict(list)
        self.model_last_trained = {}
        
    async def initialize(self) -> None:
        """Initialize ML threat analyzer"""
        try:
            # Initialize ML models for different threat types
            await self._initialize_models()
            
            logger.info("ML threat analyzer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML analyzer: {e}")
            raise

    async def analyze_events(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Analyze security events using ML models"""
        try:
            threats = []
            
            # Group events by type for analysis
            events_by_type = defaultdict(list)
            for event in events:
                events_by_type[event.event_type].append(event)
            
            # Analyze each group
            for event_type, event_list in events_by_type.items():
                event_threats = await self._analyze_event_group(event_type, event_list)
                threats.extend(event_threats)
            
            # Correlation analysis across event types
            correlation_threats = await self._correlation_analysis(events)
            threats.extend(correlation_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"ML threat analysis failed: {e}")
            return []

    async def _initialize_models(self) -> None:
        """Initialize ML models for threat detection"""
        try:
            # Initialize models for different threat categories
            self.models = {
                "anomaly_detection": self._create_anomaly_detector(),
                "brute_force": self._create_brute_force_detector(),
                "data_exfiltration": self._create_exfiltration_detector(),
                "insider_threat": self._create_insider_threat_detector()
            }
            
            # Initialize feature extractors
            self.feature_extractors = {
                "login_patterns": self._extract_login_features,
                "access_patterns": self._extract_access_features,
                "network_patterns": self._extract_network_features,
                "behavioral_patterns": self._extract_behavioral_features
            }
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise

    def _create_anomaly_detector(self):
        """Create anomaly detection model"""
        try:
            # Use Isolation Forest for anomaly detection
            from sklearn.ensemble import IsolationForest
            
            model = IsolationForest(
                contamination=0.1,  # 10% expected anomalies
                random_state=42,
                n_estimators=100
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Anomaly detector creation failed: {e}")
            return None

    def _create_brute_force_detector(self):
        """Create brute force attack detector"""
        try:
            # Simple statistical model for brute force detection
            return {
                "max_failures_per_minute": 10,
                "max_failures_per_hour": 50,
                "suspicious_user_agents": [
                    "curl", "wget", "python-requests", "bot"
                ]
            }
            
        except Exception as e:
            logger.error(f"Brute force detector creation failed: {e}")
            return None

    def _create_exfiltration_detector(self):
        """Create data exfiltration detector"""
        try:
            # Model for detecting unusual data access patterns
            return {
                "max_downloads_per_hour": 100,
                "max_data_volume_mb": 1000,
                "suspicious_access_patterns": [
                    "bulk_download", "off_hours_access", "unusual_geographic_access"
                ]
            }
            
        except Exception as e:
            logger.error(f"Exfiltration detector creation failed: {e}")
            return None

    def _create_insider_threat_detector(self):
        """Create insider threat detector"""
        try:
            # Model for detecting insider threats
            return {
                "privilege_escalation_threshold": 0.8,
                "unusual_access_threshold": 0.7,
                "behavioral_change_threshold": 0.6
            }
            
        except Exception as e:
            logger.error(f"Insider threat detector creation failed: {e}")
            return None

    async def _analyze_event_group(
        self,
        event_type: EventType,
        events: List[SecurityEvent]
    ) -> List[ThreatEvent]:
        """Analyze group of similar events"""
        try:
            threats = []
            
            if event_type == EventType.LOGIN_FAILURE:
                threats.extend(await self._detect_brute_force(events))
            elif event_type == EventType.DATA_ACCESS:
                threats.extend(await self._detect_data_exfiltration(events))
            elif event_type == EventType.PERMISSION_CHANGE:
                threats.extend(await self._detect_privilege_escalation(events))
            
            # General anomaly detection
            anomaly_threats = await self._detect_anomalies(events)
            threats.extend(anomaly_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Event group analysis failed: {e}")
            return []

    async def _detect_brute_force(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Detect brute force attacks"""
        try:
            threats = []
            
            # Group by IP address
            ip_failures = defaultdict(list)
            for event in events:
                if not event.success:
                    ip_failures[event.ip_address].append(event)
            
            # Analyze each IP
            for ip_address, failures in ip_failures.items():
                failure_count = len(failures)
                
                # Time window analysis
                if failure_count >= 10:  # 10+ failures
                    time_span = max(failure.timestamp for failure in failures) - min(failure.timestamp for failure in failures)
                    
                    if time_span.total_seconds() < 300:  # Within 5 minutes
                        threat = ThreatEvent(
                            threat_level=ThreatLevel.HIGH,
                            threat_category=ThreatCategory.BRUTE_FORCE,
                            confidence_score=min(0.9, failure_count / 20),
                            source_events=failures,
                            affected_users=set(event.user_id for event in failures if event.user_id),
                            attack_vector=f"Brute force from {ip_address}",
                            description=f"Detected {failure_count} failed login attempts from {ip_address} in {time_span.total_seconds():.0f} seconds",
                            mitigation_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT]
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Brute force detection failed: {e}")
            return []

    async def _detect_data_exfiltration(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Detect data exfiltration attempts"""
        try:
            threats = []
            
            # Group by user
            user_access = defaultdict(list)
            for event in events:
                if event.user_id:
                    user_access[event.user_id].append(event)
            
            # Analyze access patterns
            for user_id, access_events in user_access.items():
                # Check for unusual volume
                total_data_accessed = sum(
                    event.details.get("bytes_accessed", 0) for event in access_events
                )
                
                if total_data_accessed > 1000000000:  # 1GB threshold
                    threat = ThreatEvent(
                        threat_level=ThreatLevel.HIGH,
                        threat_category=ThreatCategory.DATA_EXFILTRATION,
                        confidence_score=0.8,
                        source_events=access_events,
                        affected_users={user_id},
                        affected_resources=set(event.resource for event in access_events if event.resource),
                        attack_vector="Large volume data access",
                        description=f"User {user_id} accessed {total_data_accessed / 1000000:.1f}MB of data",
                        mitigation_actions=[ResponseAction.INCREASE_MONITORING, ResponseAction.ALERT]
                    )
                    threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Data exfiltration detection failed: {e}")
            return []

    async def _detect_privilege_escalation(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Detect privilege escalation attempts"""
        try:
            threats = []
            
            # Look for rapid permission changes
            user_privilege_changes = defaultdict(list)
            for event in events:
                if event.user_id and "permission" in event.details:
                    user_privilege_changes[event.user_id].append(event)
            
            for user_id, privilege_events in user_privilege_changes.items():
                if len(privilege_events) >= 3:  # 3+ privilege changes
                    time_span = max(event.timestamp for event in privilege_events) - min(event.timestamp for event in privilege_events)
                    
                    if time_span.total_seconds() < 3600:  # Within 1 hour
                        threat = ThreatEvent(
                            threat_level=ThreatLevel.MEDIUM,
                            threat_category=ThreatCategory.PRIVILEGE_ESCALATION,
                            confidence_score=0.7,
                            source_events=privilege_events,
                            affected_users={user_id},
                            attack_vector="Rapid privilege changes",
                            description=f"User {user_id} had {len(privilege_events)} privilege changes in {time_span.total_seconds()/60:.0f} minutes",
                            mitigation_actions=[ResponseAction.INCREASE_MONITORING, ResponseAction.ALERT]
                        )
                        threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Privilege escalation detection failed: {e}")
            return []

    async def _detect_anomalies(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Detect general anomalies using ML"""
        try:
            threats = []
            
            if not events or len(events) < 10:  # Need sufficient data
                return threats
            
            # Extract features
            features = []
            for event in events:
                feature_vector = self._extract_event_features(event)
                features.append(feature_vector)
            
            if not features:
                return threats
            
            features_array = np.array(features)
            
            # Use anomaly detection model
            anomaly_model = self.models.get("anomaly_detection")
            if anomaly_model:
                try:
                    # Fit model on current data (in production, use pre-trained model)
                    anomaly_model.fit(features_array)
                    
                    # Detect anomalies
                    anomaly_scores = anomaly_model.decision_function(features_array)
                    outliers = anomaly_model.predict(features_array)
                    
                    # Identify anomalous events
                    anomalous_events = []
                    for i, (event, is_outlier, score) in enumerate(zip(events, outliers, anomaly_scores)):
                        if is_outlier == -1:  # Anomaly detected
                            anomalous_events.append((event, abs(score)))
                    
                    if anomalous_events:
                        # Create threat for anomalies
                        max_score = max(score for _, score in anomalous_events)
                        threat = ThreatEvent(
                            threat_level=ThreatLevel.MEDIUM,
                            threat_category=ThreatCategory.ANOMALOUS_BEHAVIOR,
                            confidence_score=min(0.9, max_score),
                            source_events=[event for event, _ in anomalous_events],
                            attack_vector="Anomalous behavior pattern",
                            description=f"Detected {len(anomalous_events)} anomalous events",
                            mitigation_actions=[ResponseAction.INCREASE_MONITORING, ResponseAction.ALERT]
                        )
                        threats.append(threat)
                        
                except Exception as model_error:
                    logger.error(f"Anomaly model execution failed: {model_error}")
            
            return threats
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []

    def _extract_event_features(self, event: SecurityEvent) -> List[float]:
        """Extract numerical features from security event"""
        try:
            features = []
            
            # Temporal features
            features.append(event.timestamp.hour)  # Hour of day
            features.append(event.timestamp.weekday())  # Day of week
            
            # Success/failure
            features.append(1.0 if event.success else 0.0)
            
            # Event type encoding
            event_type_encoding = {
                EventType.LOGIN_ATTEMPT: 1.0,
                EventType.LOGIN_SUCCESS: 2.0,
                EventType.LOGIN_FAILURE: 3.0,
                EventType.ACCESS_DENIED: 4.0,
                EventType.DATA_ACCESS: 5.0,
                EventType.API_REQUEST: 6.0,
            }
            features.append(event_type_encoding.get(event.event_type, 0.0))
            
            # IP address features (simplified)
            if event.ip_address and event.ip_address != "unknown":
                try:
                    ip_parts = event.ip_address.split('.')
                    if len(ip_parts) == 4:
                        features.extend([float(part) / 255.0 for part in ip_parts])
                    else:
                        features.extend([0.0, 0.0, 0.0, 0.0])
                except:
                    features.extend([0.0, 0.0, 0.0, 0.0])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
            
            # Risk score
            features.append(event.risk_score)
            
            # Details-based features
            features.append(len(event.details))  # Number of detail fields
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return [0.0] * 10  # Return default features

    async def _correlation_analysis(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Perform correlation analysis across different event types"""
        try:
            threats = []
            
            # Time-based correlation window
            correlation_window = timedelta(minutes=30)
            
            # Group events by time windows
            time_groups = defaultdict(list)
            for event in events:
                window_start = event.timestamp.replace(minute=0, second=0, microsecond=0)
                time_groups[window_start].append(event)
            
            # Analyze each time window
            for window_start, window_events in time_groups.items():
                if len(window_events) < 5:  # Need sufficient events
                    continue
                
                # Look for suspicious patterns
                correlation_threats = await self._analyze_correlation_patterns(window_events)
                threats.extend(correlation_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
            return []

    async def _analyze_correlation_patterns(self, events: List[SecurityEvent]) -> List[ThreatEvent]:
        """Analyze correlation patterns in event groups"""
        try:
            threats = []
            
            # Pattern 1: Failed login followed by successful login from different IP
            login_events = [e for e in events if e.event_type in [EventType.LOGIN_ATTEMPT, EventType.LOGIN_SUCCESS, EventType.LOGIN_FAILURE]]
            
            if len(login_events) >= 3:
                # Group by user
                user_logins = defaultdict(list)
                for event in login_events:
                    if event.user_id:
                        user_logins[event.user_id].append(event)
                
                for user_id, user_events in user_logins.items():
                    user_events.sort(key=lambda x: x.timestamp)
                    
                    # Look for failure -> success pattern with IP change
                    for i in range(len(user_events) - 1):
                        current = user_events[i]
                        next_event = user_events[i + 1]
                        
                        if (not current.success and next_event.success and
                            current.ip_address != next_event.ip_address):
                            
                            threat = ThreatEvent(
                                threat_level=ThreatLevel.MEDIUM,
                                threat_category=ThreatCategory.ACCOUNT_TAKEOVER,
                                confidence_score=0.6,
                                source_events=[current, next_event],
                                affected_users={user_id},
                                attack_vector="Failed login followed by success from different IP",
                                description=f"User {user_id} failed login from {current.ip_address} then succeeded from {next_event.ip_address}",
                                mitigation_actions=[ResponseAction.INCREASE_MONITORING, ResponseAction.ALERT]
                            )
                            threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Correlation pattern analysis failed: {e}")
            return []

    # Feature extraction methods
    def _extract_login_features(self, events: List[SecurityEvent]) -> np.ndarray:
        """Extract login pattern features"""
        # Placeholder implementation
        return np.array([])
    
    def _extract_access_features(self, events: List[SecurityEvent]) -> np.ndarray:
        """Extract access pattern features"""
        # Placeholder implementation
        return np.array([])
    
    def _extract_network_features(self, events: List[SecurityEvent]) -> np.ndarray:
        """Extract network pattern features"""
        # Placeholder implementation
        return np.array([])
    
    def _extract_behavioral_features(self, events: List[SecurityEvent]) -> np.ndarray:
        """Extract behavioral pattern features"""
        # Placeholder implementation
        return np.array([])

class ThreatDetector:
    """
    Main threat detection engine coordinating all threat detection components.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize components
        self.threat_intelligence = ThreatIntelligence(redis_url)
        self.ml_analyzer = MLThreatAnalyzer()
        
        # Event processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.active_threats: Dict[str, ThreatEvent] = {}
        self.event_buffer: deque = deque(maxlen=10000)
        
        # Configuration
        self.config = {
            "real_time_processing": True,
            "batch_analysis_interval": 300,  # 5 minutes
            "threat_correlation_window": 1800,  # 30 minutes
            "auto_response_enabled": True,
            "ml_analysis_enabled": True,
            "threat_intelligence_enabled": True,
            "alert_thresholds": {
                ThreatLevel.LOW: 0.3,
                ThreatLevel.MEDIUM: 0.5,
                ThreatLevel.HIGH: 0.7,
                ThreatLevel.CRITICAL: 0.9
            }
        }
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "response_actions_taken": 0,
            "average_detection_time": 0.0
        }

    async def initialize(self) -> None:
        """Initialize threat detection system"""
        try:
            # Initialize Redis connection
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Initialize components
            if self.config["threat_intelligence_enabled"]:
                await self.threat_intelligence.initialize()
            
            if self.config["ml_analysis_enabled"]:
                await self.ml_analyzer.initialize()
            
            # Start background tasks
            if self.config["real_time_processing"]:
                asyncio.create_task(self._event_processor())
            
            asyncio.create_task(self._batch_analyzer())
            asyncio.create_task(self._threat_correlator())
            
            logger.info("Threat detection system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize threat detector: {e}")
            raise

    async def process_event(self, event: SecurityEvent) -> Optional[List[ThreatEvent]]:
        """Process a single security event"""
        try:
            start_time = time.time()
            
            # Add to event buffer
            self.event_buffer.append(event)
            
            # Enrich event with threat intelligence
            if self.config["threat_intelligence_enabled"]:
                await self._enrich_event(event)
            
            # Real-time threat detection
            immediate_threats = await self._immediate_threat_detection(event)
            
            # Update statistics
            self.stats["events_processed"] += 1
            detection_time = (time.time() - start_time) * 1000
            self.stats["average_detection_time"] = (
                self.stats["average_detection_time"] * 0.9 + detection_time * 0.1
            )
            
            # Store event for batch analysis
            await self._store_event(event)
            
            if immediate_threats:
                for threat in immediate_threats:
                    await self._handle_threat(threat)
                return immediate_threats
            
            return None
            
        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            return None

    async def _enrich_event(self, event: SecurityEvent) -> None:
        """Enrich event with threat intelligence"""
        try:
            if event.ip_address and event.ip_address != "unknown":
                # Check IP reputation
                reputation = await self.threat_intelligence.check_ip_reputation(event.ip_address)
                event.risk_score += reputation.get("risk_score", 0.0)
                event.metadata["ip_reputation"] = reputation
            
            # Add geographic information
            if event.ip_address:
                # In production, use IP geolocation service
                event.geographic_location = {"country": "unknown", "city": "unknown"}
            
        except Exception as e:
            logger.error(f"Event enrichment failed: {e}")

    async def _immediate_threat_detection(self, event: SecurityEvent) -> List[ThreatEvent]:
        """Perform immediate threat detection on single event"""
        try:
            threats = []
            
            # High-risk event types
            if event.event_type == EventType.LOGIN_FAILURE and event.risk_score > 0.7:
                threat = ThreatEvent(
                    threat_level=ThreatLevel.MEDIUM,
                    threat_category=ThreatCategory.BRUTE_FORCE,
                    confidence_score=event.risk_score,
                    source_events=[event],
                    attack_vector="High-risk login failure",
                    description=f"High-risk login failure from {event.ip_address}",
                    mitigation_actions=[ResponseAction.INCREASE_MONITORING]
                )
                threats.append(threat)
            
            # Suspicious user agents
            if event.user_agent:
                suspicious_agents = ["bot", "crawler", "scanner", "sqlmap", "nikto"]
                if any(agent in event.user_agent.lower() for agent in suspicious_agents):
                    threat = ThreatEvent(
                        threat_level=ThreatLevel.MEDIUM,
                        threat_category=ThreatCategory.BOT_ACTIVITY,
                        confidence_score=0.6,
                        source_events=[event],
                        attack_vector="Suspicious user agent",
                        description=f"Suspicious user agent detected: {event.user_agent}",
                        mitigation_actions=[ResponseAction.INCREASE_MONITORING]
                    )
                    threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Immediate threat detection failed: {e}")
            return []

    async def _batch_analyzer(self) -> None:
        """Background task for batch threat analysis"""
        try:
            while True:
                await asyncio.sleep(self.config["batch_analysis_interval"])
                
                if not self.config["ml_analysis_enabled"]:
                    continue
                
                # Get recent events for analysis
                recent_events = list(self.event_buffer)
                
                if len(recent_events) < 10:  # Need sufficient data
                    continue
                
                # Perform ML analysis
                ml_threats = await self.ml_analyzer.analyze_events(recent_events)
                
                # Handle detected threats
                for threat in ml_threats:
                    await self._handle_threat(threat)
                
                logger.info(f"Batch analysis completed. Analyzed {len(recent_events)} events, found {len(ml_threats)} threats")
                
        except Exception as e:
            logger.error(f"Batch analyzer failed: {e}")

    async def _threat_correlator(self) -> None:
        """Background task for threat correlation"""
        try:
            while True:
                await asyncio.sleep(600)  # Run every 10 minutes
                
                # Correlate active threats
                await self._correlate_active_threats()
                
                # Age out old threats
                await self._cleanup_old_threats()
                
        except Exception as e:
            logger.error(f"Threat correlator failed: {e}")

    async def _correlate_active_threats(self) -> None:
        """Correlate active threats to identify complex attacks"""
        try:
            if len(self.active_threats) < 2:
                return
            
            # Look for related threats
            for threat_id1, threat1 in self.active_threats.items():
                for threat_id2, threat2 in self.active_threats.items():
                    if threat_id1 >= threat_id2:  # Avoid duplicate pairs
                        continue
                    
                    # Check for overlapping users or resources
                    if (threat1.affected_users & threat2.affected_users or
                        threat1.affected_resources & threat2.affected_resources):
                        
                        # Create correlated threat
                        correlated_threat = ThreatEvent(
                            threat_level=max(threat1.threat_level, threat2.threat_level),
                            threat_category=ThreatCategory.SUSPICIOUS_NETWORK,
                            confidence_score=(threat1.confidence_score + threat2.confidence_score) / 2,
                            source_events=threat1.source_events + threat2.source_events,
                            affected_users=threat1.affected_users | threat2.affected_users,
                            affected_resources=threat1.affected_resources | threat2.affected_resources,
                            attack_vector="Correlated threat activity",
                            description=f"Correlated threats: {threat1.threat_category.value} and {threat2.threat_category.value}",
                            mitigation_actions=[ResponseAction.ESCALATE, ResponseAction.ALERT]
                        )
                        
                        await self._handle_threat(correlated_threat)
                        
        except Exception as e:
            logger.error(f"Threat correlation failed: {e}")

    async def _cleanup_old_threats(self) -> None:
        """Clean up old resolved threats"""
        try:
            current_time = datetime.now(timezone.utc)
            old_threats = []
            
            for threat_id, threat in self.active_threats.items():
                age = (current_time - threat.detected_at).total_seconds()
                
                if age > 3600 and threat.status == "resolved":  # 1 hour old and resolved
                    old_threats.append(threat_id)
            
            for threat_id in old_threats:
                del self.active_threats[threat_id]
                
            if old_threats:
                logger.info(f"Cleaned up {len(old_threats)} old threats")
                
        except Exception as e:
            logger.error(f"Threat cleanup failed: {e}")

    async def _handle_threat(self, threat: ThreatEvent) -> None:
        """Handle detected threat"""
        try:
            # Add to active threats
            self.active_threats[threat.threat_id] = threat
            
            # Update statistics
            self.stats["threats_detected"] += 1
            
            # Store threat
            await self._store_threat(threat)
            
            # Create alert
            alert = SecurityAlert(
                threat_event=threat,
                alert_level=threat.threat_level,
                message=threat.description,
                channels=["email", "slack"] if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] else ["email"]
            )
            
            await self._send_alert(alert)
            
            # Execute automated response actions
            if self.config["auto_response_enabled"]:
                await self._execute_response_actions(threat)
            
            logger.warning(f"Threat detected: {threat.threat_category.value} - {threat.description}")
            
        except Exception as e:
            logger.error(f"Threat handling failed: {e}")

    async def _execute_response_actions(self, threat: ThreatEvent) -> None:
        """Execute automated response actions"""
        try:
            for action in threat.mitigation_actions:
                if action == ResponseAction.BLOCK_IP:
                    await self._block_ip_addresses(threat)
                elif action == ResponseAction.SUSPEND_USER:
                    await self._suspend_users(threat)
                elif action == ResponseAction.FORCE_LOGOUT:
                    await self._force_logout_users(threat)
                elif action == ResponseAction.INCREASE_MONITORING:
                    await self._increase_monitoring(threat)
                elif action == ResponseAction.QUARANTINE:
                    await self._quarantine_resources(threat)
                
                self.stats["response_actions_taken"] += 1
                
        except Exception as e:
            logger.error(f"Response action execution failed: {e}")

    async def _block_ip_addresses(self, threat: ThreatEvent) -> None:
        """Block IP addresses associated with threat"""
        try:
            ip_addresses = set()
            for event in threat.source_events:
                if event.ip_address and event.ip_address != "unknown":
                    ip_addresses.add(event.ip_address)
            
            for ip_address in ip_addresses:
                # Add to blocked IPs list
                await self.redis.setex(f"blocked_ip:{ip_address}", 3600, "threat_response")
                logger.info(f"Blocked IP address: {ip_address}")
                
        except Exception as e:
            logger.error(f"IP blocking failed: {e}")

    async def _suspend_users(self, threat: ThreatEvent) -> None:
        """Suspend users associated with threat"""
        try:
            for user_id in threat.affected_users:
                # Add to suspended users list
                await self.redis.setex(f"suspended_user:{user_id}", 3600, "threat_response")
                logger.info(f"Suspended user: {user_id}")
                
        except Exception as e:
            logger.error(f"User suspension failed: {e}")

    async def _force_logout_users(self, threat: ThreatEvent) -> None:
        """Force logout users associated with threat"""
        try:
            for user_id in threat.affected_users:
                # Add to force logout list
                await self.redis.setex(f"force_logout:{user_id}", 300, "threat_response")
                logger.info(f"Forced logout for user: {user_id}")
                
        except Exception as e:
            logger.error(f"Force logout failed: {e}")

    async def _increase_monitoring(self, threat: ThreatEvent) -> None:
        """Increase monitoring for threat-related entities"""
        try:
            # Increase monitoring for affected users
            for user_id in threat.affected_users:
                await self.redis.setex(f"enhanced_monitoring:{user_id}", 7200, "threat_response")
            
            # Increase monitoring for source IPs
            for event in threat.source_events:
                if event.ip_address:
                    await self.redis.setex(f"enhanced_monitoring_ip:{event.ip_address}", 7200, "threat_response")
                    
        except Exception as e:
            logger.error(f"Enhanced monitoring setup failed: {e}")

    async def _quarantine_resources(self, threat: ThreatEvent) -> None:
        """Quarantine resources associated with threat"""
        try:
            for resource in threat.affected_resources:
                await self.redis.setex(f"quarantined_resource:{resource}", 3600, "threat_response")
                logger.info(f"Quarantined resource: {resource}")
                
        except Exception as e:
            logger.error(f"Resource quarantine failed: {e}")

    async def _send_alert(self, alert: SecurityAlert) -> None:
        """Send security alert"""
        try:
            # Store alert
            alert_data = {
                "alert_id": alert.alert_id,
                "threat_id": alert.threat_event.threat_id,
                "alert_level": alert.alert_level.value,
                "message": alert.message,
                "channels": alert.channels,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.redis.setex(
                f"security_alert:{alert.alert_id}",
                86400 * 7,  # Keep for 7 days
                json.dumps(alert_data, default=str)
            )
            
            # In production, integrate with actual notification systems
            logger.warning(f"SECURITY ALERT: {alert.message}")
            
        except Exception as e:
            logger.error(f"Alert sending failed: {e}")

    async def _store_event(self, event: SecurityEvent) -> None:
        """Store security event for analysis"""
        try:
            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "resource": event.resource,
                "action": event.action,
                "success": event.success,
                "details": event.details,
                "timestamp": event.timestamp.isoformat(),
                "geographic_location": event.geographic_location,
                "risk_score": event.risk_score,
                "metadata": event.metadata
            }
            
            await self.redis.setex(
                f"security_event:{event.event_id}",
                86400 * 30,  # Keep for 30 days
                json.dumps(event_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Event storage failed: {e}")

    async def _store_threat(self, threat: ThreatEvent) -> None:
        """Store threat event"""
        try:
            threat_data = {
                "threat_id": threat.threat_id,
                "threat_level": threat.threat_level.value,
                "threat_category": threat.threat_category.value,
                "confidence_score": threat.confidence_score,
                "affected_users": list(threat.affected_users),
                "affected_resources": list(threat.affected_resources),
                "attack_vector": threat.attack_vector,
                "impact_assessment": threat.impact_assessment,
                "mitigation_actions": [action.value for action in threat.mitigation_actions],
                "detected_at": threat.detected_at.isoformat(),
                "status": threat.status,
                "description": threat.description,
                "metadata": threat.metadata
            }
            
            await self.redis.setex(
                f"threat_event:{threat.threat_id}",
                86400 * 90,  # Keep for 90 days
                json.dumps(threat_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Threat storage failed: {e}")

    async def _event_processor(self) -> None:
        """Background event processor for real-time analysis"""
        try:
            while True:
                try:
                    # Wait for events in the queue
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                    await self.process_event(event)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Event processing error: {e}")
                    
        except Exception as e:
            logger.error(f"Event processor failed: {e}")

    async def queue_event(self, event: SecurityEvent) -> None:
        """Queue event for processing"""
        try:
            await self.event_queue.put(event)
        except Exception as e:
            logger.error(f"Event queueing failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        return {
            "events_processed": self.stats["events_processed"],
            "threats_detected": self.stats["threats_detected"],
            "active_threats": len(self.active_threats),
            "false_positives": self.stats["false_positives"],
            "response_actions_taken": self.stats["response_actions_taken"],
            "average_detection_time_ms": self.stats["average_detection_time"],
            "threat_detection_rate": (
                self.stats["threats_detected"] / max(1, self.stats["events_processed"])
            ),
            "queue_size": self.event_queue.qsize(),
            "buffer_size": len(self.event_buffer)
        }

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()
        await self.threat_intelligence.cleanup()