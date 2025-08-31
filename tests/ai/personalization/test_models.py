# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Machine Learning Models Tests

Comprehensive tests for all ML models used in personalization.
Tests collaborative filtering, content-based, hybrid, and deep learning models.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import IsolatedAsyncioTestCase
import numpy as np
import torch
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import time
import os
import sys

# Import the models modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.models import (
    PersonalizationMLModel,
    CollaborativeFilteringModel,
    ContentBasedModel,
    HybridRecommenderModel,
    DeepPersonalizationModel,
    UserEmbeddingModel,
    BasePersonalizationModel,
    ModelType,
    TrainingStatus,
    ModelMetrics,
    ModelConfig
)
from ai.personalization.exceptions import (
    ModelTrainingError,
    ModelNotLoadedError,
    InsufficientDataError
)


class TestPersonalizationMLModel(IsolatedAsyncioTestCase):
    """Base tests for PersonalizationMLModel abstract class"""
    async def asyncSetUp(self):
        """Set up test environment"""        # Test with concrete implementation (CollaborativeFilteringModel)
        self.model = CollaborativeFilteringModel(
            n_factors=20,
            learning_rate=0.01,
            regularization=0.001
        )

    async def test_model_initialization(self):
        """Test model proper initialization"""        self.assertIsNotNone(self.model)
        self.assertEqual(self.model.model_type, ModelType.COLLABORATIVE_FILTERING)
        self.assertFalse(self.model.is_trained)
        self.assertIsNone(self.model.training_history)

    async def test_model_configuration(self):
        """Test model configuration management"""        config = self.model.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('n_factors', config)
        self.assertIn('learning_rate', config)
        self.assertIn('regularization', config)

    async def test_model_state_management(self):
        """Test model state save/load functionality"""        # Generate some dummy training to create state
        training_data = self._generate_training_data(100, 50)
        await self.model.train(training_data)
        
        # Save state
        state_dict = await self.model.save_state()
        self.assertIsInstance(state_dict, dict)
        self.assertIn('model_weights', state_dict)
        self.assertIn('training_config', state_dict)
        self.assertIn('metadata', state_dict)
        
        # Create new model and load state
        new_model = CollaborativeFilteringModel(n_factors=20)
        await new_model.load_state(state_dict)
        
        self.assertTrue(new_model.is_trained)
        self.assertEqual(new_model.get_config()['n_factors'], 20)

    def _generate_training_data(self, n_users: int, n_items: int) -> Dict[str, Any]:
        """Generate synthetic training data"""        # Create user-item interaction matrix
        interactions = []
        for user_id in range(n_users):
            for item_id in range(n_items):
                if np.random.random() < 0.1:  # 10% interaction probability
                    rating = np.random.uniform(1.0, 5.0)
                    interactions.append({
                        'user_id': f'user_{user_id}',
                        'item_id': f'item_{item_id}',
                        'rating': rating,
                        'timestamp': datetime.utcnow()
                    })
        
        return {
            'interactions': interactions,
            'user_features': self._generate_user_features(n_users),
            'item_features': self._generate_item_features(n_items)
        }

    def _generate_user_features(self, n_users: int) -> Dict[str, Dict[str, Any]]:
        """Generate synthetic user features"""        features = {}
        for user_id in range(n_users):
            features[f'user_{user_id}'] = {
                'age': np.random.randint(18, 65),
                'gender': np.random.choice(['M', 'F']),
                'location': np.random.choice(['US', 'DE', 'FR', 'UK']),
                'activity_level': np.random.uniform(0.1, 1.0)
            }
        return features

    def _generate_item_features(self, n_items: int) -> Dict[str, Dict[str, Any]]:
        """Generate synthetic item features"""        features = {}
        genres = ['pop', 'rock', 'electronic', 'jazz', 'classical']
        for item_id in range(n_items):
            features[f'item_{item_id}'] = {
                'genre': np.random.choice(genres),
                'duration': np.random.randint(120, 400),
                'energy': np.random.uniform(0.0, 1.0),
                'valence': np.random.uniform(0.0, 1.0),
                'popularity': np.random.uniform(0.0, 1.0)
            }
        return features


