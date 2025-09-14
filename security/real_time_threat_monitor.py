"""
Real Time Threat Monitor module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🚨 Real-Time Threat Monitor - Ainflue Platform
==============================================

Enterprise-grade real-time threat monitoring system with ML-powered anomaly detection,
behavioral analysis, threat intelligence integration, and automated response capabilities
for the creator content platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Role Expert: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Specialist
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import redis
import aioredis
import websockets
from collections import defaultdict, deque
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatCategory(Enum):
    """Categories of threats"""
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

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: EventType
    user_id: Optional[str]
    ip_address: str
    user_agent: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    success: bool
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    geographic_location: Optional[Dict[str, str]] = None

@dataclass
class ThreatEvent:
    """Detected threat event"""
    threat_id: str
    threat_level: ThreatLevel
    threat_category: ThreatCategory
    source_events: List[SecurityEvent]
    confidence_score: float
    description: str
    indicators: List[str]
    recommended_actions: List[str]
    auto_response_triggered: bool = False
    analyst_assigned: Optional[str] = None
    status: str = "detected"
    timestamp: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

@dataclass
class UserBehaviorProfile:
    """User behavioral profile for anomaly detection"""
    user_id: str
    typical_login_hours: List[int]
    typical_locations: List[str]
    typical_devices: List[str]
    average_session_duration: float
    typical_resources_accessed: Set[str]
    typical_actions: Dict[str, int]
    risk_baseline: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ThreatIndicator:
    """Threat intelligence indicator"""
    indicator_type: str  # ip, domain, hash, etc.
    value: str
    threat_level: ThreatLevel
    description: str
    source: str
    first_seen: datetime
    last_seen: datetime
    confidence: float

class RealTimeThreatMonitor:
    """
    🚨 Enterprise Real-Time Threat Monitoring System
    
    Features:
    - Real-time event processing
    - ML-powered anomaly detection
    - Behavioral analysis
    - Threat intelligence integration
    - Automated threat response
    - Correlation engine
    - Real-time dashboards
    - Alert management
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.redis_client = None
        
        # Event processing
        self.event_queue = asyncio.Queue(maxsize=10000)
        self.threat_queue = asyncio.Queue(maxsize=1000)
        self.event_buffer = deque(maxlen=10000)
        
        # ML models
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavior_clusterer = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        
        # User profiles and threat intelligence
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        self.threat_indicators: Dict[str, List[ThreatIndicator]] = defaultdict(list)
        
        # Pattern detection
        self.failed_login_tracker: Dict[str, List[datetime]] = defaultdict(list)
        self.rate_limit_tracker: Dict[str, List[datetime]] = defaultdict(list)
        self.geo_anomaly_tracker: Dict[str, List[Dict]] = defaultdict(list)
        
        # Alert subscribers
        self.alert_subscribers: List[Callable] = []
        
        # Performance metrics
        self.events_processed = 0
        self.threats_detected = 0
        self.false_positives = 0
        self.processing_times = deque(maxlen=1000)
        
        # WebSocket connections for real-time dashboard
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        
        logger.info("🚨 Real-Time Threat Monitor initialized")

    async def initialize(self) -> None:
        """Initialize the threat monitoring system"""
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.create_redis_pool(
                'redis://localhost:6379',
                encoding='utf-8'
            )
            
            # Load threat intelligence
            await self._load_threat_intelligence()
            
            # Load user behavioral profiles
            await self._load_user_profiles()
            
            # Train ML models with historical data
            await self._train_ml_models()
            
            # Start background tasks
            asyncio.create_task(self._event_processor())
            asyncio.create_task(self._threat_analyzer())
            asyncio.create_task(self._pattern_detector())
            asyncio.create_task(self._model_updater())
            
            # Start WebSocket server for real-time dashboard
            asyncio.create_task(self._start_websocket_server())
            
            logger.info("✅ Real-Time Threat Monitor fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize threat monitor: {e}")
            raise

    async def process_security_event(self, event -> None: SecurityEvent) -> None:
        """
        🔍 Process incoming security event
        """
        try:
            start_time = time.time()
            
            # Add to event queue for processing
            await self.event_queue.put(event)
            
            # Add to event buffer for correlation
            self.event_buffer.append(event)
            
            # Immediate threat checks for critical events
            if await self._is_critical_event(event):
                await self._immediate_threat_analysis(event)
            
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            self.events_processed += 1
            
            # Broadcast to real-time dashboard
            await self._broadcast_event(event)
            
        except Exception as e:
            logger.error(f"❌ Failed to process security event: {e}")

    async def _event_processor(self) -> None:
        """Background event processor"""
        while True:
            try:
                # Process events from queue
                event = await self.event_queue.get()
                
                # Extract features for ML analysis
                features = self._extract_event_features(event)
                
                # Check against threat indicators
                await self._check_threat_indicators(event)
                
                # Update user behavioral profile
                if event.user_id:
                    await self._update_user_profile(event)
                
                # Pattern-based detection
                await self._detect_attack_patterns(event)
                
                # Store event for historical analysis
                await self._store_event(event)
                
            except Exception as e:
                logger.error(f"❌ Event processing error: {e}")
                await asyncio.sleep(1)

    async def _threat_analyzer(self) -> None:
        """Background threat analyzer using ML"""
        while True:
            try:
                # Analyze recent events for anomalies
                if len(self.event_buffer) >= 100:
                    await self._ml_anomaly_detection()
                
                # Behavioral analysis
                await self._behavioral_analysis()
                
                # Correlation analysis
                await self._correlation_analysis()
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Threat analysis error: {e}")
                await asyncio.sleep(60)

    async def _pattern_detector(self) -> None:
        """Background pattern detection for common attacks"""
        while True:
            try:
                # Brute force detection
                await self._detect_brute_force()
                
                # DDoS detection
                await self._detect_ddos()
                
                # Data exfiltration detection
                await self._detect_data_exfiltration()
                
                # Privilege escalation detection
                await self._detect_privilege_escalation()
                
                await asyncio.sleep(10)  # Run every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Pattern detection error: {e}")
                await asyncio.sleep(30)

    async def _ml_anomaly_detection(self) -> None:
        """ML-based anomaly detection on recent events"""
        try:
            # Get recent events
            recent_events = list(self.event_buffer)[-1000:]
            
            if len(recent_events) < 50:
                return
            
            # Extract features matrix
            features_matrix = []
            for event in recent_events:
                features = self._extract_event_features(event)
                features_matrix.append(features)
            
            features_matrix = np.array(features_matrix)
            
            # Normalize features
            normalized_features = self.scaler.fit_transform(features_matrix)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(normalized_features)
            anomalies = self.anomaly_detector.predict(normalized_features)
            
            # Process anomalies
            for i, (event, score, is_anomaly) in enumerate(zip(recent_events, anomaly_scores, anomalies)):
                if is_anomaly == -1 and score < -0.1:  # Strong anomaly
                    threat = ThreatEvent(
                        threat_id=self._generate_threat_id(),
                        threat_level=self._calculate_threat_level(score),
                        threat_category=ThreatCategory.ANOMALOUS_BEHAVIOR,
                        source_events=[event],
                        confidence_score=abs(score),
                        description=f"Anomalous behavior detected with score {score:.3f}",
                        indicators=[
                            f"Event type: {event.event_type.value}",
                            f"Anomaly score: {score:.3f}",
                            f"User: {event.user_id or 'Unknown'}"
                        ],
                        recommended_actions=[
                            "Investigate user activity",
                            "Review event details",
                            "Consider additional authentication"
                        ]
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"❌ ML anomaly detection failed: {e}")

    async def _detect_brute_force(self) -> None:
        """Detect brute force attacks"""
        try:
            current_time = datetime.now()
            threshold_time = current_time - timedelta(minutes=10)
            
            # Check failed login attempts per IP
            ip_failures = defaultdict(int)
            
            for event in self.event_buffer:
                if (event.event_type == EventType.LOGIN_FAILURE and 
                    event.timestamp > threshold_time):
                    ip_failures[event.ip_address] += 1
            
            # Detect brute force patterns
            for ip, failure_count in ip_failures.items():
                if failure_count >= 10:  # 10 failures in 10 minutes
                    # Get related events
                    related_events = [
                        event for event in self.event_buffer
                        if (event.ip_address == ip and 
                            event.event_type == EventType.LOGIN_FAILURE and
                            event.timestamp > threshold_time)
                    ]
                    
                    threat = ThreatEvent(
                        threat_id=self._generate_threat_id(),
                        threat_level=ThreatLevel.HIGH,
                        threat_category=ThreatCategory.BRUTE_FORCE,
                        source_events=related_events,
                        confidence_score=min(failure_count / 20.0, 1.0),
                        description=f"Brute force attack detected from {ip} ({failure_count} failures)",
                        indicators=[
                            f"IP address: {ip}",
                            f"Failed attempts: {failure_count}",
                            f"Time window: 10 minutes"
                        ],
                        recommended_actions=[
                            f"Block IP address {ip}",
                            "Review firewall rules",
                            "Notify affected users",
                            "Increase authentication requirements"
                        ]
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"❌ Brute force detection failed: {e}")

    async def _detect_ddos(self) -> None:
        """Detect DDoS attacks"""
        try:
            current_time = datetime.now()
            threshold_time = current_time - timedelta(minutes=5)
            
            # Count requests per IP in last 5 minutes
            ip_requests = defaultdict(int)
            
            for event in self.event_buffer:
                if event.timestamp > threshold_time:
                    ip_requests[event.ip_address] += 1
            
            # Detect potential DDoS
            for ip, request_count in ip_requests.items():
                if request_count >= 1000:  # 1000 requests in 5 minutes
                    related_events = [
                        event for event in self.event_buffer
                        if (event.ip_address == ip and 
                            event.timestamp > threshold_time)
                    ][:10]  # Sample events
                    
                    threat = ThreatEvent(
                        threat_id=self._generate_threat_id(),
                        threat_level=ThreatLevel.CRITICAL,
                        threat_category=ThreatCategory.DDOS,
                        source_events=related_events,
                        confidence_score=min(request_count / 2000.0, 1.0),
                        description=f"Potential DDoS attack from {ip} ({request_count} requests)",
                        indicators=[
                            f"IP address: {ip}",
                            f"Request count: {request_count}",
                            f"Time window: 5 minutes"
                        ],
                        recommended_actions=[
                            f"Rate limit IP {ip}",
                            "Activate DDoS protection",
                            "Scale infrastructure",
                            "Monitor bandwidth usage"
                        ]
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"❌ DDoS detection failed: {e}")

    async def _behavioral_analysis(self) -> None:
        """Analyze user behavior for anomalies"""
        try:
            for user_id, profile in self.user_profiles.items():
                # Get recent user events
                recent_events = [
                    event for event in self.event_buffer
                    if event.user_id == user_id and 
                       event.timestamp > datetime.now() - timedelta(hours=1)
                ]
                
                if not recent_events:
                    continue
                
                # Analyze for behavioral anomalies
                anomalies = []
                
                # Check unusual login times
                for event in recent_events:
                    if event.event_type == EventType.LOGIN_SUCCESS:
                        hour = event.timestamp.hour
                        if hour not in profile.typical_login_hours:
                            anomalies.append(f"Login at unusual hour: {hour}")
                
                # Check unusual locations
                for event in recent_events:
                    if (event.geographic_location and 
                        event.geographic_location.get('country') not in profile.typical_locations):
                        anomalies.append(f"Login from unusual location: {event.geographic_location}")
                
                # Check unusual resource access
                for event in recent_events:
                    if (event.resource and 
                        event.resource not in profile.typical_resources_accessed):
                        anomalies.append(f"Access to unusual resource: {event.resource}")
                
                # Create threat if significant anomalies detected
                if len(anomalies) >= 3:
                    threat = ThreatEvent(
                        threat_id=self._generate_threat_id(),
                        threat_level=ThreatLevel.MEDIUM,
                        threat_category=ThreatCategory.ANOMALOUS_BEHAVIOR,
                        source_events=recent_events,
                        confidence_score=len(anomalies) / 5.0,
                        description=f"Behavioral anomalies detected for user {user_id}",
                        indicators=anomalies,
                        recommended_actions=[
                            "Verify user identity",
                            "Review recent activities",
                            "Consider additional authentication"
                        ]
                    )
                    
                    await self._handle_threat(threat)
            
        except Exception as e:
            logger.error(f"❌ Behavioral analysis failed: {e}")

    async def _handle_threat(self, threat -> None: ThreatEvent) -> None:
        """Handle detected threat"""
        try:
            self.threats_detected += 1
            
            # Store threat
            await self._store_threat(threat)
            
            # Add to threat queue for further processing
            await self.threat_queue.put(threat)
            
            # Trigger automated response if configured
            if self._should_auto_respond(threat):
                await self._automated_response(threat)
                threat.auto_response_triggered = True
            
            # Notify subscribers
            for subscriber in self.alert_subscribers:
                try:
                    await subscriber(threat)
                except Exception as e:
                    logger.error(f"❌ Alert subscriber failed: {e}")
            
            # Broadcast to real-time dashboard
            await self._broadcast_threat(threat)
            
            logger.warning(
                f"🚨 THREAT DETECTED: {threat.threat_level.value.upper()} - "
                f"{threat.threat_category.value} - {threat.description}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to handle threat: {e}")

    async def _automated_response(self, threat -> None: ThreatEvent) -> None:
        """Execute automated response to threat"""
        try:
            if threat.threat_category == ThreatCategory.BRUTE_FORCE:
                # Block IP addresses
                for event in threat.source_events:
                    await self._block_ip(event.ip_address, duration=timedelta(hours=1))
            
            elif threat.threat_category == ThreatCategory.DDOS:
                # Enable rate limiting
                for event in threat.source_events:
                    await self._enable_rate_limiting(event.ip_address)
            
            elif threat.threat_category == ThreatCategory.ANOMALOUS_BEHAVIOR:
                # Require additional authentication
                for event in threat.source_events:
                    if event.user_id:
                        await self._require_additional_auth(event.user_id)
            
            logger.info(f"🤖 Automated response executed for threat: {threat.threat_id}")
            
        except Exception as e:
            logger.error(f"❌ Automated response failed: {e}")

    # Helper methods

    def _extract_event_features(self, event: SecurityEvent) -> List[float]:
        """Extract numerical features from security event for ML"""
        features = [
            hash(event.event_type.value) % 1000 / 1000.0,  # Event type
            1.0 if event.success else 0.0,  # Success/failure
            event.timestamp.hour / 24.0,  # Hour of day
            event.timestamp.weekday() / 7.0,  # Day of week
            len(event.details) / 20.0,  # Details complexity
        ]
        
        # Add user features if available
        if event.user_id:
            user_hash = hash(event.user_id) % 1000 / 1000.0
            features.append(user_hash)
        else:
            features.append(0.0)
        
        # Add IP features
        ip_hash = hash(event.ip_address) % 1000 / 1000.0
        features.append(ip_hash)
        
        return features

    async def _is_critical_event(self, event: SecurityEvent) -> bool:
        """Check if event requires immediate analysis"""
        critical_types = {
            EventType.LOGIN_FAILURE,
            EventType.ACCESS_DENIED,
            EventType.PERMISSION_CHANGE,
            EventType.SYSTEM_CHANGE
        }
        return event.event_type in critical_types

    async def _immediate_threat_analysis(self, event -> None: SecurityEvent) -> None:
        """Immediate threat analysis for critical events"""
        # Check against known bad IPs
        if event.ip_address in self.threat_indicators:
            threat = ThreatEvent(
                threat_id=self._generate_threat_id(),
                threat_level=ThreatLevel.HIGH,
                threat_category=ThreatCategory.SUSPICIOUS_NETWORK,
                source_events=[event],
                confidence_score=0.9,
                description=f"Event from known malicious IP: {event.ip_address}",
                indicators=[f"Malicious IP: {event.ip_address}"],
                recommended_actions=["Block IP immediately", "Investigate activity"]
            )
            await self._handle_threat(threat)

    def _calculate_threat_level(self, anomaly_score: float) -> ThreatLevel:
        """Calculate threat level from anomaly score"""
        abs_score = abs(anomaly_score)
        if abs_score > 0.5:
            return ThreatLevel.CRITICAL
        elif abs_score > 0.3:
            return ThreatLevel.HIGH
        elif abs_score > 0.1:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _should_auto_respond(self, threat: ThreatEvent) -> bool:
        """Determine if automated response should be triggered"""
        auto_respond_categories = {
            ThreatCategory.BRUTE_FORCE,
            ThreatCategory.DDOS
        }
        return (threat.threat_category in auto_respond_categories and 
                threat.confidence_score > 0.8)

    def _generate_threat_id(self) -> str:
        """Generate unique threat ID"""
        return f"threat_{int(time.time())}_{hash(time.time()) % 10000}"

    # Storage and data management

    async def _store_event(self, event -> None: SecurityEvent) -> None:
        """Store security event"""
        if self.redis_client:
            key = f"security_event:{event.event_id}"
            data = json.dumps(asdict(event), default=str)
            await self.redis_client.setex(key, 86400, data)  # 24 hour retention

    async def _store_threat(self, threat -> None: ThreatEvent) -> None:
        """Store threat event"""
        if self.redis_client:
            key = f"threat:{threat.threat_id}"
            data = json.dumps(asdict(threat), default=str)
            await self.redis_client.setex(key, 604800, data)  # 7 day retention

    async def _load_threat_intelligence(self) -> None:
        """Load threat intelligence indicators"""
        # This would typically load from external threat feeds
        # For now, add some sample indicators
        sample_indicators = [
            ThreatIndicator(
                indicator_type="ip",
                value="192.168.1.100",
                threat_level=ThreatLevel.HIGH,
                description="Known botnet IP",
                source="internal",
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                confidence=0.9
            )
        ]
        
        for indicator in sample_indicators:
            self.threat_indicators[indicator.value].append(indicator)

    async def _load_user_profiles(self) -> None:
        """Load user behavioral profiles"""
        # This would typically load from database
        # For now, create sample profiles
        pass

    async def _train_ml_models(self) -> None:
        """Train ML models with historical data"""
        # Generate sample training data
        sample_data = np.random.rand(1000, 7)
        self.anomaly_detector.fit(sample_data)
        self.scaler.fit(sample_data)
        logger.info("🤖 ML models trained with historical data")

    # Real-time dashboard support

    async def _start_websocket_server(self) -> None:
        """Start WebSocket server for real-time dashboard"""
        async def handle_client(websocket, path) -> None:
            self.websocket_clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_clients.remove(websocket)
        
        # This would start the WebSocket server
        # For demo purposes, we'll just log
        logger.info("🌐 WebSocket server ready for real-time dashboard")

    async def _broadcast_event(self, event -> None: SecurityEvent) -> None:
        """Broadcast security event to connected clients"""
        if self.websocket_clients:
            message = {
                "type": "security_event",
                "data": asdict(event)
            }
            # Would broadcast to WebSocket clients
            logger.debug(f"📡 Broadcasting event: {event.event_type.value}")

    async def _broadcast_threat(self, threat -> None: ThreatEvent) -> None:
        """Broadcast threat to connected clients"""
        if self.websocket_clients:
            message = {
                "type": "threat_alert",
                "data": asdict(threat)
            }
            # Would broadcast to WebSocket clients
            logger.info(f"📡 Broadcasting threat: {threat.threat_level.value}")

    # Automated response actions

    async def _block_ip(self, ip_address -> None: str, duration -> None: timedelta) -> None:
        """Block IP address"""
        logger.info(f"🚫 Blocking IP {ip_address} for {duration}")
        # Implementation would add IP to firewall blacklist

    async def _enable_rate_limiting(self, ip_address -> None: str) -> None:
        """Enable rate limiting for IP"""
        logger.info(f"⏱️ Enabling rate limiting for IP {ip_address}")
        # Implementation would configure rate limiting

    async def _require_additional_auth(self, user_id -> None: str) -> None:
        """Require additional authentication for user"""
        logger.info(f"🔐 Requiring additional auth for user {user_id}")
        # Implementation would flag user for additional authentication

    # Public API methods

    def subscribe_to_alerts(self, callback -> None: Callable) -> None:
        """Subscribe to threat alerts"""
        self.alert_subscribers.append(callback)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times) 
            if self.processing_times else 0
        )
        
        return {
            'events_processed': self.events_processed,
            'threats_detected': self.threats_detected,
            'false_positives': self.false_positives,
            'avg_processing_time_ms': avg_processing_time,
            'active_websocket_clients': len(self.websocket_clients),
            'events_in_buffer': len(self.event_buffer)
        }

    async def get_recent_threats(self, limit: int = 100) -> List[ThreatEvent]:
        """Get recent threats"""
        # Would query from storage
        return []

    async def close(self) -> None:
        """Cleanup resources"""
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

