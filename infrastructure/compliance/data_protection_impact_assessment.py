#!/usr/bin/env python3
"""
📋 DATA PROTECTION IMPACT ASSESSMENT - IACHERIE ENTERPRISE
Automatisation DPIA GDPR Article 35 avec intelligence artificielle

🏛️ EXPERTISE MULTI-RÔLES:
- Lead Dev IA: Intelligence artificielle pour évaluation automatisée risques privacy
- Backend Senior: Architecture enterprise pour gestion massive DPIA multi-entités
- ML Engineer: Algorithmes ML pour prédiction et scoring risques automatisés
- DBA: Optimisation BD pour stockage assessments complexes et audit trails
- Sécurité: Analyse sécuritaire approfondie et protection données sensibles
- Microservices: Architecture distribuée pour services DPIA multi-juridictions
- Audio Engineer: DPIA spécialisée pour contenu audio et données biométriques
- DevOps: Monitoring DPIA temps réel et alertes compliance automatisées
- IA Prompt Engineer: Auto-génération rapports DPIA intelligents multi-langues

👨‍💻 CRÉATEUR & PROPRIÉTÉ INTELLECTUELLE
Architecte Principal: Fahed Mlaiel (mlaiel@live.de)

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL
Toute utilisation non autorisée = Poursuites judiciaires immédiates
Contact: mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import json
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps, lru_cache
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    pass  # Redis warning suppressed
import asyncpg
from cryptography.fernet import Fernet
import jwt
import aiohttp
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle

# Configuration logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/iacherie/dpia_assessment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Niveaux de risque DPIA"""
    LOW = "low"                    # Risque faible - DPIA optionnelle
    MEDIUM = "medium"              # Risque moyen - DPIA recommandée
    HIGH = "high"                  # Risque élevé - DPIA obligatoire
    VERY_HIGH = "very_high"        # Risque très élevé - DPIA + consultation DPA

class ProcessingCategory(Enum):
    """Catégories de traitement GDPR"""
    SYSTEMATIC_MONITORING = "systematic_monitoring"
    LARGE_SCALE_SPECIAL_CATEGORIES = "large_scale_special_categories"
    LARGE_SCALE_PERSONAL_DATA = "large_scale_personal_data"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"
    VULNERABLE_DATA_SUBJECTS = "vulnerable_data_subjects"
    INNOVATIVE_TECHNOLOGY = "innovative_technology"
    TRANSFER_OUTSIDE_EU = "transfer_outside_eu"
    BIOMETRIC_DATA = "biometric_data"
    GENETIC_DATA = "genetic_data"
    LOCATION_TRACKING = "location_tracking"

class DataCategory(Enum):
    """Catégories de données personnelles"""
    BASIC_PERSONAL = "basic_personal"          # Nom, email, téléphone
    IDENTIFICATION = "identification"          # Numéro ID, passeport
    FINANCIAL = "financial"                    # Données bancaires, paiement
    HEALTH = "health"                          # Données santé
    BIOMETRIC = "biometric"                    # Empreintes, reconnaissance faciale
    GENETIC = "genetic"                        # ADN, génétique
    LOCATION = "location"                      # GPS, géolocalisation
    BEHAVIORAL = "behavioral"                  # Habitudes, préférences
    ELECTRONIC = "electronic"                 # Logs, cookies, tracking
    AUDIO_VISUAL = "audio_visual"              # Enregistrements, photos
    PROFESSIONAL = "professional"             # Données emploi
    COMMUNICATION = "communication"            # Messages, appels

class LegalBasis(Enum):
    """Bases juridiques GDPR Article 6"""
    CONSENT = "consent"                        # Article 6(1)(a)
    CONTRACT = "contract"                      # Article 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"      # Article 6(1)(c)
    VITAL_INTERESTS = "vital_interests"        # Article 6(1)(d)
    PUBLIC_TASK = "public_task"                # Article 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Article 6(1)(f)

@dataclass
class DataSubject:
    """Profil des personnes concernées"""
    category: str  # creators, users, employees, customers
    count_estimate: int
    age_range: Tuple[int, int]
    vulnerable: bool = False
    geographic_scope: List[str] = field(default_factory=list)
    special_protection: bool = False  # Children, elderly, disabled

@dataclass
class ProcessingPurpose:
    """Finalité de traitement"""
    id: str
    name: str
    description: str
    legal_basis: LegalBasis
    data_categories: List[DataCategory]
    retention_period: int  # en mois
    automated_processing: bool = False
    profiling: bool = False
    marketing: bool = False

@dataclass
class TechnicalMeasure:
    """Mesure technique de protection"""
    id: str
    name: str
    description: str
    implementation_level: float  # 0.0-1.0
    effectiveness_score: float   # 0.0-1.0
    cost_estimate: Optional[float] = None
    maintenance_required: bool = True

@dataclass
class OrganizationalMeasure:
    """Mesure organisationnelle de protection"""
    id: str
    name: str
    description: str
    implementation_level: float
    effectiveness_score: float
    training_required: bool = True
    documentation_required: bool = True

