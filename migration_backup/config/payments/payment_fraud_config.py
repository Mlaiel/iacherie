#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Payment Fraud Configuration Module
==========================================

Enterprise-grade payment fraud detection and prevention configuration 
for the Ainflue platform. Comprehensive fraud management with ML-based 
detection, real-time monitoring, and automated response systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import ipaddress

class FraudType(str, Enum):
    """Types of fraud"""
    CARD_FRAUD = "card_fraud"                   # Credit card fraud
    IDENTITY_THEFT = "identity_theft"           # Identity theft
    ACCOUNT_TAKEOVER = "account_takeover"       # Account takeover
    CHARGEBACK_FRAUD = "chargeback_fraud"       # Chargeback fraud
    BIN_ATTACK = "bin_attack"                   # BIN number attack
    VELOCITY_FRAUD = "velocity_fraud"           # High velocity transactions
    GEOGRAPHIC_FRAUD = "geographic_fraud"       # Geographic inconsistency
    BEHAVIORAL_FRAUD = "behavioral_fraud"       # Behavioral anomaly
    SYNTHETIC_FRAUD = "synthetic_fraud"         # Synthetic identity
    REFUND_FRAUD = "refund_fraud"              # Refund abuse
    BONUS_ABUSE = "bonus_abuse"                # Promotional abuse
    MONEY_LAUNDERING = "money_laundering"      # Money laundering

class RiskLevel(str, Enum):
    """Risk levels"""
    VERY_LOW = "very_low"       # 0-10%
    LOW = "low"                 # 11-25%
    MEDIUM = "medium"           # 26-50%
    HIGH = "high"               # 51-75%
    VERY_HIGH = "very_high"     # 76-90%
    CRITICAL = "critical"       # 91-100%

class FraudAction(str, Enum):
    """Fraud prevention actions"""
    ALLOW = "allow"                     # Allow transaction
    REVIEW = "review"                   # Manual review required
    CHALLENGE = "challenge"             # Additional verification
    BLOCK = "block"                     # Block transaction
    DECLINE = "decline"                 # Decline payment
    SUSPEND_ACCOUNT = "suspend_account" # Suspend user account
    FLAG_ACCOUNT = "flag_account"       # Flag for monitoring
    REQUIRE_VERIFICATION = "require_verification"  # Require identity verification

class FraudStatus(str, Enum):
    """Fraud case status"""
    DETECTED = "detected"               # Fraud detected
    INVESTIGATING = "investigating"     # Under investigation
    CONFIRMED = "confirmed"             # Confirmed fraud
    FALSE_POSITIVE = "false_positive"   # False positive
    RESOLVED = "resolved"               # Case resolved
    DISPUTED = "disputed"               # Customer disputed
    ESCALATED = "escalated"            # Escalated to authorities

