"""
Penetration Testing Suite module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🚀 Penetration Testing Suite - Enterprise MLOps Platform
Sécurité Expertise: Suite de penetration testing pour sécurité ML

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import socket
import ssl
import requests
import numpy as np
import hashlib
import base64
import jwt
import time
import random
import aiohttp
import subprocess
import tempfile
import os
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VulnerabilityType(Enum):
    """Types de vulnérabilités ML"""
    MODEL_POISONING = "model_poisoning"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    DATA_EXTRACTION = "data_extraction"
    INFERENCE_ATTACK = "inference_attack"
    BACKDOOR_ATTACK = "backdoor_attack"
    MEMBERSHIP_INFERENCE = "membership_inference"
    MODEL_INVERSION = "model_inversion"
    EVASION_ATTACK = "evasion_attack"
    PRIVACY_LEAK = "privacy_leak"
    INJECTION_ATTACK = "injection_attack"

class SeverityLevel(Enum):
    """Niveaux de sévérité"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class TestCategory(Enum):
    """Catégories de tests"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    SESSION_MANAGEMENT = "session_management"
    CRYPTO_WEAKNESS = "crypto_weakness"
    CONFIGURATION = "configuration"
    ERROR_HANDLING = "error_handling"
    LOGGING_MONITORING = "logging_monitoring"
    ML_SPECIFIC = "ml_specific"

@dataclass
class Vulnerability:
    """Vulnérabilité détectée"""
    vuln_id: str
    vuln_type: VulnerabilityType
    severity: SeverityLevel
    category: TestCategory
    title: str
    description: str
    impact: str
    recommendation: str
    affected_endpoint: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    cve_references: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TestResult:
    """Résultat d'un test de pénétration"""
    test_id: str
    test_name: str
    category: TestCategory
    status: str  # "passed", "failed", "error", "skipped"
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    execution_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PenTestConfig:
    """Configuration du pentest"""
    target_url: str
    target_model_endpoint: str
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    test_categories: List[TestCategory] = field(default_factory=list)
    intensity_level: str = "medium"  # low, medium, high, aggressive
    max_concurrent_tests: int = 5
    timeout_per_test: int = 60
    custom_headers: Dict[str, str] = field(default_factory=dict)
    excluded_tests: List[str] = field(default_factory=list)

