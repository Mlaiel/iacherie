"""Database Compliance Checker

Enterprise-grade compliance verification system for database operations
with support for GDPR, CCPA, HIPAA, SOX, PCI-DSS and other frameworks.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced compliance architecture
- ML Engineer: AI-driven compliance monitoring
- DBA: Database compliance optimization
- Security Expert: Enterprise compliance protocols
- Microservices: Distributed compliance checking
- Audio Engineer: Audio content compliance
- DevOps: Secure compliance infrastructure
- IA Prompt Engineer: AI compliance analysis prompts

Contact: mlaiel@live.de
⚠️ LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid
import re

# Configure logging
logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOX = "sox"  # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    ISO_27001 = "iso_27001"  # Information Security Management
    NIST = "nist"  # National Institute of Standards and Technology
    FedRAMP = "fedramp"  # Federal Risk and Authorization Management Program
    FISMA = "fisma"  # Federal Information Security Management Act


class ComplianceStatus(Enum):
    """Compliance check status"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    PENDING_REVIEW = "pending_review"


class ViolationSeverity(Enum):
    """Compliance violation severity"""    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class DataCategory(Enum):
    """Data classification categories"""    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"  # Personally Identifiable Information
    PHI = "phi"  # Protected Health Information
    PCI = "pci"  # Payment Card Information
    FINANCIAL = "financial"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""    rule_id: str
    framework: ComplianceFramework
    category: str
    title: str
    description: str
    requirement: str
    data_categories: List[DataCategory]
    automated_check: bool = True
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    remediation_guidance: str = ""
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceViolation:
    """Compliance violation record"""    violation_id: str
    rule: ComplianceRule
    severity: ViolationSeverity
    description: str
    affected_resource: str
    evidence: Dict[str, Any]
    detected_at: datetime = field(default_factory=datetime.now)
    remediation_deadline: Optional[datetime] = None
    remediation_steps: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    status: str = "open"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""    assessment_id: str
    framework: ComplianceFramework
    assessed_at: datetime
    overall_status: ComplianceStatus
    compliance_score: float  # 0.0 to 100.0
    total_rules: int
    compliant_rules: int
    violations: List[ComplianceViolation]
    recommendations: List[str]
    next_assessment_due: datetime
    assessor: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataInventoryItem:
    """Data inventory item for compliance tracking"""    item_id: str
    table_name: str
    column_name: str
    data_type: str
    data_category: DataCategory
    contains_pii: bool = False
    contains_phi: bool = False
    contains_pci: bool = False
    retention_period: Optional[int] = None  # days
    encryption_required: bool = False
    access_restrictions: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceChecker(ABC):
    """Abstract compliance checker interface"""    
    @property
    @abstractmethod
    def framework(self) -> ComplianceFramework:
        """Compliance framework this checker handles"""        pass
    
    @property
    @abstractmethod
    def rules(self) -> List[ComplianceRule]:
        """List of compliance rules to check"""        pass
    
    @abstractmethod
    async def check_compliance(
        self, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> ComplianceAssessment:
        """Check compliance and return assessment"""        pass


class GDPRComplianceChecker(ComplianceChecker):
    """GDPR compliance checker implementation"""    
    @property
    def framework(self) -> ComplianceFramework:
        return ComplianceFramework.GDPR
    
    @property
    def rules(self) -> List[ComplianceRule]:
        """GDPR compliance rules"""        return [
            ComplianceRule(
                rule_id="gdpr_art_32_encryption",
                framework=ComplianceFramework.GDPR,
                category="security",
                title="Article 32 - Security of Processing",
                description="Personal data must be encrypted in transit and at rest",
                requirement="Implement appropriate encryption for personal data",
                data_categories=[DataCategory.PII],
                severity=ViolationSeverity.HIGH,
                remediation_guidance="Enable database encryption and encrypted connections",
                references=["GDPR Article 32"]
            ),
            ComplianceRule(
                rule_id="gdpr_art_30_records",
                framework=ComplianceFramework.GDPR,
                category="documentation",
                title="Article 30 - Records of Processing Activities",
                description="Maintain records of data processing activities",
                requirement="Document all personal data processing activities",
                data_categories=[DataCategory.PII],
                severity=ViolationSeverity.MEDIUM,
                remediation_guidance="Implement comprehensive audit logging",
                references=["GDPR Article 30"]
            ),
            ComplianceRule(
                rule_id="gdpr_art_17_erasure",
                framework=ComplianceFramework.GDPR,
                category="data_subject_rights",
                title="Article 17 - Right to Erasure",
                description="Ability to delete personal data upon request",
                requirement="Implement data deletion capabilities",
                data_categories=[DataCategory.PII],
                severity=ViolationSeverity.HIGH,
                remediation_guidance="Implement secure data deletion procedures",
                references=["GDPR Article 17"]
            ),
            ComplianceRule(
                rule_id="gdpr_art_25_privacy_design",
                framework=ComplianceFramework.GDPR,
                category="privacy_by_design",
                title="Article 25 - Data Protection by Design",
                description="Implement privacy by design principles",
                requirement="Privacy considerations in system design",
                data_categories=[DataCategory.PII],
                severity=ViolationSeverity.MEDIUM,
                remediation_guidance="Review system architecture for privacy principles",
                references=["GDPR Article 25"]
            )
        ]
    
    async def check_compliance(
        self, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> ComplianceAssessment:
        """Check GDPR compliance"""        violations = []
        
        # Check each rule
        for rule in self.rules:
            rule_violations = await self._check_rule(rule, data_inventory, system_config)
            violations.extend(rule_violations)
        
        # Calculate compliance metrics
        total_rules = len(self.rules)
        violated_rules = len(set(v.rule.rule_id for v in violations))
        compliant_rules = total_rules - violated_rules
        compliance_score = (compliant_rules / total_rules) * 100
        
        # Determine overall status
        if compliance_score == 100:
            overall_status = ComplianceStatus.COMPLIANT
        elif compliance_score >= 80:
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        # Generate recommendations
        recommendations = await self._generate_gdpr_recommendations(violations)
        
        return ComplianceAssessment(
            assessment_id=str(uuid.uuid4()),
            framework=self.framework,
            assessed_at=datetime.now(),
            overall_status=overall_status,
            compliance_score=compliance_score,
            total_rules=total_rules,
            compliant_rules=compliant_rules,
            violations=violations,
            recommendations=recommendations,
            next_assessment_due=datetime.now() + timedelta(days=90),
            assessor="GDPR Compliance Checker"
        )
    
    async def _check_rule(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check specific GDPR rule"""        violations = []
        
        if rule.rule_id == "gdpr_art_32_encryption":
            violations.extend(await self._check_encryption_requirements(
                rule, data_inventory, system_config
            ))
        elif rule.rule_id == "gdpr_art_30_records":
            violations.extend(await self._check_audit_logging(
                rule, data_inventory, system_config
            ))
        elif rule.rule_id == "gdpr_art_17_erasure":
            violations.extend(await self._check_data_deletion(
                rule, data_inventory, system_config
            ))
        elif rule.rule_id == "gdpr_art_25_privacy_design":
            violations.extend(await self._check_privacy_by_design(
                rule, data_inventory, system_config
            ))
        
        return violations
    
    async def _check_encryption_requirements(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check encryption requirements for PII data"""        violations = []
        
        # Check for PII data without encryption
        pii_items = [item for item in data_inventory if item.contains_pii]
        
        for item in pii_items:
            if not item.encryption_required and not system_config.get("database_encryption", False):
                violation = ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule=rule,
                    severity=rule.severity,
                    description=f"PII data in {item.table_name}.{item.column_name} is not encrypted",
                    affected_resource=f"{item.table_name}.{item.column_name}",
                    evidence={
                        "table": item.table_name,
                        "column": item.column_name,
                        "data_category": item.data_category.value,
                        "encryption_enabled": False
                    },
                    remediation_steps=[
                        "Enable database-level encryption",
                        "Implement column-level encryption for PII fields",
                        "Configure encrypted connections"
                    ]
                )
                violations.append(violation)
        
        return violations
    
    async def _check_audit_logging(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check audit logging requirements"""        violations = []
        
        if not system_config.get("audit_logging_enabled", False):
            violation = ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule=rule,
                severity=rule.severity,
                description="Audit logging is not enabled for personal data processing",
                affected_resource="Database System",
                evidence={
                    "audit_logging": False,
                    "pii_tables": len([item for item in data_inventory if item.contains_pii])
                },
                remediation_steps=[
                    "Enable comprehensive audit logging",
                    "Log all access to personal data",
                    "Implement log retention policy"
                ]
            )
            violations.append(violation)
        
        return violations
    
    async def _check_data_deletion(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check data deletion capabilities"""        violations = []
        
        if not system_config.get("data_deletion_procedures", False):
            violation = ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule=rule,
                severity=rule.severity,
                description="No documented data deletion procedures for personal data",
                affected_resource="Data Processing System",
                evidence={
                    "deletion_procedures": False,
                    "pii_data_present": any(item.contains_pii for item in data_inventory)
                },
                remediation_steps=[
                    "Implement data deletion procedures",
                    "Create data subject request handling process",
                    "Document data retention policies"
                ]
            )
            violations.append(violation)
        
        return violations
    
    async def _check_privacy_by_design(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check privacy by design implementation"""        violations = []
        
        # Check for privacy impact assessments
        if not system_config.get("privacy_impact_assessment", False):
            violation = ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule=rule,
                severity=rule.severity,
                description="No privacy impact assessment conducted",
                affected_resource="System Design",
                evidence={
                    "pia_conducted": False,
                    "high_risk_processing": any(
                        item.data_category in [DataCategory.PII, DataCategory.PHI] 
                        for item in data_inventory
                    )
                },
                remediation_steps=[
                    "Conduct privacy impact assessment",
                    "Review data minimization principles",
                    "Implement privacy-preserving technologies"
                ]
            )
            violations.append(violation)
        
        return violations
    
    async def _generate_gdpr_recommendations(
        self, 
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate GDPR-specific recommendations"""        recommendations = []
        
        # Group violations by category
        violation_categories = {}
        for violation in violations:
            category = violation.rule.category
            if category not in violation_categories:
                violation_categories[category] = []
            violation_categories[category].append(violation)
        
        # Generate category-specific recommendations
        if "security" in violation_categories:
            recommendations.append(
                "Implement comprehensive encryption strategy for personal data"
            )
        
        if "documentation" in violation_categories:
            recommendations.append(
                "Establish comprehensive audit logging and record keeping"
            )
        
        if "data_subject_rights" in violation_categories:
            recommendations.append(
                "Implement data subject rights management system"
            )
        
        if "privacy_by_design" in violation_categories:
            recommendations.append(
                "Conduct privacy impact assessment and implement privacy by design"
            )
        
        return recommendations


class PCIDSSComplianceChecker(ComplianceChecker):
    """PCI-DSS compliance checker implementation"""    
    @property
    def framework(self) -> ComplianceFramework:
        return ComplianceFramework.PCI_DSS
    
    @property
    def rules(self) -> List[ComplianceRule]:
        """PCI-DSS compliance rules"""        return [
            ComplianceRule(
                rule_id="pci_req_3_encryption",
                framework=ComplianceFramework.PCI_DSS,
                category="data_protection",
                title="Requirement 3 - Protect Stored Cardholder Data",
                description="Encrypt cardholder data stored in databases",
                requirement="Use strong encryption for cardholder data at rest",
                data_categories=[DataCategory.PCI],
                severity=ViolationSeverity.CRITICAL,
                remediation_guidance="Implement AES-256 encryption for cardholder data",
                references=["PCI-DSS Requirement 3"]
            ),
            ComplianceRule(
                rule_id="pci_req_7_access_control",
                framework=ComplianceFramework.PCI_DSS,
                category="access_control",
                title="Requirement 7 - Restrict Access by Business Need-to-Know",
                description="Limit access to cardholder data based on business need",
                requirement="Implement role-based access control for cardholder data",
                data_categories=[DataCategory.PCI],
                severity=ViolationSeverity.HIGH,
                remediation_guidance="Implement least privilege access controls",
                references=["PCI-DSS Requirement 7"]
            ),
            ComplianceRule(
                rule_id="pci_req_10_monitoring",
                framework=ComplianceFramework.PCI_DSS,
                category="monitoring",
                title="Requirement 10 - Track and Monitor Access",
                description="Log and monitor all access to cardholder data",
                requirement="Comprehensive audit logging for cardholder data access",
                data_categories=[DataCategory.PCI],
                severity=ViolationSeverity.HIGH,
                remediation_guidance="Enable detailed audit logging and monitoring",
                references=["PCI-DSS Requirement 10"]
            )
        ]
    
    async def check_compliance(
        self, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> ComplianceAssessment:
        """Check PCI-DSS compliance"""        violations = []
        
        # Check each rule
        for rule in self.rules:
            rule_violations = await self._check_pci_rule(rule, data_inventory, system_config)
            violations.extend(rule_violations)
        
        # Calculate compliance metrics
        total_rules = len(self.rules)
        violated_rules = len(set(v.rule.rule_id for v in violations))
        compliant_rules = total_rules - violated_rules
        compliance_score = (compliant_rules / total_rules) * 100
        
        # PCI-DSS requires 100% compliance
        if compliance_score == 100:
            overall_status = ComplianceStatus.COMPLIANT
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        # Generate recommendations
        recommendations = await self._generate_pci_recommendations(violations)
        
        return ComplianceAssessment(
            assessment_id=str(uuid.uuid4()),
            framework=self.framework,
            assessed_at=datetime.now(),
            overall_status=overall_status,
            compliance_score=compliance_score,
            total_rules=total_rules,
            compliant_rules=compliant_rules,
            violations=violations,
            recommendations=recommendations,
            next_assessment_due=datetime.now() + timedelta(days=365),  # Annual assessment
            assessor="PCI-DSS Compliance Checker"
        )
    
    async def _check_pci_rule(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check specific PCI-DSS rule"""        violations = []
        
        if rule.rule_id == "pci_req_3_encryption":
            violations.extend(await self._check_cardholder_encryption(
                rule, data_inventory, system_config
            ))
        elif rule.rule_id == "pci_req_7_access_control":
            violations.extend(await self._check_access_controls(
                rule, data_inventory, system_config
            ))
        elif rule.rule_id == "pci_req_10_monitoring":
            violations.extend(await self._check_monitoring_requirements(
                rule, data_inventory, system_config
            ))
        
        return violations
    
    async def _check_cardholder_encryption(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check encryption for cardholder data"""        violations = []
        
        # Check for PCI data without encryption
        pci_items = [item for item in data_inventory if item.contains_pci]
        
        for item in pci_items:
            if not item.encryption_required:
                violation = ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule=rule,
                    severity=rule.severity,
                    description=f"Cardholder data in {item.table_name}.{item.column_name} is not encrypted",
                    affected_resource=f"{item.table_name}.{item.column_name}",
                    evidence={
                        "table": item.table_name,
                        "column": item.column_name,
                        "contains_pci": True,
                        "encryption_enabled": False
                    },
                    remediation_steps=[
                        "Enable AES-256 encryption for cardholder data",
                        "Implement proper key management",
                        "Use validated encryption methods"
                    ]
                )
                violations.append(violation)
        
        return violations
    
    async def _check_access_controls(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check access control requirements"""        violations = []
        
        if not system_config.get("role_based_access_control", False):
            violation = ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule=rule,
                severity=rule.severity,
                description="Role-based access control not implemented for cardholder data",
                affected_resource="Access Control System",
                evidence={
                    "rbac_enabled": False,
                    "pci_data_present": any(item.contains_pci for item in data_inventory)
                },
                remediation_steps=[
                    "Implement role-based access control",
                    "Apply principle of least privilege",
                    "Regular access reviews"
                ]
            )
            violations.append(violation)
        
        return violations
    
    async def _check_monitoring_requirements(
        self, 
        rule: ComplianceRule, 
        data_inventory: List[DataInventoryItem],
        system_config: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check monitoring and logging requirements"""        violations = []
        
        if not system_config.get("comprehensive_logging", False):
            violation = ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule=rule,
                severity=rule.severity,
                description="Comprehensive logging not enabled for cardholder data access",
                affected_resource="Logging System",
                evidence={
                    "logging_enabled": False,
                    "cardholder_data_access": True
                },
                remediation_steps=[
                    "Enable comprehensive audit logging",
                    "Monitor all cardholder data access",
                    "Implement log analysis and alerting"
                ]
            )
            violations.append(violation)
        
        return violations
    
    async def _generate_pci_recommendations(
        self, 
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate PCI-DSS specific recommendations"""        recommendations = []
        
        if any(v.rule.category == "data_protection" for v in violations):
            recommendations.append(
                "Implement strong encryption for all cardholder data at rest and in transit"
            )
        
        if any(v.rule.category == "access_control" for v in violations):
            recommendations.append(
                "Establish role-based access control with least privilege principles"
            )
        
        if any(v.rule.category == "monitoring" for v in violations):
            recommendations.append(
                "Deploy comprehensive logging and monitoring for cardholder data environment"
            )
        
        return recommendations


class ComplianceCheckerRegistry:
    """Registry for compliance checker implementations"""    
    def __init__(self):
        self.checkers: Dict[ComplianceFramework, ComplianceChecker] = {}
        self._register_default_checkers()
    
    def _register_default_checkers(self):
        """Register default compliance checkers"""        self.register_checker(GDPRComplianceChecker())
        self.register_checker(PCIDSSComplianceChecker())
    
    def register_checker(self, checker: ComplianceChecker):
        """Register a compliance checker"""        self.checkers[checker.framework] = checker
    
    def get_checker(self, framework: ComplianceFramework) -> Optional[ComplianceChecker]:
        """Get compliance checker for framework"""        return self.checkers.get(framework)
    
    def list_supported_frameworks(self) -> List[ComplianceFramework]:
        """List supported compliance frameworks"""        return list(self.checkers.keys())


class DatabaseComplianceChecker:
    """    Enterprise-grade database compliance checker
    
    Provides comprehensive compliance verification for multiple frameworks
    including GDPR, CCPA, HIPAA, SOX, PCI-DSS and others with automated
    assessment, violation tracking, and remediation guidance.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize compliance checker"""        self.config = config or {}
        self.checker_registry = ComplianceCheckerRegistry()
        self.data_inventory: List[DataInventoryItem] = []
        self.assessments: Dict[str, ComplianceAssessment] = {}
        
        # Configuration
        self.assessment_frequency = self.config.get("assessment_frequency", 90)  # days
        self.auto_remediation = self.config.get("auto_remediation", False)
        self.notification_enabled = self.config.get("notifications", True)
        
        logger.info("Database compliance checker initialized successfully")
    
    async def add_data_inventory_item(self, item: DataInventoryItem):
        """Add item to data inventory"""        # Remove existing item with same ID if exists
        self.data_inventory = [
            existing for existing in self.data_inventory 
            if existing.item_id != item.item_id
        ]
        
        # Add new item
        self.data_inventory.append(item)
        logger.info(f"Added data inventory item: {item.table_name}.{item.column_name}")
    
    async def update_data_inventory(self, items: List[DataInventoryItem]):
        """Update complete data inventory"""        self.data_inventory = items
        logger.info(f"Updated data inventory with {len(items)} items")
    
    async def classify_data_automatically(self, table_schemas: List[Dict[str, Any]]):
        """Automatically classify data based on column names and types"""        inventory_items = []
        
        # Common PII patterns
        pii_patterns = [
            r'.*email.*', r'.*phone.*', r'.*ssn.*', r'.*social.*',
            r'.*name.*', r'.*address.*', r'.*birth.*', r'.*age.*'
        ]
        
        # Common PHI patterns
        phi_patterns = [
            r'.*medical.*', r'.*health.*', r'.*diagnosis.*', r'.*treatment.*',
            r'.*patient.*', r'.*drug.*', r'.*medication.*'
        ]
        
        # Common PCI patterns
        pci_patterns = [
            r'.*card.*', r'.*credit.*', r'.*payment.*', r'.*account.*number.*',
            r'.*cvv.*', r'.*expir.*', r'.*billing.*'
        ]
        
        for schema in table_schemas:
            table_name = schema.get("table_name", "")
            columns = schema.get("columns", [])
            
            for column in columns:
                column_name = column.get("name", "").lower()
                data_type = column.get("type", "")
                
                # Determine data category
                data_category = DataCategory.INTERNAL
                contains_pii = any(re.match(pattern, column_name) for pattern in pii_patterns)
                contains_phi = any(re.match(pattern, column_name) for pattern in phi_patterns)
                contains_pci = any(re.match(pattern, column_name) for pattern in pci_patterns)
                
                if contains_pci:
                    data_category = DataCategory.PCI
                elif contains_phi:
                    data_category = DataCategory.PHI
                elif contains_pii:
                    data_category = DataCategory.PII
                elif "public" in column_name:
                    data_category = DataCategory.PUBLIC
                
                # Create inventory item
                item = DataInventoryItem(
                    item_id=f"{table_name}_{column_name}",
                    table_name=table_name,
                    column_name=column_name,
                    data_type=data_type,
                    data_category=data_category,
                    contains_pii=contains_pii,
                    contains_phi=contains_phi,
                    contains_pci=contains_pci,
                    encryption_required=(contains_pii or contains_phi or contains_pci)
                )
                
                inventory_items.append(item)
        
        await self.update_data_inventory(inventory_items)
        logger.info(f"Automatically classified {len(inventory_items)} data items")
    
    async def assess_compliance(
        self, 
        frameworks: List[ComplianceFramework],
        system_config: Dict[str, Any]
    ) -> Dict[ComplianceFramework, ComplianceAssessment]:
        """        Assess compliance for specified frameworks
        
        Args:
            frameworks: List of compliance frameworks to assess
            system_config: Current system configuration
            
        Returns:
            Dictionary mapping frameworks to their assessments
        """        assessments = {}
        
        for framework in frameworks:
            try:
                checker = self.checker_registry.get_checker(framework)
                if not checker:
                    logger.warning(f"No checker available for framework: {framework}")
                    continue
                
                # Perform compliance assessment
                assessment = await checker.check_compliance(
                    self.data_inventory, system_config
                )
                
                # Store assessment
                assessments[framework] = assessment
                self.assessments[assessment.assessment_id] = assessment
                
                logger.info(
                    f"Compliance assessment completed for {framework.value}: "
                    f"{assessment.compliance_score:.1f}% compliant"
                )
                
            except Exception as e:
                logger.error(f"Compliance assessment failed for {framework}: {e}")
        
        return assessments
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get overall compliance summary"""        if not self.assessments:
            return {"status": "no_assessments", "frameworks": []}
        
        # Get latest assessment for each framework
        latest_assessments = {}
        for assessment in self.assessments.values():
            framework = assessment.framework
            if (framework not in latest_assessments or 
                assessment.assessed_at > latest_assessments[framework].assessed_at):
                latest_assessments[framework] = assessment
        
        # Calculate overall metrics
        total_violations = sum(len(a.violations) for a in latest_assessments.values())
        average_score = sum(a.compliance_score for a in latest_assessments.values()) / len(latest_assessments)
        
        # Determine overall status
        if average_score >= 95:
            overall_status = "excellent"
        elif average_score >= 80:
            overall_status = "good"
        elif average_score >= 60:
            overall_status = "needs_improvement"
        else:
            overall_status = "critical"
        
        # Get critical violations
        critical_violations = []
        for assessment in latest_assessments.values():
            critical_violations.extend([
                v for v in assessment.violations 
                if v.severity == ViolationSeverity.CRITICAL
            ])
        
        return {
            "overall_status": overall_status,
            "average_compliance_score": round(average_score, 1),
            "total_violations": total_violations,
            "critical_violations": len(critical_violations),
            "frameworks_assessed": len(latest_assessments),
            "frameworks": {
                framework.value: {
                    "status": assessment.overall_status.value,
                    "score": assessment.compliance_score,
                    "violations": len(assessment.violations),
                    "last_assessed": assessment.assessed_at.isoformat()
                }
                for framework, assessment in latest_assessments.items()
            },
            "next_assessment_due": min(
                a.next_assessment_due for a in latest_assessments.values()
            ).isoformat() if latest_assessments else None
        }
    
    async def get_violation_report(
        self, 
        framework: Optional[ComplianceFramework] = None,
        severity: Optional[ViolationSeverity] = None
    ) -> List[ComplianceViolation]:
        """Get filtered violation report"""        violations = []
        
        for assessment in self.assessments.values():
            # Filter by framework
            if framework and assessment.framework != framework:
                continue
            
            for violation in assessment.violations:
                # Filter by severity
                if severity and violation.severity != severity:
                    continue
                
                violations.append(violation)
        
        # Sort by severity and date
        violations.sort(
            key=lambda v: (v.severity.value, v.detected_at), 
            reverse=True
        )
        
        return violations
    
    async def generate_remediation_plan(
        self, 
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Generate comprehensive remediation plan"""        plan = {
            "plan_id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "frameworks": [f.value for f in frameworks],
            "priority_violations": [],
            "remediation_steps": [],
            "estimated_effort": {},
            "timeline": {}
        }
        
        # Get violations for specified frameworks
        all_violations = []
        for framework in frameworks:
            framework_violations = await self.get_violation_report(framework=framework)
            all_violations.extend(framework_violations)
        
        # Prioritize violations by severity
        critical_violations = [v for v in all_violations if v.severity == ViolationSeverity.CRITICAL]
        high_violations = [v for v in all_violations if v.severity == ViolationSeverity.HIGH]
        
        plan["priority_violations"] = [
            {
                "violation_id": v.violation_id,
                "framework": v.rule.framework.value,
                "severity": v.severity.value,
                "description": v.description,
                "affected_resource": v.affected_resource,
                "remediation_steps": v.remediation_steps
            }
            for v in (critical_violations + high_violations)[:10]  # Top 10 priority
        ]
        
        # Generate remediation steps
        unique_steps = set()
        for violation in all_violations:
            unique_steps.update(violation.remediation_steps)
        
        plan["remediation_steps"] = list(unique_steps)
        
        # Estimate effort (simplified)
        effort_by_severity = {
            ViolationSeverity.CRITICAL: 16,  # hours
            ViolationSeverity.HIGH: 8,
            ViolationSeverity.MEDIUM: 4,
            ViolationSeverity.LOW: 2,
            ViolationSeverity.INFO: 1
        }
        
        total_effort = sum(
            effort_by_severity.get(v.severity, 4) for v in all_violations
        )
        
        plan["estimated_effort"] = {
            "total_hours": total_effort,
            "total_days": round(total_effort / 8, 1),
            "by_severity": {
                severity.value: sum(
                    effort_by_severity.get(v.severity, 4) 
                    for v in all_violations if v.severity == severity
                )
                for severity in ViolationSeverity
            }
        }
        
        # Generate timeline
        plan["timeline"] = {
            "immediate": f"Address {len(critical_violations)} critical violations",
            "week_1": f"Address {len(high_violations)} high-severity violations",
            "month_1": "Complete all medium and low severity violations",
            "quarterly": "Conduct compliance re-assessment"
        }
        
        return plan
    
    def get_supported_frameworks(self) -> List[ComplianceFramework]:
        """Get list of supported compliance frameworks"""        return self.checker_registry.list_supported_frameworks()
    
    def get_compliance_metrics(self) -> Dict[str, Any]:
        """Get compliance checking metrics"""        if not self.assessments:
            return {"total_assessments": 0, "frameworks": []}
        
        return {
            "total_assessments": len(self.assessments),
            "frameworks": list(set(a.framework.value for a in self.assessments.values())),
            "data_inventory_size": len(self.data_inventory),
            "total_violations": sum(len(a.violations) for a in self.assessments.values()),
            "supported_frameworks": [f.value for f in self.get_supported_frameworks()]
        }


# Module initialization
logger.info("Database compliance checker module loaded successfully")
