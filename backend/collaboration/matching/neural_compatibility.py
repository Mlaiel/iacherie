"""Neural Compatibility Engine - Deep Learning Creator Compatibility Analysis
===========================================================================

Advanced neural network system for predicting creator compatibility using:
- Deep neural networks for complex pattern recognition
- Multi-layer perceptrons for feature learning
- Attention mechanisms for important feature weighting
- Transformer architectures for sequence modeling
- Real-time inference optimization

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

logger = logging.getLogger(__name__)


class NetworkArchitecture(Enum):
    """Available neural network architectures"""
    FEEDFORWARD = "feedforward"
    DEEP_MLP = "deep_mlp"
    AUTOENCODER = "autoencoder"
    TRANSFORMER = "transformer"
    ATTENTION = "attention"
    LSTM = "lstm"


@dataclass
class NeuralFeatures:
    """Neural network feature representation"""
    creator_id: str
    embedding_vector: np.ndarray = field(default_factory=lambda: np.array([]))
    behavioral_patterns: np.ndarray = field(default_factory=lambda: np.array([]))
    content_embeddings: np.ndarray = field(default_factory=lambda: np.array([]))
    interaction_history: np.ndarray = field(default_factory=lambda: np.array([]))
    temporal_sequences: np.ndarray = field(default_factory=lambda: np.array([]))
    social_graph_features: np.ndarray = field(default_factory=lambda: np.array([]))
    attention_weights: Dict[str, float] = field(default_factory=dict)
    
    def get_combined_vector(self) -> np.ndarray:
        """Combine all neural features into single vector"""
        vectors = []
        
        if self.embedding_vector.size > 0:
            vectors.append(self.embedding_vector.flatten())
        if self.behavioral_patterns.size > 0:
            vectors.append(self.behavioral_patterns.flatten())
        if self.content_embeddings.size > 0:
            vectors.append(self.content_embeddings.flatten())
        if self.interaction_history.size > 0:
            vectors.append(self.interaction_history.flatten())
        if self.temporal_sequences.size > 0:
            vectors.append(self.temporal_sequences.flatten())
        if self.social_graph_features.size > 0:
            vectors.append(self.social_graph_features.flatten())
        
        if vectors:
            return np.concatenate(vectors)
        else:
            return np.zeros(128)  # Default embedding size


@dataclass
class CompatibilityPrediction:
    """Neural network compatibility prediction result"""
    creator_a_id: str
    creator_b_id: str
    compatibility_score: float
    confidence: float
    attention_map: Dict[str, float] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    prediction_explanation: str = ""
    neural_activations: Dict[str, np.ndarray] = field(default_factory=dict)
    architecture_used: NetworkArchitecture = NetworkArchitecture.FEEDFORWARD
    
    def get_explanation(self) -> str:
        """Generate human-readable explanation"""
        if self.prediction_explanation:
            return self.prediction_explanation
        
        if self.compatibility_score >= 0.8:
            return f"High compatibility ({self.compatibility_score:.2f}) with strong feature alignment"
        elif self.compatibility_score >= 0.6:
            return f"Moderate compatibility ({self.compatibility_score:.2f}) with some complementary aspects"
        else:
            return f"Low compatibility ({self.compatibility_score:.2f}) with significant differences"


class CompatibilityNeuralNetwork:
    """
    Deep neural network for creator compatibility prediction
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize neural network"""
        self.config = config or {}
        self.architecture = NetworkArchitecture(self.config.get('architecture', 'feedforward'))
        self.input_dim = self.config.get('input_dim', 256)
        self.hidden_dims = self.config.get('hidden_dims', [128, 64, 32])
        self.output_dim = self.config.get('output_dim', 1)
        self.learning_rate = self.config.get('learning_rate', 0.001)
        self.dropout_rate = self.config.get('dropout_rate', 0.2)
        
        self.model = None
        self.is_trained = False
        self.training_history = []
        
        logger.info(f"🧠 Neural Network initialized with {self.architecture.value} architecture")
    
    async def build_model(self):
        """Build neural network model"""
        try:
            if self.architecture == NetworkArchitecture.FEEDFORWARD:
                await self._build_feedforward()
            elif self.architecture == NetworkArchitecture.DEEP_MLP:
                await self._build_deep_mlp()
            elif self.architecture == NetworkArchitecture.AUTOENCODER:
                await self._build_autoencoder()
            elif self.architecture == NetworkArchitecture.TRANSFORMER:
                await self._build_transformer()
            elif self.architecture == NetworkArchitecture.ATTENTION:
                await self._build_attention()
            elif self.architecture == NetworkArchitecture.LSTM:
                await self._build_lstm()
            
            logger.info(f"✅ Neural network model built successfully")
            
        except Exception as e:
            logger.error(f"❌ Error building neural network: {e}")
            # Fallback to simple model
            await self._build_simple_fallback()
    
    async def _build_feedforward(self):
        """Build feedforward neural network"""
        try:
            # Try TensorFlow/Keras first
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            model = models.Sequential([
                layers.Dense(self.hidden_dims[0], activation='relu', input_shape=(self.input_dim,)),
                layers.Dropout(self.dropout_rate),
                layers.Dense(self.hidden_dims[1], activation='relu'),
                layers.Dropout(self.dropout_rate),
                layers.Dense(self.hidden_dims[2], activation='relu'),
                layers.Dense(self.output_dim, activation='sigmoid')
            ])
            
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            self.model = model
            
        except ImportError:
            logger.warning("⚠️ TensorFlow not available, using sklearn alternative")
            await self._build_sklearn_mlp()
    
    async def _build_deep_mlp(self):
        """Build deep multi-layer perceptron"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            # Deeper network with more layers
            model = models.Sequential([
                layers.Dense(256, activation='relu', input_shape=(self.input_dim,)),
                layers.BatchNormalization(),
                layers.Dropout(self.dropout_rate),
                
                layers.Dense(128, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(self.dropout_rate),
                
                layers.Dense(64, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(self.dropout_rate),
                
                layers.Dense(32, activation='relu'),
                layers.Dropout(self.dropout_rate),
                
                layers.Dense(16, activation='relu'),
                layers.Dense(self.output_dim, activation='sigmoid')
            ])
            
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            self.model = model
            
        except ImportError:
            await self._build_sklearn_mlp()
    
    async def _build_autoencoder(self):
        """Build autoencoder for feature learning"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            # Encoder
            encoder_input = layers.Input(shape=(self.input_dim,))
            encoded = layers.Dense(128, activation='relu')(encoder_input)
            encoded = layers.Dense(64, activation='relu')(encoded)
            encoded = layers.Dense(32, activation='relu')(encoded)
            
            # Decoder
            decoded = layers.Dense(64, activation='relu')(encoded)
            decoded = layers.Dense(128, activation='relu')(decoded)
            decoded = layers.Dense(self.input_dim, activation='sigmoid')(decoded)
            
            # Autoencoder model
            autoencoder = models.Model(encoder_input, decoded)
            
            # Encoder model for feature extraction
            encoder = models.Model(encoder_input, encoded)
            
            # Classifier on top of encoder
            classifier_input = layers.Input(shape=(32,))
            classifier_output = layers.Dense(16, activation='relu')(classifier_input)
            classifier_output = layers.Dense(1, activation='sigmoid')(classifier_output)
            classifier = models.Model(classifier_input, classifier_output)
            
            # Combined model
            combined_output = classifier(encoder(encoder_input))
            self.model = models.Model(encoder_input, combined_output)
            
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
        except ImportError:
            await self._build_sklearn_mlp()
    
    async def _build_transformer(self):
        """Build transformer architecture for sequential data"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            # Multi-head attention layer
            class MultiHeadAttention(layers.Layer):
                def __init__(self, d_model, num_heads):
                    super().__init__()
                    self.num_heads = num_heads
                    self.d_model = d_model
                    self.depth = d_model // num_heads
                    
                    self.wq = layers.Dense(d_model)
                    self.wk = layers.Dense(d_model)
                    self.wv = layers.Dense(d_model)
                    self.dense = layers.Dense(d_model)
                
                def call(self, inputs):
                    q = self.wq(inputs)
                    k = self.wk(inputs)
                    v = self.wv(inputs)
                    
                    attention_output = tf.nn.scaled_dot_product_attention(q, k, v)
                    return self.dense(attention_output)
            
            # Transformer block
            inputs = layers.Input(shape=(self.input_dim,))
            
            # Reshape for attention
            reshaped = layers.Reshape((self.input_dim // 8, 8))(inputs)
            
            # Multi-head attention
            attention = MultiHeadAttention(8, 2)(reshaped)
            
            # Flatten and process
            flattened = layers.Flatten()(attention)
            dense1 = layers.Dense(64, activation='relu')(flattened)
            dropout1 = layers.Dropout(self.dropout_rate)(dense1)
            dense2 = layers.Dense(32, activation='relu')(dropout1)
            output = layers.Dense(1, activation='sigmoid')(dense2)
            
            self.model = models.Model(inputs, output)
            
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
        except Exception:
            await self._build_sklearn_mlp()
    
    async def _build_attention(self):
        """Build attention-based network"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            inputs = layers.Input(shape=(self.input_dim,))
            
            # Attention mechanism
            attention_weights = layers.Dense(self.input_dim, activation='softmax')(inputs)
            attended_features = layers.Multiply()([inputs, attention_weights])
            
            # Dense layers
            dense1 = layers.Dense(128, activation='relu')(attended_features)
            dropout1 = layers.Dropout(self.dropout_rate)(dense1)
            dense2 = layers.Dense(64, activation='relu')(dropout1)
            dropout2 = layers.Dropout(self.dropout_rate)(dense2)
            dense3 = layers.Dense(32, activation='relu')(dropout2)
            output = layers.Dense(1, activation='sigmoid')(dense3)
            
            self.model = models.Model(inputs, output)
            
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
        except ImportError:
            await self._build_sklearn_mlp()
    
    async def _build_lstm(self):
        """Build LSTM for temporal sequences"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            # Reshape input for LSTM
            inputs = layers.Input(shape=(self.input_dim,))
            reshaped = layers.Reshape((self.input_dim // 16, 16))(inputs)
            
            # LSTM layers
            lstm1 = layers.LSTM(64, return_sequences=True)(reshaped)
            dropout1 = layers.Dropout(self.dropout_rate)(lstm1)
            lstm2 = layers.LSTM(32)(dropout1)
            dropout2 = layers.Dropout(self.dropout_rate)(lstm2)
            
            # Dense layers
            dense1 = layers.Dense(16, activation='relu')(dropout2)
            output = layers.Dense(1, activation='sigmoid')(dense1)
            
            self.model = models.Model(inputs, output)
            
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
        except ImportError:
            await self._build_sklearn_mlp()
    
    async def _build_sklearn_mlp(self):
        """Build MLP using scikit-learn as fallback"""
        try:
            from sklearn.neural_network import MLPClassifier
            
            self.model = MLPClassifier(
                hidden_layer_sizes=tuple(self.hidden_dims),
                activation='relu',
                solver='adam',
                learning_rate_init=self.learning_rate,
                max_iter=500,
                random_state=42
            )
            
        except ImportError:
            await self._build_simple_fallback()
    
    async def _build_simple_fallback(self):
        """Simple fallback model when deep learning libraries unavailable"""
        logger.warning("⚠️ Using simple fallback model")
        
        class SimpleFallbackModel:
            def __init__(self):
                self.weights = np.random.randn(256) * 0.1
                self.bias = 0.0
            
            def predict(self, X):
                if len(X.shape) == 1:
                    X = X.reshape(1, -1)
                
                # Ensure X has correct dimensions
                if X.shape[1] != len(self.weights):
                    # Resize or pad input
                    if X.shape[1] > len(self.weights):
                        X = X[:, :len(self.weights)]
                    else:
                        padding = np.zeros((X.shape[0], len(self.weights) - X.shape[1]))
                        X = np.hstack([X, padding])
                
                scores = np.dot(X, self.weights) + self.bias
                return 1 / (1 + np.exp(-scores))  # Sigmoid activation
            
            def fit(self, X, y):
                # Simple gradient descent
                for _ in range(100):
                    predictions = self.predict(X)
                    errors = y - predictions
                    
                    # Update weights
                    for i in range(len(self.weights)):
                        if i < X.shape[1]:
                            gradient = np.mean(errors * X[:, i])
                            self.weights[i] += 0.01 * gradient
                    
                    # Update bias
                    self.bias += 0.01 * np.mean(errors)
        
        self.model = SimpleFallbackModel()
    
    async def train(self, X_train: np.ndarray, y_train: np.ndarray, 
                   X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        """Train the neural network"""
        try:
            logger.info("🚀 Starting neural network training...")
            
            if hasattr(self.model, 'fit'):
                # For scikit-learn or simple models
                self.model.fit(X_train, y_train)
                self.is_trained = True
                
            else:
                # For TensorFlow/Keras models
                validation_data = (X_val, y_val) if X_val is not None else None
                
                history = self.model.fit(
                    X_train, y_train,
                    validation_data=validation_data,
                    epochs=self.config.get('epochs', 50),
                    batch_size=self.config.get('batch_size', 32),
                    verbose=0
                )
                
                self.training_history = history.history
                self.is_trained = True
            
            logger.info("✅ Neural network training completed")
            
        except Exception as e:
            logger.error(f"❌ Error training neural network: {e}")
    
    async def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the neural network"""
        if not self.is_trained:
            logger.warning("⚠️ Model not trained, using random predictions")
            return np.random.rand(len(X))
        
        try:
            if hasattr(self.model, 'predict_proba'):
                # For scikit-learn models
                predictions = self.model.predict_proba(X)
                return predictions[:, 1] if predictions.shape[1] > 1 else predictions.flatten()
            else:
                # For TensorFlow/Keras or simple models
                predictions = self.model.predict(X)
                return predictions.flatten()
                
        except Exception as e:
            logger.error(f"❌ Error making predictions: {e}")
            return np.random.rand(len(X))


class NeuralCompatibilityEngine:
    """
    Neural network-powered creator compatibility engine
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize neural compatibility engine"""
        self.config = config or {}
        self.networks = {}
        self.feature_extractors = {}
        self.ensemble_weights = {
            NetworkArchitecture.FEEDFORWARD: 0.3,
            NetworkArchitecture.DEEP_MLP: 0.4,
            NetworkArchitecture.ATTENTION: 0.3
        }
        
        # Performance tracking
        self.prediction_cache = {}
        self.performance_metrics = {}
        
        logger.info("🧠 Neural Compatibility Engine initialized")
    
    async def initialize(self):
        """Initialize all neural networks"""
        try:
            # Initialize multiple architectures for ensemble
            for architecture in [NetworkArchitecture.FEEDFORWARD, 
                               NetworkArchitecture.DEEP_MLP, 
                               NetworkArchitecture.ATTENTION]:
                
                network_config = self.config.copy()
                network_config['architecture'] = architecture.value
                
                network = CompatibilityNeuralNetwork(network_config)
                await network.build_model()
                
                self.networks[architecture] = network
            
            logger.info("✅ All neural networks initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing neural networks: {e}")
    
    async def extract_neural_features(self, creator_profile: Dict[str, Any]) -> NeuralFeatures:
        """Extract neural network features from creator profile"""
        features = NeuralFeatures(creator_id=creator_profile['creator_id'])
        
        try:
            # Extract embedding vector (content + behavioral features)
            embedding_features = []
            
            # Content embeddings
            content_data = creator_profile.get('content_history', [])
            if content_data:
                # Simple content embedding (in production, use pre-trained embeddings)
                content_vector = self._extract_content_embeddings(content_data)
                embedding_features.extend(content_vector)
            
            # Behavioral patterns
            behavioral_data = creator_profile.get('behavioral_patterns', {})
            behavioral_vector = self._extract_behavioral_embeddings(behavioral_data)
            embedding_features.extend(behavioral_vector)
            
            # Engagement patterns
            engagement_data = creator_profile.get('engagement_history', [])
            engagement_vector = self._extract_engagement_embeddings(engagement_data)
            embedding_features.extend(engagement_vector)
            
            # Social graph features
            social_data = creator_profile.get('social_connections', {})
            social_vector = self._extract_social_embeddings(social_data)
            embedding_features.extend(social_vector)
            
            # Pad or truncate to fixed size
            target_size = 128
            if len(embedding_features) > target_size:
                embedding_features = embedding_features[:target_size]
            else:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            
            features.embedding_vector = np.array(embedding_features, dtype=np.float32)
            
            # Extract behavioral patterns
            features.behavioral_patterns = self._extract_behavioral_patterns(creator_profile)
            
            # Extract content embeddings
            features.content_embeddings = self._extract_content_patterns(creator_profile)
            
            # Extract interaction history
            features.interaction_history = self._extract_interaction_patterns(creator_profile)
            
            # Extract temporal sequences
            features.temporal_sequences = self._extract_temporal_patterns(creator_profile)
            
            # Extract social graph features
            features.social_graph_features = self._extract_social_graph_features(creator_profile)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting neural features: {e}")
            return features
    
    def _extract_content_embeddings(self, content_data: List[Dict]) -> List[float]:
        """Extract content embeddings from content history"""
        embeddings = []
        
        for content in content_data[:10]:  # Last 10 pieces of content
            # Simple feature extraction (in production, use NLP models)
            length = content.get('length', 0)
            engagement = content.get('engagement_rate', 0)
            sentiment = content.get('sentiment_score', 0)
            category = hash(content.get('category', '')) % 100 / 100.0
            
            embeddings.extend([length / 1000.0, engagement, sentiment, category])
        
        return embeddings
    
    def _extract_behavioral_embeddings(self, behavioral_data: Dict) -> List[float]:
        """Extract behavioral embeddings"""
        return [
            behavioral_data.get('posting_frequency', 0) / 10.0,
            behavioral_data.get('response_time', 0) / 24.0,  # Normalize to hours
            behavioral_data.get('consistency_score', 0),
            behavioral_data.get('collaboration_frequency', 0) / 5.0,
            behavioral_data.get('engagement_consistency', 0)
        ]
    
    def _extract_engagement_embeddings(self, engagement_data: List[Dict]) -> List[float]:
        """Extract engagement pattern embeddings"""
        if not engagement_data:
            return [0.0] * 8
        
        recent_data = engagement_data[-30:]  # Last 30 data points
        
        likes = [d.get('likes', 0) for d in recent_data]
        comments = [d.get('comments', 0) for d in recent_data]
        shares = [d.get('shares', 0) for d in recent_data]
        
        return [
            np.mean(likes) / 1000.0,
            np.std(likes) / 1000.0,
            np.mean(comments) / 100.0,
            np.std(comments) / 100.0,
            np.mean(shares) / 100.0,
            np.std(shares) / 100.0,
            len(recent_data) / 30.0,  # Data completeness
            np.corrcoef([likes, comments])[0, 1] if len(likes) > 1 else 0.0
        ]
    
    def _extract_social_embeddings(self, social_data: Dict) -> List[float]:
        """Extract social network embeddings"""
        return [
            social_data.get('follower_count', 0) / 10000.0,
            social_data.get('following_count', 0) / 1000.0,
            social_data.get('network_density', 0),
            social_data.get('influence_score', 0),
            social_data.get('community_size', 0) / 100.0
        ]
    
    def _extract_behavioral_patterns(self, creator_profile: Dict) -> np.ndarray:
        """Extract behavioral pattern sequences"""
        patterns = []
        
        # Weekly posting patterns
        weekly_patterns = creator_profile.get('weekly_posting_pattern', [0] * 7)
        patterns.extend(weekly_patterns)
        
        # Hourly activity patterns
        hourly_patterns = creator_profile.get('hourly_activity_pattern', [0] * 24)
        patterns.extend(hourly_patterns[:12])  # First 12 hours only
        
        # Monthly trends
        monthly_trends = creator_profile.get('monthly_trends', [0] * 12)
        patterns.extend(monthly_trends)
        
        return np.array(patterns, dtype=np.float32)
    
    def _extract_content_patterns(self, creator_profile: Dict) -> np.ndarray:
        """Extract content pattern sequences"""
        patterns = []
        
        # Content type distribution
        content_types = creator_profile.get('content_type_distribution', {})
        type_values = list(content_types.values())[:10]  # Top 10 content types
        patterns.extend(type_values)
        
        # Quality scores over time
        quality_history = creator_profile.get('quality_score_history', [])
        if quality_history:
            patterns.extend(quality_history[-10:])  # Last 10 quality scores
        
        # Pad to fixed size
        target_size = 32
        if len(patterns) > target_size:
            patterns = patterns[:target_size]
        else:
            patterns.extend([0.0] * (target_size - len(patterns)))
        
        return np.array(patterns, dtype=np.float32)
    
    def _extract_interaction_patterns(self, creator_profile: Dict) -> np.ndarray:
        """Extract interaction pattern sequences"""
        patterns = []
        
        # Collaboration interaction patterns
        collab_history = creator_profile.get('collaboration_interactions', [])
        for interaction in collab_history[-20:]:  # Last 20 interactions
            patterns.extend([
                interaction.get('duration_days', 0) / 30.0,
                interaction.get('communication_frequency', 0) / 10.0,
                interaction.get('satisfaction_score', 0),
                interaction.get('productivity_score', 0)
            ])
        
        # Pad to fixed size
        target_size = 80  # 20 interactions * 4 features
        if len(patterns) > target_size:
            patterns = patterns[:target_size]
        else:
            patterns.extend([0.0] * (target_size - len(patterns)))
        
        return np.array(patterns, dtype=np.float32)
    
    def _extract_temporal_patterns(self, creator_profile: Dict) -> np.ndarray:
        """Extract temporal sequence patterns"""
        patterns = []
        
        # Time-series engagement data
        engagement_timeseries = creator_profile.get('engagement_timeseries', [])
        for datapoint in engagement_timeseries[-30:]:  # Last 30 days
            patterns.extend([
                datapoint.get('likes_normalized', 0),
                datapoint.get('comments_normalized', 0),
                datapoint.get('shares_normalized', 0),
                datapoint.get('reach_normalized', 0)
            ])
        
        # Pad to fixed size
        target_size = 120  # 30 days * 4 metrics
        if len(patterns) > target_size:
            patterns = patterns[:target_size]
        else:
            patterns.extend([0.0] * (target_size - len(patterns)))
        
        return np.array(patterns, dtype=np.float32)
    
    def _extract_social_graph_features(self, creator_profile: Dict) -> np.ndarray:
        """Extract social graph features"""
        patterns = []
        
        # Network centrality measures
        network_data = creator_profile.get('network_analysis', {})
        patterns.extend([
            network_data.get('betweenness_centrality', 0),
            network_data.get('closeness_centrality', 0),
            network_data.get('degree_centrality', 0),
            network_data.get('eigenvector_centrality', 0),
            network_data.get('clustering_coefficient', 0)
        ])
        
        # Community features
        community_data = creator_profile.get('community_features', {})
        patterns.extend([
            community_data.get('community_size', 0) / 1000.0,
            community_data.get('community_engagement', 0),
            community_data.get('cross_community_influence', 0),
            community_data.get('authority_score', 0),
            community_data.get('hub_score', 0)
        ])
        
        # Pad to fixed size
        target_size = 16
        if len(patterns) > target_size:
            patterns = patterns[:target_size]
        else:
            patterns.extend([0.0] * (target_size - len(patterns)))
        
        return np.array(patterns, dtype=np.float32)
    
    async def predict_compatibility(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any],
        use_ensemble: bool = True
    ) -> CompatibilityPrediction:
        """Predict compatibility between two creators using neural networks"""
        
        try:
            # Extract features for both creators
            features_a = await self.extract_neural_features(creator_a)
            features_b = await self.extract_neural_features(creator_b)
            
            # Create combined feature vector
            combined_features = self._combine_features(features_a, features_b)
            
            if use_ensemble:
                prediction = await self._ensemble_predict(combined_features, features_a, features_b)
            else:
                # Use best performing single network
                best_architecture = max(self.networks.keys(), 
                                      key=lambda x: self.ensemble_weights.get(x, 0))
                prediction = await self._single_network_predict(
                    best_architecture, combined_features, features_a, features_b
                )
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting compatibility: {e}")
            
            # Fallback prediction
            return CompatibilityPrediction(
                creator_a_id=creator_a['creator_id'],
                creator_b_id=creator_b['creator_id'],
                compatibility_score=0.5,
                confidence=0.1,
                prediction_explanation="Error in neural prediction, using fallback"
            )
    
    def _combine_features(self, features_a: NeuralFeatures, features_b: NeuralFeatures) -> np.ndarray:
        """Combine features from two creators"""
        
        # Get combined vectors
        vector_a = features_a.get_combined_vector()
        vector_b = features_b.get_combined_vector()
        
        # Ensure same size
        max_size = max(len(vector_a), len(vector_b))
        if len(vector_a) < max_size:
            vector_a = np.pad(vector_a, (0, max_size - len(vector_a)))
        if len(vector_b) < max_size:
            vector_b = np.pad(vector_b, (0, max_size - len(vector_b)))
        
        # Combine using different strategies
        concatenated = np.concatenate([vector_a, vector_b])
        element_wise_diff = np.abs(vector_a - vector_b)
        element_wise_product = vector_a * vector_b
        
        # Final combined vector
        combined = np.concatenate([concatenated, element_wise_diff, element_wise_product])
        
        return combined
    
    async def _ensemble_predict(
        self,
        combined_features: np.ndarray,
        features_a: NeuralFeatures,
        features_b: NeuralFeatures
    ) -> CompatibilityPrediction:
        """Make ensemble prediction using multiple networks"""
        
        predictions = {}
        weights_sum = 0
        
        for architecture, network in self.networks.items():
            if network.is_trained:
                try:
                    weight = self.ensemble_weights.get(architecture, 0)
                    pred = await network.predict(combined_features.reshape(1, -1))
                    predictions[architecture] = float(pred[0]) * weight
                    weights_sum += weight
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error with {architecture}: {e}")
        
        # Calculate weighted average
        if weights_sum > 0:
            ensemble_score = sum(predictions.values()) / weights_sum
        else:
            ensemble_score = 0.5  # Default fallback
        
        # Calculate confidence based on agreement between models
        if len(predictions) > 1:
            pred_values = list(predictions.values())
            confidence = 1.0 - (np.std(pred_values) / np.mean(pred_values)) if np.mean(pred_values) > 0 else 0.5
        else:
            confidence = 0.7  # Single model confidence
        
        return CompatibilityPrediction(
            creator_a_id=features_a.creator_id,
            creator_b_id=features_b.creator_id,
            compatibility_score=ensemble_score,
            confidence=confidence,
            feature_importance=self._calculate_feature_importance(combined_features),
            architecture_used=NetworkArchitecture.ENSEMBLE
        )
    
    async def _single_network_predict(
        self,
        architecture: NetworkArchitecture,
        combined_features: np.ndarray,
        features_a: NeuralFeatures,
        features_b: NeuralFeatures
    ) -> CompatibilityPrediction:
        """Make prediction using single neural network"""
        
        network = self.networks[architecture]
        
        try:
            prediction = await network.predict(combined_features.reshape(1, -1))
            score = float(prediction[0])
            
            return CompatibilityPrediction(
                creator_a_id=features_a.creator_id,
                creator_b_id=features_b.creator_id,
                compatibility_score=score,
                confidence=score,
                feature_importance=self._calculate_feature_importance(combined_features),
                architecture_used=architecture
            )
            
        except Exception as e:
            logger.error(f"❌ Error with {architecture} prediction: {e}")
            
            return CompatibilityPrediction(
                creator_a_id=features_a.creator_id,
                creator_b_id=features_b.creator_id,
                compatibility_score=0.5,
                confidence=0.1,
                architecture_used=architecture
            )
    
    def _calculate_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance scores"""
        
        # Simple feature importance based on magnitude
        feature_names = [
            'content_embeddings', 'behavioral_patterns', 'engagement_patterns',
            'social_features', 'temporal_patterns', 'interaction_history'
        ]
        
        # Split features into segments
        segment_size = len(features) // len(feature_names)
        importance = {}
        
        for i, name in enumerate(feature_names):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < len(feature_names) - 1 else len(features)
            
            segment = features[start_idx:end_idx]
            importance[name] = float(np.mean(np.abs(segment)))
        
        return importance
    
    async def train_networks(self, training_data: List[Dict[str, Any]]):
        """Train all neural networks with historical data"""
        try:
            logger.info("🚀 Starting neural network training...")
            
            # Prepare training data
            X, y = await self._prepare_neural_training_data(training_data)
            
            if len(X) < 20:
                logger.warning("⚠️ Insufficient training data for neural networks")
                return
            
            # Split data
            from sklearn.model_selection import train_test_split
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train each network
            for architecture, network in self.networks.items():
                try:
                    await network.train(X_train, y_train, X_val, y_val)
                    logger.info(f"✅ {architecture.value} training completed")
                    
                except Exception as e:
                    logger.error(f"❌ Error training {architecture.value}: {e}")
            
            logger.info("🎯 Neural network training completed")
            
        except Exception as e:
            logger.error(f"❌ Error in neural network training: {e}")
    
    async def _prepare_neural_training_data(
        self, 
        training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for neural networks"""
        
        X, y = [], []
        
        for sample in training_data:
            try:
                # Extract features
                features_a = await self.extract_neural_features(sample['creator_a'])
                features_b = await self.extract_neural_features(sample['creator_b'])
                
                # Combine features
                combined = self._combine_features(features_a, features_b)
                
                X.append(combined)
                y.append(int(sample['successful_collaboration']))
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing training sample: {e}")
        
        return np.array(X), np.array(y)
    
    async def batch_predict_compatibility(
        self,
        query_creator: Dict[str, Any],
        candidate_creators: List[Dict[str, Any]]
    ) -> List[CompatibilityPrediction]:
        """Batch predict compatibility for multiple candidates"""
        
        predictions = []
        
        # Extract query features once
        query_features = await self.extract_neural_features(query_creator)
        
        for candidate in candidate_creators:
            try:
                prediction = await self.predict_compatibility(query_creator, candidate)
                predictions.append(prediction)
                
            except Exception as e:
                logger.warning(f"⚠️ Error predicting for candidate {candidate.get('creator_id')}: {e}")
        
        return predictions
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all networks"""
        metrics = {}
        
        for architecture, network in self.networks.items():
            if network.is_trained:
                metrics[architecture.value] = {
                    'training_history': network.training_history,
                    'ensemble_weight': self.ensemble_weights.get(architecture, 0),
                    'architecture_config': network.config
                }
        
        return metrics
    
    async def update_ensemble_weights(self, performance_feedback: Dict[str, float]):
        """Update ensemble weights based on real-world performance"""
        try:
            total_feedback = sum(performance_feedback.values())
            
            if total_feedback > 0:
                for arch_name, feedback in performance_feedback.items():
                    try:
                        architecture = NetworkArchitecture(arch_name)
                        if architecture in self.ensemble_weights:
                            # Weighted update
                            current_weight = self.ensemble_weights[architecture]
                            normalized_feedback = feedback / total_feedback
                            self.ensemble_weights[architecture] = 0.8 * current_weight + 0.2 * normalized_feedback
                    except ValueError:
                        continue
                
                # Normalize weights
                total_weight = sum(self.ensemble_weights.values())
                if total_weight > 0:
                    for architecture in self.ensemble_weights:
                        self.ensemble_weights[architecture] /= total_weight
                
                logger.info("🔄 Neural network ensemble weights updated")
            
        except Exception as e:
            logger.error(f"❌ Error updating ensemble weights: {e}")