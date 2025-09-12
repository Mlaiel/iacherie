"""
Enterprise Security Scanner - Comprehensive Security Analysis and Threat Detection
=================================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Roles: Security Expert + Backend Senior + DevOps Expert + Lead Dev IA
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive security scanning capabilities including
vulnerability detection, threat analysis, compliance checking, and security monitoring.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import secrets
import base64

# Third-party imports with fallbacks
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import cryptography
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class SecurityVulnerability:
    """Security vulnerability details"""
    id: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # OWASP category or custom
    affected_component: str
    location: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityScanResult:
    """Security scan result summary"""
    scan_id: str
    scan_type: str
    target: str
    start_time: datetime
    end_time: datetime
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    scan_metadata: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ThreatIndicator:
    """Threat indicator details"""
    indicator_type: str  # ip, domain, hash, pattern
    value: str
    threat_type: str  # malware, phishing, spam, etc.
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceCheck:
    """Compliance check result"""
    standard: str  # GDPR, HIPAA, PCI-DSS, etc.
    requirement: str
    status: str  # PASS, FAIL, NOT_APPLICABLE, MANUAL_REVIEW
    description: str
    evidence: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)


class VulnerabilityScanner:
    """Core vulnerability scanning engine"""
    
    def __init__(self):
        self.common_vulnerabilities = {
            'sql_injection': {
                'patterns': [
                    r"(\'|\")[;,\s]*[\w\s]*(\s*union\s+select|\s*or\s+1\s*=\s*1|\s*drop\s+table)",
                    r"(\s*;\s*)(drop|delete|insert|update|select)\s+",
                    r"(\s*\'\s*or\s*\'\s*1\s*=\s*\'\s*1|\s*\'\s*or\s*1\s*=\s*1)",
                ],
                'severity': 'HIGH',
                'category': 'Injection'
            },
            'xss': {
                'patterns': [
                    r"<script[^>]*>.*?</script>",
                    r"javascript\s*:",
                    r"on\w+\s*=\s*[\"']",
                    r"<iframe[^>]*>",
                    r"<object[^>]*>",
                ],
                'severity': 'MEDIUM',
                'category': 'Cross-Site Scripting'
            },
            'path_traversal': {
                'patterns': [
                    r"\.\.[\\/]",
                    r"\.\.%2f",
                    r"%2e%2e%2f",
                    r"\.\.\\",
                ],
                'severity': 'HIGH',
                'category': 'Path Traversal'
            },
            'command_injection': {
                'patterns': [
                    r"[;&|`$]",
                    r"nc\s+-",
                    r"wget\s+",
                    r"curl\s+",
                    r"python\s+-c",
                    r"perl\s+-e",
                ],
                'severity': 'CRITICAL',
                'category': 'Command Injection'
            },
            'weak_crypto': {
                'patterns': [
                    r"md5\s*\(",
                    r"sha1\s*\(",
                    r"des[\s_]",
                    r"rc4[\s_]",
                    r"password\s*=\s*[\"'][^\"']{1,8}[\"']",
                ],
                'severity': 'MEDIUM',
                'category': 'Cryptographic Issues'
            }
        }
        
        self.sensitive_data_patterns = {
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'api_key': r'[A-Za-z0-9]{32,}',
            'private_key': r'-----BEGIN.*PRIVATE KEY-----',
            'password': r'password\s*[:=]\s*["\'][^"\']+["\']',
        }
        
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=',
            'Content-Security-Policy': 'default-src',
            'Referrer-Policy': ['no-referrer', 'strict-origin-when-cross-origin'],
        }
    
    def scan_code(self, code: str, filename: str = "") -> List[SecurityVulnerability]:
        """Scan code for vulnerabilities"""
        vulnerabilities = []
        
        for vuln_type, config in self.common_vulnerabilities.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    
                    vulnerability = SecurityVulnerability(
                        id=f"{vuln_type}_{hashlib.md5(f'{filename}_{line_num}_{match.group()}'.encode()).hexdigest()[:8]}",
                        title=f"{config['category']} Vulnerability",
                        description=f"Potential {vuln_type} vulnerability detected",
                        severity=config['severity'],
                        category=config['category'],
                        affected_component=filename or "code",
                        location=f"Line {line_num}",
                        evidence={
                            'matched_pattern': pattern,
                            'matched_text': match.group(),
                            'line_number': line_num,
                            'context': self._get_code_context(code, match.start(), match.end())
                        },
                        remediation=self._get_remediation_for_vuln_type(vuln_type)
                    )
                    vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def scan_dependencies(self, requirements_file: str) -> List[SecurityVulnerability]:
        """Scan dependencies for known vulnerabilities"""
        vulnerabilities = []
        
        if not os.path.exists(requirements_file):
            return vulnerabilities
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read()
            
            # Known vulnerable packages (simplified example)
            vulnerable_packages = {
                'django': {
                    'versions': ['<3.2.0'],
                    'cve': 'CVE-2021-44420',
                    'severity': 'HIGH',
                    'description': 'Potential XSS via admin interface'
                },
                'flask': {
                    'versions': ['<1.1.0'],
                    'cve': 'CVE-2019-1010083',
                    'severity': 'MEDIUM',
                    'description': 'Path traversal vulnerability'
                },
                'pillow': {
                    'versions': ['<8.3.2'],
                    'cve': 'CVE-2021-34552',
                    'severity': 'HIGH',
                    'description': 'Buffer overflow in image processing'
                }
            }
            
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    
                    if package_name.lower() in vulnerable_packages:
                        vuln_info = vulnerable_packages[package_name.lower()]
                        
                        vulnerability = SecurityVulnerability(
                            id=f"dep_{package_name}_{vuln_info['cve']}",
                            title=f"Vulnerable Dependency: {package_name}",
                            description=vuln_info['description'],
                            severity=vuln_info['severity'],
                            category='Vulnerable Dependencies',
                            affected_component=package_name,
                            location=requirements_file,
                            cve_id=vuln_info['cve'],
                            evidence={'requirement_line': line},
                            remediation=[f"Update {package_name} to latest version"]
                        )
                        vulnerabilities.append(vulnerability)
        
        except Exception as e:
            logging.error(f"Error scanning dependencies: {e}")
        
        return vulnerabilities
    
    def scan_configuration(self, config_data: Dict[str, Any], config_name: str = "") -> List[SecurityVulnerability]:
        """Scan configuration for security issues"""
        vulnerabilities = []
        
        # Check for insecure configurations
        insecure_configs = {
            'debug': {
                'check': lambda x: x.get('DEBUG', False) or x.get('debug', False),
                'severity': 'HIGH',
                'description': 'Debug mode should be disabled in production'
            },
            'secret_key': {
                'check': lambda x: len(str(x.get('SECRET_KEY', ''))) < 32,
                'severity': 'CRITICAL',
                'description': 'Secret key is too short or missing'
            },
            'ssl_disabled': {
                'check': lambda x: not x.get('USE_SSL', True) or not x.get('SECURE_SSL_REDIRECT', True),
                'severity': 'HIGH',
                'description': 'SSL/HTTPS should be enforced'
            },
            'weak_session': {
                'check': lambda x: x.get('SESSION_COOKIE_SECURE', False) is False,
                'severity': 'MEDIUM',
                'description': 'Session cookies should be secure'
            }
        }
        
        for check_name, check_config in insecure_configs.items():
            if check_config['check'](config_data):
                vulnerability = SecurityVulnerability(
                    id=f"config_{check_name}_{hashlib.md5(config_name.encode()).hexdigest()[:8]}",
                    title=f"Insecure Configuration: {check_name}",
                    description=check_config['description'],
                    severity=check_config['severity'],
                    category='Security Misconfiguration',
                    affected_component=config_name or "configuration",
                    evidence={'config_data': config_data},
                    remediation=[f"Fix {check_name} configuration issue"]
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def scan_sensitive_data(self, text: str, context: str = "") -> List[SecurityVulnerability]:
        """Scan for sensitive data exposure"""
        vulnerabilities = []
        
        for data_type, pattern in self.sensitive_data_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                vulnerability = SecurityVulnerability(
                    id=f"sensitive_{data_type}_{hashlib.md5(match.group().encode()).hexdigest()[:8]}",
                    title=f"Sensitive Data Exposure: {data_type}",
                    description=f"Potential {data_type} detected in {context}",
                    severity='HIGH' if data_type in ['credit_card', 'ssn', 'private_key'] else 'MEDIUM',
                    category='Sensitive Data Exposure',
                    affected_component=context or "text",
                    evidence={
                        'matched_text': match.group()[:10] + "***",  # Partially redacted
                        'pattern_type': data_type,
                        'position': match.span()
                    },
                    remediation=[
                        f"Remove or encrypt {data_type}",
                        "Implement proper data handling procedures",
                        "Add data loss prevention measures"
                    ]
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _get_code_context(self, code: str, start: int, end: int, context_lines: int = 2) -> str:
        """Get code context around vulnerability"""
        lines = code.split('\n')
        start_line = code[:start].count('\n')
        end_line = code[:end].count('\n')
        
        context_start = max(0, start_line - context_lines)
        context_end = min(len(lines), end_line + context_lines + 1)
        
        context = '\n'.join(lines[context_start:context_end])
        return context
    
    def _get_remediation_for_vuln_type(self, vuln_type: str) -> List[str]:
        """Get remediation steps for vulnerability type"""
        remediation_map = {
            'sql_injection': [
                "Use parameterized queries or prepared statements",
                "Implement input validation and sanitization",
                "Use ORM frameworks with built-in protection",
                "Apply principle of least privilege to database users"
            ],
            'xss': [
                "Encode output data properly",
                "Implement Content Security Policy (CSP)",
                "Validate and sanitize input data",
                "Use secure templating engines"
            ],
            'path_traversal': [
                "Validate and normalize file paths",
                "Use whitelist of allowed files/directories",
                "Implement proper access controls",
                "Avoid user input in file system operations"
            ],
            'command_injection': [
                "Avoid system calls with user input",
                "Use safe APIs instead of shell commands",
                "Implement strict input validation",
                "Apply sandboxing and least privilege"
            ],
            'weak_crypto': [
                "Use strong cryptographic algorithms (AES, SHA-256+)",
                "Implement proper key management",
                "Use cryptographically secure random number generators",
                "Regular security audits of cryptographic implementations"
            ]
        }
        
        return remediation_map.get(vuln_type, ["Implement security best practices", "Conduct security review"])


class NetworkScanner:
    """Network security scanning capabilities"""
    
    def __init__(self):
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
        self.timeout = 5
    
    def scan_port(self, host: str, port: int) -> Dict[str, Any]:
        """Scan a specific port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return {
                'host': host,
                'port': port,
                'status': 'open' if result == 0 else 'closed',
                'service': self._identify_service(port),
                'scan_time': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'status': 'error',
                'error': str(e),
                'scan_time': datetime.now().isoformat()
            }
    
    def scan_host(self, host: str, ports: List[int] = None) -> List[Dict[str, Any]]:
        """Scan multiple ports on a host"""
        ports = ports or self.common_ports
        results = []
        
        for port in ports:
            result = self.scan_port(host, port)
            results.append(result)
        
        return results
    
    async def async_scan_host(self, host: str, ports: List[int] = None) -> List[Dict[str, Any]]:
        """Async port scanning for better performance"""
        ports = ports or self.common_ports
        tasks = []
        
        for port in ports:
            task = asyncio.create_task(self._async_scan_port(host, port))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
    
    async def _async_scan_port(self, host: str, port: int) -> Dict[str, Any]:
        """Async port scan"""
        try:
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=self.timeout)
            writer.close()
            await writer.wait_closed()
            
            return {
                'host': host,
                'port': port,
                'status': 'open',
                'service': self._identify_service(port),
                'scan_time': datetime.now().isoformat()
            }
        except Exception:
            return {
                'host': host,
                'port': port,
                'status': 'closed',
                'scan_time': datetime.now().isoformat()
            }
    
    def check_ssl_certificate(self, host: str, port: int = 443) -> Dict[str, Any]:
        """Check SSL certificate details"""
        if not CRYPTOGRAPHY_AVAILABLE:
            return {'error': 'cryptography library not available'}
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert_der = ssock.getpeercert_chain()[0]
                    cert = x509.load_der_x509_certificate(cert_der.public_bytes(ssl.Encoding.DER))
                    
                    return {
                        'host': host,
                        'port': port,
                        'subject': cert.subject.rfc4514_string(),
                        'issuer': cert.issuer.rfc4514_string(),
                        'not_valid_before': cert.not_valid_before.isoformat(),
                        'not_valid_after': cert.not_valid_after.isoformat(),
                        'expires_in_days': (cert.not_valid_after - datetime.now()).days,
                        'serial_number': str(cert.serial_number),
                        'signature_algorithm': cert.signature_algorithm_oid._name,
                        'is_expired': cert.not_valid_after < datetime.now(),
                        'expires_soon': (cert.not_valid_after - datetime.now()).days < 30
                    }
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'error': str(e),
                'ssl_available': False
            }
    
    def _identify_service(self, port: int) -> str:
        """Identify service by port number"""
        services = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            993: 'IMAPS',
            995: 'POP3S'
        }
        return services.get(port, 'Unknown')


