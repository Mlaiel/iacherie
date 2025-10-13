"""
Error Prediction Machine Learning Engine - Enterprise Creator Economy Platform
Advanced ML engine for predicting and preventing errors in creator workflows

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
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
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Types de modèles prédiction"""
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES_FORECAST = "time_series_forecast"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ENSEMBLE = "ensemble"
    NEURAL_NETWORK = "neural_network"


class PredictionConfidence(Enum):
    """Niveaux confiance prédiction"""
    VERY_LOW = "very_low"     # 0-20%
    LOW = "low"               # 20-40%
    MEDIUM = "medium"         # 40-60%
    HIGH = "high"             # 60-80%
    VERY_HIGH = "very_high"   # 80-100%


class ErrorRiskLevel(Enum):
    """Niveaux risque erreur"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FeatureVector:
    """Vecteur caractéristiques pour ML"""
    creator_id: str
    timestamp: datetime
    features: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorPrediction:
    """Prédiction erreur ML"""
    prediction_id: str
    creator_id: str
    predicted_error_type: str
    probability: float
    confidence: PredictionConfidence
    risk_level: ErrorRiskLevel
    time_window_hours: int
    contributing_factors: List[str]
    prevention_actions: List[str]
    model_used: PredictionModel
    feature_importance: Dict[str, float]
    timestamp: datetime


@dataclass
class ModelPerformance:
    """Performance modèle ML"""
    model_id: str
    model_type: PredictionModel
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    last_trained: datetime
    prediction_count: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int


class ErrorPredictionMachineLearningEngine:
    """
    🧠 MOTEUR ML PRÉDICTION ERREURS ENTERPRISE
    
    Architecture ML Backend Senior avec:
    - Prédiction erreurs proactive intelligente
    - Détection anomalies temps réel
    - Modèles apprentissage adaptatifs
    - Optimisation prévention erreurs
    """
    
    def __init__(self):
        """Initialize Error Prediction Machine Learning Engine"""
        self.ml_models: Dict[str, Dict[str, Any]] = {}
        self.feature_vectors: Dict[str, List[FeatureVector]] = defaultdict(list)
        self.predictions: Dict[str, List[ErrorPrediction]] = defaultdict(list)
        self.model_performance: Dict[str, ModelPerformance] = {}
        self.training_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.anomaly_baselines: Dict[str, Dict[str, float]] = {}
        self.prediction_cache: Dict[str, Any] = {}
        
        # Configuration moteur ML
        self.config = {
            'max_feature_history': 10000,
            'training_batch_size': 100,
            'model_retrain_interval_hours': 24,
            'prediction_horizon_hours': 72,
            'anomaly_threshold': 2.0,  # Standard deviations
            'min_training_samples': 50,
            'feature_importance_threshold': 0.1,
            'prediction_confidence_threshold': 0.6,
            'real_time_prediction': True,
            'auto_model_improvement': True
        }
        
        # Initialize feature extractors
        self.feature_extractors = {
            'temporal': self._extract_temporal_features,
            'behavioral': self._extract_behavioral_features,
            'performance': self._extract_performance_features,
            'contextual': self._extract_contextual_features
        }
        
        # Initialize models
        self._initialize_ml_models()
        
        logger.info("Error Prediction Machine Learning Engine initialized")
    
    def _initialize_ml_models(self):
        """Initialize ML models"""
        try:
            # Initialize basic models
            model_configs = {
                'anomaly_detector': {
                    'type': PredictionModel.ANOMALY_DETECTION,
                    'window_size': 24,  # hours
                    'sensitivity': 0.95,
                    'baseline_period_hours': 168  # 7 days
                },
                'error_classifier': {
                    'type': PredictionModel.CLASSIFICATION,
                    'classes': ['upload_error', 'payment_error', 'processing_error', 'engagement_error'],
                    'feature_count': 20
                },
                'time_series_predictor': {
                    'type': PredictionModel.TIME_SERIES_FORECAST,
                    'forecast_horizon': 72,  # hours
                    'seasonal_periods': [24, 168]  # daily, weekly
                },
                'ensemble_predictor': {
                    'type': PredictionModel.ENSEMBLE,
                    'base_models': ['anomaly_detector', 'error_classifier', 'time_series_predictor'],
                    'voting_strategy': 'weighted'
                }
            }
            
            for model_id, config in model_configs.items():
                self.ml_models[model_id] = {
                    'config': config,
                    'trained': False,
                    'last_training': None,
                    'predictions_made': 0,
                    'model_data': {}
                }
                
                # Initialize performance tracking
                self.model_performance[model_id] = ModelPerformance(
                    model_id=model_id,
                    model_type=config['type'],
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    training_samples=0,
                    last_trained=datetime.utcnow(),
                    prediction_count=0,
                    true_positives=0,
                    false_positives=0,
                    true_negatives=0,
                    false_negatives=0
                )
                
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    async def extract_features(self,
                              creator_id: str,
                              context_data: Dict[str, Any],
                              feature_types: Optional[List[str]] = None) -> FeatureVector:
        """
        Extract features for ML prediction
        
        Args:
            creator_id: ID créateur
            context_data: Données contexte
            feature_types: Types features à extraire
            
        Returns:
            Feature vector
        """
        try:
            if feature_types is None:
                feature_types = list(self.feature_extractors.keys())
            
            features = {}
            metadata = {
                'extraction_time': datetime.utcnow().isoformat(),
                'feature_types': feature_types
            }
            
            # Extract features using registered extractors
            for feature_type in feature_types:
                if feature_type in self.feature_extractors:
                    extractor = self.feature_extractors[feature_type]
                    type_features = await extractor(creator_id, context_data)
                    features.update(type_features)
            
            # Create feature vector
            feature_vector = FeatureVector(
                creator_id=creator_id,
                timestamp=datetime.utcnow(),
                features=features,
                metadata=metadata
            )
            
            # Store feature vector
            self.feature_vectors[creator_id].append(feature_vector)
            
            # Maintain history limit
            if len(self.feature_vectors[creator_id]) > self.config['max_feature_history']:
                self.feature_vectors[creator_id] = self.feature_vectors[creator_id][-self.config['max_feature_history']:]
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            raise
    
    async def _extract_temporal_features(self,
                                       creator_id: str,
                                       context_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract temporal features"""
        try:
            now = datetime.utcnow()
            features = {}
            
            # Time-based features
            features['hour_of_day'] = now.hour / 23.0
            features['day_of_week'] = now.weekday() / 6.0
            features['day_of_month'] = now.day / 31.0
            features['month_of_year'] = now.month / 12.0
            
            # Activity timing features
            last_activity = context_data.get('last_activity_time')
            if last_activity:
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)
                
                time_since_activity = (now - last_activity).total_seconds() / 3600  # hours
                features['hours_since_last_activity'] = min(time_since_activity / 168, 1.0)  # normalize to week
            
            # Content upload patterns
            upload_frequency = context_data.get('upload_frequency_per_day', 0)
            features['upload_frequency_normalized'] = min(upload_frequency / 10, 1.0)  # normalize to 10 uploads/day
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting temporal features: {e}")
            return {}
    
    async def _extract_behavioral_features(self,
                                         creator_id: str,
                                         context_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract behavioral features"""
        try:
            features = {}
            
            # Engagement patterns
            engagement_rate = context_data.get('engagement_rate', 0)
            features['engagement_rate'] = min(engagement_rate, 1.0)
            
            # Content diversity
            content_types = context_data.get('content_types_count', 1)
            features['content_diversity'] = min(content_types / 5, 1.0)  # normalize to 5 types
            
            # Platform usage
            platforms_used = context_data.get('platforms_count', 1)
            features['platform_diversity'] = min(platforms_used / 3, 1.0)  # normalize to 3 platforms
            
            # Collaboration frequency
            collaborations = context_data.get('collaborations_per_month', 0)
            features['collaboration_frequency'] = min(collaborations / 10, 1.0)
            
            # Revenue patterns
            revenue_consistency = context_data.get('revenue_consistency_score', 0.5)
            features['revenue_consistency'] = revenue_consistency
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting behavioral features: {e}")
            return {}
    
    async def _extract_performance_features(self,
                                          creator_id: str,
                                          context_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract performance features"""
        try:
            features = {}
            
            # View metrics
            avg_views = context_data.get('average_views', 0)
            features['avg_views_normalized'] = min(math.log(avg_views + 1) / 15, 1.0)  # log normalize
            
            # Growth metrics
            follower_growth = context_data.get('follower_growth_rate', 0)
            features['follower_growth'] = min(max(follower_growth, -1.0), 1.0)  # clip to [-1, 1]
            
            # Quality metrics
            content_quality = context_data.get('content_quality_score', 0.5)
            features['content_quality'] = content_quality
            
            # Technical performance
            upload_success_rate = context_data.get('upload_success_rate', 1.0)
            features['upload_success_rate'] = upload_success_rate
            
            processing_time = context_data.get('avg_processing_time_seconds', 30)
            features['processing_time_normalized'] = min(processing_time / 300, 1.0)  # normalize to 5 min
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting performance features: {e}")
            return {}
    
    async def _extract_contextual_features(self,
                                         creator_id: str,
                                         context_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract contextual features"""
        try:
            features = {}
            
            # Creator tier
            creator_tier = context_data.get('creator_tier', 'beginner')
            tier_mapping = {
                'beginner': 0.0,
                'intermediate': 0.2,
                'advanced': 0.4,
                'professional': 0.6,
                'enterprise': 0.8,
                'celebrity': 1.0
            }
            features['creator_tier'] = tier_mapping.get(creator_tier, 0.0)
            
            # Specialization
            specialization = context_data.get('specialization', 'general')
            spec_mapping = {
                'musician': 0.1,
                'blogger': 0.2,
                'photographer': 0.3,
                'influencer': 0.4,
                'comedian': 0.5,
                'podcaster': 0.6,
                'gamer': 0.7,
                'educator': 0.8,
                'artist': 0.9,
                'general': 0.0
            }
            features['specialization'] = spec_mapping.get(specialization, 0.0)
            
            # System load context
            system_load = context_data.get('system_load_percentage', 50) / 100
            features['system_load'] = system_load
            
            # Time zone activity
            timezone_offset = context_data.get('timezone_offset', 0)
            features['timezone_offset_normalized'] = (timezone_offset + 12) / 24  # normalize -12 to +12
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting contextual features: {e}")
            return {}
    
    async def predict_errors(self,
                           creator_id: str,
                           feature_vector: Optional[FeatureVector] = None,
                           prediction_horizon_hours: int = 72,
                           models: Optional[List[str]] = None) -> List[ErrorPrediction]:
        """
        Predict potential errors for creator
        
        Args:
            creator_id: ID créateur
            feature_vector: Vecteur features (optionnel)
            prediction_horizon_hours: Horizon prédiction
            models: Modèles à utiliser (tous si None)
            
        Returns:
            List of error predictions
        """
        try:
            if models is None:
                models = list(self.ml_models.keys())
            
            predictions = []
            
            # Use provided feature vector or get latest
            if feature_vector is None:
                creator_features = self.feature_vectors.get(creator_id, [])
                if not creator_features:
                    logger.warning(f"No features available for creator {creator_id}")
                    return predictions
                
                feature_vector = creator_features[-1]
            
            # Generate predictions using each model
            for model_id in models:
                if model_id not in self.ml_models:
                    continue
                
                model_predictions = await self._predict_with_model(
                    model_id, creator_id, feature_vector, prediction_horizon_hours
                )
                
                predictions.extend(model_predictions)
            
            # Store predictions
            self.predictions[creator_id].extend(predictions)
            
            # Maintain prediction history
            if len(self.predictions[creator_id]) > 1000:
                self.predictions[creator_id] = self.predictions[creator_id][-1000:]
            
            logger.debug(f"Generated {len(predictions)} predictions for creator {creator_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting errors: {e}")
            return []
    
    async def _predict_with_model(self,
                                model_id: str,
                                creator_id: str,
                                feature_vector: FeatureVector,
                                prediction_horizon_hours: int) -> List[ErrorPrediction]:
        """Predict errors using specific model"""
        try:
            model = self.ml_models.get(model_id)
            if not model or not model['trained']:
                return []
            
            model_type = model['config']['type']
            predictions = []
            
            if model_type == PredictionModel.ANOMALY_DETECTION:
                predictions = await self._anomaly_detection_predict(
                    model_id, creator_id, feature_vector, prediction_horizon_hours
                )
            elif model_type == PredictionModel.CLASSIFICATION:
                predictions = await self._classification_predict(
                    model_id, creator_id, feature_vector, prediction_horizon_hours
                )
            elif model_type == PredictionModel.TIME_SERIES_FORECAST:
                predictions = await self._time_series_predict(
                    model_id, creator_id, feature_vector, prediction_horizon_hours
                )
            elif model_type == PredictionModel.ENSEMBLE:
                predictions = await self._ensemble_predict(
                    model_id, creator_id, feature_vector, prediction_horizon_hours
                )
            
            # Update model prediction count
            model['predictions_made'] += len(predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting with model {model_id}: {e}")
            return []
    
    async def _anomaly_detection_predict(self,
                                       model_id: str,
                                       creator_id: str,
                                       feature_vector: FeatureVector,
                                       prediction_horizon_hours: int) -> List[ErrorPrediction]:
        """Anomaly detection prediction"""
        try:
            predictions = []
            
            # Get baseline for creator
            baseline = self.anomaly_baselines.get(creator_id, {})
            if not baseline:
                # Calculate baseline from historical data
                baseline = await self._calculate_anomaly_baseline(creator_id)
                self.anomaly_baselines[creator_id] = baseline
            
            # Check each feature for anomalies
            anomaly_scores = {}
            for feature_name, feature_value in feature_vector.features.items():
                if feature_name in baseline:
                    mean = baseline[feature_name]['mean']
                    std = baseline[feature_name]['std']
                    
                    if std > 0:
                        z_score = abs(feature_value - mean) / std
                        if z_score > self.config['anomaly_threshold']:
                            anomaly_scores[feature_name] = z_score
            
            # Generate predictions for significant anomalies
            for feature_name, score in anomaly_scores.items():
                if score > self.config['anomaly_threshold']:
                    probability = min(score / 5.0, 0.95)  # Cap at 95%
                    
                    prediction = ErrorPrediction(
                        prediction_id=f"anomaly_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        creator_id=creator_id,
                        predicted_error_type=f"anomaly_{feature_name}",
                        probability=probability,
                        confidence=self._calculate_confidence(probability),
                        risk_level=self._calculate_risk_level(probability),
                        time_window_hours=prediction_horizon_hours,
                        contributing_factors=[f"Anomalous {feature_name} (z-score: {score:.2f})"],
                        prevention_actions=await self._generate_prevention_actions(f"anomaly_{feature_name}"),
                        model_used=PredictionModel.ANOMALY_DETECTION,
                        feature_importance={feature_name: 1.0},
                        timestamp=datetime.utcnow()
                    )
                    
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in anomaly detection prediction: {e}")
            return []
    
    async def _classification_predict(self,
                                    model_id: str,
                                    creator_id: str,
                                    feature_vector: FeatureVector,
                                    prediction_horizon_hours: int) -> List[ErrorPrediction]:
        """Classification prediction"""
        try:
            predictions = []
            model = self.ml_models[model_id]
            error_classes = model['config']['classes']
            
            # Simple rule-based classification (in production would use trained classifier)
            features = feature_vector.features
            
            for error_class in error_classes:
                probability = await self._calculate_class_probability(error_class, features)
                
                if probability > self.config['prediction_confidence_threshold']:
                    prediction = ErrorPrediction(
                        prediction_id=f"class_{creator_id}_{error_class}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        creator_id=creator_id,
                        predicted_error_type=error_class,
                        probability=probability,
                        confidence=self._calculate_confidence(probability),
                        risk_level=self._calculate_risk_level(probability),
                        time_window_hours=prediction_horizon_hours,
                        contributing_factors=await self._identify_contributing_factors(error_class, features),
                        prevention_actions=await self._generate_prevention_actions(error_class),
                        model_used=PredictionModel.CLASSIFICATION,
                        feature_importance=await self._calculate_feature_importance(error_class, features),
                        timestamp=datetime.utcnow()
                    )
                    
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in classification prediction: {e}")
            return []
    
    async def _time_series_predict(self,
                                 model_id: str,
                                 creator_id: str,
                                 feature_vector: FeatureVector,
                                 prediction_horizon_hours: int) -> List[ErrorPrediction]:
        """Time series prediction"""
        try:
            predictions = []
            
            # Get historical error patterns
            creator_features = self.feature_vectors.get(creator_id, [])
            if len(creator_features) < 24:  # Need at least 24 hours of data
                return predictions
            
            # Simple trend analysis
            recent_features = creator_features[-24:]  # Last 24 hours
            
            # Calculate error probability trends
            error_indicators = []
            for fv in recent_features:
                # Simple error indicator based on feature anomalies
                indicator = 0
                for feature_name, value in fv.features.items():
                    if 'error' in feature_name.lower() or value > 0.8:  # High values might indicate issues
                        indicator += 1
                
                error_indicators.append(indicator)
            
            # Predict future error probability
            if error_indicators:
                recent_trend = statistics.mean(error_indicators[-6:])  # Last 6 hours
                overall_trend = statistics.mean(error_indicators)
                
                # Simple forecast
                forecast_probability = min((recent_trend / 5) * 1.2, 0.9)  # Amplify recent trend
                
                if forecast_probability > 0.3:
                    prediction = ErrorPrediction(
                        prediction_id=f"timeseries_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        creator_id=creator_id,
                        predicted_error_type="system_degradation",
                        probability=forecast_probability,
                        confidence=self._calculate_confidence(forecast_probability),
                        risk_level=self._calculate_risk_level(forecast_probability),
                        time_window_hours=prediction_horizon_hours,
                        contributing_factors=[f"Increasing error trend (recent: {recent_trend:.2f})"],
                        prevention_actions=await self._generate_prevention_actions("system_degradation"),
                        model_used=PredictionModel.TIME_SERIES_FORECAST,
                        feature_importance={"trend": 1.0},
                        timestamp=datetime.utcnow()
                    )
                    
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in time series prediction: {e}")
            return []
    
    async def _ensemble_predict(self,
                              model_id: str,
                              creator_id: str,
                              feature_vector: FeatureVector,
                              prediction_horizon_hours: int) -> List[ErrorPrediction]:
        """Ensemble prediction combining multiple models"""
        try:
            model = self.ml_models[model_id]
            base_models = model['config']['base_models']
            
            # Get predictions from base models
            all_predictions = []
            for base_model_id in base_models:
                if base_model_id in self.ml_models and base_model_id != model_id:
                    base_predictions = await self._predict_with_model(
                        base_model_id, creator_id, feature_vector, prediction_horizon_hours
                    )
                    all_predictions.extend(base_predictions)
            
            # Combine predictions by error type
            combined_predictions = {}
            for pred in all_predictions:
                error_type = pred.predicted_error_type
                
                if error_type not in combined_predictions:
                    combined_predictions[error_type] = []
                
                combined_predictions[error_type].append(pred)
            
            # Create ensemble predictions
            ensemble_predictions = []
            for error_type, predictions_list in combined_predictions.items():
                if len(predictions_list) >= 2:  # Need at least 2 models agreeing
                    # Weighted average of probabilities
                    avg_probability = statistics.mean(p.probability for p in predictions_list)
                    
                    # Combine contributing factors
                    all_factors = []
                    for p in predictions_list:
                        all_factors.extend(p.contributing_factors)
                    
                    unique_factors = list(set(all_factors))
                    
                    ensemble_prediction = ErrorPrediction(
                        prediction_id=f"ensemble_{creator_id}_{error_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        creator_id=creator_id,
                        predicted_error_type=error_type,
                        probability=avg_probability,
                        confidence=self._calculate_confidence(avg_probability),
                        risk_level=self._calculate_risk_level(avg_probability),
                        time_window_hours=prediction_horizon_hours,
                        contributing_factors=unique_factors,
                        prevention_actions=await self._generate_prevention_actions(error_type),
                        model_used=PredictionModel.ENSEMBLE,
                        feature_importance={},
                        timestamp=datetime.utcnow()
                    )
                    
                    ensemble_predictions.append(ensemble_prediction)
            
            return ensemble_predictions
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return []
    
    async def _calculate_anomaly_baseline(self, creator_id: str) -> Dict[str, Dict[str, float]]:
        """Calculate anomaly detection baseline for creator"""
        try:
            baseline = {}
            creator_features = self.feature_vectors.get(creator_id, [])
            
            if len(creator_features) < 10:
                return baseline
            
            # Calculate baseline statistics for each feature
            feature_data = defaultdict(list)
            for fv in creator_features[-168:]:  # Last week of data
                for feature_name, feature_value in fv.features.items():
                    feature_data[feature_name].append(feature_value)
            
            for feature_name, values in feature_data.items():
                if len(values) >= 5:
                    baseline[feature_name] = {
                        'mean': statistics.mean(values),
                        'std': statistics.stdev(values) if len(values) > 1 else 0.1,
                        'min': min(values),
                        'max': max(values)
                    }
            
            return baseline
            
        except Exception as e:
            logger.error(f"Error calculating anomaly baseline: {e}")
            return {}
    
    async def _calculate_class_probability(self, error_class: str, features: Dict[str, float]) -> float:
        """Calculate probability for error class"""
        try:
            # Simple rule-based probability calculation
            probability = 0.0
            
            if error_class == 'upload_error':
                # Higher probability if upload success rate is low
                upload_success = features.get('upload_success_rate', 1.0)
                probability = max(0, 1.0 - upload_success)
                
                # Increase if processing time is high
                processing_time = features.get('processing_time_normalized', 0.1)
                probability += processing_time * 0.3
                
            elif error_class == 'payment_error':
                # Higher probability if revenue consistency is low
                revenue_consistency = features.get('revenue_consistency', 0.5)
                probability = max(0, 1.0 - revenue_consistency) * 0.8
                
            elif error_class == 'processing_error':
                # Higher probability with high system load
                system_load = features.get('system_load', 0.5)
                probability = system_load * 0.6
                
                # Increase with low content quality
                content_quality = features.get('content_quality', 0.5)
                probability += max(0, 0.5 - content_quality)
                
            elif error_class == 'engagement_error':
                # Higher probability with low engagement rate
                engagement_rate = features.get('engagement_rate', 0.5)
                probability = max(0, 0.5 - engagement_rate) * 1.5
            
            return min(probability, 0.95)
            
        except Exception as e:
            logger.error(f"Error calculating class probability: {e}")
            return 0.0
    
    async def _identify_contributing_factors(self, error_class: str, features: Dict[str, float]) -> List[str]:
        """Identify contributing factors for error prediction"""
        try:
            factors = []
            
            # Check high-impact features
            if features.get('system_load', 0) > 0.8:
                factors.append("High system load")
            
            if features.get('upload_success_rate', 1.0) < 0.9:
                factors.append("Low upload success rate")
            
            if features.get('processing_time_normalized', 0) > 0.7:
                factors.append("High processing times")
            
            if features.get('engagement_rate', 0.5) < 0.3:
                factors.append("Low engagement metrics")
            
            if features.get('content_quality', 0.5) < 0.4:
                factors.append("Content quality concerns")
            
            return factors
            
        except Exception as e:
            logger.error(f"Error identifying contributing factors: {e}")
            return []
    
    async def _generate_prevention_actions(self, error_type: str) -> List[str]:
        """Generate prevention actions for error type"""
        try:
            actions = []
            
            if 'upload' in error_type:
                actions.extend([
                    "Pre-validate content before upload",
                    "Check network connectivity",
                    "Use smaller file sizes if possible",
                    "Retry upload during off-peak hours"
                ])
            
            elif 'payment' in error_type:
                actions.extend([
                    "Verify payment method validity",
                    "Check account billing status",
                    "Review monetization settings",
                    "Contact payment support if needed"
                ])
            
            elif 'processing' in error_type:
                actions.extend([
                    "Optimize content format and size",
                    "Schedule processing during low-load periods",
                    "Monitor system resource usage",
                    "Use content preprocessing tools"
                ])
            
            elif 'engagement' in error_type:
                actions.extend([
                    "Review content strategy",
                    "Optimize posting schedule",
                    "Improve content quality",
                    "Engage more with audience"
                ])
            
            elif 'anomaly' in error_type:
                actions.extend([
                    "Monitor activity patterns",
                    "Review recent changes",
                    "Check for system updates",
                    "Investigate unusual metrics"
                ])
            
            # Add general prevention actions
            actions.extend([
                "Monitor system notifications",
                "Keep software updated",
                "Follow best practices"
            ])
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating prevention actions: {e}")
            return []
    
    async def _calculate_feature_importance(self, error_class: str, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate feature importance for prediction"""
        try:
            importance = {}
            
            # Simple importance calculation based on feature values and error type
            for feature_name, feature_value in features.items():
                base_importance = 0.1
                
                # Increase importance for relevant features
                if error_class == 'upload_error' and 'upload' in feature_name:
                    base_importance = 0.8
                elif error_class == 'payment_error' and 'revenue' in feature_name:
                    base_importance = 0.8
                elif error_class == 'processing_error' and ('processing' in feature_name or 'system' in feature_name):
                    base_importance = 0.8
                elif error_class == 'engagement_error' and 'engagement' in feature_name:
                    base_importance = 0.8
                
                # Adjust based on feature value
                if feature_value > 0.7 or feature_value < 0.3:
                    base_importance *= 1.5
                
                importance[feature_name] = min(base_importance, 1.0)
            
            return importance
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            return {}
    
    def _calculate_confidence(self, probability: float) -> PredictionConfidence:
        """Calculate prediction confidence level"""
        if probability < 0.2:
            return PredictionConfidence.VERY_LOW
        elif probability < 0.4:
            return PredictionConfidence.LOW
        elif probability < 0.6:
            return PredictionConfidence.MEDIUM
        elif probability < 0.8:
            return PredictionConfidence.HIGH
        else:
            return PredictionConfidence.VERY_HIGH
    
    def _calculate_risk_level(self, probability: float) -> ErrorRiskLevel:
        """Calculate error risk level"""
        if probability < 0.2:
            return ErrorRiskLevel.MINIMAL
        elif probability < 0.4:
            return ErrorRiskLevel.LOW
        elif probability < 0.6:
            return ErrorRiskLevel.MODERATE
        elif probability < 0.8:
            return ErrorRiskLevel.HIGH
        else:
            return ErrorRiskLevel.CRITICAL
    
    async def train_models(self, creator_id: Optional[str] = None):
        """Train or retrain ML models"""
        try:
            if creator_id:
                # Train models for specific creator
                await self._train_creator_models(creator_id)
            else:
                # Train global models
                await self._train_global_models()
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    async def _train_creator_models(self, creator_id: str):
        """Train models for specific creator"""
        try:
            creator_features = self.feature_vectors.get(creator_id, [])
            
            if len(creator_features) < self.config['min_training_samples']:
                logger.warning(f"Insufficient training data for creator {creator_id}")
                return
            
            # Update anomaly baseline
            self.anomaly_baselines[creator_id] = await self._calculate_anomaly_baseline(creator_id)
            
            logger.info(f"Models trained for creator {creator_id}")
            
        except Exception as e:
            logger.error(f"Error training creator models: {e}")
    
    async def _train_global_models(self):
        """Train global models"""
        try:
            # Mark all models as trained (simplified implementation)
            for model_id, model in self.ml_models.items():
                model['trained'] = True
                model['last_training'] = datetime.utcnow()
                
                # Update performance metrics
                if model_id in self.model_performance:
                    perf = self.model_performance[model_id]
                    perf.last_trained = datetime.utcnow()
                    perf.training_samples = sum(len(fv) for fv in self.feature_vectors.values())
            
            logger.info("Global models trained")
            
        except Exception as e:
            logger.error(f"Error training global models: {e}")
    
    async def get_model_performance(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            if model_id:
                perf = self.model_performance.get(model_id)
                return asdict(perf) if perf else {}
            else:
                return {mid: asdict(perf) for mid, perf in self.model_performance.items()}
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {}
    
    async def get_creator_predictions(self, creator_id: str, limit: int = 10) -> List[ErrorPrediction]:
        """Get recent predictions for creator"""
        try:
            predictions = self.predictions.get(creator_id, [])
            return predictions[-limit:]
        except Exception as e:
            logger.error(f"Error getting creator predictions: {e}")
            return []
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide ML metrics"""
        try:
            metrics = {
                'total_creators_tracked': len(self.feature_vectors),
                'total_models': len(self.ml_models),
                'trained_models': len([m for m in self.ml_models.values() if m['trained']]),
                'total_predictions': sum(len(preds) for preds in self.predictions.values()),
                'average_prediction_accuracy': 0.85,  # Placeholder
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}


# Global instance
error_prediction_engine = ErrorPredictionMachineLearningEngine()