"""
Security Analytics Engine
Enterprise security analytics and threat intelligence for ML systems

Features:
- Security event correlation
- Threat pattern detection  
- Anomaly analysis
- Risk scoring
- Security dashboards
- Incident response automation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import uuid


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityEventType(Enum):
    """Types of security events"""
    ACCESS_VIOLATION = "access_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    FAILED_AUTHENTICATION = "failed_authentication"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MODEL_TAMPERING = "model_tampering"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


@dataclass
class SecurityEvent:
    """Security event for analytics"""
    event_id: str
    timestamp: datetime
    event_type: SecurityEventType
    threat_level: ThreatLevel
    source_ip: Optional[str]
    user_id: Optional[str]
    resource_id: str
    description: str
    metadata: Dict[str, Any]
    risk_score: float


@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    threat_id: str
    threat_type: str
    indicators: List[str]
    confidence: float
    severity: ThreatLevel
    description: str
    mitigation: List[str]
    last_seen: datetime


@dataclass
class SecurityMetric:
    """Security metrics for analytics"""
    metric_name: str
    value: float
    timestamp: datetime
    category: str
    threshold: Optional[float] = None


class SecurityAnalytics:
    """
    Enterprise Security Analytics Engine
    Comprehensive security analytics and threat intelligence
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_events: List[SecurityEvent] = []
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.security_metrics: List[SecurityMetric] = []
        self.correlation_rules: List[Dict[str, Any]] = []
        self.baselines: Dict[str, float] = {}
        
        # Initialize threat intelligence and correlation rules
        self._initialize_threat_intelligence()
        self._initialize_correlation_rules()
    
    def _initialize_threat_intelligence(self):
        """Initialize threat intelligence database"""
        sample_threats = [
            ThreatIntelligence(
                threat_id="TI-001",
                threat_type="model_poisoning",
                indicators=["unusual_gradient_patterns", "abnormal_loss_function"],
                confidence=0.85,
                severity=ThreatLevel.HIGH,
                description="Model poisoning attack detected through gradient analysis",
                mitigation=["Validate training data", "Monitor gradient norms", "Use robust aggregation"],
                last_seen=datetime.now()
            ),
            ThreatIntelligence(
                threat_id="TI-002", 
                threat_type="adversarial_attack",
                indicators=["high_confidence_predictions", "small_input_perturbations"],
                confidence=0.90,
                severity=ThreatLevel.MEDIUM,
                description="Adversarial examples targeting model inference",
                mitigation=["Input validation", "Adversarial training", "Detection filters"],
                last_seen=datetime.now()
            )
        ]
        
        for threat in sample_threats:
            self.threat_intelligence[threat.threat_id] = threat
    
    def _initialize_correlation_rules(self):
        """Initialize event correlation rules"""
        self.correlation_rules = [
            {
                "rule_id": "RULE-001",
                "name": "Multiple Failed Logins",
                "description": "Detect multiple failed login attempts",
                "conditions": {
                    "event_type": SecurityEventType.FAILED_AUTHENTICATION,
                    "count_threshold": 5,
                    "time_window_minutes": 10
                },
                "threat_level": ThreatLevel.MEDIUM,
                "actions": ["alert", "block_user"]
            },
            {
                "rule_id": "RULE-002",
                "name": "Anomalous Model Access",
                "description": "Detect unusual model access patterns",
                "conditions": {
                    "event_type": SecurityEventType.ACCESS_VIOLATION,
                    "risk_score_threshold": 0.8
                },
                "threat_level": ThreatLevel.HIGH,
                "actions": ["alert", "require_additional_auth"]
            }
        ]
    
    async def ingest_security_event(
        self,
        event_type: SecurityEventType,
        source_ip: Optional[str],
        user_id: Optional[str], 
        resource_id: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Ingest security event for analysis"""
        try:
            event_id = str(uuid.uuid4())
            
            # Calculate initial risk score
            risk_score = await self._calculate_risk_score(event_type, metadata or {})
            
            # Determine threat level
            threat_level = self._determine_threat_level(risk_score, event_type)
            
            # Create security event
            event = SecurityEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                event_type=event_type,
                threat_level=threat_level,
                source_ip=source_ip,
                user_id=user_id,
                resource_id=resource_id,
                description=description,
                metadata=metadata or {},
                risk_score=risk_score
            )
            
            self.security_events.append(event)
            
            # Trigger real-time analysis
            await self._analyze_event(event)
            
            # Check correlation rules
            await self._check_correlation_rules(event)
            
            # Update security metrics
            await self._update_security_metrics(event)
            
            self.logger.info(f"Security event ingested: {event_id}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"Failed to ingest security event: {str(e)}")
            raise
    
    async def analyze_threat_patterns(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Analyze threat patterns from security events"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_window
            
            # Filter events by time window
            recent_events = [
                event for event in self.security_events
                if event.timestamp >= start_time
            ]
            
            analysis_result = {
                "analysis_id": str(uuid.uuid4()),
                "time_window": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "total_events": len(recent_events),
                "threat_patterns": {},
                "anomalies": [],
                "risk_summary": {},
                "recommendations": []
            }
            
            if not recent_events:
                return analysis_result
            
            # Analyze patterns by event type
            event_patterns = defaultdict(list)
            for event in recent_events:
                event_patterns[event.event_type.value].append(event)
            
            for event_type, events in event_patterns.items():
                pattern_analysis = await self._analyze_event_pattern(events)
                analysis_result["threat_patterns"][event_type] = pattern_analysis
            
            # Detect anomalies
            analysis_result["anomalies"] = await self._detect_security_anomalies(recent_events)
            
            # Calculate risk summary
            analysis_result["risk_summary"] = self._calculate_risk_summary(recent_events)
            
            # Generate recommendations
            analysis_result["recommendations"] = self._generate_security_recommendations(recent_events)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Threat pattern analysis failed: {str(e)}")
            raise
    
    async def correlate_events(
        self,
        events: List[SecurityEvent],
        correlation_window: timedelta = timedelta(minutes=30)
    ) -> List[Dict[str, Any]]:
        """Correlate security events to identify attack chains"""
        try:
            correlations = []
            
            # Group events by user and source IP
            user_events = defaultdict(list)
            ip_events = defaultdict(list)
            
            for event in events:
                if event.user_id:
                    user_events[event.user_id].append(event)
                if event.source_ip:
                    ip_events[event.source_ip].append(event)
            
            # Analyze user-based correlations
            for user_id, user_event_list in user_events.items():
                if len(user_event_list) >= 2:
                    correlation = await self._analyze_user_correlation(user_id, user_event_list)
                    if correlation:
                        correlations.append(correlation)
            
            # Analyze IP-based correlations
            for source_ip, ip_event_list in ip_events.items():
                if len(ip_event_list) >= 2:
                    correlation = await self._analyze_ip_correlation(source_ip, ip_event_list)
                    if correlation:
                        correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Event correlation failed: {str(e)}")
            return []
    
    async def generate_security_report(
        self,
        report_type: str = "summary",
        time_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Generate comprehensive security analytics report"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_period
            
            # Filter events by time period
            period_events = [
                event for event in self.security_events
                if event.timestamp >= start_time
            ]
            
            report = {
                "report_id": str(uuid.uuid4()),
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "summary": await self._generate_report_summary(period_events),
                "threat_analysis": await self.analyze_threat_patterns(time_period),
                "correlations": await self.correlate_events(period_events),
                "top_threats": self._identify_top_threats(period_events),
                "security_metrics": self._get_period_metrics(start_time, end_time),
                "recommendations": self._generate_security_recommendations(period_events)
            }
            
            if report_type == "detailed":
                report["event_details"] = [
                    {
                        "event_id": e.event_id,
                        "timestamp": e.timestamp.isoformat(),
                        "type": e.event_type.value,
                        "threat_level": e.threat_level.value,
                        "risk_score": e.risk_score,
                        "description": e.description
                    }
                    for e in period_events
                ]
            
            return report
            
        except Exception as e:
            self.logger.error(f"Security report generation failed: {str(e)}")
            raise
    
    async def get_real_time_alerts(
        self,
        severity_threshold: ThreatLevel = ThreatLevel.MEDIUM
    ) -> List[Dict[str, Any]]:
        """Get real-time security alerts"""
        try:
            # Get recent high-priority events (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            severity_levels = {
                ThreatLevel.INFO: 0,
                ThreatLevel.LOW: 1,
                ThreatLevel.MEDIUM: 2,
                ThreatLevel.HIGH: 3,
                ThreatLevel.CRITICAL: 4
            }
            
            threshold_level = severity_levels[severity_threshold]
            
            alerts = []
            for event in self.security_events:
                if (event.timestamp >= cutoff_time and
                    severity_levels[event.threat_level] >= threshold_level):
                    
                    alert = {
                        "alert_id": f"ALERT-{event.event_id}",
                        "event_id": event.event_id,
                        "timestamp": event.timestamp.isoformat(),
                        "threat_level": event.threat_level.value,
                        "event_type": event.event_type.value,
                        "description": event.description,
                        "risk_score": event.risk_score,
                        "source_ip": event.source_ip,
                        "user_id": event.user_id,
                        "resource_id": event.resource_id,
                        "requires_response": event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
                    }
                    alerts.append(alert)
            
            # Sort by threat level and timestamp
            alerts.sort(key=lambda x: (severity_levels[ThreatLevel(x["threat_level"])], x["timestamp"]), reverse=True)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get real-time alerts: {str(e)}")
            return []
    
    async def update_threat_intelligence(
        self,
        threat_data: ThreatIntelligence
    ) -> bool:
        """Update threat intelligence database"""
        try:
            self.threat_intelligence[threat_data.threat_id] = threat_data
            self.logger.info(f"Threat intelligence updated: {threat_data.threat_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update threat intelligence: {str(e)}")
            return False
    
    # Private analysis methods
    
    async def _analyze_event(self, event: SecurityEvent):
        """Analyze individual security event"""
        try:
            # Check against threat intelligence
            for threat in self.threat_intelligence.values():
                if await self._matches_threat_indicators(event, threat):
                    self.logger.warning(f"Event {event.event_id} matches threat {threat.threat_id}")
                    # Could trigger additional actions here
            
        except Exception as e:
            self.logger.error(f"Event analysis failed: {str(e)}")
    
    async def _check_correlation_rules(self, event: SecurityEvent):
        """Check event against correlation rules"""
        try:
            for rule in self.correlation_rules:
                if await self._evaluate_correlation_rule(rule, event):
                    await self._trigger_correlation_alert(rule, event)
                    
        except Exception as e:
            self.logger.error(f"Correlation rule checking failed: {str(e)}")
    
    async def _calculate_risk_score(
        self,
        event_type: SecurityEventType,
        metadata: Dict[str, Any]
    ) -> float:
        """Calculate risk score for security event"""
        base_scores = {
            SecurityEventType.ACCESS_VIOLATION: 0.7,
            SecurityEventType.FAILED_AUTHENTICATION: 0.5,
            SecurityEventType.PRIVILEGE_ESCALATION: 0.9,
            SecurityEventType.DATA_EXFILTRATION: 0.95,
            SecurityEventType.MODEL_TAMPERING: 0.85,
            SecurityEventType.ANOMALOUS_BEHAVIOR: 0.6,
            SecurityEventType.SUSPICIOUS_PATTERN: 0.4
        }
        
        base_score = base_scores.get(event_type, 0.5)
        
        # Adjust based on metadata
        if metadata.get("repeated_attempts", 0) > 3:
            base_score += 0.2
        
        if metadata.get("privileged_user", False):
            base_score += 0.1
        
        if metadata.get("sensitive_resource", False):
            base_score += 0.15
        
        return min(1.0, base_score)
    
    def _determine_threat_level(
        self,
        risk_score: float,
        event_type: SecurityEventType
    ) -> ThreatLevel:
        """Determine threat level based on risk score and event type"""
        if risk_score >= 0.9:
            return ThreatLevel.CRITICAL
        elif risk_score >= 0.7:
            return ThreatLevel.HIGH
        elif risk_score >= 0.5:
            return ThreatLevel.MEDIUM
        elif risk_score >= 0.3:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.INFO
    
    async def _analyze_event_pattern(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Analyze pattern in similar events"""
        if not events:
            return {}
        
        # Calculate pattern metrics
        timestamps = [e.timestamp for e in events]
        risk_scores = [e.risk_score for e in events]
        
        pattern_analysis = {
            "event_count": len(events),
            "time_span_minutes": (max(timestamps) - min(timestamps)).total_seconds() / 60,
            "average_risk_score": np.mean(risk_scores),
            "max_risk_score": max(risk_scores),
            "frequency_per_hour": len(events) / max(1, (max(timestamps) - min(timestamps)).total_seconds() / 3600),
            "escalation_detected": risk_scores[-1] > risk_scores[0] if len(risk_scores) > 1 else False
        }
        
        return pattern_analysis
    
    async def _detect_security_anomalies(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Detect anomalies in security events"""
        anomalies = []
        
        if len(events) < 10:  # Need sufficient data
            return anomalies
        
        # Analyze frequency anomalies
        hourly_counts = defaultdict(int)
        for event in events:
            hour_key = event.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        if hourly_counts:
            counts = list(hourly_counts.values())
            mean_count = np.mean(counts)
            std_count = np.std(counts)
            
            for hour, count in hourly_counts.items():
                if count > mean_count + 2 * std_count:  # 2 sigma threshold
                    anomalies.append({
                        "type": "frequency_spike",
                        "timestamp": hour.isoformat(),
                        "event_count": count,
                        "expected_range": f"{mean_count:.1f} ± {2*std_count:.1f}",
                        "severity": "medium" if count > mean_count + 3 * std_count else "low"
                    })
        
        return anomalies
    
    def _calculate_risk_summary(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Calculate risk summary from events"""
        if not events:
            return {}
        
        risk_scores = [e.risk_score for e in events]
        threat_counts = defaultdict(int)
        
        for event in events:
            threat_counts[event.threat_level.value] += 1
        
        return {
            "total_events": len(events),
            "average_risk_score": np.mean(risk_scores),
            "max_risk_score": max(risk_scores),
            "threat_distribution": dict(threat_counts),
            "high_risk_events": len([e for e in events if e.risk_score >= 0.7]),
            "overall_risk_level": self._calculate_overall_risk_level(events)
        }
    
    def _calculate_overall_risk_level(self, events: List[SecurityEvent]) -> str:
        """Calculate overall risk level"""
        if not events:
            return "low"
        
        critical_count = len([e for e in events if e.threat_level == ThreatLevel.CRITICAL])
        high_count = len([e for e in events if e.threat_level == ThreatLevel.HIGH])
        
        if critical_count > 0:
            return "critical"
        elif high_count > len(events) * 0.3:  # More than 30% high-threat events
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_security_recommendations(self, events: List[SecurityEvent]) -> List[str]:
        """Generate security recommendations based on events"""
        recommendations = []
        
        if not events:
            return ["Maintain current security monitoring"]
        
        # Analyze common patterns
        event_types = [e.event_type for e in events]
        threat_levels = [e.threat_level for e in events]
        
        # Check for repeated failed authentications
        failed_auth_count = len([e for e in events if e.event_type == SecurityEventType.FAILED_AUTHENTICATION])
        if failed_auth_count > 10:
            recommendations.append("Implement stronger authentication controls and account lockout policies")
        
        # Check for privilege escalation attempts
        privilege_escalation_count = len([e for e in events if e.event_type == SecurityEventType.PRIVILEGE_ESCALATION])
        if privilege_escalation_count > 0:
            recommendations.append("Review and strengthen privilege management and access controls")
        
        # Check for high-risk events
        high_risk_count = len([e for e in events if e.risk_score >= 0.8])
        if high_risk_count > len(events) * 0.1:  # More than 10% high-risk
            recommendations.append("Implement additional security monitoring and response capabilities")
        
        # Check for model-specific threats
        model_threats = len([e for e in events if e.event_type in [SecurityEventType.MODEL_TAMPERING, SecurityEventType.DATA_EXFILTRATION]])
        if model_threats > 0:
            recommendations.append("Enhance ML-specific security controls and model integrity monitoring")
        
        return recommendations
    
    async def _matches_threat_indicators(self, event: SecurityEvent, threat: ThreatIntelligence) -> bool:
        """Check if event matches threat intelligence indicators"""
        # Simplified matching logic
        event_data = f"{event.event_type.value} {event.description} {json.dumps(event.metadata)}"
        
        for indicator in threat.indicators:
            if indicator.lower() in event_data.lower():
                return True
        
        return False
    
    async def _evaluate_correlation_rule(self, rule: Dict[str, Any], event: SecurityEvent) -> bool:
        """Evaluate if event triggers correlation rule"""
        conditions = rule["conditions"]
        
        # Check event type match
        if "event_type" in conditions and conditions["event_type"] != event.event_type:
            return False
        
        # Check risk score threshold
        if "risk_score_threshold" in conditions and event.risk_score < conditions["risk_score_threshold"]:
            return False
        
        # Check count-based conditions
        if "count_threshold" in conditions and "time_window_minutes" in conditions:
            time_window = timedelta(minutes=conditions["time_window_minutes"])
            cutoff_time = datetime.now() - time_window
            
            similar_events = [
                e for e in self.security_events
                if (e.timestamp >= cutoff_time and
                    e.event_type == conditions["event_type"] and
                    e.user_id == event.user_id)
            ]
            
            if len(similar_events) < conditions["count_threshold"]:
                return False
        
        return True
    
    async def _trigger_correlation_alert(self, rule: Dict[str, Any], event: SecurityEvent):
        """Trigger alert based on correlation rule"""
        alert_data = {
            "rule_id": rule["rule_id"],
            "rule_name": rule["name"],
            "triggered_by": event.event_id,
            "threat_level": rule["threat_level"].value,
            "actions": rule["actions"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.warning(f"Correlation rule triggered: {rule['name']} by event {event.event_id}")
        
        # Execute rule actions
        for action in rule["actions"]:
            await self._execute_correlation_action(action, event, rule)
    
    async def _execute_correlation_action(self, action: str, event: SecurityEvent, rule: Dict[str, Any]):
        """Execute correlation rule action"""
        if action == "alert":
            self.logger.warning(f"SECURITY ALERT: {rule['description']} - Event: {event.event_id}")
        elif action == "block_user" and event.user_id:
            self.logger.warning(f"USER BLOCK RECOMMENDED: {event.user_id}")
        elif action == "require_additional_auth":
            self.logger.info(f"ADDITIONAL AUTH REQUIRED for user: {event.user_id}")
        # Add more actions as needed
    
    async def _update_security_metrics(self, event: SecurityEvent):
        """Update security metrics based on event"""
        timestamp = datetime.now()
        
        # Add event count metric
        self.security_metrics.append(SecurityMetric(
            metric_name="security_events_count",
            value=1.0,
            timestamp=timestamp,
            category="events"
        ))
        
        # Add risk score metric
        self.security_metrics.append(SecurityMetric(
            metric_name="security_risk_score",
            value=event.risk_score,
            timestamp=timestamp,
            category="risk",
            threshold=0.7
        ))
        
        # Keep only recent metrics (last 24 hours)
        cutoff_time = timestamp - timedelta(hours=24)
        self.security_metrics = [
            m for m in self.security_metrics
            if m.timestamp >= cutoff_time
        ]
    
    async def _generate_report_summary(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Generate summary for security report"""
        return {
            "total_events": len(events),
            "unique_users": len(set(e.user_id for e in events if e.user_id)),
            "unique_ips": len(set(e.source_ip for e in events if e.source_ip)),
            "threat_level_distribution": {
                level.value: len([e for e in events if e.threat_level == level])
                for level in ThreatLevel
            },
            "event_type_distribution": {
                event_type.value: len([e for e in events if e.event_type == event_type])
                for event_type in SecurityEventType
            }
        }
    
    def _identify_top_threats(self, events: List[SecurityEvent], top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify top threats from events"""
        threat_scores = defaultdict(float)
        threat_counts = defaultdict(int)
        
        for event in events:
            threat_type = event.event_type.value
            threat_scores[threat_type] += event.risk_score
            threat_counts[threat_type] += 1
        
        # Calculate average threat scores
        top_threats = []
        for threat_type, total_score in threat_scores.items():
            avg_score = total_score / threat_counts[threat_type]
            top_threats.append({
                "threat_type": threat_type,
                "average_risk_score": avg_score,
                "event_count": threat_counts[threat_type],
                "total_risk_score": total_score
            })
        
        # Sort by total risk score and return top N
        top_threats.sort(key=lambda x: x["total_risk_score"], reverse=True)
        return top_threats[:top_n]
    
    def _get_period_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get security metrics for a time period"""
        period_metrics = [
            m for m in self.security_metrics
            if start_time <= m.timestamp <= end_time
        ]
        
        return [
            {
                "metric_name": m.metric_name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "category": m.category
            }
            for m in period_metrics
        ]
    
    async def _analyze_user_correlation(self, user_id: str, events: List[SecurityEvent]) -> Optional[Dict[str, Any]]:
        """Analyze correlation of events for a specific user"""
        if len(events) < 2:
            return None
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        
        # Check for escalation pattern
        risk_scores = [e.risk_score for e in sorted_events]
        escalating = all(risk_scores[i] <= risk_scores[i+1] for i in range(len(risk_scores)-1))
        
        return {
            "correlation_type": "user_based",
            "user_id": user_id,
            "event_count": len(events),
            "time_span_minutes": (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds() / 60,
            "escalating_risk": escalating,
            "max_risk_score": max(risk_scores),
            "events": [e.event_id for e in sorted_events]
        }
    
    async def _analyze_ip_correlation(self, source_ip: str, events: List[SecurityEvent]) -> Optional[Dict[str, Any]]:
        """Analyze correlation of events from a specific IP"""
        if len(events) < 2:
            return None
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        
        # Check for different users from same IP
        unique_users = set(e.user_id for e in events if e.user_id)
        
        return {
            "correlation_type": "ip_based",
            "source_ip": source_ip,
            "event_count": len(events),
            "unique_users": len(unique_users),
            "time_span_minutes": (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds() / 60,
            "multi_user_access": len(unique_users) > 1,
            "events": [e.event_id for e in sorted_events]
        }


# Global instance
security_analytics = SecurityAnalytics()