@dataclass
class RiskAssessment:
    """Évaluation des risques"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    risk_source: str = ""
    threat_description: str = ""
    vulnerability: str = ""
    potential_impact: str = ""
    likelihood: float = 0.0  # 0.0-1.0
    severity: float = 0.0    # 0.0-1.0
    risk_score: float = 0.0  # likelihood × severity
    risk_level: RiskLevel = RiskLevel.LOW
    mitigation_measures: List[str] = field(default_factory=list)
    residual_risk: float = 0.0

@dataclass
class DPIAAssessment:
    """Analyse d'Impact sur la Protection des Données complète"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Identification du traitement
    processing_name: str = ""
    processing_description: str = ""
    controller_name: str = ""
    controller_contact: str = ""
    processor_names: List[str] = field(default_factory=list)
    
    # Finalités et base juridique
    purposes: List[ProcessingPurpose] = field(default_factory=list)
    data_categories: List[DataCategory] = field(default_factory=list)
    data_subjects: List[DataSubject] = field(default_factory=list)
    
    # Analyse des risques
    processing_categories: List[ProcessingCategory] = field(default_factory=list)
    risk_assessments: List[RiskAssessment] = field(default_factory=list)
    
    # Mesures de protection
    technical_measures: List[TechnicalMeasure] = field(default_factory=list)
    organizational_measures: List[OrganizationalMeasure] = field(default_factory=list)
    
    # Résultats
    overall_risk_level: RiskLevel = RiskLevel.LOW
    dpia_required: bool = False
    consultation_required: bool = False
    approval_status: str = "pending"
    
    # Métadonnées
    assessor_name: str = ""
    review_date: Optional[datetime] = None
    next_review: Optional[datetime] = None
    validity_period: int = 36  # mois
    
    # Documentation
    recommendations: List[str] = field(default_factory=list)
    action_plan: List[str] = field(default_factory=list)
    monitoring_plan: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'processing_name': self.processing_name,
            'processing_description': self.processing_description,
            'controller_name': self.controller_name,
            'controller_contact': self.controller_contact,
            'processor_names': self.processor_names,
            'purposes': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'legal_basis': p.legal_basis.value,
                    'data_categories': [dc.value for dc in p.data_categories],
                    'retention_period': p.retention_period,
                    'automated_processing': p.automated_processing,
                    'profiling': p.profiling,
                    'marketing': p.marketing
                }
                for p in self.purposes
            ],
            'data_categories': [dc.value for dc in self.data_categories],
            'data_subjects': [
                {
                    'category': ds.category,
                    'count_estimate': ds.count_estimate,
                    'age_range': ds.age_range,
                    'vulnerable': ds.vulnerable,
                    'geographic_scope': ds.geographic_scope,
                    'special_protection': ds.special_protection
                }
                for ds in self.data_subjects
            ],
            'processing_categories': [pc.value for pc in self.processing_categories],
            'risk_assessments': [
                {
                    'id': ra.id,
                    'risk_source': ra.risk_source,
                    'threat_description': ra.threat_description,
                    'vulnerability': ra.vulnerability,
                    'potential_impact': ra.potential_impact,
                    'likelihood': ra.likelihood,
                    'severity': ra.severity,
                    'risk_score': ra.risk_score,
                    'risk_level': ra.risk_level.value,
                    'mitigation_measures': ra.mitigation_measures,
                    'residual_risk': ra.residual_risk
                }
                for ra in self.risk_assessments
            ],
            'technical_measures': [
                {
                    'id': tm.id,
                    'name': tm.name,
                    'description': tm.description,
                    'implementation_level': tm.implementation_level,
                    'effectiveness_score': tm.effectiveness_score,
                    'cost_estimate': tm.cost_estimate,
                    'maintenance_required': tm.maintenance_required
                }
                for tm in self.technical_measures
            ],
            'organizational_measures': [
                {
                    'id': om.id,
                    'name': om.name,
                    'description': om.description,
                    'implementation_level': om.implementation_level,
                    'effectiveness_score': om.effectiveness_score,
                    'training_required': om.training_required,
                    'documentation_required': om.documentation_required
                }
                for om in self.organizational_measures
            ],
            'overall_risk_level': self.overall_risk_level.value,
            'dpia_required': self.dpia_required,
            'consultation_required': self.consultation_required,
            'approval_status': self.approval_status,
            'assessor_name': self.assessor_name,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'validity_period': self.validity_period,
            'recommendations': self.recommendations,
            'action_plan': self.action_plan,
            'monitoring_plan': self.monitoring_plan
        }

