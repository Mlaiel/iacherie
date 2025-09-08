"""Advanced ML Matcher - Multi-Dimensional Machine Learning Creator Matching
=============================================================================

Sophisticated machine learning engine for creator matching using:
- Multi-dimensional feature vectors
- Ensemble learning algorithms  
- Deep learning models
- Real-time inference optimization
- Adaptive learning from feedback

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class MatchingAlgorithm(Enum):
    """Available ML matching algorithms"""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    SVM = "support_vector_machine"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"


class MLMetrics(Enum):
    """ML model performance metrics"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    ROC_AUC = "roc_auc"
    MAP_AT_K = "map_at_k"


@dataclass
class FeatureVector:
    """Multi-dimensional feature representation"""
    creator_id: str
    content_features: Dict[str, float] = field(default_factory=dict)
    engagement_features: Dict[str, float] = field(default_factory=dict)
    demographic_features: Dict[str, float] = field(default_factory=dict)
    behavioral_features: Dict[str, float] = field(default_factory=dict)
    technical_features: Dict[str, float] = field(default_factory=dict)
    social_features: Dict[str, float] = field(default_factory=dict)
    temporal_features: Dict[str, float] = field(default_factory=dict)
    collaboration_history: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    preference_vector: Dict[str, float] = field(default_factory=dict)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for ML processing"""
        all_features = []
        
        # Combine all feature dictionaries
        feature_dicts = [
            self.content_features,
            self.engagement_features,
            self.demographic_features,
            self.behavioral_features,
            self.technical_features,
            self.social_features,
            self.temporal_features,
            self.collaboration_history,
            self.performance_metrics,
            self.preference_vector
        ]
        
        for feature_dict in feature_dicts:
            all_features.extend(list(feature_dict.values()))
        
        return np.array(all_features, dtype=np.float32)
    
    def get_feature_names(self) -> List[str]:
        """Get ordered list of feature names"""
        feature_names = []
        
        feature_dicts = [
            ("content", self.content_features),
            ("engagement", self.engagement_features),
            ("demographic", self.demographic_features),
            ("behavioral", self.behavioral_features),
            ("technical", self.technical_features),
            ("social", self.social_features),
            ("temporal", self.temporal_features),
            ("collaboration", self.collaboration_history),
            ("performance", self.performance_metrics),
            ("preference", self.preference_vector)
        ]
        
        for prefix, feature_dict in feature_dicts:
            for key in feature_dict.keys():
                feature_names.append(f"{prefix}_{key}")
        
        return feature_names


@dataclass
class MLMatchingModel:
    """ML model container with metadata"""
    algorithm: MatchingAlgorithm
    model: Any  # sklearn/tensorflow model
    feature_importance: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[MLMetrics, float] = field(default_factory=dict)
    training_date: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    is_trained: bool = False
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions using the model"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        return self.model.predict(features)
    
    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
            
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(features)
        else:
            # For models without predict_proba, return predictions as probabilities
            predictions = self.model.predict(features)
            return np.column_stack([1 - predictions, predictions])


class AdvancedMLMatcher:
    """
    Advanced ML-powered creator matching engine with ensemble learning
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the advanced ML matcher"""
        self.config = config or {}
        self.models: Dict[MatchingAlgorithm, MLMatchingModel] = {}
        self.feature_extractors = {}
        self.training_data = []
        self.model_weights = {
            MatchingAlgorithm.RANDOM_FOREST: 0.2,
            MatchingAlgorithm.GRADIENT_BOOSTING: 0.3,
            MatchingAlgorithm.NEURAL_NETWORK: 0.25,
            MatchingAlgorithm.SVM: 0.15,
            MatchingAlgorithm.DEEP_LEARNING: 0.1
        }
        self.performance_threshold = self.config.get('performance_threshold', 0.8)
        self.max_recommendations = self.config.get('max_recommendations', 10)
        
        logger.info("🧠 Advanced ML Matcher initialized")
    
    async def initialize_models(self):
        """Initialize and load pre-trained models"""
        try:
            # Initialize different ML algorithms
            await self._initialize_random_forest()
            await self._initialize_gradient_boosting()
            await self._initialize_neural_network()
            await self._initialize_svm()
            await self._initialize_deep_learning()
            
            logger.info("✅ All ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing ML models: {e}")
            raise
    
    async def _initialize_random_forest(self):
        """Initialize Random Forest model"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.models[MatchingAlgorithm.RANDOM_FOREST] = MLMatchingModel(
                algorithm=MatchingAlgorithm.RANDOM_FOREST,
                model=model
            )
            
        except ImportError:
            logger.warning("⚠️ scikit-learn not available, skipping Random Forest")
    
    async def _initialize_gradient_boosting(self):
        """Initialize Gradient Boosting model"""
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.models[MatchingAlgorithm.GRADIENT_BOOSTING] = MLMatchingModel(
                algorithm=MatchingAlgorithm.GRADIENT_BOOSTING,
                model=model
            )
            
        except ImportError:
            logger.warning("⚠️ scikit-learn not available, skipping Gradient Boosting")
    
    async def _initialize_neural_network(self):
        """Initialize Neural Network model"""
        try:
            from sklearn.neural_network import MLPClassifier
            
            model = MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                learning_rate='adaptive',
                max_iter=500,
                random_state=42
            )
            
            self.models[MatchingAlgorithm.NEURAL_NETWORK] = MLMatchingModel(
                algorithm=MatchingAlgorithm.NEURAL_NETWORK,
                model=model
            )
            
        except ImportError:
            logger.warning("⚠️ scikit-learn not available, skipping Neural Network")
    
    async def _initialize_svm(self):
        """Initialize Support Vector Machine model"""
        try:
            from sklearn.svm import SVC
            
            model = SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            )
            
            self.models[MatchingAlgorithm.SVM] = MLMatchingModel(
                algorithm=MatchingAlgorithm.SVM,
                model=model
            )
            
        except ImportError:
            logger.warning("⚠️ scikit-learn not available, skipping SVM")
    
    async def _initialize_deep_learning(self):
        """Initialize Deep Learning model"""
        try:
            # This would initialize a TensorFlow/PyTorch model
            # For now, using a placeholder
            self.models[MatchingAlgorithm.DEEP_LEARNING] = MLMatchingModel(
                algorithm=MatchingAlgorithm.DEEP_LEARNING,
                model=None  # Placeholder for deep learning model
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Deep learning model initialization failed: {e}")
    
    async def extract_features(self, creator_profile: Dict[str, Any]) -> FeatureVector:
        """Extract comprehensive features from creator profile"""
        feature_vector = FeatureVector(creator_id=creator_profile['creator_id'])
        
        # Content features
        feature_vector.content_features = {
            'avg_content_length': creator_profile.get('avg_content_length', 0.0),
            'content_frequency': creator_profile.get('posts_per_week', 0.0),
            'content_diversity': creator_profile.get('content_categories', 0.0),
            'quality_score': creator_profile.get('content_quality', 0.0),
            'originality_score': creator_profile.get('originality', 0.0)
        }
        
        # Engagement features
        feature_vector.engagement_features = {
            'avg_likes': creator_profile.get('avg_likes', 0.0),
            'avg_comments': creator_profile.get('avg_comments', 0.0),
            'avg_shares': creator_profile.get('avg_shares', 0.0),
            'engagement_rate': creator_profile.get('engagement_rate', 0.0),
            'follower_growth': creator_profile.get('follower_growth_rate', 0.0)
        }
        
        # Demographic features
        feature_vector.demographic_features = {
            'age': creator_profile.get('age', 0.0),
            'follower_count': creator_profile.get('followers', 0.0),
            'account_age_days': creator_profile.get('account_age_days', 0.0),
            'verified_status': float(creator_profile.get('verified', False)),
            'location_tier': creator_profile.get('location_tier', 0.0)
        }
        
        # Behavioral features
        feature_vector.behavioral_features = {
            'posting_consistency': creator_profile.get('posting_consistency', 0.0),
            'response_time': creator_profile.get('avg_response_time_hours', 0.0),
            'collaboration_openness': creator_profile.get('collaboration_score', 0.0),
            'brand_safety': creator_profile.get('brand_safety_score', 0.0),
            'professionalism': creator_profile.get('professionalism_score', 0.0)
        }
        
        # Technical features
        feature_vector.technical_features = {
            'content_production_quality': creator_profile.get('production_quality', 0.0),
            'editing_skills': creator_profile.get('editing_score', 0.0),
            'equipment_quality': creator_profile.get('equipment_score', 0.0),
            'technical_expertise': creator_profile.get('technical_skills', 0.0),
            'platform_mastery': creator_profile.get('platform_knowledge', 0.0)
        }
        
        # Social features
        feature_vector.social_features = {
            'network_size': creator_profile.get('network_connections', 0.0),
            'influence_score': creator_profile.get('influence_rating', 0.0),
            'community_engagement': creator_profile.get('community_score', 0.0),
            'cross_platform_presence': creator_profile.get('platform_count', 0.0),
            'reputation_score': creator_profile.get('reputation', 0.0)
        }
        
        # Temporal features
        feature_vector.temporal_features = {
            'peak_activity_hour': creator_profile.get('peak_hour', 0.0),
            'active_days_per_week': creator_profile.get('active_days', 0.0),
            'timezone_offset': creator_profile.get('timezone_offset', 0.0),
            'seasonal_activity': creator_profile.get('seasonal_pattern', 0.0),
            'content_freshness': creator_profile.get('content_recency_score', 0.0)
        }
        
        # Collaboration history
        collaboration_data = creator_profile.get('collaboration_history', {})
        feature_vector.collaboration_history = {
            'total_collaborations': collaboration_data.get('total_count', 0.0),
            'successful_collaborations': collaboration_data.get('successful_count', 0.0),
            'avg_collaboration_rating': collaboration_data.get('avg_rating', 0.0),
            'collaboration_frequency': collaboration_data.get('frequency', 0.0),
            'repeat_collaboration_rate': collaboration_data.get('repeat_rate', 0.0)
        }
        
        # Performance metrics
        performance_data = creator_profile.get('performance_metrics', {})
        feature_vector.performance_metrics = {
            'roi_score': performance_data.get('roi', 0.0),
            'conversion_rate': performance_data.get('conversion_rate', 0.0),
            'brand_lift': performance_data.get('brand_lift', 0.0),
            'campaign_success_rate': performance_data.get('campaign_success', 0.0),
            'audience_retention': performance_data.get('audience_retention', 0.0)
        }
        
        # Preference vector
        preferences = creator_profile.get('preferences', {})
        feature_vector.preference_vector = {
            'collaboration_type_pref': preferences.get('collaboration_type', 0.0),
            'budget_flexibility': preferences.get('budget_flexibility', 0.0),
            'timeline_flexibility': preferences.get('timeline_flexibility', 0.0),
            'creative_control_pref': preferences.get('creative_control', 0.0),
            'exclusivity_requirement': preferences.get('exclusivity', 0.0)
        }
        
        return feature_vector
    
    async def find_matches(
        self,
        query_creator: Dict[str, Any],
        candidate_creators: List[Dict[str, Any]],
        algorithm: Optional[MatchingAlgorithm] = None
    ) -> List[Dict[str, Any]]:
        """
        Find best matches using ML algorithms
        """
        try:
            # Extract features for query creator
            query_features = await self.extract_features(query_creator)
            
            # Extract features for all candidates
            candidate_features = []
            for candidate in candidate_creators:
                features = await self.extract_features(candidate)
                candidate_features.append(features)
            
            # Use ensemble if no specific algorithm specified
            if algorithm is None:
                matches = await self._ensemble_predict(query_features, candidate_features, candidate_creators)
            else:
                matches = await self._single_algorithm_predict(
                    algorithm, query_features, candidate_features, candidate_creators
                )
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            # Return top matches
            return matches[:self.max_recommendations]
            
        except Exception as e:
            logger.error(f"❌ Error finding matches: {e}")
            return []
    
    async def _ensemble_predict(
        self,
        query_features: FeatureVector,
        candidate_features: List[FeatureVector],
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use ensemble of models for prediction"""
        matches = []
        
        for i, candidate_feature in enumerate(candidate_features):
            # Calculate compatibility using multiple algorithms
            compatibility_scores = {}
            
            for algorithm, weight in self.model_weights.items():
                if algorithm in self.models and self.models[algorithm].is_trained:
                    try:
                        score = await self._calculate_compatibility(
                            query_features, candidate_feature, algorithm
                        )
                        compatibility_scores[algorithm] = score * weight
                    except Exception as e:
                        logger.warning(f"⚠️ Error with {algorithm}: {e}")
                        compatibility_scores[algorithm] = 0.0
            
            # Calculate weighted average
            if compatibility_scores:
                ensemble_score = sum(compatibility_scores.values()) / sum(self.model_weights.values())
            else:
                ensemble_score = 0.0
            
            match_result = {
                'creator_id': candidates[i]['creator_id'],
                'creator_profile': candidates[i],
                'compatibility_score': ensemble_score,
                'algorithm_scores': compatibility_scores,
                'confidence': min(ensemble_score, 1.0),
                'recommendation_strength': self._get_recommendation_strength(ensemble_score)
            }
            
            matches.append(match_result)
        
        return matches
    
    async def _single_algorithm_predict(
        self,
        algorithm: MatchingAlgorithm,
        query_features: FeatureVector,
        candidate_features: List[FeatureVector],
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use single algorithm for prediction"""
        matches = []
        
        if algorithm not in self.models:
            logger.error(f"❌ Algorithm {algorithm} not available")
            return matches
        
        for i, candidate_feature in enumerate(candidate_features):
            try:
                score = await self._calculate_compatibility(
                    query_features, candidate_feature, algorithm
                )
                
                match_result = {
                    'creator_id': candidates[i]['creator_id'],
                    'creator_profile': candidates[i],
                    'compatibility_score': score,
                    'algorithm': algorithm.value,
                    'confidence': score,
                    'recommendation_strength': self._get_recommendation_strength(score)
                }
                
                matches.append(match_result)
                
            except Exception as e:
                logger.warning(f"⚠️ Error calculating compatibility: {e}")
        
        return matches
    
    async def _calculate_compatibility(
        self,
        query_features: FeatureVector,
        candidate_features: FeatureVector,
        algorithm: MatchingAlgorithm
    ) -> float:
        """Calculate compatibility score between two creators"""
        
        if not self.models[algorithm].is_trained:
            # Use heuristic method if model not trained
            return await self._heuristic_compatibility(query_features, candidate_features)
        
        try:
            # Prepare feature vectors for ML model
            query_vector = query_features.to_array()
            candidate_vector = candidate_features.to_array()
            
            # Calculate feature differences/combinations
            feature_diff = np.abs(query_vector - candidate_vector)
            feature_product = query_vector * candidate_vector
            feature_combo = np.concatenate([query_vector, candidate_vector, feature_diff, feature_product])
            
            # Make prediction
            model = self.models[algorithm]
            compatibility_proba = model.predict_proba(feature_combo.reshape(1, -1))
            
            # Return compatibility probability
            return float(compatibility_proba[0][1])  # Probability of positive match
            
        except Exception as e:
            logger.warning(f"⚠️ ML prediction failed, using heuristic: {e}")
            return await self._heuristic_compatibility(query_features, candidate_features)
    
    async def _heuristic_compatibility(
        self,
        query_features: FeatureVector,
        candidate_features: FeatureVector
    ) -> float:
        """Calculate heuristic compatibility when ML models unavailable"""
        
        scores = []
        
        # Content compatibility
        content_score = self._calculate_feature_similarity(
            query_features.content_features,
            candidate_features.content_features
        )
        scores.append(content_score * 0.25)
        
        # Engagement compatibility  
        engagement_score = self._calculate_feature_similarity(
            query_features.engagement_features,
            candidate_features.engagement_features
        )
        scores.append(engagement_score * 0.20)
        
        # Demographic compatibility
        demographic_score = self._calculate_feature_similarity(
            query_features.demographic_features,
            candidate_features.demographic_features
        )
        scores.append(demographic_score * 0.15)
        
        # Performance compatibility
        performance_score = self._calculate_feature_similarity(
            query_features.performance_metrics,
            candidate_features.performance_metrics
        )
        scores.append(performance_score * 0.20)
        
        # Collaboration history compatibility
        collab_score = self._calculate_feature_similarity(
            query_features.collaboration_history,
            candidate_features.collaboration_history
        )
        scores.append(collab_score * 0.20)
        
        return sum(scores)
    
    def _calculate_feature_similarity(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Calculate similarity between two feature dictionaries"""
        if not features1 or not features2:
            return 0.0
        
        # Get common features
        common_features = set(features1.keys()) & set(features2.keys())
        
        if not common_features:
            return 0.0
        
        similarities = []
        for feature in common_features:
            val1, val2 = features1[feature], features2[feature]
            
            # Avoid division by zero
            if val1 == 0 and val2 == 0:
                similarity = 1.0
            elif val1 == 0 or val2 == 0:
                similarity = 0.0
            else:
                # Calculate normalized similarity
                similarity = 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2))
            
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities)
    
    def _get_recommendation_strength(self, score: float) -> str:
        """Get human-readable recommendation strength"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "very_good"
        elif score >= 0.7:
            return "good"
        elif score >= 0.6:
            return "moderate"
        elif score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    async def train_models(self, training_data: List[Dict[str, Any]]):
        """Train all ML models with historical collaboration data"""
        try:
            logger.info("🚀 Starting ML model training...")
            
            # Prepare training data
            X, y = await self._prepare_training_data(training_data)
            
            if len(X) < 10:
                logger.warning("⚠️ Insufficient training data, using default models")
                return
            
            # Train each model
            for algorithm, model_container in self.models.items():
                if model_container.model is not None:
                    try:
                        # Split data for training/validation
                        from sklearn.model_selection import train_test_split
                        X_train, X_val, y_train, y_val = train_test_split(
                            X, y, test_size=0.2, random_state=42
                        )
                        
                        # Train model
                        model_container.model.fit(X_train, y_train)
                        model_container.is_trained = True
                        
                        # Evaluate performance
                        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
                        y_pred = model_container.model.predict(X_val)
                        
                        model_container.performance_metrics = {
                            MLMetrics.ACCURACY: accuracy_score(y_val, y_pred),
                            MLMetrics.PRECISION: precision_score(y_val, y_pred, average='weighted'),
                            MLMetrics.RECALL: recall_score(y_val, y_pred, average='weighted'),
                            MLMetrics.F1_SCORE: f1_score(y_val, y_pred, average='weighted')
                        }
                        
                        logger.info(f"✅ {algorithm.value} trained successfully")
                        
                    except Exception as e:
                        logger.error(f"❌ Error training {algorithm.value}: {e}")
            
            logger.info("🎯 ML model training completed")
            
        except Exception as e:
            logger.error(f"❌ Error in model training: {e}")
    
    async def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for ML models"""
        X, y = [], []
        
        for sample in training_data:
            try:
                # Extract features for both creators
                creator1_features = await self.extract_features(sample['creator1'])
                creator2_features = await self.extract_features(sample['creator2'])
                
                # Combine features
                vector1 = creator1_features.to_array()
                vector2 = creator2_features.to_array()
                
                # Create combined feature vector
                feature_diff = np.abs(vector1 - vector2)
                feature_product = vector1 * vector2
                combined_features = np.concatenate([vector1, vector2, feature_diff, feature_product])
                
                X.append(combined_features)
                y.append(int(sample['successful_collaboration']))
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing training sample: {e}")
        
        return np.array(X), np.array(y)
    
    async def save_models(self, model_path: str = "models/"):
        """Save trained models to disk"""
        try:
            Path(model_path).mkdir(parents=True, exist_ok=True)
            
            for algorithm, model_container in self.models.items():
                if model_container.is_trained:
                    model_file = Path(model_path) / f"{algorithm.value}_model.pkl"
                    with open(model_file, 'wb') as f:
                        pickle.dump(model_container, f)
                    
                    logger.info(f"💾 Saved {algorithm.value} model to {model_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving models: {e}")
    
    async def load_models(self, model_path: str = "models/"):
        """Load trained models from disk"""
        try:
            model_dir = Path(model_path)
            
            if not model_dir.exists():
                logger.warning(f"⚠️ Model directory {model_path} does not exist")
                return
            
            for algorithm in MatchingAlgorithm:
                model_file = model_dir / f"{algorithm.value}_model.pkl"
                
                if model_file.exists():
                    with open(model_file, 'rb') as f:
                        model_container = pickle.load(f)
                        self.models[algorithm] = model_container
                    
                    logger.info(f"📂 Loaded {algorithm.value} model from {model_file}")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
    
    async def get_model_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all trained models"""
        performance = {}
        
        for algorithm, model_container in self.models.items():
            if model_container.is_trained:
                performance[algorithm.value] = {
                    'metrics': model_container.performance_metrics,
                    'training_date': model_container.training_date.isoformat(),
                    'version': model_container.version
                }
        
        return performance
    
    async def update_model_weights(self, performance_feedback: Dict[str, float]):
        """Update ensemble weights based on real-world performance"""
        try:
            total_feedback = sum(performance_feedback.values())
            
            if total_feedback > 0:
                # Normalize feedback and update weights
                for algorithm_name, feedback in performance_feedback.items():
                    algorithm = MatchingAlgorithm(algorithm_name)
                    if algorithm in self.model_weights:
                        # Weighted update
                        current_weight = self.model_weights[algorithm]
                        normalized_feedback = feedback / total_feedback
                        self.model_weights[algorithm] = 0.8 * current_weight + 0.2 * normalized_feedback
                
                # Normalize weights to sum to 1
                total_weight = sum(self.model_weights.values())
                if total_weight > 0:
                    for algorithm in self.model_weights:
                        self.model_weights[algorithm] /= total_weight
                
                logger.info("🔄 Model weights updated based on performance feedback")
            
        except Exception as e:
            logger.error(f"❌ Error updating model weights: {e}")