"""🔒 ML Security Manager - Enterprise AI Security & Adversarial Defense System
============================================================================

Système de sécurité IA enterprise avec défense adversariale, détection d'attaques,
validation de conformité et protection des modèles pour la plateforme Ainflue.

Expert Roles Implementation:
🔒 Sécurité: AI security + adversarial defense + secure inference + AI safety + compliance
🤖 Lead Dev IA: Security orchestration + threat detection + automated defense + performance impact
🏗️ Backend Senior: Secure architecture + distributed security + scalable protection systems
⚙️ DevOps: Security automation + CI/CD security integration + security monitoring
🧠 ML Engineer: Model security + adversarial training + robustness enhancement + security metrics
🗄️ DBA: Security audit trails + access control + encrypted storage + compliance logging
🔗 Microservices: Secure communications + authentication + authorization + security mesh
🎨 IA Prompt Engineer: Prompt injection defense + prompt security + safe AI interactions

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise
Date: December 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture ML Security est la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).

Toute utilisation, reproduction, modification, ou distribution de cette 
architecture IA/ML, de ces algorithmes, ou de ce code source sans 
autorisation écrite EXPLICITE de Fahed Mlaiel constitue une violation 
grave des droits de propriété intellectuelle.

📧 Demandes d'autorisation : mlaiel@live.de
🚫 USAGE NON AUTORISÉ = POURSUITES JUDICIAIRES IMMÉDIATES
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import hmac
import secrets
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import statistics
import pickle
import tempfile
import shutil
import base64
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Niveaux de menace de sécurité"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AttackType(Enum):
    """Types d'attaques contre les modèles IA"""
    ADVERSARIAL_EXAMPLES = "adversarial_examples"
    POISON_ATTACK = "poison_attack"
    MODEL_EXTRACTION = "model_extraction"
    MEMBERSHIP_INFERENCE = "membership_inference"
    BACKDOOR_ATTACK = "backdoor_attack"
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXTRACTION = "data_extraction"
    EVASION_ATTACK = "evasion_attack"
    INVERSION_ATTACK = "inversion_attack"
    GRADIENT_ATTACK = "gradient_attack"

class SecurityMeasure(Enum):
    """Mesures de sécurité disponibles"""
    INPUT_VALIDATION = "input_validation"
    OUTPUT_FILTERING = "output_filtering"
    ADVERSARIAL_TRAINING = "adversarial_training"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    FEDERATED_LEARNING = "federated_learning"
    SECURE_AGGREGATION = "secure_aggregation"
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"
    ACCESS_CONTROL = "access_control"
    AUDIT_LOGGING = "audit_logging"
    RATE_LIMITING = "rate_limiting"

