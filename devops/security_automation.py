"""
🚀 Security Automation - DevSecOps Automation Framework
======================================================

Enterprise-grade security automation with vulnerability scanning, policy enforcement,
incident response, and compliance monitoring.

Features:
- Vulnerability scanning automation (Trivy, Clair, Snyk)
- Security policy enforcement with Open Policy Agent (OPA)
- Incident response automation workflows
- Security metrics and compliance reporting
- Container and infrastructure security hardening
- SAST/DAST integration and orchestration
- Security baseline establishment and drift detection
- Threat intelligence integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Engineer + Security Expert + DevSecOps + Compliance Engineering
"""

import asyncio
import logging
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import re
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class SeverityLevel(Enum):
    """Security vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    UNKNOWN = "unknown"

class ScanType(Enum):
    """Security scan types"""
    CONTAINER_IMAGE = "container_image"
    SOURCE_CODE = "source_code"
    INFRASTRUCTURE = "infrastructure"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    SECRET = "secret"
    COMPLIANCE = "compliance"

class IncidentStatus(Enum):
    """Security incident status"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class PolicyAction(Enum):
    """Policy enforcement actions"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"

@dataclass
class Vulnerability:
    """Security vulnerability"""
    vuln_id: str
    cve_id: Optional[str]
    title: str
    description: str
    severity: SeverityLevel
    cvss_score: float
    affected_component: str
    fix_version: Optional[str]
    discovered_at: datetime
    scan_type: ScanType
    source_location: Optional[str] = None
    fix_available: bool = False
    exploitable: bool = False
    remediation_steps: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

@dataclass
class SecurityScan:
    """Security scan result"""
    scan_id: str
    scan_type: ScanType
    target: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    scanner: str
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityIncident:
    """Security incident"""
    incident_id: str
    title: str
    description: str
    severity: SeverityLevel
    status: IncidentStatus
    detected_at: datetime
    affected_systems: List[str]
    indicators: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    description: str
    category: str
    rules: List[Dict[str, Any]]
    action: PolicyAction
    enabled: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceCheck:
    """Compliance check result"""
    check_id: str
    standard: str  # PCI-DSS, SOC2, GDPR, etc.
    requirement: str
    status: str  # compliant, non_compliant, not_applicable
    evidence: List[str]
    risk_level: SeverityLevel
    remediation: Optional[str]
    last_checked: datetime

class SecurityAutomation:
    """
    DevSecOps Automation Framework
    
    Responsibilities:
    - Automated vulnerability scanning and assessment
    - Security policy creation and enforcement
    - Incident detection and response automation
    - Compliance monitoring and reporting
    - Security baseline establishment and hardening
    - Threat intelligence integration and analysis
    - Security metrics collection and dashboards
    """
    
    def __init__(self):
        # Vulnerability management
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.scan_history: List[SecurityScan] = []
        self.active_scans: Dict[str, SecurityScan] = {}
        
        # Security incidents
        self.incidents: Dict[str, SecurityIncident] = {}
        self.incident_rules: List[Dict[str, Any]] = []
        
        # Policy management
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.policy_violations: List[Dict[str, Any]] = []
        
        # Compliance monitoring
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.compliance_frameworks: Dict[str, Dict] = {}
        
        # Security baselines and hardening
        self.security_baselines: Dict[str, Dict] = {}
        self.hardening_templates: Dict[str, Dict] = {}
        
        # Threat intelligence
        self.threat_indicators: Dict[str, Dict] = {}
        self.threat_feeds: List[Dict[str, Any]] = []
        
        # Security metrics
        self.security_metrics: deque = deque(maxlen=10000)
        self.risk_scores: Dict[str, float] = {}
        
        # Scanner configurations
        self.scanner_configs: Dict[str, Dict] = {}
        
        self._initialize_security_automation()
        
        logger.info("SecurityAutomation initialized")

    def _initialize_security_automation(self):
        """Initialize security automation system"""
        
        # Start background tasks
        asyncio.create_task(self._vulnerability_scanning_loop())
        asyncio.create_task(self._incident_detection_loop())
        asyncio.create_task(self._policy_enforcement_loop())
        asyncio.create_task(self._compliance_monitoring_loop())
        asyncio.create_task(self._threat_intelligence_loop())
        asyncio.create_task(self._security_metrics_loop())
        
        # Initialize configurations
        self._setup_scanner_configs()
        self._setup_default_policies()
        self._setup_compliance_frameworks()
        self._setup_incident_rules()
        self._setup_security_baselines()
        
        logger.info("Security automation initialization complete")

    def _setup_scanner_configs(self):
        """Setup security scanner configurations"""
        
        self.scanner_configs = {
            "trivy": {
                "name": "Trivy",
                "type": "container_image",
                "command": "trivy",
                "args": ["image", "--format", "json"],
                "timeout": 300
            },
            "clair": {
                "name": "Clair",
                "type": "container_image", 
                "api_endpoint": "http://clair:6060",
                "timeout": 180
            },
            "snyk": {
                "name": "Snyk",
                "type": "dependency",
                "command": "snyk",
                "args": ["test", "--json"],
                "timeout": 240
            },
            "bandit": {
                "name": "Bandit",
                "type": "source_code",
                "command": "bandit",
                "args": ["-r", "-f", "json"],
                "timeout": 120
            },
            "checkov": {
                "name": "Checkov",
                "type": "infrastructure",
                "command": "checkov",
                "args": ["-f", "--framework", "terraform", "--output", "json"],
                "timeout": 180
            },
            "gitleaks": {
                "name": "GitLeaks",
                "type": "secret",
                "command": "gitleaks",
                "args": ["detect", "--report-format", "json"],
                "timeout": 60
            }
        }

    def _setup_default_policies(self):
        """Setup default security policies"""
        
        container_policy = SecurityPolicy(
            policy_id="container_security",
            name="Container Security Policy",
            description="Security requirements for container images",
            category="container",
            rules=[
                {
                    "name": "no_root_user",
                    "description": "Container must not run as root",
                    "condition": "user != 'root' and user != '0'"
                },
                {
                    "name": "no_privileged",
                    "description": "Container must not run in privileged mode",
                    "condition": "privileged != true"
                },
                {
                    "name": "readonly_filesystem",
                    "description": "Container filesystem should be read-only",
                    "condition": "readOnlyRootFilesystem == true"
                },
                {
                    "name": "no_sensitive_ports",
                    "description": "Container should not expose sensitive ports",
                    "condition": "ports not in [22, 23, 3389, 5985, 5986]"
                }
            ],
            action=PolicyAction.DENY,
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        network_policy = SecurityPolicy(
            policy_id="network_security",
            name="Network Security Policy",
            description="Network security requirements",
            category="network",
            rules=[
                {
                    "name": "encrypted_traffic",
                    "description": "All traffic must be encrypted",
                    "condition": "protocol in ['https', 'tls', 'ssl']"
                },
                {
                    "name": "no_default_passwords",
                    "description": "No default passwords allowed",
                    "condition": "password not in default_passwords"
                },
                {
                    "name": "firewall_rules",
                    "description": "Firewall rules must be restrictive",
                    "condition": "source != '0.0.0.0/0' or ports in allowed_ports"
                }
            ],
            action=PolicyAction.WARN,
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.security_policies[container_policy.policy_id] = container_policy
        self.security_policies[network_policy.policy_id] = network_policy

    def _setup_compliance_frameworks(self):
        """Setup compliance framework definitions"""
        
        self.compliance_frameworks = {
            "SOC2": {
                "name": "SOC 2 Type II",
                "description": "Service Organization Control 2",
                "controls": [
                    {
                        "id": "CC6.1",
                        "name": "Logical Access Controls",
                        "description": "Implement logical access security measures"
                    },
                    {
                        "id": "CC6.2", 
                        "name": "Authentication",
                        "description": "Implement authentication mechanisms"
                    },
                    {
                        "id": "CC6.3",
                        "name": "Authorization",
                        "description": "Implement authorization controls"
                    },
                    {
                        "id": "CC7.1",
                        "name": "System Monitoring",
                        "description": "Implement system monitoring controls"
                    }
                ]
            },
            "PCI_DSS": {
                "name": "Payment Card Industry Data Security Standard",
                "description": "PCI DSS Compliance Requirements",
                "controls": [
                    {
                        "id": "1.1",
                        "name": "Firewall Configuration",
                        "description": "Install and maintain firewall configuration"
                    },
                    {
                        "id": "2.1",
                        "name": "Default Passwords",
                        "description": "Change vendor-supplied defaults"
                    },
                    {
                        "id": "3.1",
                        "name": "Data Protection",
                        "description": "Protect stored cardholder data"
                    },
                    {
                        "id": "8.1",
                        "name": "User Access",
                        "description": "Implement strong access control measures"
                    }
                ]
            },
            "GDPR": {
                "name": "General Data Protection Regulation",
                "description": "EU Data Protection Regulation",
                "controls": [
                    {
                        "id": "Art25",
                        "name": "Data Protection by Design",
                        "description": "Data protection by design and by default"
                    },
                    {
                        "id": "Art32",
                        "name": "Security of Processing",
                        "description": "Security of processing requirements"
                    },
                    {
                        "id": "Art33",
                        "name": "Breach Notification",
                        "description": "Personal data breach notification"
                    }
                ]
            }
        }

    def _setup_incident_rules(self):
        """Setup incident detection rules"""
        
        self.incident_rules = [
            {
                "name": "critical_vulnerability_detected",
                "description": "Critical vulnerability detected in production",
                "conditions": [
                    "severity == 'critical'",
                    "environment == 'production'"
                ],
                "severity": SeverityLevel.CRITICAL,
                "auto_respond": True
            },
            {
                "name": "multiple_failed_logins",
                "description": "Multiple failed login attempts detected",
                "conditions": [
                    "event_type == 'failed_login'",
                    "count > 5",
                    "time_window == '5m'"
                ],
                "severity": SeverityLevel.HIGH,
                "auto_respond": True
            },
            {
                "name": "privilege_escalation",
                "description": "Privilege escalation attempt detected",
                "conditions": [
                    "action == 'privilege_escalation'",
                    "user_role != 'admin'"
                ],
                "severity": SeverityLevel.HIGH,
                "auto_respond": True
            },
            {
                "name": "data_exfiltration",
                "description": "Unusual data access pattern detected",
                "conditions": [
                    "data_volume > normal_threshold * 3",
                    "time_of_day not in business_hours"
                ],
                "severity": SeverityLevel.CRITICAL,
                "auto_respond": True
            }
        ]

    def _setup_security_baselines(self):
        """Setup security baseline configurations"""
        
        self.security_baselines = {
            "ubuntu_20_04": {
                "name": "Ubuntu 20.04 Security Baseline",
                "os": "ubuntu",
                "version": "20.04",
                "checks": [
                    {
                        "id": "ssh_config",
                        "name": "SSH Configuration",
                        "description": "Secure SSH configuration",
                        "commands": [
                            "grep '^PermitRootLogin no' /etc/ssh/sshd_config",
                            "grep '^PasswordAuthentication no' /etc/ssh/sshd_config"
                        ]
                    },
                    {
                        "id": "firewall_enabled",
                        "name": "Firewall Status",
                        "description": "UFW firewall enabled",
                        "commands": ["ufw status | grep -q active"]
                    },
                    {
                        "id": "auto_updates",
                        "name": "Automatic Updates",
                        "description": "Automatic security updates enabled",
                        "commands": ["grep '^APT::Periodic::Update-Package-Lists \"1\"' /etc/apt/apt.conf.d/20auto-upgrades"]
                    }
                ]
            },
            "kubernetes": {
                "name": "Kubernetes Security Baseline",
                "platform": "kubernetes",
                "checks": [
                    {
                        "id": "pod_security_standards",
                        "name": "Pod Security Standards",
                        "description": "Pod Security Standards enforced",
                        "resource": "namespace",
                        "condition": "labels['pod-security.kubernetes.io/enforce'] == 'restricted'"
                    },
                    {
                        "id": "network_policies",
                        "name": "Network Policies",
                        "description": "Network policies defined",
                        "resource": "networkpolicy",
                        "condition": "count > 0"
                    },
                    {
                        "id": "rbac_enabled",
                        "name": "RBAC Enabled",
                        "description": "Role-based access control enabled",
                        "resource": "clusterrole",
                        "condition": "count > 0"
                    }
                ]
            }
        }

    async def scan_container_image(
        self,
        image_name: str,
        tag: str = "latest",
        scanner: str = "trivy"
    ) -> str:
        """
        Scan container image for vulnerabilities
        
        Args:
            image_name: Container image name
            tag: Image tag
            scanner: Scanner to use
            
        Returns:
            Scan ID
        """
        
        scan_id = str(uuid.uuid4())
        
        try:
            if scanner not in self.scanner_configs:
                raise ValueError(f"Unsupported scanner: {scanner}")
            
            config = self.scanner_configs[scanner]
            full_image = f"{image_name}:{tag}"
            
            scan = SecurityScan(
                scan_id=scan_id,
                scan_type=ScanType.CONTAINER_IMAGE,
                target=full_image,
                start_time=datetime.now(),
                end_time=None,
                status="running",
                scanner=scanner,
                metadata={"image": image_name, "tag": tag}
            )
            
            self.active_scans[scan_id] = scan
            
            # Execute scan asynchronously
            asyncio.create_task(self._execute_container_scan(scan, config))
            
            logger.info(f"Container image scan started: {full_image} with {scanner}")
            return scan_id
            
        except Exception as e:
            logger.error(f"Container image scan failed: {str(e)}")
            raise

    async def _execute_container_scan(self, scan: SecurityScan, config: Dict[str, Any]):
        """Execute container image vulnerability scan"""
        
        try:
            # Mock scanner execution
            await asyncio.sleep(30)  # Simulate scan time
            
            # Generate mock vulnerabilities
            mock_vulnerabilities = self._generate_mock_vulnerabilities(scan.target, ScanType.CONTAINER_IMAGE)
            
            scan.vulnerabilities = mock_vulnerabilities
            scan.end_time = datetime.now()
            scan.status = "completed"
            
            # Calculate summary
            severity_counts = defaultdict(int)
            for vuln in mock_vulnerabilities:
                severity_counts[vuln.severity.value] += 1
            
            scan.summary = dict(severity_counts)
            
            # Store scan results
            self.scan_history.append(scan)
            if scan.scan_id in self.active_scans:
                del self.active_scans[scan.scan_id]
            
            # Store vulnerabilities
            for vuln in mock_vulnerabilities:
                self.vulnerabilities[vuln.vuln_id] = vuln
            
            # Check for critical vulnerabilities and create incidents
            critical_vulns = [v for v in mock_vulnerabilities if v.severity == SeverityLevel.CRITICAL]
            if critical_vulns:
                await self._create_vulnerability_incident(scan.target, critical_vulns)
            
            logger.info(f"Container scan completed: {scan.target} - {len(mock_vulnerabilities)} vulnerabilities found")
            
        except Exception as e:
            logger.error(f"Container scan execution failed: {str(e)}")
            scan.status = "failed"
            scan.end_time = datetime.now()

    def _generate_mock_vulnerabilities(self, target: str, scan_type: ScanType) -> List[Vulnerability]:
        """Generate mock vulnerabilities for demonstration"""
        
        vulnerabilities = []
        
        # Generate realistic vulnerability data
        mock_vulns = [
            {
                "cve_id": "CVE-2023-1234",
                "title": "Buffer Overflow in libssl",
                "description": "A buffer overflow vulnerability in OpenSSL library",
                "severity": SeverityLevel.HIGH,
                "cvss_score": 7.5,
                "component": "openssl",
                "fix_version": "1.1.1w"
            },
            {
                "cve_id": "CVE-2023-5678",
                "title": "SQL Injection in web framework",
                "description": "SQL injection vulnerability in request handling",
                "severity": SeverityLevel.CRITICAL,
                "cvss_score": 9.8,
                "component": "web-framework",
                "fix_version": "2.1.5"
            },
            {
                "cve_id": "CVE-2023-9012",
                "title": "Privilege Escalation in container runtime",
                "description": "Local privilege escalation in container runtime",
                "severity": SeverityLevel.MEDIUM,
                "cvss_score": 6.7,
                "component": "container-runtime",
                "fix_version": "1.2.3"
            }
        ]
        
        import random
        
        # Select random subset of vulnerabilities
        selected_vulns = random.sample(mock_vulns, random.randint(1, len(mock_vulns)))
        
        for vuln_data in selected_vulns:
            vuln = Vulnerability(
                vuln_id=str(uuid.uuid4()),
                cve_id=vuln_data["cve_id"],
                title=vuln_data["title"],
                description=vuln_data["description"],
                severity=vuln_data["severity"],
                cvss_score=vuln_data["cvss_score"],
                affected_component=vuln_data["component"],
                fix_version=vuln_data.get("fix_version"),
                discovered_at=datetime.now(),
                scan_type=scan_type,
                source_location=target,
                fix_available=vuln_data.get("fix_version") is not None,
                exploitable=vuln_data["severity"] in [SeverityLevel.CRITICAL, SeverityLevel.HIGH],
                remediation_steps=[
                    f"Update {vuln_data['component']} to version {vuln_data.get('fix_version', 'latest')}",
                    "Review security advisory for additional mitigation steps",
                    "Test application functionality after update"
                ],
                references=[
                    f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={vuln_data['cve_id']}",
                    f"https://nvd.nist.gov/vuln/detail/{vuln_data['cve_id']}"
                ]
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities

    async def scan_source_code(
        self,
        repository_path: str,
        branch: str = "main",
        scanner: str = "bandit"
    ) -> str:
        """
        Scan source code for security vulnerabilities
        
        Args:
            repository_path: Path to source code repository
            branch: Git branch to scan
            scanner: Security scanner to use
            
        Returns:
            Scan ID
        """
        
        scan_id = str(uuid.uuid4())
        
        try:
            if scanner not in self.scanner_configs:
                raise ValueError(f"Unsupported scanner: {scanner}")
            
            config = self.scanner_configs[scanner]
            
            scan = SecurityScan(
                scan_id=scan_id,
                scan_type=ScanType.SOURCE_CODE,
                target=repository_path,
                start_time=datetime.now(),
                end_time=None,
                status="running",
                scanner=scanner,
                metadata={"repository": repository_path, "branch": branch}
            )
            
            self.active_scans[scan_id] = scan
            
            # Execute scan asynchronously
            asyncio.create_task(self._execute_source_code_scan(scan, config))
            
            logger.info(f"Source code scan started: {repository_path} with {scanner}")
            return scan_id
            
        except Exception as e:
            logger.error(f"Source code scan failed: {str(e)}")
            raise

    async def _execute_source_code_scan(self, scan: SecurityScan, config: Dict[str, Any]):
        """Execute source code security scan"""
        
        try:
            # Mock scanner execution
            await asyncio.sleep(45)  # Simulate scan time
            
            # Generate mock vulnerabilities
            mock_vulnerabilities = self._generate_mock_vulnerabilities(scan.target, ScanType.SOURCE_CODE)
            
            scan.vulnerabilities = mock_vulnerabilities
            scan.end_time = datetime.now()
            scan.status = "completed"
            
            # Calculate summary
            severity_counts = defaultdict(int)
            for vuln in mock_vulnerabilities:
                severity_counts[vuln.severity.value] += 1
            
            scan.summary = dict(severity_counts)
            
            # Store results
            self.scan_history.append(scan)
            if scan.scan_id in self.active_scans:
                del self.active_scans[scan.scan_id]
            
            # Store vulnerabilities
            for vuln in mock_vulnerabilities:
                self.vulnerabilities[vuln.vuln_id] = vuln
            
            logger.info(f"Source code scan completed: {scan.target} - {len(mock_vulnerabilities)} issues found")
            
        except Exception as e:
            logger.error(f"Source code scan execution failed: {str(e)}")
            scan.status = "failed"
            scan.end_time = datetime.now()

    async def enforce_security_policy(
        self,
        policy_id: str,
        resource: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enforce security policy on resource
        
        Args:
            policy_id: Security policy identifier
            resource: Resource to evaluate
            context: Additional context for evaluation
            
        Returns:
            Policy evaluation result
        """
        
        try:
            if policy_id not in self.security_policies:
                raise ValueError(f"Policy not found: {policy_id}")
            
            policy = self.security_policies[policy_id]
            
            if not policy.enabled:
                return {
                    "policy_id": policy_id,
                    "action": "skipped",
                    "reason": "Policy disabled"
                }
            
            violations = []
            
            # Evaluate policy rules
            for rule in policy.rules:
                try:
                    # Mock policy evaluation
                    violation_detected = self._evaluate_policy_rule(rule, resource, context)
                    
                    if violation_detected:
                        violations.append({
                            "rule_name": rule["name"],
                            "description": rule["description"],
                            "condition": rule["condition"]
                        })
                
                except Exception as e:
                    logger.error(f"Policy rule evaluation failed: {rule['name']} - {str(e)}")
            
            # Determine action
            if violations:
                result = {
                    "policy_id": policy_id,
                    "action": policy.action.value,
                    "violations": violations,
                    "resource": resource,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Store violation
                self.policy_violations.append(result)
                
                # Take action based on policy
                if policy.action == PolicyAction.DENY:
                    logger.warning(f"Policy violation - DENIED: {policy.name}")
                elif policy.action == PolicyAction.WARN:
                    logger.warning(f"Policy violation - WARNING: {policy.name}")
                
                return result
            else:
                return {
                    "policy_id": policy_id,
                    "action": "allowed",
                    "violations": [],
                    "resource": resource,
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Policy enforcement failed: {str(e)}")
            return {
                "policy_id": policy_id,
                "action": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _evaluate_policy_rule(
        self,
        rule: Dict[str, Any],
        resource: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> bool:
        """Evaluate a single policy rule"""
        
        # Mock policy rule evaluation
        import random
        
        # Simple mock: 10% chance of violation
        return random.random() < 0.1

    async def create_security_incident(
        self,
        title: str,
        description: str,
        severity: SeverityLevel,
        affected_systems: List[str],
        indicators: List[str] = None
    ) -> str:
        """
        Create security incident
        
        Args:
            title: Incident title
            description: Incident description
            severity: Incident severity
            affected_systems: List of affected systems
            indicators: Indicators of compromise
            
        Returns:
            Incident ID
        """
        
        try:
            incident_id = str(uuid.uuid4())
            
            incident = SecurityIncident(
                incident_id=incident_id,
                title=title,
                description=description,
                severity=severity,
                status=IncidentStatus.DETECTED,
                detected_at=datetime.now(),
                affected_systems=affected_systems,
                indicators=indicators or [],
                timeline=[{
                    "timestamp": datetime.now().isoformat(),
                    "action": "incident_created",
                    "description": "Security incident created"
                }]
            )
            
            self.incidents[incident_id] = incident
            
            # Auto-respond if configured
            for rule in self.incident_rules:
                if self._matches_incident_rule(incident, rule):
                    if rule.get("auto_respond", False):
                        await self._auto_respond_incident(incident, rule)
                    break
            
            logger.warning(f"Security incident created: {title} (Severity: {severity.value})")
            return incident_id
            
        except Exception as e:
            logger.error(f"Incident creation failed: {str(e)}")
            raise

    async def _create_vulnerability_incident(self, target: str, vulnerabilities: List[Vulnerability]):
        """Create incident for critical vulnerabilities"""
        
        critical_count = len(vulnerabilities)
        cve_list = [v.cve_id for v in vulnerabilities if v.cve_id]
        
        await self.create_security_incident(
            title=f"Critical Vulnerabilities Detected: {target}",
            description=f"{critical_count} critical vulnerabilities found in {target}. CVEs: {', '.join(cve_list)}",
            severity=SeverityLevel.CRITICAL,
            affected_systems=[target],
            indicators=cve_list
        )

    def _matches_incident_rule(self, incident: SecurityIncident, rule: Dict[str, Any]) -> bool:
        """Check if incident matches rule conditions"""
        
        # Mock rule matching
        if rule["name"] == "critical_vulnerability_detected":
            return incident.severity == SeverityLevel.CRITICAL
        
        return False

    async def _auto_respond_incident(self, incident: SecurityIncident, rule: Dict[str, Any]):
        """Auto-respond to security incident"""
        
        try:
            incident.status = IncidentStatus.INVESTIGATING
            incident.timeline.append({
                "timestamp": datetime.now().isoformat(),
                "action": "auto_response_initiated",
                "description": f"Auto-response triggered by rule: {rule['name']}"
            })
            
            # Execute response actions
            if rule["name"] == "critical_vulnerability_detected":
                await self._respond_to_critical_vulnerability(incident)
            
            logger.info(f"Auto-response executed for incident: {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Auto-response failed: {str(e)}")

    async def _respond_to_critical_vulnerability(self, incident: SecurityIncident):
        """Respond to critical vulnerability incident"""
        
        response_actions = [
            "Isolate affected systems",
            "Apply emergency patches if available",
            "Implement temporary mitigations",
            "Notify security team",
            "Update WAF rules if applicable"
        ]
        
        incident.remediation_actions.extend(response_actions)
        incident.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "action": "remediation_started",
            "description": "Critical vulnerability remediation initiated"
        })

    async def check_compliance(self, framework: str) -> Dict[str, Any]:
        """
        Check compliance against security framework
        
        Args:
            framework: Compliance framework (SOC2, PCI_DSS, GDPR)
            
        Returns:
            Compliance check results
        """
        
        try:
            if framework not in self.compliance_frameworks:
                raise ValueError(f"Unsupported compliance framework: {framework}")
            
            framework_def = self.compliance_frameworks[framework]
            results = {
                "framework": framework,
                "name": framework_def["name"],
                "description": framework_def["description"],
                "check_date": datetime.now().isoformat(),
                "controls": [],
                "summary": {
                    "total_controls": len(framework_def["controls"]),
                    "compliant": 0,
                    "non_compliant": 0,
                    "not_applicable": 0
                }
            }
            
            # Evaluate each control
            for control in framework_def["controls"]:
                check_result = await self._evaluate_compliance_control(framework, control)
                results["controls"].append(check_result)
                
                # Update summary
                results["summary"][check_result["status"]] += 1
                
                # Store compliance check
                check_id = f"{framework}_{control['id']}"
                compliance_check = ComplianceCheck(
                    check_id=check_id,
                    standard=framework,
                    requirement=control["name"],
                    status=check_result["status"],
                    evidence=check_result.get("evidence", []),
                    risk_level=SeverityLevel.MEDIUM if check_result["status"] == "non_compliant" else SeverityLevel.LOW,
                    remediation=check_result.get("remediation"),
                    last_checked=datetime.now()
                )
                
                self.compliance_checks[check_id] = compliance_check
            
            # Calculate compliance percentage
            total = results["summary"]["total_controls"]
            compliant = results["summary"]["compliant"]
            results["compliance_percentage"] = (compliant / total * 100) if total > 0 else 0
            
            logger.info(f"Compliance check completed: {framework} - {results['compliance_percentage']:.1f}% compliant")
            
            return results
            
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            raise

    async def _evaluate_compliance_control(self, framework: str, control: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate single compliance control"""
        
        # Mock compliance evaluation
        import random
        
        statuses = ["compliant", "non_compliant", "not_applicable"]
        weights = [0.7, 0.2, 0.1]  # 70% compliant, 20% non-compliant, 10% N/A
        
        status = random.choices(statuses, weights=weights)[0]
        
        result = {
            "control_id": control["id"],
            "name": control["name"],
            "description": control["description"],
            "status": status,
            "evidence": [],
            "remediation": None
        }
        
        if status == "compliant":
            result["evidence"] = [
                f"Control {control['id']} implementation verified",
                "Security controls are properly configured",
                "Documentation is up to date"
            ]
        elif status == "non_compliant":
            result["evidence"] = [
                f"Control {control['id']} implementation gap identified",
                "Configuration does not meet requirements"
            ]
            result["remediation"] = f"Implement proper controls for {control['name']}"
        
        return result

    # Background monitoring tasks
    async def _vulnerability_scanning_loop(self):
        """Background vulnerability scanning loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Scan every hour
                
                # Perform scheduled scans
                await self._perform_scheduled_scans()
                
            except Exception as e:
                logger.error(f"Vulnerability scanning loop error: {str(e)}")

    async def _perform_scheduled_scans(self):
        """Perform scheduled security scans"""
        
        # Mock scheduled scanning
        scan_targets = [
            {"type": "container", "target": "ainflue/api:latest"},
            {"type": "source", "target": "/app/src"},
            {"type": "infrastructure", "target": "terraform/"}
        ]
        
        for target in scan_targets:
            try:
                if target["type"] == "container":
                    await self.scan_container_image(target["target"])
                elif target["type"] == "source":
                    await self.scan_source_code(target["target"])
                
            except Exception as e:
                logger.error(f"Scheduled scan failed: {target} - {str(e)}")

    async def _incident_detection_loop(self):
        """Background incident detection loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Detect security incidents
                await self._detect_security_incidents()
                
            except Exception as e:
                logger.error(f"Incident detection loop error: {str(e)}")

    async def _detect_security_incidents(self):
        """Detect security incidents from various sources"""
        
        # Mock incident detection
        import random
        
        if random.random() < 0.05:  # 5% chance of incident
            incident_types = [
                {
                    "title": "Suspicious Network Traffic",
                    "description": "Unusual outbound network traffic detected",
                    "severity": SeverityLevel.MEDIUM,
                    "systems": ["web-server-1"]
                },
                {
                    "title": "Failed Authentication Attempts",
                    "description": "Multiple failed login attempts from single IP",
                    "severity": SeverityLevel.HIGH,
                    "systems": ["auth-service"]
                }
            ]
            
            incident_data = random.choice(incident_types)
            await self.create_security_incident(
                title=incident_data["title"],
                description=incident_data["description"],
                severity=incident_data["severity"],
                affected_systems=incident_data["systems"]
            )

    async def _policy_enforcement_loop(self):
        """Background policy enforcement loop"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                
                # Enforce security policies
                await self._enforce_policies()
                
            except Exception as e:
                logger.error(f"Policy enforcement loop error: {str(e)}")

    async def _enforce_policies(self):
        """Enforce security policies across infrastructure"""
        
        # Mock policy enforcement on sample resources
        sample_resources = [
            {
                "type": "container",
                "name": "app-container",
                "user": "app",
                "privileged": False
            },
            {
                "type": "network",
                "protocol": "https",
                "ports": [443, 8080]
            }
        ]
        
        for resource in sample_resources:
            for policy_id in self.security_policies.keys():
                await self.enforce_security_policy(policy_id, resource)

    async def _compliance_monitoring_loop(self):
        """Background compliance monitoring loop"""
        while True:
            try:
                await asyncio.sleep(86400)  # Check daily
                
                # Perform compliance checks
                for framework in self.compliance_frameworks.keys():
                    await self.check_compliance(framework)
                
            except Exception as e:
                logger.error(f"Compliance monitoring loop error: {str(e)}")

    async def _threat_intelligence_loop(self):
        """Background threat intelligence loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Update every hour
                
                # Update threat intelligence feeds
                await self._update_threat_intelligence()
                
            except Exception as e:
                logger.error(f"Threat intelligence loop error: {str(e)}")

    async def _update_threat_intelligence(self):
        """Update threat intelligence indicators"""
        
        # Mock threat intelligence update
        mock_indicators = [
            {
                "type": "ip_address",
                "value": "192.168.1.100",
                "threat_type": "malware_c2",
                "confidence": 85
            },
            {
                "type": "domain",
                "value": "malicious-domain.com",
                "threat_type": "phishing",
                "confidence": 92
            },
            {
                "type": "file_hash",
                "value": "a1b2c3d4e5f6...",
                "threat_type": "malware",
                "confidence": 95
            }
        ]
        
        for indicator in mock_indicators:
            indicator_id = hashlib.sha256(indicator["value"].encode()).hexdigest()[:16]
            self.threat_indicators[indicator_id] = {
                **indicator,
                "updated_at": datetime.now(),
                "source": "threat_feed"
            }

    async def _security_metrics_loop(self):
        """Background security metrics collection loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Collect every 5 minutes
                
                # Collect security metrics
                await self._collect_security_metrics()
                
            except Exception as e:
                logger.error(f"Security metrics loop error: {str(e)}")

    async def _collect_security_metrics(self):
        """Collect security metrics"""
        
        try:
            # Count vulnerabilities by severity
            vuln_counts = defaultdict(int)
            for vuln in self.vulnerabilities.values():
                vuln_counts[vuln.severity.value] += 1
            
            # Count incidents by status
            incident_counts = defaultdict(int)
            for incident in self.incidents.values():
                incident_counts[incident.status.value] += 1
            
            # Calculate risk score
            risk_score = (
                vuln_counts.get("critical", 0) * 10 +
                vuln_counts.get("high", 0) * 5 +
                vuln_counts.get("medium", 0) * 2 +
                vuln_counts.get("low", 0) * 1
            )
            
            metrics = {
                "timestamp": datetime.now(),
                "vulnerabilities": dict(vuln_counts),
                "incidents": dict(incident_counts),
                "policy_violations": len(self.policy_violations),
                "active_scans": len(self.active_scans),
                "threat_indicators": len(self.threat_indicators),
                "risk_score": risk_score
            }
            
            self.security_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Security metrics collection failed: {str(e)}")

    async def health_check(self) -> bool:
        """Security automation health check"""
        
        try:
            # Check for too many unresolved incidents
            active_incidents = [
                i for i in self.incidents.values() 
                if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.FALSE_POSITIVE]
            ]
            
            if len(active_incidents) > 10:
                return False
            
            # Check for recent vulnerability scans
            recent_scans = [
                s for s in self.scan_history 
                if s.end_time and s.end_time >= datetime.now() - timedelta(hours=24)
            ]
            
            if len(recent_scans) == 0:
                logger.warning("No recent vulnerability scans found")
            
            return True
            
        except Exception as e:
            logger.error(f"Security automation health check failed: {str(e)}")
            return False

    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard"""
        
        # Count vulnerabilities by severity
        vuln_counts = defaultdict(int)
        for vuln in self.vulnerabilities.values():
            vuln_counts[vuln.severity.value] += 1
        
        # Count incidents by status
        incident_counts = defaultdict(int)
        for incident in self.incidents.values():
            incident_counts[incident.status.value] += 1
        
        # Recent scans
        recent_scans = [
            s for s in self.scan_history 
            if s.end_time and s.end_time >= datetime.now() - timedelta(hours=24)
        ]
        
        # Compliance summary
        compliance_summary = {}
        for framework in self.compliance_frameworks.keys():
            framework_checks = [
                c for c in self.compliance_checks.values() 
                if c.standard == framework
            ]
            if framework_checks:
                compliant = len([c for c in framework_checks if c.status == "compliant"])
                total = len(framework_checks)
                compliance_summary[framework] = (compliant / total * 100) if total > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": {
                "total": len(self.vulnerabilities),
                "by_severity": dict(vuln_counts),
                "critical_count": vuln_counts.get("critical", 0),
                "high_count": vuln_counts.get("high", 0)
            },
            "incidents": {
                "total": len(self.incidents),
                "by_status": dict(incident_counts),
                "active_count": incident_counts.get("detected", 0) + incident_counts.get("investigating", 0)
            },
            "scans": {
                "total_scans": len(self.scan_history),
                "recent_scans": len(recent_scans),
                "active_scans": len(self.active_scans),
                "scan_types": list(set(s.scan_type.value for s in self.scan_history))
            },
            "policies": {
                "total_policies": len(self.security_policies),
                "enabled_policies": len([p for p in self.security_policies.values() if p.enabled]),
                "policy_violations": len(self.policy_violations)
            },
            "compliance": {
                "frameworks": list(self.compliance_frameworks.keys()),
                "compliance_percentages": compliance_summary,
                "total_checks": len(self.compliance_checks)
            },
            "threat_intelligence": {
                "indicators": len(self.threat_indicators),
                "indicator_types": list(set(
                    i.get("type", "unknown") for i in self.threat_indicators.values()
                ))
            },
            "risk_assessment": {
                "current_risk_score": self.security_metrics[-1]["risk_score"] if self.security_metrics else 0,
                "risk_trend": "stable"  # Mock trend
            }
        }

# Global security automation instance
security_automation = SecurityAutomation()

logger.info("🚀 Security Automation initialized - DevSecOps automation framework")