"""🛡️ Penetration Testing Coordinator - Ainflue Platform
================================================================
Expert: SECURITY_ENGINEER + PENETRATION_TESTER + DEVOPS_ENGINEER + QUALITY_LEAD
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Advanced penetration testing coordination system that orchestrates automated
security testing, vulnerability assessment, and security compliance validation.
================================================================
"""

import asyncio
import json
import logging
import subprocess
import time
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import xml.etree.ElementTree as ET
import concurrent.futures
import requests
import nmap
import socket
from urllib.parse import urljoin, urlparse

# Security testing libraries
try:
    import sqlmap
    HAS_SQLMAP = True
except ImportError:
    HAS_SQLMAP = False

try:
    import wapiti
    HAS_WAPITI = True
except ImportError:
    HAS_WAPITI = False

logger = logging.getLogger(__name__)

class PenetrationTestType(Enum):
    """Types of penetration tests"""
    NETWORK_SCAN = "network_scan"
    PORT_SCAN = "port_scan"
    VULNERABILITY_SCAN = "vulnerability_scan"
    WEB_APPLICATION_SCAN = "web_application_scan"
    SQL_INJECTION_TEST = "sql_injection_test"
    XSS_TEST = "xss_test"
    CSRF_TEST = "csrf_test"
    AUTHENTICATION_BYPASS = "authentication_bypass"
    AUTHORIZATION_TEST = "authorization_test"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    FILE_UPLOAD_TEST = "file_upload_test"
    API_SECURITY_TEST = "api_security_test"
    SSL_TLS_TEST = "ssl_tls_test"
    INFORMATION_DISCLOSURE = "information_disclosure"
    SESSION_MANAGEMENT = "session_management"

class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"     # 9.0-10.0
    HIGH = "high"            # 7.0-8.9
    MEDIUM = "medium"        # 4.0-6.9
    LOW = "low"             # 0.1-3.9
    INFO = "info"           # 0.0