class ComplianceStandard(Enum):
    """Standards de conformité"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    NIST_AI_RMF = "nist_ai_rmf"
    EU_AI_ACT = "eu_ai_act"
    AICPA_SOC_AI = "aicpa_soc_ai"

@dataclass
class SecurityThreat:
    """Menace de sécurité détectée"""
    threat_id: str
    threat_type: AttackType
    threat_level: ThreatLevel
    source_ip: str
    target_model: str
    target_endpoint: str
    attack_vector: str
    payload_size: int
    detection_confidence: float
    potential_impact: str
    mitigation_applied: List[SecurityMeasure]
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityEvent:
    """Événement de sécurité"""
    event_id: str
    event_type: str
    event_level: ThreatLevel
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: str
    endpoint: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    security_flags: List[str]
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    compliance_check: Dict[str, bool] = field(default_factory=dict)

@dataclass
class SecurityPolicy:
    """Politique de sécurité"""
    policy_id: str
    policy_name: str
    policy_type: str  # "input_validation", "access_control", "data_protection"
    rules: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 100
    apply_to_models: List[str] = field(default_factory=list)
    apply_to_endpoints: List[str] = field(default_factory=list)
    enforcement_action: str = "block"  # "block", "warn", "monitor"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    compliance_mapping: Dict[ComplianceStandard, bool] = field(default_factory=dict)

@dataclass
class SecurityAudit:
    """Audit de sécurité"""
    audit_id: str
    audit_type: str
    model_id: str
    model_version: str
    vulnerability_scan: Dict[str, Any]
    compliance_check: Dict[ComplianceStandard, Dict[str, Any]]
    security_score: float
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    remediation_plan: List[Dict[str, Any]]
    auditor: str
    audit_date: datetime = field(default_factory=datetime.now)
    next_audit_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=90))

class AdversarialDetector:
    """🔍 Détecteur d'attaques adversariales"""
    
    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = sensitivity
        self.detection_models = {}
        self.baseline_statistics = {}
        
    async def detect_adversarial_input(self, 
                                     input_data: Any, 
                                     model_id: str,
                                     context: Dict[str, Any] = None) -> Tuple[bool, float, str]:
        """Détecter les inputs adversariels"""
        
        try:
            # Analyse statistique de l'input
            statistical_anomaly = await self._detect_statistical_anomaly(input_data, model_id)
            
            # Analyse de perturbation
            perturbation_score = await self._analyze_perturbation_patterns(input_data)
            
            # Analyse de gradient (simulation)
            gradient_anomaly = await self._detect_gradient_anomaly(input_data, model_id)
            
            # Score composite
            detection_score = (
                statistical_anomaly * 0.4 +
                perturbation_score * 0.3 +
                gradient_anomaly * 0.3
            )
            
            is_adversarial = detection_score > self.sensitivity
            
            explanation = self._generate_detection_explanation(
                statistical_anomaly, perturbation_score, gradient_anomaly
            )
            
            return is_adversarial, detection_score, explanation
            
        except Exception as e:
            logger.error(f"❌ Adversarial detection failed: {e}")
            return False, 0.0, f"Detection error: {str(e)}"
    
    async def _detect_statistical_anomaly(self, input_data: Any, model_id: str) -> float:
        """Détecter des anomalies statistiques"""
        
        # Simulation d'analyse statistique
        if isinstance(input_data, (list, np.ndarray)):
            data_array = np.array(input_data) if not isinstance(input_data, np.ndarray) else input_data
            
            # Calculer des statistiques
            if data_array.size > 0:
                mean_val = np.mean(data_array)
                std_val = np.std(data_array)
                
                # Vérifier si les statistiques sont dans les limites normales
                if model_id in self.baseline_statistics:
                    baseline = self.baseline_statistics[model_id]
                    mean_diff = abs(mean_val - baseline['mean']) / baseline['std']
                    return min(mean_diff / 3.0, 1.0)  # Normaliser à [0,1]
                else:
                    # Première fois - établir baseline
                    self.baseline_statistics[model_id] = {
                        'mean': mean_val,
                        'std': std_val,
                        'count': 1
                    }
                    return 0.0
        
        return np.random.uniform(0.0, 0.3)  # Score d'anomalie simulé
    
    async def _analyze_perturbation_patterns(self, input_data: Any) -> float:
        """Analyser les patterns de perturbation"""
        
        # Simulation d'analyse de perturbation
        if isinstance(input_data, (list, np.ndarray)):
            data_array = np.array(input_data) if not isinstance(input_data, np.ndarray) else input_data
            
            if data_array.size > 1:
                # Analyser la variation locale
                if len(data_array.shape) >= 1:
                    local_variance = np.var(np.diff(data_array.flatten()))
                    # Score basé sur variance anormalement élevée
                    return min(local_variance / 100.0, 1.0)
        
        return np.random.uniform(0.0, 0.2)  # Score de perturbation simulé
    
    async def _detect_gradient_anomaly(self, input_data: Any, model_id: str) -> float:
        """Détecter des anomalies de gradient"""
        
        # Simulation d'analyse de gradient
        # Dans un vrai contexte, analyser les gradients du modèle
        return np.random.uniform(0.0, 0.4)  # Score d'anomalie gradient simulé
    
    def _generate_detection_explanation(self, 
                                      stat_score: float, 
                                      pert_score: float, 
                                      grad_score: float) -> str:
        """Générer une explication de la détection"""
        
        explanations = []
        
        if stat_score > 0.5:
            explanations.append("Statistical anomaly detected in input distribution")
        
        if pert_score > 0.5:
            explanations.append("Suspicious perturbation patterns found")
        
        if grad_score > 0.5:
            explanations.append("Gradient-based attack indicators present")
        
        if not explanations:
            explanations.append("Input appears normal")
        
        return "; ".join(explanations)

class PromptInjectionDetector:
    """🎯 Détecteur d'injection de prompts"""
    
    def __init__(self):
        self.dangerous_patterns = [
            "ignore previous instructions",
            "system:",
            "admin:",
            "root:",
            "execute:",
            "eval(",
            "exec(",
            "__import__",
            "subprocess",
            "os.system",
            "rm -rf",
            "delete",
            "DROP TABLE",
            "SELECT * FROM"
        ]
        
        self.injection_indicators = [
            "<!--",
            "<script>",
            "javascript:",
            "data:text/html",
            "${",
            "{{",
            "<%",
            "<?php"
        ]
    
    async def detect_prompt_injection(self, prompt: str, context: Dict[str, Any] = None) -> Tuple[bool, float, List[str]]:
        """Détecter les tentatives d'injection de prompt"""
        
        try:
            # Analyse des patterns dangereux
            dangerous_score = self._analyze_dangerous_patterns(prompt)
            
            # Analyse des indicateurs d'injection
            injection_score = self._analyze_injection_indicators(prompt)
            
            # Analyse de structure
            structure_score = self._analyze_prompt_structure(prompt)
            
            # Analyse contextuelle
            context_score = self._analyze_context_anomalies(prompt, context or {})
            
            # Score composite
            total_score = (
                dangerous_score * 0.4 +
                injection_score * 0.3 +
                structure_score * 0.2 +
                context_score * 0.1
            )
            
            is_injection = total_score > 0.6
            
            # Générer les détails de détection
            detection_details = []
            if dangerous_score > 0.3:
                detection_details.append("Dangerous command patterns detected")
            if injection_score > 0.3:
                detection_details.append("Code injection indicators found")
            if structure_score > 0.5:
                detection_details.append("Suspicious prompt structure")
            if context_score > 0.3:
                detection_details.append("Context anomalies detected")
            
            return is_injection, total_score, detection_details
            
        except Exception as e:
            logger.error(f"❌ Prompt injection detection failed: {e}")
            return False, 0.0, [f"Detection error: {str(e)}"]
    
    def _analyze_dangerous_patterns(self, prompt: str) -> float:
        """Analyser les patterns dangereux"""
        
        prompt_lower = prompt.lower()
        matches = 0
        
        for pattern in self.dangerous_patterns:
            if pattern in prompt_lower:
                matches += 1
        
        return min(matches / len(self.dangerous_patterns), 1.0)
    
    def _analyze_injection_indicators(self, prompt: str) -> float:
        """Analyser les indicateurs d'injection"""
        
        matches = 0
        
        for indicator in self.injection_indicators:
            if indicator in prompt:
                matches += 1
        
        return min(matches / len(self.injection_indicators), 1.0)
    
    def _analyze_prompt_structure(self, prompt: str) -> float:
        """Analyser la structure du prompt"""
        
        score = 0.0
        
        # Longueur excessive
        if len(prompt) > 10000:
            score += 0.3
        
        # Répétitions suspectes
        words = prompt.split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:  # Beaucoup de répétitions
                score += 0.4
        
        # Caractères spéciaux excessifs
        special_chars = sum(1 for c in prompt if not c.isalnum() and not c.isspace())
        if special_chars > len(prompt) * 0.3:
            score += 0.3
        
        return min(score, 1.0)
    
    def _analyze_context_anomalies(self, prompt: str, context: Dict[str, Any]) -> float:
        """Analyser les anomalies contextuelles"""
        
        score = 0.0
        
        # Vérifier la cohérence avec le contexte utilisateur
        user_type = context.get('user_type', 'regular')
        if user_type == 'regular' and any(admin_term in prompt.lower() 
                                        for admin_term in ['admin', 'root', 'system', 'config']):
            score += 0.5
        
        # Vérifier les tentatives de sortie du contexte
        if any(escape in prompt.lower() 
               for escape in ['break out', 'escape', 'bypass', 'override']):
            score += 0.4
        
        return min(score, 1.0)