@dataclass
class FraudRule:
    """Fraud detection rule"""
    rule_id: str
    rule_name: str
    rule_type: str
    conditions: Dict[str, Any]
    risk_score: int = 0
    action: FraudAction = FraudAction.REVIEW
    enabled: bool = True
    priority: int = 100
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def evaluate(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate rule against transaction"""
        result = {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "triggered": False,
            "risk_score": 0,
            "action": FraudAction.ALLOW,
            "details": {}
        }
        
        if not self.enabled:
            return result
        
        # Evaluate conditions
        triggered = self._evaluate_conditions(transaction_data)
        
        if triggered:
            result.update({
                "triggered": True,
                "risk_score": self.risk_score,
                "action": self.action,
                "details": {
                    "conditions_met": self.conditions,
                    "evaluation_time": datetime.now().isoformat()
                }
            })
        
        return result
    
    def _evaluate_conditions(self, data: Dict[str, Any]) -> bool:
        """Evaluate rule conditions"""
        # Implement rule evaluation logic
        return False

@dataclass
class FraudIndicator:
    """Fraud indicator"""
    indicator_id: str
    indicator_type: str
    value: str
    risk_level: RiskLevel
    confidence: float
    source: str
    detected_date: datetime = field(default_factory=datetime.now)
    expires_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if indicator is expired"""
        if self.expires_date:
            return datetime.now() > self.expires_date
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert indicator to dictionary"""
        return {
            "indicator_id": self.indicator_id,
            "indicator_type": self.indicator_type,
            "value": self.value,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence,
            "source": self.source,
            "detected_date": self.detected_date.isoformat(),
            "expires_date": self.expires_date.isoformat() if self.expires_date else None,
            "is_expired": self.is_expired(),
            "metadata": self.metadata
        }

@dataclass
class FraudIncident:
    """Fraud incident record"""
    incident_id: str
    customer_id: str
    transaction_id: Optional[str]
    fraud_type: FraudType
    risk_level: RiskLevel
    risk_score: float
    status: FraudStatus
    detected_date: datetime
    resolved_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    description: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    financial_impact: Decimal = Decimal('0')
    recovery_amount: Decimal = Decimal('0')
    investigation_notes: str = ""
    false_positive: bool = False
    
    def add_evidence(self, evidence_type: str, evidence_data: Any, source: str = "system") -> None:
        """Add evidence to incident"""
        evidence_item = {
            "evidence_id": f"ev_{len(self.evidence) + 1}",
            "evidence_type": evidence_type,
            "evidence_data": evidence_data,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        self.evidence.append(evidence_item)
    
    def add_action(self, action_type: str, action_details: str, performer: str = "system") -> None:
        """Add action to incident"""
        action_item = {
            "action_id": f"act_{len(self.actions_taken) + 1}",
            "action_type": action_type,
            "action_details": action_details,
            "performer": performer,
            "timestamp": datetime.now().isoformat()
        }
        self.actions_taken.append(action_item)
    
    def close_incident(self, resolution_notes: str = "", false_positive: bool = False) -> None:
        """Close fraud incident"""
        self.status = FraudStatus.FALSE_POSITIVE if false_positive else FraudStatus.RESOLVED
        self.resolved_date = datetime.now()
        self.false_positive = false_positive
        if resolution_notes:
            self.investigation_notes += f"\n[RESOLUTION] {resolution_notes}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary"""
        return {
            "incident_id": self.incident_id,
            "customer_id": self.customer_id,
            "transaction_id": self.transaction_id,
            "fraud_type": self.fraud_type.value,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "status": self.status.value,
            "detected_date": self.detected_date.isoformat(),
            "resolved_date": self.resolved_date.isoformat() if self.resolved_date else None,
            "assigned_to": self.assigned_to,
            "description": self.description,
            "evidence": self.evidence,
            "actions_taken": self.actions_taken,
            "financial_impact": float(self.financial_impact),
            "recovery_amount": float(self.recovery_amount),
            "investigation_notes": self.investigation_notes,
            "false_positive": self.false_positive
        }

@dataclass
class FraudDetectionConfig:
    """Fraud detection configuration"""
    enabled: bool = True
    
    # Detection engine
    detection_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_detection": True,
        "batch_analysis": True,
        "machine_learning": True,
        "rule_based_detection": True,
        "behavioral_analysis": True,
        "anomaly_detection": True,
        "pattern_recognition": True,
        "velocity_checking": True
    })
    
    # Risk scoring
    risk_scoring: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "dynamic_scoring": True,
        "weighted_factors": True,
        "time_decay": True,
        "customer_profiling": True,
        "device_fingerprinting": True,
        "geolocation_analysis": True,
        "transaction_analysis": True
    })
    
    # Machine learning
    machine_learning: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "supervised_learning": True,
        "unsupervised_learning": True,
        "ensemble_models": True,
        "model_training": True,
        "feature_engineering": True,
        "model_validation": True,
        "continuous_learning": True,
        "explainable_ai": True
    })
    
    # Real-time monitoring
    real_time_monitoring: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "streaming_analytics": True,
        "event_correlation": True,
        "threshold_monitoring": True,
        "alert_generation": True,
        "dashboard_integration": True,
        "automated_response": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get fraud detection configuration"""
        return {
            "enabled": self.enabled,
            "detection_engine": self.detection_engine,
            "risk_scoring": self.risk_scoring,
            "machine_learning": self.machine_learning,
            "real_time_monitoring": self.real_time_monitoring
        }

@dataclass
class FraudPreventionConfig:
    """Fraud prevention configuration"""
    enabled: bool = True
    
    # Prevention measures
    prevention_measures: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "transaction_limits": True,
        "velocity_controls": True,
        "geographic_restrictions": True,
        "device_restrictions": True,
        "ip_blocking": True,
        "blacklist_checking": True,
        "whitelist_enforcement": True,
        "challenge_response": True
    })
    
    # Authentication
    authentication: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "multi_factor_auth": True,
        "biometric_auth": True,
        "device_binding": True,
        "step_up_auth": True,
        "risk_based_auth": True,
        "sms_verification": True,
        "email_verification": True
    })
    
    # Device security
    device_security: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "device_fingerprinting": True,
        "device_profiling": True,
        "device_reputation": True,
        "jailbreak_detection": True,
        "emulator_detection": True,
        "malware_detection": True,
        "vpn_detection": True
    })
    
    # Behavioral controls
    behavioral_controls: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "behavioral_profiling": True,
        "session_analysis": True,
        "keystroke_dynamics": True,
        "mouse_movement": True,
        "navigation_patterns": True,
        "timing_analysis": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get fraud prevention configuration"""
        return {
            "enabled": self.enabled,
            "prevention_measures": self.prevention_measures,
            "authentication": self.authentication,
            "device_security": self.device_security,
            "behavioral_controls": self.behavioral_controls
        }