class TestStatus(Enum):
    """Penetration test status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class PenetrationTestTarget:
    """Target for penetration testing"""
    target_id: str
    name: str
    target_type: str  # "web_app", "api", "network", "mobile_app"
    base_url: Optional[str] = None
    ip_address: Optional[str] = None
    port_range: Optional[str] = None
    authentication: Dict[str, Any] = field(default_factory=dict)
    scope_restrictions: List[str] = field(default_factory=list)
    excluded_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Vulnerability:
    """Security vulnerability finding"""
    vulnerability_id: str
    name: str
    severity: VulnerabilitySeverity
    cvss_score: float
    description: str
    location: str
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    false_positive: bool = False
    verified: bool = False
    cve_ids: List[str] = field(default_factory=list)

@dataclass
class PenetrationTestResult:
    """Result of a penetration test"""
    test_id: str
    test_type: PenetrationTestType
    target: PenetrationTestTarget
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    scan_summary: Dict[str, Any] = field(default_factory=dict)
    tool_output: str = ""
    error_message: Optional[str] = None
    coverage_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class PenetrationTestSuite:
    """Collection of penetration tests"""
    suite_id: str
    name: str
    description: str
    targets: List[PenetrationTestTarget]
    test_types: List[PenetrationTestType]
    test_results: List[PenetrationTestResult] = field(default_factory=list)
    schedule: Optional[str] = None
    notification_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityAssessmentReport:
    """Comprehensive security assessment report"""
    assessment_id: str
    assessment_name: str
    targets_assessed: int
    total_tests: int
    completed_tests: int
    failed_tests: int
    total_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    risk_score: float
    compliance_score: float
    test_results: List[PenetrationTestResult]
    executive_summary: str
    technical_findings: List[Dict[str, Any]]
    remediation_roadmap: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class PenetrationTestingCoordinator:
    """
    Coordinates automated penetration testing and security assessments
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize penetration testing coordinator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.config = self._load_config()
        self.test_suites: Dict[str, PenetrationTestSuite] = {}
        self.active_tests: Dict[str, PenetrationTestResult] = {}
        
        # Tools configuration
        self.tools_config = self._initialize_tools_config()
        
        # Reports directory
        self.reports_dir = self.project_root / "security_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize default test targets
        self._initialize_platform_targets()

    def _load_config(self) -> Dict[str, Any]:
        """Load penetration testing configuration"""
        try:
            config_file = self.project_root / "config" / "pentest_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load pentest config: {e}")
        
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default penetration testing configuration"""
        return {
            "default_timeouts": {
                "network_scan": 300,
                "web_app_scan": 1800,
                "vulnerability_scan": 3600
            },
            "severity_thresholds": {
                "critical": 9.0,
                "high": 7.0,
                "medium": 4.0,
                "low": 0.1
            },
            "test_scope": {
                "include_subdomains": False,
                "max_scan_depth": 5,
                "max_concurrent_tests": 3,
                "rate_limiting": True
            },
            "reporting": {
                "auto_generate": True,
                "include_false_positives": False,
                "detailed_evidence": True
            },
            "compliance_frameworks": [
                "OWASP_TOP_10",
                "CWE_TOP_25",
                "NIST_CYBERSECURITY_FRAMEWORK"
            ]
        }

    def _initialize_tools_config(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security testing tools configuration"""
        return {
            "nmap": {
                "enabled": True,
                "path": "nmap",
                "default_args": ["-sS", "-sV", "-O", "--script=vuln"]
            },
            "nikto": {
                "enabled": True,
                "path": "nikto",
                "default_args": ["-h", "{target}", "-Format", "xml"]
            },
            "sqlmap": {
                "enabled": HAS_SQLMAP,
                "path": "sqlmap",
                "default_args": ["--batch", "--level=3", "--risk=2"]
            },
            "dirb": {
                "enabled": True,
                "path": "dirb",
                "wordlist": "/usr/share/dirb/wordlists/common.txt"
            },
            "sslyze": {
                "enabled": True,
                "path": "sslyze",
                "default_args": ["--regular"]
            },
            "zap": {
                "enabled": True,
                "path": "zap-cli",
                "default_args": ["--spider", "--ajax-spider", "--active-scan"]
            }
        }

    def _initialize_platform_targets(self):
        """Initialize default targets for Ainflue platform"""
        
        # Main API Target
        self.register_target(PenetrationTestTarget(
            target_id="ainflue_main_api",
            name="Ainflue Main API",
            target_type="api",
            base_url="http://localhost:8000",
            authentication={
                "type": "bearer_token",
                "test_credentials": {
                    "username": "pentest_user",
                    "password": "test_password"
                }
            },
            scope_restrictions=["/api/v1/*"],
            excluded_paths=["/api/v1/admin/*", "/api/v1/internal/*"],
            metadata={"critical": True, "public_facing": True}
        ))
        
        # Authentication Service
        self.register_target(PenetrationTestTarget(
            target_id="auth_service",
            name="Authentication Service",
            target_type="web_app",
            base_url="http://localhost:8001",
            scope_restrictions=["/auth/*", "/oauth/*"],
            metadata={"critical": True, "contains_pii": True}
        ))
        
        # Content Protection Service
        self.register_target(PenetrationTestTarget(
            target_id="content_protection",
            name="Content Protection Service",
            target_type="api",
            base_url="http://localhost:8002",
            scope_restrictions=["/protection/*"],
            metadata={"critical": True, "ai_service": True}
        ))
        
        # Payment Service
        self.register_target(PenetrationTestTarget(
            target_id="payment_service",
            name="Payment Service",
            target_type="api",
            base_url="http://localhost:8005",
            scope_restrictions=["/payment/*"],
            excluded_paths=["/payment/admin/*"],
            metadata={"critical": True, "pci_dss": True}
        ))
        
        # Network Infrastructure
        self.register_target(PenetrationTestTarget(
            target_id="network_infrastructure",
            name="Network Infrastructure",
            target_type="network",
            ip_address="127.0.0.1",
            port_range="1-65535",
            metadata={"scan_type": "infrastructure"}
        ))

    def register_target(self, target: PenetrationTestTarget):
        """Register a penetration testing target"""
        if not hasattr(self, 'targets'):
            self.targets: Dict[str, PenetrationTestTarget] = {}
        
        self.targets[target.target_id] = target
        self.logger.info(f"Registered penetration test target: {target.name}")

    def create_test_suite(self, suite_id: str, name: str, description: str,
                         target_ids: List[str], test_types: List[PenetrationTestType]) -> PenetrationTestSuite:
        """Create a penetration test suite"""
        targets = [self.targets[tid] for tid in target_ids if tid in self.targets]
        
        suite = PenetrationTestSuite(
            suite_id=suite_id,
            name=name,
            description=description,
            targets=targets,
            test_types=test_types
        )
        
        self.test_suites[suite_id] = suite
        self.logger.info(f"Created penetration test suite: {name}")
        return suite

    async def run_security_assessment(self, suite_id: Optional[str] = None,
                                     target_ids: Optional[List[str]] = None,
                                     test_types: Optional[List[PenetrationTestType]] = None) -> SecurityAssessmentReport:
        """Run comprehensive security assessment"""
        assessment_id = f"security_assessment_{int(time.time())}"
        start_time = time.time()
        
        self.logger.info(f"Starting security assessment: {assessment_id}")
        
        try:
            # Determine targets and tests to run
            if suite_id and suite_id in self.test_suites:
                suite = self.test_suites[suite_id]
                targets = suite.targets
                test_types_to_run = test_types or suite.test_types
            else:
                targets = [self.targets[tid] for tid in (target_ids or list(self.targets.keys()))]
                test_types_to_run = test_types or list(PenetrationTestType)
            
            # Execute tests
            all_test_results = []
            for target in targets:
                target_results = await self._run_target_tests(target, test_types_to_run)
                all_test_results.extend(target_results)
            
            # Generate comprehensive report
            report = await self._generate_security_assessment_report(
                assessment_id, targets, all_test_results, time.time() - start_time
            )
            
            # Save report
            await self._save_assessment_report(report)
            
            self.logger.info(
                f"Security assessment completed. "
                f"Vulnerabilities found: {report.total_vulnerabilities}, "
                f"Risk score: {report.risk_score:.1f}/100"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Security assessment failed: {e}")
            raise

    async def _run_target_tests(self, target: PenetrationTestTarget,
                              test_types: List[PenetrationTestType]) -> List[PenetrationTestResult]:
        """Run all specified tests against a target"""
        results = []
        
        for test_type in test_types:
            try:
                self.logger.info(f"Running {test_type.value} on {target.name}")
                result = await self._execute_single_test(target, test_type)
                results.append(result)
                
                # Store active test
                self.active_tests[result.test_id] = result
                
            except Exception as e:
                self.logger.error(f"Test {test_type.value} failed on {target.name}: {e}")
                
                # Create error result
                error_result = PenetrationTestResult(
                    test_id=f"error_{test_type.value}_{target.target_id}_{int(time.time())}",
                    test_type=test_type,
                    target=target,
                    status=TestStatus.FAILED,
                    start_time=datetime.utcnow(),
                    error_message=str(e)
                )
                results.append(error_result)
        
        return results

    async def _execute_single_test(self, target: PenetrationTestTarget,
                                 test_type: PenetrationTestType) -> PenetrationTestResult:
        """Execute a single penetration test"""
        test_id = f"{test_type.value}_{target.target_id}_{int(time.time())}"
        start_time = datetime.utcnow()
        
        result = PenetrationTestResult(
            test_id=test_id,
            test_type=test_type,
            target=target,
            status=TestStatus.RUNNING,
            start_time=start_time
        )
        
        try:
            # Route to appropriate test method
            if test_type == PenetrationTestType.NETWORK_SCAN:
                await self._run_network_scan(result)
            elif test_type == PenetrationTestType.PORT_SCAN:
                await self._run_port_scan(result)
            elif test_type == PenetrationTestType.WEB_APPLICATION_SCAN:
                await self._run_web_application_scan(result)
            elif test_type == PenetrationTestType.SQL_INJECTION_TEST:
                await self._run_sql_injection_test(result)
            elif test_type == PenetrationTestType.XSS_TEST:
                await self._run_xss_test(result)
            elif test_type == PenetrationTestType.SSL_TLS_TEST:
                await self._run_ssl_tls_test(result)
            elif test_type == PenetrationTestType.API_SECURITY_TEST:
                await self._run_api_security_test(result)
            else:
                # Generic vulnerability scan
                await self._run_generic_vulnerability_scan(result)
            
            result.status = TestStatus.COMPLETED
            result.end_time = datetime.utcnow()
            result.duration = (result.end_time - result.start_time).total_seconds()
            
        except Exception as e:
            result.status = TestStatus.FAILED
            result.end_time = datetime.utcnow()
            result.error_message = str(e)
            result.duration = (result.end_time - result.start_time).total_seconds()
        
        return result

    async def _run_network_scan(self, result: PenetrationTestResult):
        """Run network scan using nmap"""
        target = result.target
        
        if not target.ip_address:
            raise ValueError("Network scan requires IP address")
        
        try:
            nm = nmap.PortScanner()
            
            # Determine scan range
            scan_range = target.port_range or "1-1000"
            
            # Perform scan
            scan_result = nm.scan(
                hosts=target.ip_address,
                ports=scan_range,
                arguments="-sS -sV -O --script=vuln"
            )
            
            # Parse results
            vulnerabilities = self._parse_nmap_results(scan_result, target)
            result.vulnerabilities.extend(vulnerabilities)
            
            # Update scan summary
            result.scan_summary = {
                "hosts_scanned": len(scan_result.get("scan", {})),
                "open_ports": sum(
                    len([port for port, info in host_info.get("tcp", {}).items() 
                         if info.get("state") == "open"])
                    for host_info in scan_result.get("scan", {}).values()
                ),
                "services_detected": sum(
                    len([port for port, info in host_info.get("tcp", {}).items() 
                         if info.get("product")])
                    for host_info in scan_result.get("scan", {}).values()
                )
            }
            
        except Exception as e:
            raise Exception(f"Network scan failed: {e}")

    def _parse_nmap_results(self, scan_result: Dict[str, Any],
                           target: PenetrationTestTarget) -> List[Vulnerability]:
        """Parse nmap scan results for vulnerabilities"""
        vulnerabilities = []
        
        for host, host_info in scan_result.get("scan", {}).items():
            # Check for open ports with known vulnerabilities
            tcp_ports = host_info.get("tcp", {})
            
            for port, port_info in tcp_ports.items():
                if port_info.get("state") == "open":
                    service = port_info.get("product", "unknown")
                    version = port_info.get("version", "unknown")
                    
                    # Check for common vulnerable services
                    if self._is_vulnerable_service(service, version):
                        vuln = Vulnerability(
                            vulnerability_id=f"open_port_{host}_{port}",
                            name=f"Potentially Vulnerable Service: {service}",
                            severity=VulnerabilitySeverity.MEDIUM,
                            cvss_score=5.0,
                            description=f"Open port {port} running {service} {version}",
                            location=f"{host}:{port}",
                            evidence={"service": service, "version": version, "state": "open"},
                            remediation="Review service configuration and apply security updates"
                        )
                        vulnerabilities.append(vuln)
            
            # Parse script results for vulnerabilities
            host_scripts = host_info.get("hostscript", [])
            for script in host_scripts:
                if "vuln" in script.get("id", ""):
                    script_output = script.get("output", "")
                    if "VULNERABLE" in script_output:
                        vuln = Vulnerability(
                            vulnerability_id=f"script_vuln_{host}_{script['id']}",
                            name=f"Vulnerability detected by {script['id']}",
                            severity=VulnerabilitySeverity.HIGH,
                            cvss_score=7.5,
                            description=script_output,
                            location=host,
                            evidence={"script": script["id"], "output": script_output},
                            remediation="Apply security patches and review configuration"
                        )
                        vulnerabilities.append(vuln)
        
        return vulnerabilities

    def _is_vulnerable_service(self, service: str, version: str) -> bool:
        """Check if a service version is known to be vulnerable"""
        # Simplified vulnerability database check
        vulnerable_services = {
            "ssh": ["1.0", "2.0"],  # Very old versions
            "ftp": ["vsftpd 2.3.4"],  # Known backdoor
            "apache": ["2.2.0", "2.2.1"],  # Old versions with known issues
            "nginx": ["0.1.0", "0.2.0"],  # Very old versions
        }
        
        service_lower = service.lower()
        for vuln_service, vuln_versions in vulnerable_services.items():
            if vuln_service in service_lower:
                for vuln_version in vuln_versions:
                    if vuln_version in version:
                        return True
        
        return False

    async def _run_port_scan(self, result: PenetrationTestResult):
        """Run port scan"""
        target = result.target
        
        if target.base_url:
            # Extract host from URL
            from urllib.parse import urlparse
            parsed = urlparse(target.base_url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        elif target.ip_address:
            host = target.ip_address
            port = None
        else:
            raise ValueError("Port scan requires IP address or URL")
        
        # Simple port connectivity check
        open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
        
        for port_num in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result_code = sock.connect_ex((host, port_num))
                sock.close()
                
                if result_code == 0:
                    open_ports.append(port_num)
            except:
                continue
        
        # Create vulnerability for unexpected open ports
        for port in open_ports:
            if port not in [80, 443]:  # Common web ports
                vuln = Vulnerability(
                    vulnerability_id=f"open_port_{host}_{port}",
                    name=f"Unexpected Open Port: {port}",
                    severity=VulnerabilitySeverity.LOW,
                    cvss_score=2.0,
                    description=f"Port {port} is open and accessible",
                    location=f"{host}:{port}",
                    evidence={"port": port, "state": "open"},
                    remediation="Review if this port should be publicly accessible"
                )
                result.vulnerabilities.append(vuln)
        
        result.scan_summary = {"open_ports": open_ports, "total_ports_scanned": len(common_ports)}

    async def _run_web_application_scan(self, result: PenetrationTestResult):
        """Run web application security scan"""
        target = result.target
        
        if not target.base_url:
            raise ValueError("Web application scan requires base URL")
        
        # Basic web application security checks
        vulnerabilities = []
        
        # Check for common security headers
        try:
            response = requests.get(target.base_url, timeout=10)
            missing_headers = self._check_security_headers(response.headers)
            
            for header in missing_headers:
                vuln = Vulnerability(
                    vulnerability_id=f"missing_header_{header}",
                    name=f"Missing Security Header: {header}",
                    severity=VulnerabilitySeverity.LOW,
                    cvss_score=3.0,
                    description=f"Security header {header} is not set",
                    location=target.base_url,
                    evidence={"missing_header": header},
                    remediation=f"Add {header} security header to HTTP responses"
                )
                vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.warning(f"Could not check security headers: {e}")
        
        # Check for directory listing
        common_dirs = ["/admin", "/backup", "/.git", "/.env", "/config"]
        for directory in common_dirs:
            try:
                url = urljoin(target.base_url, directory)
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200 and "Index of" in response.text:
                    vuln = Vulnerability(
                        vulnerability_id=f"directory_listing_{directory}",
                        name=f"Directory Listing Enabled: {directory}",
                        severity=VulnerabilitySeverity.MEDIUM,
                        cvss_score=5.0,
                        description=f"Directory listing is enabled for {directory}",
                        location=url,
                        evidence={"status_code": response.status_code, "directory": directory},
                        remediation="Disable directory listing in web server configuration"
                    )
                    vulnerabilities.append(vuln)
            
            except:
                continue
        
        result.vulnerabilities.extend(vulnerabilities)
        result.scan_summary = {"directories_checked": len(common_dirs)}

    def _check_security_headers(self, headers: Dict[str, str]) -> List[str]:
        """Check for missing security headers"""
        required_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        missing = []
        for header in required_headers:
            if header not in headers:
                missing.append(header)
        
        return missing

    async def _run_sql_injection_test(self, result: PenetrationTestResult):
        """Run SQL injection tests"""
        target = result.target
        
        if not target.base_url:
            raise ValueError("SQL injection test requires base URL")
        
        # Basic SQL injection payload testing
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1' AND 1=1 --",
            "1' AND 1=2 --"
        ]
        
        # Test common parameters
        test_urls = [
            f"{target.base_url}/api/v1/users?id=1",
            f"{target.base_url}/search?q=test",
            f"{target.base_url}/login"
        ]
        
        vulnerabilities = []
        
        for url in test_urls:
            for payload in sql_payloads:
                try:
                    # Test GET parameter injection
                    test_url = f"{url}&test={payload}"
                    response = requests.get(test_url, timeout=5)
                    
                    # Look for SQL error messages
                    sql_errors = [
                        "SQL syntax",
                        "mysql_fetch",
                        "PostgreSQL",
                        "SQLite error",
                        "ORA-01756"
                    ]
                    
                    for error in sql_errors:
                        if error.lower() in response.text.lower():
                            vuln = Vulnerability(
                                vulnerability_id=f"sql_injection_{len(vulnerabilities)}",
                                name="SQL Injection Vulnerability",
                                severity=VulnerabilitySeverity.HIGH,
                                cvss_score=8.5,
                                description=f"SQL injection detected with payload: {payload}",
                                location=test_url,
                                request_method="GET",
                                request_url=test_url,
                                evidence={"payload": payload, "error_message": error},
                                remediation="Use parameterized queries and input validation",
                                references=["https://owasp.org/www-community/attacks/SQL_Injection"]
                            )
                            vulnerabilities.append(vuln)
                            break
                
                except:
                    continue
        
        result.vulnerabilities.extend(vulnerabilities)

    async def _run_xss_test(self, result: PenetrationTestResult):
        """Run XSS (Cross-Site Scripting) tests"""
        target = result.target
        
        if not target.base_url:
            raise ValueError("XSS test requires base URL")
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "'><script>alert('XSS')</script>"
        ]
        
        vulnerabilities = []
        
        # Test common endpoints
        test_endpoints = [
            "/search",
            "/profile",
            "/comment",
            "/feedback"
        ]
        
        for endpoint in test_endpoints:
            url = urljoin(target.base_url, endpoint)
            
            for payload in xss_payloads:
                try:
                    # Test GET parameter
                    response = requests.get(f"{url}?input={payload}", timeout=5)
                    
                    if payload in response.text:
                        vuln = Vulnerability(
                            vulnerability_id=f"xss_reflected_{len(vulnerabilities)}",
                            name="Reflected XSS Vulnerability",
                            severity=VulnerabilitySeverity.MEDIUM,
                            cvss_score=6.1,
                            description=f"Reflected XSS vulnerability detected with payload: {payload}",
                            location=url,
                            request_method="GET",
                            request_url=f"{url}?input={payload}",
                            evidence={"payload": payload, "reflected": True},
                            remediation="Implement proper input validation and output encoding",
                            references=["https://owasp.org/www-community/attacks/xss/"]
                        )
                        vulnerabilities.append(vuln)
                
                except:
                    continue
        
        result.vulnerabilities.extend(vulnerabilities)

    async def _run_ssl_tls_test(self, result: PenetrationTestResult):
        """Run SSL/TLS security tests"""
        target = result.target
        
        if not target.base_url or not target.base_url.startswith('https'):
            # Create vulnerability for missing HTTPS
            vuln = Vulnerability(
                vulnerability_id="missing_https",
                name="Missing HTTPS/TLS Encryption",
                severity=VulnerabilitySeverity.HIGH,
                cvss_score=7.5,
                description="Service does not use HTTPS encryption",
                location=target.base_url or target.ip_address,
                evidence={"protocol": "http"},
                remediation="Implement TLS/SSL encryption and redirect HTTP to HTTPS"
            )
            result.vulnerabilities.append(vuln)
            return
        
        # Basic SSL/TLS checks
        vulnerabilities = []
        
        try:
            import ssl
            import socket
            from urllib.parse import urlparse
            
            parsed = urlparse(target.base_url)
            hostname = parsed.hostname
            port = parsed.port or 443
            
            # Check SSL certificate
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    import datetime
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    if not_after < datetime.datetime.now():
                        vuln = Vulnerability(
                            vulnerability_id="expired_certificate",
                            name="Expired SSL Certificate",
                            severity=VulnerabilitySeverity.HIGH,
                            cvss_score=7.5,
                            description="SSL certificate has expired",
                            location=target.base_url,
                            evidence={"expiry_date": cert['notAfter']},
                            remediation="Renew SSL certificate"
                        )
                        vulnerabilities.append(vuln)
                    
                    # Check for weak cipher suites (simplified)
                    cipher = ssock.cipher()
                    if cipher and len(cipher) > 1:
                        if cipher[1] < 128:  # Key length less than 128 bits
                            vuln = Vulnerability(
                                vulnerability_id="weak_cipher",
                                name="Weak SSL Cipher Suite",
                                severity=VulnerabilitySeverity.MEDIUM,
                                cvss_score=5.3,
                                description=f"Weak cipher suite in use: {cipher[0]}",
                                location=target.base_url,
                                evidence={"cipher": cipher[0], "key_length": cipher[1]},
                                remediation="Configure server to use strong cipher suites only"
                            )
                            vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.warning(f"SSL/TLS test failed: {e}")
        
        result.vulnerabilities.extend(vulnerabilities)

    async def _run_api_security_test(self, result: PenetrationTestResult):
        """Run API security tests"""
        target = result.target
        
        if not target.base_url:
            raise ValueError("API security test requires base URL")
        
        vulnerabilities = []
        
        # Test common API endpoints
        api_endpoints = [
            "/api/v1/users",
            "/api/v1/auth",
            "/api/v1/admin",
            "/api/health",
            "/api/swagger",
            "/api/docs"
        ]
        
        for endpoint in api_endpoints:
            url = urljoin(target.base_url, endpoint)
            
            try:
                # Test without authentication
                response = requests.get(url, timeout=5)
                
                # Check for information disclosure
                if response.status_code == 200:
                    if any(keyword in response.text.lower() for keyword in 
                          ["password", "secret", "token", "api_key", "private"]):
                        vuln = Vulnerability(
                            vulnerability_id=f"info_disclosure_{endpoint}",
                            name="Information Disclosure in API Response",
                            severity=VulnerabilitySeverity.MEDIUM,
                            cvss_score=5.3,
                            description=f"Sensitive information exposed in API endpoint: {endpoint}",
                            location=url,
                            evidence={"endpoint": endpoint, "status_code": response.status_code},
                            remediation="Remove sensitive information from API responses"
                        )
                        vulnerabilities.append(vuln)
                
                # Test for admin endpoints without authentication
                if "admin" in endpoint and response.status_code != 401:
                    vuln = Vulnerability(
                        vulnerability_id=f"unprotected_admin_{endpoint}",
                        name="Unprotected Administrative Endpoint",
                        severity=VulnerabilitySeverity.CRITICAL,
                        cvss_score=9.1,
                        description=f"Administrative endpoint accessible without authentication: {endpoint}",
                        location=url,
                        evidence={"endpoint": endpoint, "status_code": response.status_code},
                        remediation="Implement proper authentication and authorization for admin endpoints"
                    )
                    vulnerabilities.append(vuln)
            
            except:
                continue
        
        result.vulnerabilities.extend(vulnerabilities)

    async def _run_generic_vulnerability_scan(self, result: PenetrationTestResult):
        """Run generic vulnerability scan"""
        # This is a placeholder for more comprehensive vulnerability scanning
        # In a real implementation, this would integrate with tools like OpenVAS, Nessus, etc.
        
        result.scan_summary = {"message": "Generic vulnerability scan completed"}

    async def _generate_security_assessment_report(self, assessment_id: str,
                                                  targets: List[PenetrationTestTarget],
                                                  test_results: List[PenetrationTestResult],
                                                  total_time: float) -> SecurityAssessmentReport:
        """Generate comprehensive security assessment report"""
        
        # Aggregate vulnerability statistics
        all_vulnerabilities = []
        for result in test_results:
            all_vulnerabilities.extend(result.vulnerabilities)
        
        total_vulnerabilities = len(all_vulnerabilities)
        critical_count = len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL])
        high_count = len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.HIGH])
        medium_count = len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM])
        low_count = len([v for v in all_vulnerabilities if v.severity == VulnerabilitySeverity.LOW])
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(all_vulnerabilities)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(all_vulnerabilities)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            targets, test_results, all_vulnerabilities, risk_score
        )
        
        # Generate technical findings
        technical_findings = self._generate_technical_findings(test_results)
        
        # Generate remediation roadmap
        remediation_roadmap = self._generate_remediation_roadmap(all_vulnerabilities)
        
        return SecurityAssessmentReport(
            assessment_id=assessment_id,
            assessment_name=f"Security Assessment - {datetime.utcnow().strftime('%Y-%m-%d')}",
            targets_assessed=len(targets),
            total_tests=len(test_results),
            completed_tests=len([r for r in test_results if r.status == TestStatus.COMPLETED]),
            failed_tests=len([r for r in test_results if r.status == TestStatus.FAILED]),
            total_vulnerabilities=total_vulnerabilities,
            critical_vulnerabilities=critical_count,
            high_vulnerabilities=high_count,
            medium_vulnerabilities=medium_count,
            low_vulnerabilities=low_count,
            risk_score=risk_score,
            compliance_score=compliance_score,
            test_results=test_results,
            executive_summary=executive_summary,
            technical_findings=technical_findings,
            remediation_roadmap=remediation_roadmap
        )

    def _calculate_risk_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate overall risk score based on vulnerabilities"""
        if not vulnerabilities:
            return 0.0
        
        # Weight vulnerabilities by severity
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 10,
            VulnerabilitySeverity.HIGH: 7,
            VulnerabilitySeverity.MEDIUM: 4,
            VulnerabilitySeverity.LOW: 1,
            VulnerabilitySeverity.INFO: 0
        }
        
        total_weight = sum(severity_weights.get(v.severity, 0) for v in vulnerabilities)
        max_possible = len(vulnerabilities) * severity_weights[VulnerabilitySeverity.CRITICAL]
        
        risk_percentage = (total_weight / max_possible) * 100 if max_possible > 0 else 0
        return min(100, risk_percentage)

    def _calculate_compliance_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate compliance score based on security standards"""
        # Simplified compliance calculation
        # In reality, this would map vulnerabilities to specific compliance requirements
        
        critical_compliance_issues = len([
            v for v in vulnerabilities 
            if v.severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]
        ])
        
        # Each critical issue reduces compliance by 10%
        compliance_reduction = min(100, critical_compliance_issues * 10)
        return max(0, 100 - compliance_reduction)

    def _generate_executive_summary(self, targets: List[PenetrationTestTarget],
                                  test_results: List[PenetrationTestResult],
                                  vulnerabilities: List[Vulnerability],
                                  risk_score: float) -> str:
        """Generate executive summary"""
        
        return f"""
**Executive Summary**

This security assessment evaluated {len(targets)} targets across the Ainflue platform infrastructure. 
A total of {len(test_results)} security tests were conducted, identifying {len(vulnerabilities)} 
security findings.

**Key Findings:**
- Overall Risk Score: {risk_score:.1f}/100
- Critical Vulnerabilities: {len([v for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL])}
- High-Risk Vulnerabilities: {len([v for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH])}

**Immediate Actions Required:**
{"- Address all critical vulnerabilities immediately" if any(v.severity == VulnerabilitySeverity.CRITICAL for v in vulnerabilities) else "- No critical vulnerabilities found"}
{"- Review and remediate high-risk findings" if any(v.severity == VulnerabilitySeverity.HIGH for v in vulnerabilities) else "- Continue monitoring for emerging threats"}

The security posture of the platform is {"concerning and requires immediate attention" if risk_score > 70 else "acceptable with room for improvement" if risk_score > 30 else "good with minor issues to address"}.
        """

    def _generate_technical_findings(self, test_results: List[PenetrationTestResult]) -> List[Dict[str, Any]]:
        """Generate technical findings summary"""
        findings = []
        
        for result in test_results:
            if result.vulnerabilities:
                finding = {
                    "target": result.target.name,
                    "test_type": result.test_type.value,
                    "vulnerability_count": len(result.vulnerabilities),
                    "critical_count": len([v for v in result.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL]),
                    "high_count": len([v for v in result.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH]),
                    "status": result.status.value,
                    "duration": result.duration
                }
                findings.append(finding)
        
        return findings

    def _generate_remediation_roadmap(self, vulnerabilities: List[Vulnerability]) -> List[Dict[str, Any]]:
        """Generate remediation roadmap"""
        roadmap = []
        
        # Group by severity and create timeline
        critical_vulns = [v for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL]
        high_vulns = [v for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH]
        medium_vulns = [v for v in vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM]
        
        if critical_vulns:
            roadmap.append({
                "priority": "Immediate (0-7 days)",
                "task": "Address Critical Vulnerabilities",
                "count": len(critical_vulns),
                "description": "Fix all critical security vulnerabilities that pose immediate risk"
            })
        
        if high_vulns:
            roadmap.append({
                "priority": "High (1-2 weeks)",
                "task": "Address High-Risk Vulnerabilities", 
                "count": len(high_vulns),
                "description": "Remediate high-risk security issues"
            })
        
        if medium_vulns:
            roadmap.append({
                "priority": "Medium (2-4 weeks)",
                "task": "Address Medium-Risk Vulnerabilities",
                "count": len(medium_vulns),
                "description": "Fix medium-risk security findings"
            })
        
        return roadmap

    async def _save_assessment_report(self, report: SecurityAssessmentReport):
        """Save security assessment report"""
        timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.reports_dir / f"security_assessment_{timestamp}.json"
        with open(json_file, 'w') as f:
            # Convert to serializable format
            report_dict = {
                "assessment_id": report.assessment_id,
                "assessment_name": report.assessment_name,
                "timestamp": report.timestamp.isoformat(),
                "summary": {
                    "targets_assessed": report.targets_assessed,
                    "total_tests": report.total_tests,
                    "total_vulnerabilities": report.total_vulnerabilities,
                    "critical_vulnerabilities": report.critical_vulnerabilities,
                    "high_vulnerabilities": report.high_vulnerabilities,
                    "risk_score": report.risk_score,
                    "compliance_score": report.compliance_score
                },
                "executive_summary": report.executive_summary,
                "technical_findings": report.technical_findings,
                "remediation_roadmap": report.remediation_roadmap
            }
            json.dump(report_dict, f, indent=2)
        
        # Save Markdown report
        md_file = self.reports_dir / f"security_assessment_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(self.generate_report(report, "markdown"))

    def generate_report(self, report: SecurityAssessmentReport, format: str = "markdown") -> str:
        """Generate security assessment report in specified format"""
        if format == "json":
            return self._generate_json_report(report)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(self, report: SecurityAssessmentReport) -> str:
        """Generate JSON report"""
        data = {
            "assessment_id": report.assessment_id,
            "timestamp": report.timestamp.isoformat(),
            "risk_score": report.risk_score,
            "compliance_score": report.compliance_score,
            "vulnerability_summary": {
                "total": report.total_vulnerabilities,
                "critical": report.critical_vulnerabilities,
                "high": report.high_vulnerabilities,
                "medium": report.medium_vulnerabilities,
                "low": report.low_vulnerabilities
            },
            "test_summary": {
                "total_tests": report.total_tests,
                "completed": report.completed_tests,
                "failed": report.failed_tests
            }
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, report: SecurityAssessmentReport) -> str:
        """Generate Markdown report"""
        
        # Determine overall security status
        if report.risk_score > 70:
            status_emoji = "🔴"
            status_text = "High Risk"
        elif report.risk_score > 30:
            status_emoji = "🟡"
            status_text = "Medium Risk"
        else:
            status_emoji = "🟢"
            status_text = "Low Risk"
        
        md = f"""# Security Assessment Report {status_emoji}

**Assessment ID:** {report.assessment_id}  
**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Risk Score:** {report.risk_score:.1f}/100 ({status_text})  
**Compliance Score:** {report.compliance_score:.1f}/100

## Executive Summary

{report.executive_summary}

## Vulnerability Summary

| Severity | Count |
|----------|-------|
| Critical | {report.critical_vulnerabilities} |
| High | {report.high_vulnerabilities} |
| Medium | {report.medium_vulnerabilities} |
| Low | {report.low_vulnerabilities} |
| **Total** | **{report.total_vulnerabilities}** |

## Test Summary

| Metric | Value |
|--------|-------|
| Targets Assessed | {report.targets_assessed} |
| Total Tests | {report.total_tests} |
| Completed Tests | {report.completed_tests} |
| Failed Tests | {report.failed_tests} |

## Technical Findings

"""
        
        for finding in report.technical_findings:
            md += f"### {finding['target']} - {finding['test_type']}\n"
            md += f"- **Vulnerabilities Found:** {finding['vulnerability_count']}\n"
            md += f"- **Critical:** {finding['critical_count']}, **High:** {finding['high_count']}\n"
            md += f"- **Test Duration:** {finding['duration']:.2f}s\n\n"
        
        if report.remediation_roadmap:
            md += "## Remediation Roadmap\n\n"
            for item in report.remediation_roadmap:
                md += f"### {item['priority']}: {item['task']}\n"
                md += f"**Count:** {item['count']} items  \n"
                md += f"**Description:** {item['description']}\n\n"
        
        return md

# Global penetration testing coordinator instance
penetration_testing_coordinator = PenetrationTestingCoordinator()

__all__ = [
    "PenetrationTestingCoordinator",
    "PenetrationTestTarget",
    "Vulnerability",
    "PenetrationTestResult",
    "SecurityAssessmentReport",
    "PenetrationTestType",
    "VulnerabilitySeverity",
    "TestStatus",
    "penetration_testing_coordinator"
]