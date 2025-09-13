"""Security Scanner Core - Core Security Management System
========================================================

Core security scanning infrastructure for Ainflue integrations.
Provides the main SecurityScanner class and result management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
import re
import ssl
import socket
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlparse
import ipaddress
import base64
import jwt
import json

import aiohttp
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import ssl
import certifi

logger = logging.getLogger(__name__)

class SecurityRiskLevel(Enum):
    """Security risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""
    WEAK_AUTHENTICATION = "weak_authentication"
    INSECURE_TRANSPORT = "insecure_transport"
    EXPOSED_CREDENTIALS = "exposed_credentials"
    WEAK_ENCRYPTION = "weak_encryption"
    INSUFFICIENT_AUTHORIZATION = "insufficient_authorization"
    DATA_EXPOSURE = "data_exposure"
    INJECTION_VULNERABILITY = "injection_vulnerability"
    CONFIGURATION_WEAKNESS = "configuration_weakness"
    CERTIFICATE_ISSUE = "certificate_issue"
    RATE_LIMITING_BYPASS = "rate_limiting_bypass"
    SESSION_VULNERABILITY = "session_vulnerability"
    CORS_MISCONFIGURATION = "cors_misconfiguration"

class SecurityStandard(Enum):
    """Security standards for compliance."""
    OWASP_TOP_10 = "owasp_top_10"
    NIST = "nist"
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"

@dataclass
class SecurityVulnerability:
    """Security vulnerability finding."""
    vulnerability_id: str
    vulnerability_type: VulnerabilityType
    risk_level: SecurityRiskLevel
    title: str
    description: str
    affected_endpoint: Optional[str] = None
    affected_integration: Optional[str] = None
    
    # Technical details
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Remediation
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    
    # Compliance
    compliance_violations: List[SecurityStandard] = field(default_factory=list)
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_verified: datetime = field(default_factory=datetime.utcnow)
    false_positive: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass 
class SecurityScanResult:
    """Results of a security scan."""
    scan_id: str
    target: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    scan_status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    
    # Scan statistics
    risk_score: float = 0.0
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    
    # Scan configuration
    scan_type: str = "full"
    scan_options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationSecurityProfile:
    """Security profile for an integration."""
    integration_name: str
    last_scan_date: Optional[datetime] = None
    security_score: float = 0.0
    
    # Vulnerability summary
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    medium_vulnerabilities: int = 0
    low_vulnerabilities: int = 0
    
    # Security metrics
    ssl_grade: str = "unknown"
    authentication_strength: str = "unknown"
    data_protection_level: str = "unknown"
    
    # Compliance status
    compliance_status: Dict[SecurityStandard, bool] = field(default_factory=dict)
    
    # Scan history
    scan_history: List[str] = field(default_factory=list)

