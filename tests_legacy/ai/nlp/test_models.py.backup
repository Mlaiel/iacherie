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

"""Comprehensive Tests for NLP Models Module

Industrial-grade tests for AdvancedModelManager covering AI model management,
optimization, and deployment with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import Dict, List, Any, Optional
import logging

from ai.nlp.models import (
    AdvancedModelManager, SentimentAnalysisModel, TextClassificationModel,
    EmbeddingModel, ModelCacheManager, ModelPerformanceMonitor,
    ModelConfig, ModelInstance, ModelPrediction, ModelType, ModelStatus
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedModelManager:
    """Comprehensive tests for AdvancedModelManager"""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self, model_manager):
        """Test model manager initialization"""
        assert model_manager is not None
        assert hasattr(model_manager, 'config')
        assert hasattr(model_manager, 'model_trainer')
        assert hasattr(model_manager, 'model_optimizer')
        assert hasattr(model_manager, 'model_deployer')
        
        # Test configuration
        config = model_manager.config
        assert 'supported_models' in config
        assert 'model_repository' in config
        assert 'optimization_settings' in config

    @pytest.mark.asyncio
    async def test_model_loading_and_management(self, model_manager):
        """Test model loading and management"""
        # Test loading different types of models
        model_types = [
            'sentiment_analysis',
            'content_generation',
            'translation',
            'classification',
            'extraction'
        ]
        
        loaded_models = {}
        
        for model_type in model_types:
            model_result = await model_manager.load_model(
                model_type=model_type,
                model_name=f'advanced_{model_type}_model',
                options={
                    'cache_model': True,
                    'optimize_for_inference': True,
                    'validate_model': True
                }
            )
            
            assert model_result is not None
            assert 'model_id' in model_result
            assert 'model_info' in model_result
            assert 'loading_time' in model_result
            assert 'model_status' in model_result
            
            loaded_models[model_type] = model_result
            
            # Verify model loading
            model_info = model_result['model_info']
            assert 'model_type' in model_info
            assert 'model_size' in model_info
            assert 'performance_metrics' in model_info
            
            assert model_result['model_status'] == 'loaded'
        
        # Test model listing
        model_list = await model_manager.list_loaded_models(
            options={'include_metrics': True}
        )
        
        assert model_list is not None
        assert 'models' in model_list
        assert len(model_list['models']) == len(model_types)

    @pytest.mark.asyncio
    async def test_model_inference(self, model_manager):
        """Test model inference capabilities"""
        # Load a sentiment analysis model for testing
        sentiment_model = await model_manager.load_model(
            model_type='sentiment_analysis',
            model_name='advanced_sentiment_model'
        )
        
        model_id = sentiment_model['model_id']
        
        # Test inference with different inputs
        test_inputs = [
            {
                'text': "I absolutely love this amazing product!",
                'expected_sentiment': 'positive'
            },
            {
                'text': "This is terrible and I hate it.",
                'expected_sentiment': 'negative'
            },
            {
                'text': "The weather is okay today.",
                'expected_sentiment': 'neutral'
            }
        ]
        
        inference_results = []
        
        for test_input in test_inputs:
            inference_result = await model_manager.run_inference(
                model_id=model_id,
                input_data={
                    'text': test_input['text'],
                    'options': {
                        'confidence_scoring': True,
                        'detailed_output': True
                    }
                }
            )
            
            assert inference_result is not None
            assert 'output' in inference_result
            assert 'confidence' in inference_result
            assert 'processing_time' in inference_result
            
            inference_results.append(inference_result)
            
            # Verify inference quality
            output = inference_result['output']
            confidence = inference_result['confidence']
            
            assert isinstance(output, dict)
            assert 'sentiment' in output
            assert 0.0 <= confidence <= 1.0
            
            # Should have reasonable confidence
            assert confidence > 0.5

    @pytest.mark.asyncio
    async def test_batch_inference(self, model_manager, performance_test_data):
        """Test batch model inference"""
        # Load a classification model
        classification_model = await model_manager.load_model(
            model_type='classification',
            model_name='advanced_classification_model'
        )
        
        model_id = classification_model['model_id']
        
        # Prepare batch input
        batch_texts = performance_test_data['small_batch'][:10]
        batch_input = [{'text': text} for text in batch_texts]
        
        start_time = time.time()
        batch_result = await model_manager.run_batch_inference(
            model_id=model_id,
            batch_input=batch_input,
            options={
                'parallel_processing': True,
                'batch_optimization': True,
                'progress_tracking': True
            }
        )
        batch_time = time.time() - start_time
        
        assert batch_result is not None
        assert 'outputs' in batch_result
        assert 'batch_metrics' in batch_result
        assert 'processing_summary' in batch_result
        
        outputs = batch_result['outputs']
        batch_metrics = batch_result['batch_metrics']
        
        # Verify batch processing
        assert len(outputs) == len(batch_input)
        
        for output in outputs:
            assert 'classification' in output or 'result' in output
            assert 'confidence' in output
        
        # Should process efficiently
        throughput = len(batch_input) / batch_time
        assert throughput > 5.0  # Should process at least 5 items per second

    @pytest.mark.asyncio
    async def test_model_fine_tuning(self, model_manager):
        """Test model fine-tuning capabilities"""
        # Prepare training data for fine-tuning
        training_data = [
            {'text': 'AI content creation is revolutionary for marketing.', 'label': 'technology'},
            {'text': 'Social media engagement increases with personalized content.', 'label': 'marketing'},
            {'text': 'Machine learning algorithms improve content quality.', 'label': 'technology'},
            {'text': 'Influencer partnerships drive brand awareness.', 'label': 'marketing'},
            {'text': 'Natural language processing enables automated content generation.', 'label': 'technology'},
            {'text': 'Content strategy optimization requires data-driven insights.', 'label': 'marketing'},
            {'text': 'Deep learning models excel at sentiment analysis.', 'label': 'technology'},
            {'text': 'Brand storytelling connects with target audiences.', 'label': 'marketing'}
        ]
        
        validation_data = [
            {'text': 'AI transforms digital marketing strategies.', 'label': 'technology'},
            {'text': 'Customer engagement metrics guide content decisions.', 'label': 'marketing'}
        ]
        
        # Start fine-tuning
        fine_tuning_job = await model_manager.start_fine_tuning(
            base_model_type='classification',
            training_data=training_data,
            validation_data=validation_data,
            training_config={
                'learning_rate': 1e-5,
                'batch_size': 4,
                'epochs': 3,
                'early_stopping': True,
                'validation_split': 0.2
            },
            options={
                'save_checkpoints': True,
                'track_metrics': True,
                'optimize_memory': True
            }
        )
        
        assert fine_tuning_job is not None
        assert 'job_id' in fine_tuning_job
        assert 'training_config' in fine_tuning_job
        assert 'estimated_duration' in fine_tuning_job
        
        # Monitor training progress (simulated)
        training_progress = await model_manager.get_training_progress(
            job_id=fine_tuning_job['job_id'],
            options={'detailed_metrics': True}
        )
        
        assert training_progress is not None
        assert 'current_epoch' in training_progress
        assert 'training_metrics' in training_progress
        assert 'validation_metrics' in training_progress

    @pytest.mark.asyncio
    async def test_model_optimization(self, model_manager):
        """Test model optimization techniques"""
        # Load a model for optimization
        model_result = await model_manager.load_model(
            model_type='content_generation',
            model_name='base_generation_model'
        )
        
        model_id = model_result['model_id']
        
        # Test different optimization techniques
        optimization_techniques = [
            {
                'technique': 'quantization',
                'config': {
                    'precision': 'int8',
                    'calibration_data': 'sample_dataset'
                }
            },
            {
                'technique': 'pruning',
                'config': {
                    'sparsity_level': 0.3,
                    'structured_pruning': True
                }
            },
            {
                'technique': 'distillation',
                'config': {
                    'teacher_model': model_id,
                    'student_architecture': 'lightweight'
                }
            }
        ]
        
        optimization_results = []
        
        for technique in optimization_techniques:
            optimization_result = await model_manager.optimize_model(
                model_id=model_id,
                optimization_technique=technique['technique'],
                optimization_config=technique['config'],
                options={
                    'validate_performance': True,
                    'benchmark_comparison': True,
                    'save_optimized_model': True
                }
            )
            
            assert optimization_result is not None
            assert 'optimized_model_id' in optimization_result
            assert 'optimization_metrics' in optimization_result
            assert 'performance_comparison' in optimization_result
            
            optimization_results.append(optimization_result)
            
            # Verify optimization benefits
            metrics = optimization_result['optimization_metrics']
            comparison = optimization_result['performance_comparison']
            
            assert 'model_size_reduction' in metrics
            assert 'inference_speedup' in metrics
            assert 'accuracy_retention' in metrics
            
            # Should maintain reasonable accuracy
            if 'accuracy_retention' in metrics:
                assert metrics['accuracy_retention'] > 0.8  # At least 80% accuracy retention

    @pytest.mark.asyncio
    async def test_model_deployment(self, model_manager):
        """Test model deployment capabilities"""
        # Load and optimize a model for deployment
        model_result = await model_manager.load_model(
            model_type='sentiment_analysis',
            model_name='optimized_sentiment_model'
        )
        
        model_id = model_result['model_id']
        
        # Test different deployment configurations
        deployment_configs = [
            {
                'environment': 'production',
                'scaling': 'auto',
                'instance_type': 'cpu_optimized',
                'load_balancing': True
            },
            {
                'environment': 'staging',
                'scaling': 'manual',
                'instance_type': 'gpu_enabled',
                'load_balancing': False
            }
        ]
        
        deployment_results = []
        
        for config in deployment_configs:
            deployment_result = await model_manager.deploy_model(
                model_id=model_id,
                deployment_config=config,
                options={
                    'health_checks': True,
                    'monitoring': True,
                    'rollback_capability': True
                }
            )
            
            assert deployment_result is not None
            assert 'deployment_id' in deployment_result
            assert 'endpoint_url' in deployment_result
            assert 'deployment_status' in deployment_result
            assert 'health_check_url' in deployment_result
            
            deployment_results.append(deployment_result)
            
            # Verify deployment status
            assert deployment_result['deployment_status'] in ['deployed', 'deploying', 'ready']
        
        # Test deployment health check
        deployment_id = deployment_results[0]['deployment_id']
        health_check = await model_manager.check_deployment_health(
            deployment_id=deployment_id,
            options={'detailed_status': True}
        )
        
        assert health_check is not None
        assert 'status' in health_check
        assert 'response_time' in health_check
        assert 'throughput' in health_check

    @pytest.mark.asyncio
    async def test_model_versioning(self, model_manager):
        """Test model versioning and lifecycle management"""
        # Create multiple versions of a model
        model_versions = []
        
        for version in range(1, 4):
            model_result = await model_manager.create_model_version(
                base_model_type='classification',
                version_config={
                    'version_number': f'v1.{version}',
                    'description': f'Model version 1.{version} with improvements',
                    'changes': f'Performance optimization iteration {version}',
                    'training_data_version': f'dataset_v1.{version}'
                },
                options={
                    'auto_validation': True,
                    'performance_benchmarking': True,
                    'backward_compatibility': True
                }
            )
            
            assert model_result is not None
            assert 'model_version_id' in model_result
            assert 'version_info' in model_result
            assert 'validation_results' in model_result
            
            model_versions.append(model_result)
        
        # Test version comparison
        version_comparison = await model_manager.compare_model_versions(
            version_ids=[v['model_version_id'] for v in model_versions],
            comparison_metrics=['accuracy', 'latency', 'model_size'],
            options={'detailed_analysis': True}
        )
        
        assert version_comparison is not None
        assert 'comparison_matrix' in version_comparison
        assert 'best_version_recommendations' in version_comparison
        assert 'performance_trends' in version_comparison
        
        # Test version rollback
        rollback_result = await model_manager.rollback_model_version(
            current_version_id=model_versions[-1]['model_version_id'],
            target_version_id=model_versions[0]['model_version_id'],
            options={
                'validate_rollback': True,
                'gradual_rollout': True
            }
        )
        
        assert rollback_result is not None
        assert 'rollback_status' in rollback_result
        assert 'validation_passed' in rollback_result

    @pytest.mark.asyncio
    async def test_model_monitoring(self, model_manager):
        """Test model performance monitoring"""
        # Deploy a model for monitoring
        model_result = await model_manager.load_model(
            model_type='sentiment_analysis',
            model_name='production_sentiment_model'
        )
        
        deployment_result = await model_manager.deploy_model(
            model_id=model_result['model_id'],
            deployment_config={
                'environment': 'production',
                'monitoring_enabled': True
            }
        )
        
        deployment_id = deployment_result['deployment_id']
        
        # Set up monitoring
        monitoring_setup = await model_manager.setup_model_monitoring(
            deployment_id=deployment_id,
            monitoring_config={
                'performance_tracking': True,
                'data_drift_detection': True,
                'prediction_quality_monitoring': True,
                'alert_thresholds': {
                    'accuracy_drop': 0.1,
                    'latency_increase': 2.0,
                    'error_rate_spike': 5.0
                }
            }
        )
        
        assert monitoring_setup is not None
        assert 'monitoring_id' in monitoring_setup
        assert 'tracking_metrics' in monitoring_setup
        
        # Simulate inference data for monitoring
        inference_data = [
            {'input': 'Great product!', 'predicted': 'positive', 'actual': 'positive', 'confidence': 0.95},
            {'input': 'Terrible service', 'predicted': 'negative', 'actual': 'negative', 'confidence': 0.88},
            {'input': 'Average experience', 'predicted': 'neutral', 'actual': 'neutral', 'confidence': 0.72},
            {'input': 'Love it!', 'predicted': 'positive', 'actual': 'positive', 'confidence': 0.92}
        ]
        
        for data_point in inference_data:
            await model_manager.log_inference_data(
                monitoring_id=monitoring_setup['monitoring_id'],
                inference_data=data_point,
                timestamp=time.time()
            )
        
        # Get monitoring report
        monitoring_report = await model_manager.get_monitoring_report(
            monitoring_id=monitoring_setup['monitoring_id'],
            time_period='1h',
            options={'detailed_analysis': True}
        )
        
        assert monitoring_report is not None
        assert 'performance_metrics' in monitoring_report
        assert 'drift_analysis' in monitoring_report
        assert 'quality_trends' in monitoring_report

    @pytest.mark.asyncio
    async def test_multi_model_ensemble(self, model_manager):
        """Test multi-model ensemble capabilities"""
        # Load multiple models for ensemble
        model_types = ['sentiment_analysis', 'classification', 'content_generation']
        ensemble_models = []
        
        for model_type in model_types:
            model_result = await model_manager.load_model(
                model_type=model_type,
                model_name=f'ensemble_{model_type}_model'
            )
            ensemble_models.append(model_result['model_id'])
        
        # Create ensemble
        ensemble_result = await model_manager.create_ensemble(
            model_ids=ensemble_models,
            ensemble_config={
                'combination_strategy': 'weighted_voting',
                'weights': [0.4, 0.3, 0.3],
                'consensus_threshold': 0.7
            },
            options={
                'validate_ensemble': True,
                'optimize_weights': True
            }
        )
        
        assert ensemble_result is not None
        assert 'ensemble_id' in ensemble_result
        assert 'ensemble_metrics' in ensemble_result
        assert 'validation_results' in ensemble_result
        
        # Test ensemble inference
        test_input = {
            'text': 'This AI platform is incredibly powerful and user-friendly!',
            'options': {'detailed_output': True}
        }
        
        ensemble_inference = await model_manager.run_ensemble_inference(
            ensemble_id=ensemble_result['ensemble_id'],
            input_data=test_input
        )
        
        assert ensemble_inference is not None
        assert 'ensemble_output' in ensemble_inference
        assert 'individual_outputs' in ensemble_inference
        assert 'consensus_score' in ensemble_inference

    @pytest.mark.asyncio
    async def test_model_explainability(self, model_manager):
        """Test model explainability and interpretability"""
        # Load a model for explainability testing
        model_result = await model_manager.load_model(
            model_type='sentiment_analysis',
            model_name='explainable_sentiment_model'
        )
        
        model_id = model_result['model_id']
        
        # Test model explanations
        test_cases = [
            "I absolutely love this amazing product!",
            "This service is terrible and disappointing.",
            "The experience was okay, nothing special."
        ]
        
        for test_text in test_cases:
            explanation_result = await model_manager.explain_prediction(
                model_id=model_id,
                input_data={'text': test_text},
                explanation_methods=['attention', 'gradient', 'lime'],
                options={
                    'feature_importance': True,
                    'counterfactual_examples': True,
                    'visualization_data': True
                }
            )
            
            assert explanation_result is not None
            assert 'prediction' in explanation_result
            assert 'explanations' in explanation_result
            assert 'feature_importance' in explanation_result
            
            explanations = explanation_result['explanations']
            feature_importance = explanation_result['feature_importance']
            
            # Should have explanations for each method
            assert 'attention' in explanations
            assert 'gradient' in explanations
            assert 'lime' in explanations
            
            # Should identify important features
            assert isinstance(feature_importance, dict)
            assert len(feature_importance) > 0

    @pytest.mark.asyncio
    async def test_model_security(self, model_manager):
        """Test model security and robustness"""
        # Load a model for security testing
        model_result = await model_manager.load_model(
            model_type='classification',
            model_name='secure_classification_model'
        )
        
        model_id = model_result['model_id']
        
        # Test adversarial robustness
        adversarial_test = await model_manager.test_adversarial_robustness(
            model_id=model_id,
            test_inputs=[
                'This is a normal input for testing.',
                'This is a slightly modified input for testing!',
                'This input contains unusual characters: ñáéíóú'
            ],
            attack_methods=['fgsm', 'textfooler'],
            options={
                'robustness_threshold': 0.8,
                'generate_defenses': True
            }
        )
        
        assert adversarial_test is not None
        assert 'robustness_score' in adversarial_test
        assert 'vulnerability_analysis' in adversarial_test
        assert 'defense_recommendations' in adversarial_test
        
        # Test privacy compliance
        privacy_audit = await model_manager.audit_model_privacy(
            model_id=model_id,
            audit_config={
                'data_leakage_detection': True,
                'membership_inference_testing': True,
                'differential_privacy_assessment': True
            }
        )
        
        assert privacy_audit is not None
        assert 'privacy_score' in privacy_audit
        assert 'compliance_status' in privacy_audit
        assert 'recommendations' in privacy_audit

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, model_manager, benchmark_config):
        """Test model manager performance benchmarks"""
        # Load a model for benchmarking
        model_result = await model_manager.load_model(
            model_type='sentiment_analysis',
            model_name='benchmark_sentiment_model'
        )
        
        model_id = model_result['model_id']
        
        # Test single inference latency
        test_input = {'text': 'This is a performance test for model inference.'}
        
        start_time = time.time()
        inference_result = await model_manager.run_inference(
            model_id=model_id,
            input_data=test_input
        )
        inference_time = time.time() - start_time
        
        max_latency = benchmark_config.get('max_inference_latency', 1.0)
        assert inference_time < max_latency, f"Inference took {inference_time:.3f}s, max: {max_latency}s"
        
        # Test batch inference throughput
        batch_size = 20
        batch_input = [{'text': f'Batch test input {i}'} for i in range(batch_size)]
        
        start_time = time.time()
        batch_result = await model_manager.run_batch_inference(
            model_id=model_id,
            batch_input=batch_input
        )
        batch_time = time.time() - start_time
        
        throughput = batch_size / batch_time
        min_throughput = benchmark_config.get('min_inference_throughput', 10.0)
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, model_manager):
        """Test model manager error handling"""
        # Test loading non-existent model
        result = await model_manager.load_model(
            model_type='non_existent_type',
            model_name='non_existent_model',
            options={'handle_missing': True}
        )
        assert result is not None  # Should handle gracefully
        
        # Test inference with invalid model ID
        result = await model_manager.run_inference(
            model_id='invalid_model_id',
            input_data={'text': 'test'},
            options={'handle_invalid': True}
        )
        assert result is not None
        
        # Test deployment with invalid configuration
        result = await model_manager.deploy_model(
            model_id='invalid_model',
            deployment_config={'invalid': 'config'},
            options={'validate_config': True}
        )
        assert result is not None

class TestModelTrainer:
    """Test model trainer component"""
    
    @pytest.mark.asyncio
    async def test_model_trainer_initialization(self):
        """Test model trainer initialization"""
        trainer = ModelTrainer()
        assert trainer is not None
        assert hasattr(trainer, 'train_model')

class TestModelOptimizer:
    """Test model optimizer component"""
    
    @pytest.mark.asyncio
    async def test_model_optimizer_initialization(self):
        """Test model optimizer initialization"""
        optimizer = ModelOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_model')

class TestModelDeployer:
    """Test model deployer component"""
    
    @pytest.mark.asyncio
    async def test_model_deployer_initialization(self):
        """Test model deployer initialization"""
        deployer = ModelDeployer()
        assert deployer is not None
        assert hasattr(deployer, 'deploy_model')

class TestModelConfig:
    """Test model configuration"""
    
    def test_config_creation(self):
        """Test model configuration creation"""
        config = ModelConfig(
            supported_models=['sentiment', 'classification', 'generation'],
            model_repository='s3://models',
            optimization_settings={'quantization': True, 'pruning': True}
        )
        
        assert 'sentiment' in config.supported_models
        assert config.model_repository == 's3://models'
        assert config.optimization_settings['quantization'] is True
