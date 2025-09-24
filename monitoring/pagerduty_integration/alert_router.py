"""
Intelligent Alert Router for Ainflue Platform
Smart routing and filtering of alerts based on context and machine learning

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import hashlib

from .pagerduty_client import PagerDutyClient, IncidentDetails, IncidentSeverity
from .escalation_manager import EscalationManager, IncidentContext, BusinessImpact

logger = logging.getLogger(__name__)


@dataclass
class AlertContext:
    """Alert context for intelligent routing"""
    alert_id: str
    alert_type: str
    source_system: str
    service_name: str
    workflow_stage: str
    severity: str
    message: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    timestamp: datetime
    fingerprint: str


@dataclass
class RoutingDecision:
    """Alert routing decision"""
    route_to_pagerduty: bool
    incident_severity: Optional[IncidentSeverity]
    escalation_level: str
    notification_channels: List[str]
    suppression_applied: bool
    reason: str
    confidence_score: float


class AlertFilter:
    """Alert filtering and suppression logic"""
    
    def __init__(self):
        """Initialize alert filter"""
        self.suppression_rules = self._load_suppression_rules()
        self.recent_alerts = deque(maxlen=1000)  # Keep last 1000 alerts
        self.suppressed_alerts = defaultdict(list)
    
    def should_suppress_alert(self, alert_context: AlertContext) -> Tuple[bool, str]:
        """
        Determine if alert should be suppressed
        
        Args:
            alert_context: Alert context information
            
        Returns:
            Tuple of (should_suppress, reason)
        """
        try:
            # Check for duplicate alerts
            if self._is_duplicate_alert(alert_context):
                return True, "Duplicate alert within suppression window"
            
            # Check maintenance windows
            if self._is_in_maintenance_window(alert_context):
                return True, "Service in maintenance window"
            
            # Check suppression rules
            for rule in self.suppression_rules:
                if self._matches_suppression_rule(alert_context, rule):
                    return True, f"Suppressed by rule: {rule['name']}"
            
            # Check alert frequency
            if self._is_alert_storm(alert_context):
                return True, "Alert storm detected - suppressing similar alerts"
            
            # Check if related to known issue
            if self._is_related_to_known_issue(alert_context):
                return True, "Related to existing incident"
            
            return False, "No suppression applied"
            
        except Exception as e:
            logger.error(f"Error in alert suppression check: {e}")
            return False, "Error in suppression logic"
    
    def _is_duplicate_alert(self, alert_context: AlertContext) -> bool:
        """Check if alert is duplicate of recent alert"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        for recent_alert in self.recent_alerts:
            if (recent_alert.fingerprint == alert_context.fingerprint and
                recent_alert.timestamp > cutoff_time):
                return True
        
        return False
    
    def _is_in_maintenance_window(self, alert_context: AlertContext) -> bool:
        """Check if service is in maintenance window"""
        # This would typically check against a maintenance schedule
        # For now, return False (no maintenance windows)
        return False
    
    def _matches_suppression_rule(self, alert_context: AlertContext, 
                                rule: Dict[str, Any]) -> bool:
        """Check if alert matches suppression rule"""
        conditions = rule.get("conditions", {})
        
        # Check service name
        if "services" in conditions:
            if alert_context.service_name not in conditions["services"]:
                return False
        
        # Check alert type
        if "alert_types" in conditions:
            if alert_context.alert_type not in conditions["alert_types"]:
                return False
        
        # Check severity
        if "severities" in conditions:
            if alert_context.severity not in conditions["severities"]:
                return False
        
        # Check labels
        if "labels" in conditions:
            for label_key, label_value in conditions["labels"].items():
                if (label_key not in alert_context.labels or
                    alert_context.labels[label_key] != label_value):
                    return False
        
        # Check time-based conditions
        if "time_conditions" in conditions:
            if not self._check_time_conditions(alert_context, conditions["time_conditions"]):
                return False
        
        return True
    
    def _is_alert_storm(self, alert_context: AlertContext) -> bool:
        """Check if alert is part of an alert storm"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        
        # Count similar alerts in last 10 minutes
        similar_count = 0
        for recent_alert in self.recent_alerts:
            if (recent_alert.timestamp > cutoff_time and
                recent_alert.service_name == alert_context.service_name and
                recent_alert.alert_type == alert_context.alert_type):
                similar_count += 1
        
        # If more than 20 similar alerts in 10 minutes, consider it a storm
        return similar_count > 20
    
    def _is_related_to_known_issue(self, alert_context: AlertContext) -> bool:
        """Check if alert is related to existing incident"""
        # This would check against open incidents in PagerDuty or incident management system
        # For now, return False
        return False
    
    def _check_time_conditions(self, alert_context: AlertContext,
                             time_conditions: Dict[str, Any]) -> bool:
        """Check time-based suppression conditions"""
        current_time = alert_context.timestamp
        
        # Check business hours suppression
        if time_conditions.get("suppress_outside_business_hours"):
            if not self._is_business_hours(current_time):
                return True
        
        # Check specific time ranges
        if "suppress_time_ranges" in time_conditions:
            for time_range in time_conditions["suppress_time_ranges"]:
                if self._is_in_time_range(current_time, time_range):
                    return True
        
        return False
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp is during business hours"""
        # Business hours: 9 AM - 6 PM, Monday-Friday UTC
        weekday = timestamp.weekday()  # 0 = Monday, 6 = Sunday
        hour = timestamp.hour
        
        return weekday < 5 and 9 <= hour < 18
    
    def _is_in_time_range(self, timestamp: datetime, 
                         time_range: Dict[str, str]) -> bool:
        """Check if timestamp is in specified time range"""
        # Simple time range check (could be enhanced for timezone support)
        start_hour = int(time_range.get("start", "0"))
        end_hour = int(time_range.get("end", "24"))
        
        return start_hour <= timestamp.hour < end_hour
    
    def _load_suppression_rules(self) -> List[Dict[str, Any]]:
        """Load alert suppression rules"""
        return [
            {
                "name": "Health Check Suppression",
                "conditions": {
                    "alert_types": ["health_check_failed"],
                    "severities": ["warning", "info"]
                },
                "description": "Suppress non-critical health check failures"
            },
            {
                "name": "Development Environment",
                "conditions": {
                    "labels": {"environment": "development"},
                    "severities": ["warning", "info"]
                },
                "description": "Suppress low-severity alerts from development"
            },
            {
                "name": "Staging Rate Limits",
                "conditions": {
                    "labels": {"environment": "staging"},
                    "alert_types": ["rate_limit_exceeded"]
                },
                "description": "Suppress rate limit alerts from staging"
            },
            {
                "name": "Off-Hours Info Alerts",
                "conditions": {
                    "severities": ["info"],
                    "time_conditions": {
                        "suppress_outside_business_hours": True
                    }
                },
                "description": "Suppress info alerts outside business hours"
            }
        ]


