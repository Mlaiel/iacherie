"""Data Security Validator - Comprehensive Data Security
======================================================

Enterprise data security validation with encryption verification,
access control validation, and security compliance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

import redis.asyncio as redis


class SecurityLevel(Enum):
    """Data security levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class SecurityViolationType(Enum):
    """Types of security violations."""
    ENCRYPTION_MISSING = "encryption_missing"
    WEAK_ENCRYPTION = "weak_encryption"
    ACCESS_VIOLATION = "access_violation"
    DATA_EXPOSURE = "data_exposure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class SecurityPolicy:
    """Data security policy definition."""
    id: str
    name: str
    description: str
    security_level: SecurityLevel
    encryption_required: bool
    access_controls: List[str]
    data_classification_rules: List[str]
    compliance_requirements: List[str]
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityViolation:
    """Security violation record."""
    id: str
    violation_type: SecurityViolationType
    severity: str  # low, medium, high, critical
    description: str
    asset_id: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    remediation_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataSecurityValidator:
    """Comprehensive data security validation and monitoring system."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Redis setup
        self.redis_url = redis_url
        self.redis_client = None
        
        # Security state
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.violations: Dict[str, SecurityViolation] = {}
        
        # Security validators
        self.encryption_validators: List[callable] = []
        self.access_validators: List[callable] = []
        self.data_classifiers: List[callable] = []
        
        # Performance tracking
        self.security_metrics = {
            'total_validations': 0,
            'violations_detected': 0,
            'violations_resolved': 0,
            'security_score': 100.0
        }
        
        # Setup components
        self._setup_default_policies()
        self._setup_validators()
    
    async def initialize(self):
        """Initialize the security validator."""
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        self.logger.info("Data security validator initialized")
    
    def _setup_default_policies(self):
        """Setup default security policies."""
        # PII protection policy
        pii_policy = SecurityPolicy(
            id="pii_protection",
            name="PII Protection Policy",
            description="Protects personally identifiable information",
            security_level=SecurityLevel.CONFIDENTIAL,
            encryption_required=True,
            access_controls=["role_based", "audit_logging"],
            data_classification_rules=["contains_email", "contains_phone", "contains_ssn"],
            compliance_requirements=["GDPR", "CCPA"]
        )
        
        # Financial data policy
        financial_policy = SecurityPolicy(
            id="financial_protection",
            name="Financial Data Protection",
            description="Protects financial and payment information",
            security_level=SecurityLevel.RESTRICTED,
            encryption_required=True,
            access_controls=["multi_factor_auth", "role_based", "audit_logging"],
            data_classification_rules=["contains_credit_card", "contains_bank_account"],
            compliance_requirements=["PCI_DSS", "SOX"]
        )
        
        # Register policies
        self.security_policies["pii_protection"] = pii_policy
        self.security_policies["financial_protection"] = financial_policy
    
    def _setup_validators(self):
        """Setup security validation functions."""
        self.encryption_validators = [
            self._validate_encryption_at_rest,
            self._validate_encryption_in_transit,
            self._validate_key_management
        ]
        
        self.access_validators = [
            self._validate_access_controls,
            self._validate_authentication,
            self._validate_authorization
        ]
        
        self.data_classifiers = [
            self._classify_pii_data,
            self._classify_financial_data,
            self._classify_sensitive_data
        ]
    
    async def validate_data_security(self, asset_id: str, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data security for an asset."""
        self.security_metrics['total_validations'] += 1
        
        validation_result = {
            'asset_id': asset_id,
            'timestamp': datetime.utcnow().isoformat(),
            'security_score': 100.0,
            'violations': [],
            'recommendations': [],
            'compliance_status': {}
        }
        
        # Classify data sensitivity
        classification = await self._classify_data_sensitivity(data_sample)
        
        # Apply relevant security policies
        applicable_policies = await self._get_applicable_policies(classification)
        
        violations = []
        for policy in applicable_policies:
            policy_violations = await self._validate_against_policy(asset_id, data_sample, policy)
            violations.extend(policy_violations)
        
        # Calculate security score
        if violations:
            critical_violations = len([v for v in violations if v.severity == "critical"])
            high_violations = len([v for v in violations if v.severity == "high"])
            medium_violations = len([v for v in violations if v.severity == "medium"])
            
            # Deduct points based on severity
            score_deduction = (critical_violations * 30 + high_violations * 20 + 
                             medium_violations * 10)
            validation_result['security_score'] = max(0, 100 - score_deduction)
        
        validation_result['violations'] = [
            {
                'id': v.id,
                'type': v.violation_type.value,
                'severity': v.severity,
                'description': v.description
            }
            for v in violations
        ]
        
        # Store violations
        for violation in violations:
            self.violations[violation.id] = violation
            self.security_metrics['violations_detected'] += 1
        
        # Generate recommendations
        validation_result['recommendations'] = await self._generate_security_recommendations(violations)
        
        return validation_result
    
    async def _classify_data_sensitivity(self, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """Classify data sensitivity level."""
        classification = {
            'level': SecurityLevel.PUBLIC,
            'contains_pii': False,
            'contains_financial': False,
            'contains_sensitive': False,
            'detected_patterns': []
        }
        
        for classifier in self.data_classifiers:
            result = await classifier(data_sample)
            if result['is_sensitive']:
                classification['detected_patterns'].extend(result.get('patterns', []))
                
                if result['type'] == 'pii':
                    classification['contains_pii'] = True
                elif result['type'] == 'financial':
                    classification['contains_financial'] = True
                else:
                    classification['contains_sensitive'] = True
        
        # Determine overall security level
        if classification['contains_financial']:
            classification['level'] = SecurityLevel.RESTRICTED
        elif classification['contains_pii']:
            classification['level'] = SecurityLevel.CONFIDENTIAL
        elif classification['contains_sensitive']:
            classification['level'] = SecurityLevel.INTERNAL
        
        return classification
    
    async def _get_applicable_policies(self, classification: Dict[str, Any]) -> List[SecurityPolicy]:
        """Get applicable security policies for data classification."""
        applicable = []
        
        for policy in self.security_policies.values():
            if not policy.enabled:
                continue
            
            # Check if policy applies to this classification
            if classification['contains_pii'] and 'pii' in policy.id:
                applicable.append(policy)
            elif classification['contains_financial'] and 'financial' in policy.id:
                applicable.append(policy)
            elif classification['level'].value in policy.metadata.get('applicable_levels', []):
                applicable.append(policy)
        
        return applicable
    
    async def _validate_against_policy(
        self, 
        asset_id: str, 
        data_sample: Dict[str, Any], 
        policy: SecurityPolicy
    ) -> List[SecurityViolation]:
        """Validate data against a security policy."""
        violations = []
        
        # Check encryption requirements
        if policy.encryption_required:
            encryption_violation = await self._check_encryption_compliance(asset_id, data_sample)
            if encryption_violation:
                violations.append(encryption_violation)
        
        # Check access controls
        for control in policy.access_controls:
            access_violation = await self._check_access_control(asset_id, control)
            if access_violation:
                violations.append(access_violation)
        
        # Check data classification rules
        for rule in policy.data_classification_rules:
            classification_violation = await self._check_classification_rule(asset_id, data_sample, rule)
            if classification_violation:
                violations.append(classification_violation)
        
        return violations
    
    async def _check_encryption_compliance(self, asset_id: str, data_sample: Dict[str, Any]) -> Optional[SecurityViolation]:
        """Check encryption compliance."""
        # Simulate encryption check
        is_encrypted = data_sample.get('_metadata', {}).get('encrypted', False)
        
        if not is_encrypted:
            return SecurityViolation(
                id=str(uuid.uuid4()),
                violation_type=SecurityViolationType.ENCRYPTION_MISSING,
                severity="high",
                description="Data is not encrypted as required by security policy",
                asset_id=asset_id,
                remediation_actions=[
                    "Enable encryption at rest",
                    "Implement field-level encryption for sensitive data",
                    "Review encryption key management"
                ]
            )
        
        return None
    
    async def _check_access_control(self, asset_id: str, control_type: str) -> Optional[SecurityViolation]:
        """Check access control implementation."""
        # Simulate access control check
        # In real implementation, this would verify actual access controls
        
        if control_type == "multi_factor_auth":
            # Check if MFA is enabled
            mfa_enabled = self.config.get('mfa_enabled', False)
            if not mfa_enabled:
                return SecurityViolation(
                    id=str(uuid.uuid4()),
                    violation_type=SecurityViolationType.ACCESS_VIOLATION,
                    severity="high",
                    description="Multi-factor authentication is required but not enabled",
                    asset_id=asset_id,
                    remediation_actions=[
                        "Enable multi-factor authentication",
                        "Configure MFA for all privileged accounts"
                    ]
                )
        
        return None
    
    async def _check_classification_rule(
        self, 
        asset_id: str, 
        data_sample: Dict[str, Any], 
        rule: str
    ) -> Optional[SecurityViolation]:
        """Check data classification rule compliance."""
        if rule == "contains_email":
            # Check if email fields are properly protected
            for key, value in data_sample.items():
                if isinstance(value, str) and '@' in value:
                    # Email detected - check if it's masked/encrypted
                    if not value.startswith('***'):  # Simple masking check
                        return SecurityViolation(
                            id=str(uuid.uuid4()),
                            violation_type=SecurityViolationType.DATA_EXPOSURE,
                            severity="medium",
                            description=f"Email address exposed in field '{key}'",
                            asset_id=asset_id,
                            remediation_actions=[
                                "Mask or encrypt email addresses",
                                "Implement data anonymization"
                            ]
                        )
        
        return None
    
    async def _generate_security_recommendations(self, violations: List[SecurityViolation]) -> List[str]:
        """Generate security improvement recommendations."""
        recommendations = []
        
        violation_types = [v.violation_type for v in violations]
        
        if SecurityViolationType.ENCRYPTION_MISSING in violation_types:
            recommendations.append("Implement end-to-end encryption for sensitive data")
        
        if SecurityViolationType.ACCESS_VIOLATION in violation_types:
            recommendations.append("Strengthen access controls and implement least privilege principles")
        
        if SecurityViolationType.DATA_EXPOSURE in violation_types:
            recommendations.append("Implement data masking and anonymization for sensitive fields")
        
        if len(violations) > 3:
            recommendations.append("Conduct comprehensive security audit and implement security framework")
        
        return recommendations
    
    # Data classification functions
    async def _classify_pii_data(self, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """Classify PII data patterns."""
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        detected_patterns = []
        
        for field, value in data_sample.items():
            if isinstance(value, str):
                for pattern_name, pattern in pii_patterns.items():
                    if re.search(pattern, value):
                        detected_patterns.append(f"{pattern_name}_in_{field}")
        
        return {
            'is_sensitive': bool(detected_patterns),
            'type': 'pii',
            'patterns': detected_patterns
        }
    
    async def _classify_financial_data(self, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """Classify financial data patterns."""
        financial_patterns = {
            'credit_card': r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
            'bank_account': r'\b\d{8,12}\b'
        }
        
        detected_patterns = []
        
        for field, value in data_sample.items():
            if isinstance(value, str):
                for pattern_name, pattern in financial_patterns.items():
                    if re.search(pattern, value):
                        detected_patterns.append(f"{pattern_name}_in_{field}")
        
        # Check field names for financial indicators
        financial_fields = ['salary', 'income', 'revenue', 'payment', 'amount', 'price']
        for field in data_sample.keys():
            if any(fin_field in field.lower() for fin_field in financial_fields):
                detected_patterns.append(f"financial_field_{field}")
        
        return {
            'is_sensitive': bool(detected_patterns),
            'type': 'financial',
            'patterns': detected_patterns
        }
    
    async def _classify_sensitive_data(self, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """Classify other sensitive data patterns."""
        sensitive_indicators = ['password', 'secret', 'token', 'key', 'private']
        detected_patterns = []
        
        for field in data_sample.keys():
            if any(indicator in field.lower() for indicator in sensitive_indicators):
                detected_patterns.append(f"sensitive_field_{field}")
        
        return {
            'is_sensitive': bool(detected_patterns),
            'type': 'sensitive',
            'patterns': detected_patterns
        }
    
    # Encryption validation functions
    async def _validate_encryption_at_rest(self, data_sample: Dict[str, Any]) -> bool:
        """Validate encryption at rest."""
        # Check if data has encryption metadata
        metadata = data_sample.get('_metadata', {})
        return metadata.get('encrypted_at_rest', False)
    
    async def _validate_encryption_in_transit(self, data_sample: Dict[str, Any]) -> bool:
        """Validate encryption in transit."""
        # Check if data transfer uses encryption
        metadata = data_sample.get('_metadata', {})
        return metadata.get('encrypted_in_transit', False)
    
    async def _validate_key_management(self, data_sample: Dict[str, Any]) -> bool:
        """Validate encryption key management."""
        # Check if proper key management is in place
        metadata = data_sample.get('_metadata', {})
        return metadata.get('key_management_compliant', False)
    
    # Access control validation functions
    async def _validate_access_controls(self, asset_id: str) -> bool:
        """Validate access control implementation."""
        # Check if proper access controls are in place
        return self.config.get('access_controls_enabled', False)
    
    async def _validate_authentication(self, asset_id: str) -> bool:
        """Validate authentication mechanisms."""
        return self.config.get('strong_authentication', False)
    
    async def _validate_authorization(self, asset_id: str) -> bool:
        """Validate authorization policies."""
        return self.config.get('authorization_policies', False)
    
    async def resolve_violation(self, violation_id: str, resolution_notes: str = "") -> bool:
        """Resolve a security violation."""
        if violation_id not in self.violations:
            return False
        
        violation = self.violations[violation_id]
        violation.resolved = True
        violation.metadata['resolved_at'] = datetime.utcnow().isoformat()
        violation.metadata['resolution_notes'] = resolution_notes
        
        self.security_metrics['violations_resolved'] += 1
        
        # Update overall security score
        total_violations = self.security_metrics['violations_detected']
        resolved_violations = self.security_metrics['violations_resolved']
        if total_violations > 0:
            resolution_rate = resolved_violations / total_violations
            self.security_metrics['security_score'] = 70 + (resolution_rate * 30)  # Base 70% + resolution bonus
        
        self.logger.info(f"Security violation resolved: {violation_id}")
        return True
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security validation metrics."""
        active_violations = len([v for v in self.violations.values() if not v.resolved])
        
        return {
            **self.security_metrics,
            'active_violations': active_violations,
            'security_policies': len(self.security_policies),
            'violation_types': {
                vtype.value: len([v for v in self.violations.values() if v.violation_type == vtype])
                for vtype in SecurityViolationType
            }
        }


# Example usage
if __name__ == "__main__":
    async def main():
        validator = DataSecurityValidator(
            redis_url="redis://localhost:6379",
            config={
                'mfa_enabled': False,
                'access_controls_enabled': True,
                'strong_authentication': True
            }
        )
        
        await validator.initialize()
        
        # Sample data with potential security issues
        test_data = {
            'user_id': '12345',
            'email': 'john.doe@example.com',
            'phone': '123-456-7890',
            'credit_card': '4532-1234-5678-9012',
            'salary': 75000,
            '_metadata': {
                'encrypted': False,
                'encrypted_at_rest': False
            }
        }
        
        # Validate security
        result = await validator.validate_data_security('user_table_1', test_data)
        
        print(f"Security validation result:")
        print(f"Security score: {result['security_score']}")
        print(f"Violations: {len(result['violations'])}")
        
        for violation in result['violations']:
            print(f"- {violation['severity']}: {violation['description']}")
        
        print(f"Recommendations:")
        for rec in result['recommendations']:
            print(f"- {rec}")
        
        # Get security metrics
        metrics = validator.get_security_metrics()
        print(f"\nSecurity metrics: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(main())