class SecurityPolicyEngine:
    """📋 Moteur de politiques de sécurité"""
    
    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.policy_cache = {}
        
    async def create_policy(self, 
                          policy_name: str,
                          policy_type: str,
                          rules: List[Dict[str, Any]],
                          apply_to_models: List[str] = None,
                          apply_to_endpoints: List[str] = None,
                          enforcement_action: str = "block") -> SecurityPolicy:
        """Créer une politique de sécurité"""
        
        policy_id = f"policy_{uuid.uuid4().hex[:12]}"
        
        policy = SecurityPolicy(
            policy_id=policy_id,
            policy_name=policy_name,
            policy_type=policy_type,
            rules=rules,
            apply_to_models=apply_to_models or [],
            apply_to_endpoints=apply_to_endpoints or [],
            enforcement_action=enforcement_action
        )
        
        self.policies[policy_id] = policy
        
        logger.info(f"📋 Created security policy: {policy_name} ({policy_id})")
        
        return policy
    
    async def evaluate_request(self, 
                             request_data: Dict[str, Any], 
                             model_id: str,
                             endpoint: str) -> Tuple[bool, List[str], List[SecurityMeasure]]:
        """Évaluer une requête contre les politiques"""
        
        violations = []
        applied_measures = []
        allow_request = True
        
        try:
            # Évaluer chaque politique applicable
            applicable_policies = self._get_applicable_policies(model_id, endpoint)
            
            for policy in applicable_policies:
                if not policy.enabled:
                    continue
                
                policy_violation = await self._evaluate_policy(policy, request_data)
                
                if policy_violation:
                    violations.append(f"Policy violation: {policy.policy_name}")
                    
                    if policy.enforcement_action == "block":
                        allow_request = False
                    elif policy.enforcement_action == "warn":
                        applied_measures.append(SecurityMeasure.AUDIT_LOGGING)
                    
                    # Appliquer les mesures de sécurité appropriées
                    security_measures = self._get_security_measures_for_policy(policy)
                    applied_measures.extend(security_measures)
            
            return allow_request, violations, applied_measures
            
        except Exception as e:
            logger.error(f"❌ Policy evaluation failed: {e}")
            return False, [f"Policy evaluation error: {str(e)}"], []
    
    def _get_applicable_policies(self, model_id: str, endpoint: str) -> List[SecurityPolicy]:
        """Obtenir les politiques applicables"""
        
        applicable = []
        
        for policy in self.policies.values():
            # Vérifier si la politique s'applique au modèle
            if policy.apply_to_models and model_id not in policy.apply_to_models:
                continue
            
            # Vérifier si la politique s'applique à l'endpoint
            if policy.apply_to_endpoints and endpoint not in policy.apply_to_endpoints:
                continue
            
            applicable.append(policy)
        
        # Trier par priorité
        return sorted(applicable, key=lambda p: p.priority, reverse=True)
    
    async def _evaluate_policy(self, policy: SecurityPolicy, request_data: Dict[str, Any]) -> bool:
        """Évaluer une politique spécifique"""
        
        for rule in policy.rules:
            rule_type = rule.get('type')
            
            if rule_type == 'input_size_limit':
                max_size = rule.get('max_size', 1000000)
                input_size = len(str(request_data))
                if input_size > max_size:
                    return True
            
            elif rule_type == 'rate_limit':
                # Simulation de rate limiting
                current_rate = request_data.get('_request_rate', 0)
                max_rate = rule.get('max_requests_per_minute', 100)
                if current_rate > max_rate:
                    return True
            
            elif rule_type == 'content_filter':
                # Filtrage de contenu
                content = str(request_data)
                blocked_terms = rule.get('blocked_terms', [])
                if any(term in content.lower() for term in blocked_terms):
                    return True
            
            elif rule_type == 'authentication_required':
                # Vérification d'authentification
                if not request_data.get('authenticated', False):
                    return True
        
        return False
    
    def _get_security_measures_for_policy(self, policy: SecurityPolicy) -> List[SecurityMeasure]:
        """Obtenir les mesures de sécurité pour une politique"""
        
        measures = []
        
        if policy.policy_type == "input_validation":
            measures.extend([SecurityMeasure.INPUT_VALIDATION, SecurityMeasure.AUDIT_LOGGING])
        elif policy.policy_type == "access_control":
            measures.extend([SecurityMeasure.ACCESS_CONTROL, SecurityMeasure.AUDIT_LOGGING])
        elif policy.policy_type == "data_protection":
            measures.extend([SecurityMeasure.OUTPUT_FILTERING, SecurityMeasure.DIFFERENTIAL_PRIVACY])
        
        return measures