class IntelligentAlertRouter:
    """
    Intelligent alert routing system for Ainflue Platform
    Routes alerts to appropriate teams based on context and machine learning
    """
    
    def __init__(self):
        """Initialize intelligent alert router"""
        self.pagerduty_client = PagerDutyClient()
        self.escalation_manager = EscalationManager()
        self.alert_filter = AlertFilter()
        
        self.routing_rules = self._load_routing_rules()
        self.alert_history = deque(maxlen=5000)
        self.routing_decisions = defaultdict(list)
    
    def route_alert(self, alert_context: AlertContext) -> RoutingDecision:
        """
        Intelligently route alert based on context
        
        Args:
            alert_context: Alert context information
            
        Returns:
            Routing decision with actions taken
        """
        try:
            # First, check if alert should be suppressed
            should_suppress, suppression_reason = self.alert_filter.should_suppress_alert(alert_context)
            
            if should_suppress:
                logger.info(f"Alert suppressed: {alert_context.alert_id} - {suppression_reason}")
                return RoutingDecision(
                    route_to_pagerduty=False,
                    incident_severity=None,
                    escalation_level="suppressed",
                    notification_channels=[],
                    suppression_applied=True,
                    reason=suppression_reason,
                    confidence_score=1.0
                )
            
            # Analyze alert context and determine routing
            routing_analysis = self._analyze_alert_context(alert_context)
            
            # Determine incident severity
            incident_severity = self._determine_incident_severity(alert_context, routing_analysis)
            
            # Should route to PagerDuty?
            should_route_to_pagerduty = self._should_route_to_pagerduty(
                alert_context, incident_severity, routing_analysis
            )
            
            # Get escalation information
            incident_context = self._build_incident_context(alert_context)
            escalation_level, notification_channels = self.escalation_manager.evaluate_escalation(
                incident_context
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(alert_context, routing_analysis)
            
            # Create routing decision
            decision = RoutingDecision(
                route_to_pagerduty=should_route_to_pagerduty,
                incident_severity=incident_severity if should_route_to_pagerduty else None,
                escalation_level=escalation_level.value,
                notification_channels=notification_channels,
                suppression_applied=False,
                reason=f"Routed based on {routing_analysis['primary_factor']}",
                confidence_score=confidence_score
            )
            
            # Execute routing decision
            if should_route_to_pagerduty:
                self._create_pagerduty_incident(alert_context, incident_severity)
            
            # Send notifications
            self._send_notifications(alert_context, decision)
            
            # Record decision for learning
            self._record_routing_decision(alert_context, decision)
            
            logger.info(
                f"Alert routed: {alert_context.alert_id} -> "
                f"PagerDuty: {should_route_to_pagerduty}, "
                f"Level: {escalation_level.value}, "
                f"Confidence: {confidence_score:.2f}"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error routing alert {alert_context.alert_id}: {e}")
            # Fallback routing for errors
            return RoutingDecision(
                route_to_pagerduty=True,
                incident_severity=IncidentSeverity.ERROR,
                escalation_level="level_1",
                notification_channels=["slack-incidents"],
                suppression_applied=False,
                reason=f"Fallback routing due to error: {str(e)}",
                confidence_score=0.5
            )
    
    def _analyze_alert_context(self, alert_context: AlertContext) -> Dict[str, Any]:
        """Analyze alert context for routing decisions"""
        analysis = {
            "business_critical": False,
            "user_impact_level": "low",
            "technical_severity": alert_context.severity,
            "primary_factor": "standard",
            "routing_factors": []
        }
        
        # Analyze service criticality
        critical_services = ["api_gateway", "database", "ai_engine", "payment"]
        if alert_context.service_name in critical_services:
            analysis["business_critical"] = True
            analysis["routing_factors"].append("critical_service")
        
        # Analyze workflow stage impact
        high_impact_workflows = ["payment", "authentication", "data_protection", "ai_processing"]
        if alert_context.workflow_stage in high_impact_workflows:
            analysis["user_impact_level"] = "high"
            analysis["routing_factors"].append("high_impact_workflow")
        
        # Analyze severity
        if alert_context.severity in ["critical", "emergency"]:
            analysis["primary_factor"] = "severity"
            analysis["routing_factors"].append("high_severity")
        
        # Analyze labels for additional context
        if "user_count" in alert_context.labels:
            try:
                user_count = int(alert_context.labels["user_count"])
                if user_count > 100:
                    analysis["user_impact_level"] = "high"
                    analysis["routing_factors"].append("high_user_impact")
            except ValueError:
                pass
        
        # Check for error patterns
        error_keywords = ["timeout", "connection", "memory", "cpu", "disk"]
        if any(keyword in alert_context.message.lower() for keyword in error_keywords):
            analysis["routing_factors"].append("infrastructure_issue")
        
        return analysis
    
    def _determine_incident_severity(self, alert_context: AlertContext,
                                   routing_analysis: Dict[str, Any]) -> IncidentSeverity:
        """Determine PagerDuty incident severity"""
        
        # Map alert severity to PagerDuty severity with context
        if alert_context.severity == "critical" or routing_analysis["business_critical"]:
            return IncidentSeverity.CRITICAL
        elif alert_context.severity == "error" or routing_analysis["user_impact_level"] == "high":
            return IncidentSeverity.ERROR
        elif alert_context.severity == "warning":
            return IncidentSeverity.WARNING
        else:
            return IncidentSeverity.INFO
    
    def _should_route_to_pagerduty(self, alert_context: AlertContext,
                                 incident_severity: IncidentSeverity,
                                 routing_analysis: Dict[str, Any]) -> bool:
        """Determine if alert should be routed to PagerDuty"""
        
        # Always route critical and error incidents
        if incident_severity in [IncidentSeverity.CRITICAL, IncidentSeverity.ERROR]:
            return True
        
        # Route if business critical service
        if routing_analysis["business_critical"]:
            return True
        
        # Route if high user impact
        if routing_analysis["user_impact_level"] == "high":
            return True
        
        # Route specific alert types
        pagerduty_alert_types = [
            "service_down",
            "database_connection_failed", 
            "payment_processing_failed",
            "ai_model_failure",
            "authentication_service_down"
        ]
        if alert_context.alert_type in pagerduty_alert_types:
            return True
        
        # Don't route info/debug alerts
        if incident_severity == IncidentSeverity.INFO:
            return False
        
        # Default: route warnings from production
        return alert_context.labels.get("environment") == "production"
    
    def _build_incident_context(self, alert_context: AlertContext) -> IncidentContext:
        """Build incident context for escalation manager"""
        
        # Estimate affected users from labels or default values
        affected_users = 0
        if "user_count" in alert_context.labels:
            try:
                affected_users = int(alert_context.labels["user_count"])
            except ValueError:
                pass
        
        # Calculate duration (for now, assume new incident)
        duration_minutes = 0
        
        # Check if business hours
        business_hours = self.alert_filter._is_business_hours(alert_context.timestamp)
        
        return IncidentContext(
            service_name=alert_context.service_name,
            workflow_stage=alert_context.workflow_stage,
            severity=alert_context.severity,
            error_type=alert_context.alert_type,
            affected_users=affected_users,
            duration_minutes=duration_minutes,
            previous_escalations=[],
            business_hours=business_hours,
            custom_tags=alert_context.labels
        )
    
    def _calculate_confidence_score(self, alert_context: AlertContext,
                                  routing_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for routing decision"""
        
        base_score = 0.5
        
        # Higher confidence for well-defined services
        known_services = ["api_gateway", "database", "ai_engine", "payment", "authentication"]
        if alert_context.service_name in known_services:
            base_score += 0.2
        
        # Higher confidence for clear severity levels
        if alert_context.severity in ["critical", "error"]:
            base_score += 0.2
        
        # Higher confidence if multiple routing factors
        factor_count = len(routing_analysis["routing_factors"])
        if factor_count >= 2:
            base_score += 0.1
        
        # Higher confidence for production alerts
        if alert_context.labels.get("environment") == "production":
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _create_pagerduty_incident(self, alert_context: AlertContext,
                                 incident_severity: IncidentSeverity):
        """Create PagerDuty incident"""
        
        if not self.pagerduty_client.initialized:
            logger.warning("PagerDuty not initialized - cannot create incident")
            return
        
        # Build incident details
        incident_details = IncidentDetails(
            title=f"{alert_context.alert_type}: {alert_context.service_name}",
            summary=alert_context.message,
            severity=incident_severity,
            source=alert_context.source_system,
            service_name=alert_context.service_name,
            workflow_stage=alert_context.workflow_stage,
            custom_details={
                "alert_id": alert_context.alert_id,
                "labels": alert_context.labels,
                "annotations": alert_context.annotations,
                "fingerprint": alert_context.fingerprint
            },
            links=[
                {
                    "href": f"https://monitoring.ainflue.com/alerts/{alert_context.alert_id}",
                    "text": "View Alert Details"
                },
                {
                    "href": f"https://grafana.ainflue.com/d/{alert_context.service_name}",
                    "text": f"{alert_context.service_name} Dashboard"
                }
            ]
        )
        
        # Create incident
        incident_key = self.pagerduty_client.trigger_incident(
            incident_details, 
            dedup_key=alert_context.fingerprint
        )
        
        if incident_key:
            logger.info(f"PagerDuty incident created: {incident_key} for alert {alert_context.alert_id}")
        else:
            logger.error(f"Failed to create PagerDuty incident for alert {alert_context.alert_id}")
    
    def _send_notifications(self, alert_context: AlertContext, decision: RoutingDecision):
        """Send notifications to appropriate channels"""
        
        # This would integrate with notification systems (Slack, Email, SMS)
        for channel in decision.notification_channels:
            logger.info(f"Sending notification to {channel} for alert {alert_context.alert_id}")
            # Implementation would send actual notifications
    
    def _record_routing_decision(self, alert_context: AlertContext, decision: RoutingDecision):
        """Record routing decision for machine learning and analysis"""
        
        decision_record = {
            "timestamp": datetime.utcnow(),
            "alert_context": asdict(alert_context),
            "routing_decision": asdict(decision),
            "alert_fingerprint": alert_context.fingerprint
        }
        
        # Store in routing decisions history
        self.routing_decisions[alert_context.service_name].append(decision_record)
        
        # Keep only last 100 decisions per service
        if len(self.routing_decisions[alert_context.service_name]) > 100:
            self.routing_decisions[alert_context.service_name] = \
                self.routing_decisions[alert_context.service_name][-100:]
        
        # Add to alert history
        self.alert_history.append(alert_context)
    
    def _load_routing_rules(self) -> List[Dict[str, Any]]:
        """Load intelligent routing rules"""
        return [
            {
                "name": "Critical Service Routing",
                "conditions": {
                    "services": ["api_gateway", "database", "ai_engine"],
                    "severities": ["critical", "error"]
                },
                "actions": {
                    "route_to_pagerduty": True,
                    "escalation_level": "level_2",
                    "notification_channels": ["slack-critical", "email-oncall"]
                }
            },
            {
                "name": "Payment System Routing",
                "conditions": {
                    "workflow_stages": ["payment", "monetization"],
                    "severities": ["critical", "error", "warning"]
                },
                "actions": {
                    "route_to_pagerduty": True,
                    "escalation_level": "level_3",
                    "notification_channels": ["slack-payment", "email-business"]
                }
            },
            {
                "name": "AI Processing Routing",
                "conditions": {
                    "workflow_stages": ["ai_processing"],
                    "alert_types": ["ai_model_failure", "inference_timeout"]
                },
                "actions": {
                    "route_to_pagerduty": True,
                    "escalation_level": "level_2",
                    "notification_channels": ["slack-ai-team", "email-ai-leads"]
                }
            }
        ]


# Global intelligent alert router instance
intelligent_alert_router = IntelligentAlertRouter()