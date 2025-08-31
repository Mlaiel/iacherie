"""IA Influencer Agent - Pipeline Security Management System
Enterprise-Grade Security Scanning and Compliance for CI/CD Pipelines

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive security scanning and compliance management for CI/CD
pipelines, ensuring enterprise-grade security throughout the deployment process.

Features:
- Multi-layer security scanning (code, dependencies, containers, infrastructure)
- Vulnerability assessment and reporting
- Compliance validation and enforcement
- Security policy management
- Integration with security tools and platforms

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""
import asyncio
import logging
import json
import subprocess
import tempfile
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import re

class ScanType(Enum):
    """Security scan types"""    CODE_SECURITY = "code_security"
    DEPENDENCY_SCAN = "dependency_scan"
    CONTAINER_SCAN = "container_scan"
    INFRASTRUCTURE_SCAN = "infrastructure_scan"
    SECRETS_SCAN = "secrets_scan"
    COMPLIANCE_CHECK = "compliance_check"

class SeverityLevel(Enum):
    """Vulnerability severity levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ComplianceStandard(Enum):
    """Compliance standards"""    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    NIST = "nist"

@dataclass
class Vulnerability:
    """Vulnerability information"""    id: str
    title: str
    description: str
    severity: SeverityLevel
    cve_id: Optional[str] = None
    component: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    remediation: Optional[str] = None
    references: List[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []

@dataclass
class ScanResult:
    """Security scan result"""    scan_type: ScanType
    scan_id: str
    timestamp: datetime
    status: str
    vulnerabilities: List[Vulnerability]
    summary: Dict[str, int]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SecurityPolicy:
    """Security policy definition"""    name: str
    description: str
    enabled: bool
    severity_threshold: SeverityLevel
    allowed_vulnerability_count: Dict[SeverityLevel, int]
    compliance_standards: List[ComplianceStandard]
    exclusions: List[str] = None
    
    def __post_init__(self):
        if self.exclusions is None:
            self.exclusions = []

class CodeSecurityScanner:
    """Code security vulnerability scanner"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def scan_code(self, code_path: Path, 
                       scan_config: Optional[Dict[str, Any]] = None) -> ScanResult:
        """Scan code for security vulnerabilities"""        scan_id = self._generate_scan_id("code_security")
        vulnerabilities = []
        
        try:
            # Run Bandit for Python security issues
            bandit_result = await self._run_bandit_scan(code_path)
            vulnerabilities.extend(bandit_result)
            
            # Run Semgrep for additional security patterns
            semgrep_result = await self._run_semgrep_scan(code_path)
            vulnerabilities.extend(semgrep_result)
            
            # Custom security pattern matching
            custom_result = await self._run_custom_patterns(code_path)
            vulnerabilities.extend(custom_result)
            
            # Generate summary
            summary = self._generate_summary(vulnerabilities)
            
            return ScanResult(
                scan_type=ScanType.CODE_SECURITY,
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                metadata={"code_path": str(code_path)}
            )
            
        except Exception as e:
            self.logger.error(f"Code security scan failed: {str(e)}")
            return ScanResult(
                scan_type=ScanType.CODE_SECURITY,
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                status="failed",
                vulnerabilities=[],
                summary={},
                metadata={"error": str(e)}
            )
            
    async def _run_bandit_scan(self, code_path: Path) -> List[Vulnerability]:
        """Run Bandit security scanner"""        vulnerabilities = []
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_file = f.name
                
            cmd = [
                "bandit", "-r", str(code_path), 
                "-f", "json", "-o", output_file
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Parse results
            with open(output_file, 'r') as f:
                results = json.load(f)
                
            for issue in results.get('results', []):
                vulnerability = Vulnerability(
                    id=f"bandit-{issue['test_id']}",
                    title=issue['test_name'],
                    description=issue['issue_text'],
                    severity=self._map_bandit_severity(issue['issue_severity']),
                    component="code",
                    file_path=issue['filename'],
                    line_number=issue['line_number'],
                    remediation=issue.get('more_info', '')
                )
                vulnerabilities.append(vulnerability)
                
            # Cleanup
            Path(output_file).unlink(missing_ok=True)
            
        except Exception as e:
            self.logger.error(f"Bandit scan failed: {str(e)}")
            
        return vulnerabilities
        
    async def _run_semgrep_scan(self, code_path: Path) -> List[Vulnerability]:
        """Run Semgrep security scanner"""        vulnerabilities = []
        
        try:
            cmd = [
                "semgrep", "--config=auto", "--json", str(code_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                results = json.loads(stdout.decode())
                
                for finding in results.get('results', []):
                    vulnerability = Vulnerability(
                        id=f"semgrep-{finding['check_id']}",
                        title=finding['check_id'],
                        description=finding['message'],
                        severity=self._map_semgrep_severity(finding.get('severity', 'INFO')),
                        component="code",
                        file_path=finding['path'],
                        line_number=finding['start']['line'],
                        references=[finding.get('metadata', {}).get('reference', '')]
                    )
                    vulnerabilities.append(vulnerability)
                    
        except Exception as e:
            self.logger.error(f"Semgrep scan failed: {str(e)}")
            
        return vulnerabilities
        
    async def _run_custom_patterns(self, code_path: Path) -> List[Vulnerability]:
        """Run custom security pattern matching"""        vulnerabilities = []
        
        # Define custom security patterns
        patterns = {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*=\s*["\'].*%.*["\']'
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\(',
                r'exec\s*\('
            ]
        }
        
        try:
            for python_file in code_path.rglob("*.py"):
                if python_file.is_file():
                    content = python_file.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')
                    
                    for category, pattern_list in patterns.items():
                        for pattern in pattern_list:
                            for line_num, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    vulnerability = Vulnerability(
                                        id=f"custom-{category}-{hashlib.md5(line.encode()).hexdigest()[:8]}",
                                        title=f"Potential {category.replace('_', ' ').title()}",
                                        description=f"Detected potential {category.replace('_', ' ')} pattern",
                                        severity=SeverityLevel.HIGH,
                                        component="code",
                                        file_path=str(python_file.relative_to(code_path)),
                                        line_number=line_num,
                                        remediation=f"Review and secure {category.replace('_', ' ')} usage"
                                    )
                                    vulnerabilities.append(vulnerability)
                                    
        except Exception as e:
            self.logger.error(f"Custom pattern scan failed: {str(e)}")
            
        return vulnerabilities
        
    def _map_bandit_severity(self, severity: str) -> SeverityLevel:
        """Map Bandit severity to internal severity"""        mapping = {
            'HIGH': SeverityLevel.HIGH,
            'MEDIUM': SeverityLevel.MEDIUM,
            'LOW': SeverityLevel.LOW
        }
        return mapping.get(severity.upper(), SeverityLevel.MEDIUM)
        
    def _map_semgrep_severity(self, severity: str) -> SeverityLevel:
        """Map Semgrep severity to internal severity"""        mapping = {
            'ERROR': SeverityLevel.HIGH,
            'WARNING': SeverityLevel.MEDIUM,
            'INFO': SeverityLevel.LOW
        }
        return mapping.get(severity.upper(), SeverityLevel.MEDIUM)
        
    def _generate_scan_id(self, scan_type: str) -> str:
        """Generate unique scan ID"""        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{scan_type}_{timestamp}"
        
    def _generate_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, int]:
        """Generate vulnerability summary by severity"""        summary = {severity.value: 0 for severity in SeverityLevel}
        
        for vuln in vulnerabilities:
            summary[vuln.severity.value] += 1
            
        return summary

class DependencyScanner:
    """Dependency vulnerability scanner"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def scan_dependencies(self, project_path: Path,
                              scan_config: Optional[Dict[str, Any]] = None) -> ScanResult:
        """Scan project dependencies for vulnerabilities"""        scan_id = self._generate_scan_id("dependency_scan")
        vulnerabilities = []
        
        try:
            # Scan Python dependencies
            if (project_path / "requirements.txt").exists():
                python_vulns = await self._scan_python_dependencies(project_path)
                vulnerabilities.extend(python_vulns)
                
            # Scan Node.js dependencies
            if (project_path / "package.json").exists():
                nodejs_vulns = await self._scan_nodejs_dependencies(project_path)
                vulnerabilities.extend(nodejs_vulns)
                
            # Generate summary
            summary = self._generate_summary(vulnerabilities)
            
            return ScanResult(
                scan_type=ScanType.DEPENDENCY_SCAN,
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                metadata={"project_path": str(project_path)}
            )
            
        except Exception as e:
            self.logger.error(f"Dependency scan failed: {str(e)}")
            return ScanResult(
                scan_type=ScanType.DEPENDENCY_SCAN,
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                status="failed",
                vulnerabilities=[],
                summary={},
                metadata={"error": str(e)}
            )
            
    async def _scan_python_dependencies(self, project_path: Path) -> List[Vulnerability]:
        """Scan Python dependencies using Safety"""        vulnerabilities = []
        
        try:
            cmd = ["safety", "check", "--json", "--file", str(project_path / "requirements.txt")]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                results = json.loads(stdout.decode())
                
                for issue in results:
                    vulnerability = Vulnerability(
                        id=f"safety-{issue['id']}",
                        title=f"Vulnerable dependency: {issue['package_name']}",
                        description=issue['advisory'],
                        severity=SeverityLevel.HIGH,  # Safety issues are generally high priority
                        cve_id=issue.get('cve'),
                        component=f"{issue['package_name']}=={issue['analyzed_version']}",
                        remediation=f"Upgrade to version {issue.get('minimum_version', 'latest')}"
                    )
                    vulnerabilities.append(vulnerability)
                    
        except Exception as e:
            self.logger.error(f"Python dependency scan failed: {str(e)}")
            
        return vulnerabilities
        
    async def _scan_nodejs_dependencies(self, project_path: Path) -> List[Vulnerability]:
        """Scan Node.js dependencies using npm audit"""        vulnerabilities = []
        
        try:
            cmd = ["npm", "audit", "--json"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                results = json.loads(stdout.decode())
                
                for advisory_id, advisory in results.get('advisories', {}).items():
                    vulnerability = Vulnerability(
                        id=f"npm-{advisory_id}",
                        title=advisory['title'],
                        description=advisory['overview'],
                        severity=self._map_npm_severity(advisory['severity']),
                        cve_id=advisory.get('cves', [None])[0],
                        component=advisory['module_name'],
                        remediation=advisory.get('recommendation', 'Update dependency'),
                        references=advisory.get('references', [])
                    )
                    vulnerabilities.append(vulnerability)
                    
        except Exception as e:
            self.logger.error(f"Node.js dependency scan failed: {str(e)}")
            
        return vulnerabilities
        
    def _map_npm_severity(self, severity: str) -> SeverityLevel:
        """Map npm audit severity to internal severity"""        mapping = {
            'critical': SeverityLevel.CRITICAL,
            'high': SeverityLevel.HIGH,
            'moderate': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
            'info': SeverityLevel.INFO
        }
        return mapping.get(severity.lower(), SeverityLevel.MEDIUM)
        
    def _generate_scan_id(self, scan_type: str) -> str:
        """Generate unique scan ID"""        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{scan_type}_{timestamp}"
        
    def _generate_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, int]:
        """Generate vulnerability summary by severity"""        summary = {severity.value: 0 for severity in SeverityLevel}
        
        for vuln in vulnerabilities:
            summary[vuln.severity.value] += 1
            
        return summary

