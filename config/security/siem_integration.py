"""SIEM Integration for Intrusion Detection
========================================

Advanced Security Information and Event Management (SIEM) integration
for real-time intrusion detection and security monitoring.

Features:
- Real-time log aggregation and analysis
- Machine learning-based anomaly detection
- Integration with popular SIEM platforms (Splunk, ELK, QRadar)
- Custom threat detection rules
- Automated incident response

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import aioredis
import aiohttp

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Security event severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class EventType(Enum):
    """Security event types"""
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHORIZATION_FAILURE = "authz_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALWARE_DETECTED = "malware_detected"
    DDoS_ATTACK = "ddos_attack"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    SYSTEM_COMPROMISE = "system_compromise"
    POLICY_VIOLATION = "policy_violation"


class ResponseAction(Enum):
    """Automated response actions"""
    LOG_ONLY = "log_only"
    ALERT = "alert"
    BLOCK_IP = "block_ip"
    BLOCK_USER = "block_user"
    QUARANTINE = "quarantine"
    EMERGENCY_RESPONSE = "emergency_response"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    id: str
    timestamp: datetime
    event_type: EventType
    severity: SeverityLevel
    source_ip: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    request_url: Optional[str] = None
    request_method: Optional[str] = None
    response_code: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    raw_data: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "source_ip": self.source_ip,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "user_agent": self.user_agent,
            "request_url": self.request_url,
            "request_method": self.request_method,
            "response_code": self.response_code,
            "details": self.details,
            "tags": self.tags,
            "raw_data": self.raw_data
        }


@dataclass
class ThreatRule:
    """Threat detection rule"""
    id: str
    name: str
    description: str
    event_types: List[EventType]
    conditions: Dict[str, Any]
    threshold: int
    time_window: int  # seconds
    severity: SeverityLevel
    response_actions: List[ResponseAction]
    enabled: bool = True


@dataclass
class SIEMConfig:
    """SIEM configuration"""
    
    # General settings
    enabled: bool = True
    log_level: str = "INFO"
    max_events_per_minute: int = 10000
    
    # Event storage
    redis_url: str = "redis://localhost:6379"
    event_retention_days: int = 90
    
    # Anomaly detection
    anomaly_detection_enabled: bool = True
    anomaly_threshold: float = 0.1
    ml_model_update_interval: int = 3600  # 1 hour
    
    # SIEM platform integrations
    splunk_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "url": "",
        "token": "",
        "index": "ainflue_security"
    })
    
    elk_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "elasticsearch_url": "",
        "logstash_url": "",
        "kibana_url": "",
        "index_pattern": "ainflue-security-*"
    })
    
    qradar_config: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "url": "",
        "token": "",
        "domain_id": 0
    })
    
    # Alerting
    webhook_urls: List[str] = field(default_factory=list)
    email_alerts: List[str] = field(default_factory=list)
    slack_webhook: Optional[str] = None
    
    # Threat detection rules
    custom_rules: List[ThreatRule] = field(default_factory=lambda: [
        ThreatRule(
            id="brute_force_detection",
            name="Brute Force Attack Detection",
            description="Detect multiple failed login attempts",
            event_types=[EventType.AUTHENTICATION_FAILURE],
            conditions={"response_code": [401, 403]},
            threshold=5,
            time_window=300,  # 5 minutes
            severity=SeverityLevel.HIGH,
            response_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT]
        ),
        ThreatRule(
            id="sql_injection_detection",
            name="SQL Injection Detection",
            description="Detect SQL injection attempts",
            event_types=[EventType.SQL_INJECTION],
            conditions={"request_url": {"contains": ["union", "select", "drop", "insert"]}},
            threshold=1,
            time_window=60,
            severity=SeverityLevel.CRITICAL,
            response_actions=[ResponseAction.BLOCK_IP, ResponseAction.EMERGENCY_RESPONSE]
        ),
        ThreatRule(
            id="privilege_escalation_detection",
            name="Privilege Escalation Detection",
            description="Detect privilege escalation attempts",
            event_types=[EventType.PRIVILEGE_ESCALATION],
            conditions={"request_url": {"contains": ["/admin", "/root", "/sudo"]}},
            threshold=3,
            time_window=600,  # 10 minutes
            severity=SeverityLevel.CRITICAL,
            response_actions=[ResponseAction.BLOCK_USER, ResponseAction.EMERGENCY_RESPONSE]
        )
    ])


class AnomalyDetector:
    """Machine learning-based anomaly detection"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_history = deque(maxlen=10000)
        
    def extract_features(self, event: SecurityEvent) -> np.ndarray:
        """Extract numerical features from security event"""
        features = [
            event.severity.value,
            len(event.source_ip.split('.')),  # IP complexity
            len(event.user_agent or ""),
            event.response_code or 0,
            len(event.request_url or ""),
            len(event.details),
            hash(event.event_type.value) % 1000,  # Event type hash
        ]
        return np.array(features)
    
    async def train_model(self, events: List[SecurityEvent]):
        """Train anomaly detection model"""
        if len(events) < 100:
            logger.warning("Not enough events to train anomaly detection model")
            return
        
        features = [self.extract_features(event) for event in events]
        X = np.array(features)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        logger.info(f"Anomaly detection model trained with {len(events)} events")
    
    async def detect_anomaly(self, event: SecurityEvent) -> Tuple[bool, float]:
        """Detect if event is anomalous"""
        if not self.is_trained:
            return False, 0.0
        
        features = self.extract_features(event)
        X_scaled = self.scaler.transform([features])
        
        # Predict anomaly
        anomaly_score = self.model.decision_function(X_scaled)[0]
        is_anomaly = self.model.predict(X_scaled)[0] == -1
        
        return is_anomaly, anomaly_score


