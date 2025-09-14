"""
Escalation Manager for Ainflue Platform
Intelligent incident escalation and routing based on business rules

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


class EscalationLevel(Enum):
    """Escalation levels for incidents"""
    LEVEL_1 = "level_1"  # DevOps on-call
    LEVEL_2 = "level_2"  # Senior DevOps + Team Lead
    LEVEL_3 = "level_3"  # Engineering Manager + Business Team
    LEVEL_4 = "level_4"  # C-Level executives


class BusinessImpact(Enum):
    """Business impact assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EscalationRule:
    """Escalation rule configuration"""
    name: str
    conditions: Dict[str, Any]
    escalation_level: EscalationLevel
    timeout_minutes: int
    notification_channels: List[str]
    business_impact: BusinessImpact
    auto_escalate: bool = True


@dataclass
class IncidentContext:
    """Context information for escalation decisions"""
    service_name: str
    workflow_stage: str
    severity: str
    error_type: str
    affected_users: int
    duration_minutes: int
    previous_escalations: List[str]
    business_hours: bool
    custom_tags: Dict[str, str]


class EscalationManager:
    """
    Intelligent escalation manager for Ainflue Platform
    Manages incident escalation based on business rules and context
    """
    
    def __init__(self) -> None:
        """Initialize escalation manager with business rules"""
        self.escalation_rules = self._load_escalation_rules()
        self.escalation_history = defaultdict(list)
        self.business_hours = {
            'start': 9,  # 9 AM
            'end': 18,   # 6 PM
            'timezone': 'UTC',
            'weekdays_only': True
        }
    
    def evaluate_escalation(self, incident_context: IncidentContext) -> Tuple[EscalationLevel, List[str]]:
        """
        Evaluate appropriate escalation level for incident
        
        Args:
            incident_context: Context information about the incident
            
        Returns:
            Tuple of (escalation_level, notification_channels)
        """
        try:
            # Assess business impact
            business_impact = self._assess_business_impact(incident_context)
            
            # Find matching escalation rules
            matching_rules = self._find_matching_rules(incident_context, business_impact)
            
            if not matching_rules:
                # Default escalation for unmatched incidents
                return EscalationLevel.LEVEL_1, ["slack-general"]
            
            # Select highest priority rule
            selected_rule = max(matching_rules, key=lambda r: r.escalation_level.value)
            
            # Check if additional escalation is needed based on duration
            escalation_level = self._adjust_for_duration(
                selected_rule.escalation_level, 
                incident_context.duration_minutes
            )
            
            # Get appropriate notification channels
            notification_channels = self._get_notification_channels(
                escalation_level, 
                incident_context.business_hours,
                selected_rule.notification_channels
            )
            
            # Record escalation decision
            self._record_escalation(incident_context, escalation_level, selected_rule.name)
            
            logger.info(
                f"Escalation determined: {escalation_level.value} for {incident_context.service_name} "
                f"(impact: {business_impact.value}, duration: {incident_context.duration_minutes}m)"
            )
            
            return escalation_level, notification_channels
            
        except Exception as e:
            logger.error(f"Error evaluating escalation: {e}")
            # Fallback to safe escalation
            return EscalationLevel.LEVEL_2, ["slack-incidents", "email-oncall"]
    
    def should_auto_escalate(self, incident_key: str, 
                           current_level: EscalationLevel,
                           incident_context: IncidentContext) -> bool:
        """
        Determine if incident should be auto-escalated
        
        Args:
            incident_key: Unique incident identifier
            current_level: Current escalation level
            incident_context: Current incident context
            
        Returns:
            True if incident should be escalated
        """
        try:
            # Check escalation history
            escalations = self.escalation_history.get(incident_key, [])
            
            if not escalations:
                return False
            
            last_escalation = escalations[-1]
            time_since_escalation = (datetime.utcnow() - last_escalation['timestamp']).total_seconds() / 60
            
            # Get auto-escalation rules for current level
            auto_escalation_rules = self._get_auto_escalation_rules(current_level)
            
            for rule in auto_escalation_rules:
                if (time_since_escalation >= rule['timeout_minutes'] and 
                    self._matches_auto_escalation_criteria(rule, incident_context)):
                    logger.info(f"Auto-escalation triggered for {incident_key}: {rule['name']}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking auto-escalation: {e}")
            return False
    
    def get_escalation_path(self, incident_context: IncidentContext) -> List[Dict[str, Any]]:
        """
        Get complete escalation path for incident type
        
        Args:
            incident_context: Incident context
            
        Returns:
            List of escalation steps with timings
        """
        try:
            business_impact = self._assess_business_impact(incident_context)
            
            escalation_path = []
            
            # Define escalation path based on business impact
            if business_impact == BusinessImpact.CRITICAL:
                escalation_path = [
                    {
                        "level": EscalationLevel.LEVEL_1,
                        "timeout_minutes": 5,
                        "description": "Immediate DevOps response team",
                        "channels": ["slack-critical", "sms-oncall"]
                    },
                    {
                        "level": EscalationLevel.LEVEL_2,
                        "timeout_minutes": 10,
                        "description": "Senior engineering team + Team leads",
                        "channels": ["slack-critical", "email-senior", "sms-leads"]
                    },
                    {
                        "level": EscalationLevel.LEVEL_3,
                        "timeout_minutes": 15,
                        "description": "Engineering management + Business team",
                        "channels": ["slack-management", "email-business", "phone-managers"]
                    },
                    {
                        "level": EscalationLevel.LEVEL_4,
                        "timeout_minutes": 30,
                        "description": "Executive team notification",
                        "channels": ["email-executives", "phone-ceo"]
                    }
                ]
            elif business_impact == BusinessImpact.HIGH:
                escalation_path = [
                    {
                        "level": EscalationLevel.LEVEL_1,
                        "timeout_minutes": 10,
                        "description": "DevOps team response",
                        "channels": ["slack-incidents", "email-oncall"]
                    },
                    {
                        "level": EscalationLevel.LEVEL_2,
                        "timeout_minutes": 20,
                        "description": "Senior team + leads",
                        "channels": ["slack-senior", "email-leads"]
                    },
                    {
                        "level": EscalationLevel.LEVEL_3,
                        "timeout_minutes": 45,
                        "description": "Management notification",
                        "channels": ["slack-management", "email-managers"]
                    }
                ]
            else:  # MEDIUM or LOW impact
                escalation_path = [
                    {
                        "level": EscalationLevel.LEVEL_1,
                        "timeout_minutes": 15,
                        "description": "Standard DevOps response",
                        "channels": ["slack-general", "email-oncall"]
                    },
                    {
                        "level": EscalationLevel.LEVEL_2,
                        "timeout_minutes": 60,
                        "description": "Team lead notification",
                        "channels": ["slack-leads", "email-leads"]
                    }
                ]
            
            return escalation_path
            
        except Exception as e:
            logger.error(f"Error getting escalation path: {e}")
            return []
    
    def _assess_business_impact(self, incident_context: IncidentContext) -> BusinessImpact:
        """Assess business impact of incident"""
        
        # Critical impact scenarios
        if (incident_context.severity == "critical" or 
            incident_context.affected_users > 1000 or
            incident_context.workflow_stage in ["payment", "authentication", "data_protection"]):
            return BusinessImpact.CRITICAL
        
        # High impact scenarios
        if (incident_context.severity == "error" and incident_context.affected_users > 100 or
            incident_context.workflow_stage in ["ai_processing", "content_upload", "monetization"] or
            incident_context.service_name in ["api_gateway", "database", "ai_engine"]):
            return BusinessImpact.HIGH
        
        # Medium impact scenarios
        if (incident_context.severity in ["warning", "error"] or
            incident_context.workflow_stage in ["collaboration", "analytics", "seo_optimization"]):
            return BusinessImpact.MEDIUM
        
        # Default to low impact
        return BusinessImpact.LOW
    
    def _find_matching_rules(self, incident_context: IncidentContext, 
                           business_impact: BusinessImpact) -> List[EscalationRule]:
        """Find escalation rules matching incident context"""
        matching_rules = []
        
        for rule in self.escalation_rules:
            if self._rule_matches_context(rule, incident_context, business_impact):
                matching_rules.append(rule)
        
        return matching_rules
    
    def _rule_matches_context(self, rule: EscalationRule, 
                            incident_context: IncidentContext,
                            business_impact: BusinessImpact) -> bool:
        """Check if escalation rule matches incident context"""
        conditions = rule.conditions
        
        # Check business impact
        if "min_business_impact" in conditions:
            impact_levels = ["low", "medium", "high", "critical"]
            min_impact_idx = impact_levels.index(conditions["min_business_impact"])
            current_impact_idx = impact_levels.index(business_impact.value)
            if current_impact_idx < min_impact_idx:
                return False
        
        # Check service name
        if "services" in conditions:
            if incident_context.service_name not in conditions["services"]:
                return False
        
        # Check workflow stage
        if "workflow_stages" in conditions:
            if incident_context.workflow_stage not in conditions["workflow_stages"]:
                return False
        
        # Check severity
        if "severities" in conditions:
            if incident_context.severity not in conditions["severities"]:
                return False
        
        # Check affected users threshold
        if "min_affected_users" in conditions:
            if incident_context.affected_users < conditions["min_affected_users"]:
                return False
        
        # Check custom tags
        if "tags" in conditions:
            for tag_key, tag_value in conditions["tags"].items():
                if (tag_key not in incident_context.custom_tags or 
                    incident_context.custom_tags[tag_key] != tag_value):
                    return False
        
        return True
    
    def _adjust_for_duration(self, base_level: EscalationLevel, 
                           duration_minutes: int) -> EscalationLevel:
        """Adjust escalation level based on incident duration"""
        
        # Auto-escalate based on duration
        if duration_minutes > 60:  # 1 hour
            if base_level == EscalationLevel.LEVEL_1:
                return EscalationLevel.LEVEL_2
            elif base_level == EscalationLevel.LEVEL_2:
                return EscalationLevel.LEVEL_3
        
        if duration_minutes > 120:  # 2 hours
            if base_level in [EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2]:
                return EscalationLevel.LEVEL_3
            elif base_level == EscalationLevel.LEVEL_3:
                return EscalationLevel.LEVEL_4
        
        return base_level
    
    def _get_notification_channels(self, escalation_level: EscalationLevel,
                                 business_hours: bool,
                                 rule_channels: List[str]) -> List[str]:
        """Get appropriate notification channels for escalation level"""
        
        base_channels = {
            EscalationLevel.LEVEL_1: ["slack-devops", "email-oncall"],
            EscalationLevel.LEVEL_2: ["slack-devops", "slack-senior", "email-oncall", "email-leads"],
            EscalationLevel.LEVEL_3: ["slack-devops", "slack-management", "email-managers", "email-business"],
            EscalationLevel.LEVEL_4: ["slack-executives", "email-executives", "sms-ceo"]
        }
        
        channels = base_channels.get(escalation_level, ["slack-general"])
        
        # Add rule-specific channels
        channels.extend(rule_channels)
        
        # Add urgent channels for non-business hours critical incidents
        if not business_hours and escalation_level in [EscalationLevel.LEVEL_3, EscalationLevel.LEVEL_4]:
            channels.extend(["sms-oncall", "phone-managers"])
        
        # Remove duplicates and return
        return list(set(channels))
    
    def _record_escalation(self, incident_context -> None: IncidentContext,
                          escalation_level -> None: EscalationLevel,
                          rule_name -> None: str) -> None:
        """Record escalation decision for tracking"""
        incident_key = f"{incident_context.service_name}:{incident_context.workflow_stage}"
        
        escalation_record = {
            "timestamp": datetime.utcnow(),
            "level": escalation_level.value,
            "rule": rule_name,
            "context": {
                "severity": incident_context.severity,
                "affected_users": incident_context.affected_users,
                "duration_minutes": incident_context.duration_minutes
            }
        }
        
        self.escalation_history[incident_key].append(escalation_record)
        
        # Keep only last 10 escalations per incident type
        if len(self.escalation_history[incident_key]) > 10:
            self.escalation_history[incident_key] = self.escalation_history[incident_key][-10:]
    
    def _get_auto_escalation_rules(self, current_level: EscalationLevel) -> List[Dict[str, Any]]:
        """Get auto-escalation rules for current level"""
        
        auto_rules = {
            EscalationLevel.LEVEL_1: [
                {
                    "name": "Level 1 timeout",
                    "timeout_minutes": 15,
                    "conditions": {"severity": ["critical", "error"]}
                }
            ],
            EscalationLevel.LEVEL_2: [
                {
                    "name": "Level 2 timeout",
                    "timeout_minutes": 30,
                    "conditions": {"severity": ["critical"]}
                }
            ],
            EscalationLevel.LEVEL_3: [
                {
                    "name": "Level 3 timeout",
                    "timeout_minutes": 60,
                    "conditions": {"severity": ["critical"]}
                }
            ]
        }
        
        return auto_rules.get(current_level, [])
    
    def _matches_auto_escalation_criteria(self, rule: Dict[str, Any],
                                        incident_context: IncidentContext) -> bool:
        """Check if incident matches auto-escalation criteria"""
        conditions = rule.get("conditions", {})
        
        # Check severity
        if "severity" in conditions:
            if incident_context.severity not in conditions["severity"]:
                return False
        
        # Check affected users
        if "min_affected_users" in conditions:
            if incident_context.affected_users < conditions["min_affected_users"]:
                return False
        
        return True
    
    def _load_escalation_rules(self) -> List[EscalationRule]:
        """Load escalation rules configuration"""
        
        return [
            # Critical AI engine failures
            EscalationRule(
                name="AI Engine Critical",
                conditions={
                    "services": ["ai_engine"],
                    "severities": ["critical", "error"],
                    "min_business_impact": "high"
                },
                escalation_level=EscalationLevel.LEVEL_2,
                timeout_minutes=10,
                notification_channels=["slack-ai-team", "email-ai-leads"],
                business_impact=BusinessImpact.HIGH,
                auto_escalate=True
            ),
            
            # Payment system issues
            EscalationRule(
                name="Payment Critical",
                conditions={
                    "workflow_stages": ["payment", "monetization"],
                    "severities": ["critical", "error"]
                },
                escalation_level=EscalationLevel.LEVEL_3,
                timeout_minutes=5,
                notification_channels=["slack-payment", "email-business", "sms-finance"],
                business_impact=BusinessImpact.CRITICAL,
                auto_escalate=True
            ),
            
            # Data protection incidents
            EscalationRule(
                name="Data Protection",
                conditions={
                    "workflow_stages": ["data_protection", "authentication"],
                    "severities": ["critical", "error"]
                },
                escalation_level=EscalationLevel.LEVEL_3,
                timeout_minutes=5,
                notification_channels=["slack-security", "email-security", "sms-security"],
                business_impact=BusinessImpact.CRITICAL,
                auto_escalate=True
            ),
            
            # High user impact
            EscalationRule(
                name="High User Impact",
                conditions={
                    "min_affected_users": 500,
                    "severities": ["critical", "error"]
                },
                escalation_level=EscalationLevel.LEVEL_2,
                timeout_minutes=10,
                notification_channels=["slack-user-experience", "email-product"],
                business_impact=BusinessImpact.HIGH,
                auto_escalate=True
            ),
            
            # Database issues
            EscalationRule(
                name="Database Critical",
                conditions={
                    "services": ["database", "postgresql", "redis"],
                    "severities": ["critical", "error"]
                },
                escalation_level=EscalationLevel.LEVEL_2,
                timeout_minutes=10,
                notification_channels=["slack-database", "email-dba"],
                business_impact=BusinessImpact.HIGH,
                auto_escalate=True
            ),
            
            # Standard escalation
            EscalationRule(
                name="Standard Escalation",
                conditions={
                    "min_business_impact": "low"
                },
                escalation_level=EscalationLevel.LEVEL_1,
                timeout_minutes=20,
                notification_channels=["slack-general"],
                business_impact=BusinessImpact.MEDIUM,
                auto_escalate=False
            )
        ]


# Global escalation manager instance
escalation_manager = EscalationManager()