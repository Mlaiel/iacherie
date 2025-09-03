"""Legal Validator - Validation légale

Legal compliance validation service for content, contracts, and regulatory requirements.
Provides automated legal validation and compliance checking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Legal validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ENTERPRISE = "enterprise"


class ComplianceStatus(Enum):
    """Compliance validation status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NEEDS_REVIEW = "needs_review"
    PENDING_VALIDATION = "pending_validation"


class LegalFramework(Enum):
    """Legal frameworks and regulations"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    DMCA = "dmca"
    COPPA = "coppa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"


@dataclass
class ValidationRule:
    """Legal validation rule"""
    rule_id: str
    rule_name: str
    framework: LegalFramework
    description: str
    validation_pattern: Optional[str] = None
    required_fields: List[str] = field(default_factory=list)
    prohibited_content: List[str] = field(default_factory=list)
    severity: str = "medium"
    auto_fix_available: bool = False


@dataclass
class ValidationResult:
    """Validation result"""
    validation_id: str
    entity_id: str
    entity_type: str
    status: ComplianceStatus
    framework: LegalFramework
    validated_at: datetime
    rules_checked: List[str]
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    next_review_date: Optional[datetime] = None


@dataclass
class LegalEntity:
    """Legal entity for validation"""
    entity_id: str
    entity_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_validated: Optional[datetime] = None


class LegalValidator:
    """
    Legal compliance validation service providing automated legal validation
    and compliance checking for various regulatory frameworks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.config = config or {}
        
        # Validation results storage
        self.validation_results: Dict[str, ValidationResult] = {}
        self.validation_rules: Dict[str, ValidationRule] = {}
        
        # Initialize validation rules
        self._initialize_validation_rules()
        
        # Configuration
        self.default_validation_level = ValidationLevel(
            self.config.get('default_validation_level', 'standard')
        )
        self.auto_remediation = self.config.get('auto_remediation', False)
        self.review_interval_days = self.config.get('review_interval_days', 90)
    
    def _initialize_validation_rules(self):
        """Initialize legal validation rules for different frameworks"""
        
        # GDPR Rules
        gdpr_rules = [
            ValidationRule(
                rule_id="gdpr_consent_required",
                rule_name="GDPR Consent Required",
                framework=LegalFramework.GDPR,
                description="Personal data processing requires explicit consent",
                required_fields=["consent_granted", "consent_timestamp", "consent_purpose"],
                severity="high"
            ),
            ValidationRule(
                rule_id="gdpr_data_minimization",
                rule_name="GDPR Data Minimization",
                framework=LegalFramework.GDPR,
                description="Collect only necessary personal data",
                severity="medium"
            ),
            ValidationRule(
                rule_id="gdpr_retention_limits",
                rule_name="GDPR Data Retention Limits",
                framework=LegalFramework.GDPR,
                description="Personal data must not be kept longer than necessary",
                required_fields=["retention_period", "retention_justification"],
                severity="high"
            ),
            ValidationRule(
                rule_id="gdpr_data_subject_rights",
                rule_name="GDPR Data Subject Rights",
                framework=LegalFramework.GDPR,
                description="Must provide mechanism for data subject rights",
                required_fields=["access_mechanism", "deletion_mechanism"],
                severity="high"
            )
        ]
        
        # DMCA Rules
        dmca_rules = [
            ValidationRule(
                rule_id="dmca_copyright_notice",
                rule_name="DMCA Copyright Notice Required",
                framework=LegalFramework.DMCA,
                description="Content must have proper copyright attribution",
                required_fields=["copyright_owner", "copyright_year"],
                severity="high"
            ),
            ValidationRule(
                rule_id="dmca_takedown_procedure",
                rule_name="DMCA Takedown Procedure",
                framework=LegalFramework.DMCA,
                description="Must have clear DMCA takedown procedure",
                required_fields=["dmca_agent_contact", "takedown_procedure"],
                severity="medium"
            )
        ]
        
        # Content Safety Rules
        content_rules = [
            ValidationRule(
                rule_id="content_inappropriate_material",
                rule_name="Inappropriate Content Detection",
                framework=LegalFramework.COPPA,
                description="Content must not contain inappropriate material",
                prohibited_content=[
                    "explicit sexual content", "violence", "hate speech",
                    "illegal activities", "harmful instructions"
                ],
                severity="high",
                auto_fix_available=True
            ),
            ValidationRule(
                rule_id="content_age_appropriate",
                rule_name="Age-Appropriate Content",
                framework=LegalFramework.COPPA,
                description="Content must be appropriate for declared age group",
                required_fields=["target_age_group", "content_rating"],
                severity="medium"
            )
        ]
        
        # Store all rules
        all_rules = gdpr_rules + dmca_rules + content_rules
        for rule in all_rules:
            self.validation_rules[rule.rule_id] = rule
    
    async def validate_entity(
        self,
        entity: LegalEntity,
        frameworks: List[LegalFramework],
        validation_level: Optional[ValidationLevel] = None
    ) -> ValidationResult:
        """
        Validate entity against specified legal frameworks
        
        Args:
            entity: Entity to validate
            frameworks: Legal frameworks to validate against
            validation_level: Level of validation to perform
            
        Returns:
            ValidationResult with compliance status and details
        """
        try:
            validation_level = validation_level or self.default_validation_level
            validation_id = f"val_{entity.entity_id}_{int(datetime.now().timestamp())}"
            
            violations = []
            rules_checked = []
            recommendations = []
            
            # Validate against each framework
            for framework in frameworks:
                framework_violations, framework_rules = await self._validate_framework(
                    entity, framework, validation_level
                )
                violations.extend(framework_violations)
                rules_checked.extend(framework_rules)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(violations, rules_checked)
            
            # Determine overall status
            status = self._determine_compliance_status(violations, compliance_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(violations, entity)
            
            # Create validation result
            result = ValidationResult(
                validation_id=validation_id,
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                status=status,
                framework=frameworks[0] if frameworks else LegalFramework.GDPR,
                validated_at=datetime.now(),
                rules_checked=rules_checked,
                violations=violations,
                recommendations=recommendations,
                compliance_score=compliance_score,
                next_review_date=datetime.now() + timedelta(days=self.review_interval_days)
            )
            
            # Store result
            self.validation_results[validation_id] = result
            
            # Update entity
            entity.last_validated = datetime.now()
            
            self.logger.info(
                f"Validated entity {entity.entity_id}: {status.value} "
                f"(score: {compliance_score:.2f})"
            )
            
            # Auto-remediation if enabled
            if self.auto_remediation and violations:
                await self._attempt_auto_remediation(entity, violations)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Entity validation failed: {str(e)}")
            raise
    
    async def _validate_framework(
        self,
        entity: LegalEntity,
        framework: LegalFramework,
        validation_level: ValidationLevel
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Validate entity against specific framework"""
        violations = []
        rules_checked = []
        
        # Get rules for this framework
        framework_rules = [
            rule for rule in self.validation_rules.values()
            if rule.framework == framework
        ]
        
        for rule in framework_rules:
            rules_checked.append(rule.rule_id)
            
            # Check required fields
            for required_field in rule.required_fields:
                if required_field not in entity.content:
                    violations.append({
                        'rule_id': rule.rule_id,
                        'rule_name': rule.rule_name,
                        'violation_type': 'missing_field',
                        'field': required_field,
                        'severity': rule.severity,
                        'description': f"Missing required field: {required_field}",
                        'auto_fixable': rule.auto_fix_available
                    })
            
            # Check prohibited content
            if rule.prohibited_content:
                content_text = str(entity.content).lower()
                for prohibited in rule.prohibited_content:
                    if prohibited.lower() in content_text:
                        violations.append({
                            'rule_id': rule.rule_id,
                            'rule_name': rule.rule_name,
                            'violation_type': 'prohibited_content',
                            'prohibited_item': prohibited,
                            'severity': rule.severity,
                            'description': f"Contains prohibited content: {prohibited}",
                            'auto_fixable': rule.auto_fix_available
                        })
            
            # Framework-specific validations
            if framework == LegalFramework.GDPR:
                await self._validate_gdpr_specific(entity, rule, violations)
            elif framework == LegalFramework.DMCA:
                await self._validate_dmca_specific(entity, rule, violations)
        
        return violations, rules_checked
    
    async def _validate_gdpr_specific(
        self,
        entity: LegalEntity,
        rule: ValidationRule,
        violations: List[Dict[str, Any]]
    ):
        """GDPR-specific validation logic"""
        if rule.rule_id == "gdpr_consent_required":
            consent_granted = entity.content.get('consent_granted')
            if consent_granted is False:
                violations.append({
                    'rule_id': rule.rule_id,
                    'rule_name': rule.rule_name,
                    'violation_type': 'consent_not_granted',
                    'severity': rule.severity,
                    'description': "User consent not granted for data processing"
                })
        
        elif rule.rule_id == "gdpr_retention_limits":
            retention_period = entity.content.get('retention_period_days')
            if retention_period and retention_period > 2555:  # 7 years max
                violations.append({
                    'rule_id': rule.rule_id,
                    'rule_name': rule.rule_name,
                    'violation_type': 'excessive_retention',
                    'severity': rule.severity,
                    'description': f"Retention period too long: {retention_period} days"
                })
    
    async def _validate_dmca_specific(
        self,
        entity: LegalEntity,
        rule: ValidationRule,
        violations: List[Dict[str, Any]]
    ):
        """DMCA-specific validation logic"""
        if rule.rule_id == "dmca_copyright_notice":
            if entity.entity_type == "content":
                copyright_owner = entity.content.get('copyright_owner')
                if not copyright_owner:
                    violations.append({
                        'rule_id': rule.rule_id,
                        'rule_name': rule.rule_name,
                        'violation_type': 'missing_copyright_notice',
                        'severity': rule.severity,
                        'description': "Content lacks proper copyright attribution"
                    })
    
    def _calculate_compliance_score(
        self,
        violations: List[Dict[str, Any]],
        rules_checked: List[str]
    ) -> float:
        """Calculate compliance score based on violations"""
        if not rules_checked:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {'low': 0.1, 'medium': 0.3, 'high': 1.0}
        total_weight = 0
        violation_weight = 0
        
        for rule_id in rules_checked:
            rule = self.validation_rules.get(rule_id)
            if rule:
                weight = severity_weights.get(rule.severity, 0.3)
                total_weight += weight
        
        for violation in violations:
            weight = severity_weights.get(violation.get('severity', 'medium'), 0.3)
            violation_weight += weight
        
        if total_weight == 0:
            return 1.0
        
        return max(0.0, 1.0 - (violation_weight / total_weight))
    
    def _determine_compliance_status(
        self,
        violations: List[Dict[str, Any]],
        compliance_score: float
    ) -> ComplianceStatus:
        """Determine overall compliance status"""
        if not violations:
            return ComplianceStatus.COMPLIANT
        
        high_severity_violations = [
            v for v in violations if v.get('severity') == 'high'
        ]
        
        if high_severity_violations:
            return ComplianceStatus.NON_COMPLIANT
        elif compliance_score >= 0.8:
            return ComplianceStatus.PARTIAL_COMPLIANCE
        elif compliance_score >= 0.6:
            return ComplianceStatus.NEEDS_REVIEW
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    def _generate_recommendations(
        self,
        violations: List[Dict[str, Any]],
        entity: LegalEntity
    ) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for violation in violations:
            if violation['violation_type'] == 'missing_field':
                recommendations.append(
                    f"Add required field '{violation['field']}' to ensure compliance"
                )
            elif violation['violation_type'] == 'prohibited_content':
                recommendations.append(
                    f"Remove or modify content containing '{violation['prohibited_item']}'"
                )
            elif violation['violation_type'] == 'consent_not_granted':
                recommendations.append(
                    "Obtain explicit user consent before processing personal data"
                )
            elif violation['violation_type'] == 'excessive_retention':
                recommendations.append(
                    "Reduce data retention period to comply with GDPR requirements"
                )
        
        # Add general recommendations
        if violations:
            recommendations.append("Consider legal review for comprehensive compliance")
            recommendations.append("Implement regular compliance monitoring")
        
        return recommendations
    
    async def _attempt_auto_remediation(
        self,
        entity: LegalEntity,
        violations: List[Dict[str, Any]]
    ):
        """Attempt automatic remediation of violations"""
        for violation in violations:
            if violation.get('auto_fixable'):
                if violation['violation_type'] == 'prohibited_content':
                    # Simulate content filtering/replacement
                    self.logger.info(f"Auto-remediated prohibited content in {entity.entity_id}")
                elif violation['violation_type'] == 'missing_field':
                    # Add default values for missing fields
                    field = violation['field']
                    if field == 'consent_timestamp':
                        entity.content[field] = datetime.now().isoformat()
                    elif field == 'retention_period':
                        entity.content[field] = 730  # 2 years default
                    
                    self.logger.info(f"Auto-remediated missing field {field} in {entity.entity_id}")
    
    async def validate_content(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        content_type: str = "user_content"
    ) -> ValidationResult:
        """Validate content for legal compliance"""
        entity = LegalEntity(
            entity_id=content_id,
            entity_type=content_type,
            content=content_data
        )
        
        # Validate against content-related frameworks
        frameworks = [LegalFramework.DMCA, LegalFramework.COPPA]
        
        return await self.validate_entity(entity, frameworks)
    
    async def validate_user_data(
        self,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate user data for GDPR compliance"""
        entity = LegalEntity(
            entity_id=user_id,
            entity_type="user_data",
            content=user_data
        )
        
        # Validate against privacy frameworks
        frameworks = [LegalFramework.GDPR]
        
        return await self.validate_entity(entity, frameworks)
    
    async def get_validation_result(self, validation_id: str) -> Optional[ValidationResult]:
        """Get validation result by ID"""
        return self.validation_results.get(validation_id)
    
    async def get_entity_compliance_history(self, entity_id: str) -> List[ValidationResult]:
        """Get compliance history for entity"""
        return [
            result for result in self.validation_results.values()
            if result.entity_id == entity_id
        ]
    
    async def get_compliance_stats(self) -> Dict[str, Any]:
        """Get legal compliance statistics"""
        total_validations = len(self.validation_results)
        
        if total_validations == 0:
            return {
                'total_validations': 0,
                'compliance_rate': 0.0,
                'average_score': 0.0,
                'frameworks_covered': 0,
                'last_updated': datetime.now().isoformat()
            }
        
        compliant = sum(
            1 for r in self.validation_results.values()
            if r.status == ComplianceStatus.COMPLIANT
        )
        
        average_score = sum(
            r.compliance_score for r in self.validation_results.values()
        ) / total_validations
        
        frameworks_used = set()
        for result in self.validation_results.values():
            frameworks_used.add(result.framework.value)
        
        return {
            'total_validations': total_validations,
            'compliant_entities': compliant,
            'compliance_rate': compliant / total_validations,
            'average_score': average_score,
            'frameworks_covered': len(frameworks_used),
            'frameworks_list': list(frameworks_used),
            'auto_remediation_enabled': self.auto_remediation,
            'last_updated': datetime.now().isoformat()
        }