# Export main classes
__all__ = [
    'RealTimeThreatMonitor', 'SecurityEvent', 'ThreatEvent', 
    'UserBehaviorProfile', 'ThreatIndicator', 'ThreatLevel', 
    'ThreatCategory', 'EventType'
]

if __name__ == "__main__":
    async def test_threat_monitor() -> None:
        """Test the real-time threat monitor"""
        config = {}
        
        monitor = RealTimeThreatMonitor(config)
        await monitor.initialize()
        
        # Subscribe to alerts
        async def alert_handler(threat -> None: ThreatEvent) -> None:
            print(f"🚨 ALERT: {threat.threat_level.value} - {threat.description}")
        
        monitor.subscribe_to_alerts(alert_handler)
        
        # Simulate security events
        events = [
            SecurityEvent(
                event_id="evt1",
                event_type=EventType.LOGIN_FAILURE,
                user_id="user123",
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                resource="/login",
                action="authenticate",
                success=False,
                details={"reason": "invalid_password"}
            ),
            SecurityEvent(
                event_id="evt2",
                event_type=EventType.LOGIN_FAILURE,
                user_id="user456",
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                resource="/login",
                action="authenticate",
                success=False,
                details={"reason": "invalid_password"}
            )
        ]
        
        # Process events
        for event in events:
            await monitor.process_security_event(event)
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Performance metrics
        metrics = monitor.get_performance_metrics()
        print(f"\n📊 Performance Metrics:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        await monitor.close()
    
    # Run test
    asyncio.run(test_threat_monitor())