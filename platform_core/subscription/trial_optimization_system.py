"""🚀 Platform Core Subscription - Trial Optimization System
===========================================================
Module: backend/platform_core/subscription/trial_optimization_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 SYSTÈME D'OPTIMISATION ESSAIS GRATUITS
Optimisation ML des essais gratuits et conversion
- Prédiction conversion trial vers abonnement payant
- Optimisation durée et fonctionnalités trial
- Interventions personnalisées et nudges
- Analytics comportementales trial users
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
import asyncio
import json
from decimal import Decimal
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Configure logging
logger = logging.getLogger(__name__)


class TrialStatus(Enum):
    """Statuts des essais gratuits"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"
    EXTENDED = "extended"


class ConversionProbability(Enum):
    """Niveaux de probabilité de conversion"""
    VERY_HIGH = "very_high"  # >80%
    HIGH = "high"  # 60-80%
    MEDIUM = "medium"  # 40-60%
    LOW = "low"  # 20-40%
    VERY_LOW = "very_low"  # <20%


class InterventionType(Enum):
    """Types d'interventions trial"""
    EMAIL_NUDGE = "email_nudge"
    IN_APP_NOTIFICATION = "in_app_notification"
    FEATURE_UNLOCK = "feature_unlock"
    TRIAL_EXTENSION = "trial_extension"
    DISCOUNT_OFFER = "discount_offer"
    ONBOARDING_BOOST = "onboarding_boost"
    USAGE_TIP = "usage_tip"


@dataclass
class TrialUser:
    """Utilisateur en période d'essai"""
    user_id: str
    trial_start: datetime
    trial_end: datetime
    trial_duration_days: int
    plan_type: str
    creator_type: str
    usage_data: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    behavioral_signals: Dict[str, Any]
    intervention_history: List[Dict[str, Any]]
    conversion_probability: float
    risk_factors: List[str]


@dataclass
class ConversionPrediction:
    """Prédiction de conversion"""
    user_id: str
    probability: float
    probability_level: ConversionProbability
    key_factors: List[str]
    recommended_interventions: List[str]
    optimal_conversion_day: int
    confidence_score: float
    prediction_timestamp: datetime


@dataclass
class TrialIntervention:
    """Intervention trial personnalisée"""
    intervention_id: str
    user_id: str
    intervention_type: InterventionType
    trigger_condition: str
    content: Dict[str, Any]
    scheduled_time: datetime
    executed: bool
    execution_time: Optional[datetime]
    success_metrics: Dict[str, float]


