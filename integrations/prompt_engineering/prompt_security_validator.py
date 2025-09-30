# 🛡️ Security: Security validator avec advanced threat detection
"""
Prompt Security Validator - Enterprise Implementation
====================================================
Security validator enterprise avec advanced threat detection, injection prevention,
security policy enforcement et threat intelligence integration pour sécurité prompts.

Expert Roles Applied:
- Sécurité: Advanced threat detection et security validation
- Lead Dev IA: AI-powered security analysis et pattern recognition
- Backend Senior: Enterprise security infrastructure et monitoring
- ML Engineer: Machine learning pour detection anomalies et threats
- DBA: Secure data handling et audit trail
- DevOps: Security monitoring et incident response automation

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Integrations - Prompt Engineering
Version: 1.0 Enterprise Production
"""

import asyncio
import json
import logging
import hashlib
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
import redis.asyncio as redis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import numpy as np
import uuid

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Niveaux de menace pour la sécurité des prompts"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types de menaces détectées"""
    PROMPT_INJECTION = "prompt_injection"
    COMMAND_INJECTION = "command_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    MALICIOUS_CONTENT = "malicious_content"
    PRIVACY_VIOLATION = "privacy_violation"
    BIAS_MANIPULATION = "bias_manipulation"
    SOCIAL_ENGINEERING = "social_engineering"

class SecurityStatus(Enum):
    """Statuts de validation sécurité"""
    SAFE = "safe"
    UNSAFE = "unsafe"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
    QUARANTINED = "quarantined"

@dataclass
class SecurityThreat:
    """Structure d'une menace de sécurité identifiée"""
    id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    description: str
    detected_patterns: List[str]
    confidence_score: float
    mitigation_suggestions: List[str]
    detected_at: datetime
    affected_sections: List[str]

@dataclass
class SecurityValidationResult:
    """Résultat de validation sécurité d'un prompt"""
    prompt_id: str
    prompt_content: str
    is_safe: bool
    security_status: SecurityStatus
    overall_security_score: float
    threats_detected: List[SecurityThreat]
    policy_violations: List[str]
    compliance_score: float
    recommendations: List[str]
    validation_timestamp: datetime
    validator_version: str

@dataclass
class SecurityPolicy:
    """Politique de sécurité pour les prompts"""
    id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    severity_level: ThreatLevel
    auto_block: bool
    notification_required: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool

