"""Threat Detector - IA-Influencer-Agent Platform

Real-time threat detection and security monitoring system for
identifying and responding to security threats.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    ANOMALOUS_ACCESS = "anomalous_access"
    SUSPICIOUS_TRANSACTION = "suspicious_transaction"
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_EXFILTRATION = "data_exfiltration"


@dataclass
class SecurityThreat:
    """Security threat detection"""
    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    target_resource: str
    description: str
    evidence: Dict[str, Any]
    detected_at: datetime
    mitigated: bool = False
    mitigation_actions: List[str] = None


class ThreatDetector:
    """Real-time Security Threat Detection System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.detected_threats: List[SecurityThreat] = []
        self.threat_patterns: Dict[str, Any] = self._init_threat_patterns()
        
        # Detection thresholds
        self.failed_login_threshold = config.get("failed_login_threshold", 5)
        self.suspicious_transaction_amount = config.get("suspicious_amount", 10000)
        self.monitoring_window_minutes = config.get("monitoring_window", 60)
    
    def _init_threat_patterns(self) -> Dict[str, Any]:
        """Initialize threat detection patterns"""
        return {
            "brute_force": {
                "max_failed_attempts": 5,
                "time_window_minutes": 15,
                "action": "block_ip"
            },
            "anomalous_access": {
                "unusual_location": True,
                "unusual_time": True,
                "action": "require_2fa"
            },
            "suspicious_transaction": {
                "large_amount": 10000,
                "rapid_succession": 10,
                "action": "flag_for_review"
            }
        }
    
    async def detect_threat(
        self,
        event_data: Dict[str, Any]
    ) -> Optional[SecurityThreat]:
        """Detect security threats from event data"""
        try:
            threat = None
            
            # Check for brute force attacks
            if event_data.get("event_type") == "failed_login":
                threat = await self._check_brute_force(event_data)
            
            # Check for suspicious transactions
            elif event_data.get("event_type") == "transaction":
                threat = await self._check_suspicious_transaction(event_data)
            
            # Check for anomalous access patterns
            elif event_data.get("event_type") == "access_attempt":
                threat = await self._check_anomalous_access(event_data)
            
            if threat:
                self.detected_threats.append(threat)
                await self._trigger_threat_response(threat)
            
            return threat
            
        except Exception as e:
            self.logger.error(f"Threat detection failed: {e}")
            raise
    
    async def _check_brute_force(self, event_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for brute force attack patterns"""
        source_ip = event_data.get("source_ip")
        
        # Count recent failed attempts from same IP
        recent_failures = len([
            t for t in self.detected_threats
            if (t.threat_type == ThreatType.BRUTE_FORCE and
                t.source_ip == source_ip and
                datetime.utcnow() - t.detected_at < timedelta(minutes=15))
        ])
        
        if recent_failures >= self.failed_login_threshold:
            import uuid
            return SecurityThreat(
                threat_id=str(uuid.uuid4()),
                threat_type=ThreatType.BRUTE_FORCE,
                threat_level=ThreatLevel.HIGH,
                source_ip=source_ip,
                target_resource=event_data.get("target", "unknown"),
                description=f"Brute force attack detected from {source_ip}",
                evidence={"failed_attempts": recent_failures, "pattern": "repeated_failures"},
                detected_at=datetime.utcnow()
            )
        
        return None
    
    async def _check_suspicious_transaction(self, event_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for suspicious transaction patterns"""
        amount = event_data.get("amount", 0)
        
        if amount > self.suspicious_transaction_amount:
            import uuid
            return SecurityThreat(
                threat_id=str(uuid.uuid4()),
                threat_type=ThreatType.SUSPICIOUS_TRANSACTION,
                threat_level=ThreatLevel.MEDIUM,
                source_ip=event_data.get("source_ip", "unknown"),
                target_resource=event_data.get("transaction_id", "unknown"),
                description=f"Large transaction detected: {amount}",
                evidence={"amount": amount, "threshold": self.suspicious_transaction_amount},
                detected_at=datetime.utcnow()
            )
        
        return None
    
    async def _check_anomalous_access(self, event_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Check for anomalous access patterns"""
        # Simple anomaly detection based on time
        current_hour = datetime.utcnow().hour
        
        # Flag access during unusual hours (2 AM - 5 AM)
        if 2 <= current_hour <= 5:
            import uuid
            return SecurityThreat(
                threat_id=str(uuid.uuid4()),
                threat_type=ThreatType.ANOMALOUS_ACCESS,
                threat_level=ThreatLevel.LOW,
                source_ip=event_data.get("source_ip", "unknown"),
                target_resource=event_data.get("resource", "unknown"),
                description="Access during unusual hours",
                evidence={"access_hour": current_hour, "pattern": "unusual_time"},
                detected_at=datetime.utcnow()
            )
        
        return None
    
    async def _trigger_threat_response(self, threat: SecurityThreat):
        """Trigger automated threat response"""
        try:
            self.logger.warning(f"THREAT DETECTED: {threat.description}")
            
            # Mock threat response actions
            if threat.threat_type == ThreatType.BRUTE_FORCE:
                self.logger.warning(f"Blocking IP: {threat.source_ip}")
            elif threat.threat_type == ThreatType.SUSPICIOUS_TRANSACTION:
                self.logger.warning(f"Flagging transaction for review: {threat.target_resource}")
            
            # Log to security team
            self.logger.critical(f"Security threat {threat.threat_id}: {threat.description}")
            
        except Exception as e:
            self.logger.error(f"Threat response failed: {e}")
    
    async def get_threat_summary(self) -> Dict[str, Any]:
        """Get summary of detected threats"""
        total_threats = len(self.detected_threats)
        
        level_counts = {}
        type_counts = {}
        
        for threat in self.detected_threats:
            level = threat.threat_level.value
            threat_type = threat.threat_type.value
            
            level_counts[level] = level_counts.get(level, 0) + 1
            type_counts[threat_type] = type_counts.get(threat_type, 0) + 1
        
        return {
            "total_threats": total_threats,
            "threat_level_distribution": level_counts,
            "threat_type_distribution": type_counts,
            "monitoring_window_minutes": self.monitoring_window_minutes
        }