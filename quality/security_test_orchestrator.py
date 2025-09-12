#!/usr/bin/env python3
"""
Security Test Orchestrator - Ainflue Quality Platform
===================================================

Enterprise-grade security testing orchestration system.
Demonstrates Security Specialist + DevOps + Backend Senior expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import hashlib
import hmac
import base64
import secrets
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import aiohttp
import ssl
import socket
from urllib.parse import urljoin, urlparse, parse_qs
import re
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityTestResult:
    """Security test execution result."""
    test_name: str
    test_category: str  # 'authentication', 'authorization', 'injection', 'xss', 'csrf', 'ssl'
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    status: str  # 'passed', 'failed', 'warning', 'error'
    description: str
    vulnerability_details: Dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    execution_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityTestSuite:
    """Security test suite configuration."""
    name: str
    target_url: str
    authentication: Dict[str, Any] = field(default_factory=dict)
    test_categories: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    rate_limit: float = 1.0  # Requests per second


class SQLInjectionTester:
    """SQL Injection vulnerability tester."""
    
    def __init__(self):
        self.payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "1' AND SLEEP(5)--",
            "' OR BENCHMARK(1000000,MD5(1))--",
            "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "1; SELECT * FROM users--",
            "' OR EXISTS(SELECT * FROM users WHERE id=1)--",
            "1' AND EXTRACTVALUE(1,CONCAT(0x7e,version(),0x7e))--"
        ]
    
    async def test_sql_injection(self, session: aiohttp.ClientSession, url: str, 
                               parameters: Dict[str, str]) -> List[SecurityTestResult]:
        """Test for SQL injection vulnerabilities."""
        results = []
        
        for param_name, original_value in parameters.items():
            for payload in self.payloads:
                start_time = time.time()
                
                # Test parameter injection
                test_params = parameters.copy()
                test_params[param_name] = payload
                
                result = SecurityTestResult(
                    test_name=f"sql_injection_{param_name}",
                    test_category="injection",
                    severity="critical",
                    status="passed",
                    description=f"SQL injection test for parameter '{param_name}'"
                )
                
                try:
                    async with session.get(url, params=test_params) as response:
                        response_text = await response.text()
                        
                        # Check for SQL error indicators
                        sql_errors = [
                            "SQL syntax", "mysql_fetch", "ORA-", "Microsoft OLE DB",
                            "PostgreSQL", "sqlite3.OperationalError", "SQL Server",
                            "Unclosed quotation mark", "quoted string not properly terminated"
                        ]
                        
                        for error_pattern in sql_errors:
                            if error_pattern.lower() in response_text.lower():
                                result.status = "failed"
                                result.vulnerability_details = {
                                    "parameter": param_name,
                                    "payload": payload,
                                    "error_pattern": error_pattern,
                                    "response_status": response.status
                                }
                                result.evidence.append(f"SQL error detected: {error_pattern}")
                                result.remediation = "Use parameterized queries and input validation"
                                break
                        
                        # Check for unusual response times (blind SQL injection)
                        response_time = (time.time() - start_time) * 1000
                        if "SLEEP" in payload and response_time > 4000:  # 4+ seconds
                            result.status = "failed"
                            result.vulnerability_details = {
                                "parameter": param_name,
                                "payload": payload,
                                "response_time_ms": response_time,
                                "type": "time_based_blind"
                            }
                            result.evidence.append(f"Time-based SQL injection detected (response time: {response_time:.0f}ms)")
                            result.remediation = "Use parameterized queries and input validation"
                
                except Exception as e:
                    result.status = "error"
                    result.errors.append(f"SQL injection test error: {str(e)}")
                
                result.execution_time_ms = (time.time() - start_time) * 1000
                results.append(result)
                
                # Rate limiting
                await asyncio.sleep(0.5)
        
        return results


class XSSTester:
    """Cross-Site Scripting (XSS) vulnerability tester."""
    
    def __init__(self):
        self.payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<<SCRIPT>alert('XSS')</SCRIPT>"
        ]
    
    async def test_xss(self, session: aiohttp.ClientSession, url: str, 
                      parameters: Dict[str, str]) -> List[SecurityTestResult]:
        """Test for XSS vulnerabilities."""
        results = []
        
        for param_name, original_value in parameters.items():
            for payload in self.payloads:
                start_time = time.time()
                
                # Test parameter injection
                test_params = parameters.copy()
                test_params[param_name] = payload
                
                result = SecurityTestResult(
                    test_name=f"xss_{param_name}",
                    test_category="xss",
                    severity="high",
                    status="passed",
                    description=f"XSS test for parameter '{param_name}'"
                )
                
                try:
                    async with session.get(url, params=test_params) as response:
                        response_text = await response.text()
                        
                        # Check if payload is reflected in response
                        if payload in response_text:
                            result.status = "failed"
                            result.vulnerability_details = {
                                "parameter": param_name,
                                "payload": payload,
                                "reflected": True,
                                "response_status": response.status
                            }
                            result.evidence.append(f"XSS payload reflected in response")
                            result.remediation = "Implement proper input sanitization and output encoding"
                        
                        # Check for script execution indicators
                        script_indicators = ["<script", "javascript:", "onerror=", "onload="]
                        for indicator in script_indicators:
                            if indicator in response_text and payload in response_text:
                                result.status = "failed"
                                result.severity = "critical"
                                result.vulnerability_details.update({
                                    "execution_context": indicator,
                                    "type": "reflected_xss"
                                })
                                result.evidence.append(f"Potential script execution context: {indicator}")
                                break
                
                except Exception as e:
                    result.status = "error"
                    result.errors.append(f"XSS test error: {str(e)}")
                
                result.execution_time_ms = (time.time() - start_time) * 1000
                results.append(result)
                
                # Rate limiting
                await asyncio.sleep(0.3)
        
        return results


class AuthenticationTester:
    """Authentication mechanism tester."""
    
    async def test_authentication(self, session: aiohttp.ClientSession, 
                                base_url: str) -> List[SecurityTestResult]:
        """Test authentication mechanisms."""
        results = []
        
        # Test weak password policy
        result = await self._test_weak_passwords(session, base_url)
        results.append(result)
        
        # Test brute force protection
        result = await self._test_brute_force_protection(session, base_url)
        results.append(result)
        
        # Test session management
        result = await self._test_session_management(session, base_url)
        results.append(result)
        
        return results
    
    async def _test_weak_passwords(self, session: aiohttp.ClientSession, 
                                 base_url: str) -> SecurityTestResult:
        """Test for weak password acceptance."""
        start_time = time.time()
        
        result = SecurityTestResult(
            test_name="weak_password_test",
            test_category="authentication",
            severity="medium",
            status="passed",
            description="Test for weak password acceptance"
        )
        
        weak_passwords = ["123456", "password", "admin", "test", "123", "qwerty"]
        login_url = urljoin(base_url, "/login")
        
        try:
            for password in weak_passwords:
                login_data = {
                    "username": "test@example.com",
                    "password": password
                }
                
                async with session.post(login_url, data=login_data) as response:
                    response_text = await response.text()
                    
                    # Check for successful login indicators
                    success_indicators = ["dashboard", "welcome", "profile", "logout"]
                    if response.status == 200 and any(indicator in response_text.lower() 
                                                     for indicator in success_indicators):
                        result.status = "failed"
                        result.vulnerability_details = {
                            "weak_password": password,
                            "login_successful": True
                        }
                        result.evidence.append(f"Weak password '{password}' accepted")
                        result.remediation = "Implement strong password policy"
                        break
                
                await asyncio.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            result.status = "error"
            result.errors.append(f"Weak password test error: {str(e)}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _test_brute_force_protection(self, session: aiohttp.ClientSession, 
                                         base_url: str) -> SecurityTestResult:
        """Test brute force protection mechanisms."""
        start_time = time.time()
        
        result = SecurityTestResult(
            test_name="brute_force_protection",
            test_category="authentication",
            severity="high",
            status="passed",
            description="Test for brute force protection"
        )
        
        login_url = urljoin(base_url, "/login")
        attempt_count = 0
        
        try:
            # Make multiple failed login attempts
            for i in range(10):
                login_data = {
                    "username": "test@example.com",
                    "password": f"wrongpassword{i}"
                }
                
                async with session.post(login_url, data=login_data) as response:
                    attempt_count += 1
                    
                    # Check for rate limiting or account lockout
                    if response.status == 429 or "too many attempts" in (await response.text()).lower():
                        result.evidence.append(f"Rate limiting detected after {attempt_count} attempts")
                        break
                    elif response.status == 423 or "account locked" in (await response.text()).lower():
                        result.evidence.append(f"Account lockout detected after {attempt_count} attempts")
                        break
                
                await asyncio.sleep(0.1)
            else:
                # No protection detected
                result.status = "failed"
                result.vulnerability_details = {
                    "attempts_made": attempt_count,
                    "protection_detected": False
                }
                result.evidence.append(f"No brute force protection after {attempt_count} attempts")
                result.remediation = "Implement rate limiting and account lockout mechanisms"
        
        except Exception as e:
            result.status = "error"
            result.errors.append(f"Brute force test error: {str(e)}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _test_session_management(self, session: aiohttp.ClientSession, 
                                     base_url: str) -> SecurityTestResult:
        """Test session management security."""
        start_time = time.time()
        
        result = SecurityTestResult(
            test_name="session_management",
            test_category="authentication",
            severity="medium",
            status="passed",
            description="Test session management security"
        )
        
        try:
            # Make a request to get session cookie
            async with session.get(base_url) as response:
                cookies = response.cookies
                
                security_issues = []
                
                for cookie_name, cookie in cookies.items():
                    # Check for HttpOnly flag
                    if not cookie.get('httponly'):
                        security_issues.append(f"Cookie '{cookie_name}' missing HttpOnly flag")
                    
                    # Check for Secure flag
                    if not cookie.get('secure'):
                        security_issues.append(f"Cookie '{cookie_name}' missing Secure flag")
                    
                    # Check for SameSite attribute
                    if 'samesite' not in cookie:
                        security_issues.append(f"Cookie '{cookie_name}' missing SameSite attribute")
                
                if security_issues:
                    result.status = "failed"
                    result.vulnerability_details = {
                        "cookie_issues": security_issues
                    }
                    result.evidence.extend(security_issues)
                    result.remediation = "Configure cookies with HttpOnly, Secure, and SameSite attributes"
        
        except Exception as e:
            result.status = "error"
            result.errors.append(f"Session management test error: {str(e)}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result


class SSLTester:
    """SSL/TLS security tester."""
    
    async def test_ssl_configuration(self, hostname: str, port: int = 443) -> List[SecurityTestResult]:
        """Test SSL/TLS configuration."""
        results = []
        
        # Test SSL certificate
        result = await self._test_ssl_certificate(hostname, port)
        results.append(result)
        
        # Test SSL protocols
        result = await self._test_ssl_protocols(hostname, port)
        results.append(result)
        
        # Test cipher suites
        result = await self._test_cipher_suites(hostname, port)
        results.append(result)
        
        return results
    
    async def _test_ssl_certificate(self, hostname: str, port: int) -> SecurityTestResult:
        """Test SSL certificate validity."""
        start_time = time.time()
        
        result = SecurityTestResult(
            test_name="ssl_certificate",
            test_category="ssl",
            severity="high",
            status="passed",
            description="SSL certificate validation"
        )
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiration
                    not_after = cert.get('notAfter')
                    if not_after:
                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now()).days
                        
                        if days_until_expiry < 30:
                            result.status = "failed"
                            result.severity = "critical" if days_until_expiry < 7 else "high"
                            result.vulnerability_details = {
                                "expiry_date": not_after,
                                "days_until_expiry": days_until_expiry
                            }
                            result.evidence.append(f"Certificate expires in {days_until_expiry} days")
                            result.remediation = "Renew SSL certificate before expiration"
                    
                    # Check subject alternative names
                    san_extension = None
                    for extension in cert.get('subjectAltName', []):
                        if extension[0] == 'DNS':
                            san_extension = extension[1]
                            break
                    
                    if not san_extension or hostname not in san_extension:
                        result.status = "warning"
                        result.evidence.append(f"Hostname '{hostname}' not found in SAN")
                        result.remediation = "Ensure certificate includes all required hostnames"
        
        except ssl.SSLError as e:
            result.status = "failed"
            result.severity = "critical"
            result.errors.append(f"SSL error: {str(e)}")
            result.remediation = "Fix SSL configuration"
        
        except Exception as e:
            result.status = "error"
            result.errors.append(f"SSL certificate test error: {str(e)}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _test_ssl_protocols(self, hostname: str, port: int) -> SecurityTestResult:
        """Test supported SSL/TLS protocols."""
        start_time = time.time()
        
        result = SecurityTestResult(
            test_name="ssl_protocols",
            test_category="ssl",
            severity="medium",
            status="passed",
            description="SSL protocol version testing"
        )
        
        weak_protocols = [
            (ssl.PROTOCOL_SSLv23, "SSLv2/SSLv3"),
            (ssl.PROTOCOL_TLSv1, "TLSv1.0"),
            (ssl.PROTOCOL_TLSv1_1, "TLSv1.1")
        ]
        
        supported_weak = []
        
        try:
            for protocol, name in weak_protocols:
                try:
                    context = ssl.SSLContext(protocol)
                    with socket.create_connection((hostname, port), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            supported_weak.append(name)
                except:
                    pass  # Protocol not supported (good)
            
            if supported_weak:
                result.status = "failed"
                result.vulnerability_details = {
                    "weak_protocols": supported_weak
                }
                result.evidence.extend([f"Weak protocol supported: {p}" for p in supported_weak])
                result.remediation = "Disable weak SSL/TLS protocols, use TLS 1.2+ only"
        
        except Exception as e:
            result.status = "error"
            result.errors.append(f"SSL protocol test error: {str(e)}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _test_cipher_suites(self, hostname: str, port: int) -> SecurityTestResult:
        """Test cipher suite configuration."""
        start_time = time.time()
        
        result = SecurityTestResult(
            test_name="ssl_ciphers",
            test_category="ssl",
            severity="medium",
            status="passed",
            description="SSL cipher suite testing"
        )
        
        try:
            # Get cipher information
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()
                    
                    if cipher:
                        cipher_name = cipher[0]
                        protocol_version = cipher[1]
                        key_length = cipher[2]
                        
                        result.vulnerability_details = {
                            "cipher": cipher_name,
                            "protocol": protocol_version,
                            "key_length": key_length
                        }
                        
                        # Check for weak ciphers
                        weak_ciphers = ["RC4", "DES", "3DES", "MD5", "NULL"]
                        for weak in weak_ciphers:
                            if weak in cipher_name:
                                result.status = "failed"
                                result.evidence.append(f"Weak cipher detected: {cipher_name}")
                                result.remediation = "Configure strong cipher suites only"
                                break
                        
                        # Check key length
                        if key_length < 128:
                            result.status = "failed"
                            result.evidence.append(f"Weak key length: {key_length} bits")
                            result.remediation = "Use cipher suites with key length >= 128 bits"
        
        except Exception as e:
            result.status = "error"
            result.errors.append(f"SSL cipher test error: {str(e)}")
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result


class SecurityTestOrchestrator:
    """
    Enterprise Security Testing Orchestration Engine
    ==============================================
    
    Comprehensive security testing orchestration for web applications.
    Demonstrates Security Specialist + DevOps + Backend Senior expertise.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.test_results: List[SecurityTestResult] = []
        
        # Initialize testers
        self.sql_tester = SQLInjectionTester()
        self.xss_tester = XSSTester()
        self.auth_tester = AuthenticationTester()
        self.ssl_tester = SSLTester()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load security testing configuration."""
        default_config = {
            'test_suites': {},
            'global_settings': {
                'user_agent': 'Ainflue-Security-Scanner/1.0',
                'timeout': 30,
                'rate_limit': 1.0,
                'follow_redirects': True,
                'verify_ssl': True
            },
            'reporting': {
                'include_evidence': True,
                'include_remediation': True,
                'severity_threshold': 'low'  # minimum severity to report
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def execute_security_test_suite(self, suite: SecurityTestSuite) -> List[SecurityTestResult]:
        """Execute a complete security test suite."""
        logger.info(f"Starting security test suite: {suite.name}")
        
        results = []
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=suite.timeout)
        headers = {
            'User-Agent': self.config['global_settings']['user_agent'],
            **suite.custom_headers
        }
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        ) as session:
            
            # Authentication if required
            if suite.authentication:
                await self._authenticate_session(session, suite)
            
            # Parse target URL
            parsed_url = urlparse(suite.target_url)
            
            # Extract parameters for testing
            query_params = parse_qs(parsed_url.query)
            test_params = {k: v[0] if v else '' for k, v in query_params.items()}
            
            # Add default test parameters if none exist
            if not test_params:
                test_params = {'id': '1', 'search': 'test', 'page': '1'}
            
            # Execute test categories
            for category in suite.test_categories:
                logger.info(f"Running {category} tests")
                
                try:
                    if category == 'injection':
                        category_results = await self.sql_tester.test_sql_injection(
                            session, suite.target_url, test_params
                        )
                        results.extend(category_results)
                    
                    elif category == 'xss':
                        category_results = await self.xss_tester.test_xss(
                            session, suite.target_url, test_params
                        )
                        results.extend(category_results)
                    
                    elif category == 'authentication':
                        category_results = await self.auth_tester.test_authentication(
                            session, suite.target_url
                        )
                        results.extend(category_results)
                    
                    elif category == 'ssl':
                        hostname = parsed_url.hostname
                        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
                        
                        if parsed_url.scheme == 'https':
                            category_results = await self.ssl_tester.test_ssl_configuration(
                                hostname, port
                            )
                            results.extend(category_results)
                    
                    # Rate limiting between test categories
                    await asyncio.sleep(1.0 / suite.rate_limit)
                
                except Exception as e:
                    logger.error(f"Error in {category} tests: {e}")
                    error_result = SecurityTestResult(
                        test_name=f"{category}_test_error",
                        test_category=category,
                        severity="error",
                        status="error",
                        description=f"Error executing {category} tests",
                        errors=[str(e)]
                    )
                    results.append(error_result)
        
        logger.info(f"Security test suite completed: {suite.name} ({len(results)} tests)")
        return results
    
    async def _authenticate_session(self, session: aiohttp.ClientSession, 
                                  suite: SecurityTestSuite):
        """Authenticate session if credentials provided."""
        auth_config = suite.authentication
        
        if auth_config.get('type') == 'basic':
            # Basic authentication
            username = auth_config.get('username')
            password = auth_config.get('password')
            if username and password:
                auth = aiohttp.BasicAuth(username, password)
                session._default_auth = auth
        
        elif auth_config.get('type') == 'bearer':
            # Bearer token authentication
            token = auth_config.get('token')
            if token:
                session.headers['Authorization'] = f"Bearer {token}"
        
        elif auth_config.get('type') == 'form':
            # Form-based authentication
            login_url = auth_config.get('login_url')
            username = auth_config.get('username')
            password = auth_config.get('password')
            
            if login_url and username and password:
                login_data = {
                    auth_config.get('username_field', 'username'): username,
                    auth_config.get('password_field', 'password'): password
                }
                
                async with session.post(login_url, data=login_data) as response:
                    if response.status == 200:
                        logger.info("Form authentication successful")
                    else:
                        logger.warning(f"Form authentication failed: {response.status}")
    
    async def run_security_tests(self, test_suites: List[SecurityTestSuite]) -> Dict[str, Any]:
        """Run security tests for multiple test suites."""
        logger.info(f"Starting security tests for {len(test_suites)} test suites")
        
        all_results = []
        
        for suite in test_suites:
            try:
                suite_results = await self.execute_security_test_suite(suite)
                all_results.extend(suite_results)
                
            except Exception as e:
                logger.error(f"Failed to execute test suite {suite.name}: {e}")
                # Create error result
                error_result = SecurityTestResult(
                    test_name=f"{suite.name}_execution_error",
                    test_category="general",
                    severity="error",
                    status="error",
                    description=f"Test suite execution failed",
                    errors=[str(e)]
                )
                all_results.append(error_result)
        
        self.test_results = all_results
        
        # Generate comprehensive report
        return self._generate_security_report()
    
    def _generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security test report."""
        # Filter by severity threshold
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
        threshold = severity_order.get(self.config['reporting']['severity_threshold'], 0)
        filtered_results = [
            r for r in self.test_results 
            if severity_order.get(r.severity, 0) >= threshold
        ]
        
        # Group by severity and category
        severity_counts = {}
        category_counts = {}
        vulnerabilities = []
        
        for result in filtered_results:
            # Count by severity
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1
            
            # Count by category
            category_counts[result.test_category] = category_counts.get(result.test_category, 0) + 1
            
            # Collect vulnerabilities (failed tests)
            if result.status == 'failed':
                vuln = {
                    'test_name': result.test_name,
                    'category': result.test_category,
                    'severity': result.severity,
                    'description': result.description,
                    'vulnerability_details': result.vulnerability_details,
                    'remediation': result.remediation
                }
                
                if self.config['reporting']['include_evidence']:
                    vuln['evidence'] = result.evidence
                
                vulnerabilities.append(vuln)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(severity_counts)
        
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'vulnerabilities_found': len(vulnerabilities),
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score),
                'severity_distribution': severity_counts,
                'category_distribution': category_counts
            },
            'vulnerabilities': vulnerabilities,
            'test_results': [],
            'recommendations': self._generate_security_recommendations(vulnerabilities)
        }
        
        # Add detailed test results
        for result in filtered_results:
            test_detail = {
                'test_name': result.test_name,
                'category': result.test_category,
                'severity': result.severity,
                'status': result.status,
                'description': result.description,
                'execution_time_ms': result.execution_time_ms,
                'timestamp': result.timestamp.isoformat()
            }
            
            if result.errors:
                test_detail['errors'] = result.errors
            
            if result.vulnerability_details:
                test_detail['vulnerability_details'] = result.vulnerability_details
            
            if self.config['reporting']['include_remediation'] and result.remediation:
                test_detail['remediation'] = result.remediation
            
            if self.config['reporting']['include_evidence'] and result.evidence:
                test_detail['evidence'] = result.evidence
            
            report['test_results'].append(test_detail)
        
        return report
    
    def _calculate_risk_score(self, severity_counts: Dict[str, int]) -> float:
        """Calculate overall risk score based on vulnerabilities."""
        weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 2, 'info': 1}
        
        total_score = 0
        for severity, count in severity_counts.items():
            total_score += weights.get(severity, 0) * count
        
        # Normalize to 0-100 scale
        max_possible_score = 100  # Assuming maximum of 10 critical vulnerabilities
        return min(total_score, max_possible_score)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on score."""
        if risk_score >= 70:
            return "Critical"
        elif risk_score >= 50:
            return "High"
        elif risk_score >= 30:
            return "Medium"
        elif risk_score >= 10:
            return "Low"
        else:
            return "Minimal"
    
    def _generate_security_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on found vulnerabilities."""
        recommendations = []
        
        # Group vulnerabilities by category
        categories = {}
        for vuln in vulnerabilities:
            category = vuln['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(vuln)
        
        # Generate category-specific recommendations
        if 'injection' in categories:
            recommendations.append(
                "Implement parameterized queries and input validation to prevent SQL injection attacks"
            )
        
        if 'xss' in categories:
            recommendations.append(
                "Implement proper input sanitization and output encoding to prevent XSS attacks"
            )
        
        if 'authentication' in categories:
            auth_issues = categories['authentication']
            if any('weak_password' in vuln.get('vulnerability_details', {}) for vuln in auth_issues):
                recommendations.append(
                    "Implement strong password policy with minimum complexity requirements"
                )
            if any('brute_force' in vuln['test_name'] for vuln in auth_issues):
                recommendations.append(
                    "Implement rate limiting and account lockout mechanisms"
                )
            if any('session' in vuln['test_name'] for vuln in auth_issues):
                recommendations.append(
                    "Configure secure session management with HttpOnly, Secure, and SameSite flags"
                )
        
        if 'ssl' in categories:
            recommendations.append(
                "Update SSL/TLS configuration to use strong protocols and cipher suites"
            )
        
        # General recommendations
        critical_vulns = [v for v in vulnerabilities if v['severity'] == 'critical']
        if critical_vulns:
            recommendations.insert(0, 
                f"URGENT: Address {len(critical_vulns)} critical vulnerabilities immediately"
            )
        
        if not recommendations:
            recommendations.append("Continue monitoring and regular security assessments")
        
        return recommendations
    
    async def save_report(self, report: Dict[str, Any], output_path: str = "security_test_report.json"):
        """Save security test report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Security test report saved to: {output_path}")


# CLI Interface
async def main():
    """Main CLI interface for security testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Test Orchestration Engine")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--url", help="Target URL for quick test")
    parser.add_argument("--categories", nargs='+', 
                       choices=['injection', 'xss', 'authentication', 'ssl'],
                       default=['injection', 'xss', 'authentication', 'ssl'],
                       help="Test categories to run")
    parser.add_argument("--output", default="security_test_report.json", help="Output report file")
    parser.add_argument("--severity", choices=['critical', 'high', 'medium', 'low', 'info'],
                       default='low', help="Minimum severity to report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize orchestrator
    orchestrator = SecurityTestOrchestrator(args.config)
    
    # Override severity threshold
    orchestrator.config['reporting']['severity_threshold'] = args.severity
    
    try:
        test_suites = []
        
        if args.url:
            # Quick test mode
            suite = SecurityTestSuite(
                name="quick_security_test",
                target_url=args.url,
                test_categories=args.categories
            )
            test_suites.append(suite)
        else:
            # Load from configuration
            for name, suite_config in orchestrator.config.get('test_suites', {}).items():
                suite = SecurityTestSuite(
                    name=name,
                    **suite_config
                )
                test_suites.append(suite)
        
        if not test_suites:
            logger.error("No test suites found")
            return
        
        # Run tests
        report = await orchestrator.run_security_tests(test_suites)
        
        # Save report
        await orchestrator.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n🔒 Security Test Results")
        print(f"{'='*50}")
        print(f"Tests Executed: {summary['total_tests']}")
        print(f"Vulnerabilities Found: {summary['vulnerabilities_found']}")
        print(f"Risk Level: {summary['risk_level']}")
        print(f"Risk Score: {summary['risk_score']}/100")
        
        if summary['vulnerabilities_found'] > 0:
            print(f"\n🚨 Vulnerability Summary:")
            for severity, count in summary['severity_distribution'].items():
                if count > 0:
                    print(f"  {severity.upper()}: {count}")
            
            print(f"\n💡 Top Recommendations:")
            for rec in report['recommendations'][:3]:  # Show first 3 recommendations
                print(f"  - {rec}")
        else:
            print(f"\n✅ No vulnerabilities found!")
    
    except Exception as e:
        logger.error(f"Security test execution failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())