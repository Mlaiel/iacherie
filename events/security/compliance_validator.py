"""Compliance Validator for Events Security

Real-time compliance validation for GDPR, CCPA, SOX, and other regulations.
Ensures all events meet regulatory requirements and data protection standards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceRegulation(Enum):
    """Supported compliance regulations"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    COPPA = "coppa"


class ViolationSeverity(Enum):
    """Severity levels for compliance violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """Represents a compliance rule"""
    rule_id: str
    regulation: ComplianceRegulation
    name: str
    description: str
    event_types: List[str]
    required_fields: List[str]
    validation_logic: str
    severity: ViolationSeverity
    
    def applies_to_event(self, event_type: str) -> bool:
        """Check if rule applies to given event type"""
        return any(pattern in event_type for pattern in self.event_types)


@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""
    violation_id: str
    rule_id: str
    regulation: ComplianceRegulation
    event_id: str
    user_id: str
    violation_type: str
    description: str
    severity: ViolationSeverity
    detected_at: datetime
    business_context: Dict[str, Any]
    remediation_required: bool = True
    auto_correctable: bool = False
    
    def __post_init__(self):
        if self.business_context is None:
            self.business_context = {}


@dataclass
class ComplianceValidationResult:
    """Result of compliance validation"""
    event_id: str
    compliant: bool
    violations: List[ComplianceViolation]
    warnings: List[str]
    regulations_checked: List[ComplianceRegulation]
    validation_timestamp: datetime
    
    def __post_init__(self):
        if self.validation_timestamp is None:
            self.validation_timestamp = datetime.utcnow()


class ComplianceValidator:
    """
    Advanced compliance validator for Ainflue business events.
    Real-time validation against multiple regulatory frameworks.
    """
    
    def __init__(self):
        self.enabled = True
        self.compliance_rules = self._initialize_compliance_rules()
        self.user_consents = {}  # user_id -> {regulation: consent_data}
        self.data_retention_policies = self._initialize_retention_policies()
        self.violation_history = []
        self.auto_correction_enabled = True
        logger.info("ComplianceValidator initialized")
    
    async def validate_event_compliance(self,
                                      event: Any,
                                      user_id: str,
                                      business_context: Dict[str, Any] = None) -> ComplianceValidationResult:
        """
        Validate event compliance against all applicable regulations.
        
        Args:
            event: Domain event to validate
            user_id: User ID associated with the event
            business_context: Business context for validation
            
        Returns:
            ComplianceValidationResult with validation outcome
        """
        if not self.enabled:
            return self._create_permissive_result(event)
        
        try:
            business_context = business_context or {}
            event_id = getattr(event, 'event_id', 'unknown')
            event_type = getattr(event, 'event_type', 'unknown')
            event_data = getattr(event, 'data', {})
            
            # Identify applicable regulations
            applicable_regulations = await self._identify_applicable_regulations(
                event_type, user_id, business_context
            )
            
            # Validate against each regulation
            violations = []
            warnings = []
            
            for regulation in applicable_regulations:
                regulation_violations, regulation_warnings = await self._validate_against_regulation(
                    regulation, event_id, event_type, event_data, user_id, business_context
                )
                violations.extend(regulation_violations)
                warnings.extend(regulation_warnings)
            
            # Auto-correct violations if enabled
            if self.auto_correction_enabled and violations:
                corrected_violations = await self._attempt_auto_correction(violations, event, business_context)
                violations = [v for v in violations if v not in corrected_violations]
            
            # Store violations for tracking
            for violation in violations:
                self.violation_history.append(violation)
            
            compliant = len(violations) == 0
            
            result = ComplianceValidationResult(
                event_id=event_id,
                compliant=compliant,
                violations=violations,
                warnings=warnings,
                regulations_checked=applicable_regulations
            )
            
            # Log compliance issues
            if not compliant:
                logger.warning(f"Compliance violations detected for event {event_id}: {len(violations)} violations")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in compliance validation: {str(e)}")
            return self._create_error_result(event, str(e))
    
    async def _identify_applicable_regulations(self,
                                             event_type: str,
                                             user_id: str,
                                             business_context: Dict[str, Any]) -> List[ComplianceRegulation]:
        """Identify which regulations apply to this event"""
        
        applicable = []
        
        # Check user location for regional regulations
        user_region = business_context.get('user_region', 'unknown')
        
        # GDPR applies to EU users
        if user_region in ['EU', 'UK', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE']:
            applicable.append(ComplianceRegulation.GDPR)
        
        # CCPA applies to California users
        if user_region in ['CA', 'US-CA']:
            applicable.append(ComplianceRegulation.CCPA)
        
        # SOX applies to financial events
        if event_type.startswith('monetization.') or 'financial' in event_type:
            applicable.append(ComplianceRegulation.SOX)
        
        # PCI-DSS applies to payment events
        if 'payment' in event_type or business_context.get('payment_data_involved', False):
            applicable.append(ComplianceRegulation.PCI_DSS)
        
        # HIPAA applies to health data (if applicable to creator content)
        if business_context.get('health_data_involved', False):
            applicable.append(ComplianceRegulation.HIPAA)
        
        # COPPA applies to users under 13
        user_age = business_context.get('user_age', 18)
        if user_age < 13:
            applicable.append(ComplianceRegulation.COPPA)
        
        return applicable
    
    async def _validate_against_regulation(self,
                                         regulation: ComplianceRegulation,
                                         event_id: str,
                                         event_type: str,
                                         event_data: Dict[str, Any],
                                         user_id: str,
                                         business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate event against specific regulation"""
        
        violations = []
        warnings = []
        
        if regulation == ComplianceRegulation.GDPR:
            v, w = await self._validate_gdpr(event_id, event_type, event_data, user_id, business_context)
            violations.extend(v)
            warnings.extend(w)
        
        elif regulation == ComplianceRegulation.CCPA:
            v, w = await self._validate_ccpa(event_id, event_type, event_data, user_id, business_context)
            violations.extend(v)
            warnings.extend(w)
        
        elif regulation == ComplianceRegulation.SOX:
            v, w = await self._validate_sox(event_id, event_type, event_data, user_id, business_context)
            violations.extend(v)
            warnings.extend(w)
        
        elif regulation == ComplianceRegulation.PCI_DSS:
            v, w = await self._validate_pci_dss(event_id, event_type, event_data, user_id, business_context)
            violations.extend(v)
            warnings.extend(w)
        
        elif regulation == ComplianceRegulation.HIPAA:
            v, w = await self._validate_hipaa(event_id, event_type, event_data, user_id, business_context)
            violations.extend(v)
            warnings.extend(w)
        
        elif regulation == ComplianceRegulation.COPPA:
            v, w = await self._validate_coppa(event_id, event_type, event_data, user_id, business_context)
            violations.extend(v)
            warnings.extend(w)
        
        return violations, warnings
    
    async def _validate_gdpr(self,
                           event_id: str,
                           event_type: str,
                           event_data: Dict[str, Any],
                           user_id: str,
                           business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate GDPR compliance"""
        
        violations = []
        warnings = []
        
        # Check for valid consent
        if not await self._check_user_consent(user_id, ComplianceRegulation.GDPR):
            violations.append(ComplianceViolation(
                violation_id=f"gdpr_consent_{event_id}",
                rule_id="gdpr_consent_required",
                regulation=ComplianceRegulation.GDPR,
                event_id=event_id,
                user_id=user_id,
                violation_type="missing_consent",
                description="Missing or invalid GDPR consent for data processing",
                severity=ViolationSeverity.CRITICAL,
                detected_at=datetime.utcnow(),
                business_context=business_context,
                auto_correctable=True
            ))
        
        # Check data subject rights events
        if event_type in ['user.data.export', 'user.data.delete', 'user.data.update']:
            # Must complete within 30 days
            request_date = business_context.get('request_date')
            if request_date:
                days_since_request = (datetime.utcnow() - request_date).days
                if days_since_request > 30:
                    violations.append(ComplianceViolation(
                        violation_id=f"gdpr_response_time_{event_id}",
                        rule_id="gdpr_response_time",
                        regulation=ComplianceRegulation.GDPR,
                        event_id=event_id,
                        user_id=user_id,
                        violation_type="response_time_exceeded",
                        description=f"GDPR data subject rights request exceeded 30-day response time: {days_since_request} days",
                        severity=ViolationSeverity.HIGH,
                        detected_at=datetime.utcnow(),
                        business_context=business_context
                    ))
        
        # Check for lawful basis
        if event_type.startswith('user.data.') or event_type.startswith('content.processing'):
            lawful_basis = business_context.get('lawful_basis')
            if not lawful_basis:
                warnings.append("GDPR lawful basis not specified for data processing")
        
        # Check data minimization
        data_fields = event_data.keys()
        if len(data_fields) > 10:  # Arbitrary threshold for demo
            warnings.append("Consider data minimization - large number of data fields processed")
        
        # Check data retention
        if not business_context.get('retention_policy_applied'):
            warnings.append("GDPR data retention policy should be applied")
        
        return violations, warnings
    
    async def _validate_ccpa(self,
                           event_id: str,
                           event_type: str,
                           event_data: Dict[str, Any],
                           user_id: str,
                           business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate CCPA compliance"""
        
        violations = []
        warnings = []
        
        # Check for data sale events
        if 'data.sale' in event_type or business_context.get('data_sale_involved', False):
            # Must verify opt-out status
            opt_out_verified = business_context.get('opt_out_verified', False)
            if not opt_out_verified:
                violations.append(ComplianceViolation(
                    violation_id=f"ccpa_optout_{event_id}",
                    rule_id="ccpa_optout_verification",
                    regulation=ComplianceRegulation.CCPA,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="opt_out_not_verified",
                    description="CCPA opt-out status not verified before data sale",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
        
        # Check for personal information collection
        if event_type.startswith('user.') or 'personal_info' in business_context:
            purpose_disclosed = business_context.get('purpose_disclosed', False)
            if not purpose_disclosed:
                violations.append(ComplianceViolation(
                    violation_id=f"ccpa_purpose_{event_id}",
                    rule_id="ccpa_purpose_disclosure",
                    regulation=ComplianceRegulation.CCPA,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="purpose_not_disclosed",
                    description="Purpose of personal information collection not disclosed",
                    severity=ViolationSeverity.HIGH,
                    detected_at=datetime.utcnow(),
                    business_context=business_context,
                    auto_correctable=True
                ))
        
        # Check consumer rights requests
        if event_type in ['user.data.request', 'user.data.delete']:
            # Must respond within 45 days
            request_date = business_context.get('request_date')
            if request_date:
                days_since_request = (datetime.utcnow() - request_date).days
                if days_since_request > 45:
                    violations.append(ComplianceViolation(
                        violation_id=f"ccpa_response_time_{event_id}",
                        rule_id="ccpa_response_time",
                        regulation=ComplianceRegulation.CCPA,
                        event_id=event_id,
                        user_id=user_id,
                        violation_type="response_time_exceeded",
                        description=f"CCPA consumer rights request exceeded 45-day response time: {days_since_request} days",
                        severity=ViolationSeverity.HIGH,
                        detected_at=datetime.utcnow(),
                        business_context=business_context
                    ))
        
        return violations, warnings
    
    async def _validate_sox(self,
                          event_id: str,
                          event_type: str,
                          event_data: Dict[str, Any],
                          user_id: str,
                          business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate SOX compliance for financial events"""
        
        violations = []
        warnings = []
        
        transaction_amount = business_context.get('transaction_amount', 0)
        
        # High-value transactions require dual authorization
        if transaction_amount > 10000:
            dual_auth = business_context.get('dual_authorization', False)
            if not dual_auth:
                violations.append(ComplianceViolation(
                    violation_id=f"sox_dual_auth_{event_id}",
                    rule_id="sox_dual_authorization",
                    regulation=ComplianceRegulation.SOX,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="missing_dual_authorization",
                    description=f"High-value transaction (${transaction_amount}) missing dual authorization",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
        
        # Financial actions require approval trail
        if event_type.startswith('monetization.') and transaction_amount > 1000:
            approval_trail = business_context.get('approval_trail')
            if not approval_trail:
                violations.append(ComplianceViolation(
                    violation_id=f"sox_approval_{event_id}",
                    rule_id="sox_approval_trail",
                    regulation=ComplianceRegulation.SOX,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="missing_approval_trail",
                    description="Financial transaction missing required approval trail",
                    severity=ViolationSeverity.HIGH,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
        
        # Segregation of duties check
        if event_type in ['monetization.approve', 'monetization.execute']:
            initiator = business_context.get('transaction_initiator')
            approver = business_context.get('transaction_approver')
            if initiator == approver:
                violations.append(ComplianceViolation(
                    violation_id=f"sox_segregation_{event_id}",
                    rule_id="sox_segregation_duties",
                    regulation=ComplianceRegulation.SOX,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="segregation_duties_violation",
                    description="Same person initiated and approved transaction (segregation of duties violation)",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
        
        return violations, warnings
    
    async def _validate_pci_dss(self,
                              event_id: str,
                              event_type: str,
                              event_data: Dict[str, Any],
                              user_id: str,
                              business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate PCI-DSS compliance for payment events"""
        
        violations = []
        warnings = []
        
        payment_method = business_context.get('payment_method', '')
        
        if 'card' in payment_method.lower():
            # Card data must be encrypted
            if not business_context.get('data_encrypted', False):
                violations.append(ComplianceViolation(
                    violation_id=f"pci_encryption_{event_id}",
                    rule_id="pci_data_encryption",
                    regulation=ComplianceRegulation.PCI_DSS,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="unencrypted_card_data",
                    description="Card payment data not encrypted",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
            
            # Must use PCI-compliant processor
            if not business_context.get('pci_compliant_processor', False):
                violations.append(ComplianceViolation(
                    violation_id=f"pci_processor_{event_id}",
                    rule_id="pci_compliant_processor",
                    regulation=ComplianceRegulation.PCI_DSS,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="non_compliant_processor",
                    description="Payment not processed through PCI-compliant processor",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
            
            # Access to card data must be justified
            if event_type == 'payment.view':
                if not business_context.get('access_justification'):
                    warnings.append("PCI-DSS: Access to payment data should include business justification")
        
        return violations, warnings
    
    async def _validate_hipaa(self,
                            event_id: str,
                            event_type: str,
                            event_data: Dict[str, Any],
                            user_id: str,
                            business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate HIPAA compliance for health data"""
        
        violations = []
        warnings = []
        
        if business_context.get('health_data_involved', False):
            # PHI must be encrypted
            if not business_context.get('phi_encrypted', False):
                violations.append(ComplianceViolation(
                    violation_id=f"hipaa_encryption_{event_id}",
                    rule_id="hipaa_phi_encryption",
                    regulation=ComplianceRegulation.HIPAA,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="unencrypted_phi",
                    description="Protected Health Information (PHI) not encrypted",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
            
            # Access must be logged
            if not business_context.get('access_logged', False):
                warnings.append("HIPAA: Access to PHI should be logged for audit trail")
            
            # Minimum necessary rule
            if not business_context.get('minimum_necessary_verified', False):
                warnings.append("HIPAA: Verify minimum necessary rule for PHI access")
        
        return violations, warnings
    
    async def _validate_coppa(self,
                            event_id: str,
                            event_type: str,
                            event_data: Dict[str, Any],
                            user_id: str,
                            business_context: Dict[str, Any]) -> tuple[List[ComplianceViolation], List[str]]:
        """Validate COPPA compliance for users under 13"""
        
        violations = []
        warnings = []
        
        user_age = business_context.get('user_age', 18)
        
        if user_age < 13:
            # Parental consent required
            if not business_context.get('parental_consent', False):
                violations.append(ComplianceViolation(
                    violation_id=f"coppa_consent_{event_id}",
                    rule_id="coppa_parental_consent",
                    regulation=ComplianceRegulation.COPPA,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="missing_parental_consent",
                    description="COPPA parental consent required for users under 13",
                    severity=ViolationSeverity.CRITICAL,
                    detected_at=datetime.utcnow(),
                    business_context=business_context,
                    auto_correctable=True
                ))
            
            # Limited data collection
            if len(event_data) > 5:  # Arbitrary threshold
                warnings.append("COPPA: Consider limiting data collection for users under 13")
            
            # No behavioral advertising
            if business_context.get('advertising_involved', False):
                violations.append(ComplianceViolation(
                    violation_id=f"coppa_advertising_{event_id}",
                    rule_id="coppa_no_advertising",
                    regulation=ComplianceRegulation.COPPA,
                    event_id=event_id,
                    user_id=user_id,
                    violation_type="behavioral_advertising",
                    description="Behavioral advertising prohibited for users under 13",
                    severity=ViolationSeverity.HIGH,
                    detected_at=datetime.utcnow(),
                    business_context=business_context
                ))
        
        return violations, warnings
    
    async def _check_user_consent(self, user_id: str, regulation: ComplianceRegulation) -> bool:
        """Check if user has valid consent for regulation"""
        
        user_consents = self.user_consents.get(user_id, {})
        consent_data = user_consents.get(regulation)
        
        if not consent_data:
            return False
        
        # Check if consent is still valid
        consent_expiry = consent_data.get('expires_at')
        if consent_expiry and datetime.utcnow() > consent_expiry:
            return False
        
        return consent_data.get('granted', False)
    
    async def _attempt_auto_correction(self,
                                     violations: List[ComplianceViolation],
                                     event: Any,
                                     business_context: Dict[str, Any]) -> List[ComplianceViolation]:
        """Attempt to auto-correct violations where possible"""
        
        corrected = []
        
        for violation in violations:
            if violation.auto_correctable:
                success = await self._auto_correct_violation(violation, event, business_context)
                if success:
                    corrected.append(violation)
                    logger.info(f"Auto-corrected violation: {violation.violation_id}")
        
        return corrected
    
    async def _auto_correct_violation(self,
                                    violation: ComplianceViolation,
                                    event: Any,
                                    business_context: Dict[str, Any]) -> bool:
        """Auto-correct a specific violation"""
        
        try:
            if violation.violation_type == "missing_consent":
                # Trigger consent collection workflow
                await self._trigger_consent_collection(violation.user_id, violation.regulation)
                return True
            
            elif violation.violation_type == "purpose_not_disclosed":
                # Add purpose disclosure to business context
                business_context['purpose_disclosed'] = True
                business_context['purpose'] = "Data processing for platform services"
                return True
            
            elif violation.violation_type == "missing_parental_consent":
                # Trigger parental consent workflow
                await self._trigger_parental_consent_collection(violation.user_id)
                return True
            
        except Exception as e:
            logger.error(f"Failed to auto-correct violation {violation.violation_id}: {str(e)}")
        
        return False
    
    async def _trigger_consent_collection(self, user_id: str, regulation: ComplianceRegulation):
        """Trigger consent collection workflow"""
        
        # In a real implementation, this would trigger the consent UI
        logger.info(f"Triggering {regulation.value} consent collection for user {user_id}")
        
        # Simulate consent collection
        if user_id not in self.user_consents:
            self.user_consents[user_id] = {}
        
        self.user_consents[user_id][regulation] = {
            'granted': True,
            'timestamp': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=365),
            'method': 'auto_collection'
        }
    
    async def _trigger_parental_consent_collection(self, user_id: str):
        """Trigger parental consent collection workflow"""
        
        # In a real implementation, this would send email to parent
        logger.info(f"Triggering parental consent collection for user {user_id}")
    
    def _initialize_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Initialize compliance rules database"""
        
        rules = [
            ComplianceRule(
                rule_id="gdpr_consent_required",
                regulation=ComplianceRegulation.GDPR,
                name="GDPR Consent Required",
                description="User consent required for data processing",
                event_types=["user.", "content.processing"],
                required_fields=["user_consent", "lawful_basis"],
                validation_logic="check_consent_valid",
                severity=ViolationSeverity.CRITICAL
            ),
            ComplianceRule(
                rule_id="ccpa_optout_verification",
                regulation=ComplianceRegulation.CCPA,
                name="CCPA Opt-out Verification",
                description="Verify opt-out status before data sale",
                event_types=["data.sale"],
                required_fields=["opt_out_verified"],
                validation_logic="check_optout_status",
                severity=ViolationSeverity.CRITICAL
            ),
            ComplianceRule(
                rule_id="sox_dual_authorization",
                regulation=ComplianceRegulation.SOX,
                name="SOX Dual Authorization",
                description="High-value transactions require dual authorization",
                event_types=["monetization."],
                required_fields=["dual_authorization", "transaction_amount"],
                validation_logic="check_dual_auth",
                severity=ViolationSeverity.CRITICAL
            ),
            ComplianceRule(
                rule_id="pci_data_encryption",
                regulation=ComplianceRegulation.PCI_DSS,
                name="PCI Data Encryption",
                description="Card data must be encrypted",
                event_types=["payment.", "monetization."],
                required_fields=["data_encrypted", "payment_method"],
                validation_logic="check_encryption",
                severity=ViolationSeverity.CRITICAL
            )
        ]
        
        return {rule.rule_id: rule for rule in rules}
    
    def _initialize_retention_policies(self) -> Dict[ComplianceRegulation, timedelta]:
        """Initialize data retention policies"""
        
        return {
            ComplianceRegulation.GDPR: timedelta(days=2555),  # 7 years
            ComplianceRegulation.CCPA: timedelta(days=1095),  # 3 years
            ComplianceRegulation.SOX: timedelta(days=2555),   # 7 years
            ComplianceRegulation.PCI_DSS: timedelta(days=365), # 1 year
            ComplianceRegulation.HIPAA: timedelta(days=2190),  # 6 years
            ComplianceRegulation.COPPA: timedelta(days=365)    # 1 year
        }
    
    def _create_permissive_result(self, event: Any) -> ComplianceValidationResult:
        """Create permissive result when validation is disabled"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        
        return ComplianceValidationResult(
            event_id=event_id,
            compliant=True,
            violations=[],
            warnings=["Compliance validation disabled"],
            regulations_checked=[]
        )
    
    def _create_error_result(self, event: Any, error_message: str) -> ComplianceValidationResult:
        """Create error result when validation fails"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        
        return ComplianceValidationResult(
            event_id=event_id,
            compliant=False,
            violations=[],
            warnings=[f"Compliance validation error: {error_message}"],
            regulations_checked=[]
        )
    
    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get compliance violation statistics"""
        
        if not self.violation_history:
            return {
                'total_violations': 0,
                'by_regulation': {},
                'by_severity': {},
                'recent_violations': 0
            }
        
        # Count by regulation
        by_regulation = {}
        by_severity = {}
        recent_count = 0
        
        recent_threshold = datetime.utcnow() - timedelta(days=7)
        
        for violation in self.violation_history:
            # By regulation
            reg = violation.regulation.value
            by_regulation[reg] = by_regulation.get(reg, 0) + 1
            
            # By severity
            sev = violation.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # Recent violations
            if violation.detected_at > recent_threshold:
                recent_count += 1
        
        return {
            'total_violations': len(self.violation_history),
            'by_regulation': by_regulation,
            'by_severity': by_severity,
            'recent_violations': recent_count
        }
    
    def enable_validation(self):
        """Enable compliance validation"""
        self.enabled = True
        logger.info("Compliance validation enabled")
    
    def disable_validation(self):
        """Disable compliance validation"""
        self.enabled = False
        logger.info("Compliance validation disabled")
    
    def enable_auto_correction(self):
        """Enable auto-correction of violations"""
        self.auto_correction_enabled = True
        logger.info("Auto-correction enabled")
    
    def disable_auto_correction(self):
        """Disable auto-correction of violations"""
        self.auto_correction_enabled = False
        logger.info("Auto-correction disabled")


# Export for module use
__all__ = ['ComplianceValidator', 'ComplianceRegulation', 'ComplianceViolation', 'ComplianceValidationResult', 'ViolationSeverity']