@dataclass
class FraudResponseConfig:
    """Fraud response configuration"""
    enabled: bool = True
    
    # Automated response
    automated_response: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "immediate_blocking": True,
        "account_suspension": True,
        "transaction_reversal": True,
        "notification_sending": True,
        "escalation_triggers": True,
        "evidence_collection": True,
        "reporting_generation": True
    })
    
    # Investigation workflow
    investigation_workflow: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "automatic_assignment": True,
        "priority_queues": True,
        "sla_management": True,
        "escalation_rules": True,
        "collaboration_tools": True,
        "case_management": True,
        "documentation": True
    })
    
    # Recovery actions
    recovery_actions: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "chargeback_management": True,
        "recovery_processing": True,
        "insurance_claims": True,
        "legal_actions": True,
        "customer_compensation": True,
        "asset_freezing": True
    })
    
    # Reporting
    reporting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "regulatory_reporting": True,
        "law_enforcement": True,
        "industry_sharing": True,
        "internal_reporting": True,
        "customer_notification": True,
        "audit_trails": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get fraud response configuration"""
        return {
            "enabled": self.enabled,
            "automated_response": self.automated_response,
            "investigation_workflow": self.investigation_workflow,
            "recovery_actions": self.recovery_actions,
            "reporting": self.reporting
        }

@dataclass
class FraudAnalyticsConfig:
    """Fraud analytics configuration"""
    enabled: bool = True
    
    # Analytics engine
    analytics_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_analytics": True,
        "historical_analysis": True,
        "predictive_analytics": True,
        "trend_analysis": True,
        "correlation_analysis": True,
        "statistical_analysis": True,
        "visualization": True
    })
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "detection_rate": True,
        "false_positive_rate": True,
        "response_time": True,
        "investigation_time": True,
        "recovery_rate": True,
        "financial_impact": True,
        "prevention_savings": True
    })
    
    # Reporting
    reporting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "executive_dashboards": True,
        "operational_reports": True,
        "compliance_reports": True,
        "trend_reports": True,
        "incident_reports": True,
        "performance_reports": True,
        "automated_reporting": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get fraud analytics configuration"""
        return {
            "enabled": self.enabled,
            "analytics_engine": self.analytics_engine,
            "performance_metrics": self.performance_metrics,
            "reporting": self.reporting
        }

