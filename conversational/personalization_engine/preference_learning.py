"""Preference Learning Engine
=========================

Industrial-grade ML-powered preference learning for IA Influencer Agent.
Implements collaborative filtering, content-based filtering, hybrid recommendation algorithms, and deep learning models for real-time preference adaptation.

Business Logic:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → AI rights protection → Professional SEO → Collaboration matching → Multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

WARNING: Any attempt to steal, copy, or use the concept, idea, or code without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Embedding, Input, Concatenate
import faiss
import json

from ..core.base_service import BaseService
from ..core.exceptions import PreferenceLearningError, ModelTrainingError
from ..ml.neural_networks import DeepRecommendationModel
from ..ml.feature_engineering import FeatureEngineer
from ..database.vector_store import VectorStore
from ..cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class LearningAlgorithm(str, Enum):
    """Preference learning algorithm types"""    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    NEURAL_COLLABORATIVE = "neural_collaborative"
    ENSEMBLE = "ensemble"
    REINFORCEMENT = "reinforcement"


class PreferenceType(str, Enum):
    """Types of user preferences to learn"""    CONTENT_TYPE = "content_type"
    STYLE_PREFERENCE = "style_preference"
    TIMING_PREFERENCE = "timing_preference"
    ENGAGEMENT_TYPE = "engagement_type"
    COLLABORATION_STYLE = "collaboration_style"
    LEARNING_STYLE = "learning_style"
    CREATIVE_DIRECTION = "creative_direction"


@dataclass
class UserInteraction:
    """User interaction data for preference learning"""    user_id: str
    item_id: str
    interaction_type: str  # view, like, share, comment, create, collaborate
    interaction_value: float  # normalized interaction strength
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    explicit_rating: Optional[float] = None
    implicit_feedback: Dict[str, float] = field(default_factory=dict)
    content_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreferenceModel:
    """Trained preference model"""    model_id: str
    algorithm: LearningAlgorithm
    model_data: Any  # Actual model object
    feature_names: List[str]
    performance_metrics: Dict[str, float]
    training_timestamp: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningContext:
    """Context for preference learning"""    user_id: str
    time_window: Tuple[datetime, datetime]
    content_domains: List[str]
    interaction_types: List[str]
    min_interactions: int = 10
    confidence_threshold: float = 0.7
    personalization_depth: str = "standard"


@dataclass
class PreferenceUpdate:
    """Preference update result"""    user_id: str
    preference_type: PreferenceType
    old_preferences: Dict[str, float]
    new_preferences: Dict[str, float]
    confidence_change: float
    update_reason: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PreferencePrediction:
    """Preference prediction result"""    user_id: str
    item_id: str
    predicted_rating: float
    confidence_score: float
    prediction_factors: Dict[str, float]
    similar_users: List[str]
    explanation: Optional[str] = None


class CollaborativeFilteringEngine:
    """Advanced collaborative filtering implementation"""    
    def __init__(self, n_factors: int = 100, learning_rate: float = 0.01):
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.user_factors = None
        self.item_factors = None
        self.user_biases = None
        self.item_biases = None
        self.global_bias = 0.0
        self.is_trained = False
        
    async def fit(self, interaction_matrix: np.ndarray, user_ids: List[str], 
                  item_ids: List[str], epochs: int = 100) -> None:
        """Train collaborative filtering model"""        try:
            n_users, n_items = interaction_matrix.shape
            
            # Initialize parameters
            self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
            self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))
            self.user_biases = np.zeros(n_users)
            self.item_biases = np.zeros(n_items)
            self.global_bias = np.mean(interaction_matrix[interaction_matrix > 0])
            
            # Stochastic Gradient Descent
            for epoch in range(epochs):
                for user_idx in range(n_users):
                    for item_idx in range(n_items):
                        if interaction_matrix[user_idx, item_idx] > 0:
                            prediction = await self._predict_rating(user_idx, item_idx)
                            error = interaction_matrix[user_idx, item_idx] - prediction
                            
                            # Update parameters
                            user_factor = self.user_factors[user_idx].copy()
                            item_factor = self.item_factors[item_idx].copy()
                            
                            self.user_factors[user_idx] += self.learning_rate * (
                                error * item_factor
                            )
                            self.item_factors[item_idx] += self.learning_rate * (
                                error * user_factor
                            )
                            self.user_biases[user_idx] += self.learning_rate * error
                            self.item_biases[item_idx] += self.learning_rate * error
            
            self.is_trained = True
            logger.info("Collaborative filtering model trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train collaborative filtering model: {e}")
            raise ModelTrainingError(f"CF training failed: {e}")
    
    async def _predict_rating(self, user_idx: int, item_idx: int) -> float:
        """Predict rating for user-item pair"""        if not self.is_trained:
            return self.global_bias
        
        user_item_interaction = np.dot(
            self.user_factors[user_idx], 
            self.item_factors[item_idx]
        )
        
        prediction = (
            self.global_bias + 
            self.user_biases[user_idx] + 
            self.item_biases[item_idx] + 
            user_item_interaction
        )
        
        return prediction
    
    async def predict_preferences(self, user_idx: int, 
                                  item_indices: List[int]) -> List[float]:
        """Predict preferences for multiple items"""        predictions = []
        for item_idx in item_indices:
            prediction = await self._predict_rating(user_idx, item_idx)
            predictions.append(prediction)
        return predictions


class ContentBasedFilteringEngine:
    """Advanced content-based filtering implementation"""    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
        self.content_features = None
        self.similarity_matrix = None
        self.is_trained = False
        
    async def fit(self, content_features: Dict[str, Dict[str, Any]]) -> None:
        """Train content-based filtering model"""        try:
            # Extract text features
            item_ids = list(content_features.keys())
            text_content = []
            
            for item_id in item_ids:
                features = content_features[item_id]
                combined_text = " ".join([
                    str(features.get('title', '')),
                    str(features.get('description', '')),
                    str(features.get('tags', '')),
                    str(features.get('category', ''))
                ])
                text_content.append(combined_text)
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(text_content)
            
            # Calculate similarity matrix
            self.similarity_matrix = cosine_similarity(tfidf_matrix)
            self.content_features = content_features
            self.is_trained = True
            
            logger.info("Content-based filtering model trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train content-based model: {e}")
            raise ModelTrainingError(f"CBF training failed: {e}")
    
    async def find_similar_items(self, item_id: str, 
                                 top_k: int = 10) -> List[Tuple[str, float]]:
        """Find similar items based on content"""        if not self.is_trained:
            return []
        
        item_ids = list(self.content_features.keys())
        if item_id not in item_ids:
            return []
        
        item_idx = item_ids.index(item_id)
        similarities = self.similarity_matrix[item_idx]
        
        # Get top similar items
        similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
        similar_items = [
            (item_ids[idx], similarities[idx]) 
            for idx in similar_indices
        ]
        
        return similar_items


class HybridRecommendationEngine:
    """Hybrid recommendation combining multiple algorithms"""    
    def __init__(self):
        self.collaborative_engine = CollaborativeFilteringEngine()
        self.content_engine = ContentBasedFilteringEngine()
        self.deep_model = None
        self.ensemble_weights = {
            'collaborative': 0.4,
            'content_based': 0.3,
            'deep_learning': 0.3
        }
        self.is_trained = False
    
    async def fit(self, interactions: List[UserInteraction], 
                  content_features: Dict[str, Dict[str, Any]]) -> None:
        """Train hybrid recommendation model"""        try:
            # Prepare interaction matrix
            interaction_matrix, user_ids, item_ids = await self._prepare_interaction_matrix(
                interactions
            )
            
            # Train collaborative filtering
            await self.collaborative_engine.fit(interaction_matrix, user_ids, item_ids)
            
            # Train content-based filtering
            await self.content_engine.fit(content_features)
            
            # Train deep learning model
            self.deep_model = await self._train_deep_model(interactions, content_features)
            
            self.is_trained = True
            logger.info("Hybrid recommendation model trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train hybrid model: {e}")
            raise ModelTrainingError(f"Hybrid training failed: {e}")
    
    async def predict_preference(self, user_id: str, item_id: str, 
                                 user_context: Dict[str, Any]) -> PreferencePrediction:
        """Predict user preference for item using hybrid approach"""        if not self.is_trained:
            raise PreferenceLearningError("Model not trained")
        
        try:
            predictions = {}
            
            # Collaborative filtering prediction
            cf_prediction = await self._get_collaborative_prediction(user_id, item_id)
            predictions['collaborative'] = cf_prediction
            
            # Content-based prediction
            cb_prediction = await self._get_content_based_prediction(user_id, item_id)
            predictions['content_based'] = cb_prediction
            
            # Deep learning prediction
            dl_prediction = await self._get_deep_learning_prediction(
                user_id, item_id, user_context
            )
            predictions['deep_learning'] = dl_prediction
            
            # Combine predictions
            final_prediction = sum(
                predictions[method] * self.ensemble_weights[method]
                for method in predictions
            )
            
            # Calculate confidence
            confidence_score = await self._calculate_prediction_confidence(predictions)
            
            # Get similar users for explanation
            similar_users = await self._get_similar_users(user_id, top_k=5)
            
            # Generate explanation
            explanation = await self._generate_prediction_explanation(
                predictions, self.ensemble_weights
            )
            
            return PreferencePrediction(
                user_id=user_id,
                item_id=item_id,
                predicted_rating=final_prediction,
                confidence_score=confidence_score,
                prediction_factors=predictions,
                similar_users=similar_users,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise PreferenceLearningError(f"Failed to predict preference: {e}")


class PreferenceLearningEngine(BaseService):
    """    Advanced preference learning engine with multiple ML algorithms
    """    
    def __init__(self, vector_store: VectorStore, redis_cache: RedisCache):
        super().__init__()
        self.vector_store = vector_store
        self.redis_cache = redis_cache
        self.hybrid_engine = HybridRecommendationEngine()
        self.feature_engineer = FeatureEngineer()
        
        # Configuration
        self.min_interactions_for_training = 100
        self.model_retrain_interval = timedelta(days=1)
        self.preference_update_threshold = 0.1
        
        # Model storage
        self.trained_models: Dict[str, PreferenceModel] = {}
        self.user_embeddings: Dict[str, np.ndarray] = {}
        self.item_embeddings: Dict[str, np.ndarray] = {}
        
        logger.info("PreferenceLearningEngine initialized")
    
    async def initialize(self) -> None:
        """Initialize preference learning engine"""        try:
            await self._load_existing_models()
            await self._initialize_embeddings()
            
            logger.info("PreferenceLearningEngine initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize PreferenceLearningEngine: {e}")
            raise PreferenceLearningError(f"Initialization failed: {e}")
    
    async def learn_user_preferences(
        self,
        user_id: str,
        interactions: List[UserInteraction],
        context: LearningContext
    ) -> PreferenceUpdate:
        """        Learn and update user preferences from interactions
        
        Args:
            user_id: User identifier
            interactions: User interaction history
            context: Learning context and parameters
            
        Returns:
            Preference update result
        """        try:
            # Get current preferences
            current_preferences = await self._get_current_preferences(user_id)
            
            # Extract features from interactions
            interaction_features = await self._extract_interaction_features(
                interactions, context
            )
            
            # Apply preference learning algorithms
            learned_preferences = await self._apply_learning_algorithms(
                user_id, interaction_features, context
            )
            
            # Validate preference changes
            validated_preferences = await self._validate_preference_changes(
                current_preferences, learned_preferences, context.confidence_threshold
            )
            
            # Calculate confidence change
            confidence_change = await self._calculate_confidence_change(
                current_preferences, validated_preferences
            )
            
            # Update user preferences
            await self._update_user_preferences(user_id, validated_preferences)
            
            # Update embeddings
            await self._update_user_embeddings(user_id, validated_preferences)
            
            # Cache updated preferences
            await self._cache_user_preferences(user_id, validated_preferences)
            
            return PreferenceUpdate(
                user_id=user_id,
                preference_type=PreferenceType.CONTENT_TYPE,  # This would be dynamic
                old_preferences=current_preferences,
                new_preferences=validated_preferences,
                confidence_change=confidence_change,
                update_reason="interaction_based_learning"
            )
            
        except Exception as e:
            logger.error(f"Failed to learn user preferences: {e}")
            raise PreferenceLearningError(f"Preference learning failed: {e}")
    
    async def predict_user_preference(
        self,
        user_id: str,
        item_id: str,
        context: Dict[str, Any]
    ) -> PreferencePrediction:
        """        Predict user preference for specific item
        
        Args:
            user_id: User identifier
            item_id: Item identifier
            context: Prediction context
            
        Returns:
            Preference prediction with confidence
        """        try:
            # Use hybrid recommendation engine
            prediction = await self.hybrid_engine.predict_preference(
                user_id, item_id, context
            )
            
            # Cache prediction
            await self._cache_prediction(user_id, item_id, prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict preference: {e}")
            raise PreferenceLearningError(f"Preference prediction failed: {e}")
    
    async def train_preference_models(
        self,
        interactions: List[UserInteraction],
        content_features: Dict[str, Dict[str, Any]],
        algorithm: LearningAlgorithm = LearningAlgorithm.HYBRID
    ) -> PreferenceModel:
        """        Train preference learning models
        
        Args:
            interactions: Training interaction data
            content_features: Content feature data
            algorithm: Learning algorithm to use
            
        Returns:
            Trained preference model
        """        try:
            if len(interactions) < self.min_interactions_for_training:
                raise PreferenceLearningError(
                    f"Insufficient training data: {len(interactions)} interactions"
                )
            
            # Prepare training data
            training_data = await self._prepare_training_data(
                interactions, content_features
            )
            
            # Train model based on algorithm
            if algorithm == LearningAlgorithm.HYBRID:
                await self.hybrid_engine.fit(interactions, content_features)
                model_data = self.hybrid_engine
            else:
                model_data = await self._train_specific_algorithm(
                    algorithm, training_data
                )
            
            # Evaluate model performance
            performance_metrics = await self._evaluate_model_performance(
                model_data, training_data
            )
            
            # Create model object
            model = PreferenceModel(
                model_id=f"pref_model_{algorithm.value}_{datetime.now().isoformat()}",
                algorithm=algorithm,
                model_data=model_data,
                feature_names=list(training_data.get('features', {}).keys()),
                performance_metrics=performance_metrics,
                training_timestamp=datetime.now(),
                version="1.0.0"
            )
            
            # Store model
            self.trained_models[model.model_id] = model
            await self._save_model(model)
            
            logger.info(f"Preference model trained: {model.model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to train preference model: {e}")
            raise ModelTrainingError(f"Model training failed: {e}")


# Factory functions
def create_preference_engine(
    vector_store: VectorStore,
    redis_cache: RedisCache
) -> PreferenceLearningEngine:
    """Create preference learning engine instance"""    return PreferenceLearningEngine(vector_store, redis_cache)


async def train_preference_model(
    engine: PreferenceLearningEngine,
    interactions: List[UserInteraction],
    content_features: Dict[str, Dict[str, Any]],
    algorithm: LearningAlgorithm = LearningAlgorithm.HYBRID
) -> PreferenceModel:
    """Train preference model using engine"""    return await engine.train_preference_models(
        interactions, content_features, algorithm
    )
