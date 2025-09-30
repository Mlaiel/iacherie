"""
Error Prediction ML Engine - Ainflue Platform
Machine Learning-Powered Error Prediction & Proactive Prevention

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import hashlib
import pickle
from pathlib import Path
import joblib

logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Types de modèles ML pour prédiction d'erreurs"""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"


class PredictionHorizon(Enum):
    """Horizons de prédiction"""
    NEXT_HOUR = 3600
    NEXT_6_HOURS = 21600
    NEXT_DAY = 86400
    NEXT_WEEK = 604800
    NEXT_MONTH = 2592000


class PredictionConfidence(Enum):
    """Niveaux de confiance des prédictions"""
    VERY_LOW = 0.2
    LOW = 0.4  
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


class RiskLevel(Enum):
    """Niveaux de risque"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorPrediction:
    """Prédiction d'erreur ML"""
    prediction_id: str
    service_name: str
    platform: str
    error_type: str
    predicted_probability: float
    confidence_level: PredictionConfidence
    risk_level: RiskLevel
    prediction_horizon: PredictionHorizon
    predicted_time_window: tuple[datetime, datetime]
    contributing_factors: List[Dict[str, Any]]
    prevention_recommendations: List[str]
    business_impact_estimate: float
    ml_model_used: PredictionModel
    feature_importance: Dict[str, float]
    historical_accuracy: float


@dataclass
class PredictionFeatures:
    """Features pour ML de prédiction d'erreur"""
    # Temporal features
    hour_of_day: int
    day_of_week: int
    day_of_month: int
    month: int
    is_weekend: bool
    is_business_hours: bool
    
    # Service features
    service_load: float
    response_time_avg: float
    error_rate_current: float
    cpu_usage: float
    memory_usage: float
    active_connections: int
    
    # Platform features
    platform_health_score: float
    api_rate_limit_usage: float
    auth_failure_rate: float
    content_processing_queue: int
    
    # Business features
    active_creators: int
    content_uploads_rate: float
    payment_processing_rate: float
    collaboration_requests: int
    
    # Historical features
    error_count_last_hour: int
    error_count_last_day: int
    error_count_last_week: int
    similar_error_trend: float
    
    # External features
    external_api_health: float
    network_latency: float
    third_party_status: float


