"""Data Access Audit System

Comprehensive data access auditing with real-time monitoring
and alerting for abnormal access patterns.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import hashlib

from ...core.logging import get_logger
from ...core.config import get_settings
from ...core.cache import CacheManager
from ...data_management.governance.classification import DataClassifier

logger = get_logger(__name__)


class AccessEventType(Enum):
    """Types of data access events"""
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    COPY = "copy"
    SHARE = "share"
    DOWNLOAD = "download"


class AnomalyType(Enum):
    """Types of access anomalies"""
    UNUSUAL_VOLUME = "unusual_volume"           # High volume of access
    UNUSUAL_TIME = "unusual_time"               # Access at unusual hours
    UNUSUAL_LOCATION = "unusual_location"       # Access from unusual location
    UNUSUAL_DATA_TYPE = "unusual_data_type"     # Access to unusual data types
    PRIVILEGE_ESCALATION = "privilege_escalation"  # Attempting higher privileges
    BULK_EXPORT = "bulk_export"                 # Large data exports
    FAILED_ACCESS = "failed_access"             # Multiple failed access attempts
    PATTERN_DEVIATION = "pattern_deviation"     # Deviation from normal patterns


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AccessEvent:
    """Data access event record"""
    event_id: str
    user_id: str
    event_type: AccessEventType
    resource_id: str
    resource_type: str
    data_classification: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    session_id: str
    success: bool
    details: Dict[str, Any]
    risk_score: float = 0.0


@dataclass
class AccessAnomaly:
    """Detected access anomaly"""
    anomaly_id: str
    user_id: str
    anomaly_type: AnomalyType
    severity: AlertSeverity
    description: str
    evidence: List[AccessEvent]
    detected_at: datetime
    risk_score: float
    recommendations: List[str]


class DataAccessAuditor:
    """
    Comprehensive data access auditing and monitoring system
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache = cache_manager or CacheManager()
        self.logger = logger
        self.settings = get_settings()
        
        # In-memory stores for analysis (in production, use persistent storage)
        self.access_events: deque = deque(maxlen=10000)
        self.user_patterns: Dict[str, Dict] = defaultdict(dict)
        self.alert_thresholds = self._load_alert_thresholds()
        
        # Classification for risk assessment
        self.data_classifier = DataClassifier()
        
        # Alert handlers
        self.alert_handlers: List[callable] = []
        
    def _load_alert_thresholds(self) -> Dict[str, Any]:
        """Load alerting thresholds configuration"""
        return {
            "max_events_per_hour": 100,
            "max_failed_attempts": 5,
            "unusual_hour_threshold": {"start": 22, "end": 6},  # 10 PM to 6 AM
            "bulk_export_threshold": 1000,  # records
            "high_risk_data_access_limit": 10,  # per day
            "pattern_deviation_threshold": 0.8,  # statistical threshold
        }
    
    async def log_access_event(
        self,
        user_id: str,
        event_type: AccessEventType,
        resource_id: str,
        resource_type: str,
        ip_address: str,
        user_agent: str,
        session_id: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a data access event and trigger anomaly detection
        
        Returns:
            Event ID for tracking
        """
        try:
            # Generate event ID
            event_id = f"access_{datetime.utcnow().isoformat()}_{user_id}_{resource_id}"
            event_hash = hashlib.sha256(event_id.encode()).hexdigest()[:16]
            
            # Classify the data being accessed
            data_classification = await self.data_classifier.classify_resource(
                resource_id, resource_type
            )
            
            # Calculate initial risk score
            risk_score = await self._calculate_risk_score(
                user_id, event_type, data_classification, details or {}
            )
            
            # Create access event
            access_event = AccessEvent(
                event_id=event_hash,
                user_id=user_id,
                event_type=event_type,
                resource_id=resource_id,
                resource_type=resource_type,
                data_classification=data_classification.get("level", "internal"),
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                success=success,
                details=details or {},
                risk_score=risk_score
            )
            
            # Store event
            self.access_events.append(access_event)
            
            # Cache for quick access
            await self.cache.set(
                f"access_event:{event_hash}",
                asdict(access_event),
                ttl=86400  # 24 hours
            )
            
            # Update user patterns
            await self._update_user_patterns(user_id, access_event)
            
            # Trigger real-time anomaly detection
            anomalies = await self._detect_anomalies(user_id, access_event)
            
            # Process any detected anomalies
            for anomaly in anomalies:
                await self._handle_anomaly(anomaly)
            
            self.logger.info(
                f"Access event logged: {event_hash} - User: {user_id}, "
                f"Resource: {resource_id}, Type: {event_type.value}, "
                f"Risk Score: {risk_score:.2f}"
            )
            
            return event_hash
            
        except Exception as e:
            self.logger.error(f"Failed to log access event: {str(e)}")
            raise
    
    async def _calculate_risk_score(
        self,
        user_id: str,
        event_type: AccessEventType,
        data_classification: Dict[str, Any],
        details: Dict[str, Any]
    ) -> float:
        """Calculate risk score for an access event"""
        risk_score = 0.0
        
        # Base risk by data classification
        classification_level = data_classification.get("level", "internal")
        classification_risks = {
            "public": 0.1,
            "internal": 0.3,
            "confidential": 0.6,
            "restricted": 0.8,
            "top_secret": 1.0
        }
        risk_score += classification_risks.get(classification_level, 0.3)
        
        # Risk by event type
        event_risks = {
            AccessEventType.READ: 0.1,
            AccessEventType.WRITE: 0.3,
            AccessEventType.UPDATE: 0.3,
            AccessEventType.DELETE: 0.8,
            AccessEventType.EXPORT: 0.7,
            AccessEventType.COPY: 0.5,
            AccessEventType.SHARE: 0.6,
            AccessEventType.DOWNLOAD: 0.4
        }
        risk_score += event_risks.get(event_type, 0.3)
        
        # Additional risk factors
        if details.get("bulk_operation", False):
            risk_score += 0.3
        
        if details.get("external_access", False):
            risk_score += 0.4
        
        if details.get("privileged_access", False):
            risk_score += 0.3
        
        # Normalize to 0-1 range
        return min(risk_score, 1.0)
    
    async def _update_user_patterns(self, user_id: str, event: AccessEvent):
        """Update user access patterns for baseline establishment"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                "typical_hours": set(),
                "typical_ips": set(),
                "typical_resources": set(),
                "average_events_per_hour": 0,
                "last_updated": datetime.utcnow()
            }
        
        patterns = self.user_patterns[user_id]
        
        # Update typical access hours
        patterns["typical_hours"].add(event.timestamp.hour)
        
        # Update typical IP addresses (keep last 10)
        patterns["typical_ips"].add(event.ip_address)
        if len(patterns["typical_ips"]) > 10:
            patterns["typical_ips"] = set(list(patterns["typical_ips"])[-10:])
        
        # Update typical resources (keep last 50)
        patterns["typical_resources"].add(event.resource_type)
        if len(patterns["typical_resources"]) > 50:
            patterns["typical_resources"] = set(list(patterns["typical_resources"])[-50:])
        
        patterns["last_updated"] = datetime.utcnow()
        
        # Cache updated patterns
        await self.cache.set(
            f"user_patterns:{user_id}",
            patterns,
            ttl=604800  # 7 days
        )
    
    async def _detect_anomalies(
        self,
        user_id: str,
        current_event: AccessEvent
    ) -> List[AccessAnomaly]:
        """Detect access anomalies in real-time"""
        anomalies = []
        
        # Get recent events for this user
        recent_events = [
            event for event in self.access_events
            if event.user_id == user_id and 
               event.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        # Check for unusual volume
        if len(recent_events) > self.alert_thresholds["max_events_per_hour"]:
            anomaly = await self._create_anomaly(
                user_id=user_id,
                anomaly_type=AnomalyType.UNUSUAL_VOLUME,
                severity=AlertSeverity.HIGH,
                description=f"Unusual access volume: {len(recent_events)} events in last hour",
                evidence=recent_events,
                risk_score=0.8
            )
            anomalies.append(anomaly)
        
        # Check for unusual time
        current_hour = current_event.timestamp.hour
        unusual_hours = self.alert_thresholds["unusual_hour_threshold"]
        if (current_hour >= unusual_hours["start"] or 
            current_hour <= unusual_hours["end"]):
            
            # Check if this is unusual for this user
            user_patterns = self.user_patterns.get(user_id, {})
            typical_hours = user_patterns.get("typical_hours", set())
            
            if current_hour not in typical_hours:
                anomaly = await self._create_anomaly(
                    user_id=user_id,
                    anomaly_type=AnomalyType.UNUSUAL_TIME,
                    severity=AlertSeverity.MEDIUM,
                    description=f"Access at unusual time: {current_hour:02d}:00",
                    evidence=[current_event],
                    risk_score=0.5
                )
                anomalies.append(anomaly)
        
        # Check for failed access attempts
        failed_events = [
            event for event in recent_events
            if not event.success
        ]
        
        if len(failed_events) >= self.alert_thresholds["max_failed_attempts"]:
            anomaly = await self._create_anomaly(
                user_id=user_id,
                anomaly_type=AnomalyType.FAILED_ACCESS,
                severity=AlertSeverity.HIGH,
                description=f"Multiple failed access attempts: {len(failed_events)}",
                evidence=failed_events,
                risk_score=0.9
            )
            anomalies.append(anomaly)
        
        # Check for bulk export
        if (current_event.event_type == AccessEventType.EXPORT and
            current_event.details.get("record_count", 0) > 
            self.alert_thresholds["bulk_export_threshold"]):
            
            anomaly = await self._create_anomaly(
                user_id=user_id,
                anomaly_type=AnomalyType.BULK_EXPORT,
                severity=AlertSeverity.CRITICAL,
                description=f"Bulk data export: {current_event.details.get('record_count')} records",
                evidence=[current_event],
                risk_score=1.0
            )
            anomalies.append(anomaly)
        
        # Check for unusual location
        user_patterns = self.user_patterns.get(user_id, {})
        typical_ips = user_patterns.get("typical_ips", set())
        
        if current_event.ip_address not in typical_ips:
            anomaly = await self._create_anomaly(
                user_id=user_id,
                anomaly_type=AnomalyType.UNUSUAL_LOCATION,
                severity=AlertSeverity.MEDIUM,
                description=f"Access from unusual IP: {current_event.ip_address}",
                evidence=[current_event],
                risk_score=0.6
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    async def _create_anomaly(
        self,
        user_id: str,
        anomaly_type: AnomalyType,
        severity: AlertSeverity,
        description: str,
        evidence: List[AccessEvent],
        risk_score: float
    ) -> AccessAnomaly:
        """Create an access anomaly record"""
        anomaly_id = f"anomaly_{datetime.utcnow().isoformat()}_{user_id}"
        anomaly_hash = hashlib.sha256(anomaly_id.encode()).hexdigest()[:16]
        
        # Generate recommendations based on anomaly type
        recommendations = self._generate_recommendations(anomaly_type, severity)
        
        return AccessAnomaly(
            anomaly_id=anomaly_hash,
            user_id=user_id,
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            evidence=evidence,
            detected_at=datetime.utcnow(),
            risk_score=risk_score,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        anomaly_type: AnomalyType,
        severity: AlertSeverity
    ) -> List[str]:
        """Generate security recommendations based on anomaly"""
        recommendations = []
        
        if anomaly_type == AnomalyType.UNUSUAL_VOLUME:
            recommendations.extend([
                "Review user's recent activity for legitimacy",
                "Consider temporarily limiting access rate",
                "Verify user account has not been compromised"
            ])
        
        elif anomaly_type == AnomalyType.UNUSUAL_TIME:
            recommendations.extend([
                "Verify if user is working outside normal hours",
                "Check if access is from authorized location",
                "Consider additional authentication for off-hours access"
            ])
        
        elif anomaly_type == AnomalyType.FAILED_ACCESS:
            recommendations.extend([
                "Lock user account temporarily",
                "Force password reset",
                "Investigate potential brute force attack"
            ])
        
        elif anomaly_type == AnomalyType.BULK_EXPORT:
            recommendations.extend([
                "Immediately review export legitimacy",
                "Contact user to verify export authorization",
                "Consider data loss prevention measures"
            ])
        
        elif anomaly_type == AnomalyType.UNUSUAL_LOCATION:
            recommendations.extend([
                "Verify user's current location",
                "Check for VPN or proxy usage",
                "Consider requiring additional authentication"
            ])
        
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            recommendations.append("Escalate to security team immediately")
        
        return recommendations
    
    async def _handle_anomaly(self, anomaly: AccessAnomaly):
        """Handle detected anomaly with appropriate response"""
        try:
            # Log the anomaly
            self.logger.warning(
                f"Security anomaly detected: {anomaly.anomaly_id} - "
                f"Type: {anomaly.anomaly_type.value}, "
                f"Severity: {anomaly.severity.value}, "
                f"User: {anomaly.user_id}"
            )
            
            # Cache anomaly for investigation
            await self.cache.set(
                f"anomaly:{anomaly.anomaly_id}",
                asdict(anomaly),
                ttl=604800  # 7 days
            )
            
            # Trigger alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(anomaly)
                except Exception as e:
                    self.logger.error(f"Alert handler failed: {str(e)}")
            
            # Auto-response for critical anomalies
            if anomaly.severity == AlertSeverity.CRITICAL:
                await self._trigger_critical_response(anomaly)
                
        except Exception as e:
            self.logger.error(f"Failed to handle anomaly: {str(e)}")
    
    async def _trigger_critical_response(self, anomaly: AccessAnomaly):
        """Trigger automated response for critical anomalies"""
        # Implementation would include:
        # - Account lockout
        # - Security team notification
        # - Incident response activation
        # - Data access blocking
        
        self.logger.critical(
            f"CRITICAL SECURITY ANOMALY - Automated response triggered: {anomaly.anomaly_id}"
        )
    
    def add_alert_handler(self, handler: callable):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
    
    async def get_access_report(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate access audit report"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=7)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Filter events
        filtered_events = [
            event for event in self.access_events
            if (not user_id or event.user_id == user_id) and
               start_time <= event.timestamp <= end_time
        ]
        
        # Calculate statistics
        total_events = len(filtered_events)
        successful_events = len([e for e in filtered_events if e.success])
        failed_events = total_events - successful_events
        
        unique_users = len(set(event.user_id for event in filtered_events))
        unique_resources = len(set(event.resource_id for event in filtered_events))
        
        # Risk analysis
        high_risk_events = [e for e in filtered_events if e.risk_score > 0.7]
        average_risk_score = (
            sum(event.risk_score for event in filtered_events) / total_events
            if total_events > 0 else 0
        )
        
        return {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "total_events": total_events,
                "successful_events": successful_events,
                "failed_events": failed_events,
                "unique_users": unique_users,
                "unique_resources": unique_resources
            },
            "risk_analysis": {
                "high_risk_events": len(high_risk_events),
                "average_risk_score": round(average_risk_score, 3),
                "risk_distribution": {
                    "low": len([e for e in filtered_events if e.risk_score <= 0.3]),
                    "medium": len([e for e in filtered_events if 0.3 < e.risk_score <= 0.7]),
                    "high": len([e for e in filtered_events if e.risk_score > 0.7])
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }


# Convenience decorator for automatic access logging
def audit_data_access(
    resource_type: str,
    event_type: AccessEventType = AccessEventType.READ
):
    """Decorator to automatically audit data access"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request context (implementation specific)
            # This would need to be adapted to your framework
            
            # Log access event
            auditor = DataAccessAuditor()
            await auditor.log_access_event(
                user_id="system",  # Extract from context
                event_type=event_type,
                resource_id="unknown",  # Extract from args
                resource_type=resource_type,
                ip_address="127.0.0.1",  # Extract from request
                user_agent="system",  # Extract from request
                session_id="system"  # Extract from session
            )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator