# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Utility Functions Tests

Comprehensive tests for utility functions, helpers, and common operations.
Tests data processing, validation, transformation, and configuration utilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import IsolatedAsyncioTestCase
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import time
import os
import sys
import json
import pickle
from collections import defaultdict

# Import the utils modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.utils import (
    DataValidator,
    PersonalizationCache,
    DataConverter,
    PerformanceMonitor,
    FeatureExtractor,
    ConfigurationManager,
    ValidationLevel,
    CacheStrategy,
    PerformanceMetrics
)


class TestDataValidator(IsolatedAsyncioTestCase):
    """Comprehensive tests for DataProcessor utility"""    async def asyncSetUp(self):
        """Set up test environment"""        self.processor = DataProcessor()
        self.test_data = self._generate_test_data()

    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate test data for processing"""        return {
            'user_interactions': [
                {
                    'user_id': 'user_1',
                    'item_id': 'track_1',
                    'rating': 4.5,
                    'timestamp': datetime.utcnow() - timedelta(days=1),
                    'context': {'device': 'mobile', 'location': 'home'}
                },
                {
                    'user_id': 'user_1',
                    'item_id': 'track_2',
                    'rating': 3.0,
                    'timestamp': datetime.utcnow() - timedelta(hours=12),
                    'context': {'device': 'desktop', 'location': 'work'}
                }
            ],
            'item_features': {
                'track_1': {
                    'genre': 'Electronic',
                    'energy': 0.8,
                    'valence': 0.6,
                    'duration': 240
                },
                'track_2': {
                    'genre': 'Pop',
                    'energy': 0.5,
                    'valence': 0.7,
                    'duration': 180
                }
            },
            'user_profiles': {
                'user_1': {
                    'age': 28,
                    'location': 'Berlin',
                    'preferences': {'Electronic': 0.8, 'Pop': 0.6}
                }
            }
        }

    async def test_data_cleaning(self):
        """Test data cleaning functionality"""        # Add some dirty data
        dirty_data = self.test_data['user_interactions'].copy()
        dirty_data.extend([
            {
                'user_id': '',  # Empty user ID
                'item_id': 'track_3',
                'rating': None,  # Missing rating
                'timestamp': 'invalid_date'  # Invalid timestamp
            },
            {
                'user_id': 'user_2',
                'item_id': 'track_4',
                'rating': 10.0,  # Invalid rating (out of range)
                'timestamp': datetime.utcnow()
            }
        ])
        
        cleaned_data = await self.processor.clean_data(
            dirty_data,
            remove_invalid=True,
            fix_ranges={'rating': (0.0, 5.0)}
        )
        
        # Should remove invalid entries and fix ranges
        self.assertLess(len(cleaned_data), len(dirty_data))
        
        for entry in cleaned_data:
            self.assertIsNotNone(entry.get('user_id'))
            self.assertNotEqual(entry.get('user_id'), '')
            if 'rating' in entry and entry['rating'] is not None:
                self.assertGreaterEqual(entry['rating'], 0.0)
                self.assertLessEqual(entry['rating'], 5.0)

    async def test_data_transformation(self):
        """Test data transformation utilities"""        # Transform interaction data to matrix format
        interaction_matrix = await self.processor.to_interaction_matrix(
            self.test_data['user_interactions']
        )
        
        self.assertIsInstance(interaction_matrix, (np.ndarray, pd.DataFrame))
        
        # Transform features to vectors
        feature_vectors = await self.processor.features_to_vectors(
            self.test_data['item_features']
        )
        
        self.assertIsInstance(feature_vectors, dict)
        for item_id, vector in feature_vectors.items():
            self.assertIsInstance(vector, np.ndarray)

    async def test_data_aggregation(self):
        """Test data aggregation operations"""        # Aggregate user interactions by time periods
        aggregated = await self.processor.aggregate_by_time(
            self.test_data['user_interactions'],
            period='daily',
            metrics=['count', 'avg_rating']
        )
        
        self.assertIsInstance(aggregated, dict)
        self.assertIn('daily', aggregated)

    async def test_data_sampling(self):
        """Test data sampling methods"""        # Generate larger dataset for sampling
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'user_id': f'user_{i % 100}',
                'item_id': f'track_{i % 500}',
                'rating': np.random.uniform(1.0, 5.0)
            })
        
        # Test random sampling
        sample = await self.processor.random_sample(large_dataset, size=100)
        self.assertEqual(len(sample), 100)
        
        # Test stratified sampling
        stratified_sample = await self.processor.stratified_sample(
            large_dataset,
            stratify_by='user_id',
            size=200
        )
        self.assertEqual(len(stratified_sample), 200)

    async def test_data_splitting(self):
        """Test data splitting for train/validation/test"""        splits = await self.processor.train_test_split(
            self.test_data['user_interactions'],
            test_size=0.2,
            temporal_split=True
        )
        
        self.assertIn('train', splits)
        self.assertIn('test', splits)
        self.assertGreater(len(splits['train']), 0)
        self.assertGreater(len(splits['test']), 0)

    async def test_missing_data_handling(self):
        """Test missing data handling"""        # Create data with missing values
        data_with_missing = [
            {'user_id': 'user_1', 'rating': 4.0, 'feature_a': 0.8},
            {'user_id': 'user_2', 'rating': None, 'feature_a': 0.6},
            {'user_id': 'user_3', 'rating': 3.5, 'feature_a': None}
        ]
        
        # Impute missing values
        imputed_data = await self.processor.impute_missing_values(
            data_with_missing,
            strategy='mean'
        )
        
        for entry in imputed_data:
            self.assertIsNotNone(entry['rating'])
            self.assertIsNotNone(entry['feature_a'])


class TestConfigManager(IsolatedAsyncioTestCase):
    """Comprehensive tests for ConfigManager utility"""    async def asyncSetUp(self):
        """Set up test environment"""        self.config_manager = ConfigManager()
        self.test_config = {
            'model': {
                'type': 'collaborative_filtering',
                'n_factors': 50,
                'learning_rate': 0.01,
                'regularization': 0.001
            },
            'data': {
                'batch_size': 256,
                'validation_split': 0.2,
                'min_interactions': 5
            },
            'system': {
                'cache_size': 1000,
                'timeout': 30,
                'debug': False
            }
        }

    async def test_config_loading(self):
        """Test configuration loading from various sources"""        # Load from dictionary
        await self.config_manager.load_from_dict(self.test_config)
        
        # Verify loading
        model_config = self.config_manager.get('model')
        self.assertEqual(model_config['type'], 'collaborative_filtering')
        self.assertEqual(model_config['n_factors'], 50)

    async def test_config_validation(self):
        """Test configuration validation"""        # Define schema for validation
        schema = {
            'model': {
                'type': str,
                'n_factors': int,
                'learning_rate': float
            },
            'data': {
                'batch_size': int,
                'validation_split': float
            }
        }
        
        # Validate correct config
        is_valid = await self.config_manager.validate(self.test_config, schema)
        self.assertTrue(is_valid)
        
        # Test invalid config
        invalid_config = self.test_config.copy()
        invalid_config['model']['n_factors'] = 'invalid'  # Should be int
        
        is_valid = await self.config_manager.validate(invalid_config, schema)
        self.assertFalse(is_valid)

    async def test_config_merging(self):
        """Test configuration merging"""        base_config = {'model': {'n_factors': 50}, 'data': {'batch_size': 256}}
        override_config = {'model': {'n_factors': 100}, 'system': {'debug': True}}
        
        merged = await self.config_manager.merge_configs(base_config, override_config)
        
        self.assertEqual(merged['model']['n_factors'], 100)  # Overridden
        self.assertEqual(merged['data']['batch_size'], 256)  # From base
        self.assertTrue(merged['system']['debug'])           # New key

    async def test_environment_variable_substitution(self):
        """Test environment variable substitution"""        # Set environment variable
        os.environ['TEST_LEARNING_RATE'] = '0.05'
        
        config_with_env = {
            'model': {
                'learning_rate': '${TEST_LEARNING_RATE}',
                'type': 'collaborative'
            }
        }
        
        resolved_config = await self.config_manager.resolve_environment_variables(
            config_with_env
        )
        
        self.assertEqual(resolved_config['model']['learning_rate'], '0.05')
        
        # Clean up
        del os.environ['TEST_LEARNING_RATE']

    async def test_config_encryption(self):
        """Test configuration encryption/decryption"""        sensitive_config = {
            'api_keys': {
                'spotify': 'secret_spotify_key',
                'database': 'secret_db_password'
            }
        }
        
        # Encrypt sensitive data
        encrypted_config = await self.config_manager.encrypt_sensitive_data(
            sensitive_config,
            key_phrase='test_encryption_key'
        )
        
        # Verify encryption
        self.assertNotEqual(
            encrypted_config['api_keys']['spotify'],
            sensitive_config['api_keys']['spotify']
        )
        
        # Decrypt and verify
        decrypted_config = await self.config_manager.decrypt_sensitive_data(
            encrypted_config,
            key_phrase='test_encryption_key'
        )
        
        self.assertEqual(
            decrypted_config['api_keys']['spotify'],
            sensitive_config['api_keys']['spotify']
        )


class TestValidationUtils(IsolatedAsyncioTestCase):
    """Comprehensive tests for ValidationUtils"""    async def asyncSetUp(self):
        """Set up test environment"""        self.validator = ValidationUtils()

    async def test_data_type_validation(self):
        """Test data type validation"""        # Valid data types
        self.assertTrue(await self.validator.validate_type('hello', str))
        self.assertTrue(await self.validator.validate_type(42, int))
        self.assertTrue(await self.validator.validate_type(3.14, float))
        self.assertTrue(await self.validator.validate_type([1, 2, 3], list))
        
        # Invalid data types
        self.assertFalse(await self.validator.validate_type('hello', int))
        self.assertFalse(await self.validator.validate_type(42, str))

    async def test_range_validation(self):
        """Test range validation"""        # Valid ranges
        self.assertTrue(await self.validator.validate_range(5, 1, 10))
        self.assertTrue(await self.validator.validate_range(0.5, 0.0, 1.0))
        
        # Invalid ranges
        self.assertFalse(await self.validator.validate_range(15, 1, 10))
        self.assertFalse(await self.validator.validate_range(-0.5, 0.0, 1.0))

    async def test_format_validation(self):
        """Test format validation"""        # Email validation
        self.assertTrue(await self.validator.validate_email('test@example.com'))
        self.assertFalse(await self.validator.validate_email('invalid_email'))
        
        # URL validation
        self.assertTrue(await self.validator.validate_url('https://example.com'))
        self.assertFalse(await self.validator.validate_url('not_a_url'))
        
        # User ID format
        self.assertTrue(await self.validator.validate_user_id('user_12345'))
        self.assertFalse(await self.validator.validate_user_id(''))

    async def test_schema_validation(self):
        """Test schema validation"""        schema = {
            'name': str,
            'age': int,
            'rating': float,
            'tags': list
        }
        
        valid_data = {
            'name': 'John Doe',
            'age': 30,
            'rating': 4.5,
            'tags': ['tag1', 'tag2']
        }
        
        invalid_data = {
            'name': 123,  # Should be string
            'age': '30',  # Should be int
            'rating': 4.5,
            'tags': 'not_a_list'  # Should be list
        }
        
        self.assertTrue(await self.validator.validate_schema(valid_data, schema))
        self.assertFalse(await self.validator.validate_schema(invalid_data, schema))

    async def test_custom_validation_rules(self):
        """Test custom validation rules"""        # Define custom validator
        async def validate_positive_number(value):
            return isinstance(value, (int, float)) and value > 0
        
        # Register custom validator
        self.validator.register_custom_validator('positive_number', validate_positive_number)
        
        # Test custom validation
        self.assertTrue(await self.validator.apply_custom_validation(5, 'positive_number'))
        self.assertFalse(await self.validator.apply_custom_validation(-5, 'positive_number'))


class TestTransformationUtils(IsolatedAsyncioTestCase):
    """Comprehensive tests for TransformationUtils"""    async def asyncSetUp(self):
        """Set up test environment"""        self.transformer = TransformationUtils()

    async def test_data_normalization(self):
        """Test data normalization methods"""        data = [1, 2, 3, 4, 5]
        
        # Min-max normalization
        normalized = await self.transformer.min_max_normalize(data)
        self.assertAlmostEqual(min(normalized), 0.0, places=5)
        self.assertAlmostEqual(max(normalized), 1.0, places=5)
        
        # Z-score normalization
        z_normalized = await self.transformer.z_score_normalize(data)
        self.assertAlmostEqual(np.mean(z_normalized), 0.0, places=5)
        self.assertAlmostEqual(np.std(z_normalized), 1.0, places=5)

    async def test_categorical_encoding(self):
        """Test categorical encoding methods"""        categories = ['pop', 'rock', 'jazz', 'pop', 'electronic', 'rock']
        
        # One-hot encoding
        one_hot = await self.transformer.one_hot_encode(categories)
        self.assertIsInstance(one_hot, np.ndarray)
        self.assertEqual(one_hot.shape[0], len(categories))
        
        # Label encoding
        label_encoded = await self.transformer.label_encode(categories)
        self.assertIsInstance(label_encoded, np.ndarray)
        self.assertEqual(len(label_encoded), len(categories))

    async def test_feature_scaling(self):
        """Test feature scaling methods"""        features = np.random.randn(100, 5)
        
        # Standard scaling
        scaled = await self.transformer.standard_scale(features)
        self.assertAlmostEqual(np.mean(scaled), 0.0, places=1)
        self.assertAlmostEqual(np.std(scaled), 1.0, places=1)
        
        # Robust scaling
        robust_scaled = await self.transformer.robust_scale(features)
        self.assertIsInstance(robust_scaled, np.ndarray)
        self.assertEqual(robust_scaled.shape, features.shape)

    async def test_dimensionality_reduction(self):
        """Test dimensionality reduction methods"""        high_dim_data = np.random.randn(100, 50)
        
        # PCA
        pca_reduced = await self.transformer.apply_pca(high_dim_data, n_components=10)
        self.assertEqual(pca_reduced.shape, (100, 10))
        
        # t-SNE (smaller dataset for speed)
        small_data = high_dim_data[:20, :10]
        tsne_reduced = await self.transformer.apply_tsne(small_data, n_components=2)
        self.assertEqual(tsne_reduced.shape, (20, 2))

    async def test_text_transformation(self):
        """Test text transformation utilities"""        texts = ['This is a sample text', 'Another example document', 'Machine learning rocks']
        
        # TF-IDF transformation
        tfidf_matrix = await self.transformer.text_to_tfidf(texts)
        self.assertEqual(tfidf_matrix.shape[0], len(texts))
        
        # Text cleaning
        dirty_text = 'This is DIRTY text with 123 numbers!@#'
        cleaned = await self.transformer.clean_text(dirty_text)
        self.assertNotIn('123', cleaned)
        self.assertNotIn('!@#', cleaned)


class TestCachingUtils(IsolatedAsyncioTestCase):
    """Comprehensive tests for CachingUtils"""    async def asyncSetUp(self):
        """Set up test environment"""        self.cache = CachingUtils(max_size=100, ttl=3600)

    async def test_basic_caching(self):
        """Test basic cache operations"""        # Set cache value
        await self.cache.set('key1', 'value1')
        
        # Get cache value
        value = await self.cache.get('key1')
        self.assertEqual(value, 'value1')
        
        # Check existence
        exists = await self.cache.exists('key1')
        self.assertTrue(exists)
        
        # Delete cache value
        await self.cache.delete('key1')
        value = await self.cache.get('key1')
        self.assertIsNone(value)

    async def test_cache_expiration(self):
        """Test cache expiration (TTL)"""        # Set value with short TTL
        await self.cache.set('temp_key', 'temp_value', ttl=1)
        
        # Should exist immediately
        value = await self.cache.get('temp_key')
        self.assertEqual(value, 'temp_value')
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        value = await self.cache.get('temp_key')
        self.assertIsNone(value)

    async def test_cache_size_limit(self):
        """Test cache size limitations"""        small_cache = CachingUtils(max_size=3)
        
        # Fill cache beyond limit
        await small_cache.set('key1', 'value1')
        await small_cache.set('key2', 'value2')
        await small_cache.set('key3', 'value3')
        await small_cache.set('key4', 'value4')  # Should evict oldest
        
        # First key should be evicted
        value1 = await small_cache.get('key1')
        value4 = await small_cache.get('key4')
        
        self.assertIsNone(value1)
        self.assertEqual(value4, 'value4')

    async def test_cache_patterns(self):
        """Test common caching patterns"""        # Memoization pattern
        call_count = 0
        
        async def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute function
        result1 = await self.cache.memoize('func_key_5', expensive_function, 5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call - should use cache
        result2 = await self.cache.memoize('func_key_5', expensive_function, 5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increase


class TestSimilarityCalculator(IsolatedAsyncioTestCase):
    """Comprehensive tests for SimilarityCalculator"""    async def asyncSetUp(self):
        """Set up test environment"""        self.calculator = SimilarityCalculator()

    async def test_cosine_similarity(self):
        """Test cosine similarity calculation"""        vector1 = np.array([1, 2, 3])
        vector2 = np.array([2, 4, 6])  # Parallel vector
        vector3 = np.array([-1, -2, -3])  # Opposite vector
        
        # Parallel vectors should have similarity close to 1
        sim1 = await self.calculator.cosine_similarity(vector1, vector2)
        self.assertAlmostEqual(sim1, 1.0, places=5)
        
        # Opposite vectors should have similarity close to -1
        sim2 = await self.calculator.cosine_similarity(vector1, vector3)
        self.assertAlmostEqual(sim2, -1.0, places=5)

    async def test_euclidean_distance(self):
        """Test Euclidean distance calculation"""        point1 = np.array([0, 0])
        point2 = np.array([3, 4])
        
        distance = await self.calculator.euclidean_distance(point1, point2)
        self.assertAlmostEqual(distance, 5.0, places=5)  # 3-4-5 triangle

    async def test_jaccard_similarity(self):
        """Test Jaccard similarity for sets"""        set1 = {'a', 'b', 'c', 'd'}
        set2 = {'b', 'c', 'd', 'e'}
        
        jaccard = await self.calculator.jaccard_similarity(set1, set2)
        expected = 3 / 5  # |intersection| / |union| = 3 / 5
        self.assertAlmostEqual(jaccard, expected, places=5)

    async def test_pearson_correlation(self):
        """Test Pearson correlation coefficient"""        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])  # Perfect positive correlation
        
        correlation = await self.calculator.pearson_correlation(x, y)
        self.assertAlmostEqual(correlation, 1.0, places=5)

    async def test_similarity_matrix(self):
        """Test similarity matrix computation"""        vectors = [
            np.array([1, 0, 0]),
            np.array([0, 1, 0]),
            np.array([0, 0, 1]),
            np.array([1, 1, 0])
        ]
        
        sim_matrix = await self.calculator.compute_similarity_matrix(
            vectors, method='cosine'
        )
        
        self.assertEqual(sim_matrix.shape, (4, 4))
        
        # Diagonal should be 1 (self-similarity)
        for i in range(4):
            self.assertAlmostEqual(sim_matrix[i, i], 1.0, places=5)
        
        # Matrix should be symmetric
        for i in range(4):
            for j in range(4):
                self.assertAlmostEqual(sim_matrix[i, j], sim_matrix[j, i], places=5)


class TestFeatureEngineering(IsolatedAsyncioTestCase):
    """Comprehensive tests for FeatureEngineering"""    async def asyncSetUp(self):
        """Set up test environment"""        self.feature_engineer = FeatureEngineering()

    async def test_polynomial_features(self):
        """Test polynomial feature generation"""        features = np.array([[1, 2], [3, 4], [5, 6]])
        
        poly_features = await self.feature_engineer.create_polynomial_features(
            features, degree=2
        )
        
        # Should include original features, interactions, and squares
        self.assertGreater(poly_features.shape[1], features.shape[1])

    async def test_interaction_features(self):
        """Test interaction feature creation"""        categorical_features = {
            'genre': ['pop', 'rock', 'jazz'],
            'mood': ['happy', 'sad', 'energetic']
        }
        
        interactions = await self.feature_engineer.create_interaction_features(
            categorical_features
        )
        
        self.assertIsInstance(interactions, dict)
        self.assertIn('genre_mood', interactions)

    async def test_temporal_features(self):
        """Test temporal feature extraction"""        timestamps = [
            datetime(2024, 1, 15, 14, 30),  # Monday afternoon
            datetime(2024, 1, 16, 9, 15),   # Tuesday morning
            datetime(2024, 1, 20, 20, 45)   # Saturday evening
        ]
        
        temporal_features = await self.feature_engineer.extract_temporal_features(
            timestamps
        )
        
        self.assertIsInstance(temporal_features, list)
        for features in temporal_features:
            self.assertIn('hour', features)
            self.assertIn('day_of_week', features)
            self.assertIn('is_weekend', features)

    async def test_statistical_features(self):
        """Test statistical feature computation"""        user_interactions = {
            'user_1': [4.5, 3.0, 4.0, 5.0, 2.5],
            'user_2': [3.5, 3.5, 3.5, 3.5, 3.5],
            'user_3': [1.0, 5.0, 2.0, 4.0, 3.0]
        }
        
        stats_features = await self.feature_engineer.compute_statistical_features(
            user_interactions
        )
        
        for user_id, features in stats_features.items():
            self.assertIn('mean', features)
            self.assertIn('std', features)
            self.assertIn('min', features)
            self.assertIn('max', features)
            self.assertIn('median', features)

    async def test_frequency_features(self):
        """Test frequency-based feature extraction"""        item_interactions = [
            'track_1', 'track_2', 'track_1', 'track_3', 'track_1', 'track_2'
        ]
        
        freq_features = await self.feature_engineer.compute_frequency_features(
            item_interactions
        )
        
        self.assertIsInstance(freq_features, dict)
        self.assertEqual(freq_features['track_1'], 3)
        self.assertEqual(freq_features['track_2'], 2)
        self.assertEqual(freq_features['track_3'], 1)

    async def test_embedding_features(self):
        """Test embedding-based feature creation"""        # Mock item embeddings
        item_embeddings = {
            'track_1': np.random.randn(50),
            'track_2': np.random.randn(50),
            'track_3': np.random.randn(50)
        }
        
        user_history = ['track_1', 'track_2', 'track_1']
        
        user_embedding = await self.feature_engineer.create_user_embedding_from_history(
            user_history, item_embeddings
        )
        
        self.assertIsInstance(user_embedding, np.ndarray)
        self.assertEqual(len(user_embedding), 50)


class TestPerformanceUtils(IsolatedAsyncioTestCase):
    """Comprehensive tests for PerformanceUtils"""    async def asyncSetUp(self):
        """Set up test environment"""        self.perf_utils = PerformanceUtils()

    async def test_timing_decorator(self):
        """Test timing decorator functionality"""        @self.perf_utils.time_it
        async def slow_function():
            await asyncio.sleep(0.1)
            return "completed"
        
        result, execution_time = await slow_function()
        
        self.assertEqual(result, "completed")
        self.assertGreater(execution_time, 0.1)
        self.assertLess(execution_time, 0.2)  # Should be close to 0.1

    async def test_memory_profiling(self):
        """Test memory profiling utilities"""        initial_memory = await self.perf_utils.get_memory_usage()
        
        # Allocate some memory
        large_list = [i for i in range(100000)]
        
        peak_memory = await self.perf_utils.get_memory_usage()
        
        # Clean up
        del large_list
        
        final_memory = await self.perf_utils.get_memory_usage()
        
        self.assertGreater(peak_memory, initial_memory)

    async def test_performance_monitoring(self):
        """Test performance monitoring context manager"""        async with self.perf_utils.monitor_performance() as monitor:
            # Simulate some work
            await asyncio.sleep(0.05)
            data = [i ** 2 for i in range(1000)]
        
        metrics = monitor.get_metrics()
        
        self.assertIn('execution_time', metrics)
        self.assertIn('memory_used', metrics)
        self.assertGreater(metrics['execution_time'], 0.05)

    async def test_batching_utility(self):
        """Test data batching for performance"""        large_dataset = list(range(1000))
        
        batches = await self.perf_utils.create_batches(large_dataset, batch_size=100)
        
        self.assertEqual(len(batches), 10)
        for batch in batches:
            self.assertLessEqual(len(batch), 100)

    async def test_parallel_processing(self):
        """Test parallel processing utilities"""        async def square_number(x):
            await asyncio.sleep(0.001)  # Simulate work
            return x ** 2
        
        numbers = list(range(20))
        
        # Sequential processing
        start_time = time.time()
        sequential_results = []
        for num in numbers:
            result = await square_number(num)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Parallel processing
        start_time = time.time()
        parallel_results = await self.perf_utils.process_parallel(
            square_number, numbers, max_workers=5
        )
        parallel_time = time.time() - start_time
        
        # Results should be the same
        self.assertEqual(sequential_results, parallel_results)
        
        # Parallel should be faster (with some tolerance)
        self.assertLess(parallel_time, sequential_time * 0.8)


class TestSecurityUtils(IsolatedAsyncioTestCase):
    """Comprehensive tests for SecurityUtils"""    async def asyncSetUp(self):
        """Set up test environment"""        self.security = SecurityUtils()

    async def test_data_encryption(self):
        """Test data encryption and decryption"""        sensitive_data = "user_password_123"
        encryption_key = "test_encryption_key"
        
        # Encrypt data
        encrypted = await self.security.encrypt_data(sensitive_data, encryption_key)
        self.assertNotEqual(encrypted, sensitive_data)
        
        # Decrypt data
        decrypted = await self.security.decrypt_data(encrypted, encryption_key)
        self.assertEqual(decrypted, sensitive_data)

    async def test_data_anonymization(self):
        """Test data anonymization"""        personal_data = {
            'user_id': 'user_12345',
            'email': 'john.doe@example.com',
            'name': 'John Doe',
            'phone': '+1-555-123-4567',
            'preferences': {'genre': 'pop', 'energy': 0.8}
        }
        
        anonymized = await self.security.anonymize_data(
            personal_data,
            sensitive_fields=['email', 'name', 'phone']
        )
        
        self.assertEqual(anonymized['user_id'], 'user_12345')  # Not sensitive
        self.assertEqual(anonymized['preferences'], personal_data['preferences'])  # Not sensitive
        self.assertNotEqual(anonymized['email'], personal_data['email'])  # Anonymized
        self.assertNotEqual(anonymized['name'], personal_data['name'])  # Anonymized

    async def test_input_sanitization(self):
        """Test input sanitization"""        dangerous_input = "<script>alert('xss')</script>Hello World"
        
        sanitized = await self.security.sanitize_input(dangerous_input)
        
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('alert', sanitized)
        self.assertIn('Hello World', sanitized)

    async def test_access_control(self):
        """Test access control mechanisms"""        user_permissions = {
            'user_1': ['read', 'write'],
            'user_2': ['read'],
            'admin': ['read', 'write', 'delete']
        }
        
        # Test permissions
        self.assertTrue(await self.security.check_permission('user_1', 'read', user_permissions))
        self.assertTrue(await self.security.check_permission('user_1', 'write', user_permissions))
        self.assertFalse(await self.security.check_permission('user_1', 'delete', user_permissions))
        
        self.assertTrue(await self.security.check_permission('admin', 'delete', user_permissions))
        self.assertFalse(await self.security.check_permission('user_2', 'write', user_permissions))

    async def test_rate_limiting(self):
        """Test rate limiting functionality"""        rate_limiter = await self.security.create_rate_limiter(
            max_requests=3,
            time_window=1  # 1 second
        )
        
        # Should allow first 3 requests
        for i in range(3):
            allowed = await rate_limiter.is_allowed('user_test')
            self.assertTrue(allowed)
        
        # Should deny 4th request
        allowed = await rate_limiter.is_allowed('user_test')
        self.assertFalse(allowed)
        
        # Should allow again after time window
        await asyncio.sleep(1.1)
        allowed = await rate_limiter.is_allowed('user_test')
        self.assertTrue(allowed)


class TestUtilsPerformanceAndIntegration(IsolatedAsyncioTestCase):
    """Performance and integration tests for utilities"""    async def test_large_dataset_processing(self):
        """Test utility performance on large datasets"""        processor = DataProcessor()
        
        # Generate large dataset
        large_dataset = []
        for i in range(10000):
            large_dataset.append({
                'user_id': f'user_{i % 1000}',
                'item_id': f'item_{i % 5000}',
                'rating': np.random.uniform(1.0, 5.0),
                'timestamp': datetime.utcnow() - timedelta(days=np.random.randint(0, 365))
            })
        
        # Measure processing time
        start_time = time.time()
        
        # Clean data
        cleaned = await processor.clean_data(large_dataset)
        
        # Transform to matrix
        matrix = await processor.to_interaction_matrix(cleaned)
        
        processing_time = time.time() - start_time
        
        # Should process within reasonable time
        self.assertLess(processing_time, 10.0)  # 10 seconds max
        self.assertIsNotNone(matrix)

    async def test_utility_integration(self):
        """Test integration between different utilities"""        # Use multiple utilities together
        processor = DataProcessor()
        transformer = TransformationUtils()
        cache = CachingUtils()
        validator = ValidationUtils()
        
        # Create test pipeline
        raw_data = [
            {'user_id': 'user_1', 'features': [1, 2, 3], 'category': 'pop'},
            {'user_id': 'user_2', 'features': [4, 5, 6], 'category': 'rock'}
        ]
        
        # Validate data
        for item in raw_data:
            is_valid = await validator.validate_schema(item, {
                'user_id': str,
                'features': list,
                'category': str
            })
            self.assertTrue(is_valid)
        
        # Clean and transform data
        cleaned = await processor.clean_data(raw_data)
        
        # Extract and normalize features
        feature_vectors = []
        for item in cleaned:
            features = np.array(item['features'])
            normalized = await transformer.min_max_normalize(features)
            feature_vectors.append(normalized)
        
        # Cache results
        await cache.set('processed_features', feature_vectors)
        
        # Retrieve from cache
        cached_features = await cache.get('processed_features')
        
        self.assertEqual(len(cached_features), len(feature_vectors))
        np.testing.assert_array_equal(cached_features[0], feature_vectors[0])


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=10'
    ])
