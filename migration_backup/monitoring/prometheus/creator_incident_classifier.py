"""
Creator Incident Classifier Module
Classification automatique incidents créateur - IA Chéries Platform

⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️
🔒 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

import asyncio
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import logging
import re

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Niveaux de sévérité des incidents"""
    P1_CRITICAL = "p1_critical"      # Revenue impact >$10K/hour, >1000 creators affected
    P2_HIGH = "p2_high"              # Feature degradation, >100 creators affected  
    P3_MEDIUM = "p3_medium"          # Performance issues, <100 creators affected
    P4_LOW = "p4_low"                # Maintenance alerts, monitoring degradation

class IncidentCategory(Enum):
    """Catégories d'incidents créateur"""
    UPLOAD_FAILURE = "upload_failure"
    AI_PROCESSING_ERROR = "ai_processing_error"
    MONETIZATION_ISSUE = "monetization_issue"
    COLLABORATION_PROBLEM = "collaboration_problem"
    CONTENT_PROTECTION = "content_protection"
    SEO_DEGRADATION = "seo_degradation"
    PLATFORM_ACCESS = "platform_access"
    PAYMENT_ERROR = "payment_error"
    GAMIFICATION_BUG = "gamification_bug"
    DISTRIBUTION_FAILURE = "distribution_failure"

class ResolutionType(Enum):
    """Types de résolution"""
    AUTOMATED_FIX = "automated_fix"
    MANUAL_INTERVENTION = "manual_intervention"
    ESCALATION_REQUIRED = "escalation_required"
    WORKFLOW_ADJUSTMENT = "workflow_adjustment"
    CREATOR_EDUCATION = "creator_education"

@dataclass
class CreatorIncident:
    """Structure d'un incident créateur"""
    incident_id: str
    creator_id: str
    creator_tier: str
    category: IncidentCategory
    severity: IncidentSeverity
    title: str
    description: str
    affected_features: List[str]
    business_impact: float
    timestamp: datetime
    resolution_type: Optional[ResolutionType]
    estimated_resolution_time: Optional[float]
    stakeholders: List[str]
    similar_incidents: List[str]