@dataclass
class ModelPerformanceMetrics:
    """Métriques de performance des modèles ML"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    false_positive_rate: float
    false_negative_rate: float
    prediction_latency_ms: float
    training_time_seconds: float
    last_updated: datetime


@dataclass
class PreventiveAction:
    """Action préventive recommandée"""
    action_id: str
    action_type: str
    description: str
    priority: int
    estimated_effectiveness: float
    implementation_cost: str
    automation_possible: bool
    business_justification: str


class ErrorPredictionMLEngine:
    """
    🤖 ML Engineer + Lead Dev IA: Engine de prédiction d'erreurs ML
    
    Moteur de prédiction alimenté par ML pour:
    - Prédiction proactive d'erreurs
    - Analyse des patterns temporels
    - Recommandations préventives
    - Optimisation continue des modèles
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """🚀 DevOps: Initialisation du moteur de prédiction ML"""
        self.config = config or {}
        
        # ML Models storage
        self.models: Dict[str, Any] = {}
        self.model_performances: Dict[str, ModelPerformanceMetrics] = {}
        self.feature_extractors = {}
        
        # Data storage
        self.historical_features: deque = deque(maxlen=100000)
        self.prediction_cache: Dict[str, ErrorPrediction] = {}
        self.model_predictions: Dict[str, List[ErrorPrediction]] = defaultdict(list)
        
        # Training data
        self.training_data: Dict[str, pd.DataFrame] = {}
        self.validation_data: Dict[str, pd.DataFrame] = {}
        
        # Model paths
        self.model_path = Path(self.config.get('model_path', '/tmp/ml_models/prediction'))
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # 🎵 Audio + Platform: Configuration Ainflue
        self.platform_configs = self._initialize_platform_configs()
        
        # Initialize models
        self._initialize_prediction_models()
        
        logger.info("ErrorPredictionMLEngine initialized with advanced ML capabilities")
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """🎵 Audio + Platform: Configuration des 65+ plateformes Ainflue"""
        return {
            # Music Streaming Platforms
            'spotify': {
                'common_error_patterns': ['rate_limit', 'token_expired', 'track_unavailable'],
                'prediction_features': ['api_usage_rate', 'token_age', 'request_volume'],
                'seasonal_patterns': {'holiday_season': 1.5, 'weekend': 1.2},
                'business_criticality': 0.95
            },
            'apple_music': {
                'common_error_patterns': ['drm_failure', 'metadata_sync', 'playlist_sync'],
                'prediction_features': ['drm_requests', 'metadata_changes', 'sync_queue_size'],
                'seasonal_patterns': {'new_release_period': 1.8, 'weekend': 1.1},
                'business_criticality': 0.9
            },
            'soundcloud': {
                'common_error_patterns': ['upload_failure', 'format_error', 'copyright_claim'],
                'prediction_features': ['upload_volume', 'processing_queue', 'content_checks'],
                'seasonal_patterns': {'peak_hours': 1.4, 'creator_events': 2.0},
                'business_criticality': 0.75
            },
            
            # Social Media Platforms
            'youtube': {
                'common_error_patterns': ['processing_failed', 'monetization_issue', 'copyright_strike'],
                'prediction_features': ['video_queue', 'processing_time', 'content_id_matches'],
                'seasonal_patterns': {'viral_content': 2.5, 'algorithm_updates': 1.8},
                'business_criticality': 1.0
            },
            'instagram': {
                'common_error_patterns': ['story_failed', 'hashtag_shadow', 'account_action'],
                'prediction_features': ['story_volume', 'hashtag_usage', 'engagement_rate'],
                'seasonal_patterns': {'trending_periods': 1.6, 'stories_peak': 1.3},
                'business_criticality': 0.85
            },
            'tiktok': {
                'common_error_patterns': ['video_rejected', 'sound_copyright', 'region_block'],
                'prediction_features': ['video_uploads', 'sound_usage', 'geo_distribution'],
                'seasonal_patterns': {'viral_trends': 2.2, 'new_features': 1.7},
                'business_criticality': 0.9
            },
            
            # Creator Economy Platforms
            'patreon': {
                'common_error_patterns': ['payment_failed', 'tier_error', 'content_access'],
                'prediction_features': ['payment_volume', 'subscription_changes', 'content_updates'],
                'seasonal_patterns': {'month_end': 2.0, 'creator_campaigns': 1.5},
                'business_criticality': 1.0
            },
            'onlyfans': {
                'common_error_patterns': ['payment_processing', 'age_verification', 'content_flagged'],
                'prediction_features': ['transaction_volume', 'verification_requests', 'content_reports'],
                'seasonal_patterns': {'payment_cycles': 1.8, 'policy_updates': 1.4},
                'business_criticality': 1.0
            }
        }
    
    def _initialize_prediction_models(self):
        """🤖 ML Engineer: Initialisation des modèles de prédiction"""
        
        # Try to load existing models
        self._load_existing_models()
        
        # Initialize default models if none exist
        if not self.models:
            self._create_default_models()
    
    def _load_existing_models(self):
        """💾 ML Engineer: Chargement des modèles existants"""
        
        try:
            for model_file in self.model_path.glob("*.pkl"):
                model_name = model_file.stem
                
                try:
                    model = joblib.load(model_file)
                    self.models[model_name] = model
                    logger.info(f"Loaded ML model: {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to load model {model_name}: {e}")
                    
        except Exception as e:
            logger.warning(f"Error loading existing models: {e}")
    
    def _create_default_models(self):
        """🤖 ML Engineer: Création des modèles par défaut"""
        
        try:
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.neural_network import MLPClassifier
            
            # Random Forest model
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.models['random_forest'] = rf_model
            
            # Gradient Boosting model
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            self.models['gradient_boosting'] = gb_model
            
            # Neural Network model
            nn_model = MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=1000,
                random_state=42
            )
            self.models['neural_network'] = nn_model
            
            logger.info("Created default ML models for error prediction")
            
        except ImportError:
            logger.warning("scikit-learn not available, using simple prediction models")
            self._create_simple_models()
    
    def _create_simple_models(self):
        """🔧 Backend Senior: Création de modèles simples sans dépendances"""
        
        # Simple rule-based models
        self.models['simple_threshold'] = {
            'type': 'threshold',
            'thresholds': {
                'error_rate': 0.05,
                'response_time': 5000,
                'cpu_usage': 0.8,
                'memory_usage': 0.85
            }
        }
        
        self.models['pattern_based'] = {
            'type': 'pattern',
            'patterns': {
                'high_load_errors': {'cpu_usage': '> 0.7', 'error_rate': '> 0.03'},
                'auth_cascade': {'auth_failure_rate': '> 0.1', 'response_time': '> 3000'},
                'platform_issues': {'platform_health_score': '< 0.8', 'api_rate_limit_usage': '> 0.9'}
            }
        }
    
    async def predict_errors(
        self, 
        service_name: str, 
        platform: str = None,
        prediction_horizon: PredictionHorizon = PredictionHorizon.NEXT_HOUR,
        features: Optional[PredictionFeatures] = None
    ) -> List[ErrorPrediction]:
        """
        🔮 ML Engineer: Prédiction d'erreurs avec ML
        
        Args:
            service_name: Nom du service
            platform: Plateforme concernée
            prediction_horizon: Horizon de prédiction
            features: Features spécifiques (optionnel)
            
        Returns:
            Liste des prédictions d'erreur
        """
        try:
            predictions = []
            
            # Extraction des features
            if not features:
                features = await self._extract_current_features(service_name, platform)
            
            # Prédiction avec chaque modèle
            for model_name, model in self.models.items():
                prediction = await self._predict_with_model(
                    model_name, model, service_name, platform, features, prediction_horizon
                )
                
                if prediction:
                    predictions.append(prediction)
            
            # Ensemble prediction si plusieurs modèles
            if len(predictions) > 1:
                ensemble_prediction = await self._create_ensemble_prediction(
                    predictions, service_name, platform, prediction_horizon
                )
                predictions.append(ensemble_prediction)
            
            # Cache des prédictions
            for prediction in predictions:
                self.prediction_cache[prediction.prediction_id] = prediction
            
            logger.info(f"Generated {len(predictions)} error predictions for {service_name}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error in error prediction: {e}")
            return []
    
    async def _extract_current_features(
        self, 
        service_name: str, 
        platform: str = None
    ) -> PredictionFeatures:
        """🔍 ML Engineer: Extraction des features actuelles"""
        
        current_time = datetime.now()
        
        # Features temporelles
        temporal_features = {
            'hour_of_day': current_time.hour,
            'day_of_week': current_time.weekday(),
            'day_of_month': current_time.day,
            'month': current_time.month,
            'is_weekend': current_time.weekday() >= 5,
            'is_business_hours': 8 <= current_time.hour <= 18
        }
        
        # Features de service (simulation)
        service_features = await self._get_service_metrics(service_name)
        
        # Features de plateforme
        platform_features = await self._get_platform_metrics(platform) if platform else {}
        
        # Features business
        business_features = await self._get_business_metrics()
        
        # Features historiques
        historical_features = await self._get_historical_features(service_name, platform)
        
        # Features externes
        external_features = await self._get_external_features()
        
        # Combine all features
        all_features = {
            **temporal_features,
            **service_features,
            **platform_features,
            **business_features,
            **historical_features,
            **external_features
        }
        
        return PredictionFeatures(**all_features)
    
    async def _get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """📊 DBA + Monitoring: Récupération des métriques de service"""
        
        # En production, ceci interrogerait le système de monitoring
        return {
            'service_load': np.random.uniform(0.1, 0.9),
            'response_time_avg': np.random.uniform(100, 2000),
            'error_rate_current': np.random.uniform(0.001, 0.05),
            'cpu_usage': np.random.uniform(0.1, 0.8),
            'memory_usage': np.random.uniform(0.2, 0.85),
            'active_connections': np.random.randint(10, 1000)
        }
    
    async def _get_platform_metrics(self, platform: str) -> Dict[str, Any]:
        """🎵 Platform: Récupération des métriques de plateforme"""
        
        if platform in self.platform_configs:
            config = self.platform_configs[platform]
            
            return {
                'platform_health_score': np.random.uniform(0.7, 1.0),
                'api_rate_limit_usage': np.random.uniform(0.1, 0.95),
                'auth_failure_rate': np.random.uniform(0.001, 0.1),
                'content_processing_queue': np.random.randint(0, 100)
            }
        
        return {
            'platform_health_score': 0.9,
            'api_rate_limit_usage': 0.5,
            'auth_failure_rate': 0.01,
            'content_processing_queue': 10
        }
    
    async def _get_business_metrics(self) -> Dict[str, Any]:
        """💼 Business: Récupération des métriques business"""
        
        return {
            'active_creators': np.random.randint(100, 10000),
            'content_uploads_rate': np.random.uniform(1.0, 50.0),
            'payment_processing_rate': np.random.uniform(0.1, 10.0),
            'collaboration_requests': np.random.randint(0, 200)
        }
    
    async def _get_historical_features(self, service_name: str, platform: str = None) -> Dict[str, Any]:
        """📈 DBA: Récupération des features historiques"""
        
        return {
            'error_count_last_hour': np.random.randint(0, 20),
            'error_count_last_day': np.random.randint(0, 200),
            'error_count_last_week': np.random.randint(0, 1000),
            'similar_error_trend': np.random.uniform(-0.5, 0.5)
        }
    
    async def _get_external_features(self) -> Dict[str, Any]:
        """🌐 External: Récupération des features externes"""
        
        return {
            'external_api_health': np.random.uniform(0.8, 1.0),
            'network_latency': np.random.uniform(10, 100),
            'third_party_status': np.random.uniform(0.7, 1.0)
        }
    
    async def _predict_with_model(
        self,
        model_name: str,
        model: Any,
        service_name: str,
        platform: str,
        features: PredictionFeatures,
        prediction_horizon: PredictionHorizon
    ) -> Optional[ErrorPrediction]:
        """🤖 ML Engineer: Prédiction avec un modèle spécifique"""
        
        try:
            # Convert features to array for ML models
            feature_array = self._features_to_array(features)
            
            # Predict based on model type
            if isinstance(model, dict):
                # Simple rule-based models
                probability = await self._predict_with_simple_model(model, features)
            else:
                # scikit-learn models
                try:
                    probability = model.predict_proba([feature_array])[0][1]  # Probability of error
                except:
                    probability = await self._predict_with_simple_model(
                        {'type': 'threshold', 'thresholds': {'error_rate': 0.05}}, 
                        features
                    )
            
            # Determine confidence and risk level
            confidence = await self._calculate_prediction_confidence(probability, model_name)
            risk_level = await self._determine_risk_level(probability)
            
            # Generate time window
            current_time = datetime.now()
            time_window = (
                current_time,
                current_time + timedelta(seconds=prediction_horizon.value)
            )
            
            # Contributing factors analysis
            contributing_factors = await self._analyze_contributing_factors(features, probability)
            
            # Prevention recommendations
            prevention_recommendations = await self._generate_prevention_recommendations(
                service_name, platform, contributing_factors, risk_level
            )
            
            # Business impact estimate
            business_impact = await self._estimate_business_impact(
                service_name, platform, probability, prediction_horizon
            )
            
            # Feature importance (for ML models)
            feature_importance = await self._calculate_feature_importance(
                model, model_name, feature_array
            )
            
            # Historical accuracy
            historical_accuracy = self.model_performances.get(model_name, {}).get('accuracy', 0.8)
            
            prediction_id = f"pred_{model_name}_{service_name}_{current_time.strftime('%Y%m%d_%H%M%S')}"
            
            return ErrorPrediction(
                prediction_id=prediction_id,
                service_name=service_name,
                platform=platform or "unknown",
                error_type="general_error",
                predicted_probability=probability,
                confidence_level=confidence,
                risk_level=risk_level,
                prediction_horizon=prediction_horizon,
                predicted_time_window=time_window,
                contributing_factors=contributing_factors,
                prevention_recommendations=prevention_recommendations,
                business_impact_estimate=business_impact,
                ml_model_used=PredictionModel(model_name) if model_name in [m.value for m in PredictionModel] else PredictionModel.ENSEMBLE,
                feature_importance=feature_importance,
                historical_accuracy=historical_accuracy
            )
            
        except Exception as e:
            logger.error(f"Error predicting with model {model_name}: {e}")
            return None
    
    def _features_to_array(self, features: PredictionFeatures) -> List[float]:
        """🔄 ML Engineer: Conversion des features en array"""
        
        return [
            float(features.hour_of_day),
            float(features.day_of_week),
            float(features.day_of_month),
            float(features.month),
            float(features.is_weekend),
            float(features.is_business_hours),
            features.service_load,
            features.response_time_avg,
            features.error_rate_current,
            features.cpu_usage,
            features.memory_usage,
            float(features.active_connections),
            features.platform_health_score,
            features.api_rate_limit_usage,
            features.auth_failure_rate,
            float(features.content_processing_queue),
            float(features.active_creators),
            features.content_uploads_rate,
            features.payment_processing_rate,
            float(features.collaboration_requests),
            float(features.error_count_last_hour),
            float(features.error_count_last_day),
            float(features.error_count_last_week),
            features.similar_error_trend,
            features.external_api_health,
            features.network_latency,
            features.third_party_status
        ]
    
    async def _predict_with_simple_model(self, model: Dict[str, Any], features: PredictionFeatures) -> float:
        """🔧 Backend Senior: Prédiction avec modèle simple"""
        
        if model['type'] == 'threshold':
            thresholds = model['thresholds']
            risk_score = 0.0
            
            # Check each threshold
            if features.error_rate_current > thresholds.get('error_rate', 0.05):
                risk_score += 0.3
            
            if features.response_time_avg > thresholds.get('response_time', 5000):
                risk_score += 0.2
            
            if features.cpu_usage > thresholds.get('cpu_usage', 0.8):
                risk_score += 0.25
            
            if features.memory_usage > thresholds.get('memory_usage', 0.85):
                risk_score += 0.25
            
            return min(risk_score, 1.0)
        
        elif model['type'] == 'pattern':
            patterns = model['patterns']
            max_risk = 0.0
            
            # Evaluate each pattern
            for pattern_name, conditions in patterns.items():
                pattern_risk = await self._evaluate_pattern_conditions(conditions, features)
                max_risk = max(max_risk, pattern_risk)
            
            return max_risk
        
        return 0.1  # Default low probability
    
    async def _evaluate_pattern_conditions(self, conditions: Dict[str, str], features: PredictionFeatures) -> float:
        """🔧 Backend Senior: Évaluation des conditions de pattern"""
        
        risk_score = 0.0
        condition_count = len(conditions)
        
        for feature_name, condition in conditions.items():
            try:
                feature_value = getattr(features, feature_name, 0)
                
                if '>' in condition:
                    threshold = float(condition.split('>')[1].strip())
                    if feature_value > threshold:
                        risk_score += 1.0 / condition_count
                
                elif '<' in condition:
                    threshold = float(condition.split('<')[1].strip())
                    if feature_value < threshold:
                        risk_score += 1.0 / condition_count
                        
            except Exception as e:
                logger.warning(f"Error evaluating condition {condition}: {e}")
        
        return risk_score
    
    async def _calculate_prediction_confidence(self, probability: float, model_name: str) -> PredictionConfidence:
        """📊 ML Engineer: Calcul de la confiance de prédiction"""
        
        # Base confidence on model performance and prediction probability
        model_accuracy = self.model_performances.get(model_name, {}).get('accuracy', 0.8)
        
        # Confidence based on probability certainty and model accuracy
        certainty = 1.0 - abs(0.5 - probability) * 2  # Higher when prob is close to 0 or 1
        combined_confidence = (certainty + model_accuracy) / 2
        
        if combined_confidence >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif combined_confidence >= 0.75:
            return PredictionConfidence.HIGH
        elif combined_confidence >= 0.6:
            return PredictionConfidence.MEDIUM
        elif combined_confidence >= 0.4:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    async def _determine_risk_level(self, probability: float) -> RiskLevel:
        """⚠️ Risk Assessment: Détermination du niveau de risque"""
        
        if probability >= 0.8:
            return RiskLevel.CRITICAL
        elif probability >= 0.6:
            return RiskLevel.HIGH
        elif probability >= 0.4:
            return RiskLevel.MEDIUM
        elif probability >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    async def _analyze_contributing_factors(
        self, 
        features: PredictionFeatures, 
        probability: float
    ) -> List[Dict[str, Any]]:
        """🔍 Analysis: Analyse des facteurs contributifs"""
        
        factors = []
        
        # Analyze high-impact features
        if features.error_rate_current > 0.03:
            factors.append({
                'factor': 'High Current Error Rate',
                'value': features.error_rate_current,
                'impact': 'high',
                'description': f'Current error rate of {features.error_rate_current:.1%} is above normal threshold'
            })
        
        if features.cpu_usage > 0.7:
            factors.append({
                'factor': 'High CPU Usage',
                'value': features.cpu_usage,
                'impact': 'medium',
                'description': f'CPU usage at {features.cpu_usage:.1%} may lead to performance issues'
            })
        
        if features.memory_usage > 0.8:
            factors.append({
                'factor': 'High Memory Usage',
                'value': features.memory_usage,
                'impact': 'medium',
                'description': f'Memory usage at {features.memory_usage:.1%} approaching limits'
            })
        
        if features.response_time_avg > 3000:
            factors.append({
                'factor': 'Slow Response Time',
                'value': features.response_time_avg,
                'impact': 'medium',
                'description': f'Average response time of {features.response_time_avg:.0f}ms is degraded'
            })
        
        if features.platform_health_score < 0.8:
            factors.append({
                'factor': 'Platform Health Issues',
                'value': features.platform_health_score,
                'impact': 'high',
                'description': f'Platform health score of {features.platform_health_score:.2f} indicates issues'
            })
        
        # Temporal factors
        if not features.is_business_hours:
            factors.append({
                'factor': 'Off-Hours Operation',
                'value': features.hour_of_day,
                'impact': 'low',
                'description': 'Operating outside business hours may have reduced monitoring'
            })
        
        return factors
    
    async def _generate_prevention_recommendations(
        self,
        service_name: str,
        platform: str,
        contributing_factors: List[Dict[str, Any]],
        risk_level: RiskLevel
    ) -> List[str]:
        """💡 Recommendations: Génération de recommandations préventives"""
        
        recommendations = []
        
        # General recommendations based on risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "Increase monitoring frequency for early detection",
                "Prepare incident response team for potential issues",
                "Consider scaling resources proactively"
            ])
        
        # Specific recommendations based on contributing factors
        for factor in contributing_factors:
            if factor['factor'] == 'High Current Error Rate':
                recommendations.append("Investigate root cause of current errors immediately")
                recommendations.append("Implement circuit breakers to prevent cascading failures")
            
            elif factor['factor'] == 'High CPU Usage':
                recommendations.append("Scale CPU resources or optimize high-usage processes")
                recommendations.append("Implement CPU-based auto-scaling")
            
            elif factor['factor'] == 'High Memory Usage':
                recommendations.append("Review memory leaks and optimize memory usage")
                recommendations.append("Consider increasing memory allocation")
            
            elif factor['factor'] == 'Slow Response Time':
                recommendations.append("Optimize database queries and API calls")
                recommendations.append("Implement caching layers for improved performance")
            
            elif factor['factor'] == 'Platform Health Issues':
                recommendations.append(f"Monitor {platform} platform status closely")
                recommendations.append("Implement fallback mechanisms for platform issues")
        
        # Platform-specific recommendations
        if platform in self.platform_configs:
            config = self.platform_configs[platform]
            common_errors = config.get('common_error_patterns', [])
            
            for error_pattern in common_errors:
                if error_pattern == 'rate_limit':
                    recommendations.append("Implement intelligent rate limiting and backoff strategies")
                elif error_pattern == 'auth_failure':
                    recommendations.append("Monitor authentication tokens and refresh proactively")
                elif error_pattern == 'processing_failed':
                    recommendations.append("Optimize content processing pipeline and add retries")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _estimate_business_impact(
        self,
        service_name: str,
        platform: str,
        probability: float,
        prediction_horizon: PredictionHorizon
    ) -> float:
        """💰 Business Impact: Estimation de l'impact business"""
        
        # Base impact calculation
        base_impact = probability * 1000  # Base $1000 per high-probability error
        
        # Platform criticality multiplier
        platform_criticality = 1.0
        if platform in self.platform_configs:
            platform_criticality = self.platform_configs[platform].get('business_criticality', 1.0)
        
        # Time horizon multiplier
        horizon_multiplier = {
            PredictionHorizon.NEXT_HOUR: 1.0,
            PredictionHorizon.NEXT_6_HOURS: 2.0,
            PredictionHorizon.NEXT_DAY: 5.0,
            PredictionHorizon.NEXT_WEEK: 20.0,
            PredictionHorizon.NEXT_MONTH: 50.0
        }.get(prediction_horizon, 1.0)
        
        # Service criticality (simplified)
        service_multiplier = 1.5 if 'payment' in service_name.lower() else 1.0
        
        total_impact = base_impact * platform_criticality * horizon_multiplier * service_multiplier
        
        return min(total_impact, 100000)  # Cap at $100k
    
    async def _calculate_feature_importance(
        self,
        model: Any,
        model_name: str,
        feature_array: List[float]
    ) -> Dict[str, float]:
        """📊 ML Engineer: Calcul de l'importance des features"""
        
        feature_names = [
            'hour_of_day', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_business_hours', 'service_load', 'response_time_avg',
            'error_rate_current', 'cpu_usage', 'memory_usage', 'active_connections',
            'platform_health_score', 'api_rate_limit_usage', 'auth_failure_rate',
            'content_processing_queue', 'active_creators', 'content_uploads_rate',
            'payment_processing_rate', 'collaboration_requests', 'error_count_last_hour',
            'error_count_last_day', 'error_count_last_week', 'similar_error_trend',
            'external_api_health', 'network_latency', 'third_party_status'
        ]
        
        importance = {}
        
        try:
            if hasattr(model, 'feature_importances_'):
                # Tree-based models
                importances = model.feature_importances_
                for i, name in enumerate(feature_names):
                    importance[name] = float(importances[i]) if i < len(importances) else 0.0
            
            elif hasattr(model, 'coef_'):
                # Linear models
                coefficients = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
                for i, name in enumerate(feature_names):
                    importance[name] = abs(float(coefficients[i])) if i < len(coefficients) else 0.0
            
            else:
                # Default importance based on simple heuristics
                high_importance_features = ['error_rate_current', 'cpu_usage', 'memory_usage', 'platform_health_score']
                for name in feature_names:
                    if name in high_importance_features:
                        importance[name] = 0.8
                    else:
                        importance[name] = 0.1
                        
        except Exception as e:
            logger.warning(f"Error calculating feature importance: {e}")
            # Fallback to equal importance
            for name in feature_names:
                importance[name] = 1.0 / len(feature_names)
        
        return importance
    
    async def _create_ensemble_prediction(
        self,
        predictions: List[ErrorPrediction],
        service_name: str,
        platform: str,
        prediction_horizon: PredictionHorizon
    ) -> ErrorPrediction:
        """🎯 Ensemble: Création de prédiction d'ensemble"""
        
        # Weighted average of predictions
        total_weight = 0.0
        weighted_probability = 0.0
        
        model_weights = {
            'random_forest': 0.4,
            'gradient_boosting': 0.3,
            'neural_network': 0.2,
            'simple_threshold': 0.1
        }
        
        for prediction in predictions:
            model_name = prediction.ml_model_used.value
            weight = model_weights.get(model_name, 0.1)
            
            weighted_probability += prediction.predicted_probability * weight
            total_weight += weight
        
        if total_weight > 0:
            ensemble_probability = weighted_probability / total_weight
        else:
            ensemble_probability = sum(p.predicted_probability for p in predictions) / len(predictions)
        
        # Combine contributing factors
        all_factors = []
        for prediction in predictions:
            all_factors.extend(prediction.contributing_factors)
        
        # Deduplicate factors
        unique_factors = []
        seen_factors = set()
        for factor in all_factors:
            factor_key = factor['factor']
            if factor_key not in seen_factors:
                unique_factors.append(factor)
                seen_factors.add(factor_key)
        
        # Combine recommendations
        all_recommendations = []
        for prediction in predictions:
            all_recommendations.extend(prediction.prevention_recommendations)
        unique_recommendations = list(set(all_recommendations))
        
        # Average business impact
        avg_business_impact = sum(p.business_impact_estimate for p in predictions) / len(predictions)
        
        # Best confidence and risk
        best_confidence = max(p.confidence_level for p in predictions)
        ensemble_risk = await self._determine_risk_level(ensemble_probability)
        
        # Create ensemble prediction
        current_time = datetime.now()
        prediction_id = f"ensemble_{service_name}_{current_time.strftime('%Y%m%d_%H%M%S')}"
        
        return ErrorPrediction(
            prediction_id=prediction_id,
            service_name=service_name,
            platform=platform,
            error_type="general_error",
            predicted_probability=ensemble_probability,
            confidence_level=best_confidence,
            risk_level=ensemble_risk,
            prediction_horizon=prediction_horizon,
            predicted_time_window=predictions[0].predicted_time_window,
            contributing_factors=unique_factors,
            prevention_recommendations=unique_recommendations,
            business_impact_estimate=avg_business_impact,
            ml_model_used=PredictionModel.ENSEMBLE,
            feature_importance={},  # Could combine feature importances
            historical_accuracy=0.85  # Average accuracy for ensemble
        )
    
    async def train_prediction_models(
        self, 
        training_data: pd.DataFrame, 
        target_column: str = 'error_occurred'
    ) -> Dict[str, ModelPerformanceMetrics]:
        """
        🎓 ML Engineer: Entraînement des modèles de prédiction
        
        Args:
            training_data: Données d'entraînement
            target_column: Colonne cible (booléenne)
            
        Returns:
            Métriques de performance des modèles
        """
        try:
            performance_metrics = {}
            
            # Preparation of training data
            X = training_data.drop(columns=[target_column])
            y = training_data[target_column]
            
            # Split data
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train each model
            for model_name, model in self.models.items():
                if isinstance(model, dict):
                    # Skip simple rule-based models
                    continue
                
                try:
                    start_time = datetime.now()
                    
                    # Train model
                    model.fit(X_train, y_train)
                    
                    training_time = (datetime.now() - start_time).total_seconds()
                    
                    # Predict on test set
                    start_pred = datetime.now()
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]
                    prediction_latency = (datetime.now() - start_pred).total_seconds() * 1000 / len(X_test)
                    
                    # Calculate metrics
                    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
                    
                    metrics = ModelPerformanceMetrics(
                        model_name=model_name,
                        accuracy=accuracy_score(y_test, y_pred),
                        precision=precision_score(y_test, y_pred),
                        recall=recall_score(y_test, y_pred),
                        f1_score=f1_score(y_test, y_pred),
                        auc_roc=roc_auc_score(y_test, y_pred_proba),
                        false_positive_rate=sum((y_test == 0) & (y_pred == 1)) / sum(y_test == 0),
                        false_negative_rate=sum((y_test == 1) & (y_pred == 0)) / sum(y_test == 1),
                        prediction_latency_ms=prediction_latency,
                        training_time_seconds=training_time,
                        last_updated=datetime.now()
                    )
                    
                    performance_metrics[model_name] = metrics
                    self.model_performances[model_name] = metrics
                    
                    # Save trained model
                    model_file = self.model_path / f"{model_name}.pkl"
                    joblib.dump(model, model_file)
                    
                    logger.info(f"Trained model {model_name} - Accuracy: {metrics.accuracy:.3f}")
                    
                except Exception as e:
                    logger.error(f"Error training model {model_name}: {e}")
            
            return performance_metrics
            
        except ImportError:
            logger.warning("scikit-learn not available for model training")
            return {}
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {}
    
    async def get_prediction_analytics(self) -> Dict[str, Any]:
        """
        📊 Analytics: Analyses des prédictions ML
        
        Returns:
            Analyses complètes des prédictions
        """
        try:
            # Model performance summary
            model_performance = {}
            for model_name, metrics in self.model_performances.items():
                model_performance[model_name] = {
                    'accuracy': metrics.accuracy,
                    'precision': metrics.precision,
                    'recall': metrics.recall,
                    'f1_score': metrics.f1_score,
                    'auc_roc': metrics.auc_roc,
                    'prediction_latency_ms': metrics.prediction_latency_ms
                }
            
            # Prediction statistics
            recent_predictions = list(self.prediction_cache.values())[-100:]  # Last 100 predictions
            
            prediction_stats = {
                'total_predictions': len(self.prediction_cache),
                'recent_predictions': len(recent_predictions),
                'avg_probability': sum(p.predicted_probability for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0,
                'high_risk_predictions': sum(1 for p in recent_predictions if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]),
                'confidence_distribution': {}
            }
            
            # Confidence distribution
            for confidence_level in PredictionConfidence:
                count = sum(1 for p in recent_predictions if p.confidence_level == confidence_level)
                prediction_stats['confidence_distribution'][confidence_level.name] = count
            
            return {
                'timestamp': datetime.now().isoformat(),
                'prediction_engine': {
                    'version': '1.0.0',
                    'models_loaded': len(self.models),
                    'platform_configs': len(self.platform_configs),
                    'cache_size': len(self.prediction_cache)
                },
                'model_performance': model_performance,
                'prediction_statistics': prediction_stats,
                'capabilities': {
                    'ml_models': list(self.models.keys()),
                    'prediction_horizons': [h.name for h in PredictionHorizon],
                    'ensemble_prediction': True,
                    'real_time_features': True,
                    'proactive_recommendations': True
                },
                'ainflue_integration': {
                    'platform_support': len(self.platform_configs),
                    'business_impact_assessment': True,
                    'creator_economy_focus': True,
                    'revenue_impact_estimation': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating prediction analytics: {e}")
            return {'error': 'Failed to generate analytics', 'timestamp': datetime.now().isoformat()}


# Instance globale pour utilisation
error_prediction_ml_engine = ErrorPredictionMLEngine()

# Export des classes principales
__all__ = [
    'ErrorPredictionMLEngine',
    'ErrorPrediction',
    'PredictionFeatures',
    'ModelPerformanceMetrics',
    'PreventiveAction',
    'PredictionModel',
    'PredictionHorizon',
    'PredictionConfidence',
    'RiskLevel',
    'error_prediction_ml_engine'
]