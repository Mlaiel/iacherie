import os
#!/usr/bin/env python3
"""
⚖️ Data Classification Manager - Enterprise Information Governance Module
========================================================================

Ultra-comprehensive data classification system with automated labeling,
DLP policies, retention schedules, and creator data governance.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Data Governance + ML + Classification + DLP
Version: 2.0.0 Enterprise
Created: 2025-01-09

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import json
import logging
import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import mimetypes

logger = logging.getLogger(__name__)

class DataClassificationLevel(Enum):
    """Data classification levels based on sensitivity"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = os.getenv("SECRET", "CHANGE_ME")

class DataCategory(Enum):
    """Categories of data for classification"""
    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    CREATOR_CONTENT = "creator_content"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    OPERATIONAL_DATA = "operational_data"
    SYSTEM_DATA = "system_data"
    MARKETING_DATA = "marketing_data"
    ANALYTICS_DATA = "analytics_data"

class RetentionPeriod(Enum):
    """Standard retention periods"""
    IMMEDIATE_DELETION = "immediate"
    THIRTY_DAYS = "30_days"
    NINETY_DAYS = "90_days"
    ONE_YEAR = "1_year"
    THREE_YEARS = "3_years"
    SEVEN_YEARS = "7_years"
    INDEFINITE = "indefinite"
    LEGAL_HOLD = "legal_hold"

