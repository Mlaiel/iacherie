#!/usr/bin/env python3
"""
Compliance Test Engine - Ainflue Quality Platform
===============================================

Enterprise-grade compliance testing engine for regulatory and security compliance.
Demonstrates Security Specialist + Legal + Backend Senior expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import re
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import aiohttp
import aiofiles
from urllib.parse import urlparse, parse_qs
import sqlite3
import csv
import subprocess
import platform
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import requests
import pkg_resources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOX = "sox"  # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    ISO_27001 = "iso_27001"  # Information Security Management
    NIST = "nist"  # National Institute of Standards and Technology
    OWASP = "owasp"  # Open Web Application Security Project
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    SOC2 = "soc2"  # Service Organization Control 2


class ComplianceCategory(Enum):
    """Compliance test categories"""
    DATA_PROTECTION = "data_protection"
    PRIVACY = "privacy"
    SECURITY = "security"
    ACCESS_CONTROL = "access_control"
    ENCRYPTION = "encryption"
    AUDIT_LOGGING = "audit_logging"
    DATA_RETENTION = "data_retention"
    INCIDENT_RESPONSE = "incident_response"
    BUSINESS_CONTINUITY = "business_continuity"
    THIRD_PARTY = "third_party"


class ComplianceSeverity(Enum):
    """Compliance violation severity levels"""
    CRITICAL = "critical"  # Immediate legal/regulatory risk
    HIGH = "high"  # Significant compliance risk
    MEDIUM = "medium"  # Moderate compliance concern
    LOW = "low"  # Minor compliance issue
    INFO = "info"  # Informational finding


class ComplianceStatus(Enum):
    """Compliance test status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    REQUIRES_REVIEW = "requires_review"
    ERROR = "error"


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement"""
    id: str
    standard: ComplianceStandard
    category: ComplianceCategory
    title: str
    description: str
    severity: ComplianceSeverity
    test_method: str
    remediation: str
    references: List[str] = field(default_factory=list)
    automated: bool = True
    applicable_systems: List[str] = field(default_factory=list)


@dataclass
class ComplianceTestResult:
    """Result of compliance test execution"""
    requirement_id: str
    test_name: str
    standard: ComplianceStandard
    category: ComplianceCategory
    status: ComplianceStatus
    severity: ComplianceSeverity
    timestamp: datetime
    description: str
    findings: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    execution_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Comprehensive compliance assessment report"""
    report_id: str
    generated_at: datetime
    standards_tested: List[ComplianceStandard]
    total_requirements: int
    compliant_count: int
    non_compliant_count: int
    partially_compliant_count: int
    overall_score: float
    risk_level: str
    test_results: List[ComplianceTestResult] = field(default_factory=list)
    executive_summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    next_review_date: datetime = None


