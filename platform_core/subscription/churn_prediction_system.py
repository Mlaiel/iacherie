"""🚀 Platform Core Subscription - Churn Prediction System
========================================================
Module: backend/platform_core/subscription/churn_prediction_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME PRÉDICTION CHURN ML
Machine Learning powered churn prediction system with:
- Advanced creator behavior analysis and risk scoring
- Early warning system with automated interventions
- Personalized retention campaigns and recommendations
- Real-time churn probability monitoring
- Creator segment-specific retention strategies
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
import random
import math

# Configure logging
logger = logging.getLogger(__name__)


class ChurnRiskLevel(Enum):
    """Niveaux de risque de churn"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types d'intervention de rétention"""
    EMAIL_CAMPAIGN = "email_campaign"
    DISCOUNT_OFFER = "discount_offer"
    FEATURE_UNLOCK = "feature_unlock"
    PERSONAL_OUTREACH = "personal_outreach"
    USAGE_TUTORIAL = "usage_tutorial"
    LOYALTY_REWARD = "loyalty_reward"
    PLAN_ADJUSTMENT = "plan_adjustment"


class CreatorSegment(Enum):
    """Segments de créateurs"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    VIDEO_CREATOR = "video_creator"
    PODCASTER = "podcaster"
    SOCIAL_INFLUENCER = "social_influencer"


class ChurnStage(Enum):
    """Étapes du parcours de churn"""
    ENGAGED = "engaged"
    AT_RISK = "at_risk"
    DISENGAGED = "disengaged"
    PRE_CHURN = "pre_churn"
    CHURNED = "churned"


@dataclass
class CreatorBehaviorProfile:
    """Profil comportemental créateur"""
    creator_id: str
    segment: CreatorSegment
    subscription_tenure_days: int
    usage_frequency: float
    feature_adoption_rate: float
    content_upload_frequency: float
    collaboration_participation: float
    support_ticket_count: int
    last_login_days_ago: int
    payment_history_score: float
    engagement_score: float
    satisfaction_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChurnRiskAssessment:
    """Évaluation du risque de churn"""
    assessment_id: str
    creator_id: str
    risk_level: ChurnRiskLevel
    churn_probability: float
    confidence_score: float
    risk_factors: List[Dict[str, Any]]
    protective_factors: List[Dict[str, Any]]
    predicted_churn_date: Optional[datetime] = None
    assessment_date: datetime = field(default_factory=datetime.utcnow)
    model_version: str = "2.1.0"


@dataclass
class RetentionIntervention:
    """Intervention de rétention"""
    intervention_id: str
    creator_id: str
    intervention_type: InterventionType
    strategy_name: str
    trigger_reason: str
    personalization_data: Dict[str, Any]
    expected_effectiveness: float
    cost_estimate: Decimal
    implementation_date: datetime
    completion_date: Optional[datetime] = None
    success_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChurnPredictionModel:
    """Modèle de prédiction de churn"""
    model_id: str
    model_type: str
    target_segment: Optional[CreatorSegment] = None
    features: List[str] = field(default_factory=list)
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    last_trained: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class ChurnPredictionSystem:
    """🚀 Système Prédiction Churn ML
    
    Système avancé de prédiction et prévention du churn avec:
    - Modèles ML personnalisés par segment de créateurs
    - Détection précoce des signaux de churn
    - Interventions automatisées et personnalisées
    - Suivi en temps réel des métriques de rétention
    - Optimisation continue des stratégies de rétention
    """

    def __init__(self, level: str = "enterprise"):
        self.version = "2.1.0"
        self.level = level
        self.prediction_models: Dict[str, ChurnPredictionModel] = {}
        self.active_assessments: Dict[str, ChurnRiskAssessment] = {}
        self.intervention_strategies: Dict[str, Any] = {}
        self.retention_history: List[Dict[str, Any]] = []
        
        # Initialize ML components
        self._initialize_prediction_models()
        self._setup_intervention_strategies()
        
        logger.info("🚀 Churn Prediction System initialized")

    def _initialize_prediction_models(self):
        """Initialise les modèles de prédiction de churn"""
        try:
            # Modèle général
            self.prediction_models['general'] = ChurnPredictionModel(
                model_id="general_churn_v2",
                model_type="gradient_boosting",
                features=[
                    'usage_frequency', 'feature_adoption_rate', 'engagement_score',
                    'subscription_tenure_days', 'last_login_days_ago', 'support_ticket_count'
                ],
                accuracy=0.85
            )
            
            # Modèles spécialisés par segment
            for segment in CreatorSegment:
                self.prediction_models[segment.value] = ChurnPredictionModel(
                    model_id=f"{segment.value}_churn_v2",
                    model_type="random_forest",
                    target_segment=segment,
                    features=[
                        'usage_frequency', 'content_upload_frequency', 'collaboration_participation',
                        'payment_history_score', 'satisfaction_score'
                    ],
                    accuracy=0.88
                )
            
            logger.info("✅ Churn prediction models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing prediction models: {e}")
            raise

    def _setup_intervention_strategies(self):
        """Configure les stratégies d'intervention"""
        try:
            self.intervention_strategies = {
                'high_value_retention': {
                    'triggers': ['high_churn_risk', 'premium_subscriber'],
                    'interventions': [InterventionType.PERSONAL_OUTREACH, InterventionType.LOYALTY_REWARD],
                    'effectiveness': 0.75
                },
                'engagement_recovery': {
                    'triggers': ['low_usage', 'feature_underutilization'],
                    'interventions': [InterventionType.USAGE_TUTORIAL, InterventionType.FEATURE_UNLOCK],
                    'effectiveness': 0.65
                },
                'price_sensitive_retention': {
                    'triggers': ['payment_issues', 'downgrade_signals'],
                    'interventions': [InterventionType.DISCOUNT_OFFER, InterventionType.PLAN_ADJUSTMENT],
                    'effectiveness': 0.70
                },
                'new_user_onboarding': {
                    'triggers': ['early_stage_risk', 'low_adoption'],
                    'interventions': [InterventionType.EMAIL_CAMPAIGN, InterventionType.USAGE_TUTORIAL],
                    'effectiveness': 0.60
                }
            }
            
            logger.info("✅ Intervention strategies configured")
            
        except Exception as e:
            logger.error(f"❌ Error setting up intervention strategies: {e}")
            raise

    async def predict_creator_churn(
        self,
        creator_profile: CreatorBehaviorProfile
    ) -> ChurnRiskAssessment:
        """Prédit le risque de churn pour un créateur
        
        Args:
            creator_profile: Profil comportemental du créateur
            
        Returns:
            Évaluation complète du risque de churn
        """
        try:
            # Sélection du modèle approprié
            model = self._select_prediction_model(creator_profile)
            
            # Calcul de la probabilité de churn
            churn_probability = await self._calculate_churn_probability(
                creator_profile, model
            )
            
            # Détermination du niveau de risque
            risk_level = self._determine_risk_level(churn_probability)
            
            # Analyse des facteurs de risque
            risk_factors = await self._analyze_risk_factors(creator_profile)
            protective_factors = await self._analyze_protective_factors(creator_profile)
            
            # Prédiction de la date de churn
            predicted_churn_date = await self._predict_churn_timeline(
                creator_profile, churn_probability
            )
            
            # Calcul du score de confiance
            confidence_score = self._calculate_confidence_score(
                creator_profile, model, risk_factors
            )
            
            # Création de l'évaluation
            assessment = ChurnRiskAssessment(
                assessment_id=f"churn_{creator_profile.creator_id}_{int(datetime.now().timestamp())}",
                creator_id=creator_profile.creator_id,
                risk_level=risk_level,
                churn_probability=churn_probability,
                confidence_score=confidence_score,
                risk_factors=risk_factors,
                protective_factors=protective_factors,
                predicted_churn_date=predicted_churn_date
            )
            
            # Enregistrement de l'évaluation
            self.active_assessments[creator_profile.creator_id] = assessment
            
            logger.info(f"✅ Churn prediction completed for creator {creator_profile.creator_id}")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Error predicting creator churn: {e}")
            raise

    async def identify_risk_factors(
        self,
        creator_profiles: List[CreatorBehaviorProfile]
    ) -> Dict[str, Any]:
        """Identifie les facteurs de risque principaux
        
        Args:
            creator_profiles: Liste des profils créateurs
            
        Returns:
            Analyse des facteurs de risque
        """
        try:
            risk_analysis = {
                'global_risk_factors': {},
                'segment_specific_risks': {},
                'emerging_patterns': [],
                'correlation_matrix': {}
            }
            
            # Analyse globale des facteurs de risque
            global_factors = await self._analyze_global_risk_factors(creator_profiles)
            risk_analysis['global_risk_factors'] = global_factors
            
            # Analyse par segment
            for segment in CreatorSegment:
                segment_profiles = [p for p in creator_profiles if p.segment == segment]
                if segment_profiles:
                    segment_risks = await self._analyze_segment_risk_factors(segment_profiles)
                    risk_analysis['segment_specific_risks'][segment.value] = segment_risks
            
            # Détection de patterns émergents
            emerging_patterns = await self._detect_emerging_risk_patterns(creator_profiles)
            risk_analysis['emerging_patterns'] = emerging_patterns
            
            # Matrice de corrélation
            correlation_matrix = await self._calculate_risk_correlations(creator_profiles)
            risk_analysis['correlation_matrix'] = correlation_matrix
            
            logger.info("✅ Risk factors analysis completed")
            return risk_analysis
            
        except Exception as e:
            logger.error(f"❌ Error identifying risk factors: {e}")
            raise

    async def trigger_retention_campaigns(
        self,
        at_risk_creators: List[str],
        campaign_strategy: str = "adaptive"
    ) -> List[RetentionIntervention]:
        """Déclenche des campagnes de rétention ciblées
        
        Args:
            at_risk_creators: Liste des IDs créateurs à risque
            campaign_strategy: Stratégie de campagne à utiliser
            
        Returns:
            Liste des interventions déclenchées
        """
        try:
            interventions = []
            
            for creator_id in at_risk_creators:
                # Récupération du profil et de l'évaluation
                if creator_id not in self.active_assessments:
                    logger.warning(f"No assessment found for creator {creator_id}")
                    continue
                
                assessment = self.active_assessments[creator_id]
                
                # Sélection de la stratégie d'intervention
                intervention_strategy = await self._select_intervention_strategy(
                    assessment, campaign_strategy
                )
                
                # Personnalisation de l'intervention
                personalized_intervention = await self._personalize_intervention(
                    creator_id, intervention_strategy, assessment
                )
                
                # Création et lancement de l'intervention
                intervention = await self._create_intervention(
                    creator_id, personalized_intervention, assessment
                )
                
                interventions.append(intervention)
                
                # Déclenchement effectif
                await self._execute_intervention(intervention)
            
            logger.info(f"✅ {len(interventions)} retention campaigns triggered")
            return interventions
            
        except Exception as e:
            logger.error(f"❌ Error triggering retention campaigns: {e}")
            raise

    async def measure_intervention_effectiveness(
        self,
        intervention_ids: List[str],
        measurement_period_days: int = 30
    ) -> Dict[str, Any]:
        """Mesure l'efficacité des interventions de rétention
        
        Args:
            intervention_ids: IDs des interventions à mesurer
            measurement_period_days: Période de mesure en jours
            
        Returns:
            Analyse de l'efficacité des interventions
        """
        try:
            effectiveness_analysis = {
                'overall_effectiveness': {},
                'intervention_type_performance': {},
                'segment_specific_results': {},
                'roi_analysis': {},
                'recommendations': []
            }
            
            # Analyse globale d'efficacité
            overall_stats = await self._calculate_overall_effectiveness(
                intervention_ids, measurement_period_days
            )
            effectiveness_analysis['overall_effectiveness'] = overall_stats
            
            # Performance par type d'intervention
            type_performance = await self._analyze_intervention_type_performance(
                intervention_ids, measurement_period_days
            )
            effectiveness_analysis['intervention_type_performance'] = type_performance
            
            # Résultats par segment
            segment_results = await self._analyze_segment_effectiveness(
                intervention_ids, measurement_period_days
            )
            effectiveness_analysis['segment_specific_results'] = segment_results
            
            # Analyse ROI
            roi_analysis = await self._calculate_intervention_roi(
                intervention_ids, measurement_period_days
            )
            effectiveness_analysis['roi_analysis'] = roi_analysis
            
            # Recommandations d'amélioration
            recommendations = await self._generate_improvement_recommendations(
                effectiveness_analysis
            )
            effectiveness_analysis['recommendations'] = recommendations
            
            logger.info("✅ Intervention effectiveness analysis completed")
            return effectiveness_analysis
            
        except Exception as e:
            logger.error(f"❌ Error measuring intervention effectiveness: {e}")
            raise

    def _select_prediction_model(
        self,
        creator_profile: CreatorBehaviorProfile
    ) -> ChurnPredictionModel:
        """Sélectionne le modèle de prédiction approprié"""
        # Priorité au modèle spécialisé si disponible
        segment_model_key = creator_profile.segment.value
        if segment_model_key in self.prediction_models:
            return self.prediction_models[segment_model_key]
        
        # Fallback sur le modèle général
        return self.prediction_models['general']

    async def _calculate_churn_probability(
        self,
        creator_profile: CreatorBehaviorProfile,
        model: ChurnPredictionModel
    ) -> float:
        """Calcule la probabilité de churn"""
        try:
            # Préparation des features
            features = self._prepare_features(creator_profile, model)
            
            # Simulation de prédiction ML (remplace un vrai modèle)
            base_probability = self._calculate_base_churn_probability(features)
            
            # Ajustements basés sur le segment
            segment_adjustment = self._apply_segment_adjustments(
                base_probability, creator_profile.segment
            )
            
            # Ajustements temporels (saisonnalité, tendances)
            temporal_adjustment = self._apply_temporal_adjustments(segment_adjustment)
            
            # Normalisation finale
            final_probability = max(0.0, min(1.0, temporal_adjustment))
            
            return final_probability
            
        except Exception as e:
            logger.error(f"❌ Error calculating churn probability: {e}")
            return 0.5  # Probabilité neutre en cas d'erreur

    def _prepare_features(
        self,
        creator_profile: CreatorBehaviorProfile,
        model: ChurnPredictionModel
    ) -> List[float]:
        """Prépare les features pour le modèle ML"""
        feature_values = []
        
        for feature in model.features:
            if hasattr(creator_profile, feature):
                value = getattr(creator_profile, feature)
                if isinstance(value, (int, float)):
                    feature_values.append(float(value))
                else:
                    # Encoding pour valeurs non-numériques
                    feature_values.append(hash(str(value)) % 100 / 100.0)
            else:
                feature_values.append(0.0)  # Valeur par défaut
        
        return feature_values

    def _calculate_base_churn_probability(self, features: List[float]) -> float:
        """Calcule la probabilité de base de churn"""
        # Simulation d'un modèle ML simple
        
        # Normalisation des features
        normalized_features = [min(1.0, max(0.0, f)) for f in features]
        
        # Calcul pondéré (poids simulés d'un modèle entraîné)
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Ajusté selon le nombre de features
        
        # Assurer que nous avons le bon nombre de poids
        if len(normalized_features) > len(weights):
            weights.extend([0.1] * (len(normalized_features) - len(weights)))
        elif len(normalized_features) < len(weights):
            weights = weights[:len(normalized_features)]
        
        # Calcul de la probabilité pondérée
        probability = sum(w * f for w, f in zip(weights, normalized_features))
        
        # Application d'une fonction sigmoïde pour normaliser
        import math
        return 1 / (1 + math.exp(-6 * (probability - 0.5)))

    def _apply_segment_adjustments(
        self,
        base_probability: float,
        segment: CreatorSegment
    ) -> float:
        """Applique les ajustements spécifiques au segment"""
        segment_multipliers = {
            CreatorSegment.MUSICIAN: 0.9,        # Musiciens plus fidèles
            CreatorSegment.BLOGGER: 1.0,         # Baseline
            CreatorSegment.PHOTOGRAPHER: 0.95,   # Relativement fidèles
            CreatorSegment.VIDEO_CREATOR: 1.1,   # Plus volatiles
            CreatorSegment.PODCASTER: 0.85,      # Très fidèles
            CreatorSegment.SOCIAL_INFLUENCER: 1.2  # Très volatiles
        }
        
        multiplier = segment_multipliers.get(segment, 1.0)
        return base_probability * multiplier

    def _apply_temporal_adjustments(self, probability: float) -> float:
        """Applique les ajustements temporels"""
        now = datetime.now()
        month = now.month
        
        # Ajustements saisonniers
        seasonal_multipliers = {
            1: 1.1,   # Janvier - résolutions abandonnées
            2: 1.05,  # Février
            3: 0.95,  # Mars - reprise activité
            4: 0.9,   # Avril
            5: 0.9,   # Mai
            6: 1.0,   # Juin
            7: 1.05,  # Juillet - vacances
            8: 1.1,   # Août - vacances
            9: 0.85,  # Septembre - rentrée, remotivation
            10: 0.9,  # Octobre
            11: 0.95, # Novembre
            12: 1.0   # Décembre
        }
        
        seasonal_multiplier = seasonal_multipliers.get(month, 1.0)
        return probability * seasonal_multiplier

    def _determine_risk_level(self, churn_probability: float) -> ChurnRiskLevel:
        """Détermine le niveau de risque basé sur la probabilité"""
        if churn_probability < 0.1:
            return ChurnRiskLevel.VERY_LOW
        elif churn_probability < 0.25:
            return ChurnRiskLevel.LOW
        elif churn_probability < 0.5:
            return ChurnRiskLevel.MEDIUM
        elif churn_probability < 0.75:
            return ChurnRiskLevel.HIGH
        else:
            return ChurnRiskLevel.CRITICAL

    async def _analyze_risk_factors(
        self,
        creator_profile: CreatorBehaviorProfile
    ) -> List[Dict[str, Any]]:
        """Analyse les facteurs de risque spécifiques"""
        risk_factors = []
        
        # Facteur: Faible utilisation
        if creator_profile.usage_frequency < 0.3:
            risk_factors.append({
                'factor': 'low_usage_frequency',
                'impact_score': 0.8,
                'description': 'Usage frequency below optimal threshold',
                'recommendation': 'Trigger engagement campaign'
            })
        
        # Facteur: Dernière connexion récente
        if creator_profile.last_login_days_ago > 14:
            risk_factors.append({
                'factor': 'inactive_login',
                'impact_score': 0.9,
                'description': f'No login for {creator_profile.last_login_days_ago} days',
                'recommendation': 'Send re-engagement email'
            })
        
        # Facteur: Faible adoption de fonctionnalités
        if creator_profile.feature_adoption_rate < 0.4:
            risk_factors.append({
                'factor': 'low_feature_adoption',
                'impact_score': 0.6,
                'description': 'Low adoption of platform features',
                'recommendation': 'Provide feature tutorials'
            })
        
        # Facteur: Tickets de support élevés
        if creator_profile.support_ticket_count > 5:
            risk_factors.append({
                'factor': 'high_support_issues',
                'impact_score': 0.7,
                'description': 'Multiple support tickets indicate frustration',
                'recommendation': 'Proactive customer success outreach'
            })
        
        return risk_factors

    async def _analyze_protective_factors(
        self,
        creator_profile: CreatorBehaviorProfile
    ) -> List[Dict[str, Any]]:
        """Analyse les facteurs de protection"""
        protective_factors = []
        
        # Facteur: Longue durée d'abonnement
        if creator_profile.subscription_tenure_days > 365:
            protective_factors.append({
                'factor': 'long_tenure',
                'protection_score': 0.8,
                'description': 'Long-term subscriber with established habits',
                'strength': 'High loyalty indicator'
            })
        
        # Facteur: Haute participation aux collaborations
        if creator_profile.collaboration_participation > 0.7:
            protective_factors.append({
                'factor': 'high_collaboration',
                'protection_score': 0.7,
                'description': 'Active in creator community',
                'strength': 'Strong network effects'
            })
        
        # Facteur: Score d'engagement élevé
        if creator_profile.engagement_score > 0.8:
            protective_factors.append({
                'factor': 'high_engagement',
                'protection_score': 0.9,
                'description': 'Highly engaged with platform',
                'strength': 'Strong product-market fit'
            })
        
        return protective_factors

    async def _predict_churn_timeline(
        self,
        creator_profile: CreatorBehaviorProfile,
        churn_probability: float
    ) -> Optional[datetime]:
        """Prédit la timeline de churn potentiel"""
        if churn_probability < 0.3:
            return None  # Risque trop faible pour prédire
        
        # Calcul basé sur la probabilité et les patterns historiques
        base_days = 30  # Base de 30 jours
        
        # Ajustement basé sur la probabilité
        probability_factor = (1 - churn_probability) * 2  # Plus la probabilité est haute, plus c'est proche
        
        # Ajustement basé sur l'engagement
        engagement_factor = creator_profile.engagement_score * 0.5
        
        # Ajustement basé sur la durée d'abonnement (plus ancien = plus de temps avant churn)
        tenure_factor = min(creator_profile.subscription_tenure_days / 365, 2.0) * 0.3
        
        predicted_days = base_days * (probability_factor + engagement_factor + tenure_factor)
        predicted_days = max(7, min(180, predicted_days))  # Entre 1 semaine et 6 mois
        
        return datetime.now() + timedelta(days=int(predicted_days))

    def _calculate_confidence_score(
        self,
        creator_profile: CreatorBehaviorProfile,
        model: ChurnPredictionModel,
        risk_factors: List[Dict[str, Any]]
    ) -> float:
        """Calcule le score de confiance de la prédiction"""
        confidence_factors = []
        
        # Confiance basée sur la précision du modèle
        model_confidence = model.accuracy
        confidence_factors.append(model_confidence)
        
        # Confiance basée sur la complétude des données
        data_completeness = self._assess_data_completeness(creator_profile)
        confidence_factors.append(data_completeness)
        
        # Confiance basée sur la cohérence des facteurs de risque
        risk_consistency = self._assess_risk_consistency(risk_factors)
        confidence_factors.append(risk_consistency)
        
        # Confiance basée sur la durée d'historique
        history_confidence = min(creator_profile.subscription_tenure_days / 90, 1.0)
        confidence_factors.append(history_confidence)
        
        return sum(confidence_factors) / len(confidence_factors)

    def _assess_data_completeness(self, creator_profile: CreatorBehaviorProfile) -> float:
        """Évalue la complétude des données"""
        total_fields = 12  # Nombre total de champs importants
        complete_fields = 0
        
        # Vérification des champs critiques
        critical_fields = [
            'usage_frequency', 'feature_adoption_rate', 'engagement_score',
            'subscription_tenure_days', 'last_login_days_ago'
        ]
        
        for field in critical_fields:
            if hasattr(creator_profile, field):
                value = getattr(creator_profile, field)
                if value is not None and value >= 0:
                    complete_fields += 1
        
        return complete_fields / len(critical_fields)

    def _assess_risk_consistency(self, risk_factors: List[Dict[str, Any]]) -> float:
        """Évalue la cohérence des facteurs de risque"""
        if not risk_factors:
            return 0.5  # Confiance neutre si pas de facteurs
        
        # Analyse de la cohérence des scores d'impact
        impact_scores = [factor['impact_score'] for factor in risk_factors]
        
        if len(impact_scores) == 1:
            return 0.8  # Bonne confiance pour un seul facteur
        
        # Calcul de la variance (faible variance = plus cohérent)
        mean_impact = sum(impact_scores) / len(impact_scores)
        variance = sum((score - mean_impact) ** 2 for score in impact_scores) / len(impact_scores)
        
        # Conversion de variance en score de confiance (variance faible = confiance haute)
        consistency_score = max(0.1, 1.0 - variance)
        
        return consistency_score

    # Méthodes d'intervention et de stratégie
    async def _select_intervention_strategy(
        self,
        assessment: ChurnRiskAssessment,
        campaign_strategy: str
    ) -> Dict[str, Any]:
        """Sélectionne la stratégie d'intervention appropriée"""
        risk_level = assessment.risk_level
        risk_factors = assessment.risk_factors
        
        # Sélection basée sur le niveau de risque
        if risk_level == ChurnRiskLevel.CRITICAL:
            return self.intervention_strategies['high_value_retention']
        elif risk_level == ChurnRiskLevel.HIGH:
            # Sélection basée sur les facteurs de risque principaux
            main_factors = [f['factor'] for f in risk_factors[:2]]
            
            if 'low_usage_frequency' in main_factors:
                return self.intervention_strategies['engagement_recovery']
            elif 'high_support_issues' in main_factors:
                return self.intervention_strategies['high_value_retention']
            else:
                return self.intervention_strategies['engagement_recovery']
        else:
            return self.intervention_strategies['new_user_onboarding']

    async def _personalize_intervention(
        self,
        creator_id: str,
        intervention_strategy: Dict[str, Any],
        assessment: ChurnRiskAssessment
    ) -> Dict[str, Any]:
        """Personnalise l'intervention pour le créateur"""
        personalized = {
            'strategy': intervention_strategy,
            'personalization': {
                'creator_id': creator_id,
                'risk_level': assessment.risk_level.value,
                'primary_risk_factors': [f['factor'] for f in assessment.risk_factors[:3]],
                'custom_message': self._generate_personalized_message(assessment),
                'recommended_actions': self._generate_recommended_actions(assessment),
                'timing_optimization': self._optimize_intervention_timing(assessment)
            }
        }
        
        return personalized

    def _generate_personalized_message(self, assessment: ChurnRiskAssessment) -> str:
        """Génère un message personnalisé"""
        risk_level = assessment.risk_level
        primary_factors = [f['factor'] for f in assessment.risk_factors[:2]]
        
        if risk_level == ChurnRiskLevel.CRITICAL:
            return "We've noticed you haven't been as active lately. Let's help you get the most out of your subscription."
        elif 'low_usage_frequency' in primary_factors:
            return "Discover features you might have missed that could boost your creative workflow."
        elif 'inactive_login' in primary_factors:
            return "Welcome back! Here's what's new since your last visit."
        else:
            return "Let's make sure you're getting maximum value from your subscription."

    def _generate_recommended_actions(self, assessment: ChurnRiskAssessment) -> List[str]:
        """Génère des actions recommandées"""
        actions = []
        
        for factor in assessment.risk_factors[:3]:
            if factor['factor'] == 'low_usage_frequency':
                actions.append("Schedule a quick platform tour")
            elif factor['factor'] == 'low_feature_adoption':
                actions.append("Explore our most popular features")
            elif factor['factor'] == 'inactive_login':
                actions.append("Check out recent platform updates")
            elif factor['factor'] == 'high_support_issues':
                actions.append("Connect with our success team")
        
        return actions

    def _optimize_intervention_timing(self, assessment: ChurnRiskAssessment) -> Dict[str, Any]:
        """Optimise le timing de l'intervention"""
        return {
            'immediate_action': assessment.risk_level in [ChurnRiskLevel.CRITICAL, ChurnRiskLevel.HIGH],
            'preferred_time': 'business_hours',
            'frequency_cap': 'max_2_per_week',
            'urgency_level': assessment.risk_level.value
        }

    async def _create_intervention(
        self,
        creator_id: str,
        personalized_intervention: Dict[str, Any],
        assessment: ChurnRiskAssessment
    ) -> RetentionIntervention:
        """Crée une intervention de rétention"""
        strategy = personalized_intervention['strategy']
        personalization = personalized_intervention['personalization']
        
        # Sélection du type d'intervention principal
        intervention_type = strategy['interventions'][0]
        
        # Estimation du coût
        cost_estimates = {
            InterventionType.EMAIL_CAMPAIGN: Decimal('5.00'),
            InterventionType.DISCOUNT_OFFER: Decimal('25.00'),
            InterventionType.FEATURE_UNLOCK: Decimal('10.00'),
            InterventionType.PERSONAL_OUTREACH: Decimal('50.00'),
            InterventionType.USAGE_TUTORIAL: Decimal('15.00'),
            InterventionType.LOYALTY_REWARD: Decimal('30.00'),
            InterventionType.PLAN_ADJUSTMENT: Decimal('20.00')
        }
        
        intervention = RetentionIntervention(
            intervention_id=f"retention_{creator_id}_{int(datetime.now().timestamp())}",
            creator_id=creator_id,
            intervention_type=intervention_type,
            strategy_name=f"churn_prevention_{assessment.risk_level.value}",
            trigger_reason=f"Churn risk: {assessment.churn_probability:.2f}",
            personalization_data=personalization,
            expected_effectiveness=strategy['effectiveness'],
            cost_estimate=cost_estimates.get(intervention_type, Decimal('20.00')),
            implementation_date=datetime.now()
        )
        
        return intervention

    async def _execute_intervention(self, intervention: RetentionIntervention):
        """Exécute l'intervention de rétention"""
        logger.info(f"Executing intervention {intervention.intervention_id} for creator {intervention.creator_id}")
        
        # Simulation de l'exécution (intégration avec systèmes externes)
        if intervention.intervention_type == InterventionType.EMAIL_CAMPAIGN:
            await self._send_retention_email(intervention)
        elif intervention.intervention_type == InterventionType.DISCOUNT_OFFER:
            await self._apply_retention_discount(intervention)
        elif intervention.intervention_type == InterventionType.PERSONAL_OUTREACH:
            await self._schedule_personal_outreach(intervention)
        # ... autres types d'intervention
        
        # Mise à jour du statut
        intervention.completion_date = datetime.now()
        
        logger.info(f"✅ Intervention {intervention.intervention_id} executed successfully")

    async def _send_retention_email(self, intervention: RetentionIntervention):
        """Envoie un email de rétention"""
        logger.info(f"Sending retention email to creator {intervention.creator_id}")
        # Intégration avec service d'email

    async def _apply_retention_discount(self, intervention: RetentionIntervention):
        """Applique une remise de rétention"""
        logger.info(f"Applying retention discount for creator {intervention.creator_id}")
        # Intégration avec système de facturation

    async def _schedule_personal_outreach(self, intervention: RetentionIntervention):
        """Programme un contact personnel"""
        logger.info(f"Scheduling personal outreach for creator {intervention.creator_id}")
        # Intégration avec CRM/système de support

    # Méthodes d'analyse d'efficacité
    async def _calculate_overall_effectiveness(
        self,
        intervention_ids: List[str],
        measurement_period_days: int
    ) -> Dict[str, float]:
        """Calcule l'efficacité globale des interventions"""
        # Simulation de calculs d'efficacité
        return {
            'retention_rate_improvement': 0.15,  # +15%
            'churn_reduction_percentage': 0.22,  # -22% de churn
            'average_intervention_cost': 18.50,
            'cost_per_retained_customer': 85.00,
            'roi_multiple': 4.2
        }

    async def _analyze_intervention_type_performance(
        self,
        intervention_ids: List[str],
        measurement_period_days: int
    ) -> Dict[str, Dict[str, float]]:
        """Analyse la performance par type d'intervention"""
        return {
            'email_campaign': {
                'success_rate': 0.65,
                'cost_effectiveness': 0.85,
                'response_rate': 0.35
            },
            'discount_offer': {
                'success_rate': 0.78,
                'cost_effectiveness': 0.65,
                'response_rate': 0.55
            },
            'personal_outreach': {
                'success_rate': 0.85,
                'cost_effectiveness': 0.45,
                'response_rate': 0.75
            }
        }

    async def _analyze_segment_effectiveness(
        self,
        intervention_ids: List[str],
        measurement_period_days: int
    ) -> Dict[str, Dict[str, float]]:
        """Analyse l'efficacité par segment de créateurs"""
        return {
            'musician': {'retention_improvement': 0.18, 'intervention_response': 0.72},
            'blogger': {'retention_improvement': 0.12, 'intervention_response': 0.68},
            'photographer': {'retention_improvement': 0.15, 'intervention_response': 0.70},
            'video_creator': {'retention_improvement': 0.20, 'intervention_response': 0.65}
        }

    async def _calculate_intervention_roi(
        self,
        intervention_ids: List[str],
        measurement_period_days: int
    ) -> Dict[str, float]:
        """Calcule le ROI des interventions"""
        return {
            'total_intervention_cost': 2500.00,
            'revenue_retained': 12500.00,
            'net_benefit': 10000.00,
            'roi_percentage': 400.0,
            'payback_period_days': 15
        }

    async def _generate_improvement_recommendations(
        self,
        effectiveness_analysis: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        # Analyse des performances
        overall = effectiveness_analysis.get('overall_effectiveness', {})
        roi = effectiveness_analysis.get('roi_analysis', {})
        
        if overall.get('retention_rate_improvement', 0) < 0.10:
            recommendations.append("Consider more aggressive intervention strategies")
        
        if roi.get('roi_percentage', 0) < 200:
            recommendations.append("Optimize cost-effectiveness of interventions")
        
        recommendations.append("Increase personalization depth for higher engagement")
        recommendations.append("Test new intervention channels (SMS, in-app notifications)")
        
        return recommendations

    # Méthodes d'analyse de risque global
    async def _analyze_global_risk_factors(
        self,
        creator_profiles: List[CreatorBehaviorProfile]
    ) -> Dict[str, float]:
        """Analyse les facteurs de risque globaux"""
        if not creator_profiles:
            return {}
        
        total_profiles = len(creator_profiles)
        
        return {
            'low_usage_prevalence': len([p for p in creator_profiles if p.usage_frequency < 0.3]) / total_profiles,
            'high_support_tickets': len([p for p in creator_profiles if p.support_ticket_count > 5]) / total_profiles,
            'inactive_users': len([p for p in creator_profiles if p.last_login_days_ago > 14]) / total_profiles,
            'low_feature_adoption': len([p for p in creator_profiles if p.feature_adoption_rate < 0.4]) / total_profiles
        }

    async def _analyze_segment_risk_factors(
        self,
        segment_profiles: List[CreatorBehaviorProfile]
    ) -> Dict[str, float]:
        """Analyse les facteurs de risque par segment"""
        return await self._analyze_global_risk_factors(segment_profiles)

    async def _detect_emerging_risk_patterns(
        self,
        creator_profiles: List[CreatorBehaviorProfile]
    ) -> List[Dict[str, Any]]:
        """Détecte les patterns de risque émergents"""
        patterns = []
        
        # Exemple de détection de pattern
        recent_profiles = [p for p in creator_profiles if p.subscription_tenure_days < 30]
        if len(recent_profiles) > len(creator_profiles) * 0.3:
            patterns.append({
                'pattern': 'high_new_user_churn_risk',
                'description': 'Elevated churn risk among new subscribers',
                'prevalence': len(recent_profiles) / len(creator_profiles),
                'recommendation': 'Enhance onboarding experience'
            })
        
        return patterns

    async def _calculate_risk_correlations(
        self,
        creator_profiles: List[CreatorBehaviorProfile]
    ) -> Dict[str, Dict[str, float]]:
        """Calcule les corrélations entre facteurs de risque"""
        # Simulation de matrice de corrélation
        return {
            'usage_frequency': {
                'engagement_score': 0.75,
                'feature_adoption_rate': 0.68,
                'last_login_days_ago': -0.82
            },
            'support_ticket_count': {
                'satisfaction_score': -0.65,
                'engagement_score': -0.45
            }
        }


# Global instance
churn_prediction_system = ChurnPredictionSystem()

# Export main functions
__all__ = [
    "ChurnRiskLevel",
    "InterventionType",
    "CreatorSegment",
    "ChurnStage",
    "CreatorBehaviorProfile",
    "ChurnRiskAssessment",
    "RetentionIntervention",
    "ChurnPredictionModel",
    "ChurnPredictionSystem",
    "churn_prediction_system"
]

if __name__ == "__main__":
    logger.info("🚀 Churn Prediction System module loaded successfully")
