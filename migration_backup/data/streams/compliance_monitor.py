"""Compliance Monitor for IA Influencer Agent Platform
================================================

Enterprise-grade compliance monitoring system for GDPR, SOC2, HIPAA,
and other regulatory frameworks with automated reporting and validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    CCPA = "ccpa"
    NIST = "nist"
    COPPA = "coppa"
    FERPA = "ferpa"
    CUSTOM = "custom"


class ComplianceStatus(str, Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    UNDER_REMEDIATION = "under_remediation"
    EXEMPT = "exempt"


class ViolationSeverity(str, Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataCategory(str, Enum):
    """Data category types for compliance"""
    PII = "pii"
    PHI = "phi"
    FINANCIAL = "financial"
    BIOMETRIC = "biometric"
    BEHAVIORAL = "behavioral"
    LOCATION = "location"
    COMMUNICATION = "communication"
    PREFERENCE = "preference"
    TECHNICAL = "technical"
    PUBLIC = "public"


class ProcessingLawfulness(str, Enum):
    """GDPR lawful basis for processing"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


@dataclass
class ComplianceRule:
    """Compliance rule configuration"""
    rule_id: str
    framework: ComplianceFramework
    category: str
    title: str
    description: str
    requirements: List[str] = field(default_factory=list)
    validation_criteria: Dict[str, Any] = field(default_factory=dict)
    automated_check: bool = True
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    framework: ComplianceFramework
    severity: ViolationSeverity
    title: str
    description: str
    resource_type: str
    resource_id: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    remediation_actions: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    assignee: Optional[str] = None


@dataclass
class DataProcessingRecord:
    """GDPR data processing record"""
    record_id: str
    data_controller: str
    data_processor: Optional[str] = None
    purpose: str
    data_categories: List[DataCategory] = field(default_factory=list)
    data_subjects: List[str] = field(default_factory=list)
    lawful_basis: ProcessingLawfulness = ProcessingLawfulness.CONSENT
    retention_period: str = ""
    security_measures: List[str] = field(default_factory=list)
    third_country_transfers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConsentRecord:
    """User consent record for GDPR"""
    consent_id: str
    user_id: str
    purpose: str
    data_categories: List[DataCategory] = field(default_factory=list)
    lawful_basis: ProcessingLawfulness = ProcessingLawfulness.CONSENT
    consent_given: bool = False
    consent_timestamp: Optional[datetime] = None
    withdrawal_timestamp: Optional[datetime] = None
    consent_method: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    framework: ComplianceFramework
    assessment_period_start: datetime
    assessment_period_end: datetime
    overall_status: ComplianceStatus
    compliance_score: float
    total_rules_checked: int
    compliant_rules: int
    violations_found: int
    critical_violations: int
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: str = ""