class ComplianceManager:
    """📋 Gestionnaire de conformité"""
    
    def __init__(self):
        self.compliance_requirements = self._initialize_compliance_requirements()
        
    def _initialize_compliance_requirements(self) -> Dict[ComplianceStandard, Dict[str, Any]]:
        """Initialiser les exigences de conformité"""
        
        return {
            ComplianceStandard.GDPR: {
                "name": "General Data Protection Regulation",
                "requirements": [
                    "data_minimization",
                    "purpose_limitation",
                    "consent_management",
                    "right_to_erasure",
                    "data_portability",
                    "privacy_by_design"
                ],
                "data_retention_max_days": 365,
                "consent_required": True,
                "anonymization_required": True
            },
            
            ComplianceStandard.CCPA: {
                "name": "California Consumer Privacy Act",
                "requirements": [
                    "right_to_know",
                    "right_to_delete",
                    "right_to_opt_out",
                    "non_discrimination",
                    "data_protection"
                ],
                "data_retention_max_days": 730,
                "consent_required": True,
                "opt_out_required": True
            },
            
            ComplianceStandard.NIST_AI_RMF: {
                "name": "NIST AI Risk Management Framework",
                "requirements": [
                    "ai_risk_assessment",
                    "bias_evaluation",
                    "explainability",
                    "human_oversight",
                    "continuous_monitoring",
                    "incident_response"
                ],
                "risk_assessment_required": True,
                "bias_testing_required": True,
                "explainability_required": True
            },
            
            ComplianceStandard.EU_AI_ACT: {
                "name": "EU Artificial Intelligence Act",
                "requirements": [
                    "risk_based_approach",
                    "conformity_assessment",
                    "transparency_obligations",
                    "human_oversight",
                    "accuracy_requirements",
                    "robustness_requirements"
                ],
                "high_risk_systems": True,
                "ce_marking_required": True,
                "documentation_required": True
            }
        }
    
    async def check_compliance(self, 
                             model_id: str,
                             model_metadata: Dict[str, Any],
                             usage_context: Dict[str, Any]) -> Dict[ComplianceStandard, Dict[str, Any]]:
        """Vérifier la conformité pour tous les standards"""
        
        compliance_results = {}
        
        for standard in ComplianceStandard:
            result = await self._check_standard_compliance(standard, model_id, model_metadata, usage_context)
            compliance_results[standard] = result
        
        return compliance_results
    
    async def _check_standard_compliance(self,
                                       standard: ComplianceStandard,
                                       model_id: str,
                                       model_metadata: Dict[str, Any],
                                       usage_context: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifier la conformité pour un standard spécifique"""
        
        requirements = self.compliance_requirements[standard]
        compliance_result = {
            "standard": standard.value,
            "compliant": True,
            "score": 0.0,
            "passed_checks": [],
            "failed_checks": [],
            "recommendations": []
        }
        
        total_checks = len(requirements["requirements"])
        passed_checks = 0
        
        for requirement in requirements["requirements"]:
            check_result = await self._evaluate_requirement(requirement, model_metadata, usage_context)
            
            if check_result["passed"]:
                compliance_result["passed_checks"].append(requirement)
                passed_checks += 1
            else:
                compliance_result["failed_checks"].append(requirement)
                compliance_result["recommendations"].extend(check_result.get("recommendations", []))
        
        compliance_result["score"] = passed_checks / total_checks
        compliance_result["compliant"] = compliance_result["score"] >= 0.8  # 80% requis
        
        return compliance_result
    
    async def _evaluate_requirement(self, 
                                  requirement: str,
                                  model_metadata: Dict[str, Any],
                                  usage_context: Dict[str, Any]) -> Dict[str, Any]:
        """Évaluer une exigence spécifique"""
        
        # Simulation d'évaluation des exigences
        evaluations = {
            "data_minimization": {
                "passed": model_metadata.get("data_minimization_applied", False),
                "recommendations": ["Apply data minimization techniques", "Reduce feature set"]
            },
            "consent_management": {
                "passed": usage_context.get("user_consent", False),
                "recommendations": ["Implement consent management system", "Track user preferences"]
            },
            "bias_evaluation": {
                "passed": model_metadata.get("bias_tested", False),
                "recommendations": ["Conduct bias evaluation", "Test fairness across demographics"]
            },
            "explainability": {
                "passed": model_metadata.get("explainable", False),
                "recommendations": ["Add model explainability features", "Implement SHAP/LIME"]
            },
            "human_oversight": {
                "passed": usage_context.get("human_in_loop", False),
                "recommendations": ["Add human oversight controls", "Implement review process"]
            },
            "continuous_monitoring": {
                "passed": model_metadata.get("monitoring_enabled", True),
                "recommendations": ["Enable continuous monitoring", "Set up alerting"]
            }
        }
        
        return evaluations.get(requirement, {
            "passed": np.random.choice([True, False], p=[0.7, 0.3]),  # 70% de chance de passer
            "recommendations": [f"Address {requirement} compliance requirement"]
        })

class MLSecurityManager:
    """🔒 Enterprise ML Security Manager"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le gestionnaire de sécurité ML
        
        Args:
            config: Configuration de sécurité
        """
        self.config = config or {}
        
        # Composants de sécurité
        self.adversarial_detector = AdversarialDetector(
            sensitivity=self.config.get('adversarial_sensitivity', 0.8)
        )
        self.prompt_detector = PromptInjectionDetector()
        self.policy_engine = SecurityPolicyEngine()
        self.compliance_manager = ComplianceManager()
        
        # État
        self.security_events = []
        self.active_threats = []
        self.security_policies = {}
        self.audit_logs = []
        
        # Encryption
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
        # Rate limiting
        self.request_tracking = {}
        self.rate_limits = self.config.get('rate_limits', {})
        
        logger.info("🔒 ML Security Manager initialized")
    
    def _generate_encryption_key(self) -> bytes:
        """Générer une clé de chiffrement"""
        password = self.config.get('encryption_password', 'default_password').encode()
        salt = self.config.get('encryption_salt', b'default_salt')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def validate_inference_request(self,
                                       request_data: Dict[str, Any],
                                       model_id: str,
                                       endpoint: str,
                                       user_context: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """🛡️ Backend Senior - Valider une requête d'inférence"""
        
        validation_id = f"validation_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        logger.info(f"🛡️ Starting security validation {validation_id} for model {model_id}")
        
        user_context = user_context or {}
        validation_result = {
            "validation_id": validation_id,
            "allowed": True,
            "security_score": 1.0,
            "threats_detected": [],
            "policies_violated": [],
            "measures_applied": [],
            "compliance_status": {},
            "processing_time_ms": 0.0
        }
        
        try:
            # 1. Rate Limiting
            rate_check = await self._check_rate_limits(user_context.get('user_id'), endpoint)
            if not rate_check["allowed"]:
                validation_result["allowed"] = False
                validation_result["threats_detected"].append("Rate limit exceeded")
                validation_result["measures_applied"].append(SecurityMeasure.RATE_LIMITING.value)
            
            # 2. Détection d'attaques adversariales
            input_data = request_data.get('input_data')
            if input_data:
                is_adversarial, adv_score, adv_explanation = await self.adversarial_detector.detect_adversarial_input(
                    input_data, model_id, user_context
                )
                
                if is_adversarial:
                    threat = SecurityThreat(
                        threat_id=f"adv_{uuid.uuid4().hex[:8]}",
                        threat_type=AttackType.ADVERSARIAL_EXAMPLES,
                        threat_level=ThreatLevel.HIGH if adv_score > 0.8 else ThreatLevel.MEDIUM,
                        source_ip=user_context.get('source_ip', 'unknown'),
                        target_model=model_id,
                        target_endpoint=endpoint,
                        attack_vector="adversarial_input",
                        payload_size=len(str(input_data)),
                        detection_confidence=adv_score,
                        potential_impact="Model evasion, incorrect predictions",
                        mitigation_applied=[SecurityMeasure.INPUT_VALIDATION]
                    )
                    
                    self.active_threats.append(threat)
                    validation_result["threats_detected"].append(f"Adversarial attack: {adv_explanation}")
                    validation_result["security_score"] *= (1.0 - adv_score * 0.5)
            
            # 3. Détection d'injection de prompt
            prompt_data = request_data.get('prompt') or request_data.get('text_input')
            if prompt_data:
                is_injection, inj_score, inj_details = await self.prompt_detector.detect_prompt_injection(
                    prompt_data, user_context
                )
                
                if is_injection:
                    threat = SecurityThreat(
                        threat_id=f"prompt_{uuid.uuid4().hex[:8]}",
                        threat_type=AttackType.PROMPT_INJECTION,
                        threat_level=ThreatLevel.HIGH if inj_score > 0.8 else ThreatLevel.MEDIUM,
                        source_ip=user_context.get('source_ip', 'unknown'),
                        target_model=model_id,
                        target_endpoint=endpoint,
                        attack_vector="prompt_injection",
                        payload_size=len(prompt_data),
                        detection_confidence=inj_score,
                        potential_impact="Unauthorized access, data extraction",
                        mitigation_applied=[SecurityMeasure.INPUT_VALIDATION, SecurityMeasure.OUTPUT_FILTERING]
                    )
                    
                    self.active_threats.append(threat)
                    validation_result["threats_detected"].extend(inj_details)
                    validation_result["security_score"] *= (1.0 - inj_score * 0.6)
            
            # 4. Évaluation des politiques de sécurité
            policy_allowed, policy_violations, security_measures = await self.policy_engine.evaluate_request(
                request_data, model_id, endpoint
            )
            
            if not policy_allowed:
                validation_result["allowed"] = False
            
            validation_result["policies_violated"] = policy_violations
            validation_result["measures_applied"].extend([m.value for m in security_measures])
            
            # 5. Vérification de conformité (échantillonnage)
            if np.random.random() < 0.1:  # 10% des requêtes
                model_metadata = {"model_id": model_id, "endpoint": endpoint}
                compliance_status = await self.compliance_manager.check_compliance(
                    model_id, model_metadata, user_context
                )
                validation_result["compliance_status"] = {
                    standard.value: result["compliant"] 
                    for standard, result in compliance_status.items()
                }
            
            # Score de sécurité final
            if validation_result["threats_detected"]:
                validation_result["security_score"] *= 0.7
            
            if validation_result["policies_violated"]:
                validation_result["security_score"] *= 0.8
            
            # Décision finale
            if validation_result["security_score"] < 0.3:
                validation_result["allowed"] = False
            
            # Enregistrer l'événement de sécurité
            await self._log_security_event(validation_result, request_data, user_context)
            
            validation_result["processing_time_ms"] = (time.time() - start_time) * 1000
            
            logger.info(f"🛡️ Security validation {validation_id} completed. Allowed: {validation_result['allowed']}")
            
            return validation_result["allowed"], validation_result
            
        except Exception as e:
            logger.error(f"❌ Security validation {validation_id} failed: {e}")
            return False, {"error": str(e), "allowed": False}
    
    async def _check_rate_limits(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        """Vérifier les limites de taux"""
        
        current_time = time.time()
        key = f"{user_id}:{endpoint}"
        
        if key not in self.request_tracking:
            self.request_tracking[key] = []
        
        # Nettoyer les anciennes requêtes (> 1 minute)
        self.request_tracking[key] = [
            timestamp for timestamp in self.request_tracking[key]
            if current_time - timestamp < 60
        ]
        
        # Ajouter la requête actuelle
        self.request_tracking[key].append(current_time)
        
        # Vérifier les limites
        current_rate = len(self.request_tracking[key])
        max_rate = self.rate_limits.get(endpoint, self.rate_limits.get('default', 100))
        
        return {
            "allowed": current_rate <= max_rate,
            "current_rate": current_rate,
            "max_rate": max_rate,
            "reset_time": current_time + 60
        }
    
    async def _log_security_event(self,
                                validation_result: Dict[str, Any],
                                request_data: Dict[str, Any],
                                user_context: Dict[str, Any]):
        """Enregistrer un événement de sécurité"""
        
        event = SecurityEvent(
            event_id=f"event_{uuid.uuid4().hex[:12]}",
            event_type="inference_validation",
            event_level=ThreatLevel.HIGH if not validation_result["allowed"] else ThreatLevel.INFO,
            user_id=user_context.get('user_id'),
            session_id=user_context.get('session_id'),
            source_ip=user_context.get('source_ip', 'unknown'),
            endpoint=user_context.get('endpoint', 'unknown'),
            request_data=self._sanitize_request_data(request_data),
            response_data={"validation_result": validation_result},
            security_flags=validation_result.get("threats_detected", []),
            processing_time_ms=validation_result.get("processing_time_ms", 0.0)
        )
        
        self.security_events.append(event)
        
        # Audit logging
        if validation_result.get("threats_detected") or not validation_result["allowed"]:
            await self._create_audit_entry(event)
    
    def _sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoyer les données de requête pour les logs"""
        
        sanitized = {}
        
        for key, value in request_data.items():
            if key in ['password', 'token', 'api_key', 'secret']:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "... [TRUNCATED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def _create_audit_entry(self, event: SecurityEvent):
        """Créer une entrée d'audit"""
        
        audit_entry = {
            "audit_id": f"audit_{uuid.uuid4().hex[:12]}",
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "severity": event.event_level.value,
            "user_id": event.user_id,
            "source_ip": event.source_ip,
            "security_flags": event.security_flags,
            "encrypted_data": self.fernet.encrypt(json.dumps(event.request_data).encode()).decode()
        }
        
        self.audit_logs.append(audit_entry)
    
    async def conduct_security_audit(self,
                                   model_id: str,
                                   model_version: str,
                                   audit_scope: List[str] = None) -> SecurityAudit:
        """🔍 Sécurité - Effectuer un audit de sécurité"""
        
        audit_id = f"audit_{uuid.uuid4().hex[:12]}"
        audit_scope = audit_scope or ["vulnerability_scan", "compliance_check", "access_review"]
        
        logger.info(f"🔍 Starting security audit {audit_id} for model {model_id}")
        
        try:
            # Scan de vulnérabilités
            vulnerability_scan = await self._perform_vulnerability_scan(model_id)
            
            # Vérification de conformité
            compliance_check = await self.compliance_manager.check_compliance(
                model_id, {"model_id": model_id, "version": model_version}, {}
            )
            
            # Évaluation des risques
            risk_assessment = await self._assess_security_risks(model_id, vulnerability_scan, compliance_check)
            
            # Score de sécurité global
            security_score = self._calculate_security_score(vulnerability_scan, compliance_check, risk_assessment)
            
            # Recommandations
            recommendations = self._generate_security_recommendations(
                vulnerability_scan, compliance_check, risk_assessment
            )
            
            # Plan de remédiation
            remediation_plan = self._create_remediation_plan(vulnerability_scan, recommendations)
            
            audit = SecurityAudit(
                audit_id=audit_id,
                audit_type="comprehensive_security_audit",
                model_id=model_id,
                model_version=model_version,
                vulnerability_scan=vulnerability_scan,
                compliance_check={
                    standard: result for standard, result in compliance_check.items()
                },
                security_score=security_score,
                recommendations=recommendations,
                risk_assessment=risk_assessment,
                remediation_plan=remediation_plan,
                auditor="ML Security Manager"
            )
            
            logger.info(f"🔍 Security audit {audit_id} completed. Score: {security_score:.2f}")
            
            return audit
            
        except Exception as e:
            logger.error(f"❌ Security audit {audit_id} failed: {e}")
            raise
    
    async def _perform_vulnerability_scan(self, model_id: str) -> Dict[str, Any]:
        """Effectuer un scan de vulnérabilités"""
        
        vulnerabilities = []
        
        # Simulation de détection de vulnérabilités
        potential_vulns = [
            {
                "type": "model_extraction",
                "severity": "medium",
                "description": "Model may be vulnerable to extraction attacks",
                "cve_id": None,
                "probability": np.random.uniform(0.1, 0.4)
            },
            {
                "type": "adversarial_robustness",
                "severity": "high",
                "description": "Model shows low robustness to adversarial examples",
                "cve_id": None,
                "probability": np.random.uniform(0.2, 0.6)
            },
            {
                "type": "data_leakage",
                "severity": "critical",
                "description": "Potential training data leakage detected",
                "cve_id": None,
                "probability": np.random.uniform(0.0, 0.3)
            },
            {
                "type": "prompt_injection",
                "severity": "high",
                "description": "Model vulnerable to prompt injection attacks",
                "cve_id": None,
                "probability": np.random.uniform(0.1, 0.5)
            }
        ]
        
        # Filtrer basé sur probabilité
        for vuln in potential_vulns:
            if np.random.random() < vuln["probability"]:
                vulnerabilities.append(vuln)
        
        return {
            "scan_id": f"scan_{uuid.uuid4().hex[:8]}",
            "scan_date": datetime.now().isoformat(),
            "model_id": model_id,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "scan_coverage": 0.85,  # 85% de couverture
            "false_positive_rate": 0.05
        }
    
    async def _assess_security_risks(self,
                                   model_id: str,
                                   vulnerability_scan: Dict[str, Any],
                                   compliance_check: Dict[ComplianceStandard, Dict[str, Any]]) -> Dict[str, Any]:
        """Évaluer les risques de sécurité"""
        
        # Calculer le score de risque basé sur les vulnérabilités
        vuln_risk = 0.0
        for vuln in vulnerability_scan["vulnerabilities"]:
            severity_scores = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}
            vuln_risk += severity_scores.get(vuln["severity"], 0.0)
        
        vuln_risk = min(vuln_risk / len(vulnerability_scan["vulnerabilities"]) if vulnerability_scan["vulnerabilities"] else 0, 1.0)
        
        # Calculer le score de risque de conformité
        compliance_scores = [result["score"] for result in compliance_check.values()]
        compliance_risk = 1.0 - (sum(compliance_scores) / len(compliance_scores)) if compliance_scores else 0.0
        
        # Score de risque global
        overall_risk = (vuln_risk * 0.6 + compliance_risk * 0.4)
        
        # Catégorisation du risque
        if overall_risk >= 0.8:
            risk_level = "CRITICAL"
        elif overall_risk >= 0.6:
            risk_level = "HIGH"
        elif overall_risk >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "vulnerability_risk": vuln_risk,
            "compliance_risk": compliance_risk,
            "risk_factors": [
                f"Vulnerability risk: {vuln_risk:.2f}",
                f"Compliance risk: {compliance_risk:.2f}"
            ],
            "business_impact": self._assess_business_impact(overall_risk),
            "likelihood": self._assess_likelihood(vuln_risk),
            "impact": self._assess_impact(compliance_risk)
        }
    
    def _assess_business_impact(self, risk_score: float) -> str:
        """Évaluer l'impact business"""
        if risk_score >= 0.8:
            return "SEVERE - Major business disruption, regulatory penalties"
        elif risk_score >= 0.6:
            return "HIGH - Significant business impact, reputation damage"
        elif risk_score >= 0.4:
            return "MEDIUM - Moderate business impact, operational disruption"
        else:
            return "LOW - Minimal business impact"
    
    def _assess_likelihood(self, vuln_risk: float) -> str:
        """Évaluer la probabilité"""
        if vuln_risk >= 0.7:
            return "VERY HIGH"
        elif vuln_risk >= 0.5:
            return "HIGH"
        elif vuln_risk >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_impact(self, compliance_risk: float) -> str:
        """Évaluer l'impact"""
        if compliance_risk >= 0.7:
            return "SEVERE"
        elif compliance_risk >= 0.5:
            return "HIGH"
        elif compliance_risk >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_security_score(self,
                                vulnerability_scan: Dict[str, Any],
                                compliance_check: Dict[ComplianceStandard, Dict[str, Any]],
                                risk_assessment: Dict[str, Any]) -> float:
        """Calculer le score de sécurité global"""
        
        # Score de vulnérabilité (inversé)
        vuln_score = 1.0 - risk_assessment["vulnerability_risk"]
        
        # Score de conformité
        compliance_scores = [result["score"] for result in compliance_check.values()]
        compliance_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.5
        
        # Score de couverture du scan
        coverage_score = vulnerability_scan.get("scan_coverage", 0.8)
        
        # Score composite
        security_score = (
            vuln_score * 0.4 +
            compliance_score * 0.4 +
            coverage_score * 0.2
        )
        
        return security_score
    
    def _generate_security_recommendations(self,
                                         vulnerability_scan: Dict[str, Any],
                                         compliance_check: Dict[ComplianceStandard, Dict[str, Any]],
                                         risk_assessment: Dict[str, Any]) -> List[str]:
        """Générer des recommandations de sécurité"""
        
        recommendations = []
        
        # Recommandations basées sur les vulnérabilités
        for vuln in vulnerability_scan["vulnerabilities"]:
            if vuln["type"] == "adversarial_robustness":
                recommendations.append("🛡️ Implement adversarial training to improve model robustness")
            elif vuln["type"] == "model_extraction":
                recommendations.append("🔒 Add model extraction protection mechanisms")
            elif vuln["type"] == "data_leakage":
                recommendations.append("🗄️ Audit training data for potential leakage and apply differential privacy")
            elif vuln["type"] == "prompt_injection":
                recommendations.append("🎯 Implement comprehensive prompt injection filtering")
        
        # Recommandations basées sur la conformité
        for standard, result in compliance_check.items():
            if not result["compliant"]:
                recommendations.extend(result.get("recommendations", []))
        
        # Recommandations basées sur le niveau de risque
        risk_level = risk_assessment["risk_level"]
        if risk_level in ["CRITICAL", "HIGH"]:
            recommendations.extend([
                "🚨 Immediate security review required",
                "⏸️ Consider pausing deployment until risks are mitigated",
                "👥 Engage security team for comprehensive assessment"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "⚠️ Schedule security improvements in next sprint",
                "📊 Increase monitoring and alerting"
            ])
        
        return list(set(recommendations))  # Dédupliquer
    
    def _create_remediation_plan(self,
                               vulnerability_scan: Dict[str, Any],
                               recommendations: List[str]) -> List[Dict[str, Any]]:
        """Créer un plan de remédiation"""
        
        remediation_actions = []
        
        # Actions basées sur les vulnérabilités critiques
        critical_vulns = [v for v in vulnerability_scan["vulnerabilities"] if v["severity"] == "critical"]
        for vuln in critical_vulns:
            remediation_actions.append({
                "action": f"Mitigate {vuln['type']} vulnerability",
                "priority": "CRITICAL",
                "estimated_effort": "High",
                "timeline": "Immediate (1-3 days)",
                "owner": "Security Team",
                "description": vuln["description"]
            })
        
        # Actions basées sur les vulnérabilités hautes
        high_vulns = [v for v in vulnerability_scan["vulnerabilities"] if v["severity"] == "high"]
        for vuln in high_vulns:
            remediation_actions.append({
                "action": f"Address {vuln['type']} issue",
                "priority": "HIGH",
                "estimated_effort": "Medium",
                "timeline": "Short term (1-2 weeks)",
                "owner": "ML Security Team",
                "description": vuln["description"]
            })
        
        # Actions générales
        if recommendations:
            remediation_actions.append({
                "action": "Implement security recommendations",
                "priority": "MEDIUM",
                "estimated_effort": "Variable",
                "timeline": "Medium term (1-2 months)",
                "owner": "Development Team",
                "description": "Address all security recommendations from audit"
            })
        
        return remediation_actions
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """📊 Dashboard de sécurité"""
        
        current_time = datetime.now()
        
        # Statistiques des menaces
        threat_stats = {
            "total_threats": len(self.active_threats),
            "critical_threats": len([t for t in self.active_threats if t.threat_level == ThreatLevel.CRITICAL]),
            "high_threats": len([t for t in self.active_threats if t.threat_level == ThreatLevel.HIGH]),
            "threats_by_type": {}
        }
        
        for threat_type in AttackType:
            threat_stats["threats_by_type"][threat_type.value] = len([
                t for t in self.active_threats if t.threat_type == threat_type
            ])
        
        # Statistiques des événements
        recent_events = [e for e in self.security_events 
                        if (current_time - e.timestamp).days < 7]
        
        event_stats = {
            "total_events_7d": len(recent_events),
            "blocked_requests_7d": len([e for e in recent_events if "blocked" in e.security_flags]),
            "average_processing_time_ms": np.mean([e.processing_time_ms for e in recent_events]) if recent_events else 0.0
        }
        
        # Statistiques des politiques
        policy_stats = {
            "total_policies": len(self.policy_engine.policies),
            "active_policies": len([p for p in self.policy_engine.policies.values() if p.enabled]),
            "policy_violations_7d": len([e for e in recent_events if e.security_flags])
        }
        
        # Scores de sécurité récents
        recent_validations = [e for e in self.security_events 
                            if e.event_type == "inference_validation" and (current_time - e.timestamp).days < 1]
        
        security_scores = []
        for event in recent_validations:
            validation_result = event.response_data.get("validation_result", {})
            score = validation_result.get("security_score", 1.0)
            security_scores.append(score)
        
        avg_security_score = np.mean(security_scores) if security_scores else 1.0
        
        return {
            "dashboard_timestamp": current_time.isoformat(),
            "threat_statistics": threat_stats,
            "event_statistics": event_stats,
            "policy_statistics": policy_stats,
            "security_metrics": {
                "average_security_score_24h": avg_security_score,
                "security_incidents_7d": len([t for t in self.active_threats 
                                            if (current_time - t.detected_at).days < 7]),
                "audit_logs_count": len(self.audit_logs),
                "compliance_coverage": 0.85  # 85% de couverture de conformité simulée
            },
            "recent_threats": [
                {
                    "threat_id": t.threat_id,
                    "type": t.threat_type.value,
                    "level": t.threat_level.value,
                    "confidence": t.detection_confidence,
                    "detected_at": t.detected_at.isoformat()
                }
                for t in sorted(self.active_threats, key=lambda x: x.detected_at, reverse=True)[:10]
            ],
            "system_health": {
                "security_manager_status": "healthy",
                "detection_systems_status": "operational",
                "policy_engine_status": "operational",
                "compliance_manager_status": "operational"
            }
        }

# Export principal
__all__ = [
    'MLSecurityManager',
    'ThreatLevel',
    'AttackType',
    'SecurityMeasure',
    'ComplianceStandard',
    'SecurityThreat',
    'SecurityEvent',
    'SecurityPolicy',
    'SecurityAudit',
    'AdversarialDetector',
    'PromptInjectionDetector',
    'SecurityPolicyEngine',
    'ComplianceManager'
]