class PaymentFraudConfiguration:
    """Main payment fraud configuration manager"""
    
    def __init__(self):
        """Initialize payment fraud configuration"""
        # Fraud configuration components
        self.fraud_detection = FraudDetectionConfig()
        self.fraud_prevention = FraudPreventionConfig()
        self.fraud_response = FraudResponseConfig()
        self.fraud_analytics = FraudAnalyticsConfig()
        
        # Fraud data storage
        self.fraud_rules: List[FraudRule] = []
        self.fraud_indicators: List[FraudIndicator] = []
        self.fraud_incidents: List[FraudIncident] = []
        
        # Risk thresholds
        self.risk_thresholds = {
            RiskLevel.VERY_LOW: (0, 10),
            RiskLevel.LOW: (11, 25),
            RiskLevel.MEDIUM: (26, 50),
            RiskLevel.HIGH: (51, 75),
            RiskLevel.VERY_HIGH: (76, 90),
            RiskLevel.CRITICAL: (91, 100)
        }
        
        # Action mapping
        self.risk_action_mapping = {
            RiskLevel.VERY_LOW: FraudAction.ALLOW,
            RiskLevel.LOW: FraudAction.ALLOW,
            RiskLevel.MEDIUM: FraudAction.REVIEW,
            RiskLevel.HIGH: FraudAction.CHALLENGE,
            RiskLevel.VERY_HIGH: FraudAction.BLOCK,
            RiskLevel.CRITICAL: FraudAction.DECLINE
        }
        
        # Global fraud settings
        self.fraud_protection_enabled = True
        self.real_time_monitoring = True
        self.machine_learning_enabled = True
        self.automatic_blocking = True
        
        # Velocity limits
        self.velocity_limits = {
            "transactions_per_minute": 10,
            "transactions_per_hour": 100,
            "transactions_per_day": 500,
            "amount_per_hour": Decimal('5000.0'),  # EUR
            "amount_per_day": Decimal('25000.0')   # EUR
        }
        
        # Geographic restrictions
        self.high_risk_countries = [
            "Unknown", "TOR", "Proxy"
        ]
        
        self.blocked_countries = []
        
        # Device restrictions
        self.device_restrictions = {
            "block_tor": True,
            "block_vpn": True,
            "block_proxy": True,
            "block_emulators": True,
            "block_jailbroken": True
        }
        
        # ML model settings
        self.ml_model_settings = {
            "model_update_frequency": "daily",
            "training_data_window": 90,  # days
            "feature_importance_threshold": 0.05,
            "model_confidence_threshold": 0.8
        }
        
        # Integration settings
        self.external_services = {
            "threat_intelligence": True,
            "device_fingerprinting": True,
            "ip_geolocation": True,
            "email_validation": True,
            "phone_validation": True,
            "identity_verification": True
        }
    
    def add_fraud_rule(self, rule_data: Dict[str, Any]) -> FraudRule:
        """Add new fraud rule"""
        
        rule = FraudRule(
            rule_id=f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            rule_name=rule_data.get("rule_name", ""),
            rule_type=rule_data.get("rule_type", "custom"),
            conditions=rule_data.get("conditions", {}),
            risk_score=rule_data.get("risk_score", 50),
            action=FraudAction(rule_data.get("action", "review")),
            enabled=rule_data.get("enabled", True),
            priority=rule_data.get("priority", 100)
        )
        
        self.fraud_rules.append(rule)
        return rule
    
    def add_fraud_indicator(self, indicator_data: Dict[str, Any]) -> FraudIndicator:
        """Add fraud indicator"""
        
        indicator = FraudIndicator(
            indicator_id=f"ind_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            indicator_type=indicator_data.get("indicator_type", ""),
            value=indicator_data.get("value", ""),
            risk_level=RiskLevel(indicator_data.get("risk_level", "medium")),
            confidence=indicator_data.get("confidence", 0.5),
            source=indicator_data.get("source", "manual"),
            expires_date=indicator_data.get("expires_date"),
            metadata=indicator_data.get("metadata", {})
        )
        
        self.fraud_indicators.append(indicator)
        return indicator
    
    async def analyze_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction for fraud"""
        
        analysis_result = {
            "transaction_id": transaction_data.get("transaction_id", ""),
            "analysis_timestamp": datetime.now().isoformat(),
            "risk_score": 0.0,
            "risk_level": RiskLevel.VERY_LOW,
            "recommended_action": FraudAction.ALLOW,
            "triggered_rules": [],
            "indicators_found": [],
            "fraud_detected": False,
            "details": {}
        }
        
        try:
            # Rule-based analysis
            rule_results = self._evaluate_fraud_rules(transaction_data)
            analysis_result["triggered_rules"] = rule_results
            
            # Indicator matching
            indicator_results = self._check_fraud_indicators(transaction_data)
            analysis_result["indicators_found"] = indicator_results
            
            # Calculate risk score
            total_risk_score = self._calculate_risk_score(rule_results, indicator_results, transaction_data)
            analysis_result["risk_score"] = total_risk_score
            
            # Determine risk level
            risk_level = self._determine_risk_level(total_risk_score)
            analysis_result["risk_level"] = risk_level
            
            # Determine recommended action
            recommended_action = self._determine_action(risk_level, rule_results)
            analysis_result["recommended_action"] = recommended_action
            
            # Check if fraud detected
            fraud_detected = (risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL] or
                            any(r.get("action") in [FraudAction.BLOCK, FraudAction.DECLINE] for r in rule_results))
            analysis_result["fraud_detected"] = fraud_detected
            
            # Create incident if fraud detected
            if fraud_detected:
                incident = await self._create_fraud_incident(transaction_data, analysis_result)
                analysis_result["incident_id"] = incident.incident_id
            
            # Additional analysis details
            analysis_result["details"] = {
                "velocity_check": self._check_velocity(transaction_data),
                "geographic_check": self._check_geography(transaction_data),
                "device_check": self._check_device(transaction_data),
                "behavioral_check": self._check_behavior(transaction_data)
            }
            
        except Exception as e:
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    async def investigate_incident(self, incident_id: str, investigator_id: str) -> Dict[str, Any]:
        """Investigate fraud incident"""
        
        incident = self._get_incident_by_id(incident_id)
        if not incident:
            return {"error": f"Incident {incident_id} not found"}
        
        investigation_result = {
            "incident_id": incident_id,
            "investigator_id": investigator_id,
            "investigation_started": datetime.now().isoformat(),
            "status": incident.status.value,
            "findings": [],
            "recommendations": []
        }
        
        # Update incident
        incident.status = FraudStatus.INVESTIGATING
        incident.assigned_to = investigator_id
        incident.add_action("investigation_started", f"Investigation assigned to {investigator_id}", investigator_id)
        
        # Gather additional evidence
        additional_evidence = await self._gather_evidence(incident)
        for evidence in additional_evidence:
            incident.add_evidence(evidence["type"], evidence["data"], "investigation")
        
        investigation_result["findings"] = additional_evidence
        investigation_result["recommendations"] = self._generate_recommendations(incident)
        
        return investigation_result
    
    def close_incident(self, incident_id: str, resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Close fraud incident"""
        
        incident = self._get_incident_by_id(incident_id)
        if not incident:
            return {"error": f"Incident {incident_id} not found"}
        
        closure_result = {
            "incident_id": incident_id,
            "closed_date": datetime.now().isoformat(),
            "resolution": resolution_data.get("resolution", "resolved"),
            "false_positive": resolution_data.get("false_positive", False)
        }
        
        incident.close_incident(
            resolution_notes=resolution_data.get("notes", ""),
            false_positive=resolution_data.get("false_positive", False)
        )
        
        # Add final action
        incident.add_action(
            "incident_closed",
            resolution_data.get("notes", "Incident resolved"),
            resolution_data.get("resolver", "system")
        )
        
        closure_result["success"] = True
        return closure_result
    
    def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud statistics"""
        
        stats = {
            "total_incidents": len(self.fraud_incidents),
            "incidents_by_status": {},
            "incidents_by_type": {},
            "incidents_by_risk_level": {},
            "total_financial_impact": 0.0,
            "total_recovery": 0.0,
            "detection_rate": 0.0,
            "false_positive_rate": 0.0,
            "average_investigation_time": 0.0
        }
        
        if not self.fraud_incidents:
            return stats
        
        total_impact = Decimal('0')
        total_recovery = Decimal('0')
        investigation_times = []
        false_positives = 0
        
        for incident in self.fraud_incidents:
            # Count by status
            status = incident.status.value
            stats["incidents_by_status"][status] = stats["incidents_by_status"].get(status, 0) + 1
            
            # Count by type
            fraud_type = incident.fraud_type.value
            stats["incidents_by_type"][fraud_type] = stats["incidents_by_type"].get(fraud_type, 0) + 1
            
            # Count by risk level
            risk_level = incident.risk_level.value
            stats["incidents_by_risk_level"][risk_level] = stats["incidents_by_risk_level"].get(risk_level, 0) + 1
            
            # Financial impact
            total_impact += incident.financial_impact
            total_recovery += incident.recovery_amount
            
            # Investigation time
            if incident.resolved_date:
                investigation_time = (incident.resolved_date - incident.detected_date).total_seconds() / 3600
                investigation_times.append(investigation_time)
            
            # False positives
            if incident.false_positive:
                false_positives += 1
        
        stats["total_financial_impact"] = float(total_impact)
        stats["total_recovery"] = float(total_recovery)
        
        if investigation_times:
            stats["average_investigation_time"] = sum(investigation_times) / len(investigation_times)
        
        stats["false_positive_rate"] = (false_positives / len(self.fraud_incidents)) * 100 if self.fraud_incidents else 0
        
        return stats
    
    def search_incidents(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search fraud incidents"""
        
        matching_incidents = []
        
        for incident in self.fraud_incidents:
            if self._matches_incident_criteria(incident, search_criteria):
                matching_incidents.append(incident.to_dict())
        
        return matching_incidents
    
    # Helper methods
    def _evaluate_fraud_rules(self, transaction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate fraud rules"""
        triggered_rules = []
        
        for rule in self.fraud_rules:
            if rule.enabled:
                result = rule.evaluate(transaction_data)
                if result["triggered"]:
                    triggered_rules.append(result)
        
        return triggered_rules
    
    def _check_fraud_indicators(self, transaction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check fraud indicators"""
        found_indicators = []
        
        # Check various data points against indicators
        check_fields = ["customer_id", "email", "ip_address", "device_id", "card_number"]
        
        for field in check_fields:
            value = transaction_data.get(field)
            if value:
                for indicator in self.fraud_indicators:
                    if not indicator.is_expired() and indicator.value == value:
                        found_indicators.append(indicator.to_dict())
        
        return found_indicators
    
    def _calculate_risk_score(self, rule_results: List[Dict[str, Any]], 
                            indicator_results: List[Dict[str, Any]], 
                            transaction_data: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        total_score = 0.0
        
        # Rule-based scores
        for rule_result in rule_results:
            total_score += rule_result.get("risk_score", 0)
        
        # Indicator-based scores
        for indicator in indicator_results:
            risk_level = indicator.get("risk_level", "low")
            confidence = indicator.get("confidence", 0.5)
            
            if risk_level == "critical":
                total_score += 50 * confidence
            elif risk_level == "very_high":
                total_score += 40 * confidence
            elif risk_level == "high":
                total_score += 30 * confidence
            elif risk_level == "medium":
                total_score += 20 * confidence
        
        # Cap at 100
        return min(total_score, 100.0)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        for risk_level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= risk_score <= max_score:
                return risk_level
        return RiskLevel.CRITICAL
    
    def _determine_action(self, risk_level: RiskLevel, rule_results: List[Dict[str, Any]]) -> FraudAction:
        """Determine recommended action"""
        # Check for explicit actions from rules
        for rule_result in rule_results:
            action = rule_result.get("action")
            if action in [FraudAction.BLOCK, FraudAction.DECLINE]:
                return FraudAction(action)
        
        # Use risk level mapping
        return self.risk_action_mapping.get(risk_level, FraudAction.REVIEW)
    
    async def _create_fraud_incident(self, transaction_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> FraudIncident:
        """Create fraud incident"""
        incident = FraudIncident(
            incident_id=f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            customer_id=transaction_data.get("customer_id", ""),
            transaction_id=transaction_data.get("transaction_id"),
            fraud_type=FraudType.CARD_FRAUD,  # Default, can be determined by analysis
            risk_level=RiskLevel(analysis_result["risk_level"]),
            risk_score=analysis_result["risk_score"],
            status=FraudStatus.DETECTED,
            detected_date=datetime.now(),
            description=f"Fraud detected with risk score {analysis_result['risk_score']}",
            financial_impact=Decimal(str(transaction_data.get("amount", "0")))
        )
        
        # Add evidence from analysis
        incident.add_evidence("analysis_result", analysis_result, "fraud_engine")
        incident.add_evidence("transaction_data", transaction_data, "payment_system")
        
        self.fraud_incidents.append(incident)
        return incident
    
    def _check_velocity(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check velocity limits"""
        return {"velocity_exceeded": False, "details": {}}
    
    def _check_geography(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check geographic restrictions"""
        return {"geographic_risk": False, "details": {}}
    
    def _check_device(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check device restrictions"""
        return {"device_risk": False, "details": {}}
    
    def _check_behavior(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check behavioral patterns"""
        return {"behavioral_risk": False, "details": {}}
    
    def _get_incident_by_id(self, incident_id: str) -> Optional[FraudIncident]:
        """Get incident by ID"""
        for incident in self.fraud_incidents:
            if incident.incident_id == incident_id:
                return incident
        return None
    
    async def _gather_evidence(self, incident: FraudIncident) -> List[Dict[str, Any]]:
        """Gather additional evidence"""
        return []
    
    def _generate_recommendations(self, incident: FraudIncident) -> List[str]:
        """Generate investigation recommendations"""
        return ["Review transaction details", "Verify customer identity", "Check device fingerprint"]
    
    def _matches_incident_criteria(self, incident: FraudIncident, criteria: Dict[str, Any]) -> bool:
        """Check if incident matches search criteria"""
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete fraud configuration"""
        return {
            "fraud_statistics": self.get_fraud_statistics(),
            "fraud_detection": self.fraud_detection.get_config(),
            "fraud_prevention": self.fraud_prevention.get_config(),
            "fraud_response": self.fraud_response.get_config(),
            "fraud_analytics": self.fraud_analytics.get_config(),
            "fraud_rules_count": len(self.fraud_rules),
            "fraud_indicators_count": len(self.fraud_indicators),
            "fraud_incidents_count": len(self.fraud_incidents),
            "global_settings": {
                "fraud_protection_enabled": self.fraud_protection_enabled,
                "real_time_monitoring": self.real_time_monitoring,
                "machine_learning_enabled": self.machine_learning_enabled,
                "automatic_blocking": self.automatic_blocking
            },
            "risk_thresholds": {k.value: v for k, v in self.risk_thresholds.items()},
            "velocity_limits": {k: float(v) if isinstance(v, Decimal) else v for k, v in self.velocity_limits.items()},
            "geographic_restrictions": {
                "high_risk_countries": self.high_risk_countries,
                "blocked_countries": self.blocked_countries
            },
            "device_restrictions": self.device_restrictions,
            "ml_model_settings": self.ml_model_settings,
            "external_services": self.external_services
        }

# Global payment fraud configuration instance
payment_fraud_config = PaymentFraudConfiguration()

# Export main classes
__all__ = [
    "PaymentFraudConfiguration",
    "FraudType",
    "RiskLevel",
    "FraudAction",
    "FraudStatus",
    "FraudRule",
    "FraudIndicator",
    "FraudIncident",
    "FraudDetectionConfig",
    "FraudPreventionConfig",
    "FraudResponseConfig",
    "FraudAnalyticsConfig",
    "payment_fraud_config"
]