class TestCollaborativeFilteringModel(IsolatedAsyncioTestCase):
    """Comprehensive tests for CollaborativeFilteringModel"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.model = CollaborativeFilteringModel(
            n_factors=50,
            learning_rate=0.005,
            regularization=0.01,
            epochs=10
        )
        self.training_data = self._generate_collaborative_data()

    def _generate_collaborative_data(self) -> Dict[str, Any]:
        """Generate collaborative filtering training data"""        n_users, n_items = 200, 100
        interactions = []
        
        # Create realistic interaction patterns
        for user_id in range(n_users):
            n_interactions = np.random.poisson(10)  # Average 10 interactions per user
            item_ids = np.random.choice(n_items, min(n_interactions, n_items), replace=False)
            
            for item_id in item_ids:
                # Simulate user preferences with some structure
                base_rating = 3.0 + np.random.normal(0, 0.5)
                if user_id % 3 == item_id % 3:  # Create some correlation
                    base_rating += 0.5
                
                rating = np.clip(base_rating, 1.0, 5.0)
                interactions.append({
                    'user_id': f'user_{user_id}',
                    'item_id': f'item_{item_id}',
                    'rating': rating,
                    'timestamp': datetime.utcnow() - timedelta(days=np.random.randint(0, 365))
                })
        
        return {'interactions': interactions}

    async def test_collaborative_training(self):
        """Test collaborative filtering model training"""        start_time = time.time()
        
        result = await self.model.train(self.training_data)
        
        training_time = time.time() - start_time
        
        self.assertTrue(result)
        self.assertTrue(self.model.is_trained)
        self.assertIsNotNone(self.model.training_history)
        self.assertLess(training_time, 30.0)  # Should train within 30 seconds

    async def test_collaborative_predictions(self):
        """Test collaborative filtering predictions"""        # Train the model first
        await self.model.train(self.training_data)
        
        # Test single prediction
        prediction = await self.model.predict(
            user_id='user_1',
            item_id='item_5'
        )
        
        self.assertIsInstance(prediction, (int, float))
        self.assertGreaterEqual(prediction, 0.0)
        self.assertLessEqual(prediction, 5.0)

    async def test_collaborative_batch_predictions(self):
        """Test batch predictions for collaborative filtering"""        await self.model.train(self.training_data)
        
        # Create batch prediction requests
        batch_requests = [
            {'user_id': f'user_{i}', 'item_id': f'item_{j}'}
            for i in range(5) for j in range(10)
        ]
        
        predictions = await self.model.predict_batch(batch_requests)
        
        self.assertIsInstance(predictions, list)
        self.assertEqual(len(predictions), len(batch_requests))
        
        for pred in predictions:
            self.assertIsInstance(pred, (int, float))
            self.assertGreaterEqual(pred, 0.0)
            self.assertLessEqual(pred, 5.0)

    async def test_collaborative_recommendations(self):
        """Test getting recommendations from collaborative model"""        await self.model.train(self.training_data)
        
        recommendations = await self.model.get_user_recommendations(
            user_id='user_1',
            top_k=10,
            exclude_seen=True
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)
        
        for rec in recommendations:
            self.assertIn('item_id', rec)
            self.assertIn('predicted_rating', rec)
            self.assertIn('confidence', rec)

    async def test_collaborative_user_similarity(self):
        """Test user similarity computation"""        await self.model.train(self.training_data)
        
        similar_users = await self.model.get_similar_users(
            user_id='user_1',
            top_k=5
        )
        
        self.assertIsInstance(similar_users, list)
        self.assertLessEqual(len(similar_users), 5)
        
        for user_sim in similar_users:
            self.assertIn('user_id', user_sim)
            self.assertIn('similarity', user_sim)
            self.assertGreaterEqual(user_sim['similarity'], -1.0)
            self.assertLessEqual(user_sim['similarity'], 1.0)

    async def test_collaborative_item_similarity(self):
        """Test item similarity computation"""        await self.model.train(self.training_data)
        
        similar_items = await self.model.get_similar_items(
            item_id='item_1',
            top_k=5
        )
        
        self.assertIsInstance(similar_items, list)
        self.assertLessEqual(len(similar_items), 5)
        
        for item_sim in similar_items:
            self.assertIn('item_id', item_sim)
            self.assertIn('similarity', item_sim)


class TestContentBasedModel(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentBasedModel"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.model = ContentBasedModel(
            feature_weights={'genre': 0.3, 'energy': 0.2, 'valence': 0.2, 'duration': 0.1},
            similarity_threshold=0.1
        )
        self.training_data = self._generate_content_based_data()

    def _generate_content_based_data(self) -> Dict[str, Any]:
        """Generate content-based training data"""        n_users, n_items = 100, 200
        
        # Generate item features
        genres = ['pop', 'rock', 'electronic', 'jazz', 'classical', 'hip-hop']
        item_features = {}
        for item_id in range(n_items):
            item_features[f'item_{item_id}'] = {
                'genre': np.random.choice(genres),
                'energy': np.random.uniform(0.0, 1.0),
                'valence': np.random.uniform(0.0, 1.0),
                'duration': np.random.randint(120, 400),
                'acousticness': np.random.uniform(0.0, 1.0),
                'danceability': np.random.uniform(0.0, 1.0)
            }
        
        # Generate user preferences based on content
        user_profiles = {}
        interactions = []
        
        for user_id in range(n_users):
            # Create user preference profile
            preferred_genre = np.random.choice(genres)
            preferred_energy = np.random.uniform(0.3, 0.8)
            
            user_profiles[f'user_{user_id}'] = {
                'preferred_genres': [preferred_genre],
                'energy_preference': preferred_energy,
                'valence_preference': np.random.uniform(0.2, 0.8)
            }
            
            # Generate interactions based on preferences
            for item_id in range(n_items):
                item_features_data = item_features[f'item_{item_id}']
                
                # Calculate rating based on content similarity
                rating = 3.0
                if item_features_data['genre'] == preferred_genre:
                    rating += 1.0
                
                energy_diff = abs(item_features_data['energy'] - preferred_energy)
                rating += (1.0 - energy_diff)
                
                rating = np.clip(rating + np.random.normal(0, 0.3), 1.0, 5.0)
                
                # Only include interactions with reasonable ratings
                if rating > 2.5 and np.random.random() < 0.1:
                    interactions.append({
                        'user_id': f'user_{user_id}',
                        'item_id': f'item_{item_id}',
                        'rating': rating,
                        'timestamp': datetime.utcnow()
                    })
        
        return {
            'interactions': interactions,
            'item_features': item_features,
            'user_profiles': user_profiles
        }

    async def test_content_based_training(self):
        """Test content-based model training"""        result = await self.model.train(self.training_data)
        
        self.assertTrue(result)
        self.assertTrue(self.model.is_trained)
        self.assertIsNotNone(self.model.item_profiles)

    async def test_content_based_similarity(self):
        """Test content-based similarity computation"""        await self.model.train(self.training_data)
        
        similarity = await self.model.compute_content_similarity(
            item_id1='item_1',
            item_id2='item_2'
        )
        
        self.assertIsInstance(similarity, (int, float))
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    async def test_content_based_recommendations(self):
        """Test content-based recommendations"""        await self.model.train(self.training_data)
        
        recommendations = await self.model.get_content_recommendations(
            user_id='user_1',
            top_k=15
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 15)
        
        for rec in recommendations:
            self.assertIn('item_id', rec)
            self.assertIn('content_similarity', rec)
            self.assertIn('feature_matches', rec)

    async def test_user_profile_building(self):
        """Test user profile building from interactions"""        await self.model.train(self.training_data)
        
        user_profile = await self.model.build_user_content_profile('user_1')
        
        self.assertIsInstance(user_profile, dict)
        self.assertIn('content_preferences', user_profile)
        self.assertIn('feature_weights', user_profile)

    async def test_feature_importance(self):
        """Test feature importance analysis"""        await self.model.train(self.training_data)
        
        feature_importance = await self.model.analyze_feature_importance()
        
        self.assertIsInstance(feature_importance, dict)
        for feature, importance in feature_importance.items():
            self.assertIsInstance(importance, (int, float))
            self.assertGreaterEqual(importance, 0.0)


class TestHybridRecommenderModel(IsolatedAsyncioTestCase):
    """Comprehensive tests for HybridRecommenderModel"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.model = HybridRecommenderModel(
            collaborative_weight=0.6,
            content_weight=0.4,
            cf_config={'n_factors': 30},
            cb_config={'similarity_threshold': 0.2}
        )
        self.training_data = self._generate_hybrid_data()

    def _generate_hybrid_data(self) -> Dict[str, Any]:
        """Generate comprehensive data for hybrid model"""        n_users, n_items = 150, 120
        
        # Generate interactions
        interactions = []
        for user_id in range(n_users):
            for item_id in range(n_items):
                if np.random.random() < 0.05:  # 5% interaction probability
                    rating = np.random.uniform(1.0, 5.0)
                    interactions.append({
                        'user_id': f'user_{user_id}',
                        'item_id': f'item_{item_id}',
                        'rating': rating,
                        'timestamp': datetime.utcnow()
                    })
        
        # Generate item features
        genres = ['pop', 'rock', 'electronic', 'classical']
        item_features = {}
        for item_id in range(n_items):
            item_features[f'item_{item_id}'] = {
                'genre': np.random.choice(genres),
                'energy': np.random.uniform(0.0, 1.0),
                'valence': np.random.uniform(0.0, 1.0),
                'duration': np.random.randint(120, 400)
            }
        
        return {
            'interactions': interactions,
            'item_features': item_features
        }

    async def test_hybrid_training(self):
        """Test hybrid model training"""        result = await self.model.train(self.training_data)
        
        self.assertTrue(result)
        self.assertTrue(self.model.is_trained)
        self.assertTrue(self.model.collaborative_model.is_trained)
        self.assertTrue(self.model.content_model.is_trained)

    async def test_hybrid_predictions(self):
        """Test hybrid model predictions"""        await self.model.train(self.training_data)
        
        prediction = await self.model.predict(
            user_id='user_1',
            item_id='item_5'
        )
        
        self.assertIsInstance(prediction, (int, float))
        self.assertGreaterEqual(prediction, 0.0)
        self.assertLessEqual(prediction, 5.0)

    async def test_hybrid_recommendations(self):
        """Test hybrid recommendations"""        await self.model.train(self.training_data)
        
        recommendations = await self.model.get_hybrid_recommendations(
            user_id='user_1',
            top_k=10
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)
        
        for rec in recommendations:
            self.assertIn('item_id', rec)
            self.assertIn('hybrid_score', rec)
            self.assertIn('collaborative_score', rec)
            self.assertIn('content_score', rec)

    async def test_weight_optimization(self):
        """Test hybrid weight optimization"""        await self.model.train(self.training_data)
        
        # Test different weight combinations
        original_weights = (self.model.collaborative_weight, self.model.content_weight)
        
        optimized_weights = await self.model.optimize_weights(
            validation_data=self.training_data['interactions'][:50]
        )
        
        self.assertIsInstance(optimized_weights, tuple)
        self.assertEqual(len(optimized_weights), 2)
        self.assertAlmostEqual(sum(optimized_weights), 1.0, places=2)

    async def test_component_analysis(self):
        """Test analysis of hybrid components"""        await self.model.train(self.training_data)
        
        analysis = await self.model.analyze_component_performance()
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('collaborative_performance', analysis)
        self.assertIn('content_performance', analysis)
        self.assertIn('hybrid_performance', analysis)