class WebApplicationScanner:
    """Web application security scanning"""
    
    def __init__(self):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for web scanning")
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'SecurityScanner/1.0'})
        self.timeout = 10
    
    def scan_url(self, url: str) -> List[SecurityVulnerability]:
        """Comprehensive web application scan"""
        vulnerabilities = []
        
        try:
            # Basic connectivity test
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            # Check security headers
            vulnerabilities.extend(self._check_security_headers(url, response))
            
            # Check for information disclosure
            vulnerabilities.extend(self._check_information_disclosure(url, response))
            
            # Test for common vulnerabilities
            vulnerabilities.extend(self._test_xss(url))
            vulnerabilities.extend(self._test_sql_injection(url))
            
            # Check SSL/TLS configuration
            if url.startswith('https://'):
                vulnerabilities.extend(self._check_ssl_configuration(url))
            
        except Exception as e:
            vulnerability = SecurityVulnerability(
                id=f"web_scan_error_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                title="Web Scan Error",
                description=f"Failed to scan {url}: {str(e)}",
                severity='INFO',
                category='Scan Issues',
                affected_component=url,
                evidence={'error': str(e)}
            )
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _check_security_headers(self, url: str, response: requests.Response) -> List[SecurityVulnerability]:
        """Check for missing or misconfigured security headers"""
        vulnerabilities = []
        headers = response.headers
        
        for header, expected_value in VulnerabilityScanner().security_headers.items():
            if header not in headers:
                vulnerability = SecurityVulnerability(
                    id=f"missing_header_{header}_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                    title=f"Missing Security Header: {header}",
                    description=f"Security header {header} is missing",
                    severity='MEDIUM' if header in ['X-Content-Type-Options', 'X-Frame-Options'] else 'LOW',
                    category='Security Headers',
                    affected_component=url,
                    evidence={'missing_header': header},
                    remediation=[f"Add {header} header with appropriate value"]
                )
                vulnerabilities.append(vulnerability)
            elif isinstance(expected_value, list):
                # Check if header value is in allowed list
                if headers[header] not in expected_value:
                    vulnerability = SecurityVulnerability(
                        id=f"weak_header_{header}_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                        title=f"Weak Security Header: {header}",
                        description=f"Security header {header} has weak configuration",
                        severity='MEDIUM',
                        category='Security Headers',
                        affected_component=url,
                        evidence={'header_value': headers[header], 'expected': expected_value},
                        remediation=[f"Configure {header} header properly"]
                    )
                    vulnerabilities.append(vulnerability)
            elif isinstance(expected_value, str) and expected_value not in headers.get(header, ''):
                vulnerability = SecurityVulnerability(
                    id=f"incomplete_header_{header}_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                    title=f"Incomplete Security Header: {header}",
                    description=f"Security header {header} is incomplete",
                    severity='MEDIUM',
                    category='Security Headers',
                    affected_component=url,
                    evidence={'header_value': headers.get(header), 'expected_pattern': expected_value},
                    remediation=[f"Complete {header} header configuration"]
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _check_information_disclosure(self, url: str, response: requests.Response) -> List[SecurityVulnerability]:
        """Check for information disclosure issues"""
        vulnerabilities = []
        
        # Check for verbose error messages
        error_patterns = [
            r'stack trace',
            r'database error',
            r'sql.*error',
            r'warning.*line.*\d+',
            r'fatal error',
            r'exception.*trace'
        ]
        
        content = response.text.lower()
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                vulnerability = SecurityVulnerability(
                    id=f"info_disclosure_{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                    title="Information Disclosure",
                    description=f"Verbose error messages detected: {pattern}",
                    severity='MEDIUM',
                    category='Information Disclosure',
                    affected_component=url,
                    evidence={'pattern': pattern},
                    remediation=[
                        "Implement custom error pages",
                        "Disable debug mode in production",
                        "Log errors securely without exposing details"
                    ]
                )
                vulnerabilities.append(vulnerability)
        
        # Check server information disclosure
        server_header = response.headers.get('Server', '')
        if server_header and any(tech in server_header.lower() for tech in ['apache', 'nginx', 'iis']):
            vulnerability = SecurityVulnerability(
                id=f"server_disclosure_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                title="Server Information Disclosure",
                description=f"Server information disclosed: {server_header}",
                severity='LOW',
                category='Information Disclosure',
                affected_component=url,
                evidence={'server_header': server_header},
                remediation=["Remove or modify Server header to hide version information"]
            )
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _test_xss(self, url: str) -> List[SecurityVulnerability]:
        """Test for XSS vulnerabilities"""
        vulnerabilities = []
        
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
        ]
        
        # Parse URL to find parameters
        parsed = urllib.parse.urlparse(url)
        if parsed.query:
            params = urllib.parse.parse_qs(parsed.query)
            
            for param in params:
                for payload in xss_payloads:
                    test_params = params.copy()
                    test_params[param] = [payload]
                    test_query = urllib.parse.urlencode(test_params, doseq=True)
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{test_query}"
                    
                    try:
                        response = self.session.get(test_url, timeout=self.timeout)
                        if payload in response.text:
                            vulnerability = SecurityVulnerability(
                                id=f"xss_{param}_{hashlib.md5(payload.encode()).hexdigest()[:8]}",
                                title=f"XSS Vulnerability in parameter: {param}",
                                description=f"Reflected XSS vulnerability detected in parameter {param}",
                                severity='HIGH',
                                category='Cross-Site Scripting',
                                affected_component=f"{url} (parameter: {param})",
                                evidence={
                                    'parameter': param,
                                    'payload': payload,
                                    'test_url': test_url
                                },
                                remediation=[
                                    "Encode output data properly",
                                    "Implement Content Security Policy (CSP)",
                                    "Validate and sanitize input data"
                                ]
                            )
                            vulnerabilities.append(vulnerability)
                            break  # Found vulnerability, no need to test other payloads
                    except Exception:
                        continue
        
        return vulnerabilities
    
    def _test_sql_injection(self, url: str) -> List[SecurityVulnerability]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        sql_payloads = [
            "'",
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
        ]
        
        # Parse URL to find parameters
        parsed = urllib.parse.urlparse(url)
        if parsed.query:
            params = urllib.parse.parse_qs(parsed.query)
            
            for param in params:
                for payload in sql_payloads:
                    test_params = params.copy()
                    test_params[param] = [payload]
                    test_query = urllib.parse.urlencode(test_params, doseq=True)
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{test_query}"
                    
                    try:
                        response = self.session.get(test_url, timeout=self.timeout)
                        
                        # Check for SQL error patterns
                        sql_errors = [
                            'sql syntax', 'mysql error', 'postgresql error',
                            'oracle error', 'sqlite error', 'database error'
                        ]
                        
                        content_lower = response.text.lower()
                        if any(error in content_lower for error in sql_errors):
                            vulnerability = SecurityVulnerability(
                                id=f"sqli_{param}_{hashlib.md5(payload.encode()).hexdigest()[:8]}",
                                title=f"SQL Injection Vulnerability in parameter: {param}",
                                description=f"SQL injection vulnerability detected in parameter {param}",
                                severity='CRITICAL',
                                category='Injection',
                                affected_component=f"{url} (parameter: {param})",
                                evidence={
                                    'parameter': param,
                                    'payload': payload,
                                    'test_url': test_url
                                },
                                remediation=[
                                    "Use parameterized queries or prepared statements",
                                    "Implement input validation and sanitization",
                                    "Apply principle of least privilege to database users"
                                ]
                            )
                            vulnerabilities.append(vulnerability)
                            break  # Found vulnerability, no need to test other payloads
                    except Exception:
                        continue
        
        return vulnerabilities
    
    def _check_ssl_configuration(self, url: str) -> List[SecurityVulnerability]:
        """Check SSL/TLS configuration"""
        vulnerabilities = []
        
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443
            
            # Check certificate
            context = ssl.create_default_context()
            
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiration
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry < 30:
                        severity = 'HIGH' if days_until_expiry < 7 else 'MEDIUM'
                        vulnerability = SecurityVulnerability(
                            id=f"ssl_expiry_{hashlib.md5(host.encode()).hexdigest()[:8]}",
                            title="SSL Certificate Expiring Soon",
                            description=f"SSL certificate expires in {days_until_expiry} days",
                            severity=severity,
                            category='SSL/TLS Configuration',
                            affected_component=f"{host}:{port}",
                            evidence={
                                'expires_in_days': days_until_expiry,
                                'expiry_date': not_after.isoformat()
                            },
                            remediation=["Renew SSL certificate before expiration"]
                        )
                        vulnerabilities.append(vulnerability)
                    
                    # Check for weak ciphers (simplified check)
                    cipher = ssock.cipher()
                    if cipher and len(cipher) >= 3:
                        cipher_name = cipher[0]
                        if any(weak in cipher_name.upper() for weak in ['RC4', 'DES', 'MD5']):
                            vulnerability = SecurityVulnerability(
                                id=f"weak_cipher_{hashlib.md5(cipher_name.encode()).hexdigest()[:8]}",
                                title="Weak SSL Cipher",
                                description=f"Weak cipher detected: {cipher_name}",
                                severity='MEDIUM',
                                category='SSL/TLS Configuration',
                                affected_component=f"{host}:{port}",
                                evidence={'cipher': cipher_name},
                                remediation=["Configure strong SSL ciphers only"]
                            )
                            vulnerabilities.append(vulnerability)
        
        except Exception as e:
            vulnerability = SecurityVulnerability(
                id=f"ssl_check_error_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                title="SSL Configuration Check Failed",
                description=f"Failed to check SSL configuration: {str(e)}",
                severity='INFO',
                category='SSL/TLS Configuration',
                affected_component=url,
                evidence={'error': str(e)}
            )
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities


