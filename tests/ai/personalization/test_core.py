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

"""
Core Personalization Engine Tests

Comprehensive tests for the core personalization functionality.
Tests all core engines, managers, and configuration systems.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from unittest import IsolatedAsyncioTestCase
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
import time
import json
import os
import sys

# Import the core personalization modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.core import (
    PersonalizationEngine,
    UserProfileManager,
    ContentPersonalizer,
    RecommendationEngine,
    AdaptiveLearning,
    PersonalizationConfig,
    UserProfile,
    ContentType,
    PersonalizationType
)
from ai.personalization.exceptions import (
    PersonalizationError,
    ProfileNotFoundError,
    RecommendationError,
    ModelTrainingError
)


class TestPersonalizationEngine(IsolatedAsyncioTestCase):
    """
Comprehensive tests for PersonalizationEngine"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        # Create test configuration
        self.config = PersonalizationConfig()
        self.engine = PersonalizationEngine(self.config)
        self.test_user_id = "test_user_12345"
        self.test_content_ids = [f"content_{i}" for i in range(1, 21)]
        
        # Create test user profile with correct structure
        self.test_profile = UserProfile(
            user_id=self.test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        # Set optional fields
        self.test_profile.age_group = '25-35'
        self.test_profile.gender = 'M'
        self.test_profile.location = 'DE'
        self.test_profile.preferred_genres = {'pop': 0.8, 'rock': 0.6, 'electronic': 0.9}
        self.test_profile.engagement_metrics = {'listening_time': 120, 'session_frequency': 0.8}
        self.test_profile.personality_traits = {'openness': 0.7, 'creativity': 0.8}

    async def test_engine_initialization(self):
        """Test engine proper initialization"""
        self.assertIsNotNone(self.engine)
        self.assertIsInstance(self.engine.config, PersonalizationConfig)
        self.assertIsNotNone(self.engine.models)
        self.assertIsNotNone(self.engine.analytics)
        self.assertIsNotNone(self.engine.metrics)
        self.assertEqual(self.engine.metrics["total_recommendations"], 0)

    async def test_get_recommendations_basic(self):
        """Test basic recommendation functionality"""
        # Test with minimal parameters
        recommendations = await self.engine.get_personalized_recommendations(
            user_id=self.test_user_id,
            num_recommendations=10
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)
        
        # Verify recommendation structure
        if recommendations:
            rec = recommendations[0]
            self.assertIn('content_id', rec)
            self.assertIn('score', rec)
            self.assertIsInstance(rec['score'], (int, float))
            self.assertGreaterEqual(rec['relevance_score'], 0.0)
            self.assertLessEqual(rec['relevance_score'], 1.0)

    async def test_get_recommendations_with_content_type(self):
        """
Test recommendations with specific content type"""
        from ai.personalization.core import ContentType
        
        for content_type in [ContentType.MUSIC, ContentType.VIDEO, ContentType.AUDIO, ContentType.TEXT]:
            recommendations = await self.engine.get_personalized_recommendations(
                user_id=self.test_user_id,
                content_type=content_type,
                num_recommendations=5
            )
            
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), 5)

    async def test_get_recommendations_with_strategy(self):
        """
Test recommendations with different strategies"""
        from ai.personalization.core import PersonalizationType
        
        strategies = [
            PersonalizationType.COLLABORATIVE_FILTERING, 
            PersonalizationType.CONTENT_BASED, 
            PersonalizationType.HYBRID, 
            PersonalizationType.DEEP_LEARNING
        ]
        
        for strategy in strategies:
            # Create a new config with the strategy
            config = PersonalizationConfig(model_type=strategy)
            engine = PersonalizationEngine(config)
            
            recommendations = await engine.get_personalized_recommendations(
                user_id=self.test_user_id,
                num_recommendations=5
            )
            
            self.assertIsInstance(recommendations, list)
            # Verify strategy was applied (check if recommendations contain strategy info)
            if recommendations:
                self.assertIn('strategy', recommendations[0])

    async def test_get_recommendations_performance(self):
        """
Test recommendation generation performance"""
        start_time = time.time()
        
        recommendations = await self.engine.get_personalized_recommendations(
            user_id=self.test_user_id,
            num_recommendations=50
        )
        
        execution_time = time.time() - start_time
        
        # Should complete within 500ms for 50 recommendations
        self.assertLess(execution_time, 0.5)
        self.assertIsInstance(recommendations, list)

    async def test_process_feedback_explicit(self):
        """
Test processing explicit user feedback"""
        # Test positive feedback
        result = await self.engine.process_feedback(
            user_id=self.test_user_id,
            content_id="content_1",
            feedback_type="rating",
            feedback_value=4.5
        )
        
        # Since process_feedback returns None, we check it doesn't raise exception
        self.assertIsNone(result)
        
        # Test negative feedback
        result = await self.engine.process_feedback(
            user_id=self.test_user_id,
            content_id="content_2",
            feedback_type="rating",
            feedback_value=1.5
        )
        
        self.assertIsNone(result)

    async def test_process_feedback_implicit(self):
        """Test processing implicit user feedback"""
        # Test engagement time feedback
        result = await self.engine.process_feedback(
            user_id=self.test_user_id,
            content_id="content_3",
            feedback_type="engagement_time",
            feedback_value=240.0  # 4 minutes
        )
        
        self.assertIsNone(result)
        
        # Test skip feedback
        result = await self.engine.process_feedback(
            user_id=self.test_user_id,
            content_id="content_4",
            feedback_type="skip",
            feedback_value=1.0
        )
        
        self.assertIsNone(result)

    async def test_process_feedback_multiple(self):
        """Test multiple feedback processing"""
        # Process multiple feedback items individually
        for i in range(5):
            result = await self.engine.process_feedback(
                user_id=self.test_user_id,
                content_id=f'content_{i}',
                feedback_type='rating',
                feedback_value=float(np.random.uniform(1, 5))
            )
            self.assertIsNone(result)

    async def test_update_user_profile(self):
        """
Test user profile updates"""
        # Test with interaction data
        interaction_data = {
            'content_id': 'test_content_123',
            'action': 'play',
            'value': 1.0,
            'genre': 'jazz',
            'duration': 180
        }
        
        result = await self.engine.update_user_profile(
            user_id=self.test_user_id,
            interaction_data=interaction_data
        )
        
        self.assertIsInstance(result, UserProfile)

    async def test_get_user_profile(self):
        """
Test user profile retrieval"""
        profile = await self.engine.get_user_profile(
            user_id=self.test_user_id
        )
        
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user_id, self.test_user_id)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    async def test_concurrent_recommendations(self):
        """
Test concurrent recommendation requests"""
        tasks = []
        for i in range(10):
            task = self.engine.get_personalized_recommendations(
                user_id=f"concurrent_user_{i}",
                num_recommendations=5
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        self.assertEqual(len(results), 10)
        for recommendations in results:
            self.assertIsInstance(recommendations, list)

    async def test_error_handling_invalid_user(self):
        """Test error handling for invalid user ID"""
        with self.assertRaises(PersonalizationError):
            await self.engine.get_recommendations(
                user_id="",  # Empty user ID
                max_recommendations=10
            )

    async def test_error_handling_invalid_feedback(self):
        """Test error handling for invalid feedback"""
        with self.assertRaises(PersonalizationError):
            await self.engine.process_feedback(
                user_id=self.test_user_id,
                content_id="content_1",
                feedback_type="invalid_type",
                value="invalid_value"
            )


class TestUserProfileManager(IsolatedAsyncioTestCase):
    """Comprehensive tests for UserProfileManager"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        self.config = PersonalizationConfig()
        self.manager = UserProfileManager(self.config)
        self.test_user_id = "profile_test_user"

    async def test_create_user_profile(self):
        """Test user profile creation"""
        initial_data = {
            'demographics': {'age_group': '25-35', 'location': 'FR'},
            'preferences': {'music': {'pop': 0.8}},
            'behavior_patterns': {'activity_level': 0.6}
        }
        
        profile = await self.manager.create_profile(self.test_user_id, initial_data)
        
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user_id, self.test_user_id)
        self.assertIsNotNone(profile.created_at)

    async def test_validate_profile(self):
        """
Test profile validation"""
        # Create a valid profile
        initial_data = {
            'demographics': {'age_group': '25-35'},
            'preferences': {'music': {'rock': 0.7}}
        }
        
        profile = await self.manager.create_profile(self.test_user_id, initial_data)
        
        # Test validation
        is_valid = await self.manager.validate_profile(profile)
        
        self.assertTrue(is_valid)

    async def test_optimize_profile(self):
        """
Test profile optimization"""
        # Create initial profile with many interactions
        initial_data = {
            'preferences': {'music': {'pop': 0.5}}
        }
        
        profile = await self.manager.create_profile(self.test_user_id, initial_data)
        
        # Add many interactions
        profile.interaction_history = [
            {'content_id': f'content_{i}', 'timestamp': datetime.utcnow().isoformat()}
            for i in range(100)
        ]
        
        # Optimize profile
        optimized_profile = await self.manager.optimize_profile(profile)
        
        self.assertIsInstance(optimized_profile, UserProfile)
        self.assertLessEqual(len(optimized_profile.interaction_history), self.config.max_profile_size)
        self.assertEqual(updated_profile.preferences['music']['rock'], 0.6)

    async def test_analyze_user_behavior(self):
        """
Test user behavior analysis"""
        analysis = await self.manager.analyze_user_behavior(
            user_id=self.test_user_id,
            time_window=timedelta(days=30)
        )
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('activity_patterns', analysis)
        self.assertIn('engagement_metrics', analysis)
        self.assertIn('preference_evolution', analysis)

    async def test_get_similar_users(self):
        """
Test finding similar users"""
        # Create multiple test profiles
        for i in range(5):
            profile_data = {
                'user_id': f'similar_user_{i}',
                'preferences': {
                    'music': {
                        'pop': np.random.uniform(0.5, 0.9),
                        'rock': np.random.uniform(0.3, 0.7)
                    }
                }
            }
            await self.manager.create_user_profile(profile_data)
        
        similar_users = await self.manager.get_similar_users(
            user_id='similar_user_0',
            max_users=3
        )
        
        self.assertIsInstance(similar_users, list)
        self.assertLessEqual(len(similar_users), 3)
        
        for user_data in similar_users:
            self.assertIn('user_id', user_data)
            self.assertIn('similarity_score', user_data)
            self.assertIsInstance(user_data['similarity_score'], (int, float))

    async def test_profile_not_found_error(self):
        """
Test ProfileNotFoundError handling"""
        with self.assertRaises(ProfileNotFoundError):
            await self.manager.get_user_profile("nonexistent_user")


class TestContentPersonalizer(IsolatedAsyncioTestCase):
    """Comprehensive tests for ContentPersonalizer"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        self.personalizer = ContentPersonalizer()
        self.test_user_profile = UserProfile(
            user_id="content_test_user",
            preferences={
                'music': {'electronic': 0.9, 'ambient': 0.7},
                'energy_level': 0.6
            }
        )

    async def test_personalize_content(self):
        """Test content personalization"""
        content_items = [
            {
                'content_id': f'item_{i}',
                'content_type': 'music',
                'metadata': {
                    'genre': np.random.choice(['electronic', 'pop', 'rock']),
                    'energy': np.random.uniform(0.1, 1.0),
                    'duration': np.random.randint(120, 300)
                }
            }
            for i in range(20)
        ]
        
        personalized_content = await self.personalizer.personalize_content(
            user_profile=self.test_user_profile,
            content_items=content_items,
            personalization_strength=0.8
        )
        
        self.assertIsInstance(personalized_content, list)
        self.assertLessEqual(len(personalized_content), len(content_items))
        
        # Verify personalization scores
        for item in personalized_content:
            self.assertIn('personalization_score', item)
            self.assertIsInstance(item['personalization_score'], (int, float))
            self.assertGreaterEqual(item['personalization_score'], 0.0)
            self.assertLessEqual(item['personalization_score'], 1.0)

    async def test_adapt_content_features(self):
        """
Test content feature adaptation"""
        content_features = {
            'tempo': 120,
            'key': 'C_major',
            'energy': 0.7,
            'valence': 0.6
        }
        
        adapted_features = await self.personalizer.adapt_content_features(
            user_profile=self.test_user_profile,
            content_features=content_features
        )
        
        self.assertIsInstance(adapted_features, dict)
        self.assertIn('adapted_tempo', adapted_features)
        self.assertIn('adaptation_factors', adapted_features)

    async def test_generate_content_variants(self):
        """
Test content variant generation"""
        base_content = {
            'content_id': 'base_content',
            'content_type': 'music',
            'features': {'tempo': 130, 'energy': 0.8}
        }
        
        variants = await self.personalizer.generate_content_variants(
            base_content=base_content,
            user_profile=self.test_user_profile,
            num_variants=3
        )
        
        self.assertIsInstance(variants, list)
        self.assertEqual(len(variants), 3)
        
        for variant in variants:
            self.assertIn('variant_id', variant)
            self.assertIn('adaptation_type', variant)
            self.assertIn('features', variant)


class TestRecommendationEngine(IsolatedAsyncioTestCase):
    """
Comprehensive tests for RecommendationEngine"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        self.engine = RecommendationEngine()
        self.test_user_profile = UserProfile(
            user_id="recommendation_test_user",
            preferences={'music': {'jazz': 0.8, 'blues': 0.6}}
        )

    async def test_collaborative_filtering(self):
        """Test collaborative filtering recommendations"""
        recommendations = await self.engine.get_collaborative_recommendations(
            user_profile=self.test_user_profile,
            max_recommendations=10
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)
        
        for rec in recommendations:
            self.assertIn('content_id', rec)
            self.assertIn('score', rec)
            self.assertIn('method', rec)
            self.assertEqual(rec['method'], 'collaborative_filtering')

    async def test_content_based_filtering(self):
        """
Test content-based filtering recommendations"""
        recommendations = await self.engine.get_content_based_recommendations(
            user_profile=self.test_user_profile,
            max_recommendations=10
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)
        
        for rec in recommendations:
            self.assertIn('content_id', rec)
            self.assertIn('score', rec)
            self.assertIn('method', rec)
            self.assertEqual(rec['method'], 'content_based')

    async def test_hybrid_recommendations(self):
        """
Test hybrid recommendation approach"""
        recommendations = await self.engine.get_hybrid_recommendations(
            user_profile=self.test_user_profile,
            collaborative_weight=0.6,
            content_weight=0.4,
            max_recommendations=15
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 15)
        
        for rec in recommendations:
            self.assertIn('content_id', rec)
            self.assertIn('hybrid_score', rec)
            self.assertIn('component_scores', rec)

    async def test_deep_learning_recommendations(self):
        """
Test deep learning recommendations"""
        recommendations = await self.engine.get_deep_learning_recommendations(
            user_profile=self.test_user_profile,
            max_recommendations=10
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)

    async def test_recommendation_diversity(self):
        """
Test recommendation diversity optimization"""
        recommendations = await self.engine.get_diverse_recommendations(
            user_profile=self.test_user_profile,
            diversity_factor=0.3,
            max_recommendations=20
        )
        
        self.assertIsInstance(recommendations, list)
        
        # Check diversity metrics
        if len(recommendations) > 1:
            content_types = [rec.get('content_type') for rec in recommendations]
            unique_types = set(content_types)
            diversity_ratio = len(unique_types) / len(recommendations)
            self.assertGreater(diversity_ratio, 0.0)

    async def test_recommendation_ranking(self):
        """
Test recommendation ranking and scoring"""
        candidate_items = [
            {'content_id': f'candidate_{i}', 'features': {'score': np.random.random()}}
            for i in range(50)
        ]
        
        ranked_items = await self.engine.rank_recommendations(
            user_profile=self.test_user_profile,
            candidate_items=candidate_items
        )
        
        self.assertIsInstance(ranked_items, list)
        self.assertLessEqual(len(ranked_items), len(candidate_items))
        
        # Verify ranking order (scores should be descending)
        scores = [item['final_score'] for item in ranked_items]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestAdaptiveLearning(IsolatedAsyncioTestCase):
    """
Comprehensive tests for AdaptiveLearning"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        self.adaptive_learning = AdaptiveLearning()
        self.test_user_id = "adaptive_test_user"

    async def test_online_learning_update(self):
        """Test online learning model updates"""
        feedback_data = {
            'user_id': self.test_user_id,
            'content_id': 'content_123',
            'feedback_type': 'rating',
            'value': 4.5,
            'context': {'session_length': 180}
        }
        
        result = await self.adaptive_learning.update_from_feedback(feedback_data)
        self.assertTrue(result)

    async def test_model_performance_tracking(self):
        """
Test model performance tracking"""
        performance_metrics = await self.adaptive_learning.get_performance_metrics(
            time_window=timedelta(days=7)
        )
        
        self.assertIsInstance(performance_metrics, dict)
        self.assertIn('accuracy', performance_metrics)
        self.assertIn('precision', performance_metrics)
        self.assertIn('recall', performance_metrics)
        self.assertIn('f1_score', performance_metrics)

    async def test_adaptive_parameter_tuning(self):
        """
Test adaptive parameter tuning"""
        current_params = {
            'learning_rate': 0.01,
            'regularization': 0.001,
            'batch_size': 32
        }
        
        optimized_params = await self.adaptive_learning.optimize_parameters(
            current_params=current_params,
            performance_target=0.85
        )
        
        self.assertIsInstance(optimized_params, dict)
        self.assertIn('learning_rate', optimized_params)
        self.assertIn('optimization_history', optimized_params)

    async def test_user_behavior_adaptation(self):
        """
Test adaptation to user behavior changes"""
        behavior_history = [
            {
                'timestamp': datetime.utcnow() - timedelta(days=i),
                'engagement_time': np.random.uniform(60, 300),
                'satisfaction': np.random.uniform(0.3, 1.0)
            }
            for i in range(30)
        ]
        
        adaptation_strategy = await self.adaptive_learning.adapt_to_behavior_changes(
            user_id=self.test_user_id,
            behavior_history=behavior_history
        )
        
        self.assertIsInstance(adaptation_strategy, dict)
        self.assertIn('adaptation_type', adaptation_strategy)
        self.assertIn('recommended_changes', adaptation_strategy)


class TestPersonalizationConfig(IsolatedAsyncioTestCase):
    """
Comprehensive tests for PersonalizationConfig"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        self.config = PersonalizationConfig()

    async def test_default_configuration(self):
        """
Test default configuration values"""
        self.assertIsInstance(self.config.model_configs, dict)
        self.assertIn('collaborative_filtering', self.config.model_configs)
        self.assertIn('content_based', self.config.model_configs)
        self.assertIn('hybrid', self.config.model_configs)

    async def test_config_validation(self):
        """
Test configuration validation"""
        # Test valid config
        valid_config = {
            'collaborative_filtering': {
                'n_factors': 50,
                'learning_rate': 0.01
            }
        }
        
        is_valid = await self.config.validate_config(valid_config)
        self.assertTrue(is_valid)
        
        # Test invalid config
        invalid_config = {
            'collaborative_filtering': {
                'n_factors': -10,  # Invalid negative value
                'learning_rate': 2.0  # Invalid high value
            }
        }
        
        is_valid = await self.config.validate_config(invalid_config)
        self.assertFalse(is_valid)

    async def test_config_update(self):
        """
Test configuration updates"""
        new_config = {
            'collaborative_filtering': {
                'n_factors': 100,
                'regularization': 0.05
            }
        }
        
        result = await self.config.update_config(new_config)
        self.assertTrue(result)
        
        # Verify update
        updated_value = self.config.get_config('collaborative_filtering.n_factors')
        self.assertEqual(updated_value, 100)

    async def test_environment_config_loading(self):
        """
Test loading configuration from environment"""
        # Set test environment variable
        os.environ['PERSONALIZATION_TEST_PARAM'] = '42'
        
        env_config = await self.config.load_from_environment()
        self.assertIsInstance(env_config, dict)
        
        # Clean up
        if 'PERSONALIZATION_TEST_PARAM' in os.environ:
            del os.environ['PERSONALIZATION_TEST_PARAM']


class TestPerformanceAndStress(IsolatedAsyncioTestCase):
    """
Performance and stress tests for personalization components"""
    async def asyncSetUp(self):
        """
Set up test environment"""
        self.engine = PersonalizationEngine()

    async def test_high_volume_recommendations(self):
        """
Test recommendation generation under high volume"""
        start_time = time.time()
        
        # Generate recommendations for 100 users
        tasks = []
        for i in range(100):
            task = self.engine.get_recommendations(
                user_id=f"stress_user_{i}",
                max_recommendations=10
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        execution_time = time.time() - start_time
        
        # Should complete within 5 seconds for 100 users
        self.assertLess(execution_time, 5.0)
        self.assertEqual(len(results), 100)

    async def test_memory_usage_recommendations(self):
        """Test memory usage during recommendation generation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large batch of recommendations
        for i in range(50):
            await self.engine.get_recommendations(
                user_id=f"memory_test_user_{i}",
                max_recommendations=100
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 200MB)
        self.assertLess(memory_increase, 200)

    async def test_concurrent_feedback_processing(self):
        """Test concurrent feedback processing"""
        feedback_items = [
            {
                'user_id': f'concurrent_user_{i}',
                'content_id': f'content_{i}',
                'feedback_type': 'rating',
                'value': np.random.uniform(1, 5)
            }
            for i in range(1000)
        ]
        
        start_time = time.time()
        
        # Process feedback in batches
        batch_size = 100
        tasks = []
        for i in range(0, len(feedback_items), batch_size):
            batch = feedback_items[i:i+batch_size]
            task = self.engine.process_feedback_batch(batch)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        execution_time = time.time() - start_time
        
        # Should process 1000 feedback items within 10 seconds
        self.assertLess(execution_time, 10.0)
        self.assertTrue(all(all(batch_results) for batch_results in results))


# Test runner configuration
if __name__ == '__main__':
    # Configure asyncio for testing
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    # Run tests with pytest
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto'
    ])
