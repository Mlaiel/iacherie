"""
Compliance Monitoring module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade Compliance Monitoring for Multi-Cloud Infrastructure
# GDPR, SOC2, ISO27001, HIPAA, PCI-DSS compliance automation
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.security import SecurityCenter
from google.cloud import asset_v1
from google.cloud import logging as gcp_logging
import yaml
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    FedRAMP = "fedramp"
    CCPA = "ccpa"

class ComplianceStatus(Enum):
    """Compliance check status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    UNKNOWN = "unknown"
    REMEDIATION_REQUIRED = "remediation_required"

@dataclass
class ComplianceRule:
    """Compliance rule definition."""
    id: str
    name: str
    description: str
    framework: ComplianceFramework
    severity: str  # critical, high, medium, low
    category: str
    remediation: str
    automated_check: bool = True
    tags: List[str] = field(default_factory=list)

@dataclass
class ComplianceViolation:
    """Compliance violation details."""
    rule_id: str
    resource_id: str
    resource_type: str
    provider: str
    status: ComplianceStatus
    message: str
    detected_at: datetime
    remediation_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceReport:
    """Compliance assessment report."""
    framework: ComplianceFramework
    assessment_date: datetime
    total_rules: int
    compliant_rules: int
    violations: List[ComplianceViolation]
    score: float
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ComplianceMonitor:
    """
    Enterprise-grade compliance monitoring system for multi-cloud infrastructure.
    
    Supports major compliance frameworks and provides automated checks,
    violation detection, and remediation guidance.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize compliance monitor."""
        self.config = config
        self.enabled_frameworks = set(config.get('enabled_frameworks', []))
        self.rules = {}
        self.violations = []
        self.reports = {}
        
        # Cloud clients
        self.aws_clients = {}
        self.azure_credentials = None
        self.gcp_clients = {}
        
        self._initialize_cloud_clients()
        self._load_compliance_rules()
    
    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients."""
        try:
            # AWS clients
            if self.config.get('aws', {}).get('enabled', False):
                session = boto3.Session(
                    aws_access_key_id=self.config['aws'].get('access_key'),
                    aws_secret_access_key=self.config['aws'].get('secret_key'),
                    region_name=self.config['aws'].get('region', 'us-east-1')
                )
                
                self.aws_clients = {
                    'config': session.client('config'),
                    'iam': session.client('iam'),
                    'ec2': session.client('ec2'),
                    'cloudtrail': session.client('cloudtrail'),
                    'security_hub': session.client('securityhub'),
                    'kms': session.client('kms'),
                    'guardduty': session.client('guardduty')
                }
            
            # Azure credentials
            if self.config.get('azure', {}).get('enabled', False):
                self.azure_credentials = DefaultAzureCredential()
                
            # GCP clients
            if self.config.get('gcp', {}).get('enabled', False):
                self.gcp_clients = {
                    'asset': asset_v1.AssetServiceClient(),
                    'logging': gcp_logging.Client()
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud clients: {e}")
    
    def _load_compliance_rules(self) -> None:
        """Load compliance rules for enabled frameworks."""
        try:
            # GDPR Rules
            if ComplianceFramework.GDPR in self.enabled_frameworks:
                self.rules.update(self._get_gdpr_rules())
            
            # SOC2 Rules
            if ComplianceFramework.SOC2 in self.enabled_frameworks:
                self.rules.update(self._get_soc2_rules())
            
            # ISO27001 Rules
            if ComplianceFramework.ISO27001 in self.enabled_frameworks:
                self.rules.update(self._get_iso27001_rules())
            
            # HIPAA Rules
            if ComplianceFramework.HIPAA in self.enabled_frameworks:
                self.rules.update(self._get_hipaa_rules())
            
            # PCI-DSS Rules
            if ComplianceFramework.PCI_DSS in self.enabled_frameworks:
                self.rules.update(self._get_pci_dss_rules())
            
            logger.info(f"Loaded {len(self.rules)} compliance rules")
            
        except Exception as e:
            logger.error(f"Failed to load compliance rules: {e}")
    
    def _get_gdpr_rules(self) -> Dict[str, ComplianceRule]:
        """Get GDPR compliance rules."""
        return {
            "gdpr_data_encryption": ComplianceRule(
                id="gdpr_data_encryption",
                name="Data Encryption at Rest and Transit",
                description="All personal data must be encrypted at rest and in transit",
                framework=ComplianceFramework.GDPR,
                severity="critical",
                category="data_protection",
                remediation="Enable encryption for all storage services and enforce HTTPS/TLS",
                tags=["encryption", "data_protection"]
            ),
            "gdpr_access_logging": ComplianceRule(
                id="gdpr_access_logging",
                name="Personal Data Access Logging",
                description="All access to personal data must be logged and monitored",
                framework=ComplianceFramework.GDPR,
                severity="high",
                category="access_control",
                remediation="Enable comprehensive access logging and monitoring",
                tags=["logging", "access_control"]
            ),
            "gdpr_data_retention": ComplianceRule(
                id="gdpr_data_retention",
                name="Data Retention Policies",
                description="Personal data retention policies must be implemented",
                framework=ComplianceFramework.GDPR,
                severity="high",
                category="data_lifecycle",
                remediation="Implement automated data retention and deletion policies",
                tags=["retention", "data_lifecycle"]
            )
        }
    
    def _get_soc2_rules(self) -> Dict[str, ComplianceRule]:
        """Get SOC2 compliance rules."""
        return {
            "soc2_security_controls": ComplianceRule(
                id="soc2_security_controls",
                name="Security Controls Implementation",
                description="Comprehensive security controls must be implemented",
                framework=ComplianceFramework.SOC2,
                severity="critical",
                category="security",
                remediation="Implement multi-factor authentication, encryption, and access controls",
                tags=["security", "controls"]
            ),
            "soc2_availability": ComplianceRule(
                id="soc2_availability",
                name="System Availability",
                description="Systems must maintain 99.9% availability",
                framework=ComplianceFramework.SOC2,
                severity="high",
                category="availability",
                remediation="Implement redundancy, monitoring, and disaster recovery",
                tags=["availability", "monitoring"]
            ),
            "soc2_confidentiality": ComplianceRule(
                id="soc2_confidentiality",
                name="Data Confidentiality",
                description="Confidential data must be protected from unauthorized access",
                framework=ComplianceFramework.SOC2,
                severity="critical",
                category="confidentiality",
                remediation="Implement encryption, access controls, and data classification",
                tags=["confidentiality", "encryption"]
            )
        }
    
    def _get_iso27001_rules(self) -> Dict[str, ComplianceRule]:
        """Get ISO27001 compliance rules."""
        return {
            "iso27001_isms": ComplianceRule(
                id="iso27001_isms",
                name="Information Security Management System",
                description="ISMS must be implemented and maintained",
                framework=ComplianceFramework.ISO27001,
                severity="critical",
                category="management",
                remediation="Implement comprehensive ISMS with policies and procedures",
                tags=["isms", "management"]
            ),
            "iso27001_risk_assessment": ComplianceRule(
                id="iso27001_risk_assessment",
                name="Risk Assessment Process",
                description="Regular risk assessments must be conducted",
                framework=ComplianceFramework.ISO27001,
                severity="high",
                category="risk_management",
                remediation="Implement automated risk assessment and management",
                tags=["risk", "assessment"]
            )
        }
    
    def _get_hipaa_rules(self) -> Dict[str, ComplianceRule]:
        """Get HIPAA compliance rules."""
        return {
            "hipaa_phi_encryption": ComplianceRule(
                id="hipaa_phi_encryption",
                name="PHI Encryption Requirements",
                description="Protected Health Information must be encrypted",
                framework=ComplianceFramework.HIPAA,
                severity="critical",
                category="data_protection",
                remediation="Enable encryption for all PHI storage and transmission",
                tags=["phi", "encryption"]
            ),
            "hipaa_access_controls": ComplianceRule(
                id="hipaa_access_controls",
                name="PHI Access Controls",
                description="Access to PHI must be strictly controlled and monitored",
                framework=ComplianceFramework.HIPAA,
                severity="critical",
                category="access_control",
                remediation="Implement role-based access controls and audit trails",
                tags=["access_control", "audit"]
            )
        }
    
    def _get_pci_dss_rules(self) -> Dict[str, ComplianceRule]:
        """Get PCI-DSS compliance rules."""
        return {
            "pci_dss_encryption": ComplianceRule(
                id="pci_dss_encryption",
                name="Cardholder Data Encryption",
                description="Cardholder data must be encrypted at rest and in transit",
                framework=ComplianceFramework.PCI_DSS,
                severity="critical",
                category="data_protection",
                remediation="Implement strong encryption for all cardholder data",
                tags=["encryption", "cardholder_data"]
            ),
            "pci_dss_network_security": ComplianceRule(
                id="pci_dss_network_security",
                name="Network Security Controls",
                description="Network security controls must be implemented",
                framework=ComplianceFramework.PCI_DSS,
                severity="critical",
                category="network_security",
                remediation="Implement firewalls, network segmentation, and monitoring",
                tags=["network", "security"]
            )
        }
    
    async def run_compliance_assessment(self, 
                                      framework: ComplianceFramework) -> ComplianceReport:
        """Run compliance assessment for specified framework."""
        try:
            logger.info(f"Starting compliance assessment for {framework.value}")
            
            violations = []
            framework_rules = {
                rule_id: rule for rule_id, rule in self.rules.items()
                if rule.framework == framework
            }
            
            # Run checks for each rule
            for rule_id, rule in framework_rules.items():
                if rule.automated_check:
                    rule_violations = await self._check_rule_compliance(rule)
                    violations.extend(rule_violations)
            
            # Calculate compliance score
            total_rules = len(framework_rules)
            compliant_rules = total_rules - len(violations)
            score = (compliant_rules / total_rules * 100) if total_rules > 0 else 0
            
            # Generate recommendations
            recommendations = self._generate_recommendations(violations)
            
            report = ComplianceReport(
                framework=framework,
                assessment_date=datetime.utcnow(),
                total_rules=total_rules,
                compliant_rules=compliant_rules,
                violations=violations,
                score=score,
                recommendations=recommendations
            )
            
            self.reports[framework.value] = report
            logger.info(f"Compliance assessment completed. Score: {score:.1f}%")
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance assessment failed: {e}")
            raise
    
    async def _check_rule_compliance(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check compliance for a specific rule."""
        violations = []
        
        try:
            # Route to appropriate check method based on rule category
            if rule.category == "data_protection":
                violations.extend(await self._check_data_protection(rule))
            elif rule.category == "access_control":
                violations.extend(await self._check_access_control(rule))
            elif rule.category == "network_security":
                violations.extend(await self._check_network_security(rule))
            elif rule.category == "monitoring":
                violations.extend(await self._check_monitoring(rule))
            elif rule.category == "encryption":
                violations.extend(await self._check_encryption(rule))
            else:
                # Generic check
                violations.extend(await self._generic_compliance_check(rule))
                
        except Exception as e:
            logger.error(f"Failed to check rule {rule.id}: {e}")
            violations.append(ComplianceViolation(
                rule_id=rule.id,
                resource_id="unknown",
                resource_type="unknown",
                provider="unknown",
                status=ComplianceStatus.UNKNOWN,
                message=f"Check failed: {e}",
                detected_at=datetime.utcnow()
            ))
        
        return violations
    
    async def _check_data_protection(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check data protection compliance."""
        violations = []
        
        # Check AWS encryption
        if 'config' in self.aws_clients:
            violations.extend(await self._check_aws_encryption())
        
        # Check Azure encryption
        if self.azure_credentials:
            violations.extend(await self._check_azure_encryption())
        
        # Check GCP encryption
        if self.gcp_clients:
            violations.extend(await self._check_gcp_encryption())
        
        return violations
    
    async def _check_access_control(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check access control compliance."""
        violations = []
        
        # Check IAM policies and configurations
        if 'iam' in self.aws_clients:
            violations.extend(await self._check_aws_iam())
        
        return violations
    
    async def _check_network_security(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check network security compliance."""
        violations = []
        
        # Check security groups, NACLs, firewalls
        if 'ec2' in self.aws_clients:
            violations.extend(await self._check_aws_network_security())
        
        return violations
    
    async def _check_monitoring(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check monitoring compliance."""
        violations = []
        
        # Check logging and monitoring configurations
        if 'cloudtrail' in self.aws_clients:
            violations.extend(await self._check_aws_logging())
        
        return violations
    
    async def _check_encryption(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check encryption compliance."""
        violations = []
        
        # Check encryption in transit and at rest
        violations.extend(await self._check_data_protection(rule))
        
        return violations
    
    async def _generic_compliance_check(self, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Generic compliance check for rules without specific implementation."""
        # This would be implemented based on specific rule requirements
        return []
    
    async def _check_aws_encryption(self) -> List[ComplianceViolation]:
        """Check AWS encryption compliance."""
        violations = []
        
        try:
            # Check S3 bucket encryption
            s3_client = boto3.client('s3')
            buckets = s3_client.list_buckets()['Buckets']
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                try:
                    encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
                except s3_client.exceptions.ClientError:
                    # No encryption configured
                    violations.append(ComplianceViolation(
                        rule_id="encryption_check",
                        resource_id=bucket_name,
                        resource_type="s3_bucket",
                        provider="aws",
                        status=ComplianceStatus.NON_COMPLIANT,
                        message="S3 bucket encryption not enabled",
                        detected_at=datetime.utcnow(),
                        remediation_steps=["Enable S3 bucket encryption with KMS or AES-256"]
                    ))
            
        except Exception as e:
            logger.error(f"AWS encryption check failed: {e}")
        
        return violations
    
    async def _check_azure_encryption(self) -> List[ComplianceViolation]:
        """Check Azure encryption compliance."""
        violations = []
        # Implementation would check Azure encryption settings
        return violations
    
    async def _check_gcp_encryption(self) -> List[ComplianceViolation]:
        """Check GCP encryption compliance."""
        violations = []
        # Implementation would check GCP encryption settings
        return violations
    
    async def _check_aws_iam(self) -> List[ComplianceViolation]:
        """Check AWS IAM compliance."""
        violations = []
        
        try:
            iam_client = self.aws_clients['iam']
            
            # Check for root access keys
            account_summary = iam_client.get_account_summary()
            if account_summary['SummaryMap'].get('AccountAccessKeysPresent', 0) > 0:
                violations.append(ComplianceViolation(
                    rule_id="iam_root_access_keys",
                    resource_id="root_account",
                    resource_type="iam_user",
                    provider="aws",
                    status=ComplianceStatus.NON_COMPLIANT,
                    message="Root account has access keys",
                    detected_at=datetime.utcnow(),
                    remediation_steps=["Remove root account access keys", "Use IAM users instead"]
                ))
            
            # Check MFA for users
            users = iam_client.list_users()['Users']
            for user in users:
                mfa_devices = iam_client.list_mfa_devices(UserName=user['UserName'])
                if not mfa_devices['MFADevices']:
                    violations.append(ComplianceViolation(
                        rule_id="iam_mfa_required",
                        resource_id=user['UserName'],
                        resource_type="iam_user",
                        provider="aws",
                        status=ComplianceStatus.NON_COMPLIANT,
                        message="User does not have MFA enabled",
                        detected_at=datetime.utcnow(),
                        remediation_steps=["Enable MFA for user"]
                    ))
            
        except Exception as e:
            logger.error(f"AWS IAM check failed: {e}")
        
        return violations
    
    async def _check_aws_network_security(self) -> List[ComplianceViolation]:
        """Check AWS network security compliance."""
        violations = []
        
        try:
            ec2_client = self.aws_clients['ec2']
            
            # Check security groups for overly permissive rules
            security_groups = ec2_client.describe_security_groups()['SecurityGroups']
            
            for sg in security_groups:
                for rule in sg['IpPermissions']:
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            violations.append(ComplianceViolation(
                                rule_id="network_security_group",
                                resource_id=sg['GroupId'],
                                resource_type="security_group",
                                provider="aws",
                                status=ComplianceStatus.NON_COMPLIANT,
                                message="Security group allows access from 0.0.0.0/0",
                                detected_at=datetime.utcnow(),
                                remediation_steps=["Restrict security group rules to specific IP ranges"]
                            ))
            
        except Exception as e:
            logger.error(f"AWS network security check failed: {e}")
        
        return violations
    
    async def _check_aws_logging(self) -> List[ComplianceViolation]:
        """Check AWS logging compliance."""
        violations = []
        
        try:
            cloudtrail_client = self.aws_clients['cloudtrail']
            
            # Check CloudTrail configuration
            trails = cloudtrail_client.describe_trails()['trailList']
            
            if not trails:
                violations.append(ComplianceViolation(
                    rule_id="logging_cloudtrail",
                    resource_id="account",
                    resource_type="cloudtrail",
                    provider="aws",
                    status=ComplianceStatus.NON_COMPLIANT,
                    message="No CloudTrail configured",
                    detected_at=datetime.utcnow(),
                    remediation_steps=["Configure CloudTrail for audit logging"]
                ))
            else:
                for trail in trails:
                    trail_status = cloudtrail_client.get_trail_status(
                        Name=trail['TrailARN']
                    )
                    if not trail_status['IsLogging']:
                        violations.append(ComplianceViolation(
                            rule_id="logging_cloudtrail_enabled",
                            resource_id=trail['Name'],
                            resource_type="cloudtrail",
                            provider="aws",
                            status=ComplianceStatus.NON_COMPLIANT,
                            message="CloudTrail logging is disabled",
                            detected_at=datetime.utcnow(),
                            remediation_steps=["Enable CloudTrail logging"]
                        ))
            
        except Exception as e:
            logger.error(f"AWS logging check failed: {e}")
        
        return violations
    
    def _generate_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        # Group violations by type
        violation_groups = {}
        for violation in violations:
            key = f"{violation.rule_id}_{violation.status.value}"
            if key not in violation_groups:
                violation_groups[key] = []
            violation_groups[key].append(violation)
        
        # Generate recommendations
        for group_key, group_violations in violation_groups.items():
            count = len(group_violations)
            violation_type = group_violations[0].rule_id
            
            if violation_type == "encryption_check":
                recommendations.append(
                    f"Enable encryption for {count} unencrypted resources to improve data protection"
                )
            elif violation_type == "iam_mfa_required":
                recommendations.append(
                    f"Enable MFA for {count} users to enhance access security"
                )
            elif violation_type == "network_security_group":
                recommendations.append(
                    f"Restrict {count} overly permissive security group rules"
                )
            elif violation_type == "logging_cloudtrail":
                recommendations.append(
                    "Enable CloudTrail logging for comprehensive audit trails"
                )
        
        return recommendations
    
    async def generate_compliance_dashboard(self) -> Dict[str, Any]:
        """Generate compliance dashboard data."""
        try:
            dashboard_data = {
                "overview": {
                    "total_frameworks": len(self.enabled_frameworks),
                    "total_violations": len(self.violations),
                    "last_assessment": datetime.utcnow().isoformat()
                },
                "framework_scores": {},
                "violation_summary": {},
                "top_recommendations": []
            }
            
            # Framework scores
            for framework_name, report in self.reports.items():
                dashboard_data["framework_scores"][framework_name] = {
                    "score": report.score,
                    "total_rules": report.total_rules,
                    "violations": len(report.violations)
                }
            
            # Violation summary
            violation_counts = {}
            for violation in self.violations:
                status = violation.status.value
                if status not in violation_counts:
                    violation_counts[status] = 0
                violation_counts[status] += 1
            
            dashboard_data["violation_summary"] = violation_counts
            
            # Top recommendations (from all reports)
            all_recommendations = []
            for report in self.reports.values():
                all_recommendations.extend(report.recommendations)
            
            dashboard_data["top_recommendations"] = list(set(all_recommendations))[:10]
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")
            raise
    
    async def export_compliance_report(self, 
                                     framework: ComplianceFramework,
                                     format: str = "json") -> str:
        """Export compliance report in specified format."""
        try:
            if framework.value not in self.reports:
                raise ValueError(f"No report available for framework {framework.value}")
            
            report = self.reports[framework.value]
            
            if format.lower() == "json":
                return json.dumps({
                    "framework": report.framework.value,
                    "assessment_date": report.assessment_date.isoformat(),
                    "score": report.score,
                    "total_rules": report.total_rules,
                    "compliant_rules": report.compliant_rules,
                    "violations": [
                        {
                            "rule_id": v.rule_id,
                            "resource_id": v.resource_id,
                            "resource_type": v.resource_type,
                            "provider": v.provider,
                            "status": v.status.value,
                            "message": v.message,
                            "detected_at": v.detected_at.isoformat(),
                            "remediation_steps": v.remediation_steps
                        }
                        for v in report.violations
                    ],
                    "recommendations": report.recommendations
                }, indent=2)
            
            elif format.lower() == "yaml":
                report_dict = {
                    "framework": report.framework.value,
                    "assessment_date": report.assessment_date.isoformat(),
                    "score": report.score,
                    "total_rules": report.total_rules,
                    "compliant_rules": report.compliant_rules,
                    "violations": [
                        {
                            "rule_id": v.rule_id,
                            "resource_id": v.resource_id,
                            "resource_type": v.resource_type,
                            "provider": v.provider,
                            "status": v.status.value,
                            "message": v.message,
                            "detected_at": v.detected_at.isoformat(),
                            "remediation_steps": v.remediation_steps
                        }
                        for v in report.violations
                    ],
                    "recommendations": report.recommendations
                }
                return yaml.dump(report_dict, default_flow_style=False)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            raise

# Example usage and configuration
if __name__ == "__main__":
    # Example configuration
    config = {
        "enabled_frameworks": [
            ComplianceFramework.GDPR.value,
            ComplianceFramework.SOC2.value,
            ComplianceFramework.ISO27001.value
        ],
        "aws": {
            "enabled": True,
            "region": "us-east-1"
        },
        "azure": {
            "enabled": True,
            "subscription_id": "your-subscription-id"
        },
        "gcp": {
            "enabled": True,
            "project_id": "your-project-id"
        }
    }
    
    async def main() -> None:
        # Initialize compliance monitor
        monitor = ComplianceMonitor(config)
        
        # Run GDPR assessment
        gdpr_report = await monitor.run_compliance_assessment(ComplianceFramework.GDPR)
        print(f"GDPR Compliance Score: {gdpr_report.score:.1f}%")
        
        # Generate dashboard
        dashboard = await monitor.generate_compliance_dashboard()
        print("Compliance Dashboard Generated")
        
        # Export report
        report_json = await monitor.export_compliance_report(
            ComplianceFramework.GDPR, "json"
        )
        print("Report exported to JSON")
    
    # Run the example
    asyncio.run(main())