class ComplianceChecker:
    """Check compliance with security standards"""
    
    def __init__(self):
        self.compliance_frameworks = {
            'OWASP_TOP_10': {
                'A01_Broken_Access_Control': self._check_access_control,
                'A02_Cryptographic_Failures': self._check_cryptographic_failures,
                'A03_Injection': self._check_injection,
                'A04_Insecure_Design': self._check_insecure_design,
                'A05_Security_Misconfiguration': self._check_security_misconfiguration,
                'A06_Vulnerable_Components': self._check_vulnerable_components,
                'A07_Authentication_Failures': self._check_authentication_failures,
                'A08_Software_Integrity_Failures': self._check_software_integrity,
                'A09_Logging_Failures': self._check_logging_failures,
                'A10_SSRF': self._check_ssrf
            },
            'GDPR': {
                'data_protection': self._check_gdpr_data_protection,
                'consent_management': self._check_gdpr_consent,
                'data_subject_rights': self._check_gdpr_rights,
                'breach_notification': self._check_gdpr_breach_notification
            }
        }
    
    def check_compliance(self, framework: str, scan_results: List[SecurityVulnerability]) -> List[ComplianceCheck]:
        """Check compliance against specific framework"""
        if framework not in self.compliance_frameworks:
            raise ValueError(f"Unsupported compliance framework: {framework}")
        
        compliance_results = []
        checks = self.compliance_frameworks[framework]
        
        for check_name, check_function in checks.items():
            try:
                result = check_function(scan_results)
                compliance_results.append(result)
            except Exception as e:
                result = ComplianceCheck(
                    standard=framework,
                    requirement=check_name,
                    status='MANUAL_REVIEW',
                    description=f"Error checking {check_name}: {str(e)}",
                    remediation_steps=[f"Manual review required for {check_name}"]
                )
                compliance_results.append(result)
        
        return compliance_results
    
    def _check_access_control(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A01 - Broken Access Control"""
        access_control_issues = [
            v for v in vulnerabilities 
            if 'access' in v.category.lower() or 'authorization' in v.category.lower()
        ]
        
        status = 'FAIL' if access_control_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A01_Broken_Access_Control',
            status=status,
            description='Check for access control vulnerabilities',
            evidence=[v.title for v in access_control_issues],
            remediation_steps=[
                'Implement proper access controls',
                'Use principle of least privilege',
                'Regular access control testing'
            ] if access_control_issues else []
        )
    
    def _check_cryptographic_failures(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A02 - Cryptographic Failures"""
        crypto_issues = [
            v for v in vulnerabilities 
            if 'crypto' in v.category.lower() or 'ssl' in v.category.lower() or 'weak' in v.title.lower()
        ]
        
        status = 'FAIL' if crypto_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A02_Cryptographic_Failures',
            status=status,
            description='Check for cryptographic implementation issues',
            evidence=[v.title for v in crypto_issues],
            remediation_steps=[
                'Use strong cryptographic algorithms',
                'Implement proper key management',
                'Regular cryptographic review'
            ] if crypto_issues else []
        )
    
    def _check_injection(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A03 - Injection"""
        injection_issues = [
            v for v in vulnerabilities 
            if 'injection' in v.category.lower() or v.category.lower() in ['injection', 'cross-site scripting']
        ]
        
        status = 'FAIL' if injection_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A03_Injection',
            status=status,
            description='Check for injection vulnerabilities',
            evidence=[v.title for v in injection_issues],
            remediation_steps=[
                'Use parameterized queries',
                'Implement input validation',
                'Output encoding'
            ] if injection_issues else []
        )
    
    def _check_insecure_design(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A04 - Insecure Design"""
        # This is more of an architectural review, simplified here
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A04_Insecure_Design',
            status='MANUAL_REVIEW',
            description='Requires manual architectural security review',
            remediation_steps=['Conduct threat modeling', 'Security architecture review']
        )
    
    def _check_security_misconfiguration(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A05 - Security Misconfiguration"""
        config_issues = [
            v for v in vulnerabilities 
            if 'misconfiguration' in v.category.lower() or 'configuration' in v.category.lower()
        ]
        
        status = 'FAIL' if config_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A05_Security_Misconfiguration',
            status=status,
            description='Check for security misconfigurations',
            evidence=[v.title for v in config_issues],
            remediation_steps=[
                'Review security configurations',
                'Implement security hardening',
                'Regular configuration audits'
            ] if config_issues else []
        )
    
    def _check_vulnerable_components(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A06 - Vulnerable and Outdated Components"""
        component_issues = [
            v for v in vulnerabilities 
            if 'dependencies' in v.category.lower() or 'component' in v.category.lower()
        ]
        
        status = 'FAIL' if component_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A06_Vulnerable_Components',
            status=status,
            description='Check for vulnerable components',
            evidence=[v.title for v in component_issues],
            remediation_steps=[
                'Update vulnerable components',
                'Implement dependency scanning',
                'Regular security updates'
            ] if component_issues else []
        )
    
    def _check_authentication_failures(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A07 - Identification and Authentication Failures"""
        auth_issues = [
            v for v in vulnerabilities 
            if 'authentication' in v.category.lower() or 'password' in v.title.lower()
        ]
        
        status = 'FAIL' if auth_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A07_Authentication_Failures',
            status=status,
            description='Check for authentication issues',
            evidence=[v.title for v in auth_issues],
            remediation_steps=[
                'Implement strong authentication',
                'Multi-factor authentication',
                'Secure password policies'
            ] if auth_issues else []
        )
    
    def _check_software_integrity(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A08 - Software and Data Integrity Failures"""
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A08_Software_Integrity_Failures',
            status='MANUAL_REVIEW',
            description='Requires manual review of CI/CD and update mechanisms',
            remediation_steps=['Implement code signing', 'Secure CI/CD pipelines']
        )
    
    def _check_logging_failures(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A09 - Security Logging and Monitoring Failures"""
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A09_Logging_Failures',
            status='MANUAL_REVIEW',
            description='Requires manual review of logging and monitoring implementation',
            remediation_steps=['Implement comprehensive logging', 'Security monitoring']
        )
    
    def _check_ssrf(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check OWASP A10 - Server-Side Request Forgery"""
        ssrf_issues = [
            v for v in vulnerabilities 
            if 'ssrf' in v.title.lower() or 'server-side request' in v.description.lower()
        ]
        
        status = 'FAIL' if ssrf_issues else 'PASS'
        
        return ComplianceCheck(
            standard='OWASP_TOP_10',
            requirement='A10_SSRF',
            status=status,
            description='Check for SSRF vulnerabilities',
            evidence=[v.title for v in ssrf_issues],
            remediation_steps=[
                'Validate and sanitize URLs',
                'Implement allowlist for external requests',
                'Network segmentation'
            ] if ssrf_issues else []
        )
    
    def _check_gdpr_data_protection(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check GDPR data protection requirements"""
        data_protection_issues = [
            v for v in vulnerabilities 
            if 'sensitive data' in v.category.lower() or 'encryption' in v.title.lower()
        ]
        
        status = 'FAIL' if data_protection_issues else 'PASS'
        
        return ComplianceCheck(
            standard='GDPR',
            requirement='data_protection',
            status=status,
            description='Check data protection and privacy measures',
            evidence=[v.title for v in data_protection_issues],
            remediation_steps=[
                'Implement data encryption',
                'Data minimization',
                'Privacy by design'
            ] if data_protection_issues else []
        )
    
    def _check_gdpr_consent(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check GDPR consent management"""
        return ComplianceCheck(
            standard='GDPR',
            requirement='consent_management',
            status='MANUAL_REVIEW',
            description='Requires manual review of consent mechanisms',
            remediation_steps=['Implement clear consent mechanisms', 'Consent withdrawal options']
        )
    
    def _check_gdpr_rights(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check GDPR data subject rights"""
        return ComplianceCheck(
            standard='GDPR',
            requirement='data_subject_rights',
            status='MANUAL_REVIEW',
            description='Requires manual review of data subject rights implementation',
            remediation_steps=['Implement right to access', 'Right to deletion', 'Data portability']
        )
    
    def _check_gdpr_breach_notification(self, vulnerabilities: List[SecurityVulnerability]) -> ComplianceCheck:
        """Check GDPR breach notification requirements"""
        return ComplianceCheck(
            standard='GDPR',
            requirement='breach_notification',
            status='MANUAL_REVIEW',
            description='Requires manual review of breach notification procedures',
            remediation_steps=['Implement breach detection', '72-hour notification procedure']
        )


class SecurityScanner:
    """Main security scanner class orchestrating all scanning capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.vulnerability_scanner = VulnerabilityScanner()
        self.network_scanner = NetworkScanner()
        self.compliance_checker = ComplianceChecker()
        
        # Configure logging
        logging.basicConfig(
            level=self.config.get('log_level', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize web scanner if requests is available
        self.web_scanner = None
        if REQUESTS_AVAILABLE:
            self.web_scanner = WebApplicationScanner()
    
    def scan_code_repository(self, repo_path: str) -> SecurityScanResult:
        """Scan entire code repository"""
        scan_id = f"code_scan_{int(time.time())}"
        start_time = datetime.now()
        
        vulnerabilities = []
        
        try:
            repo_path = Path(repo_path)
            
            # Scan Python files
            for py_file in repo_path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    file_vulns = self.vulnerability_scanner.scan_code(code, str(py_file))
                    vulnerabilities.extend(file_vulns)
                    
                    # Check for sensitive data
                    sensitive_vulns = self.vulnerability_scanner.scan_sensitive_data(code, str(py_file))
                    vulnerabilities.extend(sensitive_vulns)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to scan {py_file}: {e}")
            
            # Scan requirements files
            for req_file in repo_path.rglob("requirements*.txt"):
                dep_vulns = self.vulnerability_scanner.scan_dependencies(str(req_file))
                vulnerabilities.extend(dep_vulns)
            
            # Scan configuration files
            for config_file in repo_path.rglob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    config_vulns = self.vulnerability_scanner.scan_configuration(config_data, str(config_file))
                    vulnerabilities.extend(config_vulns)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to scan config {config_file}: {e}")
        
        except Exception as e:
            self.logger.error(f"Repository scan failed: {e}")
        
        end_time = datetime.now()
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(vulnerabilities)
        
        return SecurityScanResult(
            scan_id=scan_id,
            scan_type='code_repository',
            target=str(repo_path),
            start_time=start_time,
            end_time=end_time,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            recommendations=recommendations
        )
    
    def scan_web_application(self, url: str) -> SecurityScanResult:
        """Scan web application"""
        if not self.web_scanner:
            raise RuntimeError("Web scanning requires requests library")
        
        scan_id = f"web_scan_{int(time.time())}"
        start_time = datetime.now()
        
        vulnerabilities = self.web_scanner.scan_url(url)
        
        end_time = datetime.now()
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(vulnerabilities)
        
        return SecurityScanResult(
            scan_id=scan_id,
            scan_type='web_application',
            target=url,
            start_time=start_time,
            end_time=end_time,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            recommendations=recommendations
        )
    
    def scan_network_host(self, host: str, ports: List[int] = None) -> SecurityScanResult:
        """Scan network host"""
        scan_id = f"network_scan_{int(time.time())}"
        start_time = datetime.now()
        
        # Port scan
        port_results = self.network_scanner.scan_host(host, ports)
        
        # SSL certificate check for HTTPS
        ssl_result = self.network_scanner.check_ssl_certificate(host, 443)
        
        # Convert port scan results to vulnerabilities
        vulnerabilities = []
        
        for port_result in port_results:
            if port_result['status'] == 'open':
                service = port_result.get('service', 'Unknown')
                
                # Check for potentially risky open ports
                risky_ports = {21: 'FTP', 23: 'Telnet', 135: 'RPC', 139: 'NetBIOS', 445: 'SMB'}
                
                if port_result['port'] in risky_ports:
                    vulnerability = SecurityVulnerability(
                        id=f"open_port_{port_result['port']}_{host}",
                        title=f"Potentially Risky Open Port: {port_result['port']} ({service})",
                        description=f"Port {port_result['port']} ({service}) is open and may pose security risks",
                        severity='MEDIUM',
                        category='Network Security',
                        affected_component=f"{host}:{port_result['port']}",
                        evidence=port_result,
                        remediation=[f"Review necessity of {service} service", "Implement proper access controls"]
                    )
                    vulnerabilities.append(vulnerability)
        
        # Process SSL results
        if 'error' not in ssl_result:
            if ssl_result.get('expires_soon', False):
                vulnerability = SecurityVulnerability(
                    id=f"ssl_expiry_{host}",
                    title="SSL Certificate Expiring Soon",
                    description=f"SSL certificate expires in {ssl_result.get('expires_in_days', 0)} days",
                    severity='HIGH' if ssl_result.get('expires_in_days', 30) < 7 else 'MEDIUM',
                    category='SSL/TLS',
                    affected_component=f"{host}:443",
                    evidence=ssl_result,
                    remediation=["Renew SSL certificate"]
                )
                vulnerabilities.append(vulnerability)
        
        end_time = datetime.now()
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)
        
        return SecurityScanResult(
            scan_id=scan_id,
            scan_type='network_host',
            target=host,
            start_time=start_time,
            end_time=end_time,
            vulnerabilities=vulnerabilities,
            scan_metadata={'port_results': port_results, 'ssl_result': ssl_result},
            risk_score=risk_score,
            recommendations=self._generate_recommendations(vulnerabilities)
        )
    
    def check_compliance(self, scan_result: SecurityScanResult, frameworks: List[str]) -> Dict[str, List[ComplianceCheck]]:
        """Check compliance against security frameworks"""
        compliance_results = {}
        
        for framework in frameworks:
            try:
                checks = self.compliance_checker.check_compliance(framework, scan_result.vulnerabilities)
                compliance_results[framework] = checks
            except Exception as e:
                self.logger.error(f"Compliance check failed for {framework}: {e}")
                compliance_results[framework] = []
        
        return compliance_results
    
    def generate_security_report(self, scan_result: SecurityScanResult, 
                               compliance_results: Dict[str, List[ComplianceCheck]] = None) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        # Vulnerability summary
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for vuln in scan_result.vulnerabilities:
            severity_counts[vuln.severity] += 1
            category_counts[vuln.category] += 1
        
        # Compliance summary
        compliance_summary = {}
        if compliance_results:
            for framework, checks in compliance_results.items():
                passed = sum(1 for check in checks if check.status == 'PASS')
                failed = sum(1 for check in checks if check.status == 'FAIL')
                manual_review = sum(1 for check in checks if check.status == 'MANUAL_REVIEW')
                
                compliance_summary[framework] = {
                    'passed': passed,
                    'failed': failed,
                    'manual_review': manual_review,
                    'total': len(checks),
                    'compliance_rate': (passed / len(checks) * 100) if checks else 0
                }
        
        return {
            'scan_summary': {
                'scan_id': scan_result.scan_id,
                'scan_type': scan_result.scan_type,
                'target': scan_result.target,
                'scan_duration': (scan_result.end_time - scan_result.start_time).total_seconds(),
                'total_vulnerabilities': len(scan_result.vulnerabilities),
                'risk_score': scan_result.risk_score
            },
            'vulnerability_summary': {
                'by_severity': dict(severity_counts),
                'by_category': dict(category_counts),
                'top_vulnerabilities': sorted(
                    scan_result.vulnerabilities,
                    key=lambda v: {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}.get(v.severity, 0),
                    reverse=True
                )[:10]
            },
            'compliance_summary': compliance_summary,
            'recommendations': scan_result.recommendations,
            'detailed_vulnerabilities': [
                {
                    'id': v.id,
                    'title': v.title,
                    'description': v.description,
                    'severity': v.severity,
                    'category': v.category,
                    'affected_component': v.affected_component,
                    'remediation': v.remediation
                } for v in scan_result.vulnerabilities
            ]
        }
    
    def _calculate_risk_score(self, vulnerabilities: List[SecurityVulnerability]) -> float:
        """Calculate overall risk score based on vulnerabilities"""
        if not vulnerabilities:
            return 0.0
        
        severity_weights = {
            'CRITICAL': 10.0,
            'HIGH': 7.5,
            'MEDIUM': 5.0,
            'LOW': 2.5,
            'INFO': 1.0
        }
        
        total_score = sum(severity_weights.get(v.severity, 1.0) for v in vulnerabilities)
        max_possible_score = len(vulnerabilities) * 10.0
        
        # Normalize to 0-100 scale
        risk_score = (total_score / max_possible_score) * 100
        return min(100.0, risk_score)
    
    def _generate_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate security recommendations based on vulnerabilities"""
        recommendations = set()
        
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for vuln in vulnerabilities:
            severity_counts[vuln.severity] += 1
            category_counts[vuln.category] += 1
            recommendations.update(vuln.remediation)
        
        # Add general recommendations based on patterns
        if severity_counts['CRITICAL'] > 0:
            recommendations.add("Address critical vulnerabilities immediately")
        
        if category_counts.get('Injection', 0) > 0:
            recommendations.add("Implement comprehensive input validation and output encoding")
        
        if category_counts.get('Security Misconfiguration', 0) > 0:
            recommendations.add("Review and harden security configurations")
        
        if category_counts.get('Vulnerable Dependencies', 0) > 0:
            recommendations.add("Implement automated dependency vulnerability scanning")
        
        # Add monitoring recommendation if vulnerabilities found
        if vulnerabilities:
            recommendations.add("Implement continuous security monitoring")
            recommendations.add("Conduct regular security assessments")
        
        return list(recommendations)


# Export main classes and utilities
__all__ = [
    'SecurityScanner',
    'SecurityVulnerability',
    'SecurityScanResult',
    'ThreatIndicator',
    'ComplianceCheck',
    'VulnerabilityScanner',
    'NetworkScanner',
    'WebApplicationScanner',
    'ComplianceChecker'
]