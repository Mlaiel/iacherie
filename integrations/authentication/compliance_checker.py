"""Compliance Checker - Enterprise Compliance Validation System
=============================================================

Advanced compliance checking and configuration validation for Ainflue integrations.
Provides GDPR, SOC2, PCI-DSS, OWASP compliance validation and security auditing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .security_scanner_core import (
    SecurityVulnerability, VulnerabilityType, SecurityRiskLevel, 
    SecurityStandard
)

logger = logging.getLogger(__name__)

@dataclass
class ComplianceRule:
    """Compliance rule definition."""
    rule_id: str
    standard: SecurityStandard
    category: str
    title: str
    description: str
    severity: SecurityRiskLevel
    check_function: str
    remediation: str

class ComplianceChecker:
    """Advanced compliance checking and validation."""
    
    def __init__(self, security_scanner) -> None:
        self.security_scanner = security_scanner
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Load compliance rules for different standards."""
        rules = {}
        
        # GDPR Compliance Rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="GDPR_001",
                standard=SecurityStandard.GDPR,
                category="Data Protection",
                title="Personal Data Encryption",
                description="Personal data must be encrypted in transit and at rest",
                severity=SecurityRiskLevel.HIGH,
                check_function="check_data_encryption",
                remediation="Implement encryption for all personal data storage and transmission"
            ),
            ComplianceRule(
                rule_id="GDPR_002", 
                standard=SecurityStandard.GDPR,
                category="Data Processing",
                title="Data Minimization",
                description="Only necessary personal data should be collected and processed",
                severity=SecurityRiskLevel.MEDIUM,
                check_function="check_data_minimization",
                remediation="Review data collection practices and minimize personal data collection"
            ),
            ComplianceRule(
                rule_id="GDPR_003",
                standard=SecurityStandard.GDPR,
                category="User Rights",
                title="Right to Erasure",
                description="Users must be able to request deletion of their personal data",
                severity=SecurityRiskLevel.HIGH,
                check_function="check_data_deletion",
                remediation="Implement data deletion mechanisms and user control interfaces"
            )
        ]
        
        # SOC2 Compliance Rules
        soc2_rules = [
            ComplianceRule(
                rule_id="SOC2_001",
                standard=SecurityStandard.SOC2,
                category="Security",
                title="Access Controls",
                description="Logical and physical access controls must be implemented",
                severity=SecurityRiskLevel.HIGH,
                check_function="check_access_controls",
                remediation="Implement multi-factor authentication and role-based access controls"
            ),
            ComplianceRule(
                rule_id="SOC2_002",
                standard=SecurityStandard.SOC2,
                category="Monitoring",
                title="Security Monitoring",
                description="Security events and anomalies must be monitored",
                severity=SecurityRiskLevel.MEDIUM,
                check_function="check_security_monitoring",
                remediation="Implement comprehensive security monitoring and alerting"
            ),
            ComplianceRule(
                rule_id="SOC2_003",
                standard=SecurityStandard.SOC2,
                category="Availability",
                title="System Availability",
                description="Systems must be available for operation and use",
                severity=SecurityRiskLevel.MEDIUM,
                check_function="check_system_availability",
                remediation="Implement high availability architecture and disaster recovery"
            )
        ]
        
        # PCI DSS Compliance Rules
        pci_rules = [
            ComplianceRule(
                rule_id="PCI_001",
                standard=SecurityStandard.PCI_DSS,
                category="Network Security",
                title="Firewall Configuration", 
                description="Firewalls must be configured to protect cardholder data",
                severity=SecurityRiskLevel.HIGH,
                check_function="check_firewall_config",
                remediation="Configure and maintain network firewalls"
            ),
            ComplianceRule(
                rule_id="PCI_002",
                standard=SecurityStandard.PCI_DSS,
                category="Data Protection",
                title="Cardholder Data Protection",
                description="Cardholder data must be protected during transmission",
                severity=SecurityRiskLevel.CRITICAL,
                check_function="check_cardholder_protection",
                remediation="Encrypt cardholder data during transmission over public networks"
            )
        ]
        
        # OWASP Top 10 Rules
        owasp_rules = [
            ComplianceRule(
                rule_id="OWASP_001",
                standard=SecurityStandard.OWASP_TOP_10,
                category="Injection",
                title="SQL Injection Prevention",
                description="Applications must be protected against injection attacks",
                severity=SecurityRiskLevel.CRITICAL,
                check_function="check_injection_protection",
                remediation="Use parameterized queries and input validation"
            ),
            ComplianceRule(
                rule_id="OWASP_002",
                standard=SecurityStandard.OWASP_TOP_10,
                category="Authentication",
                title="Broken Authentication",
                description="Authentication mechanisms must be properly implemented",
                severity=SecurityRiskLevel.HIGH,
                check_function="check_authentication_strength",
                remediation="Implement strong authentication with MFA"
            ),
            ComplianceRule(
                rule_id="OWASP_003",
                standard=SecurityStandard.OWASP_TOP_10,
                category="Data Exposure",
                title="Sensitive Data Exposure",
                description="Sensitive data must be properly protected",
                severity=SecurityRiskLevel.HIGH,
                check_function="check_data_exposure",
                remediation="Encrypt sensitive data and use secure protocols"
            )
        ]
        
        # Combine all rules
        all_rules = gdpr_rules + soc2_rules + pci_rules + owasp_rules
        for rule in all_rules:
            rules[rule.rule_id] = rule
            
        return rules

    async def _scan_configuration(self, integration_name: str) -> List[SecurityVulnerability]:
        """Scan integration configuration for compliance violations."""
        vulnerabilities = []
        
        try:
            # Check each compliance rule
            for rule_id, rule in self.compliance_rules.items():
                try:
                    # Get the check function
                    check_function = getattr(self, rule.check_function, None)
                    if check_function:
                        violations = await check_function(integration_name, rule)
                        vulnerabilities.extend(violations)
                    else:
                        logger.warning(f"Check function {rule.check_function} not found")
                        
                except Exception as e:
                    logger.error(f"Error checking compliance rule {rule_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scanning configuration for {integration_name}: {e}")
            
        return vulnerabilities

    async def check_data_encryption(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check data encryption compliance."""
        vulnerabilities = []
        
        # Check if integration supports HTTPS
        profile = self.security_scanner.integration_profiles.get(integration_name)
        if profile and profile.ssl_grade in ['F', 'E', 'D', 'C']:
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"encryption_weak_{integration_name}",
                vulnerability_type=VulnerabilityType.WEAK_ENCRYPTION,
                risk_level=rule.severity,
                title=rule.title,
                description=f"Integration {integration_name} has weak encryption (SSL grade: {profile.ssl_grade})",
                affected_integration=integration_name,
                remediation=rule.remediation,
                compliance_violations=[rule.standard]
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def check_data_minimization(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check data minimization compliance."""
        vulnerabilities = []
        
        # This would check API responses for excessive personal data
        # For now, create a placeholder vulnerability
        vulnerability = SecurityVulnerability(
            vulnerability_id=f"data_minimization_{integration_name}",
            vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
            risk_level=rule.severity,
            title=rule.title,
            description=f"Data minimization review required for {integration_name}",
            affected_integration=integration_name,
            remediation=rule.remediation,
            compliance_violations=[rule.standard]
        )
        vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    async def check_data_deletion(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check data deletion capabilities."""
        vulnerabilities = []
        
        # Check if integration has deletion endpoints
        # This would require examining API documentation
        vulnerability = SecurityVulnerability(
            vulnerability_id=f"data_deletion_{integration_name}",
            vulnerability_type=VulnerabilityType.CONFIGURATION_WEAKNESS,
            risk_level=rule.severity,
            title=rule.title,
            description=f"Data deletion mechanism verification required for {integration_name}",
            affected_integration=integration_name,
            remediation=rule.remediation,
            compliance_violations=[rule.standard]
        )
        vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    async def check_access_controls(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check access control implementation."""
        vulnerabilities = []
        
        profile = self.security_scanner.integration_profiles.get(integration_name)
        if profile and profile.authentication_strength in ['weak', 'unknown']:
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"access_control_{integration_name}",
                vulnerability_type=VulnerabilityType.WEAK_AUTHENTICATION,
                risk_level=rule.severity,
                title=rule.title,
                description=f"Weak access controls detected for {integration_name}",
                affected_integration=integration_name,
                remediation=rule.remediation,
                compliance_violations=[rule.standard]
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def check_security_monitoring(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check security monitoring implementation."""
        vulnerabilities = []
        
        # Check if integration has monitoring configured
        vulnerability = SecurityVulnerability(
            vulnerability_id=f"monitoring_{integration_name}",
            vulnerability_type=VulnerabilityType.CONFIGURATION_WEAKNESS,
            risk_level=rule.severity,
            title=rule.title,
            description=f"Security monitoring verification required for {integration_name}",
            affected_integration=integration_name,
            remediation=rule.remediation,
            compliance_violations=[rule.standard]
        )
        vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    async def check_system_availability(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check system availability requirements."""
        vulnerabilities = []
        
        # This would check uptime and availability metrics
        vulnerability = SecurityVulnerability(
            vulnerability_id=f"availability_{integration_name}",
            vulnerability_type=VulnerabilityType.CONFIGURATION_WEAKNESS,
            risk_level=rule.severity,
            title=rule.title,
            description=f"System availability verification required for {integration_name}",
            affected_integration=integration_name,
            remediation=rule.remediation,
            compliance_violations=[rule.standard]
        )
        vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    async def check_firewall_config(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check firewall configuration."""
        vulnerabilities = []
        
        # This would check network security configuration
        vulnerability = SecurityVulnerability(
            vulnerability_id=f"firewall_{integration_name}",
            vulnerability_type=VulnerabilityType.CONFIGURATION_WEAKNESS,
            risk_level=rule.severity,
            title=rule.title,
            description=f"Firewall configuration verification required for {integration_name}",
            affected_integration=integration_name,
            remediation=rule.remediation,
            compliance_violations=[rule.standard]
        )
        vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    async def check_cardholder_protection(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check cardholder data protection."""
        vulnerabilities = []
        
        # Check for payment data protection
        vulnerability = SecurityVulnerability(
            vulnerability_id=f"cardholder_protection_{integration_name}",
            vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
            risk_level=rule.severity,
            title=rule.title,
            description=f"Cardholder data protection verification required for {integration_name}",
            affected_integration=integration_name,
            remediation=rule.remediation,
            compliance_violations=[rule.standard]
        )
        vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    async def check_injection_protection(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check injection attack protection."""
        vulnerabilities = []
        
        # This would test for SQL injection, XSS, etc.
        # For now, check if there are existing injection vulnerabilities
        existing_injection_vulns = [
            v for v in self.security_scanner.vulnerabilities.values()
            if v.affected_integration == integration_name and 
            v.vulnerability_type == VulnerabilityType.INJECTION_VULNERABILITY
        ]
        
        if existing_injection_vulns:
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"injection_protection_{integration_name}",
                vulnerability_type=VulnerabilityType.INJECTION_VULNERABILITY,
                risk_level=rule.severity,
                title=rule.title,
                description=f"Injection vulnerabilities found in {integration_name}",
                affected_integration=integration_name,
                remediation=rule.remediation,
                compliance_violations=[rule.standard]
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def check_authentication_strength(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check authentication strength."""
        vulnerabilities = []
        
        profile = self.security_scanner.integration_profiles.get(integration_name)
        if profile and profile.authentication_strength in ['weak', 'unknown']:
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"auth_strength_{integration_name}",
                vulnerability_type=VulnerabilityType.WEAK_AUTHENTICATION,
                risk_level=rule.severity,
                title=rule.title,
                description=f"Weak authentication mechanisms in {integration_name}",
                affected_integration=integration_name,
                remediation=rule.remediation,
                compliance_violations=[rule.standard]
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def check_data_exposure(self, integration_name: str, rule: ComplianceRule) -> List[SecurityVulnerability]:
        """Check for sensitive data exposure."""
        vulnerabilities = []
        
        # Check if there are existing data exposure vulnerabilities
        existing_exposure_vulns = [
            v for v in self.security_scanner.vulnerabilities.values()
            if v.affected_integration == integration_name and 
            v.vulnerability_type == VulnerabilityType.DATA_EXPOSURE
        ]
        
        if existing_exposure_vulns:
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"data_exposure_{integration_name}",
                vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
                risk_level=rule.severity,
                title=rule.title,
                description=f"Sensitive data exposure found in {integration_name}",
                affected_integration=integration_name,
                remediation=rule.remediation,
                compliance_violations=[rule.standard]
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def generate_compliance_report(
        self, 
        integration_name: Optional[str] = None,
        standards: Optional[List[SecurityStandard]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        
        # Filter vulnerabilities
        vulnerabilities = list(self.security_scanner.vulnerabilities.values())
        
        if integration_name:
            vulnerabilities = [v for v in vulnerabilities 
                             if v.affected_integration == integration_name]
        
        if standards:
            vulnerabilities = [v for v in vulnerabilities 
                             if any(std in v.compliance_violations for std in standards)]
        
        # Generate compliance summary
        compliance_summary = {}
        for standard in SecurityStandard:
            if standards and standard not in standards:
                continue
                
            standard_vulns = [v for v in vulnerabilities 
                            if standard in v.compliance_violations]
            
            compliance_summary[standard.value] = {
                'total_violations': len(standard_vulns),
                'critical': len([v for v in standard_vulns 
                               if v.risk_level == SecurityRiskLevel.CRITICAL]),
                'high': len([v for v in standard_vulns 
                           if v.risk_level == SecurityRiskLevel.HIGH]),
                'medium': len([v for v in standard_vulns 
                             if v.risk_level == SecurityRiskLevel.MEDIUM]),
                'low': len([v for v in standard_vulns 
                          if v.risk_level == SecurityRiskLevel.LOW]),
                'compliance_score': max(0, 100 - (len(standard_vulns) * 10))
            }
        
        # Generate detailed report
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'scope': {
                'integration': integration_name,
                'standards': [s.value for s in standards] if standards else 'all'
            },
            'compliance_summary': compliance_summary,
            'total_violations': len(vulnerabilities),
            'violations_by_standard': {},
            'remediation_priority': [],
            'detailed_violations': []
        }
        
        # Group violations by standard
        for standard in SecurityStandard:
            if standards and standard not in standards:
                continue
                
            standard_vulns = [v for v in vulnerabilities 
                            if standard in v.compliance_violations]
            report['violations_by_standard'][standard.value] = len(standard_vulns)
        
        # Create remediation priority list
        critical_vulns = [v for v in vulnerabilities 
                         if v.risk_level == SecurityRiskLevel.CRITICAL]
        high_vulns = [v for v in vulnerabilities 
                     if v.risk_level == SecurityRiskLevel.HIGH]
        
        report['remediation_priority'] = [
            {
                'vulnerability_id': v.vulnerability_id,
                'title': v.title,
                'risk_level': v.risk_level.value,
                'standards': [s.value for s in v.compliance_violations],
                'remediation': v.remediation
            }
            for v in sorted(critical_vulns + high_vulns, 
                          key=lambda x: (x.risk_level.value, x.title))
        ]
        
        # Add detailed violations
        report['detailed_violations'] = [
            {
                'vulnerability_id': v.vulnerability_id,
                'title': v.title,
                'description': v.description,
                'risk_level': v.risk_level.value,
                'type': v.vulnerability_type.value,
                'affected_endpoint': v.affected_endpoint,
                'affected_integration': v.affected_integration,
                'compliance_violations': [s.value for s in v.compliance_violations],
                'remediation': v.remediation,
                'discovered_at': v.discovered_at.isoformat()
            }
            for v in vulnerabilities
        ]
        
        return report

    async def validate_compliance_framework(
        self, 
        integration_name: str, 
        framework: SecurityStandard
    ) -> Dict[str, Any]:
        """Validate compliance against specific framework."""
        
        # Get framework-specific rules
        framework_rules = {
            rule_id: rule for rule_id, rule in self.compliance_rules.items()
            if rule.standard == framework
        }
        
        validation_results = {
            'framework': framework.value,
            'integration': integration_name,
            'validated_at': datetime.utcnow().isoformat(),
            'total_rules': len(framework_rules),
            'passed_rules': 0,
            'failed_rules': 0,
            'rule_results': {},
            'compliance_score': 0.0,
            'recommendations': []
        }
        
        # Check each rule
        for rule_id, rule in framework_rules.items():
            try:
                check_function = getattr(self, rule.check_function, None)
                if check_function:
                    violations = await check_function(integration_name, rule)
                    
                    rule_result = {
                        'rule_id': rule_id,
                        'title': rule.title,
                        'category': rule.category,
                        'passed': len(violations) == 0,
                        'violations': len(violations),
                        'severity': rule.severity.value,
                        'description': rule.description,
                        'remediation': rule.remediation
                    }
                    
                    validation_results['rule_results'][rule_id] = rule_result
                    
                    if len(violations) == 0:
                        validation_results['passed_rules'] += 1
                    else:
                        validation_results['failed_rules'] += 1
                        validation_results['recommendations'].append({
                            'rule': rule.title,
                            'priority': rule.severity.value,
                            'recommendation': rule.remediation
                        })
                        
            except Exception as e:
                logger.error(f"Error validating rule {rule_id}: {e}")
                
        # Calculate compliance score
        if validation_results['total_rules'] > 0:
            validation_results['compliance_score'] = (
                validation_results['passed_rules'] / validation_results['total_rules']
            ) * 100
            
        return validation_results


# Export main classes
__all__ = [
    "ComplianceChecker",
    "ComplianceRule"
]