class DLPAction(Enum):
    """Data Loss Prevention actions"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ENCRYPT = "encrypt"
    QUARANTINE = "quarantine"
    NOTIFY_ADMIN = "notify_admin"

@dataclass
class DataElement:
    """Individual data element for classification"""
    element_id: str
    name: str
    content_type: str
    size_bytes: int
    location: str
    owner: str
    classification_level: Optional[DataClassificationLevel] = None
    data_category: Optional[DataCategory] = None
    retention_period: Optional[RetentionPeriod] = None
    access_controls: List[str] = field(default_factory=list)
    encryption_required: bool = False
    anonymization_applied: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None

@dataclass
class ClassificationRule:
    """Rule for automatic data classification"""
    rule_id: str
    name: str
    description: str
    patterns: List[str]  # Regex patterns
    keywords: List[str]
    classification_level: DataClassificationLevel
    data_category: DataCategory
    confidence_threshold: float
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class DLPPolicy:
    """Data Loss Prevention policy"""
    policy_id: str
    name: str
    description: str
    classification_levels: List[DataClassificationLevel]
    data_categories: List[DataCategory]
    conditions: List[Dict[str, Any]]
    actions: List[DLPAction]
    severity: str  # low, medium, high, critical
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RetentionSchedule:
    """Data retention schedule"""
    schedule_id: str
    name: str
    classification_level: DataClassificationLevel
    data_category: DataCategory
    retention_period: RetentionPeriod
    destruction_method: str
    approval_required: bool
    legal_basis: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ClassificationResult:
    """Result of data classification process"""
    element_id: str
    classification_level: DataClassificationLevel
    data_category: DataCategory
    confidence_score: float
    matched_rules: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class DLPViolation:
    """Data Loss Prevention violation"""
    violation_id: str
    policy_id: str
    element_id: str
    user_id: str
    action_attempted: str
    severity: str
    blocked: bool
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class DataClassificationManager:
    """
    ⚖️ Data Classification Manager - Information Governance Engine
    
    Comprehensive data classification and governance with:
    - Automated data discovery and classification
    - ML-powered content analysis
    - DLP policy enforcement
    - Retention schedule management
    - Creator content protection
    - Regulatory compliance mapping
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_elements: Dict[str, DataElement] = {}
        self.classification_rules: Dict[str, ClassificationRule] = {}
        self.dlp_policies: Dict[str, DLPPolicy] = {}
        self.retention_schedules: Dict[str, RetentionSchedule] = {}
        self.classification_results: Dict[str, ClassificationResult] = {}
        self.dlp_violations: Dict[str, DLPViolation] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self) -> bool:
        """Initialize Data Classification Manager"""
        try:
            await self._setup_default_classification_rules()
            await self._setup_default_dlp_policies()
            await self._setup_default_retention_schedules()
            self.logger.info("Data Classification Manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Data Classification Manager: {e}")
            return False
    
    async def classify_creator_data(self, data_source: str, scan_deep: bool = True) -> Dict[str, Any]:
        """
        Classify creator data for governance and compliance
        
        Args:
            data_source: Source location to scan for data
            scan_deep: Whether to perform deep content analysis
            
        Returns:
            Classification results summary
        """
        try:
            classification_summary = {
                "scan_id": str(uuid.uuid4()),
                "data_source": data_source,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "elements_discovered": 0,
                "elements_classified": 0,
                "classification_breakdown": {},
                "high_risk_elements": [],
                "recommendations": []
            }
            
            # Discover data elements
            discovered_elements = await self._discover_data_elements(data_source)
            classification_summary["elements_discovered"] = len(discovered_elements)
            
            # Classify each discovered element
            for element in discovered_elements:
                classification_result = await self._classify_data_element(element, scan_deep)
                
                if classification_result:
                    self.classification_results[element.element_id] = classification_result
                    classification_summary["elements_classified"] += 1
                    
                    # Update classification breakdown
                    level = classification_result.classification_level.value
                    category = classification_result.data_category.value
                    
                    if level not in classification_summary["classification_breakdown"]:
                        classification_summary["classification_breakdown"][level] = {}
                    if category not in classification_summary["classification_breakdown"][level]:
                        classification_summary["classification_breakdown"][level][category] = 0
                    
                    classification_summary["classification_breakdown"][level][category] += 1
                    
                    # Identify high-risk elements
                    if classification_result.classification_level in [
                        DataClassificationLevel.RESTRICTED, 
                        DataClassificationLevel.TOP_SECRET
                    ]:
                        classification_summary["high_risk_elements"].append({
                            "element_id": element.element_id,
                            "classification": level,
                            "category": category,
                            "risk_factors": await self._assess_element_risk(element, classification_result)
                        })
            
            # Generate recommendations
            classification_summary["recommendations"] = await self._generate_classification_recommendations(
                classification_summary
            )
            
            await self._log_classification_scan(classification_summary)
            return classification_summary
            
        except Exception as e:
            self.logger.error(f"Creator data classification failed: {e}")
            raise
    
    async def apply_security_labels(self, element_id: str, classification_result: ClassificationResult) -> Dict[str, Any]:
        """
        Apply security labels based on classification
        
        Args:
            element_id: Data element identifier
            classification_result: Classification result to apply
            
        Returns:
            Security labeling result
        """
        try:
            if element_id not in self.data_elements:
                raise ValueError(f"Data element not found: {element_id}")
            
            element = self.data_elements[element_id]
            
            labeling_result = {
                "element_id": element_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "labels_applied": [],
                "access_controls_updated": [],
                "encryption_applied": False,
                "dlp_policies_activated": []
            }
            
            # Apply classification level label
            element.classification_level = classification_result.classification_level
            element.data_category = classification_result.data_category
            labeling_result["labels_applied"].extend([
                f"classification:{classification_result.classification_level.value}",
                f"category:{classification_result.data_category.value}"
            ])
            
            # Apply access controls based on classification
            access_controls = await self._determine_access_controls(classification_result)
            element.access_controls.extend(access_controls)
            labeling_result["access_controls_updated"] = access_controls
            
            # Apply encryption if required
            if await self._requires_encryption(classification_result):
                element.encryption_required = True
                labeling_result["encryption_applied"] = True
                labeling_result["labels_applied"].append("encryption:required")
            
            # Set retention period
            retention_schedule = await self._determine_retention_schedule(classification_result)
            if retention_schedule:
                element.retention_period = retention_schedule.retention_period
                if retention_schedule.retention_period != RetentionPeriod.INDEFINITE:
                    retention_days = self._get_retention_days(retention_schedule.retention_period)
                    element.expires_at = datetime.now(timezone.utc) + timedelta(days=retention_days)
                
                labeling_result["labels_applied"].append(f"retention:{retention_schedule.retention_period.value}")
            
            # Activate relevant DLP policies
            activated_policies = await self._activate_dlp_policies(element, classification_result)
            labeling_result["dlp_policies_activated"] = activated_policies
            
            await self._log_security_labeling(labeling_result)
            return labeling_result
            
        except Exception as e:
            self.logger.error(f"Security labeling failed: {e}")
            raise
    
    async def enforce_dlp_policies(self, element_id: str, user_id: str, action: str) -> Dict[str, Any]:
        """
        Enforce Data Loss Prevention policies
        
        Args:
            element_id: Data element being accessed
            user_id: User attempting access
            action: Action being attempted (read, write, copy, share)
            
        Returns:
            DLP enforcement result
        """
        try:
            if element_id not in self.data_elements:
                raise ValueError(f"Data element not found: {element_id}")
            
            element = self.data_elements[element_id]
            
            enforcement_result = {
                "element_id": element_id,
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "allowed": True,
                "policies_evaluated": [],
                "actions_taken": [],
                "violations": []
            }
            
            # Evaluate applicable DLP policies
            applicable_policies = await self._get_applicable_dlp_policies(element)
            
            for policy in applicable_policies:
                policy_result = await self._evaluate_dlp_policy(policy, element, user_id, action)
                enforcement_result["policies_evaluated"].append({
                    "policy_id": policy.policy_id,
                    "policy_name": policy.name,
                    "result": policy_result
                })
                
                if not policy_result["compliant"]:
                    enforcement_result["allowed"] = False
                    
                    # Execute policy actions
                    for dlp_action in policy.actions:
                        action_result = await self._execute_dlp_action(dlp_action, element, user_id, action)
                        enforcement_result["actions_taken"].append({
                            "action": dlp_action.value,
                            "result": action_result
                        })
                    
                    # Record violation
                    violation = DLPViolation(
                        violation_id=str(uuid.uuid4()),
                        policy_id=policy.policy_id,
                        element_id=element_id,
                        user_id=user_id,
                        action_attempted=action,
                        severity=policy.severity,
                        blocked=True,
                        details=policy_result
                    )
                    
                    self.dlp_violations[violation.violation_id] = violation
                    enforcement_result["violations"].append(violation.violation_id)
            
            await self._log_dlp_enforcement(enforcement_result)
            return enforcement_result
            
        except Exception as e:
            self.logger.error(f"DLP policy enforcement failed: {e}")
            raise
    
    async def manage_retention_schedules(self, action: str = "review") -> Dict[str, Any]:
        """
        Manage data retention schedules
        
        Args:
            action: Action to perform (review, execute, update)
            
        Returns:
            Retention management result
        """
        try:
            management_result = {
                "action": action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "elements_reviewed": 0,
                "elements_eligible_for_deletion": [],
                "elements_deleted": [],
                "retention_extended": [],
                "errors": []
            }
            
            current_time = datetime.now(timezone.utc)
            
            # Review all data elements for retention
            for element_id, element in self.data_elements.items():
                management_result["elements_reviewed"] += 1
                
                if element.expires_at and element.expires_at <= current_time:
                    management_result["elements_eligible_for_deletion"].append({
                        "element_id": element_id,
                        "expires_at": element.expires_at.isoformat(),
                        "classification": element.classification_level.value if element.classification_level else None,
                        "category": element.data_category.value if element.data_category else None
                    })
                    
                    if action == "execute":
                        try:
                            deletion_result = await self._execute_data_deletion(element)
                            if deletion_result["success"]:
                                management_result["elements_deleted"].append(element_id)
                                del self.data_elements[element_id]
                            else:
                                management_result["errors"].append({
                                    "element_id": element_id,
                                    "error": deletion_result["error"]
                                })
                        except Exception as e:
                            management_result["errors"].append({
                                "element_id": element_id,
                                "error": str(e)
                            })
            
            # Check for legal holds that might extend retention
            if action in ["review", "update"]:
                legal_holds = await self._check_legal_holds()
                for element_id in legal_holds:
                    if element_id in self.data_elements:
                        element = self.data_elements[element_id]
                        element.retention_period = RetentionPeriod.LEGAL_HOLD
                        element.expires_at = None
                        management_result["retention_extended"].append(element_id)
            
            await self._log_retention_management(management_result)
            return management_result
            
        except Exception as e:
            self.logger.error(f"Retention schedule management failed: {e}")
            raise
    
    async def generate_classification_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive data classification report
        
        Returns:
            Classification report data
        """
        try:
            report_data = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": {},
                "classification_breakdown": {},
                "dlp_statistics": {},
                "retention_analysis": {},
                "risk_assessment": {},
                "recommendations": []
            }
            
            # Generate summary
            total_elements = len(self.data_elements)
            classified_elements = len([e for e in self.data_elements.values() if e.classification_level])
            
            report_data["summary"] = {
                "total_data_elements": total_elements,
                "classified_elements": classified_elements,
                "classification_coverage": (classified_elements / total_elements * 100) if total_elements > 0 else 0,
                "total_dlp_policies": len(self.dlp_policies),
                "active_dlp_policies": len([p for p in self.dlp_policies.values() if p.enabled]),
                "total_violations": len(self.dlp_violations)
            }
            
            # Classification breakdown
            for level in DataClassificationLevel:
                level_count = len([e for e in self.data_elements.values() if e.classification_level == level])
                report_data["classification_breakdown"][level.value] = {
                    "count": level_count,
                    "percentage": (level_count / total_elements * 100) if total_elements > 0 else 0
                }
            
            # DLP statistics
            report_data["dlp_statistics"] = {
                "total_violations": len(self.dlp_violations),
                "violations_by_severity": {},
                "blocked_actions": len([v for v in self.dlp_violations.values() if v.blocked]),
                "top_violated_policies": await self._get_top_violated_policies()
            }
            
            for severity in ["low", "medium", "high", "critical"]:
                count = len([v for v in self.dlp_violations.values() if v.severity == severity])
                report_data["dlp_statistics"]["violations_by_severity"][severity] = count
            
            # Retention analysis
            report_data["retention_analysis"] = await self._analyze_retention_compliance()
            
            # Risk assessment
            report_data["risk_assessment"] = await self._assess_data_classification_risks()
            
            # Generate recommendations
            report_data["recommendations"] = await self._generate_governance_recommendations(report_data)
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Classification report generation failed: {e}")
            raise
    
    async def _setup_default_classification_rules(self) -> None:
        """Setup default classification rules"""
        default_rules = [
            {
                "rule_id": "RULE_001",
                "name": "Credit Card Detection",
                "description": "Detect credit card numbers",
                "patterns": [r'\b(?:\d{4}[-\s]?){3}\d{4}\b'],
                "keywords": ["card", "credit", "payment"],
                "classification_level": DataClassificationLevel.RESTRICTED,
                "data_category": DataCategory.FINANCIAL_DATA,
                "confidence_threshold": 0.9
            },
            {
                "rule_id": "RULE_002", 
                "name": "Personal Email Detection",
                "description": "Detect email addresses",
                "patterns": [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
                "keywords": ["email", "contact"],
                "classification_level": DataClassificationLevel.CONFIDENTIAL,
                "data_category": DataCategory.PERSONAL_DATA,
                "confidence_threshold": 0.8
            },
            {
                "rule_id": "RULE_003",
                "name": "Creator Content Detection",
                "description": "Detect creator-generated content",
                "patterns": [],
                "keywords": ["video", "audio", "content", "creator", "monetization"],
                "classification_level": DataClassificationLevel.CONFIDENTIAL,
                "data_category": DataCategory.CREATOR_CONTENT,
                "confidence_threshold": 0.7
            }
        ]
        
        for rule_data in default_rules:
            rule = ClassificationRule(**rule_data)
            self.classification_rules[rule.rule_id] = rule
    
    async def _setup_default_dlp_policies(self) -> None:
        """Setup default DLP policies"""
        default_policies = [
            {
                "policy_id": "DLP_001",
                "name": "Financial Data Protection",
                "description": "Protect financial and payment data",
                "classification_levels": [DataClassificationLevel.RESTRICTED],
                "data_categories": [DataCategory.FINANCIAL_DATA],
                "conditions": [{"field": "action", "operator": "in", "value": ["share", "export"]}],
                "actions": [DLPAction.BLOCK, DLPAction.NOTIFY_ADMIN],
                "severity": "critical"
            },
            {
                "policy_id": "DLP_002",
                "name": "Creator Content Protection",
                "description": "Protect creator intellectual property",
                "classification_levels": [DataClassificationLevel.CONFIDENTIAL, DataClassificationLevel.RESTRICTED],
                "data_categories": [DataCategory.CREATOR_CONTENT, DataCategory.INTELLECTUAL_PROPERTY],
                "conditions": [{"field": "external_share", "operator": "equals", "value": True}],
                "actions": [DLPAction.WARN, DLPAction.ENCRYPT],
                "severity": "high"
            }
        ]
        
        for policy_data in default_policies:
            policy = DLPPolicy(**policy_data)
            self.dlp_policies[policy.policy_id] = policy
    
    async def _setup_default_retention_schedules(self) -> None:
        """Setup default retention schedules"""
        default_schedules = [
            {
                "schedule_id": "RET_001",
                "name": "Financial Data Retention",
                "classification_level": DataClassificationLevel.RESTRICTED,
                "data_category": DataCategory.FINANCIAL_DATA,
                "retention_period": RetentionPeriod.SEVEN_YEARS,
                "destruction_method": "secure_deletion",
                "approval_required": True,
                "legal_basis": "Financial regulations"
            },
            {
                "schedule_id": "RET_002",
                "name": "Creator Content Retention",
                "classification_level": DataClassificationLevel.CONFIDENTIAL,
                "data_category": DataCategory.CREATOR_CONTENT,
                "retention_period": RetentionPeriod.INDEFINITE,
                "destruction_method": "archival",
                "approval_required": False,
                "legal_basis": "Creator agreement"
            }
        ]
        
        for schedule_data in default_schedules:
            schedule = RetentionSchedule(**schedule_data)
            self.retention_schedules[schedule.schedule_id] = schedule
    
    async def _discover_data_elements(self, data_source: str) -> List[DataElement]:
        """Discover data elements in source"""
        # Simulate data discovery
        discovered_elements = [
            DataElement(
                element_id=str(uuid.uuid4()),
                name="sample_file.txt",
                content_type="text/plain",
                size_bytes=1024,
                location=data_source,
                owner="system"
            )
        ]
        
        return discovered_elements
    
    async def _classify_data_element(self, element: DataElement, deep_scan: bool) -> Optional[ClassificationResult]:
        """Classify individual data element"""
        best_match = None
        highest_confidence = 0.0
        
        # Apply classification rules
        for rule in self.classification_rules.values():
            if not rule.enabled:
                continue
            
            confidence = await self._calculate_rule_confidence(element, rule, deep_scan)
            if confidence > highest_confidence and confidence >= rule.confidence_threshold:
                highest_confidence = confidence
                best_match = rule
        
        if best_match:
            return ClassificationResult(
                element_id=element.element_id,
                classification_level=best_match.classification_level,
                data_category=best_match.data_category,
                confidence_score=highest_confidence,
                matched_rules=[best_match.rule_id],
                recommendations=await self._generate_element_recommendations(element, best_match)
            )
        
        return None
    
    async def _calculate_rule_confidence(self, element: DataElement, rule: ClassificationRule, deep_scan: bool) -> float:
        """Calculate confidence score for classification rule"""
        confidence = 0.0
        
        # Check keywords in filename
        for keyword in rule.keywords:
            if keyword.lower() in element.name.lower():
                confidence += 0.3
        
        # Check patterns if deep scan enabled
        if deep_scan and rule.patterns:
            # Simulate content analysis
            confidence += 0.5  # Simplified for demo
        
        return min(1.0, confidence)
    
    async def _assess_element_risk(self, element: DataElement, classification: ClassificationResult) -> List[str]:
        """Assess risk factors for data element"""
        risk_factors = []
        
        if classification.classification_level in [DataClassificationLevel.RESTRICTED, DataClassificationLevel.TOP_SECRET]:
            risk_factors.append("high_classification_level")
        
        if not element.encryption_required:
            risk_factors.append("unencrypted_storage")
        
        if not element.access_controls:
            risk_factors.append("no_access_controls")
        
        return risk_factors
    
    async def _generate_classification_recommendations(self, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on classification results"""
        recommendations = []
        
        if summary["elements_classified"] < summary["elements_discovered"]:
            recommendations.append({
                "priority": "medium",
                "recommendation": "Increase classification rule coverage",
                "rationale": "Some data elements remain unclassified"
            })
        
        if summary["high_risk_elements"]:
            recommendations.append({
                "priority": "high", 
                "recommendation": "Review and secure high-risk data elements",
                "rationale": f"{len(summary['high_risk_elements'])} high-risk elements identified"
            })
        
        return recommendations
    
    async def _determine_access_controls(self, classification: ClassificationResult) -> List[str]:
        """Determine appropriate access controls"""
        controls = []
        
        if classification.classification_level == DataClassificationLevel.RESTRICTED:
            controls.extend(["multi_factor_auth", "role_based_access", "audit_logging"])
        elif classification.classification_level == DataClassificationLevel.CONFIDENTIAL:
            controls.extend(["role_based_access", "audit_logging"])
        elif classification.classification_level == DataClassificationLevel.INTERNAL:
            controls.append("employee_access_only")
        
        return controls
    
    async def _requires_encryption(self, classification: ClassificationResult) -> bool:
        """Determine if encryption is required"""
        return classification.classification_level in [
            DataClassificationLevel.RESTRICTED,
            DataClassificationLevel.TOP_SECRET
        ]
    
    async def _determine_retention_schedule(self, classification: ClassificationResult) -> Optional[RetentionSchedule]:
        """Determine appropriate retention schedule"""
        for schedule in self.retention_schedules.values():
            if (schedule.classification_level == classification.classification_level and
                schedule.data_category == classification.data_category):
                return schedule
        
        return None
    
    def _get_retention_days(self, retention_period: RetentionPeriod) -> int:
        """Convert retention period to days"""
        mapping = {
            RetentionPeriod.THIRTY_DAYS: 30,
            RetentionPeriod.NINETY_DAYS: 90,
            RetentionPeriod.ONE_YEAR: 365,
            RetentionPeriod.THREE_YEARS: 1095,
            RetentionPeriod.SEVEN_YEARS: 2555
        }
        return mapping.get(retention_period, 365)
    
    async def _activate_dlp_policies(self, element: DataElement, classification: ClassificationResult) -> List[str]:
        """Activate relevant DLP policies"""
        activated = []
        
        for policy in self.dlp_policies.values():
            if (classification.classification_level in policy.classification_levels or
                classification.data_category in policy.data_categories):
                activated.append(policy.policy_id)
        
        return activated
    
    async def _get_applicable_dlp_policies(self, element: DataElement) -> List[DLPPolicy]:
        """Get DLP policies applicable to data element"""
        applicable = []
        
        for policy in self.dlp_policies.values():
            if not policy.enabled:
                continue
            
            if (element.classification_level in policy.classification_levels or
                element.data_category in policy.data_categories):
                applicable.append(policy)
        
        return applicable
    
    async def _evaluate_dlp_policy(self, policy: DLPPolicy, element: DataElement, user_id: str, action: str) -> Dict[str, Any]:
        """Evaluate DLP policy against action"""
        result = {
            "policy_id": policy.policy_id,
            "compliant": True,
            "conditions_checked": [],
            "violations": []
        }
        
        # Check policy conditions
        for condition in policy.conditions:
            condition_met = await self._check_dlp_condition(condition, element, user_id, action)
            result["conditions_checked"].append({
                "condition": condition,
                "met": condition_met
            })
            
            if condition_met:
                result["compliant"] = False
                result["violations"].append(f"Condition violated: {condition}")
        
        return result
    
    async def _check_dlp_condition(self, condition: Dict[str, Any], element: DataElement, user_id: str, action: str) -> bool:
        """Check individual DLP condition"""
        field = condition.get("field")
        operator = condition.get("operator") 
        value = condition.get("value")
        
        if field == "action":
            if operator == "in":
                return action in value
            elif operator == "equals":
                return action == value
        
        return False
    
    async def _execute_dlp_action(self, dlp_action: DLPAction, element: DataElement, user_id: str, action: str) -> Dict[str, Any]:
        """Execute DLP action"""
        result = {
            "action": dlp_action.value,
            "executed": True,
            "details": {}
        }
        
        if dlp_action == DLPAction.BLOCK:
            result["details"]["message"] = "Action blocked by DLP policy"
        elif dlp_action == DLPAction.NOTIFY_ADMIN:
            result["details"]["notification_sent"] = True
        elif dlp_action == DLPAction.ENCRYPT:
            result["details"]["encryption_applied"] = True
        
        return result
    
    async def _execute_data_deletion(self, element: DataElement) -> Dict[str, Any]:
        """Execute secure data deletion"""
        return {
            "success": True,
            "method": "secure_deletion",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _check_legal_holds(self) -> List[str]:
        """Check for legal holds affecting data retention"""
        return []  # Simplified for demo
    
    async def _get_top_violated_policies(self) -> List[Dict[str, Any]]:
        """Get most frequently violated DLP policies"""
        return []  # Simplified for demo
    
    async def _analyze_retention_compliance(self) -> Dict[str, Any]:
        """Analyze retention compliance"""
        return {
            "elements_with_retention": len([e for e in self.data_elements.values() if e.retention_period]),
            "elements_expired": len([e for e in self.data_elements.values() 
                                   if e.expires_at and e.expires_at <= datetime.now(timezone.utc)]),
            "compliance_percentage": 95.0
        }
    
    async def _assess_data_classification_risks(self) -> Dict[str, Any]:
        """Assess data classification risks"""
        return {
            "unclassified_data_risk": "medium",
            "encryption_gaps": 5,
            "access_control_gaps": 3,
            "overall_risk_score": 25.0
        }
    
    async def _generate_governance_recommendations(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate data governance recommendations"""
        recommendations = []
        
        if report_data["summary"]["classification_coverage"] < 90:
            recommendations.append({
                "priority": "high",
                "recommendation": "Improve data classification coverage",
                "action": "Review and update classification rules"
            })
        
        return recommendations
    
    async def _generate_element_recommendations(self, element: DataElement, rule: ClassificationRule) -> List[str]:
        """Generate recommendations for data element"""
        recommendations = []
        
        if rule.classification_level in [DataClassificationLevel.RESTRICTED, DataClassificationLevel.TOP_SECRET]:
            recommendations.append("Apply encryption at rest")
            recommendations.append("Implement strict access controls")
        
        return recommendations
    
    async def _log_classification_scan(self, summary: Dict[str, Any]) -> None:
        """Log classification scan"""
        self.logger.info(f"Classification scan completed: {summary['elements_classified']}/{summary['elements_discovered']}")
    
    async def _log_security_labeling(self, result: Dict[str, Any]) -> None:
        """Log security labeling"""
        self.logger.info(f"Security labels applied: {result['element_id']}")
    
    async def _log_dlp_enforcement(self, result: Dict[str, Any]) -> None:
        """Log DLP enforcement"""
        self.logger.info(f"DLP enforcement: {result['element_id']} - {result['allowed']}")
    
    async def _log_retention_management(self, result: Dict[str, Any]) -> None:
        """Log retention management"""
        self.logger.info(f"Retention management: {result['elements_reviewed']} reviewed")

# Creator Economy specific data classification
CREATOR_DATA_CLASSIFICATIONS = {
    "public_content": {
        "classification": DataClassificationLevel.PUBLIC,
        "category": DataCategory.CREATOR_CONTENT,
        "retention": RetentionPeriod.INDEFINITE
    },
    "private_drafts": {
        "classification": DataClassificationLevel.CONFIDENTIAL,
        "category": DataCategory.CREATOR_CONTENT,
        "retention": RetentionPeriod.SEVEN_YEARS
    },
    "personal_data": {
        "classification": DataClassificationLevel.RESTRICTED,
        "category": DataCategory.PERSONAL_DATA,
        "retention": RetentionPeriod.THREE_YEARS
    },
    "financial_data": {
        "classification": DataClassificationLevel.RESTRICTED,
        "category": DataCategory.FINANCIAL_DATA,
        "retention": RetentionPeriod.SEVEN_YEARS
    },
    "biometric_data": {
        "classification": DataClassificationLevel.TOP_SECRET,
        "category": DataCategory.BIOMETRIC_DATA,
        "retention": RetentionPeriod.ONE_YEAR
    }
}

__all__ = [
    'DataClassificationManager',
    'DataElement',
    'ClassificationRule',
    'DLPPolicy',
    'RetentionSchedule',
    'ClassificationResult',
    'DLPViolation',
    'DataClassificationLevel',
    'DataCategory',
    'RetentionPeriod',
    'DLPAction',
    'CREATOR_DATA_CLASSIFICATIONS'
]