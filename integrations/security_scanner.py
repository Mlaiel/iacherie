"""Security Scanner - Integration Security Validation System
=========================================================

Comprehensive security scanning system for integration endpoints, API keys,
authentication flows, and compliance validation.

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
import asyncio_dns
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
    """Security scan result."""
    scan_id: str
    target: str
    scan_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Results
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    risk_score: int = 0  # 0-100
    
    # Statistics
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Status
    scan_status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None

@dataclass
class IntegrationSecurityProfile:
    """Security profile for an integration."""
    integration_name: str
    last_scan: Optional[datetime] = None
    security_score: int = 100  # 100 = secure, 0 = very insecure
    
    # Vulnerability counts
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    
    # Security features
    uses_https: bool = True
    uses_oauth: bool = False
    uses_api_keys: bool = False
    uses_jwt: bool = False
    rate_limited: bool = False
    
    # Compliance status
    compliance_status: Dict[SecurityStandard, bool] = field(default_factory=dict)
    
    # Certificate info
    certificate_valid: bool = True
    certificate_expires: Optional[datetime] = None

class SecurityScanner:
    """Comprehensive security scanner for integrations."""
    
    def __init__(
        self,
        scan_interval: int = 24 * 3600,  # 24 hours
        enable_vulnerability_db: bool = True,
        max_concurrent_scans: int = 5
    ):
        self.scan_interval = scan_interval
        self.enable_vulnerability_db = enable_vulnerability_db
        self.max_concurrent_scans = max_concurrent_scans
        
        # Security data
        self.vulnerabilities: Dict[str, SecurityVulnerability] = {}
        self.scan_results: Dict[str, SecurityScanResult] = {}
        self.integration_profiles: Dict[str, IntegrationSecurityProfile] = {}
        
        # Scanning configuration
        self.scanning_enabled = True
        self.scan_semaphore = asyncio.Semaphore(max_concurrent_scans)
        
        # Background tasks
        self.scheduled_scan_task = None
        self.vulnerability_update_task = None
        
        # Security patterns and rules
        self.security_patterns = self._load_security_patterns()
        self.vulnerability_signatures = self._load_vulnerability_signatures()
        
        # HTTP session for scanning
        self.http_session = None
        
        logger.info("Security Scanner initialized")

    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security patterns for vulnerability detection."""
        return {
            'exposed_credentials': [
                r'(?i)(api[_-]?key|password|secret|token)\s*[=:]\s*["\']?[a-zA-Z0-9]{8,}["\']?',
                r'(?i)bearer\s+[a-zA-Z0-9_-]{10,}',
                r'(?i)basic\s+[a-zA-Z0-9+/=]{10,}',
                r'sk_[a-zA-Z0-9]{20,}',  # Stripe secret key
                r'rk_[a-zA-Z0-9]{20,}',  # Restricted key
            ],
            'weak_encryption': [
                r'(?i)ssl_?v[23]',
                r'(?i)tls_?v1\.0',
                r'(?i)rc4',
                r'(?i)md5',
                r'(?i)sha1(?!_)',
            ],
            'injection_patterns': [
                r'(?i)select\s+.*\s+from\s+',
                r'(?i)union\s+select',
                r'(?i)insert\s+into\s+',
                r'(?i)delete\s+from\s+',
                r'(?i)drop\s+table\s+',
                r'<script[^>]*>',
                r'javascript:',
                r'eval\s*\(',
            ],
            'cors_issues': [
                r'access-control-allow-origin:\s*\*',
                r'access-control-allow-credentials:\s*true',
            ]
        }

    def _load_vulnerability_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load known vulnerability signatures."""
        return {
            'weak_jwt_secret': {
                'pattern': r'jwt\.encode\([^,]+,\s*["\'][^"\']{1,10}["\']',
                'risk_level': SecurityRiskLevel.HIGH,
                'description': 'JWT signed with weak secret'
            },
            'hardcoded_api_key': {
                'pattern': r'(?i)(api[_-]?key|secret)\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
                'risk_level': SecurityRiskLevel.CRITICAL,
                'description': 'Hardcoded API key detected'
            },
            'insecure_random': {
                'pattern': r'random\.(random|randint)\(',
                'risk_level': SecurityRiskLevel.MEDIUM,
                'description': 'Use of insecure random number generator'
            },
            'sql_injection_risk': {
                'pattern': r'(?i)execute\s*\(\s*["\'][^"\']*%s[^"\']*["\']',
                'risk_level': SecurityRiskLevel.HIGH,
                'description': 'Potential SQL injection vulnerability'
            }
        }

    async def initialize(self) -> None:
        """Initialize security scanner."""
        try:
            # Create HTTP session with security headers
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context(cafile=certifi.where()),
                limit=100,
                limit_per_host=30,
                keepalive_timeout=300
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            self.http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Ainflue-SecurityScanner/1.0',
                    'Accept': 'application/json, text/plain, */*',
                }
            )
            
            # Start background tasks
            if self.scanning_enabled:
                self.scheduled_scan_task = asyncio.create_task(self._scheduled_scan_loop())
                
            if self.enable_vulnerability_db:
                self.vulnerability_update_task = asyncio.create_task(self._update_vulnerability_db())
                
            logger.info("Security Scanner initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize security scanner: {e}")
            raise

    async def scan_integration(
        self,
        integration_name: str,
        base_url: str,
        api_key: Optional[str] = None,
        additional_endpoints: Optional[List[str]] = None
    ) -> SecurityScanResult:
        """Perform comprehensive security scan of an integration."""
        scan_id = f"scan_{integration_name}_{int(datetime.utcnow().timestamp())}"
        
        scan_result = SecurityScanResult(
            scan_id=scan_id,
            target=base_url,
            scan_type="integration_scan",
            started_at=datetime.utcnow()
        )
        
        try:
            async with self.scan_semaphore:
                logger.info(f"Starting security scan for {integration_name}")
                
                # Transport layer security scan
                transport_vulns = await self._scan_transport_security(base_url)
                scan_result.vulnerabilities.extend(transport_vulns)
                
                # API endpoint security scan
                endpoint_vulns = await self._scan_api_endpoints(
                    base_url, api_key, additional_endpoints or []
                )
                scan_result.vulnerabilities.extend(endpoint_vulns)
                
                # Authentication mechanism scan
                auth_vulns = await self._scan_authentication(base_url, api_key)
                scan_result.vulnerabilities.extend(auth_vulns)
                
                # Certificate validation
                cert_vulns = await self._scan_certificates(base_url)
                scan_result.vulnerabilities.extend(cert_vulns)
                
                # Configuration security scan
                config_vulns = await self._scan_configuration(integration_name)
                scan_result.vulnerabilities.extend(config_vulns)
                
                # Calculate risk score and statistics
                await self._calculate_scan_metrics(scan_result)
                
                # Update integration security profile
                await self._update_integration_profile(integration_name, scan_result)
                
                scan_result.scan_status = "completed"
                scan_result.completed_at = datetime.utcnow()
                
                # Store results
                self.scan_results[scan_id] = scan_result
                
                logger.info(f"Security scan completed for {integration_name}: {len(scan_result.vulnerabilities)} vulnerabilities found")
                
        except Exception as e:
            scan_result.scan_status = "failed"
            scan_result.error_message = str(e)
            scan_result.completed_at = datetime.utcnow()
            logger.error(f"Security scan failed for {integration_name}: {e}")
            
        return scan_result

    async def _scan_transport_security(self, base_url: str) -> List[SecurityVulnerability]:
        """Scan transport layer security."""
        vulnerabilities = []
        
        try:
            parsed_url = urlparse(base_url)
            
            # Check if HTTPS is used
            if parsed_url.scheme != 'https':
                vulnerability = SecurityVulnerability(
                    vulnerability_id=f"transport_insecure_{parsed_url.netloc}",
                    vulnerability_type=VulnerabilityType.INSECURE_TRANSPORT,
                    risk_level=SecurityRiskLevel.HIGH,
                    title="Insecure Transport Protocol",
                    description="API endpoint does not use HTTPS encryption",
                    affected_endpoint=base_url,
                    remediation="Configure the API to use HTTPS instead of HTTP",
                    compliance_violations=[SecurityStandard.OWASP_TOP_10, SecurityStandard.PCI_DSS]
                )
                vulnerabilities.append(vulnerability)
                
            # Test SSL/TLS configuration for HTTPS endpoints
            if parsed_url.scheme == 'https':
                ssl_vulns = await self._test_ssl_configuration(parsed_url.netloc, parsed_url.port or 443)
                vulnerabilities.extend(ssl_vulns)
                
        except Exception as e:
            logger.error(f"Error scanning transport security for {base_url}: {e}")
            
        return vulnerabilities

    async def _test_ssl_configuration(self, hostname: str, port: int) -> List[SecurityVulnerability]:
        """Test SSL/TLS configuration."""
        vulnerabilities = []
        
        try:
            # Create SSL context for testing
            context = ssl.create_default_context()
            
            # Test connection
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    # Check TLS version
                    if version in ['TLSv1', 'TLSv1.1']:
                        vulnerability = SecurityVulnerability(
                            vulnerability_id=f"tls_version_{hostname}",
                            vulnerability_type=VulnerabilityType.WEAK_ENCRYPTION,
                            risk_level=SecurityRiskLevel.MEDIUM,
                            title="Weak TLS Version",
                            description=f"Server supports outdated TLS version: {version}",
                            affected_endpoint=f"https://{hostname}:{port}",
                            remediation="Configure server to support only TLS 1.2 or higher",
                            evidence={'tls_version': version}
                        )
                        vulnerabilities.append(vulnerability)
                        
                    # Check cipher strength
                    if cipher and len(cipher[1]) < 128:
                        vulnerability = SecurityVulnerability(
                            vulnerability_id=f"weak_cipher_{hostname}",
                            vulnerability_type=VulnerabilityType.WEAK_ENCRYPTION,
                            risk_level=SecurityRiskLevel.MEDIUM,
                            title="Weak Cipher Suite",
                            description=f"Server uses weak cipher: {cipher[0]}",
                            affected_endpoint=f"https://{hostname}:{port}",
                            remediation="Configure server to use strong cipher suites (AES-256 or higher)",
                            evidence={'cipher': cipher[0], 'key_length': cipher[1]}
                        )
                        vulnerabilities.append(vulnerability)
                        
        except Exception as e:
            logger.error(f"Error testing SSL configuration for {hostname}:{port}: {e}")
            
        return vulnerabilities

    async def _scan_api_endpoints(
        self,
        base_url: str,
        api_key: Optional[str],
        additional_endpoints: List[str]
    ) -> List[SecurityVulnerability]:
        """Scan API endpoints for security issues."""
        vulnerabilities = []
        
        if not self.http_session:
            return vulnerabilities
            
        # Standard endpoints to test
        test_endpoints = [
            '/',
            '/api',
            '/v1',
            '/health',
            '/status',
            '/admin',
            '/debug',
            '/.well-known/security.txt',
        ] + additional_endpoints
        
        for endpoint in test_endpoints:
            try:
                url = f"{base_url.rstrip('/')}{endpoint}"
                
                # Test without authentication
                vulns = await self._test_endpoint_security(url, None)
                vulnerabilities.extend(vulns)
                
                # Test with authentication if available
                if api_key:
                    vulns = await self._test_endpoint_security(url, api_key)
                    vulnerabilities.extend(vulns)
                    
            except Exception as e:
                logger.error(f"Error scanning endpoint {endpoint}: {e}")
                
        return vulnerabilities

    async def _test_endpoint_security(
        self,
        url: str,
        api_key: Optional[str]
    ) -> List[SecurityVulnerability]:
        """Test individual endpoint security."""
        vulnerabilities = []
        
        try:
            headers = {}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
                
            # Test GET request
            async with self.http_session.get(url, headers=headers) as response:
                # Check security headers
                header_vulns = await self._check_security_headers(url, response.headers)
                vulnerabilities.extend(header_vulns)
                
                # Check for information disclosure
                if response.status == 200:
                    text = await response.text()
                    info_vulns = await self._check_information_disclosure(url, text, response.headers)
                    vulnerabilities.extend(info_vulns)
                    
                # Check CORS configuration
                cors_vulns = await self._check_cors_configuration(url, response.headers)
                vulnerabilities.extend(cors_vulns)
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout scanning endpoint {url}")
        except Exception as e:
            logger.error(f"Error testing endpoint {url}: {e}")
            
        return vulnerabilities

    async def _check_security_headers(
        self,
        url: str,
        headers: Dict[str, str]
    ) -> List[SecurityVulnerability]:
        """Check for missing security headers."""
        vulnerabilities = []
        
        required_headers = {
            'strict-transport-security': {
                'title': 'Missing Strict-Transport-Security Header',
                'risk': SecurityRiskLevel.MEDIUM,
                'description': 'Missing HSTS header allows downgrade attacks'
            },
            'x-frame-options': {
                'title': 'Missing X-Frame-Options Header', 
                'risk': SecurityRiskLevel.MEDIUM,
                'description': 'Missing X-Frame-Options header allows clickjacking attacks'
            },
            'x-content-type-options': {
                'title': 'Missing X-Content-Type-Options Header',
                'risk': SecurityRiskLevel.LOW,
                'description': 'Missing X-Content-Type-Options header allows MIME sniffing'
            },
            'content-security-policy': {
                'title': 'Missing Content-Security-Policy Header',
                'risk': SecurityRiskLevel.MEDIUM,
                'description': 'Missing CSP header allows XSS attacks'
            }
        }
        
        for header_name, header_info in required_headers.items():
            if header_name not in [h.lower() for h in headers.keys()]:
                vulnerability = SecurityVulnerability(
                    vulnerability_id=f"missing_header_{header_name}_{urlparse(url).netloc}",
                    vulnerability_type=VulnerabilityType.CONFIGURATION_WEAKNESS,
                    risk_level=header_info['risk'],
                    title=header_info['title'],
                    description=header_info['description'],
                    affected_endpoint=url,
                    remediation=f"Add {header_name} header to API responses"
                )
                vulnerabilities.append(vulnerability)
                
        return vulnerabilities

    async def _check_information_disclosure(
        self,
        url: str,
        response_text: str,
        headers: Dict[str, str]
    ) -> List[SecurityVulnerability]:
        """Check for information disclosure vulnerabilities."""
        vulnerabilities = []
        
        # Check for exposed credentials in response
        for pattern_name, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response_text):
                    vulnerability = SecurityVulnerability(
                        vulnerability_id=f"info_disclosure_{pattern_name}_{urlparse(url).netloc}",
                        vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
                        risk_level=SecurityRiskLevel.HIGH,
                        title=f"Information Disclosure: {pattern_name.replace('_', ' ').title()}",
                        description=f"Sensitive information exposed in API response",
                        affected_endpoint=url,
                        remediation="Remove sensitive information from API responses",
                        evidence={'pattern': pattern}
                    )
                    vulnerabilities.append(vulnerability)
                    break  # Only report once per pattern type
                    
        # Check server header for version disclosure
        server_header = headers.get('server', '')
        if server_header and any(version_pattern in server_header.lower() 
                               for version_pattern in ['apache/2', 'nginx/1', 'iis/7', 'iis/8']):
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"server_version_{urlparse(url).netloc}",
                vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
                risk_level=SecurityRiskLevel.LOW,
                title="Server Version Disclosure",
                description="Server header reveals software version information",
                affected_endpoint=url,
                remediation="Configure server to hide version information",
                evidence={'server_header': server_header}
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def _check_cors_configuration(
        self,
        url: str,
        headers: Dict[str, str]
    ) -> List[SecurityVulnerability]:
        """Check CORS configuration for security issues."""
        vulnerabilities = []
        
        cors_origin = headers.get('access-control-allow-origin', '')
        cors_credentials = headers.get('access-control-allow-credentials', '').lower()
        
        # Check for wildcard origin with credentials
        if cors_origin == '*' and cors_credentials == 'true':
            vulnerability = SecurityVulnerability(
                vulnerability_id=f"cors_wildcard_{urlparse(url).netloc}",
                vulnerability_type=VulnerabilityType.CORS_MISCONFIGURATION,
                risk_level=SecurityRiskLevel.HIGH,
                title="Dangerous CORS Configuration",
                description="CORS allows any origin with credentials enabled",
                affected_endpoint=url,
                remediation="Configure CORS to allow specific origins instead of wildcard",
                evidence={'cors_origin': cors_origin, 'cors_credentials': cors_credentials}
            )
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities

    async def _scan_authentication(
        self,
        base_url: str,
        api_key: Optional[str]
    ) -> List[SecurityVulnerability]:
        """Scan authentication mechanisms."""
        vulnerabilities = []
        
        if not api_key:
            return vulnerabilities
            
        try:
            # Test API key strength
            if len(api_key) < 20:
                vulnerability = SecurityVulnerability(
                    vulnerability_id=f"weak_api_key_{urlparse(base_url).netloc}",
                    vulnerability_type=VulnerabilityType.WEAK_AUTHENTICATION,
                    risk_level=SecurityRiskLevel.MEDIUM,
                    title="Weak API Key",
                    description="API key appears to be too short for secure authentication",
                    affected_endpoint=base_url,
                    remediation="Use longer, more complex API keys (minimum 32 characters)"
                )
                vulnerabilities.append(vulnerability)
                
            # Test if API key is JWT
            if api_key.count('.') == 2:  # Likely a JWT
                jwt_vulns = await self._analyze_jwt_security(base_url, api_key)
                vulnerabilities.extend(jwt_vulns)
                
        except Exception as e:
            logger.error(f"Error scanning authentication for {base_url}: {e}")
            
        return vulnerabilities

    async def _analyze_jwt_security(
        self,
        base_url: str,
        jwt_token: str
    ) -> List[SecurityVulnerability]:
        """Analyze JWT token security."""
        vulnerabilities = []
        
        try:
            # Decode JWT header without verification
            header = jwt.get_unverified_header(jwt_token)
            payload = jwt.decode(jwt_token, options={"verify_signature": False})
            
            # Check algorithm
            alg = header.get('alg', '').lower()
            if alg in ['none', 'hs256']:
                vulnerability = SecurityVulnerability(
                    vulnerability_id=f"weak_jwt_alg_{urlparse(base_url).netloc}",
                    vulnerability_type=VulnerabilityType.WEAK_AUTHENTICATION,
                    risk_level=SecurityRiskLevel.HIGH if alg == 'none' else SecurityRiskLevel.MEDIUM,
                    title=f"Weak JWT Algorithm: {alg.upper()}",
                    description=f"JWT uses weak signing algorithm: {alg}",
                    affected_endpoint=base_url,
                    remediation="Use stronger algorithms like RS256 or ES256",
                    evidence={'algorithm': alg}
                )
                vulnerabilities.append(vulnerability)
                
            # Check expiration
            exp = payload.get('exp')
            if exp:
                exp_time = datetime.fromtimestamp(exp)
                if exp_time > datetime.utcnow() + timedelta(days=365):
                    vulnerability = SecurityVulnerability(
                        vulnerability_id=f"long_jwt_exp_{urlparse(base_url).netloc}",
                        vulnerability_type=VulnerabilityType.WEAK_AUTHENTICATION,
                        risk_level=SecurityRiskLevel.MEDIUM,
                        title="Long JWT Expiration",
                        description="JWT has unusually long expiration time",
                        affected_endpoint=base_url,
                        remediation="Use shorter JWT expiration times (hours, not years)",
                        evidence={'expiration': exp_time.isoformat()}
                    )
                    vulnerabilities.append(vulnerability)
                    
        except Exception as e:
            logger.error(f"Error analyzing JWT: {e}")
            
        return vulnerabilities

    async def _scan_certificates(self, base_url: str) -> List[SecurityVulnerability]:
        """Scan SSL certificates."""
        vulnerabilities = []
        
        if not base_url.startswith('https://'):
            return vulnerabilities
            
        try:
            parsed_url = urlparse(base_url)
            hostname = parsed_url.netloc
            port = parsed_url.port or 443
            
            # Get certificate
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert_chain()[0]
                    cert = x509.load_der_x509_certificate(cert_der)
                    
                    # Check expiration
                    expires = cert.not_valid_after
                    if expires < datetime.utcnow() + timedelta(days=30):
                        risk_level = SecurityRiskLevel.CRITICAL if expires < datetime.utcnow() else SecurityRiskLevel.HIGH
                        vulnerability = SecurityVulnerability(
                            vulnerability_id=f"cert_expiration_{hostname}",
                            vulnerability_type=VulnerabilityType.CERTIFICATE_ISSUE,
                            risk_level=risk_level,
                            title="Certificate Expiration",
                            description=f"SSL certificate expires soon: {expires}",
                            affected_endpoint=base_url,
                            remediation="Renew SSL certificate before expiration",
                            evidence={'expires': expires.isoformat()}
                        )
                        vulnerabilities.append(vulnerability)
                        
                    # Check key strength
                    public_key = cert.public_key()
                    if hasattr(public_key, 'key_size') and public_key.key_size < 2048:
                        vulnerability = SecurityVulnerability(
                            vulnerability_id=f"weak_cert_key_{hostname}",
                            vulnerability_type=VulnerabilityType.WEAK_ENCRYPTION,
                            risk_level=SecurityRiskLevel.MEDIUM,
                            title="Weak Certificate Key",
                            description=f"Certificate uses weak key size: {public_key.key_size} bits",
                            affected_endpoint=base_url,
                            remediation="Use certificates with at least 2048-bit keys",
                            evidence={'key_size': public_key.key_size}
                        )
                        vulnerabilities.append(vulnerability)
                        
        except Exception as e:
            logger.error(f"Error scanning certificates for {base_url}: {e}")
            
        return vulnerabilities

    async def _scan_configuration(self, integration_name: str) -> List[SecurityVulnerability]:
        """Scan integration configuration for security issues."""
        vulnerabilities = []
        
        try:
            # This would typically scan configuration files, environment variables, etc.
            # For now, we'll do basic checks
            
            # Check for common insecure configurations
            insecure_configs = {
                'DEBUG': 'Debug mode enabled in production',
                'DISABLE_SSL_VERIFY': 'SSL verification disabled',
                'ALLOW_ALL_ORIGINS': 'CORS allows all origins',
                'NO_RATE_LIMIT': 'Rate limiting disabled'
            }
            
            for config_key, description in insecure_configs.items():
                # This would check actual configuration
                # For demonstration, we'll skip actual checks
                pass
                
        except Exception as e:
            logger.error(f"Error scanning configuration for {integration_name}: {e}")
            
        return vulnerabilities

    async def _calculate_scan_metrics(self, scan_result: SecurityScanResult) -> None:
        """Calculate scan metrics and risk scores."""
        # Count vulnerabilities by severity
        for vuln in scan_result.vulnerabilities:
            if vuln.risk_level == SecurityRiskLevel.CRITICAL:
                scan_result.critical_count += 1
            elif vuln.risk_level == SecurityRiskLevel.HIGH:
                scan_result.high_count += 1
            elif vuln.risk_level == SecurityRiskLevel.MEDIUM:
                scan_result.medium_count += 1
            elif vuln.risk_level == SecurityRiskLevel.LOW:
                scan_result.low_count += 1
                
        # Calculate risk score (0-100)
        risk_score = 0
        risk_score += scan_result.critical_count * 25
        risk_score += scan_result.high_count * 15
        risk_score += scan_result.medium_count * 8
        risk_score += scan_result.low_count * 3
        
        scan_result.risk_score = min(100, risk_score)

    async def _update_integration_profile(
        self,
        integration_name: str,
        scan_result: SecurityScanResult
    ) -> None:
        """Update integration security profile."""
        profile = self.integration_profiles.get(
            integration_name,
            IntegrationSecurityProfile(integration_name=integration_name)
        )
        
        profile.last_scan = scan_result.completed_at or datetime.utcnow()
        profile.security_score = max(0, 100 - scan_result.risk_score)
        profile.total_vulnerabilities = len(scan_result.vulnerabilities)
        profile.critical_vulnerabilities = scan_result.critical_count
        profile.high_vulnerabilities = scan_result.high_count
        
        # Determine security features from scan
        if scan_result.target.startswith('https://'):
            profile.uses_https = True
            
        # Store profile
        self.integration_profiles[integration_name] = profile

    async def _scheduled_scan_loop(self) -> None:
        """Scheduled security scanning loop."""
        while True:
            try:
                await asyncio.sleep(self.scan_interval)
                
                # Scan all registered integrations
                for integration_name, profile in self.integration_profiles.items():
                    if (not profile.last_scan or 
                        datetime.utcnow() - profile.last_scan > timedelta(seconds=self.scan_interval)):
                        
                        # This would need integration endpoint configuration
                        # For now, we'll skip automatic scanning
                        logger.info(f"Scheduled scan needed for {integration_name}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled scan loop: {e}")

    async def _update_vulnerability_db(self) -> None:
        """Update vulnerability database."""
        while True:
            try:
                await asyncio.sleep(24 * 3600)  # Daily update
                
                # This would typically fetch from CVE databases, OWASP, etc.
                logger.info("Updating vulnerability database...")
                
                # Update vulnerability signatures
                # This would be implemented with real vulnerability feeds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating vulnerability database: {e}")

    async def get_vulnerability_report(
        self,
        integration_name: Optional[str] = None,
        risk_level: Optional[SecurityRiskLevel] = None
    ) -> Dict[str, Any]:
        """Generate vulnerability report."""
        vulnerabilities = list(self.vulnerabilities.values())
        
        # Filter by integration
        if integration_name:
            vulnerabilities = [v for v in vulnerabilities if v.affected_integration == integration_name]
            
        # Filter by risk level
        if risk_level:
            vulnerabilities = [v for v in vulnerabilities if v.risk_level == risk_level]
            
        # Generate report
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'integration_name': integration_name,
            'risk_level_filter': risk_level.value if risk_level else None,
            'total_vulnerabilities': len(vulnerabilities),
            'vulnerability_breakdown': {
                'critical': len([v for v in vulnerabilities if v.risk_level == SecurityRiskLevel.CRITICAL]),
                'high': len([v for v in vulnerabilities if v.risk_level == SecurityRiskLevel.HIGH]),
                'medium': len([v for v in vulnerabilities if v.risk_level == SecurityRiskLevel.MEDIUM]),
                'low': len([v for v in vulnerabilities if v.risk_level == SecurityRiskLevel.LOW])
            },
            'vulnerabilities': [asdict(v) for v in vulnerabilities[:50]]  # Limit to first 50
        }
        
        return report

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data."""
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