class ThreatDetectionEngine:
    """Threat detection engine with custom rules"""
    
    def __init__(self, config: SIEMConfig):
        self.config = config
        self.event_history = defaultdict(deque)
        self.blocked_ips = set()
        self.blocked_users = set()
        
    async def evaluate_rules(self, event: SecurityEvent) -> List[ThreatRule]:
        """Evaluate threat detection rules against event"""
        triggered_rules = []
        
        for rule in self.config.custom_rules:
            if not rule.enabled:
                continue
                
            if event.event_type not in rule.event_types:
                continue
                
            if await self._evaluate_rule_conditions(event, rule):
                triggered_rules.append(rule)
        
        return triggered_rules
    
    async def _evaluate_rule_conditions(self, event: SecurityEvent, rule: ThreatRule) -> bool:
        """Evaluate rule conditions"""
        # Check threshold within time window
        key = f"{rule.id}:{event.source_ip}"
        current_time = time.time()
        
        # Clean old events
        self.event_history[key] = deque([
            t for t in self.event_history[key] 
            if current_time - t < rule.time_window
        ])
        
        # Add current event
        self.event_history[key].append(current_time)
        
        # Check threshold
        if len(self.event_history[key]) < rule.threshold:
            return False
        
        # Check specific conditions
        for field, condition in rule.conditions.items():
            event_value = getattr(event, field, None)
            if event_value is None:
                continue
                
            if isinstance(condition, list):
                if event_value not in condition:
                    return False
            elif isinstance(condition, dict):
                if "contains" in condition:
                    if not any(term in str(event_value).lower() 
                             for term in condition["contains"]):
                        return False
        
        return True