class TrialOptimizationSystem:
    """🚀 Système d'Optimisation Essais Gratuits Enterprise
    
    Système ML avancé pour optimisation des conversions trial
    avec prédictions comportementales et interventions personnalisées.
    """
    
    def __init__(self):
        """Initialise le système d'optimisation trial"""
        self.ml_models = {}
        self.trial_users = {}
        self.intervention_templates = {}
        self.conversion_data = []
        self.optimization_rules = {}
        
        # Configuration des modèles ML
        self.model_config = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        # Initialisation des templates d'intervention
        self._initialize_intervention_templates()
        
        # Règles d'optimisation
        self._initialize_optimization_rules()
        
        logger.info("🚀 Trial Optimization System initialized")
    
    def _initialize_intervention_templates(self):
        """Initialise les templates d'intervention"""
        
        self.intervention_templates = {
            'high_engagement_nudge': {
                'type': InterventionType.EMAIL_NUDGE,
                'trigger': 'high_engagement_low_conversion_risk',
                'content': {
                    'subject': 'Vous êtes sur la bonne voie ! Continuez votre succès',
                    'template': 'high_engagement_conversion',
                    'cta': 'Upgrader maintenant avec 20% de réduction'
                },
                'timing_offset_hours': 72
            },
            
            'low_engagement_boost': {
                'type': InterventionType.ONBOARDING_BOOST,
                'trigger': 'low_engagement_early_trial',
                'content': {
                    'features_to_highlight': ['collaboration_tools', 'premium_templates'],
                    'guided_tour': True,
                    'personal_success_manager': True
                },
                'timing_offset_hours': 24
            },
            
            'conversion_window_offer': {
                'type': InterventionType.DISCOUNT_OFFER,
                'trigger': 'optimal_conversion_window',
                'content': {
                    'discount_percentage': 30,
                    'urgency_timer': True,
                    'social_proof': True,
                    'limited_time': 48
                },
                'timing_offset_hours': 120  # 5 jours
            },
            
            'feature_discovery': {
                'type': InterventionType.FEATURE_UNLOCK,
                'trigger': 'medium_engagement_mid_trial',
                'content': {
                    'unlock_features': ['advanced_analytics', 'collaboration_premium'],
                    'temporary_unlock_hours': 48,
                    'explanation': 'Aperçu exclusif des fonctionnalités premium'
                },
                'timing_offset_hours': 96
            }
        }
    
    def _initialize_optimization_rules(self):
        """Initialise les règles d'optimisation"""
        
        self.optimization_rules = {
            'trial_duration': {
                'musician': {'min': 14, 'max': 30, 'optimal': 21},
                'blogger': {'min': 7, 'max': 21, 'optimal': 14},
                'photographer': {'min': 10, 'max': 30, 'optimal': 18},
                'default': {'min': 14, 'max': 21, 'optimal': 14}
            },
            
            'conversion_windows': {
                'early': [3, 7],  # Jours 3-7
                'mid': [8, 14],   # Jours 8-14
                'late': [15, 21]  # Jours 15-21
            },
            
            'risk_thresholds': {
                'high_risk': 0.2,    # <20% probabilité conversion
                'medium_risk': 0.5,  # 20-50%
                'low_risk': 0.8      # >50%
            }
        }
    
    async def analyze_trial_user(self, user_id: str, user_data: Dict[str, Any]) -> TrialUser:
        """Analyse complète d'un utilisateur trial"""
        try:
            # Extraction des données utilisateur
            trial_start = datetime.fromisoformat(user_data['trial_start'])
            trial_end = datetime.fromisoformat(user_data['trial_end'])
            trial_duration = (trial_end - trial_start).days
            
            # Métriques d'engagement
            engagement_metrics = await self._calculate_engagement_metrics(user_id, user_data)
            
            # Signaux comportementaux
            behavioral_signals = await self._extract_behavioral_signals(user_id, user_data)
            
            # Prédiction de conversion
            conversion_probability = await self._predict_conversion_probability(user_id, user_data)
            
            # Facteurs de risque
            risk_factors = await self._identify_risk_factors(user_id, user_data, engagement_metrics)
            
            # Historique des interventions
            intervention_history = user_data.get('intervention_history', [])
            
            trial_user = TrialUser(
                user_id=user_id,
                trial_start=trial_start,
                trial_end=trial_end,
                trial_duration_days=trial_duration,
                plan_type=user_data.get('plan_type', 'standard'),
                creator_type=user_data.get('creator_type', 'general'),
                usage_data=user_data.get('usage_data', {}),
                engagement_metrics=engagement_metrics,
                behavioral_signals=behavioral_signals,
                intervention_history=intervention_history,
                conversion_probability=conversion_probability,
                risk_factors=risk_factors
            )
            
            # Stockage pour suivi
            self.trial_users[user_id] = trial_user
            
            logger.info(f"✅ Trial user analyzed: {user_id} (conversion probability: {conversion_probability:.2%})")
            return trial_user
            
        except Exception as e:
            logger.error(f"❌ Error analyzing trial user {user_id}: {e}")
            return None
    
    async def _calculate_engagement_metrics(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Calcule les métriques d'engagement"""
        try:
            usage_data = user_data.get('usage_data', {})
            trial_days = (datetime.now() - datetime.fromisoformat(user_data['trial_start'])).days
            
            metrics = {
                'daily_active_sessions': usage_data.get('total_sessions', 0) / max(trial_days, 1),
                'feature_adoption_rate': len(usage_data.get('features_used', [])) / 20,  # Sur 20 features possibles
                'content_creation_rate': usage_data.get('content_created', 0) / max(trial_days, 1),
                'collaboration_engagement': usage_data.get('collaboration_sessions', 0) / max(trial_days, 1),
                'platform_stickiness': usage_data.get('return_visits', 0) / max(trial_days, 1),
                'help_usage_rate': usage_data.get('help_requests', 0) / max(trial_days, 1),
                'profile_completion': usage_data.get('profile_completion_percent', 0) / 100,
                'social_connections': min(usage_data.get('connections_made', 0) / 10, 1.0)  # Normalisé sur 10
            }
            
            # Score global d'engagement
            weights = {
                'daily_active_sessions': 0.2,
                'feature_adoption_rate': 0.15,
                'content_creation_rate': 0.2,
                'collaboration_engagement': 0.15,
                'platform_stickiness': 0.1,
                'help_usage_rate': 0.05,
                'profile_completion': 0.1,
                'social_connections': 0.05
            }
            
            metrics['overall_engagement_score'] = sum(
                metrics[key] * weight for key, weight in weights.items()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating engagement metrics: {e}")
            return {}
    
    async def _extract_behavioral_signals(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les signaux comportementaux"""
        try:
            usage_data = user_data.get('usage_data', {})
            
            signals = {
                'time_to_first_action': usage_data.get('time_to_first_action_hours', 24),
                'peak_usage_hours': usage_data.get('peak_usage_hours', []),
                'feature_exploration_pattern': usage_data.get('feature_sequence', []),
                'session_duration_trend': usage_data.get('session_durations', []),
                'weekend_usage': usage_data.get('weekend_sessions', 0) > 0,
                'mobile_usage_ratio': usage_data.get('mobile_sessions', 0) / max(usage_data.get('total_sessions', 1), 1),
                'content_type_preference': usage_data.get('preferred_content_types', []),
                'collaboration_initiation': usage_data.get('initiated_collaborations', 0),
                'support_interaction': usage_data.get('support_tickets', 0) > 0,
                'billing_page_visits': usage_data.get('billing_page_visits', 0),
                'pricing_page_time': usage_data.get('pricing_page_seconds', 0),
                'comparison_research': usage_data.get('competitor_research_signals', False)
            }
            
            # Calcul de patterns avancés
            signals['usage_consistency'] = self._calculate_usage_consistency(usage_data.get('daily_sessions', []))
            signals['feature_depth'] = self._calculate_feature_depth(usage_data.get('feature_usage_details', {}))
            signals['conversion_intent'] = self._calculate_conversion_intent(signals)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error extracting behavioral signals: {e}")
            return {}
    
    def _calculate_usage_consistency(self, daily_sessions: List[int]) -> float:
        """Calcule la consistance d'usage"""
        if len(daily_sessions) < 3:
            return 0.0
        
        # Coefficient de variation inversé (plus faible = plus consistant)
        mean_sessions = np.mean(daily_sessions)
        if mean_sessions == 0:
            return 0.0
        
        cv = np.std(daily_sessions) / mean_sessions
        return max(0, 1 - cv)  # Inversé et normalisé
    
    def _calculate_feature_depth(self, feature_usage: Dict[str, Any]) -> float:
        """Calcule la profondeur d'utilisation des features"""
        if not feature_usage:
            return 0.0
        
        depth_scores = []
        for feature, usage_data in feature_usage.items():
            # Score basé sur durée et fréquence
            duration = usage_data.get('total_time_seconds', 0)
            frequency = usage_data.get('usage_count', 0)
            advanced_actions = usage_data.get('advanced_actions', 0)
            
            feature_depth = min(1.0, (duration / 3600 + frequency / 10 + advanced_actions / 5) / 3)
            depth_scores.append(feature_depth)
        
        return np.mean(depth_scores) if depth_scores else 0.0
    
    def _calculate_conversion_intent(self, signals: Dict[str, Any]) -> float:
        """Calcule l'intention de conversion"""
        intent_factors = {
            'billing_page_visits': signals.get('billing_page_visits', 0) * 0.3,
            'pricing_page_time': min(signals.get('pricing_page_time', 0) / 300, 1.0) * 0.2,  # Normalisé sur 5 min
            'comparison_research': 0.1 if signals.get('comparison_research', False) else 0,
            'feature_exploration': min(len(signals.get('feature_exploration_pattern', [])) / 10, 1.0) * 0.2,
            'collaboration_activity': min(signals.get('collaboration_initiation', 0) / 3, 1.0) * 0.2
        }
        
        return min(sum(intent_factors.values()), 1.0)
    
    async def _predict_conversion_probability(self, user_id: str, user_data: Dict[str, Any]) -> float:
        """Prédit la probabilité de conversion"""
        try:
            # Extraction des features ML
            features = await self._extract_ml_features(user_id, user_data)
            
            # Utilisation du modèle ML si disponible
            if 'conversion_predictor' in self.ml_models:
                scaler = self.ml_models.get('feature_scaler')
                model = self.ml_models['conversion_predictor']
                
                if scaler and model:
                    features_scaled = scaler.transform([features])
                    probability = model.predict_proba(features_scaled)[0][1]  # Probabilité classe positive
                    return min(max(probability, 0.0), 1.0)
            
            # Modèle heuristique en l'absence de ML entraîné
            return await self._heuristic_conversion_prediction(user_id, user_data)
            
        except Exception as e:
            logger.error(f"❌ Error predicting conversion probability: {e}")
            return 0.5  # Probabilité neutre par défaut
    
    async def _extract_ml_features(self, user_id: str, user_data: Dict[str, Any]) -> List[float]:
        """Extrait les features pour ML"""
        usage_data = user_data.get('usage_data', {})
        trial_days = (datetime.now() - datetime.fromisoformat(user_data['trial_start'])).days
        
        features = [
            trial_days,  # Jours depuis début trial
            usage_data.get('total_sessions', 0),
            usage_data.get('content_created', 0),
            usage_data.get('collaboration_sessions', 0),
            len(usage_data.get('features_used', [])),
            usage_data.get('profile_completion_percent', 0),
            usage_data.get('billing_page_visits', 0),
            usage_data.get('pricing_page_seconds', 0),
            usage_data.get('support_tickets', 0),
            usage_data.get('mobile_sessions', 0) / max(usage_data.get('total_sessions', 1), 1),
            1 if usage_data.get('weekend_sessions', 0) > 0 else 0,
            len(usage_data.get('peak_usage_hours', [])),
            usage_data.get('return_visits', 0),
            usage_data.get('connections_made', 0),
            usage_data.get('initiated_collaborations', 0)
        ]
        
        return features
    
    async def _heuristic_conversion_prediction(self, user_id: str, user_data: Dict[str, Any]) -> float:
        """Prédiction heuristique de conversion"""
        try:
            engagement_metrics = await self._calculate_engagement_metrics(user_id, user_data)
            behavioral_signals = await self._extract_behavioral_signals(user_id, user_data)
            
            # Facteurs positifs
            positive_factors = [
                engagement_metrics.get('overall_engagement_score', 0) * 0.4,
                behavioral_signals.get('conversion_intent', 0) * 0.3,
                behavioral_signals.get('usage_consistency', 0) * 0.1,
                behavioral_signals.get('feature_depth', 0) * 0.2
            ]
            
            # Facteurs négatifs
            negative_factors = [
                -0.1 if behavioral_signals.get('support_interaction', False) else 0,  # Support = potentiel problème
                -0.05 if behavioral_signals.get('time_to_first_action', 24) > 48 else 0  # Adoption lente
            ]
            
            base_probability = sum(positive_factors) + sum(negative_factors)
            
            # Ajustements par type de créateur
            creator_type = user_data.get('creator_type', 'general')
            type_adjustments = {
                'musician': 0.1,     # Généralement plus engagés
                'blogger': 0.05,     # Engagement modéré
                'photographer': 0.08, # Bon engagement visuel
                'general': 0.0
            }
            
            final_probability = base_probability + type_adjustments.get(creator_type, 0)
            return min(max(final_probability, 0.05), 0.95)  # Entre 5% et 95%
            
        except Exception as e:
            logger.error(f"❌ Error in heuristic conversion prediction: {e}")
            return 0.5
    
    async def _identify_risk_factors(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        engagement_metrics: Dict[str, float]
    ) -> List[str]:
        """Identifie les facteurs de risque de non-conversion"""
        risk_factors = []
        
        try:
            usage_data = user_data.get('usage_data', {})
            trial_days = (datetime.now() - datetime.fromisoformat(user_data['trial_start'])).days
            
            # Risques d'engagement
            if engagement_metrics.get('overall_engagement_score', 0) < 0.3:
                risk_factors.append("Engagement global faible")
            
            if engagement_metrics.get('daily_active_sessions', 0) < 0.5:
                risk_factors.append("Faible fréquence d'utilisation")
            
            if engagement_metrics.get('feature_adoption_rate', 0) < 0.2:
                risk_factors.append("Adoption limitée des fonctionnalités")
            
            # Risques comportementaux
            if usage_data.get('time_to_first_action_hours', 24) > 72:
                risk_factors.append("Activation tardive")
            
            if trial_days > 7 and usage_data.get('content_created', 0) == 0:
                risk_factors.append("Aucune création de contenu")
            
            if usage_data.get('profile_completion_percent', 0) < 50:
                risk_factors.append("Profil incomplet")
            
            # Risques d'intention
            if usage_data.get('billing_page_visits', 0) == 0 and trial_days > 10:
                risk_factors.append("Aucun intérêt pour les plans payants")
            
            if usage_data.get('support_tickets', 0) > 2:
                risk_factors.append("Problèmes techniques récurrents")
            
            # Risques temporels
            remaining_days = (datetime.fromisoformat(user_data['trial_end']) - datetime.now()).days
            if remaining_days < 3 and engagement_metrics.get('overall_engagement_score', 0) < 0.5:
                risk_factors.append("Fin de trial imminente avec engagement faible")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"❌ Error identifying risk factors: {e}")
            return []
    
    async def generate_conversion_predictions(self, user_ids: List[str]) -> List[ConversionPrediction]:
        """Génère des prédictions de conversion pour plusieurs utilisateurs"""
        try:
            predictions = []
            
            for user_id in user_ids:
                if user_id not in self.trial_users:
                    logger.warning(f"Trial user not found: {user_id}")
                    continue
                
                trial_user = self.trial_users[user_id]
                
                # Facteurs clés de conversion
                key_factors = await self._identify_key_conversion_factors(trial_user)
                
                # Interventions recommandées
                recommended_interventions = await self._recommend_interventions(trial_user)
                
                # Jour optimal de conversion
                optimal_day = await self._calculate_optimal_conversion_day(trial_user)
                
                # Niveau de probabilité
                probability_level = self._get_probability_level(trial_user.conversion_probability)
                
                prediction = ConversionPrediction(
                    user_id=user_id,
                    probability=trial_user.conversion_probability,
                    probability_level=probability_level,
                    key_factors=key_factors,
                    recommended_interventions=recommended_interventions,
                    optimal_conversion_day=optimal_day,
                    confidence_score=0.85,  # Score de confiance du modèle
                    prediction_timestamp=datetime.now()
                )
                
                predictions.append(prediction)
            
            logger.info(f"✅ Generated conversion predictions for {len(predictions)} users")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Error generating conversion predictions: {e}")
            return []
    
    async def _identify_key_conversion_factors(self, trial_user: TrialUser) -> List[str]:
        """Identifie les facteurs clés de conversion"""
        factors = []
        
        # Facteurs d'engagement
        if trial_user.engagement_metrics.get('overall_engagement_score', 0) > 0.7:
            factors.append("Engagement élevé")
        
        if trial_user.engagement_metrics.get('feature_adoption_rate', 0) > 0.6:
            factors.append("Bonne adoption des fonctionnalités")
        
        if trial_user.engagement_metrics.get('collaboration_engagement', 0) > 1.0:
            factors.append("Activité collaborative forte")
        
        # Facteurs comportementaux
        if trial_user.behavioral_signals.get('conversion_intent', 0) > 0.6:
            factors.append("Intention de conversion élevée")
        
        if trial_user.behavioral_signals.get('usage_consistency', 0) > 0.7:
            factors.append("Usage consistant")
        
        if trial_user.behavioral_signals.get('feature_depth', 0) > 0.5:
            factors.append("Utilisation approfondie des features")
        
        # Facteurs de timing
        current_day = (datetime.now() - trial_user.trial_start).days
        if 8 <= current_day <= 14:
            factors.append("Fenêtre de conversion optimale")
        
        return factors[:5]  # Top 5 facteurs
    
    async def _recommend_interventions(self, trial_user: TrialUser) -> List[str]:
        """Recommande des interventions personnalisées"""
        interventions = []
        
        current_day = (datetime.now() - trial_user.trial_start).days
        engagement_score = trial_user.engagement_metrics.get('overall_engagement_score', 0)
        conversion_probability = trial_user.conversion_probability
        
        # Interventions basées sur l'engagement et la probabilité
        if engagement_score > 0.7 and conversion_probability > 0.6:
            interventions.append("Email de conversion avec remise")
            interventions.append("Démonstration des fonctionnalités premium")
        
        elif engagement_score < 0.4:
            interventions.append("Programme d'onboarding personnalisé")
            interventions.append("Session de support individuel")
        
        elif 0.4 <= engagement_score <= 0.7:
            interventions.append("Déverrouillage temporaire de fonctionnalités premium")
            interventions.append("Invitation à des webinaires")
        
        # Interventions temporelles
        if current_day >= 10 and conversion_probability < 0.5:
            interventions.append("Extension d'essai avec objectifs")
        
        if current_day >= 7 and trial_user.behavioral_signals.get('billing_page_visits', 0) == 0:
            interventions.append("Notification pricing avec comparaison")
        
        # Interventions par type de créateur
        creator_type = trial_user.creator_type
        if creator_type == 'musician' and trial_user.usage_data.get('audio_uploads', 0) < 3:
            interventions.append("Tutorial audio avancé")
        
        elif creator_type == 'blogger' and trial_user.usage_data.get('seo_tool_usage', 0) == 0:
            interventions.append("Formation SEO personnalisée")
        
        return interventions[:3]  # Top 3 interventions
    
    async def _calculate_optimal_conversion_day(self, trial_user: TrialUser) -> int:
        """Calcule le jour optimal pour la conversion"""
        try:
            current_day = (datetime.now() - trial_user.trial_start).days
            remaining_days = trial_user.trial_duration_days - current_day
            
            # Fenêtres de conversion par type de créateur
            conversion_windows = self.optimization_rules['conversion_windows']
            
            # Facteurs de timing
            engagement_trend = self._calculate_engagement_trend(trial_user.usage_data)
            
            if trial_user.conversion_probability > 0.8:
                # Haute probabilité = conversion rapide
                return min(current_day + 2, trial_user.trial_duration_days - 2)
            
            elif trial_user.conversion_probability > 0.5:
                # Probabilité moyenne = fenêtre mid-trial
                optimal_window = conversion_windows['mid']
                return min(max(optimal_window[0], current_day + 1), optimal_window[1])
            
            else:
                # Faible probabilité = dernière chance
                return max(trial_user.trial_duration_days - 3, current_day + 1)
                
        except Exception as e:
            logger.error(f"❌ Error calculating optimal conversion day: {e}")
            return min(current_day + 3, trial_user.trial_duration_days - 1)
    
    def _calculate_engagement_trend(self, usage_data: Dict[str, Any]) -> str:
        """Calcule la tendance d'engagement"""
        daily_sessions = usage_data.get('daily_sessions', [])
        
        if len(daily_sessions) < 3:
            return 'insufficient_data'
        
        recent_sessions = daily_sessions[-3:]
        older_sessions = daily_sessions[:-3] if len(daily_sessions) > 3 else daily_sessions[:3]
        
        recent_avg = np.mean(recent_sessions)
        older_avg = np.mean(older_sessions)
        
        if recent_avg > older_avg * 1.2:
            return 'increasing'
        elif recent_avg < older_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_probability_level(self, probability: float) -> ConversionProbability:
        """Détermine le niveau de probabilité"""
        if probability >= 0.8:
            return ConversionProbability.VERY_HIGH
        elif probability >= 0.6:
            return ConversionProbability.HIGH
        elif probability >= 0.4:
            return ConversionProbability.MEDIUM
        elif probability >= 0.2:
            return ConversionProbability.LOW
        else:
            return ConversionProbability.VERY_LOW
    
    async def schedule_intervention(
        self,
        user_id: str,
        intervention_type: InterventionType,
        custom_content: Optional[Dict[str, Any]] = None
    ) -> str:
        """Programme une intervention"""
        try:
            if user_id not in self.trial_users:
                raise ValueError(f"Trial user not found: {user_id}")
            
            trial_user = self.trial_users[user_id]
            intervention_id = f"{user_id}_{intervention_type.value}_{int(datetime.now().timestamp())}"
            
            # Contenu de l'intervention
            if custom_content:
                content = custom_content
            else:
                # Recherche d'un template approprié
                template_key = self._find_appropriate_template(trial_user, intervention_type)
                content = self.intervention_templates.get(template_key, {}).get('content', {})
            
            # Programmation
            schedule_time = datetime.now() + timedelta(minutes=5)  # 5 minutes par défaut
            
            intervention = TrialIntervention(
                intervention_id=intervention_id,
                user_id=user_id,
                intervention_type=intervention_type,
                trigger_condition=f"Manual scheduling for {intervention_type.value}",
                content=content,
                scheduled_time=schedule_time,
                executed=False,
                execution_time=None,
                success_metrics={}
            )
            
            # Ajout à l'historique
            trial_user.intervention_history.append({
                'intervention_id': intervention_id,
                'type': intervention_type.value,
                'scheduled': schedule_time.isoformat(),
                'content': content
            })
            
            logger.info(f"✅ Intervention scheduled: {intervention_id} for user {user_id}")
            return intervention_id
            
        except Exception as e:
            logger.error(f"❌ Error scheduling intervention: {e}")
            return ""
    
    def _find_appropriate_template(self, trial_user: TrialUser, intervention_type: InterventionType) -> str:
        """Trouve le template d'intervention approprié"""
        engagement_score = trial_user.engagement_metrics.get('overall_engagement_score', 0)
        conversion_probability = trial_user.conversion_probability
        
        # Mapping basé sur profil utilisateur
        if engagement_score > 0.7 and conversion_probability > 0.6:
            return 'high_engagement_nudge'
        elif engagement_score < 0.4:
            return 'low_engagement_boost'
        elif intervention_type == InterventionType.DISCOUNT_OFFER:
            return 'conversion_window_offer'
        elif intervention_type == InterventionType.FEATURE_UNLOCK:
            return 'feature_discovery'
        else:
            return 'high_engagement_nudge'  # Template par défaut
    
    async def get_trial_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Récupère les analytics des essais gratuits"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filtrage des utilisateurs trial récents
            recent_trials = [
                user for user in self.trial_users.values()
                if user.trial_start >= cutoff_date
            ]
            
            if not recent_trials:
                return {'message': 'No trial data available for the specified period'}
            
            # Métriques générales
            total_trials = len(recent_trials)
            avg_conversion_probability = np.mean([user.conversion_probability for user in recent_trials])
            
            # Distribution par niveau de probabilité
            probability_distribution = {}
            for level in ConversionProbability:
                count = sum(1 for user in recent_trials if self._get_probability_level(user.conversion_probability) == level)
                probability_distribution[level.value] = count
            
            # Métriques par type de créateur
            creator_type_metrics = {}
            for user in recent_trials:
                creator_type = user.creator_type
                if creator_type not in creator_type_metrics:
                    creator_type_metrics[creator_type] = {
                        'count': 0,
                        'avg_probability': 0,
                        'avg_engagement': 0
                    }
                
                creator_type_metrics[creator_type]['count'] += 1
                creator_type_metrics[creator_type]['avg_probability'] += user.conversion_probability
                creator_type_metrics[creator_type]['avg_engagement'] += user.engagement_metrics.get('overall_engagement_score', 0)
            
            # Calcul des moyennes
            for creator_type in creator_type_metrics:
                count = creator_type_metrics[creator_type]['count']
                creator_type_metrics[creator_type]['avg_probability'] /= count
                creator_type_metrics[creator_type]['avg_engagement'] /= count
            
            # Facteurs de risque les plus fréquents
            all_risk_factors = []
            for user in recent_trials:
                all_risk_factors.extend(user.risk_factors)
            
            risk_factor_frequency = {}
            for factor in all_risk_factors:
                risk_factor_frequency[factor] = risk_factor_frequency.get(factor, 0) + 1
            
            # Top facteurs de risque
            top_risk_factors = sorted(risk_factor_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analytics = {
                'period_days': days,
                'total_trials': total_trials,
                'avg_conversion_probability': avg_conversion_probability,
                'probability_distribution': probability_distribution,
                'creator_type_metrics': creator_type_metrics,
                'top_risk_factors': dict(top_risk_factors),
                'summary': {
                    'high_probability_users': sum(1 for user in recent_trials if user.conversion_probability > 0.7),
                    'at_risk_users': sum(1 for user in recent_trials if len(user.risk_factors) > 2),
                    'avg_trial_duration': np.mean([user.trial_duration_days for user in recent_trials])
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting trial analytics: {e}")
            return {}
    
    async def train_conversion_model(self, training_data: pd.DataFrame) -> bool:
        """Entraîne le modèle de prédiction de conversion"""
        try:
            logger.info("🚀 Training conversion prediction model...")
            
            # Préparation des données
            features = training_data.drop(['user_id', 'converted'], axis=1)
            labels = training_data['converted']
            
            # Normalisation
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Entraînement Random Forest
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(features_scaled, labels)
            
            # Évaluation
            predictions = rf_model.predict(features_scaled)
            accuracy = accuracy_score(labels, predictions)
            precision = precision_score(labels, predictions)
            recall = recall_score(labels, predictions)
            
            # Sauvegarde des modèles
            self.ml_models['conversion_predictor'] = rf_model
            self.ml_models['feature_scaler'] = scaler
            
            logger.info(f"✅ Conversion model trained - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training conversion model: {e}")
            return False


# Instance globale
trial_optimization_system = TrialOptimizationSystem()

# Export des classes principales
__all__ = [
    'TrialOptimizationSystem',
    'TrialUser',
    'ConversionPrediction',
    'TrialIntervention',
    'TrialStatus',
    'ConversionProbability',
    'InterventionType',
    'trial_optimization_system'
]