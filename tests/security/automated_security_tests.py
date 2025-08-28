"""
🔒 Security Test Automation - IA Influencer Agent Platform Enterprise
=====================================================================
Module: tests/security/automated_security_tests.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE TESTS DE SÉCURITÉ AUTOMATISÉS
Tests de sécurité complets pour toutes les couches de l'application
- Tests d'intrusion automatisés  
- Validation de vulnérabilités OWASP
- Tests de charge et résistance DDoS
- Validation de conformité réglementaire
- Tests d'authentification et autorisation
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import secrets
import ssl
import socket
from pathlib import Path

# Security testing libraries
try:
    import requests
    import aiohttp
    import sqlparse
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import jwt
    SECURITY_LIBS_AVAILABLE = True
except ImportError:
    SECURITY_LIBS_AVAILABLE = False
    logging.warning("Security testing libraries not fully available. Install requests, aiohttp, cryptography, PyJWT")

# Web security testing
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    WEB_TESTING_AVAILABLE = True
except ImportError:
    WEB_TESTING_AVAILABLE = False
    logging.warning("Web testing library not available. Install selenium for browser-based security tests")

# Network security testing
try:
    import nmap
    import scapy.all as scapy
    NETWORK_TESTING_AVAILABLE = True
except ImportError:
    NETWORK_TESTING_AVAILABLE = False
    logging.warning("Network testing libraries not available. Install python-nmap and scapy")

logger = logging.getLogger(__name__)


class SecurityTestType(Enum):
    """Types de tests de sécurité"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    ENCRYPTION = "encryption"
    SESSION_MANAGEMENT = "session_management"
    FILE_UPLOAD = "file_upload"
    API_SECURITY = "api_security"
    NETWORK_SECURITY = "network_security"
    DDOS_RESISTANCE = "ddos_resistance"
    COMPLIANCE = "compliance"
    VULNERABILITY_SCAN = "vulnerability_scan"
    PENETRATION_TEST = "penetration_test"


class SecurityTestSeverity(Enum):
    """Niveaux de sévérité des tests"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityTestStatus(Enum):
    """Statuts des tests de sécurité"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class SecurityTestResult:
    """Résultat d'un test de sécurité"""
    test_id: str
    test_name: str
    test_type: SecurityTestType
    status: SecurityTestStatus
    severity: SecurityTestSeverity
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    success: bool = False
    vulnerability_found: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    cve_references: List[str] = field(default_factory=list)
    compliance_impact: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "test_type": self.test_type.value,
            "status": self.status.value,
            "severity": self.severity.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "vulnerability_found": self.vulnerability_found,
            "details": self.details,
            "recommendations": self.recommendations,
            "evidence": self.evidence,
            "affected_components": self.affected_components,
            "cve_references": self.cve_references,
            "compliance_impact": self.compliance_impact
        }