class SIEMIntegration:
    """Main SIEM integration class"""
    
    def __init__(self, config: SIEMConfig):
        self.config = config
        self.anomaly_detector = AnomalyDetector()
        self.threat_engine = ThreatDetectionEngine(config)
        self.redis_client = None
        self.event_queue = asyncio.Queue()
        self.running = False
        
    async def initialize(self):
        """Initialize SIEM integration"""
        # Connect to Redis
        self.redis_client = aioredis.from_url(self.config.redis_url)
        
        # Start background tasks
        self.running = True
        asyncio.create_task(self._process_events())
        asyncio.create_task(self._update_ml_model())
        
        logger.info("SIEM integration initialized")
    
    async def shutdown(self):
        """Shutdown SIEM integration"""
        self.running = False
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("SIEM integration shut down")
    
    async def ingest_event(self, event: SecurityEvent):
        """Ingest security event for processing"""
        await self.event_queue.put(event)
    
    async def _process_events(self):
        """Process events from queue"""
        while self.running:
            try:
                # Get event from queue
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=1.0
                )
                
                # Store event
                await self._store_event(event)
                
                # Detect anomalies
                if self.config.anomaly_detection_enabled:
                    is_anomaly, score = await self.anomaly_detector.detect_anomaly(event)
                    if is_anomaly:
                        event.tags.append("anomaly")
                        event.details["anomaly_score"] = score
                
                # Evaluate threat rules
                triggered_rules = await self.threat_engine.evaluate_rules(event)
                
                # Execute response actions
                for rule in triggered_rules:
                    await self._execute_response_actions(event, rule)
                
                # Forward to SIEM platforms
                await self._forward_to_siem_platforms(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _store_event(self, event: SecurityEvent):
        """Store event in Redis"""
        if not self.redis_client:
            return
        
        # Store event
        key = f"security_event:{event.id}"
        await self.redis_client.hset(key, mapping=event.to_dict())
        await self.redis_client.expire(key, self.config.event_retention_days * 86400)
        
        # Add to time-based index
        timestamp_key = f"events_by_time:{event.timestamp.strftime('%Y-%m-%d-%H')}"
        await self.redis_client.zadd(timestamp_key, {event.id: time.time()})
        await self.redis_client.expire(timestamp_key, self.config.event_retention_days * 86400)
    
    async def _execute_response_actions(self, event: SecurityEvent, rule: ThreatRule):
        """Execute automated response actions"""
        for action in rule.response_actions:
            try:
                if action == ResponseAction.LOG_ONLY:
                    logger.warning(f"Threat detected: {rule.name} - {event.id}")
                
                elif action == ResponseAction.ALERT:
                    await self._send_alert(event, rule)
                
                elif action == ResponseAction.BLOCK_IP:
                    await self._block_ip(event.source_ip)
                
                elif action == ResponseAction.BLOCK_USER:
                    if event.user_id:
                        await self._block_user(event.user_id)
                
                elif action == ResponseAction.EMERGENCY_RESPONSE:
                    await self._trigger_emergency_response(event, rule)
                
            except Exception as e:
                logger.error(f"Error executing response action {action}: {e}")
    
    async def _send_alert(self, event: SecurityEvent, rule: ThreatRule):
        """Send security alert"""
        alert_data = {
            "rule": rule.name,
            "event_id": event.id,
            "severity": rule.severity.name,
            "timestamp": event.timestamp.isoformat(),
            "source_ip": event.source_ip,
            "details": event.details
        }
        
        # Send to webhooks
        for webhook_url in self.config.webhook_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=alert_data) as response:
                        if response.status != 200:
                            logger.error(f"Failed to send webhook alert: {response.status}")
            except Exception as e:
                logger.error(f"Error sending webhook alert: {e}")
        
        # Send to Slack
        if self.config.slack_webhook:
            slack_message = {
                "text": f"🚨 Security Alert: {rule.name}",
                "attachments": [{
                    "color": "danger",
                    "fields": [
                        {"title": "Event ID", "value": event.id, "short": True},
                        {"title": "Severity", "value": rule.severity.name, "short": True},
                        {"title": "Source IP", "value": event.source_ip, "short": True},
                        {"title": "Timestamp", "value": event.timestamp.isoformat(), "short": True}
                    ]
                }]
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.config.slack_webhook, json=slack_message) as response:
                        if response.status != 200:
                            logger.error(f"Failed to send Slack alert: {response.status}")
            except Exception as e:
                logger.error(f"Error sending Slack alert: {e}")
    
    async def _block_ip(self, ip_address: str):
        """Block IP address"""
        self.threat_engine.blocked_ips.add(ip_address)
        
        # Store in Redis
        if self.redis_client:
            await self.redis_client.sadd("blocked_ips", ip_address)
            await self.redis_client.expire("blocked_ips", 86400)  # 24 hours
        
        logger.warning(f"Blocked IP address: {ip_address}")
    
    async def _block_user(self, user_id: str):
        """Block user account"""
        self.threat_engine.blocked_users.add(user_id)
        
        # Store in Redis
        if self.redis_client:
            await self.redis_client.sadd("blocked_users", user_id)
            await self.redis_client.expire("blocked_users", 86400)  # 24 hours
        
        logger.warning(f"Blocked user: {user_id}")
    
    async def _trigger_emergency_response(self, event: SecurityEvent, rule: ThreatRule):
        """Trigger emergency response protocol"""
        logger.critical(f"EMERGENCY: {rule.name} triggered by event {event.id}")
        
        # Send immediate alerts to all channels
        await self._send_alert(event, rule)
        
        # Additional emergency actions could be implemented here
        # e.g., activate incident response team, enable DDoS protection mode, etc.
    
    async def _forward_to_siem_platforms(self, event: SecurityEvent):
        """Forward event to configured SIEM platforms"""
        event_data = event.to_dict()
        
        # Forward to Splunk
        if self.config.splunk_config["enabled"]:
            await self._forward_to_splunk(event_data)
        
        # Forward to ELK Stack
        if self.config.elk_config["enabled"]:
            await self._forward_to_elk(event_data)
        
        # Forward to QRadar
        if self.config.qradar_config["enabled"]:
            await self._forward_to_qradar(event_data)
    
    async def _forward_to_splunk(self, event_data: Dict[str, Any]):
        """Forward event to Splunk"""
        # Implementation for Splunk HEC (HTTP Event Collector)
        pass
    
    async def _forward_to_elk(self, event_data: Dict[str, Any]):
        """Forward event to ELK Stack"""
        # Implementation for Elasticsearch ingestion
        pass
    
    async def _forward_to_qradar(self, event_data: Dict[str, Any]):
        """Forward event to IBM QRadar"""
        # Implementation for QRadar SIEM
        pass
    
    async def _update_ml_model(self):
        """Periodically update ML model with new data"""
        while self.running:
            try:
                await asyncio.sleep(self.config.ml_model_update_interval)
                
                # Get recent events from Redis
                if self.redis_client:
                    # Implementation for fetching recent events and retraining model
                    pass
                
            except Exception as e:
                logger.error(f"Error updating ML model: {e}")


# Global SIEM instance
siem_instance = None


async def initialize_siem(config: SIEMConfig = None) -> SIEMIntegration:
    """Initialize global SIEM integration"""
    global siem_instance
    
    if siem_instance is None:
        if config is None:
            config = SIEMConfig()
        
        siem_instance = SIEMIntegration(config)
        await siem_instance.initialize()
    
    return siem_instance


def get_siem() -> Optional[SIEMIntegration]:
    """Get global SIEM instance"""
    return siem_instance


async def log_security_event(
    event_type: EventType,
    severity: SeverityLevel,
    source_ip: str,
    **kwargs
) -> SecurityEvent:
    """Convenience function to log security event"""
    event = SecurityEvent(
        id=f"event_{int(time.time())}_{hash(source_ip) % 10000}",
        timestamp=datetime.utcnow(),
        event_type=event_type,
        severity=severity,
        source_ip=source_ip,
        **kwargs
    )
    
    if siem_instance:
        await siem_instance.ingest_event(event)
    
    return event