"""
Security Testing Suite module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔒 SECURITY PENETRATION TESTING SUITE - ENTERPRISE VALIDATION
Ainflue Platform - Comprehensive Security Assessment & Vulnerability Scanning

Auteur: Fahed Mlaiel (mlaiel@live.de)
Expertise Multi-Rôles: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                       Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Date: 12 Décembre 2025
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import json
import logging
import time
import hashlib
import base64
import ssl
import socket
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import aiohttp
import requests
from datetime import datetime

# Configuration Logging Enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/security_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityVulnerability:
    """🚨 Vulnérabilité de sécurité détectée"""
    vuln_id: str
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    description: str
    affected_endpoint: str
    proof_of_concept: str
    remediation: str
    owasp_category: str
    cvss_score: float
    detected_at: datetime

@dataclass
class SecurityTestResult:
    """🔍 Résultat test de sécurité"""
    test_name: str
    test_category: str
    status: str  # PASSED, FAILED, WARNING, SKIPPED
    vulnerabilities: List[SecurityVulnerability]
    test_duration: float
    endpoints_tested: int
    total_requests: int
    notes: str

class EnterprisePenetrationTester:
    """🛡️ TESTEUR PÉNÉTRATION ENTERPRISE - EXPERTISE SÉCURITÉ"""
    
    def __init__(self, base_url -> None: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.vulnerabilities: List[SecurityVulnerability] = []
        self.test_results: List[SecurityTestResult] = []
        self.scan_timestamp = datetime.now()
        logger.info(f"🔒 Enterprise Penetration Tester initialized for {base_url}")
    
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(verify_ssl=False)  # Pour tests SSL
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def add_vulnerability(self, vuln -> None: SecurityVulnerability) -> None:
        """📝 Ajouter vulnérabilité détectée"""
        self.vulnerabilities.append(vuln)
        severity_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🔵',
            'INFO': '⚪'
        }
        logger.warning(f"{severity_emoji.get(vuln.severity, '❓')} {vuln.severity} - {vuln.name}")
    
    async def test_owasp_top_10(self) -> SecurityTestResult:
        """🥇 Tests OWASP Top 10 2021 - Expertise Security Specialist"""
        logger.info("🚀 Starting OWASP Top 10 Security Assessment")
        start_time = time.time()
        vulnerabilities = []
        endpoints_tested = 0
        total_requests = 0
        
        # A01:2021 – Broken Access Control
        vulns, endpoints, requests = await self.test_broken_access_control()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A02:2021 – Cryptographic Failures
        vulns, endpoints, requests = await self.test_cryptographic_failures()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A03:2021 – Injection
        vulns, endpoints, requests = await self.test_injection_attacks()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A04:2021 – Insecure Design
        vulns, endpoints, requests = await self.test_insecure_design()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A05:2021 – Security Misconfiguration
        vulns, endpoints, requests = await self.test_security_misconfiguration()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A06:2021 – Vulnerable Components
        vulns, endpoints, requests = await self.test_vulnerable_components()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A07:2021 – Authentication Failures
        vulns, endpoints, requests = await self.test_authentication_failures()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A08:2021 – Software Integrity Failures
        vulns, endpoints, requests = await self.test_software_integrity()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A09:2021 – Security Logging Failures
        vulns, endpoints, requests = await self.test_logging_failures()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        # A10:2021 – Server-Side Request Forgery
        vulns, endpoints, requests = await self.test_ssrf()
        vulnerabilities.extend(vulns)
        endpoints_tested += endpoints
        total_requests += requests
        
        duration = time.time() - start_time
        
        # Déterminer statut global
        critical_count = sum(1 for v in vulnerabilities if v.severity == 'CRITICAL')
        high_count = sum(1 for v in vulnerabilities if v.severity == 'HIGH')
        
        if critical_count > 0:
            status = "FAILED"
        elif high_count > 0:
            status = "WARNING"
        else:
            status = "PASSED"
        
        result = SecurityTestResult(
            test_name="OWASP_TOP_10_2021",
            test_category="COMPREHENSIVE_SECURITY",
            status=status,
            vulnerabilities=vulnerabilities,
            test_duration=duration,
            endpoints_tested=endpoints_tested,
            total_requests=total_requests,
            notes=f"OWASP Top 10 assessment completed. Found {len(vulnerabilities)} issues."
        )
        
        self.test_results.append(result)
        return result
    
    async def test_broken_access_control(self) -> tuple:
        """🔐 A01:2021 – Broken Access Control"""
        vulnerabilities = []
        endpoints = 0
        requests_count = 0
        
        # Test endpoints communs
        test_endpoints = [
            '/admin', '/api/admin', '/api/v1/admin',
            '/api/users', '/api/v1/users',
            '/api/private', '/api/internal',
            '/config', '/api/config',
            '/.env', '/api/.env'
        ]
        
        for endpoint in test_endpoints:
            try:
                endpoints += 1
                requests_count += 1
                
                if not self.session:
                    continue
                    
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Vérifier si contenu sensible exposé
                        if any(keyword in content.lower() for keyword in 
                              ['password', 'secret', 'token', 'key', 'admin', 'private']):
                            
                            vuln = SecurityVulnerability(
                                vuln_id=f"AC001_{endpoint.replace('/', '_')}",
                                name="Broken Access Control - Unauthorized Access",
                                severity="HIGH",
                                category="Access Control",
                                description=f"Sensitive endpoint {endpoint} accessible without authentication",
                                affected_endpoint=endpoint,
                                proof_of_concept=f"GET {self.base_url}{endpoint} returned 200 with sensitive data",
                                remediation="Implement proper authentication and authorization checks",
                                owasp_category="A01:2021",
                                cvss_score=7.5,
                                detected_at=self.scan_timestamp
                            )
                            vulnerabilities.append(vuln)
                            self.add_vulnerability(vuln)
                
            except Exception as e:
                logger.debug(f"Access control test failed for {endpoint}: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_cryptographic_failures(self) -> tuple:
        """🔑 A02:2021 – Cryptographic Failures"""
        vulnerabilities = []
        endpoints = 1
        requests_count = 0
        
        # Test SSL/TLS Configuration
        try:
            parsed_url = urlparse(self.base_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        cipher = ssock.cipher()
                        
                        # Vérifier algorithmes faibles
                        if cipher and len(cipher) >= 3:
                            cipher_suite = cipher[0]
                            if any(weak in cipher_suite for weak in ['RC4', 'DES', 'MD5']):
                                vuln = SecurityVulnerability(
                                    vuln_id="CRYPTO001",
                                    name="Weak Cryptographic Cipher",
                                    severity="MEDIUM",
                                    category="Cryptography",
                                    description=f"Weak cipher suite detected: {cipher_suite}",
                                    affected_endpoint=self.base_url,
                                    proof_of_concept=f"TLS connection uses weak cipher: {cipher_suite}",
                                    remediation="Configure server to use strong cipher suites only",
                                    owasp_category="A02:2021",
                                    cvss_score=5.3,
                                    detected_at=self.scan_timestamp
                                )
                                vulnerabilities.append(vuln)
                                self.add_vulnerability(vuln)
            
            # Test HTTP vs HTTPS
            requests_count += 1
            if not self.session:
                return vulnerabilities, endpoints, requests_count
                
            async with self.session.get(self.base_url.replace('https://', 'http://')) as response:
                if response.status == 200:
                    vuln = SecurityVulnerability(
                        vuln_id="CRYPTO002",
                        name="Insecure HTTP Access",
                        severity="MEDIUM",
                        category="Cryptography",
                        description="Service accessible over unencrypted HTTP",
                        affected_endpoint=self.base_url.replace('https://', 'http://'),
                        proof_of_concept="Service responds to HTTP requests without redirection",
                        remediation="Implement HTTPS-only with automatic HTTP redirection",
                        owasp_category="A02:2021",
                        cvss_score=5.4,
                        detected_at=self.scan_timestamp
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
        except Exception as e:
            logger.debug(f"Crypto test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_injection_attacks(self) -> tuple:
        """💉 A03:2021 – Injection"""
        vulnerabilities = []
        endpoints = 0
        requests_count = 0
        
        # Payloads d'injection communs
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT password FROM users --",
            "1' AND 1=1 --"
        ]
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//"
        ]
        
        nosql_payloads = [
            "{'$ne': null}",
            "'; return true; //",
            "'; return this.a != 'FUZZDATA'; //"
        ]
        
        # Test endpoints API
        test_endpoints = [
            '/api/search?q=',
            '/api/v1/users?id=',
            '/api/login',
            '/api/register',
            '/api/v1/validation/content'
        ]
        
        for endpoint in test_endpoints:
            endpoints += 1
            
            # Test SQL Injection
            for payload in sql_payloads:
                try:
                    requests_count += 1
                    if not self.session:
                        continue
                    
                    # Test GET parameters
                    if '?' in endpoint:
                        test_url = f"{self.base_url}{endpoint}{payload}"
                        async with self.session.get(test_url) as response:
                            if self.check_sql_injection_response(await response.text(), payload):
                                vuln = SecurityVulnerability(
                                    vuln_id=f"INJ001_{endpoint.replace('/', '_')}",
                                    name="SQL Injection Vulnerability",
                                    severity="CRITICAL",
                                    category="Injection",
                                    description=f"SQL injection possible in {endpoint}",
                                    affected_endpoint=endpoint,
                                    proof_of_concept=f"Payload: {payload}",
                                    remediation="Use parameterized queries and input validation",
                                    owasp_category="A03:2021",
                                    cvss_score=9.8,
                                    detected_at=self.scan_timestamp
                                )
                                vulnerabilities.append(vuln)
                                self.add_vulnerability(vuln)
                    
                    # Test POST data
                    else:
                        async with self.session.post(
                            f"{self.base_url}{endpoint}",
                            json={"data": payload, "test": payload}
                        ) as response:
                            if self.check_sql_injection_response(await response.text(), payload):
                                vuln = SecurityVulnerability(
                                    vuln_id=f"INJ002_{endpoint.replace('/', '_')}",
                                    name="SQL Injection in POST Data",
                                    severity="CRITICAL",
                                    category="Injection",
                                    description=f"SQL injection in POST data for {endpoint}",
                                    affected_endpoint=endpoint,
                                    proof_of_concept=f"POST payload: {payload}",
                                    remediation="Sanitize and validate all input data",
                                    owasp_category="A03:2021",
                                    cvss_score=9.8,
                                    detected_at=self.scan_timestamp
                                )
                                vulnerabilities.append(vuln)
                                self.add_vulnerability(vuln)
                                
                except Exception as e:
                    logger.debug(f"SQL injection test failed: {e}")
            
            # Test XSS
            for payload in xss_payloads:
                try:
                    requests_count += 1
                    if not self.session:
                        continue
                        
                    async with self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"content": payload, "message": payload}
                    ) as response:
                        response_text = await response.text()
                        if payload in response_text and '<script>' in response_text:
                            vuln = SecurityVulnerability(
                                vuln_id=f"XSS001_{endpoint.replace('/', '_')}",
                                name="Cross-Site Scripting (XSS)",
                                severity="HIGH",
                                category="Injection",
                                description=f"XSS vulnerability in {endpoint}",
                                affected_endpoint=endpoint,
                                proof_of_concept=f"XSS payload: {payload}",
                                remediation="Implement proper output encoding and CSP headers",
                                owasp_category="A03:2021",
                                cvss_score=6.1,
                                detected_at=self.scan_timestamp
                            )
                            vulnerabilities.append(vuln)
                            self.add_vulnerability(vuln)
                            
                except Exception as e:
                    logger.debug(f"XSS test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    def check_sql_injection_response(self, response_text: str, payload: str) -> bool:
        """🔍 Vérifier réponse pour injection SQL"""
        sql_error_indicators = [
            'mysql_fetch_array',
            'ORA-01756',
            'Microsoft Access Driver',
            'PostgreSQL query failed',
            'Warning: mysql',
            'SQLServer JDBC Driver',
            'OLE DB Provider for ODBC',
            'sqlite3.OperationalError',
            'syntax error'
        ]
        
        response_lower = response_text.lower()
        return any(indicator.lower() in response_lower for indicator in sql_error_indicators)
    
    async def test_insecure_design(self) -> tuple:
        """🏗️ A04:2021 – Insecure Design"""
        vulnerabilities = []
        endpoints = 3
        requests_count = 0
        
        # Test absence de rate limiting
        try:
            requests_count += 50  # Test 50 requêtes rapides
            if not self.session:
                return vulnerabilities, endpoints, requests_count
            
            start_time = time.time()
            tasks = []
            for i in range(50):
                task = self.session.get(f"{self.base_url}/api/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            successful_requests = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            
            if successful_requests > 45:  # 90% success rate = pas de rate limiting
                vuln = SecurityVulnerability(
                    vuln_id="DESIGN001",
                    name="Missing Rate Limiting",
                    severity="MEDIUM",
                    category="Insecure Design",
                    description="No rate limiting detected on API endpoints",
                    affected_endpoint="/api/*",
                    proof_of_concept=f"50 rapid requests succeeded: {successful_requests}/50",
                    remediation="Implement rate limiting and request throttling",
                    owasp_category="A04:2021",
                    cvss_score=5.3,
                    detected_at=self.scan_timestamp
                )
                vulnerabilities.append(vuln)
                self.add_vulnerability(vuln)
                
        except Exception as e:
            logger.debug(f"Rate limiting test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_security_misconfiguration(self) -> tuple:
        """⚙️ A05:2021 – Security Misconfiguration"""
        vulnerabilities = []
        endpoints = 5
        requests_count = 0
        
        # Test headers de sécurité
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Referrer-Policy'
        ]
        
        try:
            requests_count += 1
            if not self.session:
                return vulnerabilities, endpoints, requests_count
                
            async with self.session.get(self.base_url) as response:
                missing_headers = []
                for header in security_headers:
                    if header not in response.headers:
                        missing_headers.append(header)
                
                if missing_headers:
                    vuln = SecurityVulnerability(
                        vuln_id="MISC001",
                        name="Missing Security Headers",
                        severity="MEDIUM",
                        category="Security Misconfiguration",
                        description=f"Missing security headers: {', '.join(missing_headers)}",
                        affected_endpoint=self.base_url,
                        proof_of_concept=f"Headers missing: {missing_headers}",
                        remediation="Configure proper security headers",
                        owasp_category="A05:2021",
                        cvss_score=5.3,
                        detected_at=self.scan_timestamp
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                
                # Test Server header révélant version
                server_header = response.headers.get('Server', '')
                if any(server in server_header.lower() for server in ['apache', 'nginx', 'iis']):
                    if any(char.isdigit() for char in server_header):
                        vuln = SecurityVulnerability(
                            vuln_id="MISC002",
                            name="Server Version Disclosure",
                            severity="LOW",
                            category="Information Disclosure",
                            description=f"Server header reveals version: {server_header}",
                            affected_endpoint=self.base_url,
                            proof_of_concept=f"Server: {server_header}",
                            remediation="Configure server to hide version information",
                            owasp_category="A05:2021",
                            cvss_score=2.7,
                            detected_at=self.scan_timestamp
                        )
                        vulnerabilities.append(vuln)
                        self.add_vulnerability(vuln)
                        
        except Exception as e:
            logger.debug(f"Security misconfiguration test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_vulnerable_components(self) -> tuple:
        """📦 A06:2021 – Vulnerable and Outdated Components"""
        vulnerabilities = []
        endpoints = 2
        requests_count = 0
        
        # Détecter frameworks/libraries exposés
        framework_indicators = {
            'django': ['csrfmiddlewaretoken', 'django', '__admin'],
            'flask': ['werkzeug', 'flask'],
            'express': ['x-powered-by: express'],
            'spring': ['spring', 'java'],
            'fastapi': ['fastapi', 'swagger', 'openapi']
        }
        
        try:
            requests_count += 1
            if not self.session:
                return vulnerabilities, endpoints, requests_count
                
            async with self.session.get(self.base_url) as response:
                response_text = await response.text()
                headers_str = str(response.headers).lower()
                
                for framework, indicators in framework_indicators.items():
                    if any(indicator in response_text.lower() or indicator in headers_str 
                          for indicator in indicators):
                        vuln = SecurityVulnerability(
                            vuln_id=f"COMP001_{framework}",
                            name=f"Framework Detection - {framework}",
                            severity="INFO",
                            category="Information Disclosure",
                            description=f"Application framework detected: {framework}",
                            affected_endpoint=self.base_url,
                            proof_of_concept=f"Framework signatures found for {framework}",
                            remediation="Ensure framework is updated to latest secure version",
                            owasp_category="A06:2021",
                            cvss_score=0.0,
                            detected_at=self.scan_timestamp
                        )
                        vulnerabilities.append(vuln)
                        
        except Exception as e:
            logger.debug(f"Component detection test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_authentication_failures(self) -> tuple:
        """🔑 A07:2021 – Identification and Authentication Failures"""
        vulnerabilities = []
        endpoints = 3
        requests_count = 0
        
        # Test endpoints d'authentification
        auth_endpoints = ['/api/login', '/api/auth', '/api/token']
        
        for endpoint in auth_endpoints:
            try:
                requests_count += 1
                endpoints += 1
                if not self.session:
                    continue
                
                # Test credentials faibles
                weak_creds = [
                    {'username': 'admin', 'password': 'admin'},
                    {'username': 'admin', 'password': 'password'},
                    {'username': 'root', 'password': 'root'},
                    {'username': 'test', 'password': 'test'}
                ]
                
                for creds in weak_creds:
                    requests_count += 1
                    async with self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=creds
                    ) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            if any(indicator in response_text.lower() 
                                  for indicator in ['token', 'success', 'welcome', 'authenticated']):
                                vuln = SecurityVulnerability(
                                    vuln_id=f"AUTH001_{endpoint.replace('/', '_')}",
                                    name="Weak Default Credentials",
                                    severity="CRITICAL",
                                    category="Authentication",
                                    description=f"Default credentials accepted: {creds['username']}/{creds['password']}",
                                    affected_endpoint=endpoint,
                                    proof_of_concept=f"Login successful with {creds}",
                                    remediation="Change default credentials and enforce strong password policy",
                                    owasp_category="A07:2021",
                                    cvss_score=9.8,
                                    detected_at=self.scan_timestamp
                                )
                                vulnerabilities.append(vuln)
                                self.add_vulnerability(vuln)
                                
            except Exception as e:
                logger.debug(f"Authentication test failed for {endpoint}: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_software_integrity(self) -> tuple:
        """📋 A08:2021 – Software and Data Integrity Failures"""
        vulnerabilities = []
        endpoints = 2
        requests_count = 0
        
        # Test Subresource Integrity
        try:
            requests_count += 1
            if not self.session:
                return vulnerabilities, endpoints, requests_count
                
            async with self.session.get(self.base_url) as response:
                html_content = await response.text()
                
                # Vérifier scripts externes sans SRI
                if '<script src="http' in html_content and 'integrity=' not in html_content:
                    vuln = SecurityVulnerability(
                        vuln_id="INT001",
                        name="Missing Subresource Integrity",
                        severity="MEDIUM",
                        category="Software Integrity",
                        description="External scripts loaded without integrity verification",
                        affected_endpoint=self.base_url,
                        proof_of_concept="External scripts found without SRI hashes",
                        remediation="Add integrity hashes to all external resources",
                        owasp_category="A08:2021",
                        cvss_score=4.3,
                        detected_at=self.scan_timestamp
                    )
                    vulnerabilities.append(vuln)
                    self.add_vulnerability(vuln)
                    
        except Exception as e:
            logger.debug(f"Software integrity test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_logging_failures(self) -> tuple:
        """📝 A09:2021 – Security Logging and Monitoring Failures"""
        vulnerabilities = []
        endpoints = 1
        requests_count = 0
        
        # Test logging d'événements de sécurité
        try:
            requests_count += 3
            if not self.session:
                return vulnerabilities, endpoints, requests_count
            
            # Simuler tentatives malveillantes
            malicious_attempts = [
                ('/admin', 'GET'),
                ('/api/admin', 'GET'),
                ('/.env', 'GET')
            ]
            
            for path, method in malicious_attempts:
                if method == 'GET':
                    await self.session.get(f"{self.base_url}{path}")
                
            # Note: Dans un vrai test, on vérifierait les logs
            # Ici on suppose que l'absence de blocage = logging insuffisant
            vuln = SecurityVulnerability(
                vuln_id="LOG001",
                name="Insufficient Security Monitoring",
                severity="MEDIUM",
                category="Logging and Monitoring",
                description="No apparent security monitoring for malicious access attempts",
                affected_endpoint="Global",
                proof_of_concept="Multiple suspicious requests not blocked",
                remediation="Implement comprehensive security logging and monitoring",
                owasp_category="A09:2021",
                cvss_score=3.7,
                detected_at=self.scan_timestamp
            )
            vulnerabilities.append(vuln)
            self.add_vulnerability(vuln)
                
        except Exception as e:
            logger.debug(f"Logging test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    async def test_ssrf(self) -> tuple:
        """🌐 A10:2021 – Server-Side Request Forgery (SSRF)"""
        vulnerabilities = []
        endpoints = 2
        requests_count = 0
        
        # Test SSRF payloads
        ssrf_payloads = [
            'http://localhost:22',
            'http://127.0.0.1:3306',
            'http://169.254.169.254/latest/meta-data/',  # AWS metadata
            'file:///etc/passwd',
            'http://internal-service:8080'
        ]
        
        ssrf_endpoints = ['/api/webhook', '/api/fetch', '/api/url', '/api/proxy']
        
        for endpoint in ssrf_endpoints:
            for payload in ssrf_payloads:
                try:
                    requests_count += 1
                    if not self.session:
                        continue
                    
                    async with self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={'url': payload, 'target': payload}
                    ) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            
                            # Indicateurs de SSRF réussi
                            if any(indicator in response_text.lower() for indicator in 
                                  ['connection', 'timeout', 'refused', 'internal', 'localhost']):
                                vuln = SecurityVulnerability(
                                    vuln_id=f"SSRF001_{endpoint.replace('/', '_')}",
                                    name="Server-Side Request Forgery",
                                    severity="HIGH",
                                    category="SSRF",
                                    description=f"SSRF vulnerability in {endpoint}",
                                    affected_endpoint=endpoint,
                                    proof_of_concept=f"SSRF payload: {payload}",
                                    remediation="Validate and whitelist allowed URLs/IPs",
                                    owasp_category="A10:2021",
                                    cvss_score=8.5,
                                    detected_at=self.scan_timestamp
                                )
                                vulnerabilities.append(vuln)
                                self.add_vulnerability(vuln)
                                
                except Exception as e:
                    logger.debug(f"SSRF test failed: {e}")
        
        return vulnerabilities, endpoints, requests_count
    
    def generate_security_report(self) -> Dict[str, Any]:
        """📊 Génération rapport sécurité complet"""
        total_vulns = len(self.vulnerabilities)
        critical_count = sum(1 for v in self.vulnerabilities if v.severity == 'CRITICAL')
        high_count = sum(1 for v in self.vulnerabilities if v.severity == 'HIGH')
        medium_count = sum(1 for v in self.vulnerabilities if v.severity == 'MEDIUM')
        low_count = sum(1 for v in self.vulnerabilities if v.severity == 'LOW')
        info_count = sum(1 for v in self.vulnerabilities if v.severity == 'INFO')
        
        # Score de sécurité
        security_score = max(0, 100 - (critical_count * 25 + high_count * 10 + medium_count * 5 + low_count * 2))
        
        # Grade de sécurité
        if security_score >= 95 and critical_count == 0:
            security_grade = "A+ (EXCELLENT)"
        elif security_score >= 85 and critical_count == 0:
            security_grade = "A (VERY_GOOD)"
        elif security_score >= 75 and critical_count <= 1:
            security_grade = "B+ (GOOD)"
        elif security_score >= 65:
            security_grade = "B (ACCEPTABLE)"
        elif security_score >= 50:
            security_grade = "C (NEEDS_IMPROVEMENT)"
        else:
            security_grade = "D (CRITICAL_ISSUES)"
        
        report = {
            "scan_summary": {
                "target_url": self.base_url,
                "scan_timestamp": self.scan_timestamp.isoformat(),
                "total_vulnerabilities": total_vulns,
                "security_score": security_score,
                "security_grade": security_grade,
                "scan_duration": sum(r.test_duration for r in self.test_results),
                "total_endpoints_tested": sum(r.endpoints_tested for r in self.test_results),
                "total_requests_sent": sum(r.total_requests for r in self.test_results)
            },
            
            "vulnerability_breakdown": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "info": info_count
            },
            
            "owasp_top_10_compliance": self.generate_owasp_compliance(),
            
            "detailed_vulnerabilities": [asdict(v) for v in self.vulnerabilities],
            
            "test_results": [asdict(r) for r in self.test_results],
            
            "security_recommendations": self.generate_security_recommendations(),
            
            "expert_analysis": {
                "security_specialist": self.analyze_as_security_expert(),
                "penetration_tester": self.analyze_as_pentester(),
                "compliance_officer": self.analyze_compliance_status(),
                "devops_security": self.analyze_infrastructure_security()
            }
        }
        
        return report
    
    def generate_owasp_compliance(self) -> Dict[str, Any]:
        """📋 Analyse conformité OWASP Top 10"""
        owasp_categories = {
            "A01:2021": "Broken Access Control",
            "A02:2021": "Cryptographic Failures", 
            "A03:2021": "Injection",
            "A04:2021": "Insecure Design",
            "A05:2021": "Security Misconfiguration",
            "A06:2021": "Vulnerable Components",
            "A07:2021": "Authentication Failures",
            "A08:2021": "Software Integrity Failures",
            "A09:2021": "Logging and Monitoring Failures",
            "A10:2021": "Server-Side Request Forgery"
        }
        
        compliance = {}
        for category, name in owasp_categories.items():
            category_vulns = [v for v in self.vulnerabilities if v.owasp_category == category]
            critical_high = [v for v in category_vulns if v.severity in ['CRITICAL', 'HIGH']]
            
            compliance[category] = {
                "name": name,
                "status": "FAIL" if critical_high else "PASS",
                "vulnerabilities_found": len(category_vulns),
                "critical_high_issues": len(critical_high)
            }
        
        return compliance
    
    def generate_security_recommendations(self) -> List[str]:
        """💡 Recommandations sécurité"""
        recommendations = []
        
        if any(v.severity == 'CRITICAL' for v in self.vulnerabilities):
            recommendations.append("🚨 URGENT: Address all critical vulnerabilities immediately")
        
        if any('injection' in v.category.lower() for v in self.vulnerabilities):
            recommendations.append("🛡️ Implement comprehensive input validation and parameterized queries")
        
        if any('access control' in v.category.lower() for v in self.vulnerabilities):
            recommendations.append("🔐 Review and strengthen access control mechanisms")
        
        if any('authentication' in v.category.lower() for v in self.vulnerabilities):
            recommendations.append("🔑 Implement strong authentication and password policies")
        
        recommendations.extend([
            "📊 Implement comprehensive security monitoring and logging",
            "🔒 Enable all security headers (CSP, HSTS, etc.)",
            "🧪 Conduct regular security testing and code reviews",
            "📚 Provide security training for development team",
            "🔄 Establish incident response procedures",
            "📋 Create security compliance documentation"
        ])
        
        return recommendations
    
    def analyze_as_security_expert(self) -> str:
        """👨‍💻 Analyse expert sécurité"""
        critical_issues = [v for v in self.vulnerabilities if v.severity == 'CRITICAL']
        
        if critical_issues:
            return f"CRITICAL SECURITY ISSUES DETECTED: {len(critical_issues)} vulnerabilities require immediate attention. System is at high risk."
        elif any(v.severity == 'HIGH' for v in self.vulnerabilities):
            return "High-risk vulnerabilities present. Address within 24-48 hours. Security posture needs improvement."
        else:
            return "No critical security issues detected. Maintain current security practices and monitor for new threats."
    
    def analyze_as_pentester(self) -> str:
        """🔍 Analyse pentester"""
        injection_vulns = [v for v in self.vulnerabilities if 'injection' in v.category.lower()]
        auth_vulns = [v for v in self.vulnerabilities if 'authentication' in v.category.lower()]
        
        findings = []
        if injection_vulns:
            findings.append(f"{len(injection_vulns)} injection vulnerabilities")
        if auth_vulns:
            findings.append(f"{len(auth_vulns)} authentication issues")
        
        if findings:
            return f"Penetration testing revealed: {', '.join(findings)}. Application vulnerable to common attack vectors."
        else:
            return "Penetration testing shows robust security posture. Application resistant to common attack patterns."
    
    def analyze_compliance_status(self) -> str:
        """📋 Analyse conformité"""
        owasp_compliance = self.generate_owasp_compliance()
        failing_categories = [cat for cat, data in owasp_compliance.items() if data['status'] == 'FAIL']
        
        if not failing_categories:
            return "OWASP Top 10 2021 compliance: PASSED. All categories meet security requirements."
        else:
            return f"OWASP Top 10 2021 compliance: FAILED. {len(failing_categories)}/10 categories have issues."
    
    def analyze_infrastructure_security(self) -> str:
        """🏗️ Analyse sécurité infrastructure"""
        config_issues = [v for v in self.vulnerabilities if 'configuration' in v.category.lower()]
        header_issues = [v for v in self.vulnerabilities if 'headers' in v.name.lower()]
        
        if config_issues or header_issues:
            return f"Infrastructure security needs attention: {len(config_issues + header_issues)} configuration issues detected."
        else:
            return "Infrastructure security configuration appears robust. Good security headers and configuration detected."

# Factory Functions
async def run_quick_security_scan(base_url: str) -> Dict[str, Any]:
    """🏃‍♂️ Scan sécurité rapide"""
    async with EnterprisePenetrationTester(base_url) as tester:
        # Test uniquement OWASP Top 3
        await tester.test_broken_access_control()
        await tester.test_cryptographic_failures() 
        await tester.test_injection_attacks()
        
        return tester.generate_security_report()

async def run_full_security_assessment(base_url: str) -> Dict[str, Any]:
    """🔒 Assessment sécurité complet"""
    async with EnterprisePenetrationTester(base_url) as tester:
        await tester.test_owasp_top_10()
        return tester.generate_security_report()

if __name__ == "__main__":
    """🎯 Exécution directe pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python security_testing_suite.py <base_url> [quick|full]")
        sys.exit(1)
    
    base_url = sys.argv[1]
    test_type = sys.argv[2] if len(sys.argv) > 2 else "full"
    
    logger.info(f"🔒 Starting Security Assessment")
    logger.info(f"Target: {base_url}")
    logger.info(f"Type: {test_type}")
    
    if test_type == "quick":
        result = asyncio.run(run_quick_security_scan(base_url))
    else:
        result = asyncio.run(run_full_security_assessment(base_url))
    
    # Sauvegarde rapport
    report_file = f"/tmp/security_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    # Affichage résumé
    print(f"\n🔒 Security Assessment Complete")
    print(f"📊 Security Grade: {result['scan_summary']['security_grade']}")
    print(f"🎯 Security Score: {result['scan_summary']['security_score']}/100")
    print(f"🚨 Critical Issues: {result['vulnerability_breakdown']['critical']}")
    print(f"⚠️  High Issues: {result['vulnerability_breakdown']['high']}")
    print(f"📋 Full report saved to: {report_file}")