class CreatorIncidentClassifier:
    """
    Classification automatique incidents créateur
    
    Fonctionnalités:
    - Incident severity auto-classification
    - Creator impact assessment
    - Business priority routing
    - Stakeholder auto-notification
    - Resolution time prediction
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.incidents_cache: Dict[str, CreatorIncident] = {}
        self.ml_models = self._initialize_ml_models()
        self.classification_rules = self._load_classification_rules()
        self.stakeholder_routing = self._setup_stakeholder_routing()
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialise les métriques Prometheus"""
        
        # Métriques de classification
        self.incident_classification_accuracy = Gauge(
            'ainflue_incidents_classification_accuracy',
            'Incident classification accuracy',
            labelnames=['classification_type', 'model_version'],
            registry=self.registry
        )
        
        self.incidents_by_category = Counter(
            'ainflue_incidents_category_total',
            'Total incidents by category',
            labelnames=['category', 'creator_tier', 'severity'],
            registry=self.registry
        )
        
        self.incident_resolution_prediction_accuracy = Gauge(
            'ainflue_incidents_resolution_prediction_accuracy',
            'Resolution time prediction accuracy',
            labelnames=['prediction_model', 'incident_category'],
            registry=self.registry
        )
        
        # Métriques d'impact créateur
        self.creator_impact_score = Gauge(
            'ainflue_incidents_creator_impact_score',
            'Creator impact score for incidents',
            labelnames=['creator_id', 'creator_tier', 'impact_type'],
            registry=self.registry
        )
        
        self.affected_creators_count = Gauge(
            'ainflue_incidents_affected_creators_count',
            'Number of creators affected by incidents',
            labelnames=['incident_category', 'severity'],
            registry=self.registry
        )
        
        self.creator_satisfaction_impact = Gauge(
            'ainflue_incidents_creator_satisfaction_impact',
            'Impact on creator satisfaction',
            labelnames=['creator_tier', 'incident_type'],
            registry=self.registry
        )
        
        # Métriques de routage business
        self.stakeholder_notification_time = Histogram(
            'ainflue_incidents_stakeholder_notification_time_seconds',
            'Time to notify stakeholders',
            labelnames=['stakeholder_type', 'notification_method'],
            registry=self.registry
        )
        
        self.business_priority_score = Gauge(
            'ainflue_incidents_business_priority_score',
            'Business priority score for incidents',
            labelnames=['incident_category', 'business_unit'],
            registry=self.registry
        )
        
        self.escalation_rate = Gauge(
            'ainflue_incidents_escalation_rate',
            'Rate of incident escalations',
            labelnames=['escalation_level', 'incident_type'],
            registry=self.registry
        )
        
        # Métriques de prédiction de résolution
        self.resolution_time_prediction = Histogram(
            'ainflue_incidents_resolution_time_prediction_seconds',
            'Predicted resolution time',
            labelnames=['incident_category', 'complexity_level'],
            registry=self.registry
        )
        
        self.actual_vs_predicted_resolution = Gauge(
            'ainflue_incidents_resolution_prediction_error',
            'Error between actual and predicted resolution time',
            labelnames=['prediction_model', 'error_type'],
            registry=self.registry
        )
        
        logger.info("Creator incident classifier metrics initialized")
    
    def _initialize_ml_models(self) -> Dict[str, Any]:
        """Initialise les modèles ML pour la classification"""
        return {
            'text_vectorizer': TfidfVectorizer(max_features=1000, stop_words='english'),
            'severity_classifier': RandomForestClassifier(n_estimators=100, random_state=42),
            'category_classifier': MultinomialNB(),
            'resolution_predictor': RandomForestClassifier(n_estimators=50, random_state=42),
            'impact_calculator': None,  # Modèle personnalisé à implémenter
            'similarity_matcher': None   # Pour trouver des incidents similaires
        }
    
    def _load_classification_rules(self) -> Dict[str, Any]:
        """Charge les règles de classification"""
        return {
            'severity_keywords': {
                'p1_critical': [
                    'platform down', 'payment failed', 'massive outage', 'revenue loss',
                    'security breach', 'data loss', 'critical error'
                ],
                'p2_high': [
                    'feature broken', 'upload failing', 'ai not working', 'collaboration error',
                    'performance degraded', 'user complaints'
                ],
                'p3_medium': [
                    'slow performance', 'minor bug', 'ui issue', 'recommendation error',
                    'analytics delay'
                ],
                'p4_low': [
                    'cosmetic issue', 'documentation', 'enhancement request', 'monitoring alert'
                ]
            },
            'category_patterns': {
                'upload_failure': r'(?i)(upload|file|content).*(?:fail|error|problem|issue)',
                'ai_processing_error': r'(?i)(ai|ml|processing|enhancement).*(?:fail|error|slow)',
                'monetization_issue': r'(?i)(payment|revenue|monetiz|earning).*(?:fail|error|issue)',
                'collaboration_problem': r'(?i)(collaboration|partner|brand|match).*(?:fail|error)',
                'content_protection': r'(?i)(protection|copyright|ip|violation).*(?:fail|error)',
                'seo_degradation': r'(?i)(seo|ranking|search|visibility).*(?:drop|fail|low)',
                'platform_access': r'(?i)(login|access|auth|account).*(?:fail|error|lock)',
                'payment_error': r'(?i)(payment|transaction|billing).*(?:fail|error|decline)',
                'gamification_bug': r'(?i)(achievement|badge|score|level).*(?:bug|error|wrong)',
                'distribution_failure': r'(?i)(distribution|publish|cross.platform).*(?:fail|error)'
            },
            'creator_tier_impact': {
                'platinum': 4.0,
                'gold': 3.0,
                'silver': 2.0,
                'bronze': 1.0
            },
            'business_units': {
                'upload_failure': ['content_team', 'engineering'],
                'ai_processing_error': ['ai_team', 'engineering'],
                'monetization_issue': ['finance', 'business_development'],
                'collaboration_problem': ['partnerships', 'business_development'],
                'content_protection': ['legal', 'security_team'],
                'seo_degradation': ['marketing', 'seo_team'],
                'platform_access': ['support', 'security_team'],
                'payment_error': ['finance', 'payment_team'],
                'gamification_bug': ['product', 'engineering'],
                'distribution_failure': ['partnerships', 'engineering']
            }
        }
    
    def _setup_stakeholder_routing(self) -> Dict[str, Any]:
        """Configure le routage des stakeholders"""
        return {
            'severity_routing': {
                'p1_critical': ['ceo', 'cto', 'head_of_operations', 'incident_commander'],
                'p2_high': ['head_of_engineering', 'product_manager', 'incident_commander'],
                'p3_medium': ['team_lead', 'senior_engineer'],
                'p4_low': ['assigned_engineer']
            },
            'category_routing': {
                'upload_failure': ['content_team_lead', 'storage_engineer'],
                'ai_processing_error': ['ai_team_lead', 'ml_engineer'],
                'monetization_issue': ['finance_manager', 'payment_specialist'],
                'collaboration_problem': ['partnerships_manager', 'business_dev'],
                'content_protection': ['legal_counsel', 'security_engineer'],
                'seo_degradation': ['seo_manager', 'marketing_team'],
                'platform_access': ['security_team', 'auth_engineer'],
                'payment_error': ['payment_team_lead', 'finance_manager'],
                'gamification_bug': ['product_manager', 'gamification_engineer'],
                'distribution_failure': ['partnerships_team', 'api_engineer']
            },
            'notification_methods': {
                'p1_critical': ['phone', 'slack', 'email', 'pagerduty'],
                'p2_high': ['slack', 'email', 'pagerduty'],
                'p3_medium': ['slack', 'email'],
                'p4_low': ['email']
            }
        }
    
    async def classify_incident(self, 
                              creator_id: str,
                              creator_tier: str,
                              title: str,
                              description: str,
                              affected_features: Optional[List[str]] = None) -> CreatorIncident:
        """Classifie automatiquement un incident créateur"""
        
        start_time = time.time()
        
        try:
            # Génération de l'ID incident
            incident_id = self._generate_incident_id(creator_id, title)
            
            # Classification de la catégorie
            category = await self._classify_category(title, description)
            
            # Classification de la sévérité
            severity = await self._classify_severity(title, description, creator_tier, category)
            
            # Calcul de l'impact business
            business_impact = await self._calculate_business_impact(
                category, severity, creator_tier, affected_features or []
            )
            
            # Prédiction du type de résolution
            resolution_type = await self._predict_resolution_type(category, severity, description)
            
            # Estimation du temps de résolution
            estimated_resolution_time = await self._estimate_resolution_time(
                category, severity, resolution_type
            )
            
            # Identification des stakeholders
            stakeholders = await self._identify_stakeholders(category, severity)
            
            # Recherche d'incidents similaires
            similar_incidents = await self._find_similar_incidents(title, description)
            
            # Création de l'incident
            incident = CreatorIncident(
                incident_id=incident_id,
                creator_id=creator_id,
                creator_tier=creator_tier,
                category=category,
                severity=severity,
                title=title,
                description=description,
                affected_features=affected_features or [],
                business_impact=business_impact,
                timestamp=datetime.now(),
                resolution_type=resolution_type,
                estimated_resolution_time=estimated_resolution_time,
                stakeholders=stakeholders,
                similar_incidents=similar_incidents
            )
            
            # Mise en cache
            self.incidents_cache[incident_id] = incident
            
            # Mise à jour des métriques
            await self._update_classification_metrics(incident)
            
            # Notification des stakeholders
            await self._notify_stakeholders(incident)
            
            processing_time = time.time() - start_time
            logger.info(f"Incident classified: {incident_id} in {processing_time:.2f}s")
            
            return incident
            
        except Exception as e:
            logger.error(f"Error classifying incident: {e}")
            raise
    
    def _generate_incident_id(self, creator_id: str, title: str) -> str:
        """Génère un ID unique pour l'incident"""
        timestamp = str(int(time.time()))
        content = f"{creator_id}{title}{timestamp}"
        return f"INC-{hashlib.sha256(content.encode()).hexdigest()[:8].upper()}"
    
    async def _classify_category(self, title: str, description: str) -> IncidentCategory:
        """Classifie la catégorie de l'incident"""
        try:
            text = f"{title} {description}".lower()
            
            # Classification basée sur des patterns regex
            for category_name, pattern in self.classification_rules['category_patterns'].items():
                if re.search(pattern, text):
                    return IncidentCategory(category_name)
            
            # Classification ML si pas de match pattern
            # (Ici simulation, dans un env réel utiliser le modèle entraîné)
            predicted_category = self._ml_predict_category(text)
            
            return predicted_category
            
        except Exception as e:
            logger.error(f"Error classifying category: {e}")
            return IncidentCategory.PLATFORM_ACCESS  # Défaut
    
    def _ml_predict_category(self, text: str) -> IncidentCategory:
        """Prédiction ML de la catégorie (simulation)"""
        # Simulation - remplacer par un vrai modèle entraîné
        import random
        categories = list(IncidentCategory)
        return random.choice(categories)
    
    async def _classify_severity(self, 
                                title: str, 
                                description: str, 
                                creator_tier: str,
                                category: IncidentCategory) -> IncidentSeverity:
        """Classifie la sévérité de l'incident"""
        try:
            text = f"{title} {description}".lower()
            
            # Facteurs de sévérité
            severity_scores = {}
            
            # Score basé sur les mots-clés
            for severity_name, keywords in self.classification_rules['severity_keywords'].items():
                score = sum(1 for keyword in keywords if keyword in text)
                severity_scores[severity_name] = score
            
            # Ajustement basé sur le tier créateur
            tier_multiplier = self.classification_rules['creator_tier_impact'].get(creator_tier, 1.0)
            
            # Ajustement basé sur la catégorie
            category_severity_map = {
                IncidentCategory.PAYMENT_ERROR: 1.5,
                IncidentCategory.MONETIZATION_ISSUE: 1.4,
                IncidentCategory.AI_PROCESSING_ERROR: 1.2,
                IncidentCategory.UPLOAD_FAILURE: 1.3,
                IncidentCategory.CONTENT_PROTECTION: 1.6
            }
            category_multiplier = category_severity_map.get(category, 1.0)
            
            # Calcul du score final
            final_scores = {}
            for severity_name, score in severity_scores.items():
                final_scores[severity_name] = score * tier_multiplier * category_multiplier
            
            # Sélection de la sévérité avec le score le plus élevé
            if not final_scores or max(final_scores.values()) == 0:
                return IncidentSeverity.P3_MEDIUM  # Défaut
            
            predicted_severity = max(final_scores.items(), key=lambda x: x[1])[0]
            return IncidentSeverity(predicted_severity)
            
        except Exception as e:
            logger.error(f"Error classifying severity: {e}")
            return IncidentSeverity.P3_MEDIUM
    
    async def _calculate_business_impact(self, 
                                       category: IncidentCategory,
                                       severity: IncidentSeverity,
                                       creator_tier: str,
                                       affected_features: List[str]) -> float:
        """Calcule l'impact business de l'incident"""
        try:
            # Scores de base par catégorie
            category_impact = {
                IncidentCategory.PAYMENT_ERROR: 0.9,
                IncidentCategory.MONETIZATION_ISSUE: 0.8,
                IncidentCategory.UPLOAD_FAILURE: 0.7,
                IncidentCategory.AI_PROCESSING_ERROR: 0.6,
                IncidentCategory.COLLABORATION_PROBLEM: 0.5,
                IncidentCategory.CONTENT_PROTECTION: 0.8,
                IncidentCategory.SEO_DEGRADATION: 0.4,
                IncidentCategory.PLATFORM_ACCESS: 0.6,
                IncidentCategory.GAMIFICATION_BUG: 0.3,
                IncidentCategory.DISTRIBUTION_FAILURE: 0.5
            }
            
            # Scores par sévérité
            severity_impact = {
                IncidentSeverity.P1_CRITICAL: 1.0,
                IncidentSeverity.P2_HIGH: 0.7,
                IncidentSeverity.P3_MEDIUM: 0.4,
                IncidentSeverity.P4_LOW: 0.1
            }
            
            # Multiplicateur par tier créateur
            tier_impact = self.classification_rules['creator_tier_impact']
            
            # Facteur fonctionnalités affectées
            feature_impact = min(1.0, len(affected_features) * 0.2)
            
            # Calcul final
            base_impact = category_impact.get(category, 0.5)
            severity_multiplier = severity_impact.get(severity, 0.5)
            tier_multiplier = tier_impact.get(creator_tier, 1.0) / 4.0  # Normalisation
            
            business_impact = (
                base_impact * 0.4 +
                severity_multiplier * 0.4 +
                tier_multiplier * 0.1 +
                feature_impact * 0.1
            )
            
            return min(1.0, business_impact)
            
        except Exception as e:
            logger.error(f"Error calculating business impact: {e}")
            return 0.5
    
    async def _predict_resolution_type(self, 
                                     category: IncidentCategory,
                                     severity: IncidentSeverity,
                                     description: str) -> ResolutionType:
        """Prédit le type de résolution nécessaire"""
        try:
            # Règles basées sur la catégorie et sévérité
            if severity in [IncidentSeverity.P1_CRITICAL, IncidentSeverity.P2_HIGH]:
                if category in [IncidentCategory.PAYMENT_ERROR, IncidentCategory.MONETIZATION_ISSUE]:
                    return ResolutionType.ESCALATION_REQUIRED
                else:
                    return ResolutionType.MANUAL_INTERVENTION
            
            # Détection de patterns pour automation
            automation_keywords = ['configuration', 'cache', 'restart', 'reset', 'sync']
            if any(keyword in description.lower() for keyword in automation_keywords):
                return ResolutionType.AUTOMATED_FIX
            
            # Détection de besoin d'éducation créateur
            education_keywords = ['how to', 'dont understand', 'confused', 'help with']
            if any(keyword in description.lower() for keyword in education_keywords):
                return ResolutionType.CREATOR_EDUCATION
            
            # Détection de besoin d'ajustement workflow
            workflow_keywords = ['process', 'workflow', 'steps', 'procedure']
            if any(keyword in description.lower() for keyword in workflow_keywords):
                return ResolutionType.WORKFLOW_ADJUSTMENT
            
            return ResolutionType.MANUAL_INTERVENTION
            
        except Exception as e:
            logger.error(f"Error predicting resolution type: {e}")
            return ResolutionType.MANUAL_INTERVENTION
    
    async def _estimate_resolution_time(self, 
                                      category: IncidentCategory,
                                      severity: IncidentSeverity,
                                      resolution_type: ResolutionType) -> float:
        """Estime le temps de résolution en minutes"""
        try:
            # Temps de base par sévérité
            base_times = {
                IncidentSeverity.P1_CRITICAL: 60,   # 1 heure
                IncidentSeverity.P2_HIGH: 240,      # 4 heures
                IncidentSeverity.P3_MEDIUM: 480,    # 8 heures
                IncidentSeverity.P4_LOW: 1440       # 24 heures
            }
            
            # Multiplicateurs par type de résolution
            resolution_multipliers = {
                ResolutionType.AUTOMATED_FIX: 0.1,
                ResolutionType.CREATOR_EDUCATION: 0.3,
                ResolutionType.WORKFLOW_ADJUSTMENT: 0.8,
                ResolutionType.MANUAL_INTERVENTION: 1.0,
                ResolutionType.ESCALATION_REQUIRED: 1.5
            }
            
            # Multiplicateurs par catégorie
            category_multipliers = {
                IncidentCategory.PAYMENT_ERROR: 1.2,
                IncidentCategory.AI_PROCESSING_ERROR: 1.5,
                IncidentCategory.CONTENT_PROTECTION: 2.0,
                IncidentCategory.COLLABORATION_PROBLEM: 1.3,
                IncidentCategory.UPLOAD_FAILURE: 0.8
            }
            
            base_time = base_times.get(severity, 480)
            resolution_mult = resolution_multipliers.get(resolution_type, 1.0)
            category_mult = category_multipliers.get(category, 1.0)
            
            estimated_time = base_time * resolution_mult * category_mult
            
            return estimated_time
            
        except Exception as e:
            logger.error(f"Error estimating resolution time: {e}")
            return 480.0  # 8 heures par défaut
    
    async def _identify_stakeholders(self, 
                                   category: IncidentCategory,
                                   severity: IncidentSeverity) -> List[str]:
        """Identifie les stakeholders à notifier"""
        try:
            stakeholders = set()
            
            # Stakeholders basés sur la sévérité
            severity_stakeholders = self.stakeholder_routing['severity_routing'].get(
                severity.value, []
            )
            stakeholders.update(severity_stakeholders)
            
            # Stakeholders basés sur la catégorie
            category_stakeholders = self.stakeholder_routing['category_routing'].get(
                category.value, []
            )
            stakeholders.update(category_stakeholders)
            
            return list(stakeholders)
            
        except Exception as e:
            logger.error(f"Error identifying stakeholders: {e}")
            return ['incident_commander']
    
    async def _find_similar_incidents(self, title: str, description: str) -> List[str]:
        """Trouve des incidents similaires"""
        try:
            # Simulation de recherche d'incidents similaires
            # Dans un environnement réel, utiliser TF-IDF ou embeddings
            
            current_text = f"{title} {description}".lower()
            similar_incidents = []
            
            for incident_id, incident in self.incidents_cache.items():
                incident_text = f"{incident.title} {incident.description}".lower()
                
                # Calcul de similarité simple (mots communs)
                current_words = set(current_text.split())
                incident_words = set(incident_text.split())
                
                if len(current_words) > 0:
                    similarity = len(current_words & incident_words) / len(current_words | incident_words)
                    
                    if similarity > 0.3:  # Seuil de similarité
                        similar_incidents.append(incident_id)
            
            return similar_incidents[:5]  # Top 5 incidents similaires
            
        except Exception as e:
            logger.error(f"Error finding similar incidents: {e}")
            return []
    
    async def _update_classification_metrics(self, incident: CreatorIncident):
        """Met à jour les métriques de classification"""
        try:
            # Compteur par catégorie
            self.incidents_by_category.labels(
                category=incident.category.value,
                creator_tier=incident.creator_tier,
                severity=incident.severity.value
            ).inc()
            
            # Score d'impact créateur
            self.creator_impact_score.labels(
                creator_id=incident.creator_id,
                creator_tier=incident.creator_tier,
                impact_type='business'
            ).set(incident.business_impact)
            
            # Score de priorité business
            business_units = self.classification_rules['business_units'].get(
                incident.category.value, ['general']
            )
            
            for business_unit in business_units:
                self.business_priority_score.labels(
                    incident_category=incident.category.value,
                    business_unit=business_unit
                ).set(incident.business_impact)
            
            # Prédiction de temps de résolution
            if incident.estimated_resolution_time:
                complexity = 'high' if incident.estimated_resolution_time > 480 else 'medium' if incident.estimated_resolution_time > 120 else 'low'
                
                self.resolution_time_prediction.labels(
                    incident_category=incident.category.value,
                    complexity_level=complexity
                ).observe(incident.estimated_resolution_time * 60)  # Conversion en secondes
                
        except Exception as e:
            logger.error(f"Error updating classification metrics: {e}")
    
    async def _notify_stakeholders(self, incident: CreatorIncident):
        """Notifie les stakeholders de l'incident"""
        try:
            notification_methods = self.stakeholder_routing['notification_methods'].get(
                incident.severity.value, ['email']
            )
            
            for stakeholder in incident.stakeholders:
                for method in notification_methods:
                    start_time = time.time()
                    
                    # Simulation d'envoi de notification
                    await asyncio.sleep(0.05)  # Simulation du délai
                    
                    notification_time = time.time() - start_time
                    
                    self.stakeholder_notification_time.labels(
                        stakeholder_type=stakeholder,
                        notification_method=method
                    ).observe(notification_time)
                    
                    logger.debug(f"Notified {stakeholder} via {method} for incident {incident.incident_id}")
                    
        except Exception as e:
            logger.error(f"Error notifying stakeholders: {e}")
    
    def get_incident_by_id(self, incident_id: str) -> Optional[CreatorIncident]:
        """Récupère un incident par son ID"""
        return self.incidents_cache.get(incident_id)
    
    def get_incidents_by_creator(self, creator_id: str) -> List[CreatorIncident]:
        """Récupère tous les incidents d'un créateur"""
        return [incident for incident in self.incidents_cache.values() 
                if incident.creator_id == creator_id]
    
    def get_incidents_by_category(self, category: IncidentCategory) -> List[CreatorIncident]:
        """Récupère tous les incidents d'une catégorie"""
        return [incident for incident in self.incidents_cache.values() 
                if incident.category == category]
    
    def get_high_priority_incidents(self) -> List[CreatorIncident]:
        """Récupère les incidents de haute priorité"""
        return [incident for incident in self.incidents_cache.values() 
                if incident.severity in [IncidentSeverity.P1_CRITICAL, IncidentSeverity.P2_HIGH]]
    
    async def update_incident_resolution(self, 
                                       incident_id: str, 
                                       actual_resolution_time: float,
                                       resolution_successful: bool = True):
        """Met à jour les informations de résolution d'un incident"""
        try:
            incident = self.incidents_cache.get(incident_id)
            if not incident:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            # Calcul de l'erreur de prédiction
            if incident.estimated_resolution_time:
                prediction_error = abs(actual_resolution_time - incident.estimated_resolution_time)
                error_percentage = prediction_error / incident.estimated_resolution_time
                
                self.actual_vs_predicted_resolution.labels(
                    prediction_model='random_forest',
                    error_type='absolute_error'
                ).set(prediction_error)
                
                self.actual_vs_predicted_resolution.labels(
                    prediction_model='random_forest',
                    error_type='percentage_error'
                ).set(error_percentage)
            
            logger.info(f"Updated resolution info for incident {incident_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating incident resolution: {e}")
            return False
    
    def export_registry(self) -> CollectorRegistry:
        """Exporte le registry Prometheus"""
        return self.registry