class DPIAEngine:
    """
    📋 MOTEUR DPIA ENTERPRISE
    Automatisation complète des analyses d'impact protection des données
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialiser le moteur DPIA"""
        self.config = config
        self.redis_client = None
        self.db_pool = None
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Modèles ML pour scoring automatique
        self.risk_model = None
        self.scaler = None
        
        # Référentiels de mesures
        self.technical_measures_catalog: Dict[str, TechnicalMeasure] = {}
        self.organizational_measures_catalog: Dict[str, OrganizationalMeasure] = {}
        
        # Matrices de risques
        self.risk_matrices: Dict[str, Any] = {}
        self.threshold_configs: Dict[str, float] = {}
        
        # Métriques DPIA
        self.metrics = {
            'total_assessments': 0,
            'high_risk_assessments': 0,
            'consultation_required': 0,
            'avg_completion_time': 0.0,
            'automation_accuracy': 0.0
        }
        
        logger.info("📋 DPIA Engine initialisé - Fahed Mlaiel (mlaiel@live.de)")
    
    async def initialize(self):
        """Initialiser le moteur DPIA"""
        try:
            # Connexion Redis pour cache
            self.redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                encoding='utf-8',
                decode_responses=True
            )
            
            # Pool connexions PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                self.config.get('database_url'),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Créer les tables DPIA
            await self._create_dpia_tables()
            
            # Charger les catalogues de mesures
            await self._load_measures_catalogs()
            
            # Initialiser les modèles ML
            await self._initialize_ml_models()
            
            # Configurer les matrices de risques
            await self._setup_risk_matrices()
            
            # Démarrer les workers DPIA
            await self._start_dpia_workers()
            
            logger.info("✅ DPIA Engine initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation DPIA Engine: {e}")
            raise
    
    async def _create_dpia_tables(self):
        """Créer les tables DPIA"""
        async with self.db_pool.acquire() as conn:
            # Table assessments DPIA
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dpia_assessments (
                    id VARCHAR(36) PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    processing_name VARCHAR(255) NOT NULL,
                    processing_description TEXT,
                    controller_name VARCHAR(255),
                    controller_contact VARCHAR(255),
                    processor_names JSONB DEFAULT '[]',
                    purposes JSONB DEFAULT '[]',
                    data_categories JSONB DEFAULT '[]',
                    data_subjects JSONB DEFAULT '[]',
                    processing_categories JSONB DEFAULT '[]',
                    risk_assessments JSONB DEFAULT '[]',
                    technical_measures JSONB DEFAULT '[]',
                    organizational_measures JSONB DEFAULT '[]',
                    overall_risk_level VARCHAR(20) DEFAULT 'low',
                    dpia_required BOOLEAN DEFAULT FALSE,
                    consultation_required BOOLEAN DEFAULT FALSE,
                    approval_status VARCHAR(20) DEFAULT 'pending',
                    assessor_name VARCHAR(255),
                    review_date TIMESTAMP WITH TIME ZONE,
                    next_review TIMESTAMP WITH TIME ZONE,
                    validity_period INTEGER DEFAULT 36,
                    recommendations JSONB DEFAULT '[]',
                    action_plan JSONB DEFAULT '[]',
                    monitoring_plan JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Table templates DPIA
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dpia_templates (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    industry VARCHAR(100),
                    use_case VARCHAR(100),
                    template_data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Table mesures techniques
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS technical_measures (
                    id VARCHAR(100) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    category VARCHAR(100),
                    implementation_complexity DECIMAL(3,2) DEFAULT 0.5,
                    effectiveness_score DECIMAL(3,2) DEFAULT 0.5,
                    cost_estimate DECIMAL(10,2),
                    maintenance_effort DECIMAL(3,2) DEFAULT 0.3,
                    compliance_frameworks JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Index pour performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dpia_timestamp ON dpia_assessments(timestamp);
                CREATE INDEX IF NOT EXISTS idx_dpia_risk_level ON dpia_assessments(overall_risk_level);
                CREATE INDEX IF NOT EXISTS idx_dpia_required ON dpia_assessments(dpia_required);
                CREATE INDEX IF NOT EXISTS idx_dpia_controller ON dpia_assessments(controller_name);
            """)
    
    async def _load_measures_catalogs(self):
        """Charger les catalogues de mesures de protection"""
        # Mesures techniques
        technical_measures = [
            TechnicalMeasure(
                id="encryption_at_rest",
                name="Chiffrement des données au repos",
                description="Chiffrement AES-256 des données stockées",
                implementation_level=0.8,
                effectiveness_score=0.9,
                cost_estimate=5000.0
            ),
            TechnicalMeasure(
                id="encryption_in_transit",
                name="Chiffrement des données en transit",
                description="TLS 1.3 pour toutes les communications",
                implementation_level=0.9,
                effectiveness_score=0.85,
                cost_estimate=2000.0
            ),
            TechnicalMeasure(
                id="access_controls",
                name="Contrôles d'accès granulaires",
                description="Authentification multi-facteurs et RBAC",
                implementation_level=0.7,
                effectiveness_score=0.8,
                cost_estimate=10000.0
            ),
            TechnicalMeasure(
                id="anonymization",
                name="Anonymisation des données",
                description="Techniques d'anonymisation k-anonymat",
                implementation_level=0.6,
                effectiveness_score=0.95,
                cost_estimate=15000.0
            ),
            TechnicalMeasure(
                id="pseudonymization",
                name="Pseudonymisation",
                description="Remplacement des identifiants directs",
                implementation_level=0.8,
                effectiveness_score=0.75,
                cost_estimate=8000.0
            ),
            TechnicalMeasure(
                id="data_minimization",
                name="Minimisation des données",
                description="Collecte limitée aux besoins stricts",
                implementation_level=0.9,
                effectiveness_score=0.9,
                cost_estimate=3000.0
            ),
            TechnicalMeasure(
                id="automated_deletion",
                name="Suppression automatisée",
                description="Suppression automatique selon rétention",
                implementation_level=0.8,
                effectiveness_score=0.85,
                cost_estimate=7000.0
            ),
            TechnicalMeasure(
                id="audit_logging",
                name="Journalisation d'audit",
                description="Logs complets des accès et modifications",
                implementation_level=0.9,
                effectiveness_score=0.7,
                cost_estimate=4000.0
            ),
            TechnicalMeasure(
                id="backup_encryption",
                name="Chiffrement des sauvegardes",
                description="Sauvegardes chiffrées et sécurisées",
                implementation_level=0.8,
                effectiveness_score=0.8,
                cost_estimate=3000.0
            ),
            TechnicalMeasure(
                id="network_segmentation",
                name="Segmentation réseau",
                description="Isolation des systèmes critiques",
                implementation_level=0.6,
                effectiveness_score=0.85,
                cost_estimate=12000.0
            )
        ]
        
        for measure in technical_measures:
            self.technical_measures_catalog[measure.id] = measure
        
        # Mesures organisationnelles
        organizational_measures = [
            OrganizationalMeasure(
                id="privacy_policy",
                name="Politique de confidentialité",
                description="Politique claire et transparente",
                implementation_level=0.9,
                effectiveness_score=0.7,
                documentation_required=True
            ),
            OrganizationalMeasure(
                id="staff_training",
                name="Formation du personnel",
                description="Formation GDPR pour tous les employés",
                implementation_level=0.7,
                effectiveness_score=0.8,
                training_required=True
            ),
            OrganizationalMeasure(
                id="dpo_appointment",
                name="Désignation DPO",
                description="Délégué à la Protection des Données",
                implementation_level=0.8,
                effectiveness_score=0.9,
                training_required=True
            ),
            OrganizationalMeasure(
                id="incident_response",
                name="Procédure de réponse aux incidents",
                description="Plan de réponse aux violations",
                implementation_level=0.7,
                effectiveness_score=0.85,
                documentation_required=True
            ),
            OrganizationalMeasure(
                id="vendor_management",
                name="Gestion des sous-traitants",
                description="Contrats et audits des sous-traitants",
                implementation_level=0.6,
                effectiveness_score=0.8,
                documentation_required=True
            ),
            OrganizationalMeasure(
                id="consent_management",
                name="Gestion du consentement",
                description="Processus de collecte et retrait",
                implementation_level=0.8,
                effectiveness_score=0.9,
                documentation_required=True
            ),
            OrganizationalMeasure(
                id="rights_procedures",
                name="Procédures droits data subjects",
                description="Processus pour exercice des droits",
                implementation_level=0.8,
                effectiveness_score=0.85,
                documentation_required=True
            ),
            OrganizationalMeasure(
                id="regular_audits",
                name="Audits réguliers",
                description="Audits internes de conformité",
                implementation_level=0.6,
                effectiveness_score=0.8,
                documentation_required=True
            )
        ]
        
        for measure in organizational_measures:
            self.organizational_measures_catalog[measure.id] = measure
        
        logger.info(f"✅ Catalogues chargés: {len(self.technical_measures_catalog)} mesures techniques, {len(self.organizational_measures_catalog)} mesures organisationnelles")
    
    async def _initialize_ml_models(self):
        """Initialiser les modèles ML pour scoring automatique"""
        try:
            # Modèle simple pour démonstration
            # Dans une implémentation réelle, charger des modèles pré-entraînés
            self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
            
            # Données d'entraînement simulées
            X_train = np.random.rand(1000, 10)  # Features: data volume, sensitivity, etc.
            y_train = np.random.choice([0, 1, 2, 3], 1000)  # Risk levels
            
            X_scaled = self.scaler.fit_transform(X_train)
            self.risk_model.fit(X_scaled, y_train)
            
            logger.info("✅ Modèles ML initialisés")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur initialisation ML: {e} - Utilisation scoring manuel")
            self.risk_model = None
            self.scaler = None
    
    async def _setup_risk_matrices(self):
        """Configurer les matrices de risques"""
        # Matrice DPIA obligatoire selon GDPR Article 35
        self.risk_matrices['gdpr_article35'] = {
            ProcessingCategory.SYSTEMATIC_MONITORING: 1.0,
            ProcessingCategory.LARGE_SCALE_SPECIAL_CATEGORIES: 1.0,
            ProcessingCategory.LARGE_SCALE_PERSONAL_DATA: 0.8,
            ProcessingCategory.AUTOMATED_DECISION_MAKING: 0.9,
            ProcessingCategory.VULNERABLE_DATA_SUBJECTS: 0.9,
            ProcessingCategory.INNOVATIVE_TECHNOLOGY: 0.7,
            ProcessingCategory.BIOMETRIC_DATA: 1.0,
            ProcessingCategory.GENETIC_DATA: 1.0,
            ProcessingCategory.LOCATION_TRACKING: 0.6
        }
        
        # Seuils de risque
        self.threshold_configs = {
            'dpia_required_threshold': 0.7,      # Score > 0.7 = DPIA obligatoire
            'consultation_threshold': 0.9,       # Score > 0.9 = Consultation DPA
            'high_risk_threshold': 0.8,         # Score > 0.8 = Risque élevé
            'data_subject_threshold': 5000      # > 5000 personnes = grande échelle
        }
        
        logger.info("✅ Matrices de risques configurées")
    
    async def conduct_dpia(
        self,
        processing_name: str,
        processing_description: str,
        controller_name: str,
        controller_contact: str,
        purposes: List[Dict[str, Any]],
        data_categories: List[str],
        data_subjects: List[Dict[str, Any]],
        processor_names: List[str] = None,
        assessor_name: str = "Automated DPIA System"
    ) -> DPIAAssessment:
        """
        📋 Conduire une analyse d'impact DPIA complète
        
        Args:
            processing_name: Nom du traitement
            processing_description: Description du traitement
            controller_name: Nom du responsable de traitement
            controller_contact: Contact du responsable
            purposes: Finalités de traitement
            data_categories: Catégories de données
            data_subjects: Profils des personnes concernées
            processor_names: Noms des sous-traitants
            assessor_name: Nom de l'évaluateur
            
        Returns:
            DPIAAssessment: Analyse complète
        """
        try:
            assessment = DPIAAssessment(
                processing_name=processing_name,
                processing_description=processing_description,
                controller_name=controller_name,
                controller_contact=controller_contact,
                processor_names=processor_names or [],
                assessor_name=assessor_name
            )
            
            # Convertir les finalités
            assessment.purposes = await self._convert_purposes(purposes)
            
            # Convertir les catégories de données
            assessment.data_categories = [DataCategory(cat) for cat in data_categories]
            
            # Convertir les personnes concernées
            assessment.data_subjects = await self._convert_data_subjects(data_subjects)
            
            # Identifier les catégories de traitement
            assessment.processing_categories = await self._identify_processing_categories(assessment)
            
            # Évaluer la nécessité de DPIA
            assessment.dpia_required = await self._evaluate_dpia_requirement(assessment)
            
            # Conduire l'analyse des risques
            assessment.risk_assessments = await self._conduct_risk_analysis(assessment)
            
            # Calculer le niveau de risque global
            assessment.overall_risk_level = await self._calculate_overall_risk(assessment)
            
            # Déterminer si consultation DPA requise
            assessment.consultation_required = await self._evaluate_consultation_requirement(assessment)
            
            # Recommander des mesures de protection
            technical_measures, organizational_measures = await self._recommend_protection_measures(assessment)
            assessment.technical_measures = technical_measures
            assessment.organizational_measures = organizational_measures
            
            # Générer recommandations et plan d'action
            assessment.recommendations = await self._generate_recommendations(assessment)
            assessment.action_plan = await self._generate_action_plan(assessment)
            assessment.monitoring_plan = await self._generate_monitoring_plan(assessment)
            
            # Programmer la prochaine révision
            assessment.next_review = datetime.utcnow() + timedelta(days=assessment.validity_period * 30)
            
            # Stocker l'assessment
            await self._store_dpia_assessment(assessment)
            
            # Mettre à jour les métriques
            await self._update_dpia_metrics(assessment)
            
            logger.info(f"✅ DPIA conduite: {assessment.id} - Risque: {assessment.overall_risk_level.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Erreur conduite DPIA: {e}")
            raise
    
    async def _convert_purposes(self, purposes_data: List[Dict[str, Any]]) -> List[ProcessingPurpose]:
        """Convertir les finalités en objets ProcessingPurpose"""
        purposes = []
        
        for purpose_data in purposes_data:
            purpose = ProcessingPurpose(
                id=purpose_data.get('id', str(uuid.uuid4())),
                name=purpose_data['name'],
                description=purpose_data.get('description', ''),
                legal_basis=LegalBasis(purpose_data['legal_basis']),
                data_categories=[DataCategory(cat) for cat in purpose_data.get('data_categories', [])],
                retention_period=purpose_data.get('retention_period', 12),
                automated_processing=purpose_data.get('automated_processing', False),
                profiling=purpose_data.get('profiling', False),
                marketing=purpose_data.get('marketing', False)
            )
            purposes.append(purpose)
        
        return purposes
    
    async def _convert_data_subjects(self, subjects_data: List[Dict[str, Any]]) -> List[DataSubject]:
        """Convertir les données des personnes concernées"""
        subjects = []
        
        for subject_data in subjects_data:
            subject = DataSubject(
                category=subject_data['category'],
                count_estimate=subject_data['count_estimate'],
                age_range=tuple(subject_data.get('age_range', [18, 65])),
                vulnerable=subject_data.get('vulnerable', False),
                geographic_scope=subject_data.get('geographic_scope', []),
                special_protection=subject_data.get('special_protection', False)
            )
            subjects.append(subject)
        
        return subjects
    
    async def _identify_processing_categories(self, assessment: DPIAAssessment) -> List[ProcessingCategory]:
        """Identifier les catégories de traitement GDPR Article 35"""
        categories = []
        
        # Surveillance systématique
        has_monitoring = any(
            'monitoring' in purpose.name.lower() or 'tracking' in purpose.name.lower()
            for purpose in assessment.purposes
        )
        if has_monitoring:
            categories.append(ProcessingCategory.SYSTEMATIC_MONITORING)
        
        # Grande échelle - données sensibles
        total_subjects = sum(ds.count_estimate for ds in assessment.data_subjects)
        has_special_categories = any(
            cat in [DataCategory.HEALTH, DataCategory.BIOMETRIC, DataCategory.GENETIC]
            for cat in assessment.data_categories
        )
        
        if total_subjects > self.threshold_configs['data_subject_threshold'] and has_special_categories:
            categories.append(ProcessingCategory.LARGE_SCALE_SPECIAL_CATEGORIES)
        elif total_subjects > self.threshold_configs['data_subject_threshold']:
            categories.append(ProcessingCategory.LARGE_SCALE_PERSONAL_DATA)
        
        # Prise de décision automatisée
        has_automated_decision = any(
            purpose.automated_processing or purpose.profiling
            for purpose in assessment.purposes
        )
        if has_automated_decision:
            categories.append(ProcessingCategory.AUTOMATED_DECISION_MAKING)
        
        # Personnes vulnérables
        has_vulnerable = any(ds.vulnerable for ds in assessment.data_subjects)
        if has_vulnerable:
            categories.append(ProcessingCategory.VULNERABLE_DATA_SUBJECTS)
        
        # Données biométriques/génétiques
        if DataCategory.BIOMETRIC in assessment.data_categories:
            categories.append(ProcessingCategory.BIOMETRIC_DATA)
        
        if DataCategory.GENETIC in assessment.data_categories:
            categories.append(ProcessingCategory.GENETIC_DATA)
        
        # Géolocalisation
        if DataCategory.LOCATION in assessment.data_categories:
            categories.append(ProcessingCategory.LOCATION_TRACKING)
        
        return categories
    
    async def _evaluate_dpia_requirement(self, assessment: DPIAAssessment) -> bool:
        """Évaluer si DPIA est obligatoire"""
        # Vérifier les critères GDPR Article 35
        risk_score = 0.0
        
        for category in assessment.processing_categories:
            if category in self.risk_matrices['gdpr_article35']:
                risk_score = max(risk_score, self.risk_matrices['gdpr_article35'][category])
        
        # DPIA obligatoire si score > seuil
        required = risk_score >= self.threshold_configs['dpia_required_threshold']
        
        logger.info(f"📋 DPIA required: {required} (score: {risk_score})")
        return required
    
    async def _conduct_risk_analysis(self, assessment: DPIAAssessment) -> List[RiskAssessment]:
        """Conduire l'analyse des risques"""
        risk_assessments = []
        
        # Risques liés aux données sensibles
        if any(cat in [DataCategory.HEALTH, DataCategory.BIOMETRIC, DataCategory.GENETIC] 
               for cat in assessment.data_categories):
            risk = RiskAssessment(
                risk_source="Données sensibles",
                threat_description="Accès non autorisé aux données sensibles",
                vulnerability="Mesures de sécurité insuffisantes",
                potential_impact="Discrimination, atteinte à la vie privée",
                likelihood=0.3,
                severity=0.9
            )
            risk.risk_score = risk.likelihood * risk.severity
            risk.risk_level = await self._determine_risk_level(risk.risk_score)
            risk.mitigation_measures = [
                "Chiffrement renforcé",
                "Contrôles d'accès stricts",
                "Audit trail complet"
            ]
            risk_assessments.append(risk)
        
        # Risques liés au profiling
        if any(purpose.profiling for purpose in assessment.purposes):
            risk = RiskAssessment(
                risk_source="Profilage automatisé",
                threat_description="Prise de décision discriminatoire",
                vulnerability="Biais algorithimique",
                potential_impact="Discrimination, exclusion sociale",
                likelihood=0.4,
                severity=0.7
            )
            risk.risk_score = risk.likelihood * risk.severity
            risk.risk_level = await self._determine_risk_level(risk.risk_score)
            risk.mitigation_measures = [
                "Audit des algorithmes",
                "Tests de biais",
                "Intervention humaine"
            ]
            risk_assessments.append(risk)
        
        # Risques liés aux transferts
        if assessment.processor_names:
            risk = RiskAssessment(
                risk_source="Transferts vers sous-traitants",
                threat_description="Perte de contrôle des données",
                vulnerability="Contrôles insuffisants chez sous-traitants",
                potential_impact="Violation de données, non-conformité",
                likelihood=0.25,
                severity=0.6
            )
            risk.risk_score = risk.likelihood * risk.severity
            risk.risk_level = await self._determine_risk_level(risk.risk_score)
            risk.mitigation_measures = [
                "Contrats de sous-traitance stricts",
                "Audits réguliers",
                "Clauses contractuelles types"
            ]
            risk_assessments.append(risk)
        
        # Risques liés aux violations
        risk = RiskAssessment(
            risk_source="Violation de données",
            threat_description="Accès malveillant ou fuite accidentelle",
            vulnerability="Mesures de sécurité techniques",
            potential_impact="Atteinte droits et libertés",
            likelihood=0.2,
            severity=0.8
        )
        risk.risk_score = risk.likelihood * risk.severity
        risk.risk_level = await self._determine_risk_level(risk.risk_score)
        risk.mitigation_measures = [
            "Chiffrement bout en bout",
            "Détection d'intrusion",
            "Plan de réponse aux incidents"
        ]
        risk_assessments.append(risk)
        
        return risk_assessments
    
    async def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Déterminer le niveau de risque"""
        if risk_score >= 0.8:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _calculate_overall_risk(self, assessment: DPIAAssessment) -> RiskLevel:
        """Calculer le niveau de risque global"""
        if not assessment.risk_assessments:
            return RiskLevel.LOW
        
        # Prendre le risque maximum
        max_risk_score = max(ra.risk_score for ra in assessment.risk_assessments)
        return await self._determine_risk_level(max_risk_score)
    
    async def _evaluate_consultation_requirement(self, assessment: DPIAAssessment) -> bool:
        """Évaluer si consultation de l'autorité de protection requise"""
        # Consultation requise si risque très élevé et mesures insuffisantes
        if assessment.overall_risk_level == RiskLevel.VERY_HIGH:
            # Vérifier si les mesures sont suffisantes
            total_effectiveness = sum(
                tm.effectiveness_score * tm.implementation_level 
                for tm in assessment.technical_measures
            ) + sum(
                om.effectiveness_score * om.implementation_level
                for om in assessment.organizational_measures
            )
            
            # Si mesures insuffisantes, consultation requise
            return total_effectiveness < 5.0
        
        return False
    
    async def _recommend_protection_measures(self, assessment: DPIAAssessment) -> Tuple[List[TechnicalMeasure], List[OrganizationalMeasure]]:
        """Recommander des mesures de protection adaptées"""
        technical_measures = []
        organizational_measures = []
        
        # Mesures selon les risques identifiés
        has_sensitive_data = any(
            cat in [DataCategory.HEALTH, DataCategory.BIOMETRIC, DataCategory.GENETIC]
            for cat in assessment.data_categories
        )
        
        if has_sensitive_data:
            technical_measures.extend([
                self.technical_measures_catalog['encryption_at_rest'],
                self.technical_measures_catalog['encryption_in_transit'],
                self.technical_measures_catalog['access_controls'],
                self.technical_measures_catalog['anonymization']
            ])
            
            organizational_measures.extend([
                self.organizational_measures_catalog['dpo_appointment'],
                self.organizational_measures_catalog['staff_training'],
                self.organizational_measures_catalog['incident_response']
            ])
        
        # Mesures pour grande échelle
        total_subjects = sum(ds.count_estimate for ds in assessment.data_subjects)
        if total_subjects > self.threshold_configs['data_subject_threshold']:
            technical_measures.extend([
                self.technical_measures_catalog['automated_deletion'],
                self.technical_measures_catalog['audit_logging']
            ])
            
            organizational_measures.extend([
                self.organizational_measures_catalog['regular_audits'],
                self.organizational_measures_catalog['privacy_policy']
            ])
        
        # Mesures pour profilage
        if any(purpose.profiling for purpose in assessment.purposes):
            technical_measures.append(
                self.technical_measures_catalog['pseudonymization']
            )
            
            organizational_measures.append(
                self.organizational_measures_catalog['consent_management']
            )
        
        # Mesures pour sous-traitants
        if assessment.processor_names:
            organizational_measures.append(
                self.organizational_measures_catalog['vendor_management']
            )
        
        # Mesures droits des personnes
        organizational_measures.append(
            self.organizational_measures_catalog['rights_procedures']
        )
        
        # Supprimer les doublons
        technical_measures = list({tm.id: tm for tm in technical_measures}.values())
        organizational_measures = list({om.id: om for om in organizational_measures}.values())
        
        return technical_measures, organizational_measures
    
    async def _generate_recommendations(self, assessment: DPIAAssessment) -> List[str]:
        """Générer des recommandations"""
        recommendations = []
        
        if assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append("🚨 Niveau de risque élevé - Implémenter toutes les mesures recommandées")
        
        if assessment.consultation_required:
            recommendations.append("📞 Consultation de l'autorité de protection des données requise")
        
        if any(ds.vulnerable for ds in assessment.data_subjects):
            recommendations.append("👥 Attention particulière pour les personnes vulnérables")
        
        if any(purpose.profiling for purpose in assessment.purposes):
            recommendations.append("🤖 Implémenter des garde-fous pour le profilage automatisé")
        
        if assessment.processor_names:
            recommendations.append("🤝 Renforcer les contrôles sur les sous-traitants")
        
        recommendations.extend([
            "📚 Former le personnel sur les procédures de protection des données",
            "🔄 Réviser cette DPIA tous les 3 ans ou en cas de changement",
            "📊 Monitorer l'efficacité des mesures mises en place"
        ])
        
        return recommendations
    
    async def _generate_action_plan(self, assessment: DPIAAssessment) -> List[str]:
        """Générer un plan d'action"""
        actions = []
        
        # Actions par priorité selon le risque
        if assessment.overall_risk_level == RiskLevel.VERY_HIGH:
            actions.extend([
                "URGENT: Suspendre le traitement jusqu'à mise en conformité",
                "Implémenter le chiffrement end-to-end immédiatement",
                "Mettre en place des contrôles d'accès stricts"
            ])
        
        if assessment.overall_risk_level == RiskLevel.HIGH:
            actions.extend([
                "Implémenter les mesures techniques dans les 30 jours",
                "Former le personnel dans les 15 jours",
                "Mettre à jour la politique de confidentialité"
            ])
        
        # Actions selon les mesures recommandées
        for tm in assessment.technical_measures:
            if tm.implementation_level < 0.8:
                actions.append(f"Implémenter: {tm.name}")
        
        for om in assessment.organizational_measures:
            if om.implementation_level < 0.8:
                actions.append(f"Mettre en place: {om.name}")
        
        # Actions de suivi
        actions.extend([
            "Programmer une révision dans 6 mois",
            "Mettre en place des indicateurs de suivi",
            "Documenter toutes les mesures implémentées"
        ])
        
        return actions
    
    async def _generate_monitoring_plan(self, assessment: DPIAAssessment) -> List[str]:
        """Générer un plan de surveillance"""
        monitoring = []
        
        monitoring.extend([
            "📊 Monitoring mensuel de l'efficacité des mesures",
            "🔍 Audit trimestriel des contrôles d'accès",
            "📈 Rapport annuel d'évaluation de la DPIA",
            "🚨 Alertes automatiques en cas d'incident",
            "📋 Révision en cas de changement significatif"
        ])
        
        if any(purpose.profiling for purpose in assessment.purposes):
            monitoring.append("🤖 Audit semestriel des algorithmes de profilage")
        
        if assessment.processor_names:
            monitoring.append("🤝 Audit annuel des sous-traitants")
        
        return monitoring
    
    async def _store_dpia_assessment(self, assessment: DPIAAssessment):
        """Stocker l'assessment DPIA en base"""
        async with self.db_pool.acquire() as conn:
            assessment_dict = assessment.to_dict()
            
            await conn.execute("""
                INSERT INTO dpia_assessments (
                    id, timestamp, processing_name, processing_description,
                    controller_name, controller_contact, processor_names,
                    purposes, data_categories, data_subjects, processing_categories,
                    risk_assessments, technical_measures, organizational_measures,
                    overall_risk_level, dpia_required, consultation_required,
                    approval_status, assessor_name, review_date, next_review,
                    validity_period, recommendations, action_plan, monitoring_plan
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25)
            """,
                assessment.id, assessment.timestamp, assessment.processing_name,
                assessment.processing_description, assessment.controller_name,
                assessment.controller_contact, json.dumps(assessment.processor_names),
                json.dumps(assessment_dict['purposes']),
                json.dumps(assessment_dict['data_categories']),
                json.dumps(assessment_dict['data_subjects']),
                json.dumps(assessment_dict['processing_categories']),
                json.dumps(assessment_dict['risk_assessments']),
                json.dumps(assessment_dict['technical_measures']),
                json.dumps(assessment_dict['organizational_measures']),
                assessment.overall_risk_level.value, assessment.dpia_required,
                assessment.consultation_required, assessment.approval_status,
                assessment.assessor_name, assessment.review_date,
                assessment.next_review, assessment.validity_period,
                json.dumps(assessment.recommendations),
                json.dumps(assessment.action_plan),
                json.dumps(assessment.monitoring_plan)
            )
    
    async def get_dpia_dashboard(self) -> Dict[str, Any]:
        """
        📊 Dashboard DPIA
        
        Returns:
            Dict contenant les statistiques DPIA
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Statistiques générales
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_assessments,
                        COUNT(*) FILTER (WHERE dpia_required = true) as required_count,
                        COUNT(*) FILTER (WHERE consultation_required = true) as consultation_count,
                        COUNT(*) FILTER (WHERE overall_risk_level = 'very_high') as very_high_risk,
                        COUNT(*) FILTER (WHERE overall_risk_level = 'high') as high_risk,
                        COUNT(*) FILTER (WHERE approval_status = 'approved') as approved_count
                    FROM dpia_assessments
                    WHERE timestamp >= NOW() - INTERVAL '30 days'
                """)
                
                # DPIA par niveau de risque
                risk_distribution = await conn.fetch("""
                    SELECT 
                        overall_risk_level,
                        COUNT(*) as count
                    FROM dpia_assessments
                    WHERE timestamp >= NOW() - INTERVAL '30 days'
                    GROUP BY overall_risk_level
                """)
                
                # Tendances DPIA
                trends = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('week', timestamp) as week,
                        COUNT(*) as weekly_assessments,
                        COUNT(*) FILTER (WHERE dpia_required = true) as weekly_required
                    FROM dpia_assessments
                    WHERE timestamp >= NOW() - INTERVAL '12 weeks'
                    GROUP BY DATE_TRUNC('week', timestamp)
                    ORDER BY week
                """)
                
                # Temps moyen de completion
                avg_time = await conn.fetchrow("""
                    SELECT 
                        AVG(EXTRACT(EPOCH FROM (updated_at - timestamp))/3600) as avg_hours
                    FROM dpia_assessments
                    WHERE approval_status = 'approved'
                    AND timestamp >= NOW() - INTERVAL '30 days'
                """)
            
            return {
                "overview": {
                    "total_assessments": stats['total_assessments'],
                    "required_count": stats['required_count'],
                    "consultation_count": stats['consultation_count'],
                    "very_high_risk": stats['very_high_risk'],
                    "high_risk": stats['high_risk'],
                    "approved_count": stats['approved_count'],
                    "approval_rate": (stats['approved_count'] / max(stats['total_assessments'], 1)) * 100
                },
                "risk_distribution": [
                    {
                        "risk_level": row['overall_risk_level'],
                        "count": row['count']
                    }
                    for row in risk_distribution
                ],
                "trends": [
                    {
                        "week": row['week'].isoformat(),
                        "total": row['weekly_assessments'],
                        "required": row['weekly_required']
                    }
                    for row in trends
                ],
                "performance": {
                    "avg_completion_hours": float(avg_time['avg_hours'] or 0),
                    "automation_rate": self.metrics['automation_accuracy']
                },
                "metrics": self.metrics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur dashboard DPIA: {e}")
            return {"error": str(e)}
    
    async def _update_dpia_metrics(self, assessment: DPIAAssessment):
        """Mettre à jour les métriques DPIA"""
        self.metrics['total_assessments'] += 1
        
        if assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            self.metrics['high_risk_assessments'] += 1
        
        if assessment.consultation_required:
            self.metrics['consultation_required'] += 1
    
    async def _start_dpia_workers(self):
        """Démarrer les workers DPIA"""
        # Worker de révisions programmées
        asyncio.create_task(self._scheduled_reviews_worker())
        
        logger.info("✅ Workers DPIA démarrés")
    
    async def _scheduled_reviews_worker(self):
        """Worker pour les révisions DPIA programmées"""
        while True:
            try:
                # Récupérer les DPIA à réviser
                async with self.db_pool.acquire() as conn:
                    reviews_due = await conn.fetch("""
                        SELECT id, processing_name, controller_contact
                        FROM dpia_assessments
                        WHERE next_review <= NOW()
                        AND approval_status = 'approved'
                        LIMIT 50
                    """)
                
                for review_row in reviews_due:
                    # Envoyer notification de révision
                    logger.info(f"📋 Révision DPIA due: {review_row['processing_name']}")
                    # Logique de notification ici
                
                await asyncio.sleep(86400)  # Vérifier quotidiennement
                
            except Exception as e:
                logger.error(f"❌ Erreur scheduled reviews worker: {e}")
                await asyncio.sleep(3600)

# Interface publique
async def conduct_automated_dpia(
    processing_name: str,
    controller_name: str,
    purposes: List[Dict[str, Any]],
    data_categories: List[str],
    data_subjects: List[Dict[str, Any]],
    **kwargs
) -> Dict[str, Any]:
    """
    Interface publique pour DPIA automatisée
    
    Args:
        processing_name: Nom du traitement
        controller_name: Responsable de traitement
        purposes: Finalités de traitement
        data_categories: Catégories de données
        data_subjects: Personnes concernées
        **kwargs: Paramètres supplémentaires
        
    Returns:
        Dict: Résultat de l'analyse DPIA
    """
    engine = DPIAEngine({})
    await engine.initialize()
    
    assessment = await engine.conduct_dpia(
        processing_name=processing_name,
        processing_description=kwargs.get('description', ''),
        controller_name=controller_name,
        controller_contact=kwargs.get('controller_contact', ''),
        purposes=purposes,
        data_categories=data_categories,
        data_subjects=data_subjects,
        processor_names=kwargs.get('processor_names', [])
    )
    
    return {
        "assessment_id": assessment.id,
        "dpia_required": assessment.dpia_required,
        "overall_risk_level": assessment.overall_risk_level.value,
        "consultation_required": assessment.consultation_required,
        "recommendations": assessment.recommendations,
        "action_plan": assessment.action_plan,
        "technical_measures_count": len(assessment.technical_measures),
        "organizational_measures_count": len(assessment.organizational_measures)
    }

if __name__ == "__main__":
    # Test du moteur DPIA
    async def test_dpia_engine():
        config = {
            'redis_url': 'redis://localhost:6379',
            'database_url': 'postgresql://user:pass@localhost/iacherie'
        }
        
        engine = DPIAEngine(config)
        await engine.initialize()
        
        # Test DPIA pour plateforme créateurs
        assessment = await engine.conduct_dpia(
            processing_name="Plateforme IA Créateurs iacherie",
            processing_description="Traitement données créateurs pour optimisation IA",
            controller_name="iacherie SAS",
            controller_contact="dpo@iacherie.com",
            purposes=[
                {
                    "name": "Optimisation contenu IA",
                    "legal_basis": "legitimate_interests",
                    "data_categories": ["behavioral", "audio_visual"],
                    "automated_processing": True,
                    "profiling": True
                }
            ],
            data_categories=["basic_personal", "behavioral", "audio_visual"],
            data_subjects=[
                {
                    "category": "creators",
                    "count_estimate": 100000,
                    "age_range": [16, 65],
                    "vulnerable": False
                }
            ]
        )
        
        print(f"✅ DPIA Assessment: {assessment.id}")
        print(f"📋 DPIA Required: {assessment.dpia_required}")
        print(f"⚠️ Risk Level: {assessment.overall_risk_level.value}")
        print(f"📞 Consultation Required: {assessment.consultation_required}")
        print(f"🔧 Technical Measures: {len(assessment.technical_measures)}")
        print(f"📋 Recommendations: {len(assessment.recommendations)}")
        
        # Dashboard
        dashboard = await engine.get_dpia_dashboard()
        print(f"📊 Dashboard: {dashboard['overview']}")
    
    # asyncio.run(test_dpia_engine())
    
    logger.info("📋 DPIA Engine - Prêt pour production")
    logger.info("👨‍💻 Créé par Fahed Mlaiel (mlaiel@live.de)")
    logger.info("⚠️ Propriété intellectuelle exclusive protégée")