class ComplianceTestEngine:
    """
    Enterprise compliance testing engine
    
    Demonstrates expertise in:
    - Security Specialist: Security compliance and regulatory requirements
    - Legal: Understanding of regulatory frameworks and legal implications
    - Backend Senior: Systematic testing and audit capabilities
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.requirements_db = {}
        self.test_history = []
        self.current_assessment = None
        
        # Initialize directories
        self.reports_dir = Path("reports/compliance")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load compliance requirements
        self._load_compliance_requirements()
        
        logger.info("ComplianceTestEngine initialized")
    
    def _load_compliance_requirements(self):
        """Load compliance requirements definitions (Legal + Security expertise)"""
        # GDPR Requirements
        gdpr_requirements = [
            ComplianceRequirement(
                id="GDPR-001",
                standard=ComplianceStandard.GDPR,
                category=ComplianceCategory.DATA_PROTECTION,
                title="Data Processing Lawfulness",
                description="Ensure all personal data processing has a lawful basis",
                severity=ComplianceSeverity.CRITICAL,
                test_method="audit_data_processing_activities",
                remediation="Implement consent management and lawful basis documentation",
                references=["GDPR Article 6", "GDPR Article 7"]
            ),
            ComplianceRequirement(
                id="GDPR-002",
                standard=ComplianceStandard.GDPR,
                category=ComplianceCategory.PRIVACY,
                title="Data Subject Rights",
                description="Implement mechanisms for data subject rights (access, portability, deletion)",
                severity=ComplianceSeverity.HIGH,
                test_method="test_data_subject_rights",
                remediation="Implement automated data subject request handling",
                references=["GDPR Chapter III"]
            ),
            ComplianceRequirement(
                id="GDPR-003",
                standard=ComplianceStandard.GDPR,
                category=ComplianceCategory.SECURITY,
                title="Data Protection by Design",
                description="Implement privacy by design and default principles",
                severity=ComplianceSeverity.HIGH,
                test_method="assess_privacy_by_design",
                remediation="Integrate privacy controls into system architecture",
                references=["GDPR Article 25"]
            )
        ]
        
        # PCI DSS Requirements
        pci_requirements = [
            ComplianceRequirement(
                id="PCI-001",
                standard=ComplianceStandard.PCI_DSS,
                category=ComplianceCategory.SECURITY,
                title="Install and Maintain Firewall Configuration",
                description="Build and maintain secure network and system configurations",
                severity=ComplianceSeverity.CRITICAL,
                test_method="audit_firewall_configuration",
                remediation="Implement and document firewall rules and network segmentation",
                references=["PCI DSS Requirement 1"]
            ),
            ComplianceRequirement(
                id="PCI-002",
                standard=ComplianceStandard.PCI_DSS,
                category=ComplianceCategory.ENCRYPTION,
                title="Protect Cardholder Data",
                description="Protect stored cardholder data with strong encryption",
                severity=ComplianceSeverity.CRITICAL,
                test_method="test_cardholder_data_encryption",
                remediation="Implement AES-256 encryption for all cardholder data at rest",
                references=["PCI DSS Requirement 3"]
            )
        ]
        
        # OWASP Security Requirements
        owasp_requirements = [
            ComplianceRequirement(
                id="OWASP-001",
                standard=ComplianceStandard.OWASP,
                category=ComplianceCategory.SECURITY,
                title="Injection Prevention",
                description="Prevent injection flaws (SQL, NoSQL, OS, LDAP)",
                severity=ComplianceSeverity.CRITICAL,
                test_method="test_injection_vulnerabilities",
                remediation="Implement parameterized queries and input validation",
                references=["OWASP Top 10 A03:2021"]
            ),
            ComplianceRequirement(
                id="OWASP-002",
                standard=ComplianceStandard.OWASP,
                category=ComplianceCategory.SECURITY,
                title="Broken Authentication",
                description="Implement proper authentication and session management",
                severity=ComplianceSeverity.HIGH,
                test_method="test_authentication_security",
                remediation="Implement multi-factor authentication and secure session handling",
                references=["OWASP Top 10 A07:2021"]
            )
        ]
        
        # Store requirements by standard
        all_requirements = gdpr_requirements + pci_requirements + owasp_requirements
        
        for req in all_requirements:
            if req.standard not in self.requirements_db:
                self.requirements_db[req.standard] = []
            self.requirements_db[req.standard].append(req)
        
        logger.info(f"Loaded {len(all_requirements)} compliance requirements")
    
    async def run_compliance_assessment(self, 
                                      standards: List[ComplianceStandard] = None,
                                      target_systems: List[str] = None) -> ComplianceReport:
        """
        Run comprehensive compliance assessment
        
        Security expertise: Multi-standard compliance validation
        Legal expertise: Regulatory requirement verification
        Backend expertise: Systematic testing and documentation
        """
        logger.info("Starting compliance assessment")
        
        if standards is None:
            standards = list(ComplianceStandard)
        
        report_id = f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report = ComplianceReport(
            report_id=report_id,
            generated_at=datetime.now(),
            standards_tested=standards,
            total_requirements=0,
            compliant_count=0,
            non_compliant_count=0,
            partially_compliant_count=0,
            overall_score=0.0,
            risk_level="UNKNOWN"
        )
        
        self.current_assessment = report
        
        try:
            # Test each standard
            for standard in standards:
                if standard in self.requirements_db:
                    requirements = self.requirements_db[standard]
                    report.total_requirements += len(requirements)
                    
                    for requirement in requirements:
                        result = await self._test_requirement(requirement, target_systems)
                        report.test_results.append(result)
                        
                        # Update counters
                        if result.status == ComplianceStatus.COMPLIANT:
                            report.compliant_count += 1
                        elif result.status == ComplianceStatus.NON_COMPLIANT:
                            report.non_compliant_count += 1
                        elif result.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                            report.partially_compliant_count += 1
            
            # Calculate overall compliance score
            if report.total_requirements > 0:
                compliant_weight = report.compliant_count * 1.0
                partial_weight = report.partially_compliant_count * 0.5
                report.overall_score = (compliant_weight + partial_weight) / report.total_requirements * 100
            
            # Determine risk level
            report.risk_level = self._calculate_risk_level(report)
            
            # Generate executive summary and recommendations
            await self._generate_executive_summary(report)
            await self._generate_recommendations(report)
            
            # Save report
            await self._save_compliance_report(report)
            
            # Set next review date
            report.next_review_date = datetime.now() + timedelta(days=90)  # Quarterly review
            
        except Exception as e:
            logger.error(f"Compliance assessment failed: {e}")
            raise
        
        logger.info(f"Compliance assessment completed: {report.overall_score:.1f}% compliant")
        return report
    
    async def _test_requirement(self, requirement: ComplianceRequirement, 
                               target_systems: List[str] = None) -> ComplianceTestResult:
        """Test individual compliance requirement"""
        start_time = time.time()
        
        result = ComplianceTestResult(
            requirement_id=requirement.id,
            test_name=requirement.title,
            standard=requirement.standard,
            category=requirement.category,
            status=ComplianceStatus.ERROR,
            severity=requirement.severity,
            timestamp=datetime.now(),
            description=requirement.description
        )
        
        try:
            # Route to appropriate test method
            if requirement.test_method == "audit_data_processing_activities":
                await self._test_data_processing_activities(result)
            elif requirement.test_method == "test_data_subject_rights":
                await self._test_data_subject_rights(result)
            elif requirement.test_method == "assess_privacy_by_design":
                await self._test_privacy_by_design(result)
            elif requirement.test_method == "audit_firewall_configuration":
                await self._test_firewall_configuration(result)
            elif requirement.test_method == "test_cardholder_data_encryption":
                await self._test_cardholder_data_encryption(result)
            elif requirement.test_method == "test_injection_vulnerabilities":
                await self._test_injection_vulnerabilities(result)
            elif requirement.test_method == "test_authentication_security":
                await self._test_authentication_security(result)
            else:
                result.status = ComplianceStatus.NOT_APPLICABLE
                result.findings.append(f"Test method '{requirement.test_method}' not implemented")
        
        except Exception as e:
            result.status = ComplianceStatus.ERROR
            result.errors.append(str(e))
            logger.error(f"Failed to test requirement {requirement.id}: {e}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _test_data_processing_activities(self, result: ComplianceTestResult):
        """Test GDPR data processing lawfulness (Legal + Security expertise)"""
        logger.info("Testing data processing activities compliance")
        
        # Check for privacy policy
        privacy_policy_found = False
        consent_management_found = False
        
        # Look for privacy policy files
        privacy_files = [
            "privacy_policy.md", "privacy.md", "PRIVACY.md",
            "privacy_policy.html", "privacy.html"
        ]
        
        for policy_file in privacy_files:
            if Path(policy_file).exists():
                privacy_policy_found = True
                result.evidence.append(f"Privacy policy found: {policy_file}")
                break
        
        # Check for consent management implementation
        consent_patterns = [
            r"consent.*management", r"gdpr.*consent", r"cookie.*consent",
            r"data.*processing.*consent", r"lawful.*basis"
        ]
        
        # Search in source code for consent-related patterns
        source_dirs = [".", "src", "app", "backend", "frontend"]
        for source_dir in source_dirs:
            if Path(source_dir).exists():
                for py_file in Path(source_dir).rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        for pattern in consent_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                consent_management_found = True
                                result.evidence.append(f"Consent management code found in {py_file}")
                                break
                    except Exception:
                        continue
        
        # Evaluate compliance
        if privacy_policy_found and consent_management_found:
            result.status = ComplianceStatus.COMPLIANT
            result.findings.append("Privacy policy and consent management mechanisms found")
        elif privacy_policy_found or consent_management_found:
            result.status = ComplianceStatus.PARTIALLY_COMPLIANT
            result.findings.append("Partial compliance: Missing either privacy policy or consent management")
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
            result.findings.append("No privacy policy or consent management mechanisms found")
            result.recommendations.append("Implement privacy policy and consent management system")
    
    async def _test_data_subject_rights(self, result: ComplianceTestResult):
        """Test GDPR data subject rights implementation (Legal + Backend expertise)"""
        logger.info("Testing data subject rights implementation")
        
        # Check for data subject rights endpoints/functionality
        rights_endpoints = {
            "access": ["data_export", "get_user_data", "data_access"],
            "deletion": ["delete_user", "data_deletion", "right_to_be_forgotten"],
            "portability": ["export_data", "data_portability", "download_data"],
            "rectification": ["update_user", "correct_data", "data_correction"]
        }
        
        implemented_rights = []
        
        # Search for API endpoints or functions implementing data subject rights
        source_dirs = [".", "src", "app", "backend", "api"]
        for source_dir in source_dirs:
            if Path(source_dir).exists():
                for py_file in Path(source_dir).rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        for right, patterns in rights_endpoints.items():
                            for pattern in patterns:
                                if pattern.lower() in content.lower():
                                    if right not in implemented_rights:
                                        implemented_rights.append(right)
                                        result.evidence.append(f"Data subject right '{right}' found in {py_file}")
                    except Exception:
                        continue
        
        # Evaluate compliance based on implemented rights
        total_rights = len(rights_endpoints)
        implemented_count = len(implemented_rights)
        
        if implemented_count >= total_rights:
            result.status = ComplianceStatus.COMPLIANT
        elif implemented_count >= total_rights // 2:
            result.status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
        
        result.findings.append(f"Implemented {implemented_count}/{total_rights} data subject rights")
        
        if implemented_count < total_rights:
            missing_rights = [right for right in rights_endpoints.keys() if right not in implemented_rights]
            result.recommendations.append(f"Implement missing data subject rights: {', '.join(missing_rights)}")
    
    async def _test_privacy_by_design(self, result: ComplianceTestResult):
        """Test privacy by design implementation (Security + Backend expertise)"""
        logger.info("Testing privacy by design principles")
        
        privacy_indicators = {
            "data_minimization": ["minimal_data", "data_minimization", "collect_only_necessary"],
            "encryption": ["encrypt", "cryptography", "hash", "secure"],
            "access_control": ["authenticate", "authorize", "permission", "rbac"],
            "audit_logging": ["audit", "log", "tracking", "monitor"],
            "anonymization": ["anonymize", "pseudonymize", "mask_data"]
        }
        
        found_indicators = []
        
        # Search for privacy by design indicators in code
        source_dirs = [".", "src", "app", "backend"]
        for source_dir in source_dirs:
            if Path(source_dir).exists():
                for py_file in Path(source_dir).rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        for principle, patterns in privacy_indicators.items():
                            for pattern in patterns:
                                if pattern.lower() in content.lower():
                                    if principle not in found_indicators:
                                        found_indicators.append(principle)
                                        result.evidence.append(f"Privacy principle '{principle}' found in {py_file}")
                    except Exception:
                        continue
        
        # Evaluate privacy by design implementation
        total_principles = len(privacy_indicators)
        found_count = len(found_indicators)
        
        if found_count >= total_principles * 0.8:  # 80% threshold
            result.status = ComplianceStatus.COMPLIANT
        elif found_count >= total_principles * 0.5:  # 50% threshold
            result.status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
        
        result.findings.append(f"Found {found_count}/{total_principles} privacy by design principles")
        
        if found_count < total_principles:
            missing_principles = [p for p in privacy_indicators.keys() if p not in found_indicators]
            result.recommendations.append(f"Implement missing privacy principles: {', '.join(missing_principles)}")
    
    async def _test_firewall_configuration(self, result: ComplianceTestResult):
        """Test firewall configuration (Security + DevOps expertise)"""
        logger.info("Testing firewall configuration")
        
        # Check for firewall configuration files
        firewall_configs = [
            "iptables.rules", "ufw.rules", "firewall.conf",
            "security-groups.yaml", "network-policies.yaml"
        ]
        
        config_found = False
        for config_file in firewall_configs:
            if Path(config_file).exists():
                config_found = True
                result.evidence.append(f"Firewall configuration found: {config_file}")
        
        # Check Docker/Kubernetes network policies
        docker_files = list(Path(".").glob("*docker*"))
        k8s_files = list(Path(".").glob("*k8s*")) + list(Path(".").glob("*kubernetes*"))
        
        if docker_files or k8s_files:
            result.evidence.append("Container network configuration found")
            config_found = True
        
        # Test network connectivity (basic port scan)
        try:
            common_ports = [22, 80, 443, 3306, 5432, 6379, 27017]
            open_ports = []
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result_code = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result_code == 0:
                    open_ports.append(port)
            
            if open_ports:
                result.findings.append(f"Open ports detected: {open_ports}")
                if len(open_ports) > 5:
                    result.recommendations.append("Review and restrict unnecessary open ports")
            
        except Exception as e:
            result.errors.append(f"Port scan failed: {e}")
        
        # Evaluate compliance
        if config_found:
            result.status = ComplianceStatus.COMPLIANT
            result.findings.append("Firewall configuration documented and implemented")
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
            result.findings.append("No firewall configuration found")
            result.recommendations.append("Implement and document firewall rules")
    
    async def _test_cardholder_data_encryption(self, result: ComplianceTestResult):
        """Test cardholder data encryption (Security + Backend expertise)"""
        logger.info("Testing cardholder data encryption")
        
        # Look for encryption implementations
        encryption_patterns = [
            r"AES.*encrypt", r"RSA.*encrypt", r"encrypt.*card",
            r"cryptography", r"Fernet", r"cipher", r"bcrypt"
        ]
        
        encryption_found = False
        weak_encryption_found = False
        
        # Search for encryption in code
        source_dirs = [".", "src", "app", "backend"]
        for source_dir in source_dirs:
            if Path(source_dir).exists():
                for py_file in Path(source_dir).rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        for pattern in encryption_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                encryption_found = True
                                result.evidence.append(f"Encryption implementation found in {py_file}")
                        
                        # Check for weak encryption
                        weak_patterns = [r"MD5", r"SHA1", r"DES", r"RC4"]
                        for weak_pattern in weak_patterns:
                            if re.search(weak_pattern, content, re.IGNORECASE):
                                weak_encryption_found = True
                                result.findings.append(f"Weak encryption algorithm found: {weak_pattern}")
                    except Exception:
                        continue
        
        # Check for environment variables with encryption keys
        env_files = [".env", ".env.production", ".env.staging"]
        for env_file in env_files:
            if Path(env_file).exists():
                try:
                    content = Path(env_file).read_text()
                    if re.search(r"(ENCRYPT|CIPHER|KEY)", content, re.IGNORECASE):
                        result.evidence.append(f"Encryption configuration found in {env_file}")
                except Exception:
                    pass
        
        # Evaluate compliance
        if encryption_found and not weak_encryption_found:
            result.status = ComplianceStatus.COMPLIANT
            result.findings.append("Strong encryption implementation found")
        elif encryption_found and weak_encryption_found:
            result.status = ComplianceStatus.PARTIALLY_COMPLIANT
            result.findings.append("Encryption found but weak algorithms detected")
            result.recommendations.append("Replace weak encryption with AES-256 or equivalent")
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
            result.findings.append("No encryption implementation found for sensitive data")
            result.recommendations.append("Implement AES-256 encryption for all cardholder data")
    
    async def _test_injection_vulnerabilities(self, result: ComplianceTestResult):
        """Test for injection vulnerabilities (Security expertise)"""
        logger.info("Testing for injection vulnerabilities")
        
        # SQL injection patterns to look for (vulnerable code)
        vulnerable_patterns = [
            r"cursor\.execute\([^%]*%[^s]",  # String formatting in SQL
            r"\.execute\(.*\+.*\)",  # String concatenation in SQL
            r"query.*=.*['\"].*\+",  # Query string concatenation
            r"SELECT.*\+.*FROM",  # Direct SQL concatenation
        ]
        
        # Safe patterns to look for (good practices)
        safe_patterns = [
            r"cursor\.execute\(.*,.*\)",  # Parameterized queries
            r"\.execute\(.*\?.*\)",  # Parameterized queries
            r"prepared.*statement", r"bind.*parameter",
            r"sqlalchemy", r"ORM"  # ORM usage
        ]
        
        vulnerabilities_found = []
        safe_practices_found = []
        
        # Search in source code
        source_dirs = [".", "src", "app", "backend"]
        for source_dir in source_dirs:
            if Path(source_dir).exists():
                for py_file in Path(source_dir).rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        
                        # Check for vulnerable patterns
                        for pattern in vulnerable_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                vulnerabilities_found.extend(matches)
                                result.findings.append(f"Potential SQL injection in {py_file}")
                        
                        # Check for safe patterns
                        for pattern in safe_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                safe_practices_found.append(pattern)
                                result.evidence.append(f"Safe SQL practice found in {py_file}")
                    
                    except Exception:
                        continue
        
        # Evaluate compliance
        if not vulnerabilities_found and safe_practices_found:
            result.status = ComplianceStatus.COMPLIANT
            result.findings.append("No injection vulnerabilities found, safe practices implemented")
        elif not vulnerabilities_found:
            result.status = ComplianceStatus.PARTIALLY_COMPLIANT
            result.findings.append("No obvious vulnerabilities, but limited safe practices found")
            result.recommendations.append("Implement more parameterized queries and input validation")
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
            result.findings.append(f"Found {len(vulnerabilities_found)} potential injection vulnerabilities")
            result.recommendations.append("Fix SQL injection vulnerabilities with parameterized queries")
    
    async def _test_authentication_security(self, result: ComplianceTestResult):
        """Test authentication security implementation (Security + Backend expertise)"""
        logger.info("Testing authentication security")
        
        # Authentication security indicators
        security_patterns = {
            "password_hashing": [r"bcrypt", r"scrypt", r"pbkdf2", r"argon2"],
            "session_security": [r"secure.*session", r"httponly", r"samesite"],
            "mfa": [r"multi.*factor", r"2fa", r"mfa", r"totp", r"authenticator"],
            "rate_limiting": [r"rate.*limit", r"throttle", r"slowdown"],
            "secure_headers": [r"csrf", r"xframe", r"hsts", r"content.*security"]
        }
        
        found_features = {}
        
        # Search in source code and configuration
        search_paths = [".", "src", "app", "backend", "config"]
        for search_path in search_paths:
            if Path(search_path).exists():
                for file_path in Path(search_path).rglob("*"):
                    if file_path.suffix in ['.py', '.js', '.yaml', '.json', '.conf']:
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            
                            for feature, patterns in security_patterns.items():
                                for pattern in patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        if feature not in found_features:
                                            found_features[feature] = []
                                        found_features[feature].append(str(file_path))
                                        result.evidence.append(f"Security feature '{feature}' found in {file_path}")
                        except Exception:
                            continue
        
        # Evaluate authentication security
        total_features = len(security_patterns)
        found_count = len(found_features)
        
        if found_count >= total_features * 0.8:  # 80% of security features
            result.status = ComplianceStatus.COMPLIANT
        elif found_count >= total_features * 0.5:  # 50% of security features
            result.status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            result.status = ComplianceStatus.NON_COMPLIANT
        
        result.findings.append(f"Found {found_count}/{total_features} authentication security features")
        
        # Generate recommendations for missing features
        missing_features = [feature for feature in security_patterns.keys() if feature not in found_features]
        if missing_features:
            result.recommendations.append(f"Implement missing security features: {', '.join(missing_features)}")
    
    def _calculate_risk_level(self, report: ComplianceReport) -> str:
        """Calculate overall risk level based on compliance results"""
        if report.overall_score >= 90:
            return "LOW"
        elif report.overall_score >= 70:
            return "MEDIUM"
        elif report.overall_score >= 50:
            return "HIGH"
        else:
            return "CRITICAL"
    
    async def _generate_executive_summary(self, report: ComplianceReport):
        """Generate executive summary (Legal + Business expertise)"""
        summary_parts = []
        
        summary_parts.append(f"Compliance Assessment Summary for {len(report.standards_tested)} standards:")
        summary_parts.append(f"Overall Compliance Score: {report.overall_score:.1f}%")
        summary_parts.append(f"Risk Level: {report.risk_level}")
        summary_parts.append("")
        
        summary_parts.append(f"Results Breakdown:")
        summary_parts.append(f"- Compliant: {report.compliant_count} requirements")
        summary_parts.append(f"- Non-Compliant: {report.non_compliant_count} requirements")
        summary_parts.append(f"- Partially Compliant: {report.partially_compliant_count} requirements")
        summary_parts.append("")
        
        # Critical findings
        critical_findings = [r for r in report.test_results 
                           if r.severity == ComplianceSeverity.CRITICAL and 
                           r.status == ComplianceStatus.NON_COMPLIANT]
        
        if critical_findings:
            summary_parts.append(f"CRITICAL: {len(critical_findings)} critical compliance violations require immediate attention.")
        
        report.executive_summary = "\n".join(summary_parts)
    
    async def _generate_recommendations(self, report: ComplianceReport):
        """Generate compliance recommendations (Legal + Security expertise)"""
        recommendations = []
        
        # Priority recommendations based on critical findings
        critical_issues = [r for r in report.test_results 
                          if r.severity == ComplianceSeverity.CRITICAL and 
                          r.status == ComplianceStatus.NON_COMPLIANT]
        
        if critical_issues:
            recommendations.append("IMMEDIATE ACTIONS REQUIRED:")
            for issue in critical_issues[:5]:  # Top 5 critical issues
                recommendations.extend(issue.recommendations)
        
        # General recommendations by category
        categories_with_issues = {}
        for result in report.test_results:
            if result.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:
                if result.category not in categories_with_issues:
                    categories_with_issues[result.category] = []
                categories_with_issues[result.category].append(result)
        
        if categories_with_issues:
            recommendations.append("\nCATEGORICAL IMPROVEMENTS:")
            for category, issues in categories_with_issues.items():
                recommendations.append(f"- {category.value.replace('_', ' ').title()}: {len(issues)} issues")
        
        # Timeline recommendations
        recommendations.append("\nRECOMMENDED TIMELINE:")
        recommendations.append("- Critical issues: Address within 30 days")
        recommendations.append("- High priority issues: Address within 90 days")
        recommendations.append("- Medium/Low issues: Address within 6 months")
        recommendations.append("- Next compliance review: 90 days")
        
        report.recommendations = recommendations
    
    async def _save_compliance_report(self, report: ComplianceReport):
        """Save compliance report to file (Backend expertise)"""
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_report_{report.report_id}_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Convert report to dict for JSON serialization
        report_dict = {
            'report_id': report.report_id,
            'generated_at': report.generated_at.isoformat(),
            'standards_tested': [s.value for s in report.standards_tested],
            'total_requirements': report.total_requirements,
            'compliant_count': report.compliant_count,
            'non_compliant_count': report.non_compliant_count,
            'partially_compliant_count': report.partially_compliant_count,
            'overall_score': report.overall_score,
            'risk_level': report.risk_level,
            'executive_summary': report.executive_summary,
            'recommendations': report.recommendations,
            'next_review_date': report.next_review_date.isoformat() if report.next_review_date else None,
            'test_results': []
        }
        
        # Add test results
        for result in report.test_results:
            result_dict = {
                'requirement_id': result.requirement_id,
                'test_name': result.test_name,
                'standard': result.standard.value,
                'category': result.category.value,
                'status': result.status.value,
                'severity': result.severity.value,
                'timestamp': result.timestamp.isoformat(),
                'description': result.description,
                'findings': result.findings,
                'evidence': result.evidence,
                'recommendations': result.recommendations,
                'affected_systems': result.affected_systems,
                'risk_score': result.risk_score,
                'execution_time_ms': result.execution_time_ms,
                'errors': result.errors
            }
            report_dict['test_results'].append(result_dict)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(report_dict, indent=2))
        
        logger.info(f"Compliance report saved to: {filepath}")
    
    async def generate_compliance_dashboard(self, report: ComplianceReport) -> str:
        """Generate compliance dashboard HTML (Frontend + Backend expertise)"""
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Compliance Dashboard - {report.report_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .score {{ font-size: 48px; font-weight: bold; }}
                .risk-{report.risk_level.lower()} {{ color: {'red' if report.risk_level == 'CRITICAL' else 'orange' if report.risk_level == 'HIGH' else 'green'}; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .results {{ margin: 20px 0; }}
                .compliant {{ color: green; }}
                .non-compliant {{ color: red; }}
                .partial {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Compliance Assessment Report</h1>
                <div class="score risk-{report.risk_level.lower()}">{report.overall_score:.1f}%</div>
                <p>Risk Level: {report.risk_level}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Requirements</h3>
                    <div class="score">{report.total_requirements}</div>
                </div>
                <div class="metric">
                    <h3>Compliant</h3>
                    <div class="score compliant">{report.compliant_count}</div>
                </div>
                <div class="metric">
                    <h3>Non-Compliant</h3>
                    <div class="score non-compliant">{report.non_compliant_count}</div>
                </div>
                <div class="metric">
                    <h3>Partial</h3>
                    <div class="score partial">{report.partially_compliant_count}</div>
                </div>
            </div>
            
            <div class="results">
                <h2>Executive Summary</h2>
                <pre>{report.executive_summary}</pre>
                
                <h2>Recommendations</h2>
                <ul>
        """
        
        for recommendation in report.recommendations:
            dashboard_html += f"<li>{recommendation}</li>"
        
        dashboard_html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return dashboard_html


# Global instance
compliance_test_engine = ComplianceTestEngine()


async def run_gdpr_assessment() -> ComplianceReport:
    """Quick GDPR compliance assessment"""
    return await compliance_test_engine.run_compliance_assessment([ComplianceStandard.GDPR])


async def run_security_compliance_assessment() -> ComplianceReport:
    """Security-focused compliance assessment"""
    return await compliance_test_engine.run_compliance_assessment([
        ComplianceStandard.OWASP,
        ComplianceStandard.NIST,
        ComplianceStandard.ISO_27001
    ])


async def run_full_compliance_assessment() -> ComplianceReport:
    """Comprehensive compliance assessment"""
    return await compliance_test_engine.run_compliance_assessment()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Run GDPR assessment
        report = await run_gdpr_assessment()
        print(f"GDPR Compliance Score: {report.overall_score:.1f}%")
        print(f"Risk Level: {report.risk_level}")
        
        if report.recommendations:
            print("\nRecommendations:")
            for rec in report.recommendations[:5]:
                print(f"  - {rec}")
    
    asyncio.run(main())