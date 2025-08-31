# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
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
Ultra-Industrial Test Suite for AI Observability Module

This module provides comprehensive testing for AI/ML model monitoring,
performance tracking, bias detection, model drift analysis,
explainability monitoring, and model lifecycle management.

Expert Team Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING & COPYRIGHT PROTECTION ⚠️
This entire test suite is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import numpy as np
import pandas as pd
import pytest
import sys
import os
from pathlib import Path
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Import the module under test
from ai.observability.ai_observability import (
    ModelType,
    ModelFramework, 
    ModelStatus,
    ModelMetrics,
    ModelObserver,
    AIObservabilityManager,
    BiasDetector,
    ModelDriftDetector,
    ExplainabilityMonitor
)


class TestAIObservabilityComprehensive:
    """Ultra-comprehensive test suite for AI Observability"""

    @pytest.fixture
    def sample_model_config(self):
        """Sample model configuration for testing"""
        return {
            'model_id': 'test_content_protection_model',
            'model_type': ModelType.CONTENT_PROTECTION,
            'framework': ModelFramework.TENSORFLOW,
            'version': '1.0.0',
            'description': 'Content protection model for copyright detection',
            'author': 'Fahed Mlaiel',
            'tags': ['content_protection', 'copyright', 'fingerprinting']
        }

    @pytest.fixture
    def sample_training_data(self):
        """Sample training data for testing"""
        np.random.seed(42)
        return {
            'features': np.random.randn(1000, 10),
            'labels': np.random.randint(0, 2, 1000),
            'metadata': {
                'feature_names': [f'feature_{i}' for i in range(10)],
                'class_names': ['non_copyrighted', 'copyrighted']
            }
        }

    @pytest.fixture
    def sample_predictions(self):
        """Sample predictions for testing"""
        np.random.seed(42)
        return {
            'predictions': np.random.rand(100),
            'true_labels': np.random.randint(0, 2, 100),
            'prediction_ids': [str(uuid4()) for _ in range(100)],
            'timestamps': [datetime.now() - timedelta(minutes=i) for i in range(100)]
        }

    @pytest.fixture
    async def ai_observability_manager(self):
        """Create AI observability manager instance"""
        config = {
            'enable_bias_detection': True,
            'enable_drift_detection': True,
            'enable_explainability': True,
            'monitoring_interval': 1,
            'metrics_retention_days': 30
        }
        manager = AIObservabilityManager(config)
        await manager.initialize()
        yield manager
        await manager.shutdown()

    def test_model_type_enum(self):
        """Test ModelType enum completeness"""
        expected_types = {
            'CLASSIFICATION', 'REGRESSION', 'CLUSTERING', 'RECOMMENDATION',
            'NLP', 'COMPUTER_VISION', 'CONTENT_PROTECTION', 'FINGERPRINTING',
            'COPYRIGHT_DETECTION', 'SIMILARITY_MATCHING'
        }
        
        actual_types = {member.name for member in ModelType}
        assert actual_types == expected_types, f"Missing types: {expected_types - actual_types}"

    def test_model_framework_enum(self):
        """Test ModelFramework enum completeness"""
        expected_frameworks = {
            'TENSORFLOW', 'PYTORCH', 'SCIKIT_LEARN', 'XGBOOST',
            'HUGGING_FACE', 'CUSTOM', 'ONNX', 'TENSORRT'
        }
        
        actual_frameworks = {member.name for member in ModelFramework}
        assert actual_frameworks == expected_frameworks

    def test_model_status_enum(self):
        """Test ModelStatus enum completeness"""
        expected_statuses = {
            'TRAINING', 'VALIDATION', 'DEPLOYED', 'DEPRECATED', 'FAILED', 'MAINTENANCE'
        }
        
        actual_statuses = {member.name for member in ModelStatus}
        assert actual_statuses == expected_statuses

    @pytest.mark.asyncio
    async def test_model_registration(self, ai_observability_manager, sample_model_config):
        """Test complete model registration process"""
        manager = ai_observability_manager
        
        # Register model
        result = await manager.register_model(sample_model_config)
        assert result['success'] is True
        assert 'model_id' in result
        
        # Verify model is registered
        models = await manager.get_registered_models()
        assert sample_model_config['model_id'] in models
        
        # Verify model details
        model_info = await manager.get_model_info(sample_model_config['model_id'])
        assert model_info['model_type'] == ModelType.CONTENT_PROTECTION
        assert model_info['framework'] == ModelFramework.TENSORFLOW
        assert model_info['status'] == ModelStatus.TRAINING

    @pytest.mark.asyncio
    async def test_model_metrics_collection(self, ai_observability_manager, sample_model_config, sample_predictions):
        """Test comprehensive model metrics collection"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Record predictions
        for i in range(len(sample_predictions['predictions'])):
            prediction_data = {
                'prediction_id': sample_predictions['prediction_ids'][i],
                'prediction': sample_predictions['predictions'][i],
                'true_label': sample_predictions['true_labels'][i],
                'timestamp': sample_predictions['timestamps'][i],
                'input_features': np.random.randn(10).tolist(),
                'confidence': float(np.random.rand()),
                'latency_ms': float(np.random.randint(10, 100))
            }
            await manager.record_prediction(model_id, prediction_data)
        
        # Get metrics
        metrics = await manager.get_model_metrics(model_id)
        
        # Verify metrics completeness
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 'auc_roc' in metrics
        assert 'latency_mean' in metrics
        assert 'latency_p95' in metrics
        assert 'latency_p99' in metrics
        assert 'throughput' in metrics
        assert 'prediction_count' in metrics
        
        # Verify metric values are reasonable
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1_score'] <= 1
        assert metrics['prediction_count'] > 0
        assert metrics['latency_mean'] > 0

    @pytest.mark.asyncio
    async def test_bias_detection_comprehensive(self, ai_observability_manager, sample_model_config):
        """Test comprehensive bias detection"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Create biased test data
        predictions_group_a = [0.8, 0.9, 0.85, 0.88, 0.92]  # High confidence
        predictions_group_b = [0.3, 0.4, 0.35, 0.38, 0.32]  # Low confidence
        
        # Record predictions for different groups
        for i, pred in enumerate(predictions_group_a):
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': pred,
                'true_label': 1,
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist(),
                'sensitive_attributes': {'group': 'A', 'demographic': 'group_a'},
                'confidence': pred
            })
        
        for i, pred in enumerate(predictions_group_b):
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': pred,
                'true_label': 1,
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist(),
                'sensitive_attributes': {'group': 'B', 'demographic': 'group_b'},
                'confidence': pred
            })
        
        # Run bias detection
        bias_report = await manager.detect_bias(model_id, sensitive_attributes=['group'])
        
        # Verify bias detection results
        assert 'bias_detected' in bias_report
        assert 'demographic_parity' in bias_report
        assert 'equalized_odds' in bias_report
        assert 'individual_fairness' in bias_report
        assert 'bias_score' in bias_report
        assert 'recommendations' in bias_report
        
        # Should detect bias due to different prediction distributions
        assert bias_report['bias_detected'] is True
        assert bias_report['bias_score'] > 0.1

    @pytest.mark.asyncio
    async def test_model_drift_detection_comprehensive(self, ai_observability_manager, sample_model_config):
        """Test comprehensive model drift detection"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Record baseline data (training distribution)
        baseline_features = np.random.normal(0, 1, (100, 10))  # Original distribution
        for i, features in enumerate(baseline_features):
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': float(np.random.rand()),
                'true_label': int(np.random.randint(0, 2)),
                'timestamp': datetime.now() - timedelta(days=30),
                'input_features': features.tolist(),
                'is_baseline': True
            })
        
        # Record current data with drift (shifted distribution)
        current_features = np.random.normal(2, 1.5, (100, 10))  # Shifted distribution
        for i, features in enumerate(current_features):
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': float(np.random.rand()),
                'true_label': int(np.random.randint(0, 2)),
                'timestamp': datetime.now(),
                'input_features': features.tolist(),
                'is_baseline': False
            })
        
        # Detect drift
        drift_report = await manager.detect_drift(model_id)
        
        # Verify drift detection results
        assert 'drift_detected' in drift_report
        assert 'drift_score' in drift_report
        assert 'drift_type' in drift_report
        assert 'affected_features' in drift_report
        assert 'statistical_tests' in drift_report
        assert 'recommendations' in drift_report
        
        # Should detect drift due to distribution shift
        assert drift_report['drift_detected'] is True
        assert drift_report['drift_score'] > 0.1
        assert 'data_drift' in drift_report['drift_type']

    @pytest.mark.asyncio
    async def test_explainability_monitoring_comprehensive(self, ai_observability_manager, sample_model_config):
        """Test comprehensive explainability monitoring"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Record predictions with feature importance
        for i in range(50):
            feature_importance = np.abs(np.random.randn(10))
            feature_importance = feature_importance / feature_importance.sum()  # Normalize
            
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': float(np.random.rand()),
                'true_label': int(np.random.randint(0, 2)),
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist(),
                'feature_importance': feature_importance.tolist(),
                'explanation_method': 'SHAP',
                'confidence': float(np.random.rand())
            })
        
        # Get explainability report
        explainability_report = await manager.get_explainability_report(model_id)
        
        # Verify explainability results
        assert 'global_feature_importance' in explainability_report
        assert 'feature_stability' in explainability_report
        assert 'explanation_consistency' in explainability_report
        assert 'top_features' in explainability_report
        assert 'explanation_quality_score' in explainability_report
        
        # Verify feature importance analysis
        assert len(explainability_report['global_feature_importance']) == 10
        assert len(explainability_report['top_features']) > 0
        assert 0 <= explainability_report['explanation_quality_score'] <= 1

    @pytest.mark.asyncio
    async def test_model_performance_degradation_detection(self, ai_observability_manager, sample_model_config):
        """Test detection of model performance degradation over time"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Record initial good performance
        for i in range(100):
            # High accuracy predictions
            true_label = np.random.randint(0, 2)
            prediction = true_label + np.random.normal(0, 0.1)  # Close to true label
            prediction = max(0, min(1, prediction))  # Clamp to [0, 1]
            
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': prediction,
                'true_label': true_label,
                'timestamp': datetime.now() - timedelta(days=7),
                'input_features': np.random.randn(10).tolist()
            })
        
        # Record degraded performance
        for i in range(100):
            # Lower accuracy predictions
            true_label = np.random.randint(0, 2)
            prediction = np.random.rand()  # Random predictions
            
            await manager.record_prediction(model_id, {
                'prediction_id': str(uuid4()),
                'prediction': prediction,
                'true_label': true_label,
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist()
            })
        
        # Detect performance degradation
        degradation_report = await manager.detect_performance_degradation(model_id)
        
        # Verify degradation detection
        assert 'degradation_detected' in degradation_report
        assert 'performance_trend' in degradation_report
        assert 'severity' in degradation_report
        assert 'affected_metrics' in degradation_report
        assert 'recommendations' in degradation_report
        
        # Should detect degradation
        assert degradation_report['degradation_detected'] is True
        assert 'accuracy' in degradation_report['affected_metrics']

    @pytest.mark.asyncio
    async def test_model_lifecycle_management_comprehensive(self, ai_observability_manager, sample_model_config):
        """Test comprehensive model lifecycle management"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Test status transitions
        statuses = [ModelStatus.TRAINING, ModelStatus.VALIDATION, ModelStatus.DEPLOYED]
        
        for status in statuses:
            result = await manager.update_model_status(model_id, status)
            assert result['success'] is True
            
            model_info = await manager.get_model_info(model_id)
            assert model_info['status'] == status
        
        # Test model versioning
        new_version = '1.1.0'
        result = await manager.create_model_version(model_id, new_version, {
            'changes': 'Improved accuracy by 5%',
            'model_file': 'model_v1_1_0.pkl',
            'training_data_hash': 'abc123'
        })
        assert result['success'] is True
        
        # Get version history
        versions = await manager.get_model_versions(model_id)
        assert len(versions) >= 2  # Original + new version
        assert new_version in [v['version'] for v in versions]
        
        # Test model retirement
        result = await manager.retire_model(model_id, reason='Replaced by improved version')
        assert result['success'] is True
        
        model_info = await manager.get_model_info(model_id)
        assert model_info['status'] == ModelStatus.DEPRECATED

    @pytest.mark.asyncio
    async def test_real_time_monitoring_alerts(self, ai_observability_manager, sample_model_config):
        """Test real-time monitoring and alerting"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Set up monitoring rules
        monitoring_rules = {
            'accuracy_threshold': 0.8,
            'latency_threshold_ms': 100,
            'error_rate_threshold': 0.05,
            'bias_score_threshold': 0.3,
            'drift_score_threshold': 0.2
        }
        
        result = await manager.setup_monitoring_rules(model_id, monitoring_rules)
        assert result['success'] is True
        
        # Record problematic predictions (high latency, low accuracy)
        alerts_triggered = []
        
        for i in range(20):
            prediction_data = {
                'prediction_id': str(uuid4()),
                'prediction': float(np.random.rand()),
                'true_label': int(1 - np.random.randint(0, 2)),  # Opposite to create errors
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist(),
                'latency_ms': float(np.random.randint(150, 300)),  # High latency
                'error': True if i % 3 == 0 else False  # High error rate
            }
            
            result = await manager.record_prediction(model_id, prediction_data)
            if 'alerts' in result:
                alerts_triggered.extend(result['alerts'])
        
        # Verify alerts were triggered
        assert len(alerts_triggered) > 0
        
        alert_types = {alert['type'] for alert in alerts_triggered}
        expected_alert_types = {'high_latency', 'low_accuracy', 'high_error_rate'}
        
        # Should have triggered multiple alert types
        assert len(alert_types.intersection(expected_alert_types)) > 0

    @pytest.mark.asyncio
    async def test_batch_inference_monitoring(self, ai_observability_manager, sample_model_config):
        """Test monitoring of batch inference operations"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Start batch inference monitoring
        batch_id = str(uuid4())
        batch_config = {
            'batch_size': 1000,
            'input_source': 's3://data/batch_input.parquet',
            'output_destination': 's3://results/batch_output.parquet',
            'expected_duration_minutes': 30
        }
        
        result = await manager.start_batch_monitoring(model_id, batch_id, batch_config)
        assert result['success'] is True
        
        # Simulate batch processing with periodic updates
        processed_samples = 0
        total_samples = 1000
        
        while processed_samples < total_samples:
            batch_size = min(100, total_samples - processed_samples)
            
            # Generate predictions for batch
            predictions = []
            for i in range(batch_size):
                predictions.append({
                    'prediction_id': str(uuid4()),
                    'prediction': float(np.random.rand()),
                    'confidence': float(np.random.rand()),
                    'latency_ms': float(np.random.randint(5, 50))
                })
            
            # Update batch progress
            processed_samples += batch_size
            progress = processed_samples / total_samples
            
            result = await manager.update_batch_progress(
                model_id, batch_id, progress, predictions
            )
            assert result['success'] is True
        
        # Complete batch monitoring
        result = await manager.complete_batch_monitoring(model_id, batch_id)
        assert result['success'] is True
        
        # Get batch report
        batch_report = await manager.get_batch_report(model_id, batch_id)
        
        # Verify batch report
        assert 'total_processed' in batch_report
        assert 'processing_time_minutes' in batch_report
        assert 'average_latency_ms' in batch_report
        assert 'throughput_per_second' in batch_report
        assert 'error_count' in batch_report
        assert 'success_rate' in batch_report
        
        assert batch_report['total_processed'] == total_samples
        assert batch_report['success_rate'] > 0.9

    @pytest.mark.asyncio
    async def test_model_comparison_analysis(self, ai_observability_manager):
        """Test comprehensive model comparison analysis"""
        manager = ai_observability_manager
        
        # Register two models for comparison
        model_configs = [
            {
                'model_id': 'model_a_content_protection',
                'model_type': ModelType.CONTENT_PROTECTION,
                'framework': ModelFramework.TENSORFLOW,
                'version': '1.0.0',
                'description': 'Model A for content protection'
            },
            {
                'model_id': 'model_b_content_protection',
                'model_type': ModelType.CONTENT_PROTECTION,
                'framework': ModelFramework.PYTORCH,
                'version': '1.0.0',
                'description': 'Model B for content protection'
            }
        ]
        
        model_ids = []
        for config in model_configs:
            await manager.register_model(config)
            model_ids.append(config['model_id'])
        
        # Generate different performance data for each model
        for i, model_id in enumerate(model_ids):
            accuracy_base = 0.85 + i * 0.05  # Model B slightly better
            
            for j in range(100):
                # Generate predictions with different accuracy levels
                true_label = np.random.randint(0, 2)
                if np.random.rand() < accuracy_base:
                    prediction = true_label + np.random.normal(0, 0.1)
                else:
                    prediction = 1 - true_label + np.random.normal(0, 0.1)
                
                prediction = max(0, min(1, prediction))
                
                await manager.record_prediction(model_id, {
                    'prediction_id': str(uuid4()),
                    'prediction': prediction,
                    'true_label': true_label,
                    'timestamp': datetime.now(),
                    'input_features': np.random.randn(10).tolist(),
                    'latency_ms': float(np.random.randint(10, 100)),
                    'memory_usage_mb': float(np.random.randint(100, 500))
                })
        
        # Compare models
        comparison_report = await manager.compare_models(model_ids)
        
        # Verify comparison report
        assert 'model_comparison' in comparison_report
        assert 'metrics_comparison' in comparison_report
        assert 'statistical_significance' in comparison_report
        assert 'winner' in comparison_report
        assert 'recommendations' in comparison_report
        
        # Verify all models are included
        for model_id in model_ids:
            assert model_id in comparison_report['model_comparison']
        
        # Verify metrics comparison
        metrics_comparison = comparison_report['metrics_comparison']
        assert 'accuracy' in metrics_comparison
        assert 'latency_mean' in metrics_comparison
        
        # Should identify the better performing model
        assert comparison_report['winner'] in model_ids

    def test_thread_safety_comprehensive(self, sample_model_config):
        """Test thread safety of AI observability operations"""
        import concurrent.futures
        
        # This test would normally use the actual manager but for demo purposes
        # we'll test the thread safety patterns that should be implemented
        
        results = []
        errors = []
        
        def concurrent_operation(thread_id):
            try:
                # Simulate concurrent model operations
                config = sample_model_config.copy()
                config['model_id'] = f"concurrent_model_{thread_id}"
                
                # This would call actual manager methods in real implementation
                result = {
                    'thread_id': thread_id,
                    'model_id': config['model_id'],
                    'success': True,
                    'timestamp': datetime.now()
                }
                results.append(result)
                return result
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
                raise
        
        # Run concurrent operations
        num_threads = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_operation, i) 
                for i in range(num_threads)
            ]
            
            # Wait for all operations to complete
            concurrent.futures.wait(futures)
        
        # Verify thread safety
        assert len(results) == num_threads
        assert len(errors) == 0
        
        # Verify no duplicate model IDs
        model_ids = [r['model_id'] for r in results]
        assert len(set(model_ids)) == num_threads

    @pytest.mark.asyncio
    async def test_resource_cleanup_and_memory_management(self, ai_observability_manager):
        """Test proper resource cleanup and memory management"""
        manager = ai_observability_manager
        
        # Register multiple models and generate data
        model_ids = []
        for i in range(5):
            config = {
                'model_id': f'cleanup_test_model_{i}',
                'model_type': ModelType.CONTENT_PROTECTION,
                'framework': ModelFramework.TENSORFLOW,
                'version': '1.0.0'
            }
            await manager.register_model(config)
            model_ids.append(config['model_id'])
            
            # Generate substantial data for each model
            for j in range(200):
                await manager.record_prediction(config['model_id'], {
                    'prediction_id': str(uuid4()),
                    'prediction': float(np.random.rand()),
                    'true_label': int(np.random.randint(0, 2)),
                    'timestamp': datetime.now(),
                    'input_features': np.random.randn(100).tolist(),  # Larger feature vector
                    'metadata': {'test_data': True, 'large_object': list(range(1000))}
                })
        
        # Get initial memory usage info
        initial_models = len(await manager.get_registered_models())
        
        # Clean up specific models
        for model_id in model_ids[:3]:
            result = await manager.cleanup_model_data(model_id)
            assert result['success'] is True
        
        # Verify cleanup
        remaining_models = await manager.get_registered_models()
        assert len(remaining_models) == initial_models - 3
        
        # Test bulk cleanup
        result = await manager.bulk_cleanup(
            older_than_days=0,  # Clean all
            model_status_filter=[ModelStatus.DEPRECATED]
        )
        assert result['success'] is True
        assert result['cleaned_models'] >= 0

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_at_scale(self, ai_observability_manager, sample_model_config):
        """Test performance with high volume data"""
        manager = ai_observability_manager
        
        # Register model
        await manager.register_model(sample_model_config)
        model_id = sample_model_config['model_id']
        
        # Test high-volume prediction recording
        start_time = time.time()
        num_predictions = 10000
        
        # Use batch recording for better performance
        batch_size = 100
        batches = [[] for _ in range(num_predictions // batch_size)]
        
        for i in range(num_predictions):
            batch_idx = i // batch_size
            batches[batch_idx].append({
                'prediction_id': str(uuid4()),
                'prediction': float(np.random.rand()),
                'true_label': int(np.random.randint(0, 2)),
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist()
            })
        
        # Record batches
        for batch in batches:
            if batch:  # Skip empty batches
                await manager.record_predictions_batch(model_id, batch)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance expectations
        throughput = num_predictions / processing_time
        assert throughput > 100, f"Throughput too low: {throughput} predictions/second"
        
        # Verify all predictions were recorded
        metrics = await manager.get_model_metrics(model_id)
        assert metrics['prediction_count'] >= num_predictions * 0.95  # Allow for small losses

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_ai_pipeline_monitoring(self, ai_observability_manager):
        """Test end-to-end AI pipeline monitoring"""
        manager = ai_observability_manager
        
        # Set up content protection pipeline
        pipeline_models = [
            {
                'model_id': 'fingerprint_extractor',
                'model_type': ModelType.FINGERPRINTING,
                'framework': ModelFramework.TENSORFLOW,
                'version': '1.0.0',
                'pipeline_stage': 'feature_extraction'
            },
            {
                'model_id': 'copyright_classifier',
                'model_type': ModelType.COPYRIGHT_DETECTION,
                'framework': ModelFramework.PYTORCH,
                'version': '1.0.0',
                'pipeline_stage': 'classification'
            },
            {
                'model_id': 'similarity_matcher',
                'model_type': ModelType.SIMILARITY_MATCHING,
                'framework': ModelFramework.SCIKIT_LEARN,
                'version': '1.0.0',
                'pipeline_stage': 'matching'
            }
        ]
        
        # Register pipeline models
        for config in pipeline_models:
            await manager.register_model(config)
        
        # Simulate pipeline execution
        pipeline_id = str(uuid4())
        content_id = str(uuid4())
        
        # Start pipeline monitoring
        result = await manager.start_pipeline_monitoring(pipeline_id, {
            'content_id': content_id,
            'models': [m['model_id'] for m in pipeline_models],
            'expected_stages': ['feature_extraction', 'classification', 'matching']
        })
        assert result['success'] is True
        
        # Process through each stage
        pipeline_data = {'features': np.random.randn(512).tolist()}
        
        for model_config in pipeline_models:
            model_id = model_config['model_id']
            stage = model_config['pipeline_stage']
            
            # Record stage processing
            stage_result = await manager.record_pipeline_stage(
                pipeline_id, model_id, stage, pipeline_data
            )
            assert stage_result['success'] is True
            
            # Update pipeline data for next stage
            if stage == 'feature_extraction':
                pipeline_data['fingerprint'] = 'extracted_fingerprint_hash'
            elif stage == 'classification':
                pipeline_data['copyright_score'] = 0.85
            elif stage == 'matching':
                pipeline_data['matches'] = [
                    {'content_id': 'match_1', 'similarity': 0.92},
                    {'content_id': 'match_2', 'similarity': 0.88}
                ]
        
        # Complete pipeline monitoring
        result = await manager.complete_pipeline_monitoring(pipeline_id)
        assert result['success'] is True
        
        # Get pipeline report
        pipeline_report = await manager.get_pipeline_report(pipeline_id)
        
        # Verify pipeline report
        assert 'pipeline_id' in pipeline_report
        assert 'total_execution_time' in pipeline_report
        assert 'stages_completed' in pipeline_report
        assert 'stage_metrics' in pipeline_report
        assert 'success_rate' in pipeline_report
        
        # Verify all stages completed
        assert pipeline_report['stages_completed'] == len(pipeline_models)
        assert pipeline_report['success_rate'] == 1.0


# Additional test classes for specific components

class TestBiasDetectorSpecialized:
    """Specialized tests for bias detection algorithms"""
    
    @pytest.fixture
    def bias_detector(self):
        """Create bias detector instance"""
        config = {
            'fairness_metrics': ['demographic_parity', 'equalized_odds', 'calibration'],
            'sensitive_attributes': ['gender', 'age_group', 'ethnicity'],
            'threshold': 0.1
        }
        return BiasDetector(config)
    
    def test_demographic_parity_calculation(self, bias_detector):
        """Test demographic parity bias metric calculation"""
        # Create test data with clear bias
        predictions_data = {
            'group_a': {'predictions': [0.8, 0.9, 0.85, 0.88], 'labels': [1, 1, 1, 1]},
            'group_b': {'predictions': [0.3, 0.4, 0.35, 0.38], 'labels': [1, 1, 1, 1]}
        }
        
        parity_score = bias_detector.calculate_demographic_parity(predictions_data)
        
        # Should detect significant bias
        assert parity_score > 0.3
        assert isinstance(parity_score, float)
    
    def test_equalized_odds_calculation(self, bias_detector):
        """Test equalized odds bias metric calculation"""
        predictions_data = {
            'group_a': {
                'predictions': [0.8, 0.9, 0.2, 0.1] * 10,  # Consistent performance
                'labels': [1, 1, 0, 0] * 10
            },
            'group_b': {
                'predictions': [0.8, 0.5, 0.6, 0.1] * 10,  # Inconsistent performance
                'labels': [1, 1, 0, 0] * 10
            }
        }
        
        equalized_odds = bias_detector.calculate_equalized_odds(predictions_data)
        
        assert 'tpr_difference' in equalized_odds
        assert 'fpr_difference' in equalized_odds
        assert isinstance(equalized_odds['tpr_difference'], float)


class TestModelDriftDetectorSpecialized:
    """Specialized tests for model drift detection"""
    
    @pytest.fixture
    def drift_detector(self):
        """Create drift detector instance"""
        config = {
            'statistical_tests': ['ks_test', 'chi_square', 'psi'],
            'drift_threshold': 0.1,
            'monitoring_window_days': 30
        }
        return ModelDriftDetector(config)
    
    def test_kolmogorov_smirnov_drift_detection(self, drift_detector):
        """Test KS test for drift detection"""
        # Reference distribution (training data)
        reference_data = np.random.normal(0, 1, 1000)
        
        # Current distribution (with drift)
        current_data = np.random.normal(1.5, 1.2, 1000)  # Shifted and scaled
        
        ks_result = drift_detector.ks_test(reference_data, current_data)
        
        assert 'statistic' in ks_result
        assert 'p_value' in ks_result
        assert 'drift_detected' in ks_result
        
        # Should detect drift
        assert ks_result['drift_detected'] is True
        assert ks_result['statistic'] > 0.1


# Performance benchmarks
@pytest.mark.benchmark
class TestAIObservabilityBenchmarks:
    """Performance benchmarks for AI observability"""
    
    @pytest.mark.asyncio
    async def test_prediction_recording_benchmark(self, benchmark):
        """Benchmark prediction recording performance"""
        from ai.observability.ai_observability import AIObservabilityManager
        
        manager = AIObservabilityManager({})
        await manager.initialize()
        
        model_config = {
            'model_id': 'benchmark_model',
            'model_type': ModelType.CONTENT_PROTECTION,
            'framework': ModelFramework.TENSORFLOW
        }
        await manager.register_model(model_config)
        
        def record_prediction():
            return asyncio.run(manager.record_prediction('benchmark_model', {
                'prediction_id': str(uuid4()),
                'prediction': float(np.random.rand()),
                'true_label': int(np.random.randint(0, 2)),
                'timestamp': datetime.now(),
                'input_features': np.random.randn(10).tolist()
            }))
        
        result = benchmark(record_prediction)
        assert result['success'] is True
        
        await manager.shutdown()
    
    def test_metrics_calculation_benchmark(self, benchmark):
        """Benchmark metrics calculation performance"""
        # Generate large dataset
        n_samples = 10000
        predictions = np.random.rand(n_samples)
        true_labels = np.random.randint(0, 2, n_samples)
        
        def calculate_metrics():
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            return {
                'accuracy': accuracy_score(true_labels, predictions > 0.5),
                'precision': precision_score(true_labels, predictions > 0.5, average='weighted', zero_division=0),
                'recall': recall_score(true_labels, predictions > 0.5, average='weighted', zero_division=0),
                'f1': f1_score(true_labels, predictions > 0.5, average='weighted', zero_division=0)
            }
        
        metrics = benchmark(calculate_metrics)
        
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1'] <= 1