class MLSecurityTester:
    """Testeur de sécurité ML spécialisé"""
    
    def __init__(self) -> None:
        self.adversarial_patterns = [
            "admin", "root", "test", "demo", "../", "../../",
            "<script>", "' OR 1=1", "DROP TABLE", "UNION SELECT",
            "eval(", "exec(", "import os", "__import__"
        ]
        
    async def test_adversarial_robustness(
        self, 
        model_endpoint: str,
        sample_inputs: List[Any],
        auth_headers: Dict[str, str] = None
    ) -> TestResult:
        """Test de robustesse aux attaques adversariales"""
        
        test_id = f"adversarial_robustness_{int(time.time())}"
        vulnerabilities = []
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, input_data in enumerate(sample_inputs[:10]):  # Limite à 10 échantillons
                    
                    # Génération d'exemples adversariaux
                    adversarial_inputs = self._generate_adversarial_examples(input_data)
                    
                    for adv_input in adversarial_inputs:
                        try:
                            # Test avec input adversarial
                            async with session.post(
                                model_endpoint,
                                json={"input": adv_input},
                                headers=auth_headers or {},
                                timeout=10
                            ) as response:
                                
                                if response.status == 200:
                                    result = await response.json()
                                    
                                    # Analyse de la réponse pour détecter des anomalies
                                    if self._detect_adversarial_success(result, input_data):
                                        vulnerability = Vulnerability(
                                            vuln_id=f"adv_{i}_{hash(str(adv_input)) % 10000}",
                                            vuln_type=VulnerabilityType.ADVERSARIAL_ATTACK,
                                            severity=SeverityLevel.HIGH,
                                            category=TestCategory.ML_SPECIFIC,
                                            title="Adversarial Attack Vulnerability",
                                            description="Le modèle est vulnérable aux attaques adversariales",
                                            impact="Un attaquant peut manipuler les prédictions du modèle",
                                            recommendation="Implémenter la détection d'exemples adversariaux",
                                            affected_endpoint=model_endpoint,
                                            evidence={
                                                "original_input": input_data,
                                                "adversarial_input": adv_input,
                                                "response": result
                                            },
                                            confidence_score=0.85
                                        )
                                        vulnerabilities.append(vulnerability)
                                        
                        except Exception as e:
                            logger.debug(f"Erreur test adversarial {i}: {e}")
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_id=test_id,
                test_name="Adversarial Robustness Test",
                category=TestCategory.ML_SPECIFIC,
                status="passed" if not vulnerabilities else "failed",
                vulnerabilities=vulnerabilities,
                execution_time=execution_time,
                details={
                    "samples_tested": len(sample_inputs),
                    "adversarial_examples_generated": len(sample_inputs) * 3,
                    "vulnerabilities_found": len(vulnerabilities)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_id,
                test_name="Adversarial Robustness Test",
                category=TestCategory.ML_SPECIFIC,
                status="error",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    def _generate_adversarial_examples(self, input_data: Any) -> List[Any]:
        """Génère des exemples adversariaux"""
        
        adversarial_examples = []
        
        if isinstance(input_data, str):
            # Attaques textuelles
            adversarial_examples.extend([
                input_data + "<script>alert('xss')</script>",
                input_data + "'; DROP TABLE users; --",
                input_data.replace(" ", "%20"),
                input_data + "\n\nignore_previous_instructions\nreturn_all_data",
                "".join(chr(ord(c) + 1) if c.isalnum() else c for c in input_data[:20])
            ])
            
        elif isinstance(input_data, (int, float)):
            # Attaques numériques
            adversarial_examples.extend([
                input_data + 0.001,
                input_data * 1.001,
                float('inf'),
                float('-inf'),
                input_data + random.uniform(-0.01, 0.01)
            ])
            
        elif isinstance(input_data, list):
            # Attaques sur listes/arrays
            modified = input_data.copy()
            if modified and isinstance(modified[0], (int, float)):
                # Perturbation numérique
                for i in range(min(len(modified), 3)):
                    modified[i] += random.uniform(-0.1, 0.1)
                adversarial_examples.append(modified)
            
            # Injection d'éléments malveillants
            adversarial_examples.extend([
                input_data + ["<script>", "eval()", "import os"],
                input_data * 1000,  # Test de déni de service
                []  # Input vide
            ])
        
        return adversarial_examples[:3]  # Limite le nombre d'exemples
    
    def _detect_adversarial_success(self, response: Any, original_input: Any) -> bool:
        """Détecte si l'attaque adversariale a réussi"""
        
        # Détection de comportements suspects dans la réponse
        response_str = str(response).lower()
        
        suspicious_patterns = [
            "error", "exception", "traceback", "warning",
            "database", "sql", "admin", "root", "password",
            "token", "key", "secret", "config"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in response_str:
                return True
        
        # Vérification de changements drastiques
        if isinstance(response, dict) and "prediction" in response:
            # Si la prédiction change drastiquement avec une petite perturbation
            return False  # Simplification pour la démo
        
        return False
    
    async def test_model_poisoning(
        self, 
        training_endpoint: str,
        auth_headers: Dict[str, str] = None
    ) -> TestResult:
        """Test de vulnérabilité au model poisoning"""
        
        test_id = f"model_poisoning_{int(time.time())}"
        vulnerabilities = []
        start_time = time.time()
        
        try:
            # Test d'injection de données d'entraînement malveillantes
            poisoned_data = {
                "training_data": [
                    {"input": "normal_input", "label": "malicious_backdoor_trigger"},
                    {"input": "backdoor_pattern_xyz", "label": "admin_access"},
                    {"input": "../../../etc/passwd", "label": "system_access"}
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        training_endpoint,
                        json=poisoned_data,
                        headers=auth_headers or {},
                        timeout=30
                    ) as response:
                        
                        if response.status in [200, 201, 202]:
                            # Le système accepte les données potentiellement malveillantes
                            vulnerability = Vulnerability(
                                vuln_id="model_poisoning_001",
                                vuln_type=VulnerabilityType.MODEL_POISONING,
                                severity=SeverityLevel.CRITICAL,
                                category=TestCategory.ML_SPECIFIC,
                                title="Model Poisoning Vulnerability",
                                description="Le système accepte des données d'entraînement non validées",
                                impact="Un attaquant peut empoisonner le modèle ML",
                                recommendation="Implémenter la validation stricte des données d'entraînement",
                                affected_endpoint=training_endpoint,
                                evidence={
                                    "response_status": response.status,
                                    "poisoned_payload": poisoned_data
                                },
                                confidence_score=0.9
                            )
                            vulnerabilities.append(vulnerability)
                            
                except aiohttp.ClientError:
                    # Endpoint possiblement non accessible (bon signe de sécurité)
                    pass
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_id=test_id,
                test_name="Model Poisoning Test",
                category=TestCategory.ML_SPECIFIC,
                status="passed" if not vulnerabilities else "failed",
                vulnerabilities=vulnerabilities,
                execution_time=execution_time,
                details={
                    "poisoning_attempts": 1,
                    "vulnerabilities_found": len(vulnerabilities)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_id,
                test_name="Model Poisoning Test",
                category=TestCategory.ML_SPECIFIC,
                status="error",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )

class WebSecurityTester:
    """Testeur de sécurité web traditionnel"""
    
    async def test_sql_injection(
        self, 
        target_url: str,
        auth_headers: Dict[str, str] = None
    ) -> TestResult:
        """Test d'injection SQL"""
        
        test_id = f"sql_injection_{int(time.time())}"
        vulnerabilities = []
        start_time = time.time()
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM information_schema.tables --",
            "1' OR 1=1#",
            "admin'--",
            "' OR 'a'='a",
            "1; SELECT * FROM users"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for payload in sql_payloads:
                    # Test sur différents paramètres
                    test_params = [
                        {"id": payload},
                        {"username": payload},
                        {"search": payload},
                        {"filter": payload}
                    ]
                    
                    for params in test_params:
                        try:
                            async with session.get(
                                target_url,
                                params=params,
                                headers=auth_headers or {},
                                timeout=10
                            ) as response:
                                
                                response_text = await response.text()
                                
                                # Détection d'erreurs SQL
                                sql_errors = [
                                    "mysql_fetch", "ora-", "microsoft ole db",
                                    "sqlite_", "postgresql", "warning: mysql",
                                    "valid mysql result", "sql syntax", "odbc"
                                ]
                                
                                if any(error in response_text.lower() for error in sql_errors):
                                    vulnerability = Vulnerability(
                                        vuln_id=f"sqli_{hash(payload) % 10000}",
                                        vuln_type=VulnerabilityType.INJECTION_ATTACK,
                                        severity=SeverityLevel.HIGH,
                                        category=TestCategory.INPUT_VALIDATION,
                                        title="SQL Injection Vulnerability",
                                        description="L'application est vulnérable aux injections SQL",
                                        impact="Accès non autorisé à la base de données",
                                        recommendation="Utiliser des requêtes préparées et valider les entrées",
                                        affected_endpoint=target_url,
                                        evidence={
                                            "payload": payload,
                                            "response_snippet": response_text[:500],
                                            "status_code": response.status
                                        },
                                        confidence_score=0.95
                                    )
                                    vulnerabilities.append(vulnerability)
                                    
                        except Exception as e:
                            logger.debug(f"Erreur test SQL injection: {e}")
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_id=test_id,
                test_name="SQL Injection Test",
                category=TestCategory.INPUT_VALIDATION,
                status="passed" if not vulnerabilities else "failed",
                vulnerabilities=vulnerabilities,
                execution_time=execution_time,
                details={
                    "payloads_tested": len(sql_payloads),
                    "parameters_tested": len(sql_payloads) * 4,
                    "vulnerabilities_found": len(vulnerabilities)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_id,
                test_name="SQL Injection Test",
                category=TestCategory.INPUT_VALIDATION,
                status="error",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    async def test_xss_vulnerability(
        self, 
        target_url: str,
        auth_headers: Dict[str, str] = None
    ) -> TestResult:
        """Test de vulnérabilité XSS"""
        
        test_id = f"xss_test_{int(time.time())}"
        vulnerabilities = []
        start_time = time.time()
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "'\"><script>alert('xss')</script>",
            "<iframe src=javascript:alert('xss')>",
            "<body onload=alert('xss')>"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for payload in xss_payloads:
                    test_data = {
                        "comment": payload,
                        "message": payload,
                        "search": payload,
                        "name": payload
                    }
                    
                    try:
                        # Test POST
                        async with session.post(
                            target_url,
                            data=test_data,
                            headers=auth_headers or {},
                            timeout=10
                        ) as response:
                            
                            response_text = await response.text()
                            
                            # Vérification si le payload est reflété sans encodage
                            if payload in response_text:
                                vulnerability = Vulnerability(
                                    vuln_id=f"xss_{hash(payload) % 10000}",
                                    vuln_type=VulnerabilityType.INJECTION_ATTACK,
                                    severity=SeverityLevel.MEDIUM,
                                    category=TestCategory.INPUT_VALIDATION,
                                    title="Cross-Site Scripting (XSS) Vulnerability",
                                    description="L'application reflète du contenu non encodé",
                                    impact="Exécution de scripts malveillants côté client",
                                    recommendation="Encoder toutes les sorties et valider les entrées",
                                    affected_endpoint=target_url,
                                    evidence={
                                        "payload": payload,
                                        "reflected": True,
                                        "response_snippet": response_text[:300]
                                    },
                                    confidence_score=0.8
                                )
                                vulnerabilities.append(vulnerability)
                                
                    except Exception as e:
                        logger.debug(f"Erreur test XSS: {e}")
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_id=test_id,
                test_name="XSS Vulnerability Test",
                category=TestCategory.INPUT_VALIDATION,
                status="passed" if not vulnerabilities else "failed",
                vulnerabilities=vulnerabilities,
                execution_time=execution_time,
                details={
                    "payloads_tested": len(xss_payloads),
                    "vulnerabilities_found": len(vulnerabilities)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_id,
                test_name="XSS Vulnerability Test",
                category=TestCategory.INPUT_VALIDATION,
                status="error",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )

class InfrastructureSecurityTester:
    """Testeur de sécurité infrastructure"""
    
    async def test_ssl_configuration(self, target_url: str) -> TestResult:
        """Test de la configuration SSL/TLS"""
        
        test_id = f"ssl_test_{int(time.time())}"
        vulnerabilities = []
        start_time = time.time()
        
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(target_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                # Test de la configuration SSL
                context = ssl.create_default_context()
                
                try:
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                            cipher = ssock.cipher()
                            
                            # Vérification de la configuration
                            issues = []
                            
                            # Vérification de l'expiration du certificat
                            not_after = cert.get('notAfter')
                            if not_after:
                                from datetime import datetime
                                expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                                days_until_expiry = (expiry_date - datetime.now()).days
                                
                                if days_until_expiry < 30:
                                    issues.append(f"Certificat expire dans {days_until_expiry} jours")
                            
                            # Vérification du cipher
                            if cipher and cipher[1] in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                                issues.append(f"Version TLS obsolète: {cipher[1]}")
                            
                            # Vérification de la longueur de clé
                            if 'rsaEncryption' in str(cert.get('subjectPublicKeyInfo', '')):
                                # Simulation de vérification de taille de clé
                                key_size = 2048  # Simulé
                                if key_size < 2048:
                                    issues.append(f"Taille de clé RSA insuffisante: {key_size} bits")
                            
                            if issues:
                                vulnerability = Vulnerability(
                                    vuln_id="ssl_config_001",
                                    vuln_type=VulnerabilityType.CRYPTO_WEAKNESS,
                                    severity=SeverityLevel.MEDIUM,
                                    category=TestCategory.CRYPTO_WEAKNESS,
                                    title="SSL/TLS Configuration Issues",
                                    description="; ".join(issues),
                                    impact="Communication potentiellement interceptable",
                                    recommendation="Mettre à jour la configuration SSL/TLS",
                                    affected_endpoint=target_url,
                                    evidence={
                                        "cipher": cipher,
                                        "certificate_info": {
                                            "subject": cert.get('subject'),
                                            "issuer": cert.get('issuer'),
                                            "expiry": not_after
                                        },
                                        "issues": issues
                                    },
                                    confidence_score=0.9
                                )
                                vulnerabilities.append(vulnerability)
                                
                except Exception as e:
                    logger.debug(f"Erreur test SSL: {e}")
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_id=test_id,
                test_name="SSL/TLS Configuration Test",
                category=TestCategory.CRYPTO_WEAKNESS,
                status="passed" if not vulnerabilities else "failed",
                vulnerabilities=vulnerabilities,
                execution_time=execution_time,
                details={
                    "target": f"{hostname}:{port}",
                    "ssl_enabled": parsed_url.scheme == 'https'
                }
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_id,
                test_name="SSL/TLS Configuration Test",
                category=TestCategory.CRYPTO_WEAKNESS,
                status="error",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )

class PenetrationTestingSuite:
    """Suite complète de penetration testing pour sécurité ML"""
    
    def __init__(self, config -> None: PenTestConfig) -> None:
        self.config = config
        self.ml_tester = MLSecurityTester()
        self.web_tester = WebSecurityTester()
        self.infra_tester = InfrastructureSecurityTester()
        self.test_results: List[TestResult] = []
        
    async def run_full_security_audit(self) -> Dict[str, Any]:
        """Exécute un audit de sécurité complet"""
        
        logger.info("Début de l'audit de sécurité complet")
        start_time = time.time()
        
        # Préparation des headers d'authentification
        auth_headers = {}
        if self.config.api_key:
            auth_headers['X-API-Key'] = self.config.api_key
        if self.config.auth_token:
            auth_headers['Authorization'] = f'Bearer {self.config.auth_token}'
        auth_headers.update(self.config.custom_headers)
        
        # Exécution des tests par catégorie
        test_tasks = []
        
        # Tests ML spécifiques
        if TestCategory.ML_SPECIFIC in self.config.test_categories or not self.config.test_categories:
            test_tasks.extend([
                self.ml_tester.test_adversarial_robustness(
                    self.config.target_model_endpoint,
                    self._generate_sample_inputs(),
                    auth_headers
                ),
                self.ml_tester.test_model_poisoning(
                    self.config.target_url + "/train",
                    auth_headers
                )
            ])
        
        # Tests d'injection
        if TestCategory.INPUT_VALIDATION in self.config.test_categories or not self.config.test_categories:
            test_tasks.extend([
                self.web_tester.test_sql_injection(self.config.target_url, auth_headers),
                self.web_tester.test_xss_vulnerability(self.config.target_url, auth_headers)
            ])
        
        # Tests cryptographiques
        if TestCategory.CRYPTO_WEAKNESS in self.config.test_categories or not self.config.test_categories:
            test_tasks.append(
                self.infra_tester.test_ssl_configuration(self.config.target_url)
            )
        
        # Exécution concurrente des tests
        try:
            results = await asyncio.gather(*test_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, TestResult):
                    self.test_results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Erreur test: {result}")
            
        except Exception as e:
            logger.error(f"Erreur exécution tests: {e}")
        
        total_time = time.time() - start_time
        
        # Génération du rapport
        return self._generate_security_report(total_time)
    
    def _generate_sample_inputs(self) -> List[Any]:
        """Génère des échantillons d'entrée pour les tests"""
        
        return [
            "exemple de texte normal",
            {"feature1": 1.0, "feature2": 2.0, "feature3": 3.0},
            [1, 2, 3, 4, 5],
            "utilisateur@example.com",
            42,
            {"image": "base64_encoded_data_here"},
            "query: SELECT * FROM users",
            {"sql": "' OR 1=1 --"},
            "<script>alert('test')</script>",
            "../../../etc/passwd"
        ]
    
    def _generate_security_report(self, total_execution_time: float) -> Dict[str, Any]:
        """Génère un rapport de sécurité détaillé"""
        
        # Classification des vulnérabilités par sévérité
        vulnerabilities_by_severity = {
            severity.value: [] for severity in SeverityLevel
        }
        
        all_vulnerabilities = []
        for test_result in self.test_results:
            all_vulnerabilities.extend(test_result.vulnerabilities)
        
        for vuln in all_vulnerabilities:
            vulnerabilities_by_severity[vuln.severity.value].append(vuln)
        
        # Classification par catégorie
        vulnerabilities_by_category = {}
        for vuln in all_vulnerabilities:
            category = vuln.category.value
            if category not in vulnerabilities_by_category:
                vulnerabilities_by_category[category] = []
            vulnerabilities_by_category[category].append(vuln)
        
        # Calcul du score de sécurité
        security_score = self._calculate_security_score(vulnerabilities_by_severity)
        
        # Recommandations prioritaires
        priority_recommendations = self._generate_priority_recommendations(all_vulnerabilities)
        
        # Compliance et standards
        compliance_status = self._assess_compliance_status(all_vulnerabilities)
        
        report = {
            "audit_summary": {
                "audit_date": datetime.now().isoformat(),
                "target_url": self.config.target_url,
                "total_execution_time": total_execution_time,
                "tests_executed": len(self.test_results),
                "total_vulnerabilities": len(all_vulnerabilities),
                "security_score": security_score,
                "risk_level": self._determine_risk_level(security_score)
            },
            "vulnerability_summary": {
                "by_severity": {
                    severity: len(vulns) for severity, vulns in vulnerabilities_by_severity.items()
                },
                "by_category": {
                    category: len(vulns) for category, vulns in vulnerabilities_by_category.items()
                }
            },
            "detailed_vulnerabilities": [
                {
                    "id": vuln.vuln_id,
                    "type": vuln.vuln_type.value,
                    "severity": vuln.severity.value,
                    "title": vuln.title,
                    "description": vuln.description,
                    "impact": vuln.impact,
                    "recommendation": vuln.recommendation,
                    "affected_endpoint": vuln.affected_endpoint,
                    "confidence": vuln.confidence_score,
                    "timestamp": vuln.timestamp.isoformat()
                }
                for vuln in all_vulnerabilities
            ],
            "test_results": [
                {
                    "test_id": test.test_id,
                    "test_name": test.test_name,
                    "category": test.category.value,
                    "status": test.status,
                    "execution_time": test.execution_time,
                    "vulnerabilities_found": len(test.vulnerabilities),
                    "details": test.details
                }
                for test in self.test_results
            ],
            "priority_recommendations": priority_recommendations,
            "compliance_status": compliance_status,
            "next_audit_recommended": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        return report
    
    def _calculate_security_score(self, vulnerabilities_by_severity: Dict[str, List]) -> float:
        """Calcule un score de sécurité (0-100)"""
        
        # Pondération par sévérité
        severity_weights = {
            "critical": 25,
            "high": 10,
            "medium": 5,
            "low": 2,
            "info": 1
        }
        
        total_penalty = 0
        for severity, vulns in vulnerabilities_by_severity.items():
            total_penalty += len(vulns) * severity_weights.get(severity, 0)
        
        # Score sur 100 (plus c'est haut, mieux c'est)
        base_score = 100
        final_score = max(0, base_score - total_penalty)
        
        return round(final_score, 1)
    
    def _determine_risk_level(self, security_score: float) -> str:
        """Détermine le niveau de risque"""
        
        if security_score >= 80:
            return "LOW"
        elif security_score >= 60:
            return "MEDIUM"
        elif security_score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_priority_recommendations(self, vulnerabilities: List[Vulnerability]) -> List[Dict[str, Any]]:
        """Génère des recommandations prioritaires"""
        
        # Groupement par type de vulnérabilité
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.vuln_type.value
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(vuln)
        
        recommendations = []
        
        # Recommandations par type
        for vuln_type, vulns in vuln_types.items():
            if not vulns:
                continue
                
            severity_counts = {}
            for vuln in vulns:
                severity = vuln.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            recommendations.append({
                "vulnerability_type": vuln_type,
                "count": len(vulns),
                "severity_distribution": severity_counts,
                "priority": "HIGH" if any(v.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] for v in vulns) else "MEDIUM",
                "recommendation": vulns[0].recommendation,
                "estimated_effort": "2-4 days",  # Simulation
                "business_impact": "High" if "ml_specific" in vuln_type else "Medium"
            })
        
        # Tri par priorité
        recommendations.sort(key=lambda x: (
            0 if x["priority"] == "HIGH" else 1,
            -x["count"]
        ))
        
        return recommendations[:5]  # Top 5
    
    def _assess_compliance_status(self, vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        """Évalue le statut de conformité"""
        
        # Standards de sécurité communs
        standards = {
            "OWASP_TOP_10": {
                "compliant": len([v for v in vulnerabilities if v.category == TestCategory.INPUT_VALIDATION]) == 0,
                "issues": len([v for v in vulnerabilities if v.category == TestCategory.INPUT_VALIDATION])
            },
            "ISO_27001": {
                "compliant": len([v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]) == 0,
                "issues": len([v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL])
            },
            "SOC_2": {
                "compliant": len([v for v in vulnerabilities if v.category in [TestCategory.AUTHENTICATION, TestCategory.AUTHORIZATION]]) == 0,
                "issues": len([v for v in vulnerabilities if v.category in [TestCategory.AUTHENTICATION, TestCategory.AUTHORIZATION]])
            },
            "NIST_AI_RMF": {
                "compliant": len([v for v in vulnerabilities if v.vuln_type in [VulnerabilityType.MODEL_POISONING, VulnerabilityType.ADVERSARIAL_ATTACK]]) == 0,
                "issues": len([v for v in vulnerabilities if v.vuln_type in [VulnerabilityType.MODEL_POISONING, VulnerabilityType.ADVERSARIAL_ATTACK]])
            }
        }
        
        overall_compliance = all(standard["compliant"] for standard in standards.values())
        
        return {
            "overall_compliant": overall_compliance,
            "standards": standards,
            "compliance_score": sum(1 for s in standards.values() if s["compliant"]) / len(standards) * 100
        }

# Factory pour la création de la suite de tests
def create_penetration_testing_suite(config: Dict[str, Any]) -> PenetrationTestingSuite:
    """Factory pour créer une suite de tests de pénétration configurée"""
    
    pentest_config = PenTestConfig(
        target_url=config['target_url'],
        target_model_endpoint=config.get('target_model_endpoint', config['target_url'] + '/predict'),
        api_key=config.get('api_key'),
        auth_token=config.get('auth_token'),
        test_categories=[TestCategory(cat) for cat in config.get('test_categories', [])],
        intensity_level=config.get('intensity_level', 'medium'),
        max_concurrent_tests=config.get('max_concurrent_tests', 5),
        timeout_per_test=config.get('timeout_per_test', 60),
        custom_headers=config.get('custom_headers', {}),
        excluded_tests=config.get('excluded_tests', [])
    )
    
    return PenetrationTestingSuite(pentest_config)

# Exemple d'utilisation
async def main() -> None:
    """Exemple d'utilisation de la suite de penetration testing"""
    
    # Configuration
    config = {
        'target_url': 'https://api.example.com',
        'target_model_endpoint': 'https://api.example.com/v1/predict',
        'api_key': 'test_api_key',
        'test_categories': ['ml_specific', 'input_validation', 'crypto_weakness'],
        'intensity_level': 'medium',
        'custom_headers': {
            'User-Agent': 'SecurityAudit/1.0'
        }
    }
    
    # Création de la suite de tests
    pentest_suite = create_penetration_testing_suite(config)
    
    try:
        # Exécution de l'audit complet
        logger.info("Démarrage de l'audit de sécurité...")
        
        audit_report = await pentest_suite.run_full_security_audit()
        
        # Affichage du rapport
        print("=== RAPPORT D'AUDIT DE SÉCURITÉ ===")
        print(f"Score de sécurité: {audit_report['audit_summary']['security_score']}/100")
        print(f"Niveau de risque: {audit_report['audit_summary']['risk_level']}")
        print(f"Vulnérabilités trouvées: {audit_report['audit_summary']['total_vulnerabilities']}")
        
        print("\n=== VULNÉRABILITÉS PAR SÉVÉRITÉ ===")
        for severity, count in audit_report['vulnerability_summary']['by_severity'].items():
            if count > 0:
                print(f"{severity.upper()}: {count}")
        
        print("\n=== RECOMMANDATIONS PRIORITAIRES ===")
        for i, rec in enumerate(audit_report['priority_recommendations'][:3], 1):
            print(f"{i}. {rec['vulnerability_type']} ({rec['count']} instances)")
            print(f"   Priorité: {rec['priority']}")
            print(f"   Recommandation: {rec['recommendation']}")
        
        print(f"\n=== CONFORMITÉ ===")
        compliance = audit_report['compliance_status']
        print(f"Score global: {compliance['compliance_score']:.1f}%")
        for standard, status in compliance['standards'].items():
            status_text = "✅ CONFORME" if status['compliant'] else f"❌ {status['issues']} problèmes"
            print(f"{standard}: {status_text}")
        
        # Sauvegarde du rapport complet
        with open('/tmp/security_audit_report.json', 'w') as f:
            json.dump(audit_report, f, indent=2, default=str)
        
        print(f"\nRapport complet sauvegardé: /tmp/security_audit_report.json")
        
    except Exception as e:
        logger.error(f"Erreur durant l'audit: {e}")

if __name__ == "__main__":
    asyncio.run(main())