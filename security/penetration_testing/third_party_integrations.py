"""Third-Party Penetration Testing Integration Framework
Orchestrates and integrates with external penetration testing services
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import subprocess
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class PentestProvider(Enum):
    """Supported penetration testing providers"""
    NESSUS = "nessus"
    OPENVAS = "openvas"
    QUALYS = "qualys"
    RAPID7 = "rapid7"
    NUCLEI = "nuclei"
    NMAP = "nmap"
    OWASP_ZAP = "owasp_zap"
    BURP_SUITE = "burp_suite"


class TestType(Enum):
    """Types of penetration tests"""
    NETWORK_SCAN = "network_scan"
    WEB_APPLICATION = "web_application"
    API_SECURITY = "api_security"
    INFRASTRUCTURE = "infrastructure"
    SOCIAL_ENGINEERING = "social_engineering"
    WIRELESS = "wireless"
    DATABASE = "database"
    COMPLIANCE = "compliance"


class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PentestConfig:
    """Configuration for penetration testing"""
    provider: PentestProvider
    test_type: TestType
    target_urls: List[str]
    target_ips: List[str] = None
    schedule_cron: str = None  # For automated testing
    notify_on_completion: bool = True
    export_formats: List[str] = None  # ["json", "xml", "pdf", "html"]
    compliance_frameworks: List[str] = None  # ["SOC2", "ISO27001", "PCI_DSS"]


@dataclass
class Vulnerability:
    """Vulnerability finding from penetration test"""
    id: str
    title: str
    severity: SeverityLevel
    description: str
    affected_component: str
    cve_id: str = None
    cvss_score: float = None
    remediation: str = None
    references: List[str] = None
    discovered_at: datetime = None


@dataclass
class PentestResult:
    """Penetration test result"""
    test_id: str
    provider: PentestProvider
    test_type: TestType
    start_time: datetime
    end_time: datetime
    status: str  # "running", "completed", "failed"
    vulnerabilities: List[Vulnerability]
    summary: Dict[str, Any]
    raw_report_path: str = None
    compliance_status: Dict[str, bool] = None


class ThirdPartyPentestManager:
    """
    Manager for third-party penetration testing integrations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, PentestResult] = {}
        self.test_history: List[PentestResult] = []
        self.configs: Dict[str, Dict[str, Any]] = {}
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load configurations for different penetration testing tools"""
        self.configs = {
            PentestProvider.NUCLEI.value: {
                "binary_path": "/usr/local/bin/nuclei",
                "templates_path": "/opt/nuclei-templates",
                "rate_limit": 100,
                "timeout": 300
            },
            PentestProvider.NMAP.value: {
                "binary_path": "/usr/bin/nmap",
                "default_options": "-sV -sC --script vuln",
                "timeout": 600
            },
            PentestProvider.OWASP_ZAP.value: {
                "api_url": "http://localhost:8080",
                "api_key": None,  # Should be set via environment
                "timeout": 1800
            },
            PentestProvider.NESSUS.value: {
                "api_url": "https://localhost:8834",
                "access_key": None,  # Should be set via environment
                "secret_key": None,  # Should be set via environment
                "scan_policy_id": None
            }
        }
    
    async def schedule_penetration_test(self, config: PentestConfig) -> str:
        """Schedule a penetration test with specified provider"""
        test_id = f"pentest_{config.provider.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.logger.info(f"Scheduling penetration test: {test_id}")
            
            # Create test result placeholder
            result = PentestResult(
                test_id=test_id,
                provider=config.provider,
                test_type=config.test_type,
                start_time=datetime.now(),
                end_time=None,
                status="scheduled",
                vulnerabilities=[],
                summary={}
            )
            
            self.active_tests[test_id] = result
            
            # Execute test based on provider
            if config.provider == PentestProvider.NUCLEI:
                await self._run_nuclei_test(test_id, config)
            elif config.provider == PentestProvider.NMAP:
                await self._run_nmap_test(test_id, config)
            elif config.provider == PentestProvider.OWASP_ZAP:
                await self._run_zap_test(test_id, config)
            elif config.provider == PentestProvider.NESSUS:
                await self._run_nessus_test(test_id, config)
            else:
                await self._run_custom_test(test_id, config)
            
            return test_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling penetration test: {e}")
            if test_id in self.active_tests:
                self.active_tests[test_id].status = "failed"
                self.active_tests[test_id].end_time = datetime.now()
            raise
    
    async def _run_nuclei_test(self, test_id: str, config: PentestConfig):
        """Run Nuclei vulnerability scanner"""
        try:
            result = self.active_tests[test_id]
            result.status = "running"
            result.start_time = datetime.now()
            
            nuclei_config = self.configs[PentestProvider.NUCLEI.value]
            
            # Prepare Nuclei command
            cmd = [
                nuclei_config["binary_path"],
                "-t", nuclei_config["templates_path"],
                "-rate-limit", str(nuclei_config["rate_limit"]),
                "-timeout", str(nuclei_config["timeout"]),
                "-json"
            ]
            
            # Add targets
            for target in config.target_urls:
                cmd.extend(["-u", target])
            
            # Execute Nuclei
            self.logger.info(f"Running Nuclei: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse Nuclei JSON output
                vulnerabilities = self._parse_nuclei_output(stdout.decode())
                result.vulnerabilities = vulnerabilities
                result.status = "completed"
                result.summary = {
                    "total_vulnerabilities": len(vulnerabilities),
                    "critical": len([v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]),
                    "high": len([v for v in vulnerabilities if v.severity == SeverityLevel.HIGH]),
                    "medium": len([v for v in vulnerabilities if v.severity == SeverityLevel.MEDIUM]),
                    "low": len([v for v in vulnerabilities if v.severity == SeverityLevel.LOW])
                }
            else:
                result.status = "failed"
                self.logger.error(f"Nuclei failed: {stderr.decode()}")
            
            result.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error running Nuclei test: {e}")
            result.status = "failed"
            result.end_time = datetime.now()
    
    async def _run_nmap_test(self, test_id: str, config: PentestConfig):
        """Run Nmap network scan"""
        try:
            result = self.active_tests[test_id]
            result.status = "running"
            result.start_time = datetime.now()
            
            nmap_config = self.configs[PentestProvider.NMAP.value]
            
            # Prepare Nmap command
            cmd = [
                nmap_config["binary_path"],
                "-oX", f"/tmp/{test_id}_nmap.xml",
                *nmap_config["default_options"].split()
            ]
            
            # Add targets
            if config.target_ips:
                cmd.extend(config.target_ips)
            else:
                # Extract domains from URLs
                for url in config.target_urls:
                    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                    cmd.append(domain)
            
            # Execute Nmap
            self.logger.info(f"Running Nmap: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse Nmap XML output
                vulnerabilities = self._parse_nmap_output(f"/tmp/{test_id}_nmap.xml")
                result.vulnerabilities = vulnerabilities
                result.status = "completed"
                result.raw_report_path = f"/tmp/{test_id}_nmap.xml"
                result.summary = {
                    "total_vulnerabilities": len(vulnerabilities),
                    "ports_scanned": "variable",  # Would parse from XML
                    "hosts_scanned": len(config.target_ips or config.target_urls)
                }
            else:
                result.status = "failed"
                self.logger.error(f"Nmap failed: {stderr.decode()}")
            
            result.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error running Nmap test: {e}")
            result.status = "failed"
            result.end_time = datetime.now()
    
    async def _run_zap_test(self, test_id: str, config: PentestConfig):
        """Run OWASP ZAP web application security test"""
        try:
            result = self.active_tests[test_id]
            result.status = "running"
            result.start_time = datetime.now()
            
            zap_config = self.configs[PentestProvider.OWASP_ZAP.value]
            
            # For this implementation, we'll simulate ZAP API calls
            # In production, you would use the actual ZAP Python API
            
            vulnerabilities = []
            for target_url in config.target_urls:
                # Simulate ZAP scan results
                mock_vulnerabilities = [
                    Vulnerability(
                        id=f"zap_001_{target_url}",
                        title="Cross-Site Scripting (XSS)",
                        severity=SeverityLevel.HIGH,
                        description="Potential XSS vulnerability detected",
                        affected_component=target_url,
                        remediation="Implement input validation and output encoding",
                        discovered_at=datetime.now()
                    ),
                    Vulnerability(
                        id=f"zap_002_{target_url}",
                        title="Missing Security Headers",
                        severity=SeverityLevel.MEDIUM,
                        description="Security headers not properly configured",
                        affected_component=target_url,
                        remediation="Configure security headers (CSP, HSTS, etc.)",
                        discovered_at=datetime.now()
                    )
                ]
                vulnerabilities.extend(mock_vulnerabilities)
            
            result.vulnerabilities = vulnerabilities
            result.status = "completed"
            result.summary = {
                "total_vulnerabilities": len(vulnerabilities),
                "urls_tested": len(config.target_urls),
                "test_type": "web_application_security"
            }
            result.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error running ZAP test: {e}")
            result.status = "failed"
            result.end_time = datetime.now()
    
    async def _run_nessus_test(self, test_id: str, config: PentestConfig):
        """Run Nessus vulnerability scan"""
        try:
            result = self.active_tests[test_id]
            result.status = "running"
            result.start_time = datetime.now()
            
            # For this implementation, we'll simulate Nessus API integration
            # In production, you would use the actual Nessus API
            
            # Simulate compliance-focused vulnerabilities
            vulnerabilities = [
                Vulnerability(
                    id="nessus_001",
                    title="SSL/TLS Certificate Issues",
                    severity=SeverityLevel.HIGH,
                    description="SSL certificate has issues that may affect compliance",
                    affected_component="TLS Configuration",
                    cve_id="CVE-2023-0001",
                    cvss_score=7.5,
                    remediation="Update SSL certificate and configuration",
                    discovered_at=datetime.now()
                ),
                Vulnerability(
                    id="nessus_002",
                    title="Outdated Software Components",
                    severity=SeverityLevel.MEDIUM,
                    description="Some software components are outdated",
                    affected_component="System Components",
                    remediation="Update all software components to latest versions",
                    discovered_at=datetime.now()
                )
            ]
            
            result.vulnerabilities = vulnerabilities
            result.status = "completed"
            result.summary = {
                "total_vulnerabilities": len(vulnerabilities),
                "compliance_scan": True,
                "frameworks_checked": config.compliance_frameworks or ["SOC2", "ISO27001"]
            }
            
            # Set compliance status
            result.compliance_status = {
                "SOC2": len([v for v in vulnerabilities if v.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]) == 0,
                "ISO27001": len([v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]) == 0
            }
            
            result.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error running Nessus test: {e}")
            result.status = "failed"
            result.end_time = datetime.now()
    
    async def _run_custom_test(self, test_id: str, config: PentestConfig):
        """Run custom penetration test"""
        try:
            result = self.active_tests[test_id]
            result.status = "running"
            result.start_time = datetime.now()
            
            # Placeholder for custom testing logic
            await asyncio.sleep(10)  # Simulate test execution
            
            result.vulnerabilities = []
            result.status = "completed"
            result.summary = {"note": "Custom test completed"}
            result.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error running custom test: {e}")
            result.status = "failed"
            result.end_time = datetime.now()
    
    def _parse_nuclei_output(self, output: str) -> List[Vulnerability]:
        """Parse Nuclei JSON output into vulnerability objects"""
        vulnerabilities = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            try:
                data = json.loads(line)
                vuln = Vulnerability(
                    id=data.get("template-id", "unknown"),
                    title=data.get("info", {}).get("name", "Unknown"),
                    severity=self._map_nuclei_severity(data.get("info", {}).get("severity", "info")),
                    description=data.get("info", {}).get("description", ""),
                    affected_component=data.get("matched-at", ""),
                    discovered_at=datetime.now()
                )
                vulnerabilities.append(vuln)
            except json.JSONDecodeError:
                continue
        
        return vulnerabilities
    
    def _parse_nmap_output(self, xml_file: str) -> List[Vulnerability]:
        """Parse Nmap XML output into vulnerability objects"""
        vulnerabilities = []
        
        # Simplified parsing - in production, use proper XML parsing
        try:
            with open(xml_file, 'r') as f:
                content = f.read()
                
            # Look for script results indicating vulnerabilities
            if "vuln" in content.lower():
                vuln = Vulnerability(
                    id="nmap_vuln_001",
                    title="Potential Vulnerability Detected",
                    severity=SeverityLevel.MEDIUM,
                    description="Nmap vulnerability scripts detected potential issues",
                    affected_component="Network Service",
                    discovered_at=datetime.now()
                )
                vulnerabilities.append(vuln)
                
        except FileNotFoundError:
            self.logger.warning(f"Nmap output file not found: {xml_file}")
        
        return vulnerabilities
    
    def _map_nuclei_severity(self, nuclei_severity: str) -> SeverityLevel:
        """Map Nuclei severity to our severity levels"""
        mapping = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.HIGH,
            "medium": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW,
            "info": SeverityLevel.INFO
        }
        return mapping.get(nuclei_severity.lower(), SeverityLevel.INFO)
    
    async def get_test_status(self, test_id: str) -> Optional[PentestResult]:
        """Get status of a specific penetration test"""
        return self.active_tests.get(test_id)
    
    async def get_all_test_results(self) -> List[PentestResult]:
        """Get all penetration test results"""
        all_results = list(self.active_tests.values()) + self.test_history
        return sorted(all_results, key=lambda x: x.start_time, reverse=True)
    
    async def generate_compliance_report(self, frameworks: List[str] = None) -> Dict[str, Any]:
        """Generate compliance report based on penetration test results"""
        if frameworks is None:
            frameworks = ["SOC2", "ISO27001"]
        
        all_results = await self.get_all_test_results()
        recent_results = [r for r in all_results if r.end_time and 
                         r.end_time >= datetime.now() - timedelta(days=30)]
        
        # Aggregate vulnerability data
        all_vulnerabilities = []
        for result in recent_results:
            all_vulnerabilities.extend(result.vulnerabilities)
        
        # Calculate compliance status
        compliance_status = {}
        for framework in frameworks:
            if framework == "SOC2":
                # SOC2 focuses on security controls
                critical_high = [v for v in all_vulnerabilities if v.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
                compliance_status[framework] = len(critical_high) == 0
            elif framework == "ISO27001":
                # ISO27001 focuses on information security management
                critical_vulns = [v for v in all_vulnerabilities if v.severity == SeverityLevel.CRITICAL]
                compliance_status[framework] = len(critical_vulns) == 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "frameworks": frameworks,
            "compliance_status": compliance_status,
            "tests_conducted": len(recent_results),
            "vulnerabilities_found": len(all_vulnerabilities),
            "vulnerability_breakdown": {
                "critical": len([v for v in all_vulnerabilities if v.severity == SeverityLevel.CRITICAL]),
                "high": len([v for v in all_vulnerabilities if v.severity == SeverityLevel.HIGH]),
                "medium": len([v for v in all_vulnerabilities if v.severity == SeverityLevel.MEDIUM]),
                "low": len([v for v in all_vulnerabilities if v.severity == SeverityLevel.LOW])
            },
            "recommendations": self._generate_compliance_recommendations(all_vulnerabilities, frameworks)
        }
    
    def _generate_compliance_recommendations(self, vulnerabilities: List[Vulnerability], 
                                           frameworks: List[str]) -> List[str]:
        """Generate compliance-specific recommendations"""
        recommendations = []
        
        critical_vulns = [v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]
        high_vulns = [v for v in vulnerabilities if v.severity == SeverityLevel.HIGH]
        
        if critical_vulns:
            recommendations.append("Address all critical vulnerabilities immediately for compliance")
        
        if high_vulns:
            recommendations.append("Remediate high-severity vulnerabilities within 30 days")
        
        if "SOC2" in frameworks:
            recommendations.append("Implement continuous monitoring for SOC2 Type II compliance")
            recommendations.append("Document all security controls and their effectiveness")
        
        if "ISO27001" in frameworks:
            recommendations.append("Establish formal risk management processes per ISO27001")
            recommendations.append("Conduct regular security awareness training")
        
        return recommendations


# Global penetration testing manager
pentest_manager = ThirdPartyPentestManager()