class ComplianceMonitor:
    """
    Enterprise-grade compliance monitoring system for regulatory frameworks
    including GDPR, SOC2, HIPAA, PCI-DSS, and others.
    
    Features:
    - Automated compliance rule checking
    - Real-time violation detection
    - Data processing record management
    - Consent management (GDPR)
    - Compliance reporting and dashboards
    - Remediation workflow management
    """
    
    def __init__(
        self,
        enabled_frameworks: Optional[List[ComplianceFramework]] = None,
        enable_real_time_monitoring: bool = True,
        enable_automated_reporting: bool = True
    ):
        # Configuration
        self.enabled_frameworks = enabled_frameworks or [
            ComplianceFramework.GDPR,
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001
        ]
        self.enable_real_time_monitoring = enable_real_time_monitoring
        self.enable_automated_reporting = enable_automated_reporting
        
        # Compliance rules management
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.violation_handlers: List[Callable] = []
        
        # Data processing records (GDPR)
        self.processing_records: Dict[str, DataProcessingRecord] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        
        # Compliance reports
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        self.assessment_history: deque = deque(maxlen=1000)
        
        # Monitoring state
        self.last_assessment: Dict[ComplianceFramework, datetime] = {}
        self.compliance_metrics = {
            "total_rules": 0,
            "active_violations": 0,
            "resolved_violations": 0,
            "compliance_score": 100.0,
            "last_assessment": None
        }
        
        # Background tasks
        self.compliance_monitor_task: Optional[asyncio.Task] = None
        self.reporting_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # State management
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # Initialize default compliance rules
        self._init_default_rules()
        
        logger.info("ComplianceMonitor initialized")
        
    async def initialize(self) -> None:
        """Initialize the compliance monitor"""
        try:
            if self._running:
                return
                
            # Start background tasks
            if self.enable_real_time_monitoring:
                self.compliance_monitor_task = asyncio.create_task(self._compliance_monitor())
                
            if self.enable_automated_reporting:
                self.reporting_task = asyncio.create_task(self._automated_reporting())
                
            self.cleanup_task = asyncio.create_task(self._cleanup_worker())
            
            self._running = True
            logger.info("ComplianceMonitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ComplianceMonitor: {e}")
            raise
            
    async def add_compliance_rule(
        self,
        framework: ComplianceFramework,
        category: str,
        title: str,
        description: str,
        requirements: List[str],
        validation_criteria: Dict[str, Any],
        severity: ViolationSeverity = ViolationSeverity.MEDIUM
    ) -> str:
        """
        Add a new compliance rule
        
        Args:
            framework: Compliance framework
            category: Rule category
            title: Rule title
            description: Rule description
            requirements: List of requirements
            validation_criteria: Validation criteria
            severity: Violation severity if rule fails
            
        Returns:
            Rule ID
        """
        try:
            rule_id = str(uuid.uuid4())
            
            rule = ComplianceRule(
                rule_id=rule_id,
                framework=framework,
                category=category,
                title=title,
                description=description,
                requirements=requirements,
                validation_criteria=validation_criteria,
                severity=severity
            )
            
            self.compliance_rules[rule_id] = rule
            self.compliance_metrics["total_rules"] += 1
            
            logger.info(f"Compliance rule added: {title} ({framework.value})")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to add compliance rule: {e}")
            return ""
            
    async def record_data_processing(
        self,
        data_controller: str,
        purpose: str,
        data_categories: List[DataCategory],
        lawful_basis: ProcessingLawfulness,
        retention_period: str,
        security_measures: List[str],
        data_processor: Optional[str] = None,
        third_country_transfers: Optional[List[str]] = None
    ) -> str:
        """
        Record data processing activity (GDPR Article 30)
        
        Args:
            data_controller: Data controller organization
            purpose: Processing purpose
            data_categories: Categories of data processed
            lawful_basis: Lawful basis for processing
            retention_period: Data retention period
            security_measures: Security measures in place
            data_processor: Optional data processor
            third_country_transfers: Optional third country transfers
            
        Returns:
            Record ID
        """
        try:
            record_id = str(uuid.uuid4())
            
            record = DataProcessingRecord(
                record_id=record_id,
                data_controller=data_controller,
                data_processor=data_processor,
                purpose=purpose,
                data_categories=data_categories,
                lawful_basis=lawful_basis,
                retention_period=retention_period,
                security_measures=security_measures,
                third_country_transfers=third_country_transfers or []
            )
            
            self.processing_records[record_id] = record
            
            logger.info(f"Data processing recorded: {purpose} by {data_controller}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to record data processing: {e}")
            return ""
            
    async def record_user_consent(
        self,
        user_id: str,
        purpose: str,
        data_categories: List[DataCategory],
        consent_given: bool,
        consent_method: str = "web_form",
        evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record user consent (GDPR compliance)
        
        Args:
            user_id: User identifier
            purpose: Purpose of data processing
            data_categories: Categories of data
            consent_given: Whether consent was given
            consent_method: Method of consent collection
            evidence: Additional evidence
            
        Returns:
            Consent ID
        """
        try:
            consent_id = str(uuid.uuid4())
            
            consent = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                purpose=purpose,
                data_categories=data_categories,
                consent_given=consent_given,
                consent_timestamp=datetime.now(timezone.utc) if consent_given else None,
                consent_method=consent_method,
                evidence=evidence or {}
            )
            
            self.consent_records[consent_id] = consent
            
            logger.info(f"User consent recorded: {user_id} - {purpose} ({'given' if consent_given else 'refused'})")
            return consent_id
            
        except Exception as e:
            logger.error(f"Failed to record user consent: {e}")
            return ""
            
    async def withdraw_consent(
        self,
        user_id: str,
        purpose: str
    ) -> bool:
        """
        Withdraw user consent (GDPR right to withdraw)
        
        Args:
            user_id: User identifier
            purpose: Purpose to withdraw consent for
            
        Returns:
            Success status
        """
        try:
            # Find relevant consent records
            for consent in self.consent_records.values():
                if (consent.user_id == user_id and 
                    consent.purpose == purpose and 
                    consent.consent_given and 
                    consent.withdrawal_timestamp is None):
                    
                    consent.withdrawal_timestamp = datetime.now(timezone.utc)
                    consent.consent_given = False
                    
                    logger.info(f"Consent withdrawn: {user_id} - {purpose}")
                    return True
                    
            logger.warning(f"No active consent found to withdraw: {user_id} - {purpose}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            return False
            
    async def check_compliance_rule(
        self,
        rule_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check a specific compliance rule
        
        Args:
            rule_id: Rule identifier
            context: Context data for validation
            
        Returns:
            True if compliant, False if violation
        """
        try:
            if rule_id not in self.compliance_rules:
                logger.error(f"Compliance rule not found: {rule_id}")
                return False
                
            rule = self.compliance_rules[rule_id]
            
            # Perform rule validation based on criteria
            is_compliant = await self._validate_rule(rule, context)
            
            if not is_compliant:
                # Create violation record
                await self._create_violation(rule, context)
                
            return is_compliant
            
        except Exception as e:
            logger.error(f"Failed to check compliance rule: {e}")
            return False
            
    async def run_compliance_assessment(
        self,
        framework: ComplianceFramework,
        scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Run comprehensive compliance assessment
        
        Args:
            framework: Framework to assess
            scope: Optional assessment scope
            
        Returns:
            Report ID
        """
        try:
            report_id = str(uuid.uuid4())
            assessment_start = datetime.now(timezone.utc)
            
            # Get rules for framework
            framework_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.framework == framework
            ]
            
            compliant_count = 0
            violations_found = []
            critical_violations = 0
            
            # Check each rule
            for rule in framework_rules:
                context = scope or {}
                is_compliant = await self._validate_rule(rule, context)
                
                if is_compliant:
                    compliant_count += 1
                else:
                    violation = await self._create_violation(rule, context)
                    violations_found.append(violation)
                    
                    if rule.severity == ViolationSeverity.CRITICAL:
                        critical_violations += 1
                        
            # Calculate compliance score
            total_rules = len(framework_rules)
            compliance_score = (compliant_count / total_rules * 100) if total_rules > 0 else 100
            
            # Determine overall status
            if compliance_score >= 95:
                overall_status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 75:
                overall_status = ComplianceStatus.PARTIAL
            else:
                overall_status = ComplianceStatus.NON_COMPLIANT
                
            # Generate recommendations
            recommendations = await self._generate_recommendations(framework, violations_found)
            
            # Create report
            report = ComplianceReport(
                report_id=report_id,
                framework=framework,
                assessment_period_start=assessment_start,
                assessment_period_end=datetime.now(timezone.utc),
                overall_status=overall_status,
                compliance_score=compliance_score,
                total_rules_checked=total_rules,
                compliant_rules=compliant_count,
                violations_found=len(violations_found),
                critical_violations=critical_violations,
                recommendations=recommendations,
                generated_by="system"
            )
            
            self.compliance_reports[report_id] = report
            self.last_assessment[framework] = datetime.now(timezone.utc)
            
            # Update metrics
            self.compliance_metrics["compliance_score"] = compliance_score
            self.compliance_metrics["last_assessment"] = datetime.now(timezone.utc)
            
            logger.info(f"Compliance assessment completed: {framework.value} - {compliance_score:.1f}% compliant")
            return report_id
            
        except Exception as e:
            logger.error(f"Failed to run compliance assessment: {e}")
            return ""
            
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        try:
            # Active violations by severity
            active_violations = [v for v in self.violations.values() if not v.resolved]
            violations_by_severity = defaultdict(int)
            for violation in active_violations:
                violations_by_severity[violation.severity.value] += 1
                
            # Framework compliance scores
            framework_scores = {}
            for framework in self.enabled_frameworks:
                latest_report = self._get_latest_report(framework)
                if latest_report:
                    framework_scores[framework.value] = latest_report.compliance_score
                else:
                    framework_scores[framework.value] = 0
                    
            # Recent activity
            recent_violations = [
                v for v in self.violations.values()
                if v.detected_at >= datetime.now(timezone.utc) - timedelta(days=7)
            ]
            
            return {
                "overall_compliance_score": self.compliance_metrics["compliance_score"],
                "total_rules": self.compliance_metrics["total_rules"],
                "active_violations": len(active_violations),
                "resolved_violations": self.compliance_metrics["resolved_violations"],
                "violations_by_severity": dict(violations_by_severity),
                "framework_scores": framework_scores,
                "recent_violations_7d": len(recent_violations),
                "last_assessment": self.compliance_metrics["last_assessment"],
                "enabled_frameworks": [f.value for f in self.enabled_frameworks],
                "data_processing_records": len(self.processing_records),
                "consent_records": len(self.consent_records)
            }
            
        except Exception as e:
            logger.error(f"Failed to get compliance dashboard: {e}")
            return {}
            
    def _init_default_rules(self) -> None:
        """Initialize default compliance rules"""
        try:
            # GDPR rules
            if ComplianceFramework.GDPR in self.enabled_frameworks:
                self._init_gdpr_rules()
                
            # SOC2 rules
            if ComplianceFramework.SOC2 in self.enabled_frameworks:
                self._init_soc2_rules()
                
            # ISO27001 rules
            if ComplianceFramework.ISO27001 in self.enabled_frameworks:
                self._init_iso27001_rules()
                
        except Exception as e:
            logger.error(f"Failed to initialize default rules: {e}")
            
    def _init_gdpr_rules(self) -> None:
        """Initialize GDPR compliance rules"""
        try:
            # Data processing records rule
            gdpr_article30 = ComplianceRule(
                rule_id="gdpr_article30",
                framework=ComplianceFramework.GDPR,
                category="Records of Processing",
                title="Article 30 - Records of Processing Activities",
                description="Organizations must maintain records of processing activities",
                requirements=[
                    "Maintain records of all processing activities",
                    "Include purposes of processing",
                    "Include categories of data subjects and personal data",
                    "Include recipients of personal data",
                    "Include retention periods"
                ],
                validation_criteria={
                    "min_records": 1,
                    "required_fields": ["purpose", "data_categories", "lawful_basis"]
                },
                severity=ViolationSeverity.HIGH
            )
            self.compliance_rules["gdpr_article30"] = gdpr_article30
            
            # Consent management rule
            gdpr_consent = ComplianceRule(
                rule_id="gdpr_consent",
                framework=ComplianceFramework.GDPR,
                category="Consent Management",
                title="Valid Consent Requirements",
                description="Consent must be freely given, specific, informed and unambiguous",
                requirements=[
                    "Obtain explicit consent for data processing",
                    "Provide clear information about processing purposes",
                    "Allow easy withdrawal of consent",
                    "Maintain records of consent"
                ],
                validation_criteria={
                    "consent_method": "explicit",
                    "withdrawal_available": True
                },
                severity=ViolationSeverity.CRITICAL
            )
            self.compliance_rules["gdpr_consent"] = gdpr_consent
            
            # Data retention rule
            gdpr_retention = ComplianceRule(
                rule_id="gdpr_retention",
                framework=ComplianceFramework.GDPR,
                category="Data Retention",
                title="Data Retention Limits",
                description="Personal data must not be kept longer than necessary",
                requirements=[
                    "Define retention periods for each processing purpose",
                    "Implement automatic deletion procedures",
                    "Regular review of stored data"
                ],
                validation_criteria={
                    "max_retention_days": 2555,  # 7 years default
                    "auto_deletion": True
                },
                severity=ViolationSeverity.HIGH
            )
            self.compliance_rules["gdpr_retention"] = gdpr_retention
            
            self.compliance_metrics["total_rules"] += 3
            
        except Exception as e:
            logger.error(f"Failed to initialize GDPR rules: {e}")
            
    def _init_soc2_rules(self) -> None:
        """Initialize SOC2 compliance rules"""
        try:
            # Security principle
            soc2_security = ComplianceRule(
                rule_id="soc2_security",
                framework=ComplianceFramework.SOC2,
                category="Security",
                title="Security Controls",
                description="Implement adequate security controls to protect against unauthorized access",
                requirements=[
                    "Multi-factor authentication",
                    "Access controls and authorization",
                    "Regular security monitoring",
                    "Incident response procedures"
                ],
                validation_criteria={
                    "mfa_enabled": True,
                    "access_controls": True,
                    "monitoring_enabled": True
                },
                severity=ViolationSeverity.HIGH
            )
            self.compliance_rules["soc2_security"] = soc2_security
            
            # Availability principle
            soc2_availability = ComplianceRule(
                rule_id="soc2_availability",
                framework=ComplianceFramework.SOC2,
                category="Availability",
                title="System Availability",
                description="Ensure system availability meets agreed-upon service levels",
                requirements=[
                    "Monitor system uptime",
                    "Implement redundancy and failover",
                    "Capacity planning and management",
                    "Regular backup and recovery testing"
                ],
                validation_criteria={
                    "min_uptime_percentage": 99.9,
                    "backup_frequency": "daily",
                    "recovery_testing": True
                },
                severity=ViolationSeverity.MEDIUM
            )
            self.compliance_rules["soc2_availability"] = soc2_availability
            
            self.compliance_metrics["total_rules"] += 2
            
        except Exception as e:
            logger.error(f"Failed to initialize SOC2 rules: {e}")
            
    def _init_iso27001_rules(self) -> None:
        """Initialize ISO27001 compliance rules"""
        try:
            # Information security policy
            iso_policy = ComplianceRule(
                rule_id="iso27001_policy",
                framework=ComplianceFramework.ISO27001,
                category="Security Policy",
                title="Information Security Policy",
                description="Establish and maintain information security policy",
                requirements=[
                    "Document information security policy",
                    "Regular policy review and updates",
                    "Communication to all personnel",
                    "Management approval and support"
                ],
                validation_criteria={
                    "policy_documented": True,
                    "review_frequency": "annual",
                    "management_approved": True
                },
                severity=ViolationSeverity.MEDIUM
            )
            self.compliance_rules["iso27001_policy"] = iso_policy
            
            self.compliance_metrics["total_rules"] += 1
            
        except Exception as e:
            logger.error(f"Failed to initialize ISO27001 rules: {e}")
            
    async def _validate_rule(self, rule: ComplianceRule, context: Dict[str, Any]) -> bool:
        """Validate a compliance rule against context"""
        try:
            criteria = rule.validation_criteria
            
            # Framework-specific validation
            if rule.framework == ComplianceFramework.GDPR:
                return await self._validate_gdpr_rule(rule, context)
            elif rule.framework == ComplianceFramework.SOC2:
                return await self._validate_soc2_rule(rule, context)
            elif rule.framework == ComplianceFramework.ISO27001:
                return await self._validate_iso27001_rule(rule, context)
            else:
                # Generic validation
                return await self._validate_generic_rule(rule, context)
                
        except Exception as e:
            logger.error(f"Failed to validate rule {rule.rule_id}: {e}")
            return False
            
    async def _validate_gdpr_rule(self, rule: ComplianceRule, context: Dict[str, Any]) -> bool:
        """Validate GDPR-specific rules"""
        try:
            if rule.rule_id == "gdpr_article30":
                # Check if processing records exist
                return len(self.processing_records) > 0
                
            elif rule.rule_id == "gdpr_consent":
                # Check consent management
                user_id = context.get("user_id")
                if user_id:
                    user_consents = [
                        c for c in self.consent_records.values()
                        if c.user_id == user_id and c.consent_given
                    ]
                    return len(user_consents) > 0
                return True
                
            elif rule.rule_id == "gdpr_retention":
                # Check data retention compliance
                # This would integrate with actual data storage systems
                return True
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate GDPR rule: {e}")
            return False
            
    async def _validate_soc2_rule(self, rule: ComplianceRule, context: Dict[str, Any]) -> bool:
        """Validate SOC2-specific rules"""
        try:
            if rule.rule_id == "soc2_security":
                # Check security controls
                security_controls = context.get("security_controls", {})
                return (security_controls.get("mfa_enabled", False) and
                       security_controls.get("access_controls", False))
                       
            elif rule.rule_id == "soc2_availability":
                # Check availability metrics
                availability = context.get("availability_percentage", 0)
                return availability >= 99.9
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate SOC2 rule: {e}")
            return False
            
    async def _validate_iso27001_rule(self, rule: ComplianceRule, context: Dict[str, Any]) -> bool:
        """Validate ISO27001-specific rules"""
        try:
            if rule.rule_id == "iso27001_policy":
                # Check policy documentation
                policy_status = context.get("security_policy", {})
                return (policy_status.get("documented", False) and
                       policy_status.get("management_approved", False))
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate ISO27001 rule: {e}")
            return False
            
    async def _validate_generic_rule(self, rule: ComplianceRule, context: Dict[str, Any]) -> bool:
        """Validate generic compliance rules"""
        try:
            criteria = rule.validation_criteria
            
            # Check each validation criterion
            for key, expected_value in criteria.items():
                actual_value = context.get(key)
                
                if isinstance(expected_value, bool):
                    if actual_value != expected_value:
                        return False
                elif isinstance(expected_value, (int, float)):
                    if actual_value is None or actual_value < expected_value:
                        return False
                elif isinstance(expected_value, str):
                    if actual_value != expected_value:
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate generic rule: {e}")
            return False
            
    async def _create_violation(self, rule: ComplianceRule, context: Dict[str, Any]) -> str:
        """Create a compliance violation record"""
        try:
            violation_id = str(uuid.uuid4())
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                framework=rule.framework,
                severity=rule.severity,
                title=f"Violation: {rule.title}",
                description=f"Rule '{rule.title}' failed validation",
                resource_type=context.get("resource_type", "unknown"),
                resource_id=context.get("resource_id", "unknown"),
                evidence=context
            )
            
            self.violations[violation_id] = violation
            self.compliance_metrics["active_violations"] += 1
            
            # Trigger violation handlers
            await self._trigger_violation_handlers(violation)
            
            logger.warning(f"Compliance violation created: {rule.title} ({rule.framework.value})")
            return violation_id
            
        except Exception as e:
            logger.error(f"Failed to create violation: {e}")
            return ""
            
    async def _generate_recommendations(
        self,
        framework: ComplianceFramework,
        violations: List[str]
    ) -> List[str]:
        """Generate compliance recommendations"""
        try:
            recommendations = []
            
            if framework == ComplianceFramework.GDPR:
                recommendations.extend([
                    "Implement comprehensive data mapping and classification",
                    "Establish clear consent management procedures",
                    "Implement automated data retention and deletion",
                    "Conduct regular privacy impact assessments"
                ])
                
            elif framework == ComplianceFramework.SOC2:
                recommendations.extend([
                    "Implement multi-factor authentication for all users",
                    "Establish comprehensive monitoring and alerting",
                    "Implement regular backup and recovery testing",
                    "Conduct annual penetration testing"
                ])
                
            elif framework == ComplianceFramework.ISO27001:
                recommendations.extend([
                    "Develop comprehensive information security policies",
                    "Implement risk management framework",
                    "Establish security awareness training program",
                    "Conduct regular security audits and assessments"
                ])
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
            
    def _get_latest_report(self, framework: ComplianceFramework) -> Optional[ComplianceReport]:
        """Get latest compliance report for framework"""
        try:
            framework_reports = [
                report for report in self.compliance_reports.values()
                if report.framework == framework
            ]
            
            if framework_reports:
                return max(framework_reports, key=lambda r: r.generated_at)
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest report: {e}")
            return None
            
    async def _trigger_violation_handlers(self, violation: ComplianceViolation) -> None:
        """Trigger registered violation handlers"""
        try:
            for handler in self.violation_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(violation)
                    else:
                        handler(violation)
                except Exception as e:
                    logger.error(f"Violation handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger violation handlers: {e}")
            
    async def _compliance_monitor(self) -> None:
        """Background compliance monitoring task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Monitor every hour
                
                # Run automated compliance checks
                for framework in self.enabled_frameworks:
                    await self._run_automated_checks(framework)
                    
            except Exception as e:
                logger.error(f"Compliance monitor error: {e}")
                
    async def _automated_reporting(self) -> None:
        """Background automated reporting task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(86400)  # Report daily
                
                # Generate daily compliance reports
                for framework in self.enabled_frameworks:
                    await self.run_compliance_assessment(framework)
                    
            except Exception as e:
                logger.error(f"Automated reporting error: {e}")
                
    async def _cleanup_worker(self) -> None:
        """Background cleanup task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Clean old resolved violations
                cutoff = datetime.now(timezone.utc) - timedelta(days=90)
                old_violations = [
                    v_id for v_id, v in self.violations.items()
                    if v.resolved and v.resolved_at and v.resolved_at < cutoff
                ]
                
                for v_id in old_violations[:50]:  # Limit cleanup per cycle
                    del self.violations[v_id]
                    
                # Clean old reports
                old_reports = [
                    r_id for r_id, r in self.compliance_reports.items()
                    if r.generated_at < cutoff
                ]
                
                for r_id in old_reports[:20]:  # Limit cleanup per cycle
                    del self.compliance_reports[r_id]
                    
                logger.info(f"Compliance cleanup completed: removed {len(old_violations)} violations, {len(old_reports)} reports")
                
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                
    async def _run_automated_checks(self, framework: ComplianceFramework) -> None:
        """Run automated compliance checks for framework"""
        try:
            # This would integrate with actual system monitoring
            # For now, implement basic checks
            
            if framework == ComplianceFramework.GDPR:
                # Check GDPR compliance
                context = {
                    "data_processing_records": len(self.processing_records),
                    "consent_records": len(self.consent_records)
                }
                
                for rule in self.compliance_rules.values():
                    if rule.framework == framework and rule.automated_check:
                        await self.check_compliance_rule(rule.rule_id, context)
                        
        except Exception as e:
            logger.error(f"Failed to run automated checks: {e}")
            
    async def shutdown(self) -> None:
        """Gracefully shutdown the compliance monitor"""
        try:
            logger.info("Shutting down ComplianceMonitor...")
            
            self._shutdown_event.set()
            
            # Cancel background tasks
            tasks_to_cancel = [
                self.compliance_monitor_task,
                self.reporting_task,
                self.cleanup_task
            ]
            
            for task in tasks_to_cancel:
                if task:
                    task.cancel()
                    
            self._running = False
            logger.info("ComplianceMonitor shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")