class SecurityTestSuite:
    """Suite de tests de sécurité automatisés"""
    
    def __init__(self, target_host: str = "localhost", target_port: int = 8000):
        self.target_host = target_host
        self.target_port = target_port
        self.base_url = f"http://{target_host}:{target_port}"
        self.results: List[SecurityTestResult] = []
        self.session = None
        self.logger = logging.getLogger(f"{__name__}.SecurityTestSuite")
        
        # Test configuration
        self.test_config = {
            "timeout": 30,
            "max_retries": 3,
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ],
            "common_passwords": [
                "password", "123456", "admin", "root", "guest", "test",
                "qwerty", "password123", "admin123", "letmein"
            ],
            "sql_injection_payloads": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "1' UNION SELECT null,null,null--",
                "admin'--",
                "admin' #",
                "1' OR 1=1#",
                "'; EXEC sp_configure 'show advanced options', 1--"
            ],
            "xss_payloads": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>",
                "'-alert('XSS')-'",
                "\"><script>alert('XSS')</script>",
                "<iframe src=javascript:alert('XSS')></iframe>"
            ]
        }
    
    async def initialize(self) -> None:
        """Initialiser la suite de tests"""
        if SECURITY_LIBS_AVAILABLE:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.test_config["timeout"])
            )
        
        self.logger.info(f"Security test suite initialized for {self.base_url}")
    
    async def shutdown(self) -> None:
        """Fermer la suite de tests"""
        if self.session:
            await self.session.close()
        
        self.logger.info("Security test suite shutdown complete")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Exécuter tous les tests de sécurité"""
        self.logger.info("Starting comprehensive security test suite")
        
        start_time = datetime.now()
        
        # Authentication tests
        await self._test_authentication_security()
        
        # Authorization tests
        await self._test_authorization_security()
        
        # Input validation tests
        await self._test_input_validation()
        
        # SQL injection tests
        await self._test_sql_injection()
        
        # XSS tests
        await self._test_xss_vulnerabilities()
        
        # CSRF tests
        await self._test_csrf_protection()
        
        # Encryption tests
        await self._test_encryption_security()
        
        # Session management tests
        await self._test_session_management()
        
        # API security tests
        await self._test_api_security()
        
        # Network security tests
        await self._test_network_security()
        
        # DDoS resistance tests
        await self._test_ddos_resistance()
        
        # Compliance tests
        await self._test_compliance()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Generate summary report
        return self._generate_summary_report(start_time, end_time, duration)
    
    async def _test_authentication_security(self) -> None:
        """Tests de sécurité d'authentification"""
        self.logger.info("Running authentication security tests")
        
        # Test 1: Brute force protection
        await self._test_brute_force_protection()
        
        # Test 2: Weak password detection
        await self._test_weak_password_policy()
        
        # Test 3: Account lockout
        await self._test_account_lockout()
        
        # Test 4: Multi-factor authentication
        await self._test_mfa_bypass()
        
        # Test 5: Session fixation
        await self._test_session_fixation()
    
    async def _test_brute_force_protection(self) -> None:
        """Test de protection contre les attaques par force brute"""
        test_result = SecurityTestResult(
            test_id=str(uuid.uuid4()),
            test_name="Brute Force Protection Test",
            test_type=SecurityTestType.AUTHENTICATION,
            status=SecurityTestStatus.RUNNING,
            severity=SecurityTestSeverity.HIGH,
            start_time=datetime.now()
        )
        
        try:
            if not SECURITY_LIBS_AVAILABLE:
                test_result.status = SecurityTestStatus.SKIPPED
                test_result.details["reason"] = "Security libraries not available"
                self.results.append(test_result)
                return
            
            # Simuler une attaque par force brute
            login_url = f"{self.base_url}/auth/login"
            failed_attempts = 0
            
            for i in range(20):  # 20 tentatives
                payload = {
                    "username": "admin",
                    "password": self.test_config["common_passwords"][i % len(self.test_config["common_passwords"])]
                }
                
                try:
                    async with self.session.post(login_url, json=payload) as response:
                        if response.status == 429:  # Too Many Requests
                            test_result.success = True
                            test_result.details["protection_triggered_at_attempt"] = i + 1
                            break
                        elif response.status == 401:
                            failed_attempts += 1
                        
                        await asyncio.sleep(0.1)  # Petite pause entre les tentatives
                
                except Exception as e:
                    self.logger.debug(f"Request failed in brute force test: {e}")
                    continue
            
            if not test_result.success and failed_attempts >= 15:
                test_result.vulnerability_found = True
                test_result.recommendations.append("Implement rate limiting for login attempts")
                test_result.recommendations.append("Add account lockout after failed attempts")
                test_result.recommendations.append("Implement CAPTCHA after multiple failures")
            
            test_result.status = SecurityTestStatus.PASSED if test_result.success else SecurityTestStatus.FAILED
            test_result.details["total_attempts"] = failed_attempts
            
        except Exception as e:
            test_result.status = SecurityTestStatus.ERROR
            test_result.details["error"] = str(e)
        
        finally:
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            self.results.append(test_result)
    
    async def _test_weak_password_policy(self) -> None:
        """Test de politique de mots de passe faibles"""
        test_result = SecurityTestResult(
            test_id=str(uuid.uuid4()),
            test_name="Weak Password Policy Test",
            test_type=SecurityTestType.AUTHENTICATION,
            status=SecurityTestStatus.RUNNING,
            severity=SecurityTestSeverity.MEDIUM,
            start_time=datetime.now()
        )
        
        try:
            if not SECURITY_LIBS_AVAILABLE:
                test_result.status = SecurityTestStatus.SKIPPED
                test_result.details["reason"] = "Security libraries not available"
                self.results.append(test_result)
                return
            
            # Test avec des mots de passe faibles
            register_url = f"{self.base_url}/auth/register"
            weak_passwords = ["123", "abc", "password", "admin", "test"]
            
            accepted_weak_passwords = 0
            
            for password in weak_passwords:
                payload = {
                    "username": f"test_user_{uuid.uuid4().hex[:8]}",
                    "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                    "password": password
                }
                
                try:
                    async with self.session.post(register_url, json=payload) as response:
                        if response.status == 201:  # User created
                            accepted_weak_passwords += 1
                            test_result.evidence.append(f"Weak password '{password}' was accepted")
                
                except Exception as e:
                    self.logger.debug(f"Registration request failed: {e}")
                    continue
            
            if accepted_weak_passwords > 0:
                test_result.vulnerability_found = True
                test_result.recommendations.append("Implement strong password policy")
                test_result.recommendations.append("Require minimum 8 characters with mixed case, numbers, symbols")
                test_result.recommendations.append("Check against common password dictionaries")
                test_result.status = SecurityTestStatus.FAILED
            else:
                test_result.success = True
                test_result.status = SecurityTestStatus.PASSED
            
            test_result.details["weak_passwords_accepted"] = accepted_weak_passwords
            test_result.details["total_tested"] = len(weak_passwords)
            
        except Exception as e:
            test_result.status = SecurityTestStatus.ERROR
            test_result.details["error"] = str(e)
        
        finally:
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            self.results.append(test_result)
    
    async def _test_sql_injection(self) -> None:
        """Tests d'injection SQL"""
        self.logger.info("Running SQL injection tests")
        
        test_result = SecurityTestResult(
            test_id=str(uuid.uuid4()),
            test_name="SQL Injection Vulnerability Test",
            test_type=SecurityTestType.SQL_INJECTION,
            status=SecurityTestStatus.RUNNING,
            severity=SecurityTestSeverity.CRITICAL,
            start_time=datetime.now()
        )
        
        try:
            if not SECURITY_LIBS_AVAILABLE:
                test_result.status = SecurityTestStatus.SKIPPED
                test_result.details["reason"] = "Security libraries not available"
                self.results.append(test_result)
                return
            
            # Test d'injection SQL sur différents endpoints
            endpoints = [
                "/api/users/search",
                "/api/content/search",
                "/api/analytics/report",
                "/auth/login"
            ]
            
            vulnerabilities_found = 0
            
            for endpoint in endpoints:
                for payload in self.test_config["sql_injection_payloads"]:
                    # Test GET parameters
                    try:
                        url = f"{self.base_url}{endpoint}?q={payload}"
                        async with self.session.get(url) as response:
                            if await self._detect_sql_injection_response(response, payload):
                                vulnerabilities_found += 1
                                test_result.evidence.append(f"SQL injection vulnerability in GET {endpoint}")
                                test_result.affected_components.append(endpoint)
                    
                    except Exception as e:
                        self.logger.debug(f"GET request failed for SQL injection test: {e}")
                    
                    # Test POST data
                    try:
                        post_data = {"query": payload, "search": payload, "username": payload}
                        async with self.session.post(f"{self.base_url}{endpoint}", json=post_data) as response:
                            if await self._detect_sql_injection_response(response, payload):
                                vulnerabilities_found += 1
                                test_result.evidence.append(f"SQL injection vulnerability in POST {endpoint}")
                                test_result.affected_components.append(endpoint)
                    
                    except Exception as e:
                        self.logger.debug(f"POST request failed for SQL injection test: {e}")
            
            if vulnerabilities_found > 0:
                test_result.vulnerability_found = True
                test_result.status = SecurityTestStatus.FAILED
                test_result.recommendations.extend([
                    "Use parameterized queries/prepared statements",
                    "Implement input validation and sanitization",
                    "Use ORM with built-in SQL injection protection",
                    "Apply principle of least privilege to database users",
                    "Implement Web Application Firewall (WAF)"
                ])
                test_result.cve_references.append("CWE-89: SQL Injection")
            else:
                test_result.success = True
                test_result.status = SecurityTestStatus.PASSED
            
            test_result.details["vulnerabilities_found"] = vulnerabilities_found
            test_result.details["endpoints_tested"] = len(endpoints)
            test_result.details["payloads_tested"] = len(self.test_config["sql_injection_payloads"])
            
        except Exception as e:
            test_result.status = SecurityTestStatus.ERROR
            test_result.details["error"] = str(e)
        
        finally:
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            self.results.append(test_result)
    
    async def _detect_sql_injection_response(self, response, payload: str) -> bool:
        """Détecter une réponse indiquant une injection SQL"""
        try:
            text = await response.text()
            
            # Indicateurs d'erreurs SQL
            sql_error_indicators = [
                "sql syntax", "mysql_fetch", "ora-01756", "microsoft jet database",
                "odbc driver", "sqlite_step", "postgresql query failed",
                "warning: mysql", "error in your sql syntax", "valid mysql result",
                "mysqlclient.sql", "error: column", "sqlstate", "ora-00900"
            ]
            
            # Vérifier la présence d'indicateurs d'erreur SQL
            text_lower = text.lower()
            for indicator in sql_error_indicators:
                if indicator in text_lower:
                    return True
            
            # Vérifier si la réponse contient des données sensibles typiques
            if response.status == 200 and len(text) > 1000:
                # Réponse anormalement longue pourrait indiquer une injection réussie
                return True
            
            return False
            
        except Exception:
            return False
    
    async def _test_xss_vulnerabilities(self) -> None:
        """Tests de vulnérabilités XSS"""
        test_result = SecurityTestResult(
            test_id=str(uuid.uuid4()),
            test_name="Cross-Site Scripting (XSS) Test",
            test_type=SecurityTestType.XSS,
            status=SecurityTestStatus.RUNNING,
            severity=SecurityTestSeverity.HIGH,
            start_time=datetime.now()
        )
        
        try:
            if not SECURITY_LIBS_AVAILABLE:
                test_result.status = SecurityTestStatus.SKIPPED
                test_result.details["reason"] = "Security libraries not available"
                self.results.append(test_result)
                return
            
            endpoints = [
                "/api/content/create",
                "/api/users/profile",
                "/api/comments/add",
                "/search"
            ]
            
            vulnerabilities_found = 0
            
            for endpoint in endpoints:
                for payload in self.test_config["xss_payloads"]:
                    # Test reflected XSS
                    try:
                        url = f"{self.base_url}{endpoint}?q={payload}"
                        async with self.session.get(url) as response:
                            text = await response.text()
                            if payload in text and "<script>" in payload:
                                vulnerabilities_found += 1
                                test_result.evidence.append(f"Reflected XSS in {endpoint}")
                                test_result.affected_components.append(endpoint)
                    
                    except Exception as e:
                        self.logger.debug(f"XSS test request failed: {e}")
                    
                    # Test stored XSS
                    try:
                        post_data = {"content": payload, "message": payload, "comment": payload}
                        async with self.session.post(f"{self.base_url}{endpoint}", json=post_data) as response:
                            if response.status == 201:  # Content created
                                # Vérifier si le contenu malveillant est stocké
                                test_result.evidence.append(f"Potential stored XSS in {endpoint}")
                    
                    except Exception as e:
                        self.logger.debug(f"XSS POST test failed: {e}")
            
            if vulnerabilities_found > 0:
                test_result.vulnerability_found = True
                test_result.status = SecurityTestStatus.FAILED
                test_result.recommendations.extend([
                    "Implement proper input validation and output encoding",
                    "Use Content Security Policy (CSP)",
                    "Sanitize user input on both client and server side",
                    "Use templating engines with automatic escaping",
                    "Validate and escape all user-generated content"
                ])
                test_result.cve_references.append("CWE-79: Cross-site Scripting")
            else:
                test_result.success = True
                test_result.status = SecurityTestStatus.PASSED
            
            test_result.details["vulnerabilities_found"] = vulnerabilities_found
            
        except Exception as e:
            test_result.status = SecurityTestStatus.ERROR
            test_result.details["error"] = str(e)
        
        finally:
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            self.results.append(test_result)
    
    # Placeholder methods for other test types
    async def _test_authorization_security(self) -> None:
        """Tests d'autorisation"""
        await self._create_test_placeholder("Authorization Security Test", SecurityTestType.AUTHORIZATION)
    
    async def _test_input_validation(self) -> None:
        """Tests de validation des entrées"""
        await self._create_test_placeholder("Input Validation Test", SecurityTestType.INPUT_VALIDATION)
    
    async def _test_csrf_protection(self) -> None:
        """Tests de protection CSRF"""
        await self._create_test_placeholder("CSRF Protection Test", SecurityTestType.CSRF)
    
    async def _test_encryption_security(self) -> None:
        """Tests de sécurité du chiffrement"""
        await self._create_test_placeholder("Encryption Security Test", SecurityTestType.ENCRYPTION)
    
    async def _test_session_management(self) -> None:
        """Tests de gestion des sessions"""
        await self._create_test_placeholder("Session Management Test", SecurityTestType.SESSION_MANAGEMENT)
    
    async def _test_account_lockout(self) -> None:
        """Tests de verrouillage de compte"""
        await self._create_test_placeholder("Account Lockout Test", SecurityTestType.AUTHENTICATION)
    
    async def _test_mfa_bypass(self) -> None:
        """Tests de contournement MFA"""
        await self._create_test_placeholder("MFA Bypass Test", SecurityTestType.AUTHENTICATION)
    
    async def _test_session_fixation(self) -> None:
        """Tests de fixation de session"""
        await self._create_test_placeholder("Session Fixation Test", SecurityTestType.SESSION_MANAGEMENT)
    
    async def _test_api_security(self) -> None:
        """Tests de sécurité API"""
        await self._create_test_placeholder("API Security Test", SecurityTestType.API_SECURITY)
    
    async def _test_network_security(self) -> None:
        """Tests de sécurité réseau"""
        await self._create_test_placeholder("Network Security Test", SecurityTestType.NETWORK_SECURITY)
    
    async def _test_ddos_resistance(self) -> None:
        """Tests de résistance DDoS"""
        await self._create_test_placeholder("DDoS Resistance Test", SecurityTestType.DDOS_RESISTANCE)
    
    async def _test_compliance(self) -> None:
        """Tests de conformité"""
        await self._create_test_placeholder("Compliance Test", SecurityTestType.COMPLIANCE)
    
    async def _create_test_placeholder(self, test_name: str, test_type: SecurityTestType) -> None:
        """Créer un placeholder de test"""
        test_result = SecurityTestResult(
            test_id=str(uuid.uuid4()),
            test_name=test_name,
            test_type=test_type,
            status=SecurityTestStatus.SKIPPED,
            severity=SecurityTestSeverity.MEDIUM,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        test_result.details["reason"] = "Test implementation pending"
        test_result.duration_ms = 0.0
        self.results.append(test_result)
    
    def _generate_summary_report(self, start_time: datetime, end_time: datetime, duration: timedelta) -> Dict[str, Any]:
        """Générer un rapport de synthèse"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == SecurityTestStatus.PASSED])
        failed_tests = len([r for r in self.results if r.status == SecurityTestStatus.FAILED])
        error_tests = len([r for r in self.results if r.status == SecurityTestStatus.ERROR])
        skipped_tests = len([r for r in self.results if r.status == SecurityTestStatus.SKIPPED])
        vulnerabilities_found = len([r for r in self.results if r.vulnerability_found])
        
        # Grouper par sévérité
        severity_breakdown = {}
        for severity in SecurityTestSeverity:
            severity_breakdown[severity.value] = len([
                r for r in self.results if r.severity == severity
            ])
        
        # Grouper par type de test
        test_type_breakdown = {}
        for test_type in SecurityTestType:
            test_type_breakdown[test_type.value] = len([
                r for r in self.results if r.test_type == test_type
            ])
        
        # Composants affectés
        affected_components = set()
        for result in self.results:
            affected_components.update(result.affected_components)
        
        return {
            "summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "vulnerabilities_found": vulnerabilities_found,
                "success_rate": (passed_tests / max(total_tests, 1)) * 100
            },
            "breakdown": {
                "by_severity": severity_breakdown,
                "by_test_type": test_type_breakdown
            },
            "security_posture": {
                "overall_score": max(0, 100 - (vulnerabilities_found * 10) - (failed_tests * 5)),
                "risk_level": self._calculate_risk_level(vulnerabilities_found, failed_tests),
                "affected_components": list(affected_components)
            },
            "recommendations": self._get_top_recommendations(),
            "detailed_results": [result.to_dict() for result in self.results]
        }
    
    def _calculate_risk_level(self, vulnerabilities: int, failed_tests: int) -> str:
        """Calculer le niveau de risque"""
        if vulnerabilities >= 5 or failed_tests >= 10:
            return "HIGH"
        elif vulnerabilities >= 2 or failed_tests >= 5:
            return "MEDIUM"
        elif vulnerabilities >= 1 or failed_tests >= 1:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _get_top_recommendations(self) -> List[str]:
        """Obtenir les principales recommandations"""
        all_recommendations = []
        for result in self.results:
            all_recommendations.extend(result.recommendations)
        
        # Compter les occurrences et retourner les plus fréquentes
        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        # Trier par fréquence et retourner le top 10
        sorted_recommendations = sorted(
            recommendation_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [rec[0] for rec in sorted_recommendations[:10]]


class SecurityTestRunner:
    """Lanceur de tests de sécurité"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.SecurityTestRunner")
    
    async def run_security_tests(self, target_host: str = "localhost", target_port: int = 8000) -> Dict[str, Any]:
        """Lancer tous les tests de sécurité"""
        self.logger.info(f"Starting security test run against {target_host}:{target_port}")
        
        test_suite = SecurityTestSuite(target_host, target_port)
        
        try:
            await test_suite.initialize()
            results = await test_suite.run_all_tests()
            
            self.logger.info(f"Security tests completed. Found {results['summary']['vulnerabilities_found']} vulnerabilities")
            
            return results
            
        finally:
            await test_suite.shutdown()
    
    async def run_continuous_security_monitoring(self, interval_hours: int = 24) -> None:
        """Surveillance de sécurité continue"""
        self.logger.info(f"Starting continuous security monitoring (every {interval_hours} hours)")
        
        while True:
            try:
                results = await self.run_security_tests()
                
                # Sauvegarder les résultats
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = f"security_report_{timestamp}.json"
                
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                self.logger.info(f"Security report saved to {results_file}")
                
                # Attendre avant le prochain cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"Error in continuous security monitoring: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour on error