class SecurityScanner:
    """Comprehensive security scanner for integrations."""
    
    def __init__(
        self,
        scan_interval: int = 86400,  # 24 hours
        max_concurrent_scans: int = 5,
        vulnerability_db_update_interval: int = 3600,  # 1 hour
        enable_real_time_monitoring: bool = True,
        compliance_standards: Optional[List[SecurityStandard]] = None
    ):
        self.scan_interval = scan_interval
        self.max_concurrent_scans = max_concurrent_scans
        self.vulnerability_db_update_interval = vulnerability_db_update_interval
        self.enable_real_time_monitoring = enable_real_time_monitoring
        self.compliance_standards = compliance_standards or [
            SecurityStandard.OWASP_TOP_10,
            SecurityStandard.SOC2,
            SecurityStandard.GDPR
        ]
        
        # Internal state
        self.scan_results: Dict[str, SecurityScanResult] = {}
        self.vulnerabilities: Dict[str, SecurityVulnerability] = {}
        self.integration_profiles: Dict[str, IntegrationSecurityProfile] = {}
        self.security_patterns: Dict[str, List[str]] = {}
        self.vulnerability_signatures: Dict[str, Dict[str, Any]] = {}
        
        # Async components
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.scheduled_scan_task: Optional[asyncio.Task] = None
        self.vulnerability_update_task: Optional[asyncio.Task] = None
        self.scanning_enabled: bool = True
        
        logger.info("Security scanner initialized with compliance standards: %s", 
                   [std.value for std in self.compliance_standards])

    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security patterns for vulnerability detection."""
        return {
            'exposed_keys': [
                r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{16,})',
                r'(?i)(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
                r'(?i)(database[_-]?url|db[_-]?url)["\']?\s*[:=]\s*["\']?([^\s"\']+)',
                r'(?i)(private[_-]?key)["\']?\s*[:=]\s*["\']?([^\s"\']+)',
            ],
            'sql_injection': [
                r'(?i)(union\s+select|or\s+1\s*=\s*1|\'\s+or\s+\'\w+\'\s*=\s*\'\w+)',
                r'(?i)(drop\s+table|delete\s+from|update\s+.*\s+set)',
                r'(?i)(exec\s*\(|sp_executesql|xp_cmdshell)',
            ],
            'xss_vectors': [
                r'<script[^>]*>.*?</script>',
                r'javascript:[^"\s]*',
                r'on\w+\s*=\s*["\'][^"\']*["\']',
                r'(?i)(alert\s*\(|confirm\s*\(|prompt\s*\()',
            ],
            'cors_misconfig': [
                r'Access-Control-Allow-Origin:\s*\*',
                r'Access-Control-Allow-Credentials:\s*true',
                r'Access-Control-Allow-Methods:\s*.*\*',
            ]
        }

    def _load_vulnerability_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load vulnerability signatures database."""
        return {
            'weak_tls': {
                'versions': ['TLSv1', 'TLSv1.1', 'SSLv2', 'SSLv3'],
                'ciphers': ['RC4', 'DES', '3DES', 'MD5'],
                'risk_level': SecurityRiskLevel.MEDIUM
            },
            'insecure_headers': {
                'missing_headers': [
                    'Strict-Transport-Security',
                    'X-Content-Type-Options',
                    'X-Frame-Options',
                    'X-XSS-Protection',
                    'Content-Security-Policy'
                ],
                'insecure_values': {
                    'X-Frame-Options': ['ALLOW-FROM'],
                    'X-XSS-Protection': ['0']
                },
                'risk_level': SecurityRiskLevel.LOW
            },
            'authentication_bypass': {
                'patterns': [
                    r'(?i)admin["\']?\s*[:=]\s*["\']?admin',
                    r'(?i)test["\']?\s*[:=]\s*["\']?test',
                    r'(?i)guest["\']?\s*[:=]\s*["\']?guest',
                ],
                'risk_level': SecurityRiskLevel.CRITICAL
            }
        }

    async def initialize(self) -> None:
        """Initialize the security scanner."""
        try:
            # Load security patterns and signatures
            self.security_patterns = self._load_security_patterns()
            self.vulnerability_signatures = self._load_vulnerability_signatures()
            
            # Create HTTP session with security settings
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context(cafile=certifi.where()),
                limit=100,
                limit_per_host=20
            )
            
            self.http_session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'AinflueSecurity/1.0 SecurityScanner'
                }
            )
            
            # Start background tasks
            if self.enable_real_time_monitoring:
                self.scheduled_scan_task = asyncio.create_task(self._scheduled_scan_loop())
                self.vulnerability_update_task = asyncio.create_task(self._update_vulnerability_db())
                
            logger.info("Security scanner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security scanner: {e}")
            raise

    async def _calculate_scan_metrics(self, scan_result: SecurityScanResult) -> None:
        """Calculate scan metrics and risk score."""
        total_vulns = len(scan_result.vulnerabilities)
        if total_vulns == 0:
            scan_result.risk_score = 0.0
            return
            
        # Calculate risk score based on vulnerability severity
        risk_weights = {
            SecurityRiskLevel.CRITICAL: 10.0,
            SecurityRiskLevel.HIGH: 5.0,
            SecurityRiskLevel.MEDIUM: 2.0,
            SecurityRiskLevel.LOW: 1.0
        }
        
        total_risk = sum(risk_weights.get(vuln.risk_level, 1.0) 
                        for vuln in scan_result.vulnerabilities)
        max_possible_risk = total_vulns * risk_weights[SecurityRiskLevel.CRITICAL]
        
        scan_result.risk_score = min(100.0, (total_risk / max_possible_risk) * 100)
        scan_result.total_checks = total_vulns + scan_result.passed_checks
        scan_result.failed_checks = total_vulns

    async def _update_integration_profile(
        self, 
        integration_name: str, 
        scan_result: SecurityScanResult
    ) -> None:
        """Update integration security profile."""
        if integration_name not in self.integration_profiles:
            self.integration_profiles[integration_name] = IntegrationSecurityProfile(
                integration_name=integration_name
            )
            
        profile = self.integration_profiles[integration_name]
        profile.last_scan_date = datetime.utcnow()
        profile.security_score = 100.0 - scan_result.risk_score
        
        # Count vulnerabilities by severity
        profile.critical_vulnerabilities = len([v for v in scan_result.vulnerabilities 
                                              if v.risk_level == SecurityRiskLevel.CRITICAL])
        profile.high_vulnerabilities = len([v for v in scan_result.vulnerabilities 
                                          if v.risk_level == SecurityRiskLevel.HIGH])
        profile.medium_vulnerabilities = len([v for v in scan_result.vulnerabilities 
                                            if v.risk_level == SecurityRiskLevel.MEDIUM])
        profile.low_vulnerabilities = len([v for v in scan_result.vulnerabilities 
                                         if v.risk_level == SecurityRiskLevel.LOW])
        
        # Add to scan history
        profile.scan_history.append(scan_result.scan_id)
        if len(profile.scan_history) > 10:  # Keep last 10 scans
            profile.scan_history = profile.scan_history[-10:]

    async def _scheduled_scan_loop(self) -> None:
        """Background task for scheduled security scans."""
        while self.scanning_enabled:
            try:
                await asyncio.sleep(self.scan_interval)
                
                # Scan all registered integrations
                for integration_name in self.integration_profiles.keys():
                    if self.scanning_enabled:
                        logger.info(f"Starting scheduled scan for {integration_name}")
                        # Note: This would need actual integration endpoints
                        # await self.scan_integration(integration_name, "https://api.example.com", "dummy_key")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled scan loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _update_vulnerability_db(self) -> None:
        """Background task to update vulnerability database."""
        while self.scanning_enabled:
            try:
                await asyncio.sleep(self.vulnerability_db_update_interval)
                
                # Update vulnerability signatures (placeholder)
                logger.debug("Updating vulnerability database...")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating vulnerability database: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def get_vulnerability_report(
        self, 
        integration_name: Optional[str] = None,
        risk_level: Optional[SecurityRiskLevel] = None,
        include_resolved: bool = False
    ) -> Dict[str, Any]:
        """Generate vulnerability report."""
        vulnerabilities = list(self.vulnerabilities.values())
        
        # Filter by integration
        if integration_name:
            vulnerabilities = [v for v in vulnerabilities 
                             if v.affected_integration == integration_name]
            
        # Filter by risk level
        if risk_level:
            vulnerabilities = [v for v in vulnerabilities 
                             if v.risk_level == risk_level]
            
        # Filter resolved vulnerabilities
        if not include_resolved:
            vulnerabilities = [v for v in vulnerabilities if not v.resolved]
            
        # Generate report
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'filter_criteria': {
                'integration': integration_name,
                'risk_level': risk_level.value if risk_level else None,
                'include_resolved': include_resolved
            },
            'summary': {
                'total_vulnerabilities': len(vulnerabilities),
                'by_risk_level': {},
                'by_integration': {},
                'by_type': {}
            },
            'vulnerabilities': [asdict(vuln) for vuln in vulnerabilities]
        }
        
        # Calculate summaries
        for vuln in vulnerabilities:
            # By risk level
            risk_key = vuln.risk_level.value
            report['summary']['by_risk_level'][risk_key] = \
                report['summary']['by_risk_level'].get(risk_key, 0) + 1
                
            # By integration
            if vuln.affected_integration:
                integration_key = vuln.affected_integration
                report['summary']['by_integration'][integration_key] = \
                    report['summary']['by_integration'].get(integration_key, 0) + 1
                    
            # By type
            type_key = vuln.vulnerability_type.value
            report['summary']['by_type'][type_key] = \
                report['summary']['by_type'].get(type_key, 0) + 1
        
        return report

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Generate security dashboard data."""
        dashboard = {
            'overview': {
                'total_integrations': len(self.integration_profiles),
                'total_vulnerabilities': len(self.vulnerabilities),
                'recent_scans': len([s for s in self.scan_results.values() 
                                  if s.completed_at and 
                                  datetime.utcnow() - s.completed_at < timedelta(days=7)])
            },
            'risk_summary': {
                'critical': len([v for v in self.vulnerabilities.values() 
                               if v.risk_level == SecurityRiskLevel.CRITICAL]),
                'high': len([v for v in self.vulnerabilities.values() 
                           if v.risk_level == SecurityRiskLevel.HIGH]),
                'medium': len([v for v in self.vulnerabilities.values() 
                             if v.risk_level == SecurityRiskLevel.MEDIUM]),
                'low': len([v for v in self.vulnerabilities.values() 
                          if v.risk_level == SecurityRiskLevel.LOW])
            },
            'integration_scores': {
                name: profile.security_score 
                for name, profile in self.integration_profiles.items()
            },
            'compliance_status': {},
            'recent_scans': [
                {
                    'scan_id': result.scan_id,
                    'target': result.target,
                    'started_at': result.started_at.isoformat(),
                    'status': result.scan_status,
                    'vulnerabilities': len(result.vulnerabilities)
                }
                for result in sorted(self.scan_results.values(), 
                                   key=lambda x: x.started_at, reverse=True)[:10]
            ]
        }
        
        return dashboard

    async def health_check(self) -> Dict[str, Any]:
        """Perform security scanner health check."""
        health = {
            "status": "healthy",
            "integrations_monitored": len(self.integration_profiles),
            "vulnerabilities_tracked": len(self.vulnerabilities),
            "recent_scans": len(self.scan_results),
            "scanning_enabled": self.scanning_enabled,
            "issues": []
        }
        
        # Check for critical vulnerabilities
        critical_vulns = [v for v in self.vulnerabilities.values() 
                         if v.risk_level == SecurityRiskLevel.CRITICAL and not v.resolved]
        if critical_vulns:
            health["issues"].append(f"{len(critical_vulns)} unresolved critical vulnerabilities")
            health["status"] = "critical"
            
        # Check scanner functionality
        if not self.http_session:
            health["issues"].append("HTTP session not initialized")
            health["status"] = "degraded"
            
        return health

    async def shutdown(self) -> None:
        """Shutdown security scanner gracefully."""
        logger.info("Shutting down security scanner...")
        
        # Cancel background tasks
        for task in [self.scheduled_scan_task, self.vulnerability_update_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        # Close HTTP session
        if self.http_session:
            await self.http_session.close()
            
        logger.info("Security scanner shutdown completed")

    def __repr__(self) -> str:
        return f"SecurityScanner(integrations={len(self.integration_profiles)}, vulnerabilities={len(self.vulnerabilities)})"


# Global security scanner instance
security_scanner = SecurityScanner()

# Export main classes and functions
__all__ = [
    "SecurityScanner",
    "SecurityVulnerability",
    "SecurityScanResult", 
    "IntegrationSecurityProfile",
    "SecurityRiskLevel",
    "VulnerabilityType",
    "SecurityStandard",
    "security_scanner"
]