class TestDeepPersonalizationModel(IsolatedAsyncioTestCase):
    """Comprehensive tests for DeepPersonalizationModel"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.model = DeepPersonalizationModel(
            embedding_dim=64,
            hidden_layers=[128, 64, 32],
            dropout_rate=0.2,
            learning_rate=0.001
        )
        self.training_data = self._generate_deep_learning_data()

    def _generate_deep_learning_data(self) -> Dict[str, Any]:
        """Generate data suitable for deep learning model"""        n_users, n_items = 300, 200
        
        # Generate rich feature vectors
        user_features = {}
        for user_id in range(n_users):
            user_features[f'user_{user_id}'] = {
                'demographic_vector': np.random.randn(10),
                'behavior_vector': np.random.randn(15),
                'preference_vector': np.random.randn(20)
            }
        
        item_features = {}
        for item_id in range(n_items):
            item_features[f'item_{item_id}'] = {
                'content_vector': np.random.randn(25),
                'metadata_vector': np.random.randn(10),
                'acoustic_vector': np.random.randn(20)
            }
        
        # Generate interactions with context
        interactions = []
        for user_id in range(n_users):
            for item_id in range(n_items):
                if np.random.random() < 0.03:  # 3% interaction probability
                    context_features = np.random.randn(8)  # Time, device, etc.
                    rating = np.random.uniform(1.0, 5.0)
                    
                    interactions.append({
                        'user_id': f'user_{user_id}',
                        'item_id': f'item_{item_id}',
                        'rating': rating,
                        'context_features': context_features.tolist(),
                        'timestamp': datetime.utcnow()
                    })
        
        return {
            'interactions': interactions,
            'user_features': user_features,
            'item_features': item_features
        }

    async def test_deep_model_architecture(self):
        """Test deep model architecture setup"""        # Check if PyTorch is available
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available for deep learning tests")
        
        await self.model.build_model()
        
        self.assertIsNotNone(self.model.neural_network)
        self.assertIsNotNone(self.model.optimizer)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    async def test_deep_training(self):
        """Test deep learning model training"""        result = await self.model.train(
            self.training_data,
            epochs=5,
            batch_size=64
        )
        
        self.assertTrue(result)
        self.assertTrue(self.model.is_trained)
        self.assertIsNotNone(self.model.training_history)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    async def test_deep_predictions(self):
        """Test deep learning predictions"""        await self.model.train(self.training_data, epochs=2)
        
        prediction = await self.model.predict(
            user_id='user_1',
            item_id='item_5',
            context_features=np.random.randn(8).tolist()
        )
        
        self.assertIsInstance(prediction, (int, float))
        self.assertGreaterEqual(prediction, 0.0)
        self.assertLessEqual(prediction, 5.0)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    async def test_embedding_quality(self):
        """Test quality of learned embeddings"""        await self.model.train(self.training_data, epochs=3)
        
        user_embedding = await self.model.get_user_embedding('user_1')
        item_embedding = await self.model.get_item_embedding('item_1')
        
        self.assertIsInstance(user_embedding, np.ndarray)
        self.assertIsInstance(item_embedding, np.ndarray)
        self.assertEqual(len(user_embedding), 64)  # embedding_dim
        self.assertEqual(len(item_embedding), 64)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    async def test_attention_mechanism(self):
        """Test attention mechanism in deep model"""        await self.model.train(self.training_data, epochs=2)
        
        attention_weights = await self.model.get_attention_weights(
            user_id='user_1',
            item_candidates=[f'item_{i}' for i in range(10)]
        )
        
        self.assertIsInstance(attention_weights, dict)
        self.assertEqual(len(attention_weights), 10)
        
        # Attention weights should sum to approximately 1
        total_weight = sum(attention_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=1)


class TestUserEmbeddingModel(IsolatedAsyncioTestCase):
    """Comprehensive tests for UserEmbeddingModel"""
    async def asyncSetUp(self):
        """Set up test environment"""        self.model = UserEmbeddingModel(
            embedding_dim=100,
            context_dim=20,
            learning_rate=0.01
        )
        self.training_data = self._generate_embedding_data()

    def _generate_embedding_data(self) -> Dict[str, Any]:
        """Generate data for embedding model training"""        n_users = 500
        
        # Generate user sequences (interaction history)
        user_sequences = {}
        for user_id in range(n_users):
            sequence_length = np.random.randint(10, 100)
            sequence = []
            
            for _ in range(sequence_length):
                sequence.append({
                    'item_id': f'item_{np.random.randint(0, 1000)}',
                    'rating': np.random.uniform(1.0, 5.0),
                    'context': np.random.randn(20).tolist(),
                    'timestamp': datetime.utcnow() - timedelta(days=np.random.randint(0, 365))
                })
            
            user_sequences[f'user_{user_id}'] = sorted(sequence, key=lambda x: x['timestamp'])
        
        return {'user_sequences': user_sequences}

    async def test_embedding_training(self):
        """Test user embedding model training"""        result = await self.model.train(
            self.training_data,
            epochs=10,
            batch_size=32
        )
        
        self.assertTrue(result)
        self.assertTrue(self.model.is_trained)

    async def test_user_embedding_quality(self):
        """Test quality of user embeddings"""        await self.model.train(self.training_data, epochs=5)
        
        embedding = await self.model.get_user_embedding('user_1')
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(len(embedding), 100)  # embedding_dim
        
        # Embedding should be normalized
        norm = np.linalg.norm(embedding)
        self.assertAlmostEqual(norm, 1.0, places=1)

    async def test_embedding_similarity(self):
        """Test embedding-based similarity computation"""        await self.model.train(self.training_data, epochs=5)
        
        similarity = await self.model.compute_user_similarity(
            user_id1='user_1',
            user_id2='user_2'
        )
        
        self.assertIsInstance(similarity, (int, float))
        self.assertGreaterEqual(similarity, -1.0)
        self.assertLessEqual(similarity, 1.0)

    async def test_embedding_clustering(self):
        """Test user clustering based on embeddings"""        await self.model.train(self.training_data, epochs=5)
        
        clusters = await self.model.cluster_users(n_clusters=10)
        
        self.assertIsInstance(clusters, dict)
        self.assertEqual(len(clusters), 10)
        
        # Check that all users are assigned to clusters
        all_users = set()
        for cluster_users in clusters.values():
            all_users.update(cluster_users)
        
        self.assertGreater(len(all_users), 0)


class TestModelPerformanceAndScalability(IsolatedAsyncioTestCase):
    """Performance and scalability tests for all models"""
    async def test_training_performance(self):
        """Test training performance across different model types"""        models_to_test = [
            CollaborativeFilteringModel(n_factors=20),
            ContentBasedModel(),
            HybridRecommenderModel(
                cf_config={'n_factors': 20},
                cb_config={'similarity_threshold': 0.1}
            )
        ]
        
        # Generate moderate-sized dataset
        training_data = self._generate_performance_test_data(200, 150)
        
        for model in models_to_test:
            start_time = time.time()
            
            await model.train(training_data)
            
            training_time = time.time() - start_time
            
            # Each model should train within reasonable time
            self.assertLess(training_time, 60.0)  # 1 minute max
            self.assertTrue(model.is_trained)

    async def test_prediction_performance(self):
        """Test prediction performance"""        model = CollaborativeFilteringModel(n_factors=30)
        training_data = self._generate_performance_test_data(100, 80)
        
        await model.train(training_data)
        
        # Test batch prediction performance
        batch_requests = [
            {'user_id': f'user_{i}', 'item_id': f'item_{j}'}
            for i in range(10) for j in range(20)
        ]
        
        start_time = time.time()
        predictions = await model.predict_batch(batch_requests)
        prediction_time = time.time() - start_time
        
        # Should predict 200 items within 5 seconds
        self.assertLess(prediction_time, 5.0)
        self.assertEqual(len(predictions), len(batch_requests))

    async def test_memory_usage(self):
        """Test memory usage during model operations"""        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and train large model
        model = CollaborativeFilteringModel(n_factors=100)
        large_data = self._generate_performance_test_data(1000, 500)
        
        await model.train(large_data)
        
        # Generate many predictions
        for i in range(100):
            await model.predict(f'user_{i}', f'item_{i}')
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 500MB)
        self.assertLess(memory_increase, 500)

    def _generate_performance_test_data(self, n_users: int, n_items: int) -> Dict[str, Any]:
        """Generate data for performance testing"""        interactions = []
        
        for user_id in range(n_users):
            n_interactions = np.random.poisson(15)
            item_ids = np.random.choice(n_items, min(n_interactions, n_items), replace=False)
            
            for item_id in item_ids:
                interactions.append({
                    'user_id': f'user_{user_id}',
                    'item_id': f'item_{item_id}',
                    'rating': np.random.uniform(1.0, 5.0),
                    'timestamp': datetime.utcnow()
                })
        
        # Generate item features
        item_features = {}
        genres = ['pop', 'rock', 'electronic', 'jazz']
        for item_id in range(n_items):
            item_features[f'item_{item_id}'] = {
                'genre': np.random.choice(genres),
                'energy': np.random.uniform(0.0, 1.0),
                'valence': np.random.uniform(0.0, 1.0)
            }
        
        return {
            'interactions': interactions,
            'item_features': item_features
        }


class TestModelRobustness(IsolatedAsyncioTestCase):
    """Robustness and edge case tests"""
    async def test_empty_data_handling(self):
        """Test handling of empty training data"""        model = CollaborativeFilteringModel()
        
        empty_data = {'interactions': []}
        
        with self.assertRaises(InsufficientDataError):
            await model.train(empty_data)

    async def test_single_user_data(self):
        """Test handling of single user data"""        model = CollaborativeFilteringModel()
        
        single_user_data = {
            'interactions': [
                {
                    'user_id': 'single_user',
                    'item_id': 'item_1',
                    'rating': 4.0,
                    'timestamp': datetime.utcnow()
                }
            ]
        }
        
        with self.assertRaises(InsufficientDataError):
            await model.train(single_user_data)

    async def test_missing_features_handling(self):
        """Test handling of missing features"""        model = ContentBasedModel()
        
        # Data with missing item features
        incomplete_data = {
            'interactions': [
                {'user_id': 'user_1', 'item_id': 'item_1', 'rating': 4.0}
            ],
            'item_features': {}  # Missing features
        }
        
        with self.assertRaises(InsufficientDataError):
            await model.train(incomplete_data)

    async def test_invalid_rating_values(self):
        """Test handling of invalid rating values"""        model = CollaborativeFilteringModel()
        
        # Create data with invalid ratings
        invalid_data = {
            'interactions': [
                {'user_id': 'user_1', 'item_id': 'item_1', 'rating': -1.0},  # Invalid
                {'user_id': 'user_1', 'item_id': 'item_2', 'rating': 10.0},  # Invalid
                {'user_id': 'user_2', 'item_id': 'item_1', 'rating': 3.0}   # Valid
            ]
        }
        
        # Model should handle or filter invalid ratings
        result = await model.train(invalid_data)
        self.assertTrue(result)

    async def test_duplicate_interactions(self):
        """Test handling of duplicate interactions"""        model = CollaborativeFilteringModel()
        
        # Data with duplicate interactions
        duplicate_data = {
            'interactions': [
                {'user_id': 'user_1', 'item_id': 'item_1', 'rating': 4.0, 'timestamp': datetime.utcnow()},
                {'user_id': 'user_1', 'item_id': 'item_1', 'rating': 5.0, 'timestamp': datetime.utcnow()},  # Duplicate
                {'user_id': 'user_2', 'item_id': 'item_1', 'rating': 3.0, 'timestamp': datetime.utcnow()}
            ]
        }
        
        result = await model.train(duplicate_data)
        self.assertTrue(result)

    async def test_model_state_corruption(self):
        """Test handling of corrupted model state"""        model = CollaborativeFilteringModel()
        
        # Create corrupted state dict
        corrupted_state = {
            'model_weights': 'invalid_data',
            'training_config': {},
            'metadata': {}
        }
        
        with self.assertRaises(ModelTrainingError):
            await model.load_state(corrupted_state)


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=5'
    ])