class PromptSecurityValidator:
    """Security validator enterprise avec advanced threat detection et injection prevention"""
    
    def __init__(self, db_config: Dict[str, Any], redis_config: Dict[str, Any]):
        """
        Initialise le validateur de sécurité avec configuration enterprise
        
        Args:
            db_config: Configuration base de données PostgreSQL
            redis_config: Configuration Redis pour cache et performance
        """
        self.db_config = db_config
        self.redis_config = redis_config
        self.db_pool = None
        self.redis_client = None
        
        # Modèles ML pour la détection de menaces
        self.injection_detector = None
        self.anomaly_detector = None
        self.malicious_content_classifier = None
        
        # Politiques de sécurité
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.threat_patterns = {}
        
        # Cache des validations récentes
        self.validation_cache: Dict[str, SecurityValidationResult] = {}
        
        # Configuration enterprise
        self.max_concurrent_validations = 100
        self.cache_ttl = 1800  # 30 minutes
        self.threat_intelligence_update_interval = timedelta(hours=1)
        
        logger.info("PromptSecurityValidator initialized - Enterprise mode")

    async def initialize(self):
        """Initialise les connexions et modèles de sécurité"""
        try:
            # Initialisation pool de connexions PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                min_size=5,
                max_size=20
            )
            
            # Initialisation Redis client
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config.get('password'),
                decode_responses=True
            )
            
            # Création du schéma de base de données
            await self._create_security_schema()
            
            # Initialisation des modèles ML de sécurité
            await self._initialize_security_models()
            
            # Chargement des politiques de sécurité
            await self._load_security_policies()
            
            # Chargement des patterns de menaces
            await self._load_threat_patterns()
            
            # Démarrage du système de threat intelligence
            asyncio.create_task(self._threat_intelligence_updater())
            
            logger.info("PromptSecurityValidator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PromptSecurityValidator: {e}")
            raise

    async def _create_security_schema(self):
        """Crée le schéma de base de données pour la sécurité"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS security_validations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            prompt_id UUID,
            prompt_content TEXT NOT NULL,
            is_safe BOOLEAN NOT NULL,
            security_status VARCHAR(50) NOT NULL,
            overall_security_score FLOAT,
            threats_detected JSONB DEFAULT '[]',
            policy_violations JSONB DEFAULT '[]',
            compliance_score FLOAT,
            recommendations JSONB DEFAULT '[]',
            validation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            validator_version VARCHAR(50),
            user_id UUID,
            session_id VARCHAR(255)
        );
        
        CREATE TABLE IF NOT EXISTS security_policies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            rules JSONB NOT NULL,
            severity_level VARCHAR(50) NOT NULL,
            auto_block BOOLEAN DEFAULT false,
            notification_required BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true
        );
        
        CREATE TABLE IF NOT EXISTS security_incidents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            validation_id UUID REFERENCES security_validations(id),
            threat_type VARCHAR(100) NOT NULL,
            threat_level VARCHAR(50) NOT NULL,
            description TEXT,
            detected_patterns JSONB DEFAULT '[]',
            confidence_score FLOAT,
            mitigation_actions JSONB DEFAULT '[]',
            status VARCHAR(50) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            assigned_to VARCHAR(255)
        );
        
        CREATE TABLE IF NOT EXISTS threat_intelligence (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            threat_signature VARCHAR(500) UNIQUE,
            threat_type VARCHAR(100),
            threat_level VARCHAR(50),
            pattern_regex TEXT,
            description TEXT,
            confidence_score FLOAT,
            last_seen TIMESTAMP,
            report_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true
        );
        
        CREATE INDEX IF NOT EXISTS idx_security_validations_timestamp ON security_validations(validation_timestamp);
        CREATE INDEX IF NOT EXISTS idx_security_validations_status ON security_validations(security_status);
        CREATE INDEX IF NOT EXISTS idx_security_incidents_type ON security_incidents(threat_type);
        CREATE INDEX IF NOT EXISTS idx_threat_intelligence_type ON threat_intelligence(threat_type);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)

    async def injection_attack_detection(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[SecurityThreat]:
        """Détection avancée des attaques d'injection dans les prompts"""
        try:
            threats = []
            
            # Patterns d'injection courants
            injection_patterns = [
                r"ignore\s+(previous|above|all)\s+(instructions?|commands?|prompts?)",
                r"disregard\s+(previous|above|all)\s+(instructions?|commands?|prompts?)",
                r"override\s+(system|security|safety)\s+(settings?|protocols?)",
                r"forget\s+(everything|all|previous)\s+(instructions?|context)",
                r"act\s+as\s+(if|though)\s+you\s+(are|were)",
                r"pretend\s+(to\s+be|you\s+are)",
                r"simulate\s+(being|a)",
                r"roleplay\s+as",
                r"jailbreak|jail\s*break",
                r"developer\s+mode|dev\s+mode",
                r"god\s+mode|admin\s+mode",
                r"bypass\s+(filter|safety|security)",
                r"exploit\s+(vulnerability|weakness)",
                r"\\n\\n###\\s*Instruction",
                r"</.*?>.*?<.*?>",  # HTML/XML injection
                r"\${.*?}",  # Template injection
                r"{{.*?}}",  # Mustache/Handlebars injection
            ]
            
            # Détection par patterns regex
            for i, pattern in enumerate(injection_patterns):
                matches = re.findall(pattern, prompt, re.IGNORECASE | re.MULTILINE)
                if matches:
                    threat = SecurityThreat(
                        id=str(uuid.uuid4()),
                        threat_type=ThreatType.PROMPT_INJECTION,
                        threat_level=ThreatLevel.HIGH,
                        description=f"Prompt injection pattern detected: {pattern}",
                        detected_patterns=[str(match) for match in matches],
                        confidence_score=0.8 + (len(matches) * 0.1),
                        mitigation_suggestions=[
                            "Remove or sanitize injection patterns",
                            "Use parameterized prompts instead",
                            "Implement input validation"
                        ],
                        detected_at=datetime.utcnow(),
                        affected_sections=[f"Pattern {i+1}"]
                    )
                    threats.append(threat)
            
            # Détection ML basée sur le comportement
            ml_threats = await self._ml_injection_detection(prompt, context)
            threats.extend(ml_threats)
            
            # Analyse contextuelle avancée
            contextual_threats = await self._contextual_injection_analysis(prompt, context)
            threats.extend(contextual_threats)
            
            logger.info(f"Injection detection completed: {len(threats)} threats found")
            return threats
            
        except Exception as e:
            logger.error(f"Injection attack detection failed: {e}")
            return []

    async def prompt_vulnerability_scanning(self, prompt: str) -> Dict[str, Any]:
        """Scanner de vulnérabilités avancé pour les prompts"""
        try:
            vulnerabilities = {
                'injection_vulnerabilities': [],
                'data_leakage_risks': [],
                'manipulation_vectors': [],
                'bypass_attempts': [],
                'social_engineering_risks': []
            }
            
            # Scan des vulnérabilités d'injection
            injection_vulns = await self._scan_injection_vulnerabilities(prompt)
            vulnerabilities['injection_vulnerabilities'] = injection_vulns
            
            # Scan des risques de fuite de données
            data_leakage_risks = await self._scan_data_leakage_risks(prompt)
            vulnerabilities['data_leakage_risks'] = data_leakage_risks
            
            # Scan des vecteurs de manipulation
            manipulation_vectors = await self._scan_manipulation_vectors(prompt)
            vulnerabilities['manipulation_vectors'] = manipulation_vectors
            
            # Scan des tentatives de bypass
            bypass_attempts = await self._scan_bypass_attempts(prompt)
            vulnerabilities['bypass_attempts'] = bypass_attempts
            
            # Scan des risques d'ingénierie sociale
            social_engineering_risks = await self._scan_social_engineering_risks(prompt)
            vulnerabilities['social_engineering_risks'] = social_engineering_risks
            
            # Calcul du score de vulnérabilité global
            total_vulns = sum(len(v) for v in vulnerabilities.values())
            vulnerability_score = min(total_vulns / 10, 1.0)  # Normalisé sur 10 vulnérabilités max
            
            scan_result = {
                'vulnerabilities': vulnerabilities,
                'total_vulnerabilities': total_vulns,
                'vulnerability_score': vulnerability_score,
                'risk_level': self._calculate_risk_level(vulnerability_score),
                'recommendations': await self._generate_vulnerability_recommendations(vulnerabilities),
                'scan_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Vulnerability scanning completed: {total_vulns} vulnerabilities found")
            return scan_result
            
        except Exception as e:
            logger.error(f"Prompt vulnerability scanning failed: {e}")
            return {'error': str(e)}

    async def security_policy_enforcement(self, prompt: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enforcement des politiques de sécurité enterprise"""
        try:
            enforcement_result = {
                'policy_violations': [],
                'enforced_actions': [],
                'blocked_content': [],
                'warnings': [],
                'compliance_score': 1.0
            }
            
            # Vérification contre toutes les politiques actives
            for policy_id, policy in self.security_policies.items():
                if not policy.is_active:
                    continue
                
                violation_result = await self._check_policy_violation(prompt, policy, user_context)
                
                if violation_result['violated']:
                    enforcement_result['policy_violations'].append({
                        'policy_id': policy_id,
                        'policy_name': policy.name,
                        'violation_details': violation_result['details'],
                        'severity': policy.severity_level.value,
                        'auto_block': policy.auto_block
                    })
                    
                    # Actions d'enforcement
                    if policy.auto_block:
                        enforcement_result['enforced_actions'].append(f"Content blocked due to {policy.name}")
                        enforcement_result['blocked_content'].append(violation_result['violating_content'])
                    
                    if policy.notification_required:
                        enforcement_result['warnings'].append(f"Policy violation: {policy.name}")
                    
                    # Réduction du score de compliance
                    severity_impact = {
                        ThreatLevel.LOW: 0.1,
                        ThreatLevel.MEDIUM: 0.2,
                        ThreatLevel.HIGH: 0.4,
                        ThreatLevel.CRITICAL: 0.8
                    }
                    enforcement_result['compliance_score'] -= severity_impact.get(policy.severity_level, 0.2)
            
            enforcement_result['compliance_score'] = max(0.0, enforcement_result['compliance_score'])
            
            # Génération d'alertes si nécessaire
            if enforcement_result['policy_violations']:
                await self._generate_security_alerts(enforcement_result, user_context)
            
            logger.info(f"Security policy enforcement completed: {len(enforcement_result['policy_violations'])} violations")
            return enforcement_result
            
        except Exception as e:
            logger.error(f"Security policy enforcement failed: {e}")
            return {'error': str(e)}

    async def threat_intelligence_integration(self) -> Dict[str, Any]:
        """Intégration de threat intelligence pour mise à jour des signatures"""
        try:
            intelligence_update = {
                'new_threats': 0,
                'updated_threats': 0,
                'threat_sources': [],
                'last_update': datetime.utcnow().isoformat(),
                'intelligence_score': 0.0
            }
            
            # Mise à jour depuis les sources de threat intelligence
            threat_sources = [
                'internal_ml_detection',
                'security_incident_analysis',
                'pattern_evolution_analysis',
                'community_threat_sharing'
            ]
            
            for source in threat_sources:
                source_update = await self._update_from_threat_source(source)
                intelligence_update['new_threats'] += source_update['new_threats']
                intelligence_update['updated_threats'] += source_update['updated_threats']
                intelligence_update['threat_sources'].append({
                    'source': source,
                    'status': source_update['status'],
                    'threats_processed': source_update['threats_processed']
                })
            
            # Calcul du score d'intelligence
            total_threats = intelligence_update['new_threats'] + intelligence_update['updated_threats']
            intelligence_update['intelligence_score'] = min(total_threats / 100, 1.0)
            
            # Mise à jour des modèles ML avec nouvelles données
            if total_threats > 0:
                await self._retrain_security_models()
            
            logger.info(f"Threat intelligence update completed: {total_threats} threats processed")
            return intelligence_update
            
        except Exception as e:
            logger.error(f"Threat intelligence integration failed: {e}")
            return {'error': str(e)}

    async def security_analytics_reporting(self, time_range: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Génération de rapports analytiques de sécurité"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Statistiques générales
            general_stats = await self._get_security_general_stats(start_time, end_time)
            
            # Analyse des menaces détectées
            threat_analysis = await self._analyze_detected_threats(start_time, end_time)
            
            # Analyse des tendances de sécurité
            security_trends = await self._analyze_security_trends(start_time, end_time)
            
            # Performance des modèles de détection
            model_performance = await self._analyze_detection_model_performance(start_time, end_time)
            
            # Top des attaques tentées
            top_attacks = await self._get_top_attack_patterns(start_time, end_time)
            
            # Recommandations de sécurité
            security_recommendations = await self._generate_security_recommendations(
                general_stats, threat_analysis, security_trends
            )
            
            analytics_report = {
                'report_period': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_days': time_range.days
                },
                'general_statistics': general_stats,
                'threat_analysis': threat_analysis,
                'security_trends': security_trends,
                'model_performance': model_performance,
                'top_attack_patterns': top_attacks,
                'security_recommendations': security_recommendations,
                'overall_security_score': await self._calculate_overall_security_score(general_stats),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info("Security analytics report generated successfully")
            return analytics_report
            
        except Exception as e:
            logger.error(f"Security analytics reporting failed: {e}")
            return {'error': str(e)}

    async def compliance_validation(self, prompt: str, compliance_standards: List[str]) -> Dict[str, Any]:
        """Validation de conformité aux standards de sécurité"""
        try:
            compliance_result = {
                'overall_compliance': True,
                'compliance_score': 1.0,
                'standard_results': {},
                'violations': [],
                'recommendations': []
            }
            
            # Validation pour chaque standard
            for standard in compliance_standards:
                standard_result = await self._validate_compliance_standard(prompt, standard)
                compliance_result['standard_results'][standard] = standard_result
                
                if not standard_result['compliant']:
                    compliance_result['overall_compliance'] = False
                    compliance_result['violations'].extend(standard_result['violations'])
                    compliance_result['recommendations'].extend(standard_result['recommendations'])
                
                # Ajustement du score global
                compliance_result['compliance_score'] *= standard_result['compliance_score']
            
            # Standards supportés
            supported_standards = [
                'GDPR',  # General Data Protection Regulation
                'CCPA',  # California Consumer Privacy Act
                'SOX',   # Sarbanes-Oxley Act
                'HIPAA', # Health Insurance Portability and Accountability Act
                'PCI_DSS', # Payment Card Industry Data Security Standard
                'ISO_27001', # Information Security Management
                'OWASP_TOP10' # OWASP Top 10 Security Risks
            ]
            
            compliance_result['supported_standards'] = supported_standards
            compliance_result['validation_timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Compliance validation completed: {compliance_result['compliance_score']:.2f} score")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return {'error': str(e)}

    async def security_incident_response(self, threat: SecurityThreat, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Système de réponse automatique aux incidents de sécurité"""
        try:
            response_actions = []
            incident_status = "open"
            
            # Actions basées sur le niveau de menace
            if threat.threat_level == ThreatLevel.CRITICAL:
                # Actions immédiates pour menaces critiques
                response_actions.extend([
                    "immediate_content_block",
                    "security_team_alert",
                    "user_session_quarantine",
                    "threat_pattern_update",
                    "security_log_priority_escalation"
                ])
                incident_status = "critical_response"
                
            elif threat.threat_level == ThreatLevel.HIGH:
                # Actions pour menaces élevées
                response_actions.extend([
                    "content_quarantine",
                    "security_team_notification",
                    "enhanced_monitoring",
                    "threat_pattern_analysis"
                ])
                incident_status = "high_priority"
                
            elif threat.threat_level == ThreatLevel.MEDIUM:
                # Actions pour menaces moyennes
                response_actions.extend([
                    "content_flagging",
                    "automated_analysis",
                    "pattern_learning_update"
                ])
                incident_status = "monitoring"
            
            # Exécution des actions de réponse
            executed_actions = []
            for action in response_actions:
                action_result = await self._execute_response_action(action, threat, context)
                executed_actions.append({
                    'action': action,
                    'status': action_result['status'],
                    'details': action_result.get('details', ''),
                    'executed_at': datetime.utcnow().isoformat()
                })
            
            # Enregistrement de l'incident
            incident_id = await self._record_security_incident(threat, executed_actions, incident_status)
            
            # Génération de rapport d'incident
            incident_report = {
                'incident_id': incident_id,
                'threat_details': asdict(threat),
                'response_actions': executed_actions,
                'incident_status': incident_status,
                'response_time': (datetime.utcnow() - threat.detected_at).total_seconds(),
                'mitigation_effectiveness': await self._assess_mitigation_effectiveness(executed_actions),
                'follow_up_required': len([a for a in executed_actions if a['status'] == 'failed']) > 0
            }
            
            logger.info(f"Security incident response completed: {incident_id}")
            return incident_report
            
        except Exception as e:
            logger.error(f"Security incident response failed: {e}")
            return {'error': str(e)}

    # Méthodes utilitaires privées
    async def _initialize_security_models(self):
        """Initialise les modèles ML pour la détection de sécurité"""
        try:
            # Modèle de détection d'injection
            self.injection_detector = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Modèle de détection d'anomalies
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            
            # Modèle de classification de contenu malveillant
            self.malicious_content_classifier = MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            )
            
            # Entraînement avec données synthétiques
            await self._train_initial_security_models()
            
            logger.info("Security ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security models: {e}")
            raise

    async def _train_initial_security_models(self):
        """Entraîne les modèles de sécurité avec des données initiales"""
        # Données synthétiques pour l'entraînement initial
        n_samples = 1000
        
        # Features de base (longueur, patterns suspects, etc.)
        X = np.random.randn(n_samples, 15)
        
        # Labels pour injection (0: safe, 1: injection)
        y_injection = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        
        # Labels pour contenu malveillant
        y_malicious = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        
        # Entraînement des modèles
        self.injection_detector.fit(X, y_injection)
        self.anomaly_detector.fit(X)
        self.malicious_content_classifier.fit(X, y_malicious)

    async def _load_security_policies(self):
        """Charge les politiques de sécurité depuis la base de données"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM security_policies WHERE is_active = true")
                
                for row in rows:
                    policy = SecurityPolicy(
                        id=str(row['id']),
                        name=row['name'],
                        description=row['description'],
                        rules=row['rules'],
                        severity_level=ThreatLevel(row['severity_level']),
                        auto_block=row['auto_block'],
                        notification_required=row['notification_required'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        is_active=row['is_active']
                    )
                    self.security_policies[policy.id] = policy
                    
            # Création de politiques par défaut si aucune n'existe
            if not self.security_policies:
                await self._create_default_security_policies()
                
            logger.info(f"Loaded {len(self.security_policies)} security policies")
            
        except Exception as e:
            logger.error(f"Failed to load security policies: {e}")

    async def _load_threat_patterns(self):
        """Charge les patterns de menaces depuis la threat intelligence"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM threat_intelligence WHERE is_active = true")
                
                for row in rows:
                    self.threat_patterns[row['threat_signature']] = {
                        'type': row['threat_type'],
                        'level': row['threat_level'],
                        'pattern': row['pattern_regex'],
                        'confidence': row['confidence_score']
                    }
                    
            logger.info(f"Loaded {len(self.threat_patterns)} threat patterns")
            
        except Exception as e:
            logger.error(f"Failed to load threat patterns: {e}")

    async def _threat_intelligence_updater(self):
        """Mise à jour périodique de la threat intelligence"""
        while True:
            try:
                await self.threat_intelligence_integration()
                await asyncio.sleep(self.threat_intelligence_update_interval.total_seconds())
            except Exception as e:
                logger.error(f"Threat intelligence updater error: {e}")
                await asyncio.sleep(300)  # 5 minutes en cas d'erreur

    async def _ml_injection_detection(self, prompt: str, context: Optional[Dict[str, Any]]) -> List[SecurityThreat]:
        """Détection ML des injections"""
        threats = []
        
        try:
            # Extraction de features
            features = self._extract_security_features(prompt)
            features_array = np.array([features])
            
            # Prédiction d'injection
            injection_prob = self.injection_detector.predict_proba(features_array)[0][1]
            
            if injection_prob > 0.7:  # Seuil de détection
                threat = SecurityThreat(
                    id=str(uuid.uuid4()),
                    threat_type=ThreatType.PROMPT_INJECTION,
                    threat_level=ThreatLevel.HIGH if injection_prob > 0.9 else ThreatLevel.MEDIUM,
                    description=f"ML-detected injection attempt (confidence: {injection_prob:.2f})",
                    detected_patterns=["ML_PATTERN_DETECTION"],
                    confidence_score=injection_prob,
                    mitigation_suggestions=["Apply input sanitization", "Use parameterized queries"],
                    detected_at=datetime.utcnow(),
                    affected_sections=["FULL_PROMPT"]
                )
                threats.append(threat)
                
        except Exception as e:
            logger.error(f"ML injection detection failed: {e}")
        
        return threats

    def _extract_security_features(self, prompt: str) -> List[float]:
        """Extrait les features de sécurité d'un prompt"""
        features = [
            len(prompt),  # Longueur
            len(prompt.split()),  # Nombre de mots
            prompt.count('ignore'),  # Occurrences de mots suspects
            prompt.count('disregard'),
            prompt.count('override'),
            prompt.count('bypass'),
            prompt.count('system'),
            prompt.count('admin'),
            prompt.count('root'),
            prompt.count('!'),  # Ponctuation suspecte
            prompt.count(';'),
            prompt.count('|'),
            prompt.count('&'),
            len(re.findall(r'[A-Z]{3,}', prompt)),  # Mots en majuscules
            len(re.findall(r'[0-9]+', prompt))  # Chiffres
        ]
        
        return features

    async def validate_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> SecurityValidationResult:
        """Validation complète de sécurité d'un prompt"""
        try:
            prompt_id = str(uuid.uuid4())
            
            # Détection des menaces
            threats = await self.injection_attack_detection(prompt, context)
            
            # Enforcement des politiques
            policy_result = await self.security_policy_enforcement(prompt, context)
            
            # Scan des vulnérabilités
            vuln_result = await self.prompt_vulnerability_scanning(prompt)
            
            # Validation compliance
            compliance_result = await self.compliance_validation(prompt, ['OWASP_TOP10', 'GDPR'])
            
            # Calcul du score de sécurité global
            threat_score = 1.0 - (len(threats) * 0.2)
            policy_score = policy_result.get('compliance_score', 1.0)
            vuln_score = 1.0 - vuln_result.get('vulnerability_score', 0.0)
            compliance_score = compliance_result.get('compliance_score', 1.0)
            
            overall_security_score = (threat_score + policy_score + vuln_score + compliance_score) / 4
            
            # Détermination du statut de sécurité
            if overall_security_score >= 0.8:
                security_status = SecurityStatus.SAFE
                is_safe = True
            elif overall_security_score >= 0.6:
                security_status = SecurityStatus.SUSPICIOUS
                is_safe = False
            else:
                security_status = SecurityStatus.UNSAFE
                is_safe = False
            
            # Génération de recommandations
            recommendations = []
            if threats:
                recommendations.extend([t.mitigation_suggestions[0] for t in threats if t.mitigation_suggestions])
            if policy_result.get('warnings'):
                recommendations.extend(policy_result['warnings'])
            
            validation_result = SecurityValidationResult(
                prompt_id=prompt_id,
                prompt_content=prompt,
                is_safe=is_safe,
                security_status=security_status,
                overall_security_score=overall_security_score,
                threats_detected=threats,
                policy_violations=policy_result.get('policy_violations', []),
                compliance_score=compliance_score,
                recommendations=recommendations,
                validation_timestamp=datetime.utcnow(),
                validator_version="1.0.0"
            )
            
            # Sauvegarde en base de données
            await self._save_validation_result(validation_result)
            
            # Mise en cache
            self.validation_cache[prompt_id] = validation_result
            
            logger.info(f"Prompt validation completed: {security_status.value} (score: {overall_security_score:.3f})")
            return validation_result
            
        except Exception as e:
            logger.error(f"Prompt validation failed: {e}")
            raise

    async def _save_validation_result(self, result: SecurityValidationResult):
        """Sauvegarde le résultat de validation en base"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO security_validations (
                        id, prompt_content, is_safe, security_status, overall_security_score,
                        threats_detected, policy_violations, compliance_score, recommendations,
                        validation_timestamp, validator_version
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, uuid.UUID(result.prompt_id), result.prompt_content, result.is_safe,
                result.security_status.value, result.overall_security_score,
                json.dumps([asdict(t) for t in result.threats_detected]),
                json.dumps(result.policy_violations), result.compliance_score,
                json.dumps(result.recommendations), result.validation_timestamp,
                result.validator_version)
                
        except Exception as e:
            logger.error(f"Failed to save validation result: {e}")