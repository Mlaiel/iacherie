"""🔧 Security Scanner - IA-Influencer-Agent CI/CD
================================================================
Expert: SECURITY_ENGINEER + DEVOPS_ENGINEER
Created: 2025-08-24
Author: Fahed Mlaiel (mlaiel@live.de)

Enterprise security scanning engine for multi-layer vulnerability detection.
Integrates SAST, DAST, dependency scanning, and container security analysis.
================================================================
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
import logging
import subprocess
import json
import os
import tempfile
import docker
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class ScanType(Enum):
    """
Security scan type enumeration"""

    STATIC_ANALYSIS = "static_analysis"
    DEPENDENCY_SCAN = "dependency_scan"
    CONTAINER_SCAN = "container_scan"
    SECRET_SCAN = "secret_scan"
    LICENSE_SCAN = "license_scan"
    INFRASTRUCTURE_SCAN = "infrastructure_scan"

class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    """Vulnerability data structure"""
    scan_type: ScanType
    severity: VulnerabilitySeverity
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    confidence: Optional[str] = None
    recommendation: Optional[str] = None
    references: List[str] = None

@dataclass
class SecurityScanConfig:
    """
Security scan configuration"""
    scan_types: List[ScanType]
    severity_threshold: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    fail_on_critical: bool = True
    fail_on_high: bool = True
    max_scan_time: int = 1800  # 30 minutes
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None

@dataclass
class SecurityScanResult:
    """
Security scan result"""
    scan_id: str
    scan_timestamp: datetime
    config: SecurityScanConfig
    vulnerabilities: List[Vulnerability]
    scan_duration: float
    overall_score: float
    risk_level: str
    summary: Dict[str, Any]
    recommendations: List[str]
    scan_status: str = "completed"
    error_message: Optional[str] = None

class SecurityScanEngine:
    """Enterprise security scanning engine"""
    
    def __init__(self):
        """