class ContainerScanner:
    """Container image vulnerability scanner"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def scan_container(self, image_name: str,
                           scan_config: Optional[Dict[str, Any]] = None) -> ScanResult:
        """Scan container image for vulnerabilities"""        scan_id = self._generate_scan_id("container_scan")
        vulnerabilities = []
        
        try:
            # Use Trivy for container scanning
            trivy_vulns = await self._scan_with_trivy(image_name)
            vulnerabilities.extend(trivy_vulns)
            
            # Generate summary
            summary = self._generate_summary(vulnerabilities)
            
            return ScanResult(
                scan_type=ScanType.CONTAINER_SCAN,
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                metadata={"image_name": image_name}
            )
            
        except Exception as e:
            self.logger.error(f"Container scan failed: {str(e)}")
            return ScanResult(
                scan_type=ScanType.CONTAINER_SCAN,
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                status="failed",
                vulnerabilities=[],
                summary={},
                metadata={"error": str(e), "image_name": image_name}
            )
            
    async def _scan_with_trivy(self, image_name: str) -> List[Vulnerability]:
        """Scan container with Trivy"""        vulnerabilities = []
        
        try:
            cmd = ["trivy", "image", "--format", "json", image_name]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                results = json.loads(stdout.decode())
                
                for result in results.get('Results', []):
                    for vuln in result.get('Vulnerabilities', []):
                        vulnerability = Vulnerability(
                            id=f"trivy-{vuln['VulnerabilityID']}",
                            title=vuln['Title'],
                            description=vuln.get('Description', ''),
                            severity=self._map_trivy_severity(vuln.get('Severity', 'UNKNOWN')),
                            cve_id=vuln['VulnerabilityID'],
                            component=f"{vuln.get('PkgName', '')}@{vuln.get('InstalledVersion', '')}",
                            remediation=f"Update to version {vuln.get('FixedVersion', 'latest')}" if vuln.get('FixedVersion') else "No fix available",
                            references=vuln.get('References', [])
                        )
                        vulnerabilities.append(vulnerability)
                        
        except Exception as e:
            self.logger.error(f"Trivy scan failed: {str(e)}")
            
        return vulnerabilities
        
    def _map_trivy_severity(self, severity: str) -> SeverityLevel:
        """Map Trivy severity to internal severity"""        mapping = {
            'CRITICAL': SeverityLevel.CRITICAL,
            'HIGH': SeverityLevel.HIGH,
            'MEDIUM': SeverityLevel.MEDIUM,
            'LOW': SeverityLevel.LOW,
            'UNKNOWN': SeverityLevel.INFO
        }
        return mapping.get(severity.upper(), SeverityLevel.MEDIUM)
        
    def _generate_scan_id(self, scan_type: str) -> str:
        """Generate unique scan ID"""        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{scan_type}_{timestamp}"
        
    def _generate_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, int]:
        """Generate vulnerability summary by severity"""        summary = {severity.value: 0 for severity in SeverityLevel}
        
        for vuln in vulnerabilities:
            summary[vuln.severity.value] += 1
            
        return summary

class SecurityPolicyManager:
    """Security policy management and enforcement"""    
    def __init__(self, policies_dir: Optional[Path] = None):
        self.policies_dir = policies_dir or Path(__file__).parent / "security_policies"
        self.policies_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Load security policies
        self.policies: Dict[str, SecurityPolicy] = {}
        self._load_policies()
        
    def _load_policies(self):
        """Load security policies from configuration files"""        # Create default policies if they don't exist
        self._create_default_policies()
        
        # Load policies from files
        for policy_file in self.policies_dir.glob("*.yaml"):
            try:
                with open(policy_file, 'r') as f:
                    policy_data = yaml.safe_load(f)
                    
                policy = SecurityPolicy(
                    name=policy_data['name'],
                    description=policy_data['description'],
                    enabled=policy_data.get('enabled', True),
                    severity_threshold=SeverityLevel(policy_data['severity_threshold']),
                    allowed_vulnerability_count={
                        SeverityLevel(k): v for k, v in policy_data['allowed_vulnerability_count'].items()
                    },
                    compliance_standards=[
                        ComplianceStandard(std) for std in policy_data.get('compliance_standards', [])
                    ],
                    exclusions=policy_data.get('exclusions', [])
                )
                
                self.policies[policy.name] = policy
                self.logger.info(f"Loaded security policy: {policy.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load policy {policy_file}: {str(e)}")
                
    def _create_default_policies(self):
        """Create default security policies"""        default_policies = {
            'development': {
                'name': 'development',
                'description': 'Development environment security policy',
                'enabled': True,
                'severity_threshold': 'high',
                'allowed_vulnerability_count': {
                    'critical': 0,
                    'high': 5,
                    'medium': 10,
                    'low': 20,
                    'info': 100
                },
                'compliance_standards': ['gdpr'],
                'exclusions': ['test-*', '*-test.py']
            },
            'staging': {
                'name': 'staging',
                'description': 'Staging environment security policy',
                'enabled': True,
                'severity_threshold': 'medium',
                'allowed_vulnerability_count': {
                    'critical': 0,
                    'high': 2,
                    'medium': 5,
                    'low': 10,
                    'info': 50
                },
                'compliance_standards': ['gdpr', 'soc2'],
                'exclusions': ['test-*']
            },
            'production': {
                'name': 'production',
                'description': 'Production environment security policy',
                'enabled': True,
                'severity_threshold': 'low',
                'allowed_vulnerability_count': {
                    'critical': 0,
                    'high': 0,
                    'medium': 2,
                    'low': 5,
                    'info': 20
                },
                'compliance_standards': ['gdpr', 'soc2', 'iso27001'],
                'exclusions': []
            }
        }
        
        for policy_name, policy_data in default_policies.items():
            policy_file = self.policies_dir / f"{policy_name}.yaml"
            if not policy_file.exists():
                with open(policy_file, 'w') as f:
                    yaml.dump(policy_data, f, default_flow_style=False)
                self.logger.info(f"Created default security policy: {policy_name}")
                
    def evaluate_scan_results(self, scan_results: List[ScanResult], 
                            policy_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate scan results against security policy"""        if policy_name not in self.policies:
            raise ValueError(f"Security policy not found: {policy_name}")
            
        policy = self.policies[policy_name]
        if not policy.enabled:
            return True, {"status": "policy_disabled"}
            
        evaluation_result = {
            "policy_name": policy_name,
            "compliance_check": True,
            "violations": [],
            "summary": {
                "total_vulnerabilities": 0,
                "by_severity": {severity.value: 0 for severity in SeverityLevel},
                "by_scan_type": {}
            }
        }
        
        # Aggregate vulnerabilities from all scan results
        all_vulnerabilities = []
        for scan_result in scan_results:
            all_vulnerabilities.extend(scan_result.vulnerabilities)
            evaluation_result["summary"]["by_scan_type"][scan_result.scan_type.value] = len(scan_result.vulnerabilities)
            
        # Count vulnerabilities by severity
        severity_counts = {severity.value: 0 for severity in SeverityLevel}
        for vuln in all_vulnerabilities:
            severity_counts[vuln.severity.value] += 1
            
        evaluation_result["summary"]["total_vulnerabilities"] = len(all_vulnerabilities)
        evaluation_result["summary"]["by_severity"] = severity_counts
        
        # Check against policy thresholds
        for severity, count in severity_counts.items():
            severity_level = SeverityLevel(severity)
            allowed_count = policy.allowed_vulnerability_count.get(severity_level, 0)
            
            if count > allowed_count:
                evaluation_result["compliance_check"] = False
                evaluation_result["violations"].append({
                    "type": "vulnerability_threshold_exceeded",
                    "severity": severity,
                    "found": count,
                    "allowed": allowed_count,
                    "message": f"Found {count} {severity} vulnerabilities, policy allows {allowed_count}"
                })
                
        # Check minimum severity threshold
        critical_severities = [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        if policy.severity_threshold in [SeverityLevel.MEDIUM, SeverityLevel.LOW]:
            critical_severities.append(SeverityLevel.MEDIUM)
        if policy.severity_threshold == SeverityLevel.LOW:
            critical_severities.append(SeverityLevel.LOW)
            
        blocking_vulnerabilities = [
            vuln for vuln in all_vulnerabilities 
            if vuln.severity in critical_severities
        ]
        
        if blocking_vulnerabilities:
            evaluation_result["violations"].append({
                "type": "blocking_vulnerabilities",
                "count": len(blocking_vulnerabilities),
                "threshold": policy.severity_threshold.value,
                "message": f"Found {len(blocking_vulnerabilities)} vulnerabilities above threshold {policy.severity_threshold.value}"
            })
            
        return evaluation_result["compliance_check"], evaluation_result

class PipelineSecurityManager:
    """    Comprehensive Pipeline Security Management System
    
    Provides enterprise-grade security scanning and compliance management with:
    - Multi-layer security scanning (code, dependencies, containers, infrastructure)
    - Vulnerability assessment and reporting
    - Security policy enforcement
    - Compliance validation
    - Integration with security tools and platforms
    """    
    def __init__(self, policies_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize scanners
        self.code_scanner = CodeSecurityScanner()
        self.dependency_scanner = DependencyScanner()
        self.container_scanner = ContainerScanner()
        
        # Initialize policy manager
        self.policy_manager = SecurityPolicyManager(policies_dir)
        
        # Scan history
        self.scan_history: List[ScanResult] = []
        
    async def run_comprehensive_security_scan(self, 
                                            project_path: Path,
                                            image_name: Optional[str] = None,
                                            policy_name: str = "development") -> Dict[str, Any]:
        """Run comprehensive security scan across all layers"""        scan_results = []
        
        try:
            self.logger.info("Starting comprehensive security scan")
            
            # Code security scan
            self.logger.info("Running code security scan")
            code_result = await self.code_scanner.scan_code(project_path)
            scan_results.append(code_result)
            self.scan_history.append(code_result)
            
            # Dependency scan
            self.logger.info("Running dependency vulnerability scan")
            dep_result = await self.dependency_scanner.scan_dependencies(project_path)
            scan_results.append(dep_result)
            self.scan_history.append(dep_result)
            
            # Container scan (if image provided)
            if image_name:
                self.logger.info(f"Running container security scan for {image_name}")
                container_result = await self.container_scanner.scan_container(image_name)
                scan_results.append(container_result)
                self.scan_history.append(container_result)
                
            # Evaluate against security policy
            self.logger.info(f"Evaluating results against policy: {policy_name}")
            compliance_status, evaluation = self.policy_manager.evaluate_scan_results(
                scan_results, policy_name
            )
            
            # Generate comprehensive report
            report = {
                "scan_timestamp": datetime.utcnow().isoformat(),
                "project_path": str(project_path),
                "image_name": image_name,
                "policy_name": policy_name,
                "compliance_status": compliance_status,
                "scan_results": [asdict(result) for result in scan_results],
                "policy_evaluation": evaluation,
                "recommendations": self._generate_recommendations(scan_results)
            }
            
            self.logger.info(f"Security scan completed. Compliance: {'PASS' if compliance_status else 'FAIL'}")
            return report
            
        except Exception as e:
            self.logger.error(f"Comprehensive security scan failed: {str(e)}")
            return {
                "scan_timestamp": datetime.utcnow().isoformat(),
                "status": "failed",
                "error": str(e),
                "compliance_status": False
            }
            
    def _generate_recommendations(self, scan_results: List[ScanResult]) -> List[str]:
        """Generate security recommendations based on scan results"""        recommendations = []
        
        for result in scan_results:
            if result.vulnerabilities:
                # Get top vulnerabilities by severity
                critical_vulns = [v for v in result.vulnerabilities if v.severity == SeverityLevel.CRITICAL]
                high_vulns = [v for v in result.vulnerabilities if v.severity == SeverityLevel.HIGH]
                
                if critical_vulns:
                    recommendations.append(
                        f"CRITICAL: Address {len(critical_vulns)} critical vulnerabilities in {result.scan_type.value}"
                    )
                    
                if high_vulns:
                    recommendations.append(
                        f"HIGH: Address {len(high_vulns)} high-severity vulnerabilities in {result.scan_type.value}"
                    )
                    
                # Specific recommendations by scan type
                if result.scan_type == ScanType.DEPENDENCY_SCAN:
                    recommendations.append("Update dependencies to latest secure versions")
                elif result.scan_type == ScanType.CODE_SECURITY:
                    recommendations.append("Review and fix security issues in source code")
                elif result.scan_type == ScanType.CONTAINER_SCAN:
                    recommendations.append("Use minimal base images and keep them updated")
                    
        if not recommendations:
            recommendations.append("No critical security issues found - maintain current security practices")
            
        return recommendations
        
    def get_scan_history(self, scan_type: Optional[ScanType] = None,
                        days: int = 30) -> List[ScanResult]:
        """Get scan history filtered by type and time range"""        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        filtered_results = [
            result for result in self.scan_history
            if result.timestamp >= cutoff_date
        ]
        
        if scan_type:
            filtered_results = [
                result for result in filtered_results
                if result.scan_type == scan_type
            ]
            
        return filtered_results
        
    def generate_security_report(self, environment: str = "all",
                               days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive security report"""        scan_history = self.get_scan_history(days=days)
        
        # Aggregate statistics
        total_scans = len(scan_history)
        vulnerability_counts = {severity.value: 0 for severity in SeverityLevel}
        scan_type_counts = {scan_type.value: 0 for scan_type in ScanType}
        
        for scan_result in scan_history:
            scan_type_counts[scan_result.scan_type.value] += 1
            for vuln in scan_result.vulnerabilities:
                vulnerability_counts[vuln.severity.value] += 1
                
        # Calculate trends (simplified)
        recent_scans = [s for s in scan_history if s.timestamp >= datetime.utcnow() - timedelta(days=7)]
        older_scans = [s for s in scan_history if s.timestamp < datetime.utcnow() - timedelta(days=7)]
        
        recent_vuln_count = sum(len(s.vulnerabilities) for s in recent_scans)
        older_vuln_count = sum(len(s.vulnerabilities) for s in older_scans)
        
        trend = "improving" if recent_vuln_count < older_vuln_count else "concerning" if recent_vuln_count > older_vuln_count else "stable"
        
        return {
            "report_timestamp": datetime.utcnow().isoformat(),
            "period_days": days,
            "environment": environment,
            "summary": {
                "total_scans": total_scans,
                "total_vulnerabilities": sum(vulnerability_counts.values()),
                "vulnerability_by_severity": vulnerability_counts,
                "scans_by_type": scan_type_counts,
                "security_trend": trend
            },
            "recent_activity": {
                "scans_last_7_days": len(recent_scans),
                "vulnerabilities_last_7_days": recent_vuln_count
            },
            "top_vulnerabilities": self._get_top_vulnerabilities(scan_history),
            "recommendations": self._generate_recommendations(scan_history)
        }
        
    def _get_top_vulnerabilities(self, scan_results: List[ScanResult], 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """Get top vulnerabilities by severity and frequency"""        vulnerability_counts = {}
        
        for result in scan_results:
            for vuln in result.vulnerabilities:
                key = (vuln.title, vuln.severity.value)
                if key not in vulnerability_counts:
                    vulnerability_counts[key] = {
                        "title": vuln.title,
                        "severity": vuln.severity.value,
                        "count": 0,
                        "latest_occurrence": vuln.id
                    }
                vulnerability_counts[key]["count"] += 1
                
        # Sort by severity and count
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        
        sorted_vulns = sorted(
            vulnerability_counts.values(),
            key=lambda x: (severity_order.get(x["severity"], 0), x["count"]),
            reverse=True
        )
        
        return sorted_vulns[:limit]

# Global security manager instance
security_manager = PipelineSecurityManager()