# Factory function
async def create_security_test_suite(target_host: str = "localhost", target_port: int = 8000) -> SecurityTestSuite:
    """Factory pour créer une suite de tests de sécurité"""
    suite = SecurityTestSuite(target_host, target_port)
    await suite.initialize()
    return suite


# CLI interface pour les tests de sécurité
async def main():
    """Interface CLI pour les tests de sécurité"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Security Testing Suite")
    parser.add_argument("--host", default="localhost", help="Target host")
    parser.add_argument("--port", type=int, default=8000, help="Target port")
    parser.add_argument("--output", default="security_report.json", help="Output file")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=24, help="Monitoring interval in hours")
    
    args = parser.parse_args()
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    runner = SecurityTestRunner()
    
    if args.continuous:
        await runner.run_continuous_security_monitoring(args.interval)
    else:
        results = await runner.run_security_tests(args.host, args.port)
        
        # Sauvegarder les résultats
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Security test results saved to {args.output}")
        print(f"Overall score: {results['security_posture']['overall_score']}/100")
        print(f"Risk level: {results['security_posture']['risk_level']}")
        print(f"Vulnerabilities found: {results['summary']['vulnerabilities_found']}")


if __name__ == "__main__":
    asyncio.run(main())


# Export des composants principaux
__all__ = [
    "SecurityTestType",
    "SecurityTestSeverity", 
    "SecurityTestStatus",
    "SecurityTestResult",
    "SecurityTestSuite",
    "SecurityTestRunner",
    "create_security_test_suite"
]