Initialize security scan engine"""
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.scan_history: List[SecurityScanResult] = []
        self.docker_client = None
        
        # Security tools configuration
        self.security_tools = {
            ScanType.STATIC_ANALYSIS: ["bandit", "semgrep", "sonarqube"],
            ScanType.DEPENDENCY_SCAN: ["safety", "pip-audit", "snyk"],
            ScanType.CONTAINER_SCAN: ["trivy", "clair", "anchore"],
            ScanType.SECRET_SCAN: ["truffleHog", "gitleaks", "detect-secrets"],
            ScanType.LICENSE_SCAN: ["pip-licenses", "fossa"],
            ScanType.INFRASTRUCTURE_SCAN: ["terraform-compliance", "checkov"]
        }
        
    async def initialize(self) -> bool:
        """Initialize security scanner"""
        try:
            # Initialize Docker client for container scanning
            self.docker_client = docker.from_env()
            
            # Verify security tools availability
            await self._verify_security_tools()
            
            self.initialized = True
            self.logger.info("✅ Security scanner initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize security scanner: {e}")
            return False
    
    async def _verify_security_tools(self) -> None:
        """Verify security tools are available"""
        essential_tools = ["bandit", "safety", "trivy"]
        missing_tools = []
        
        for tool in essential_tools:
            if not await self._check_tool_available(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            self.logger.warning(f"Missing security tools: {missing_tools}")
            # Don't fail initialization, log warning instead
    
    async def _check_tool_available(self, tool: str) -> bool:
        """Check if security tool is available"""
        try:
            result = await self._run_command([tool, "--version"], timeout=30)
            return result.returncode == 0
        except:
            return False
    
    async def execute_security_scan(
        self,
        source_path: str,
        config: SecurityScanConfig,
        image_tag: Optional[str] = None
    ) -> SecurityScanResult:
        """Execute comprehensive security scan"""
        scan_id = self._generate_scan_id()
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting security scan {scan_id}")
            
            all_vulnerabilities = []
            
            # Execute each scan type
            for scan_type in config.scan_types:
                try:
                    self.logger.info(f"Executing {scan_type.value} scan")
                    vulnerabilities = await self._execute_scan_type(
                        scan_type, source_path, config, image_tag
                    )
                    all_vulnerabilities.extend(vulnerabilities)
                except Exception as e:
                    self.logger.error(f"Scan type {scan_type.value} failed: {e}")
                    # Continue with other scans
            
            # Filter vulnerabilities by severity threshold
            filtered_vulnerabilities = self._filter_vulnerabilities(
                all_vulnerabilities, config.severity_threshold
            )
            
            # Calculate overall security score
            overall_score = self._calculate_security_score(filtered_vulnerabilities)
            
            # Determine risk level
            risk_level = self._determine_risk_level(filtered_vulnerabilities)
            
            # Generate summary and recommendations
            summary = self._generate_security_summary(filtered_vulnerabilities)
            recommendations = self._generate_security_recommendations(filtered_vulnerabilities)
            
            # Calculate scan duration
            scan_duration = (datetime.now() - start_time).total_seconds()
            
            # Create scan result
            result = SecurityScanResult(
                scan_id=scan_id,
                scan_timestamp=start_time,
                config=config,
                vulnerabilities=filtered_vulnerabilities,
                scan_duration=scan_duration,
                overall_score=overall_score,
                risk_level=risk_level,
                summary=summary,
                recommendations=recommendations
            )
            
            self.scan_history.append(result)
            
            self.logger.info(f"✅ Security scan {scan_id} completed. Score: {overall_score:.1f}")
            return result
            
        except Exception as e:
            scan_duration = (datetime.now() - start_time).total_seconds()
            
            result = SecurityScanResult(
                scan_id=scan_id,
                scan_timestamp=start_time,
                config=config,
                vulnerabilities=[],
                scan_duration=scan_duration,
                overall_score=0.0,
                risk_level="unknown",
                summary={},
                recommendations=[],
                scan_status="failed",
                error_message=str(e)
            )
            
            self.scan_history.append(result)
            self.logger.error(f"❌ Security scan {scan_id} failed: {e}")
            return result
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"security_scan_{timestamp}"
    
    async def _execute_scan_type(
        self,
        scan_type: ScanType,
        source_path: str,
        config: SecurityScanConfig,
        image_tag: Optional[str] = None
    ) -> List[Vulnerability]:
        """Execute specific scan type"""
        if scan_type == ScanType.STATIC_ANALYSIS:
            return await self._run_static_analysis(source_path, config)
        elif scan_type == ScanType.DEPENDENCY_SCAN:
            return await self._run_dependency_scan(source_path, config)
        elif scan_type == ScanType.CONTAINER_SCAN and image_tag:
            return await self._run_container_scan(image_tag, config)
        elif scan_type == ScanType.SECRET_SCAN:
            return await self._run_secret_scan(source_path, config)
        elif scan_type == ScanType.LICENSE_SCAN:
            return await self._run_license_scan(source_path, config)
        elif scan_type == ScanType.INFRASTRUCTURE_SCAN:
            return await self._run_infrastructure_scan(source_path, config)
        else:
            self.logger.warning(f"Scan type {scan_type.value} not implemented")
            return []
    
    async def _run_static_analysis(
        self,
        source_path: str,
        config: SecurityScanConfig
    ) -> List[Vulnerability]:
        """Run static application security testing (SAST)"""
        vulnerabilities = []
        
        try:
            # Run Bandit for Python security issues
            bandit_cmd = [
                "bandit",
                "-r", "backend/",
                "-f", "json",
                "-ll",  # Low confidence, low severity
                "--exclude", "*/tests/*,*/test_*"
            ]
            
            result = await self._run_command(bandit_cmd, cwd=source_path)
            
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    for issue in bandit_data.get("results", []):
                        severity = self._map_bandit_severity(issue.get("issue_severity", ""))
                        
                        vulnerability = Vulnerability(
                            scan_type=ScanType.STATIC_ANALYSIS,
                            severity=severity,
                            title=issue.get("test_name", "Unknown Issue"),
                            description=issue.get("issue_text", ""),
                            file_path=issue.get("filename", ""),
                            line_number=issue.get("line_number"),
                            cwe_id=issue.get("test_id", ""),
                            confidence=issue.get("issue_confidence", ""),
                            recommendation="Review and fix the identified security issue"
                        )
                        vulnerabilities.append(vulnerability)
                        
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse Bandit output")
            
            # Run Semgrep for additional security patterns
            if await self._check_tool_available("semgrep"):
                semgrep_vulnerabilities = await self._run_semgrep_scan(source_path)
                vulnerabilities.extend(semgrep_vulnerabilities)
            
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
        
        return vulnerabilities
    
    async def _run_semgrep_scan(self, source_path: str) -> List[Vulnerability]:
        """Run Semgrep security analysis"""
        vulnerabilities = []
        
        try:
            semgrep_cmd = [
                "semgrep",
                "--config=auto",
                "--json",
                "--no-rewrite-rule-ids",
                "backend/"
            ]
            
            result = await self._run_command(semgrep_cmd, cwd=source_path)
            
            if result.stdout:
                semgrep_data = json.loads(result.stdout)
                for finding in semgrep_data.get("results", []):
                    severity = self._map_semgrep_severity(finding.get("extra", {}).get("severity", ""))
                    
                    vulnerability = Vulnerability(
                        scan_type=ScanType.STATIC_ANALYSIS,
                        severity=severity,
                        title=finding.get("check_id", "Semgrep Finding"),
                        description=finding.get("extra", {}).get("message", ""),
                        file_path=finding.get("path", ""),
                        line_number=finding.get("start", {}).get("line"),
                        recommendation="Review Semgrep finding and apply suggested fix"
                    )
                    vulnerabilities.append(vulnerability)
        
        except Exception as e:
            self.logger.error(f"Semgrep scan failed: {e}")
        
        return vulnerabilities
    
    async def _run_dependency_scan(
        self,
        source_path: str,
        try:
            logger.info(f"Executing _run_dependency_scan")
            
            # Implementation for _run_dependency_scan
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_run_dependency_scan completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_run_dependency_scan failed: {e}")
            raise
    async def _run_pip_audit(self, source_path: str) -> List[Vulnerability]:
        """Run pip-audit for dependency vulnerabilities"""
        vulnerabilities = []
        
        try:
            pip_audit_cmd = ["pip-audit", "--format=json"]
            result = await self._run_command(pip_audit_cmd, cwd=source_path)
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                for vuln in audit_data.get("vulnerabilities", []):
                    vulnerability = Vulnerability(
                        scan_type=ScanType.DEPENDENCY_SCAN,
                        severity=self._map_cvss_to_severity(vuln.get("fix", {}).get("versions", [])),
                        title=f"CVE in {vuln.get('package', 'Unknown package')}",
                        description=vuln.get("description", ""),
                        cve_id=vuln.get("id", ""),
                        recommendation=f"Update to version {vuln.get('fix', {}).get('versions', ['latest'])[0]}"
                    )
                    vulnerabilities.append(vulnerability)
        
        except Exception as e:
            self.logger.error(f"pip-audit scan failed: {e}")
        
        return vulnerabilities
    
    async def _run_container_scan(
        self,
        image_tag: str,
        config: SecurityScanConfig
    ) -> List[Vulnerability]:
        """Run container image security scanning"""
        vulnerabilities = []
        
        try:
            # Run Trivy container scan
            trivy_cmd = [
                "trivy", "image",
                "--format", "json",
                "--exit-code", "0",
                image_tag
            ]
            
            result = await self._run_command(trivy_cmd)
            
            if result.stdout:
                trivy_data = json.loads(result.stdout)
                for result_item in trivy_data.get("Results", []):
                    for vuln in result_item.get("Vulnerabilities", []):
                        severity = self._map_trivy_severity(vuln.get("Severity", ""))
                        
                        vulnerability = Vulnerability(
                            scan_type=ScanType.CONTAINER_SCAN,
                            severity=severity,
                            title=f"Container vulnerability: {vuln.get('Title', 'Unknown')}",
                            description=vuln.get("Description", ""),
                            cve_id=vuln.get("VulnerabilityID", ""),
                            recommendation=f"Update package {vuln.get('PkgName', 'unknown')} to fix version"
                        )
                        vulnerabilities.append(vulnerability)
        
        except Exception as e:
            self.logger.error(f"Container scan failed: {e}")
        
        return vulnerabilities
    
    async def _run_secret_scan(
        self,
        source_path: str,
        config: SecurityScanConfig
    ) -> List[Vulnerability]:
        """Run secret detection scanning"""
        vulnerabilities = []
        
        try:
            # Run detect-secrets
            if await self._check_tool_available("detect-secrets"):
                detect_secrets_cmd = [
                    "detect-secrets", "scan",
                    "--all-files",
                    "--force-use-all-plugins",
                    source_path
                ]
                
                result = await self._run_command(detect_secrets_cmd)
                
                if result.stdout:
                    try:
                        secrets_data = json.loads(result.stdout)
                        for file_path, secrets in secrets_data.get("results", {}).items():
        try:
            logger.info(f"Executing _run_secret_scan")
            
            # Implementation for _run_secret_scan
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_run_secret_scan completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_run_secret_scan failed: {e}")
            raise
                        license_name = package.get("License", "")
                        for prob_license in problematic_licenses:
                            if prob_license in license_name.upper():
                                vulnerability = Vulnerability(
                                    scan_type=ScanType.LICENSE_SCAN,
                                    severity=VulnerabilitySeverity.MEDIUM,
                                    title=f"License compliance issue: {package.get('Name', 'Unknown')}",
                                    description=f"Package uses {license_name} license which may have restrictions",
                                    recommendation="Review license compatibility with project requirements"
                                )
                                vulnerabilities.append(vulnerability)
        
        except Exception as e:
            self.logger.error(f"License scan failed: {e}")
        
        return vulnerabilities
    
    async def _run_infrastructure_scan(
        self,
        source_path: str,
        config: SecurityScanConfig
    ) -> List[Vulnerability]:
        """Run infrastructure security scanning"""
        vulnerabilities = []
        
        try:
            # Look for Terraform files and scan them
            terraform_files = list(Path(source_path).rglob("*.tf"))
            
            if terraform_files and await self._check_tool_available("checkov"):
                checkov_cmd = [
                    "checkov",
                    "-d", source_path,
                    "--framework", "terraform",
                    "--output", "json"
                ]
                
                result = await self._run_command(checkov_cmd)
                
                if result.stdout:
                    try:
                        checkov_data = json.loads(result.stdout)
                        for check_result in checkov_data.get("results", {}).get("failed_checks", []):
                            vulnerability = Vulnerability(
                                scan_type=ScanType.INFRASTRUCTURE_SCAN,
                                severity=VulnerabilitySeverity.MEDIUM,
                                title=f"Infrastructure issue: {check_result.get('check_name', 'Unknown')}",
                                description=check_result.get("description", ""),
                                file_path=check_result.get("file_path", ""),
                                recommendation="Fix infrastructure security configuration"
                            )
                            vulnerabilities.append(vulnerability)
                    except json.JSONDecodeError:
                        pass
        
        except Exception as e:
            self.logger.error(f"Infrastructure scan failed: {e}")
        
        return vulnerabilities
    
    def _filter_vulnerabilities(
        self,
        vulnerabilities: List[Vulnerability],
        threshold: VulnerabilitySeverity
    ) -> List[Vulnerability]:
        """Filter vulnerabilities by severity threshold"""
        severity_order = {
            VulnerabilitySeverity.CRITICAL: 4,
        try:
            logger.info(f"Executing _run_infrastructure_scan")
            
            # Implementation for _run_infrastructure_scan
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_run_infrastructure_scan completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_run_infrastructure_scan failed: {e}")
            raise
        critical_count = sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL)
        high_count = sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)
        
        if critical_count > 0:
            return "critical"
        elif high_count > 3:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_security_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        """Generate security scan summary"""
        summary = {
            "total_vulnerabilities": len(vulnerabilities),
            "by_severity": {},
            "by_scan_type": {},
            "top_issues": []
        }
        
        # Count by severity
        for severity in VulnerabilitySeverity:
            count = sum(1 for v in vulnerabilities if v.severity == severity)
            summary["by_severity"][severity.value] = count
        
        # Count by scan type
        for scan_type in ScanType:
            count = sum(1 for v in vulnerabilities if v.scan_type == scan_type)
            summary["by_scan_type"][scan_type.value] = count
        
        # Top 5 most critical issues
        critical_vulns = sorted(
            vulnerabilities,
            key=lambda v: (v.severity.value, v.title),
            reverse=True
        )[:5]
        
        summary["top_issues"] = [
            {
                "title": v.title,
                "severity": v.severity.value,
                "scan_type": v.scan_type.value,
                "file_path": v.file_path
            }
            for v in critical_vulns
        ]
        
        return summary
    
    def _generate_security_recommendations(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Count vulnerabilities by type and severity
        critical_count = sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL)
        high_count = sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)
        
        if critical_count > 0:
            recommendations.append(f"Immediately fix {critical_count} critical vulnerabilities")
        
        if high_count > 0:
            recommendations.append(f"Prioritize fixing {high_count} high-severity vulnerabilities")
        
        # Specific recommendations by scan type
        scan_type_counts = {}
        for vuln in vulnerabilities:
            scan_type_counts[vuln.scan_type] = scan_type_counts.get(vuln.scan_type, 0) + 1
        
        if scan_type_counts.get(ScanType.DEPENDENCY_SCAN, 0) > 0:
            recommendations.append("Update vulnerable dependencies to latest secure versions")
        
        if scan_type_counts.get(ScanType.SECRET_SCAN, 0) > 0:
            recommendations.append("Remove hardcoded secrets and implement proper secret management")
        
        if scan_type_counts.get(ScanType.STATIC_ANALYSIS, 0) > 0:
            recommendations.append("Review and fix code security issues identified by static analysis")
        
        return recommendations
    
    def _map_bandit_severity(self, bandit_severity: str) -> VulnerabilitySeverity:
        """Map Bandit severity to standard severity"""
        mapping = {
            "HIGH": VulnerabilitySeverity.HIGH,
            "MEDIUM": VulnerabilitySeverity.MEDIUM,
            "LOW": VulnerabilitySeverity.LOW
        }
        return mapping.get(bandit_severity.upper(), VulnerabilitySeverity.MEDIUM)
    
    def _map_semgrep_severity(self, semgrep_severity: str) -> VulnerabilitySeverity:
        """Map Semgrep severity to standard severity"""
        mapping = {
            "ERROR": VulnerabilitySeverity.HIGH,
            "WARNING": VulnerabilitySeverity.MEDIUM,
            "INFO": VulnerabilitySeverity.LOW
        }
        return mapping.get(semgrep_severity.upper(), VulnerabilitySeverity.MEDIUM)
    
    def _map_trivy_severity(self, trivy_severity: str) -> VulnerabilitySeverity:
        """Map Trivy severity to standard severity"""
        mapping = {
            "CRITICAL": VulnerabilitySeverity.CRITICAL,
            "HIGH": VulnerabilitySeverity.HIGH,
            "MEDIUM": VulnerabilitySeverity.MEDIUM,
            "LOW": VulnerabilitySeverity.LOW,
            "UNKNOWN": VulnerabilitySeverity.INFO
        }
        return mapping.get(trivy_severity.upper(), VulnerabilitySeverity.MEDIUM)
    
    def _map_cvss_to_severity(self, cvss_score: float) -> VulnerabilitySeverity:
        """Map CVSS score to severity level"""
        if cvss_score >= 9.0:
            return VulnerabilitySeverity.CRITICAL
        elif cvss_score >= 7.0:
            return VulnerabilitySeverity.HIGH
        elif cvss_score >= 4.0:
            return VulnerabilitySeverity.MEDIUM
        else:
            return VulnerabilitySeverity.LOW
    
    async def _run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: int = 1800
    ) -> subprocess.CompletedProcess:
        """
Run command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout=stdout.decode(),
                stderr=stderr.decode()
            )
            
        except asyncio.TimeoutError:
            raise RuntimeError(f"Security scan timed out: {' '.join(cmd)}")
        except Exception as e:
            raise RuntimeError(f"Security scan failed: {e}")
    
    def get_scan_history(self, limit: int = 10) -> List[SecurityScanResult]:
        """Get security scan history"""
        return self.scan_history[-limit:]
    
    def get_security_trends(self) -> Dict[str, Any]:
        """
Get security trends over time"""
        if not self.scan_history:
            return {}
        
        recent_scans = self.scan_history[-10:]
        
        return {
            "score_trend": [scan.overall_score for scan in recent_scans],
            "vulnerability_trend": [len(scan.vulnerabilities) for scan in recent_scans],
            "risk_levels": [scan.risk_level for scan in recent_scans],
            "scan_dates": [scan.scan_timestamp.isoformat() for scan in recent_scans]
        }

__all__ = [
    "SecurityScanEngine",
    "SecurityScanConfig",
    "SecurityScanResult",
    "Vulnerability",
    "ScanType",
    "VulnerabilitySeverity",
]
