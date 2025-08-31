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
Model Manager Tests - Enterprise Grade Test Suite

Comprehensive tests for ML model management, versioning, deployment,
monitoring, and governance systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import tensorflow as tf
import asyncio
import tempfile
import json
import pickle
import joblib
import onnx
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Tuple, Optional
import mlflow
from transformers import AutoModel, AutoTokenizer
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage

from ai.ml.model_manager import (
    ModelManager, ModelRegistry, ModelVersionController, ModelDeploymentManager,
    ModelMonitor, ModelGovernance, ModelSerializer, ModelValidator,
    ModelMetadataManager, ModelArtifactManager, ModelPerformanceTracker,
    ModelSecurityManager, ModelComplianceChecker, ModelOptimizer,
    ModelConverter, ModelEnsembleManager, ModelA/BTestManager,
    DistributedModelManager, EdgeModelManager, CloudModelManager,
    ModelLifecycleHooks, ModelHealthChecker, ModelRollbackManager
)


class TestModelManager:
    """Tests for core model management functionality"""
    
    def test_init_model_manager(self):
        """Test model manager initialization"""
        manager = ModelManager(
            registry_backend="mlflow",
            storage_backend="s3",
            deployment_targets=["kubernetes", "cloud_run", "edge"],
            enable_versioning=True,
            enable_monitoring=True,
            enable_governance=True
        )
        
        assert manager.registry_backend == "mlflow"
        assert manager.storage_backend == "s3"
        assert len(manager.deployment_targets) == 3
        assert manager.enable_versioning
        assert manager.enable_monitoring
        assert manager.enable_governance

    def test_model_registration(self, trained_model, model_metadata):
        """Test model registration process"""
        manager = ModelManager()
        
        registration_config = {
            "model_name": "content_classifier_v2",
            "model_version": "2.1.0",
            "framework": "pytorch",
            "task_type": "multiclass_classification",
            "description": "Advanced content classification model",
            "tags": ["nlp", "content", "classification", "production"]
        }
        
        with patch.object(manager, 'register_model') as mock_register:
            mock_register.return_value = {
                "model_id": "model_12345",
                "registry_uri": "s3://models/content_classifier_v2/2.1.0/",
                "registration_timestamp": datetime.now().isoformat(),
                "model_signature": {
                    "inputs": [{"name": "text", "type": "string", "shape": [-1]}],
                    "outputs": [{"name": "predictions", "type": "tensor", "shape": [-1, 10]}]
                },
                "model_size_mb": 245.6,
                "status": "registered"
            }
            
            registration_result = manager.register_model(
                model=trained_model,
                metadata=registration_config
            )
            
            assert "model_id" in registration_result
            assert "registry_uri" in registration_result
            assert "model_signature" in registration_result
            assert registration_result["status"] == "registered"

    def test_model_loading_pytorch(self, temp_dir):
        """Test PyTorch model loading"""
        manager = ModelManager()
        
        # Create mock PyTorch model
        model_path = temp_dir / "pytorch_model.pth"
        mock_model_state = {"layer.weight": torch.randn(10, 5), "layer.bias": torch.randn(10)}
        torch.save(mock_model_state, model_path)
        
        with patch.object(manager, 'load_pytorch_model') as mock_load:
            mock_load.return_value = {
                "model": Mock(spec=torch.nn.Module),
                "model_config": {"architecture": "transformer", "layers": 12},
                "loading_time": 2.3,
                "memory_usage_mb": 156.7
            }
            
            loaded_model = manager.load_pytorch_model(model_path)
            
            assert "model" in loaded_model
            assert "model_config" in loaded_model
            assert "loading_time" in loaded_model

    def test_model_loading_tensorflow(self, temp_dir):
        """Test TensorFlow model loading"""
        manager = ModelManager()
        
        # Create mock TensorFlow model directory
        model_dir = temp_dir / "tensorflow_model"
        model_dir.mkdir()
        (model_dir / "saved_model.pb").touch()
        
        with patch('tensorflow.keras.models.load_model') as mock_tf_load:
            mock_tf_load.return_value = Mock(spec=tf.keras.Model)
            
            loaded_model = manager.load_tensorflow_model(str(model_dir))
            
            assert loaded_model is not None
            mock_tf_load.assert_called_once_with(str(model_dir))

    def test_model_loading_huggingface(self):
        """Test Hugging Face model loading"""
        manager = ModelManager()
        
        model_name = "bert-base-uncased"
        
        with patch('transformers.AutoModel.from_pretrained') as mock_model, \
             patch('transformers.AutoTokenizer.from_pretrained') as mock_tokenizer:
            
            mock_model.return_value = Mock()
            mock_tokenizer.return_value = Mock()
            
            loaded_components = manager.load_huggingface_model(model_name)
            
            assert "model" in loaded_components
            assert "tokenizer" in loaded_components
            mock_model.assert_called_once_with(model_name)
            mock_tokenizer.assert_called_once_with(model_name)

    def test_model_serialization_formats(self, trained_model, temp_dir):
        """Test model serialization in different formats"""
        manager = ModelManager()
        
        serialization_formats = ["pickle", "joblib", "onnx", "torchscript"]
        
        for fmt in serialization_formats:
            output_path = temp_dir / f"model.{fmt}"
            
            with patch.object(manager, f'serialize_model_{fmt}') as mock_serialize:
                mock_serialize.return_value = {
                    "serialized_path": str(output_path),
                    "format": fmt,
                    "file_size_mb": 123.4,
                    "serialization_time": 5.2
                }
                
                serialization_result = manager.serialize_model(
                    model=trained_model,
                    format=fmt,
                    output_path=output_path
                )
                
                assert "serialized_path" in serialization_result
                assert serialization_result["format"] == fmt

    def test_model_validation(self, trained_model, validation_dataset):
        """Test model validation process"""
        manager = ModelManager()
        
        validation_config = {
            "validation_metrics": ["accuracy", "precision", "recall", "f1_score"],
            "validation_dataset": validation_dataset,
            "batch_size": 32,
            "enable_error_analysis": True
        }
        
        with patch.object(manager, 'validate_model') as mock_validate:
            mock_validate.return_value = {
                "validation_results": {
                    "accuracy": 0.94,
                    "precision": 0.92,
                    "recall": 0.93,
                    "f1_score": 0.92
                },
                "validation_time": 45.6,
                "sample_predictions": [
                    {"input": "sample text", "predicted": "class_A", "confidence": 0.89},
                    {"input": "another sample", "predicted": "class_B", "confidence": 0.76}
                ],
                "error_analysis": {
                    "misclassified_count": 12,
                    "common_errors": ["class_A_as_class_B", "class_C_as_class_A"],
                    "confidence_distribution": {"high": 180, "medium": 15, "low": 5}
                },
                "validation_status": "passed"
            }
            
            validation_result = manager.validate_model(
                model=trained_model,
                config=validation_config
            )
            
            assert "validation_results" in validation_result
            assert "error_analysis" in validation_result
            assert validation_result["validation_status"] == "passed"

    def test_model_optimization(self, trained_model):
        """Test model optimization techniques"""
        manager = ModelManager()
        
        optimization_config = {
            "techniques": ["quantization", "pruning", "knowledge_distillation"],
            "target_metrics": {"size_reduction": 0.5, "speed_improvement": 2.0},
            "quality_threshold": 0.9  # Maintain 90% of original quality
        }
        
        with patch.object(manager, 'optimize_model') as mock_optimize:
            mock_optimize.return_value = {
                "optimized_model": Mock(),
                "optimization_results": {
                    "original_size_mb": 245.6,
                    "optimized_size_mb": 122.8,
                    "size_reduction_ratio": 0.5,
                    "original_latency_ms": 45.2,
                    "optimized_latency_ms": 22.6,
                    "speed_improvement": 2.0,
                    "quality_retention": 0.94
                },
                "applied_techniques": ["quantization", "pruning"],
                "optimization_time": 1200  # seconds
            }
            
            optimization_result = manager.optimize_model(
                model=trained_model,
                config=optimization_config
            )
            
            assert "optimized_model" in optimization_result
            assert "optimization_results" in optimization_result
            assert optimization_result["optimization_results"]["quality_retention"] >= 0.9

    def test_model_conversion_onnx(self, trained_pytorch_model, temp_dir):
        """Test model conversion to ONNX format"""
        manager = ModelManager()
        
        conversion_config = {
            "input_shape": (1, 3, 224, 224),
            "input_names": ["input"],
            "output_names": ["output"],
            "dynamic_axes": {"input": {0: "batch_size"}, "output": {0: "batch_size"}},
            "opset_version": 11
        }
        
        onnx_path = temp_dir / "model.onnx"
        
        with patch('torch.onnx.export') as mock_export:
            mock_export.return_value = None
            
            with patch.object(manager, 'convert_to_onnx') as mock_convert:
                mock_convert.return_value = {
                    "onnx_path": str(onnx_path),
                    "conversion_success": True,
                    "onnx_model_size_mb": 89.3,
                    "input_shapes": {"input": [1, 3, 224, 224]},
                    "output_shapes": {"output": [1, 1000]},
                    "opset_version": 11
                }
                
                conversion_result = manager.convert_to_onnx(
                    model=trained_pytorch_model,
                    config=conversion_config,
                    output_path=onnx_path
                )
                
                assert "onnx_path" in conversion_result
                assert conversion_result["conversion_success"] is True


class TestModelRegistry:
    """Tests for model registry functionality"""
    
    def test_init_model_registry(self):
        """Test model registry initialization"""
        registry = ModelRegistry(
            backend="mlflow",
            tracking_uri="http://mlflow:5000",
            default_experiment="model_experiments",
            enable_model_staging=True
        )
        
        assert registry.backend == "mlflow"
        assert registry.tracking_uri == "http://mlflow:5000"
        assert registry.enable_model_staging

    def test_model_search_and_discovery(self):
        """Test model search and discovery functionality"""
        registry = ModelRegistry()
        
        search_criteria = {
            "model_name": "content_classifier*",
            "tags": ["production", "nlp"],
            "framework": "pytorch",
            "min_accuracy": 0.9,
            "created_after": "2024-01-01",
            "stage": ["staging", "production"]
        }
        
        with patch.object(registry, 'search_models') as mock_search:
            mock_search.return_value = {
                "models": [
                    {
                        "model_id": "model_001",
                        "model_name": "content_classifier_v1",
                        "version": "1.2.3",
                        "stage": "production",
                        "accuracy": 0.94,
                        "tags": ["production", "nlp", "pytorch"]
                    },
                    {
                        "model_id": "model_002",
                        "model_name": "content_classifier_v2",
                        "version": "2.0.1",
                        "stage": "staging",
                        "accuracy": 0.96,
                        "tags": ["staging", "nlp", "pytorch"]
                    }
                ],
                "total_count": 2,
                "search_time": 0.234
            }
            
            search_results = registry.search_models(search_criteria)
            
            assert "models" in search_results
            assert len(search_results["models"]) == 2
            assert all(model["accuracy"] >= 0.9 for model in search_results["models"])

    def test_model_lineage_tracking(self):
        """Test model lineage tracking"""
        registry = ModelRegistry()
        
        lineage_info = {
            "model_id": "model_123",
            "parent_models": ["model_100", "model_110"],
            "training_dataset": {
                "dataset_id": "dataset_456",
                "version": "v2.1",
                "hash": "sha256:abc123..."
            },
            "code_version": {
                "repository": "https://github.com/company/ml-models",
                "commit_hash": "def456...",
                "branch": "main"
            },
            "experiment_id": "exp_789",
            "training_config": {
                "algorithm": "transformer",
                "hyperparameters": {"learning_rate": 0.001, "epochs": 10}
            }
        }
        
        with patch.object(registry, 'track_model_lineage') as mock_lineage:
            mock_lineage.return_value = {
                "lineage_id": "lineage_999",
                "lineage_graph": {
                    "nodes": [
                        {"id": "model_123", "type": "model"},
                        {"id": "dataset_456", "type": "dataset"},
                        {"id": "exp_789", "type": "experiment"}
                    ],
                    "edges": [
                        {"from": "dataset_456", "to": "model_123", "type": "trained_on"},
                        {"from": "exp_789", "to": "model_123", "type": "produced_by"}
                    ]
                },
                "provenance_score": 0.95
            }
            
            lineage_result = registry.track_model_lineage(lineage_info)
            
            assert "lineage_id" in lineage_result
            assert "lineage_graph" in lineage_result
            assert "provenance_score" in lineage_result

    def test_model_staging_workflow(self):
        """Test model staging workflow"""
        registry = ModelRegistry(enable_model_staging=True)
        
        staging_config = {
            "model_id": "model_123",
            "current_stage": "None",
            "target_stage": "staging",
            "approval_required": True,
            "quality_gates": {
                "min_accuracy": 0.9,
                "max_latency_ms": 100,
                "security_scan": True
            }
        }
        
        with patch.object(registry, 'transition_model_stage') as mock_transition:
            mock_transition.return_value = {
                "transition_id": "trans_456",
                "model_id": "model_123",
                "previous_stage": "None",
                "current_stage": "staging",
                "quality_gate_results": {
                    "accuracy_check": {"passed": True, "value": 0.94},
                    "latency_check": {"passed": True, "value": 85},
                    "security_scan": {"passed": True, "issues": 0}
                },
                "approval_status": "pending",
                "transition_timestamp": datetime.now().isoformat()
            }
            
            transition_result = registry.transition_model_stage(staging_config)
            
            assert "transition_id" in transition_result
            assert transition_result["current_stage"] == "staging"
            assert "quality_gate_results" in transition_result

    def test_model_comparison(self):
        """Test model comparison functionality"""
        registry = ModelRegistry()
        
        comparison_config = {
            "model_ids": ["model_123", "model_124", "model_125"],
            "comparison_metrics": ["accuracy", "precision", "recall", "latency", "model_size"],
            "test_dataset_id": "dataset_test_001"
        }
        
        with patch.object(registry, 'compare_models') as mock_compare:
            mock_compare.return_value = {
                "comparison_id": "comp_789",
                "model_comparisons": [
                    {
                        "model_id": "model_123",
                        "model_name": "classifier_v1",
                        "metrics": {
                            "accuracy": 0.92,
                            "precision": 0.90,
                            "recall": 0.91,
                            "latency": 45,
                            "model_size": 123.4
                        }
                    },
                    {
                        "model_id": "model_124",
                        "model_name": "classifier_v2",
                        "metrics": {
                            "accuracy": 0.94,
                            "precision": 0.93,
                            "recall": 0.92,
                            "latency": 52,
                            "model_size": 145.6
                        }
                    }
                ],
                "winner": {
                    "model_id": "model_124",
                    "winning_criteria": "highest_accuracy",
                    "confidence": 0.87
                },
                "comparison_report": "model_124 shows 2% improvement in accuracy"
            }
            
            comparison_result = registry.compare_models(comparison_config)
            
            assert "comparison_id" in comparison_result
            assert "model_comparisons" in comparison_result
            assert "winner" in comparison_result


class TestModelVersionController:
    """Tests for model version control functionality"""
    
    def test_init_version_controller(self):
        """Test version controller initialization"""
        controller = ModelVersionController(
            versioning_backend="git",
            enable_semantic_versioning=True,
            auto_increment_policy="patch",
            enable_branching=True
        )
        
        assert controller.versioning_backend == "git"
        assert controller.enable_semantic_versioning
        assert controller.auto_increment_policy == "patch"

    def test_semantic_versioning(self):
        """Test semantic versioning functionality"""
        controller = ModelVersionController(enable_semantic_versioning=True)
        
        version_operations = [
            {"current": "1.0.0", "change_type": "patch", "expected": "1.0.1"},
            {"current": "1.0.1", "change_type": "minor", "expected": "1.1.0"},
            {"current": "1.1.0", "change_type": "major", "expected": "2.0.0"},
            {"current": "2.0.0", "change_type": "prerelease", "expected": "2.0.1-alpha.1"}
        ]
        
        for op in version_operations:
            new_version = controller.increment_version(
                current_version=op["current"],
                change_type=op["change_type"]
            )
            assert new_version == op["expected"]

    def test_model_branching(self):
        """Test model branching functionality"""
        controller = ModelVersionController(enable_branching=True)
        
        branching_config = {
            "base_model_id": "model_123",
            "base_version": "1.2.0",
            "branch_name": "experimental_features",
            "branch_description": "Testing new attention mechanism",
            "branching_point": "commit_abc123"
        }
        
        with patch.object(controller, 'create_model_branch') as mock_branch:
            mock_branch.return_value = {
                "branch_id": "branch_456",
                "branch_name": "experimental_features",
                "base_model_id": "model_123",
                "branch_model_id": "model_123_branch_456",
                "branching_timestamp": datetime.now().isoformat(),
                "branch_status": "active"
            }
            
            branch_result = controller.create_model_branch(branching_config)
            
            assert "branch_id" in branch_result
            assert "branch_model_id" in branch_result
            assert branch_result["branch_name"] == "experimental_features"

    def test_model_merging(self):
        """Test model merging functionality"""
        controller = ModelVersionController()
        
        merge_config = {
            "source_branch_id": "branch_456",
            "target_branch": "main",
            "merge_strategy": "model_ensemble",
            "conflict_resolution": "automated",
            "merge_message": "Merge experimental features with 3% accuracy improvement"
        }
        
        with patch.object(controller, 'merge_model_branches') as mock_merge:
            mock_merge.return_value = {
                "merge_id": "merge_789",
                "merged_model_id": "model_130",
                "merge_strategy": "model_ensemble",
                "merge_results": {
                    "performance_improvement": 0.03,
                    "model_size_change": 0.15,
                    "conflicts_resolved": 0
                },
                "merge_timestamp": datetime.now().isoformat(),
                "merge_status": "completed"
            }
            
            merge_result = controller.merge_model_branches(merge_config)
            
            assert "merge_id" in merge_result
            assert "merged_model_id" in merge_result
            assert merge_result["merge_status"] == "completed"

    def test_version_rollback(self):
        """Test version rollback functionality"""
        controller = ModelVersionController()
        
        rollback_config = {
            "model_id": "model_123",
            "current_version": "2.1.0",
            "target_version": "1.8.0",
            "rollback_reason": "performance_regression",
            "preserve_artifacts": True
        }
        
        with patch.object(controller, 'rollback_model_version') as mock_rollback:
            mock_rollback.return_value = {
                "rollback_id": "rollback_101",
                "model_id": "model_123",
                "previous_version": "2.1.0",
                "current_version": "1.8.0",
                "rollback_timestamp": datetime.now().isoformat(),
                "artifacts_preserved": True,
                "rollback_status": "completed"
            }
            
            rollback_result = controller.rollback_model_version(rollback_config)
            
            assert "rollback_id" in rollback_result
            assert rollback_result["current_version"] == "1.8.0"
            assert rollback_result["rollback_status"] == "completed"


class TestModelDeploymentManager:
    """Tests for model deployment management"""
    
    def test_init_deployment_manager(self):
        """Test deployment manager initialization"""
        manager = ModelDeploymentManager(
            deployment_targets=["kubernetes", "cloud_run", "lambda", "edge"],
            default_scaling_policy="auto",
            enable_blue_green_deployment=True,
            enable_canary_deployment=True
        )
        
        assert len(manager.deployment_targets) == 4
        assert manager.default_scaling_policy == "auto"
        assert manager.enable_blue_green_deployment
        assert manager.enable_canary_deployment

    def test_kubernetes_deployment(self, trained_model):
        """Test Kubernetes deployment"""
        manager = ModelDeploymentManager()
        
        k8s_config = {
            "model_id": "model_123",
            "deployment_name": "content-classifier-v2",
            "namespace": "ml-models",
            "replicas": 3,
            "resources": {
                "requests": {"cpu": "100m", "memory": "256Mi"},
                "limits": {"cpu": "500m", "memory": "1Gi"}
            },
            "service_type": "LoadBalancer",
            "health_check": {
                "path": "/health",
                "port": 8080,
                "initial_delay": 30
            }
        }
        
        with patch('kubernetes.client.AppsV1Api') as mock_k8s:
            mock_deployment = Mock()
            mock_k8s.return_value.create_namespaced_deployment.return_value = mock_deployment
            
            with patch.object(manager, 'deploy_to_kubernetes') as mock_deploy:
                mock_deploy.return_value = {
                    "deployment_id": "deploy_k8s_456",
                    "deployment_name": "content-classifier-v2",
                    "namespace": "ml-models",
                    "service_endpoint": "http://content-classifier-v2.ml-models.svc.cluster.local:8080",
                    "external_endpoint": "http://34.123.45.67:8080",
                    "deployment_status": "running",
                    "replicas": {"desired": 3, "available": 3, "ready": 3}
                }
                
                deployment_result = manager.deploy_to_kubernetes(k8s_config)
                
                assert "deployment_id" in deployment_result
                assert "service_endpoint" in deployment_result
                assert deployment_result["deployment_status"] == "running"

    def test_cloud_run_deployment(self, trained_model):
        """Test Google Cloud Run deployment"""
        manager = ModelDeploymentManager()
        
        cloud_run_config = {
            "model_id": "model_123",
            "service_name": "content-classifier-v2",
            "region": "us-central1",
            "memory": "2Gi",
            "cpu": "2",
            "max_instances": 10,
            "min_instances": 1,
            "container_image": "gcr.io/project/content-classifier:v2.1.0"
        }
        
        with patch.object(manager, 'deploy_to_cloud_run') as mock_deploy:
            mock_deploy.return_value = {
                "deployment_id": "deploy_cr_789",
                "service_name": "content-classifier-v2",
                "service_url": "https://content-classifier-v2-abcd1234-uc.a.run.app",
                "region": "us-central1",
                "deployment_status": "ready",
                "traffic_allocation": {"latest": 100}
            }
            
            deployment_result = manager.deploy_to_cloud_run(cloud_run_config)
            
            assert "service_url" in deployment_result
            assert deployment_result["deployment_status"] == "ready"

    def test_blue_green_deployment(self, trained_model):
        """Test blue-green deployment strategy"""
        manager = ModelDeploymentManager(enable_blue_green_deployment=True)
        
        blue_green_config = {
            "model_id": "model_124",
            "blue_deployment": "content-classifier-blue",
            "green_deployment": "content-classifier-green",
            "traffic_split_strategy": "gradual",
            "validation_criteria": {
                "min_success_rate": 0.99,
                "max_latency_p95": 200,
                "monitoring_duration": "10m"
            }
        }
        
        with patch.object(manager, 'deploy_blue_green') as mock_bg_deploy:
            mock_bg_deploy.return_value = {
                "deployment_id": "deploy_bg_999",
                "blue_endpoint": "https://content-classifier-blue.example.com",
                "green_endpoint": "https://content-classifier-green.example.com",
                "current_traffic": {"blue": 100, "green": 0},
                "deployment_phase": "green_validation",
                "switch_scheduled": "2024-12-25T15:30:00Z"
            }
            
            bg_result = manager.deploy_blue_green(blue_green_config)
            
            assert "blue_endpoint" in bg_result
            assert "green_endpoint" in bg_result
            assert "current_traffic" in bg_result

    def test_canary_deployment(self, trained_model):
        """Test canary deployment strategy"""
        manager = ModelDeploymentManager(enable_canary_deployment=True)
        
        canary_config = {
            "model_id": "model_125",
            "stable_version": "v1.8.0",
            "canary_version": "v2.0.0",
            "canary_traffic_percentage": 10,
            "success_criteria": {
                "error_rate_threshold": 0.01,
                "latency_threshold": 150,
                "business_metric_threshold": 0.95
            },
            "rollback_policy": {
                "auto_rollback": True,
                "rollback_threshold": 0.02
            }
        }
        
        with patch.object(manager, 'deploy_canary') as mock_canary:
            mock_canary.return_value = {
                "deployment_id": "deploy_canary_111",
                "stable_endpoint": "https://api.example.com/v1/predict",
                "canary_endpoint": "https://api-canary.example.com/v1/predict",
                "traffic_split": {"stable": 90, "canary": 10},
                "canary_metrics": {
                    "error_rate": 0.005,
                    "avg_latency": 120,
                    "business_metric": 0.97
                },
                "canary_status": "healthy"
            }
            
            canary_result = manager.deploy_canary(canary_config)
            
            assert "stable_endpoint" in canary_result
            assert "canary_endpoint" in canary_result
            assert canary_result["canary_status"] == "healthy"

    def test_deployment_rollback(self):
        """Test deployment rollback functionality"""
        manager = ModelDeploymentManager()
        
        rollback_config = {
            "deployment_id": "deploy_k8s_456",
            "target_version": "v1.8.0",
            "rollback_reason": "high_error_rate",
            "rollback_strategy": "immediate"
        }
        
        with patch.object(manager, 'rollback_deployment') as mock_rollback:
            mock_rollback.return_value = {
                "rollback_id": "rollback_222",
                "deployment_id": "deploy_k8s_456",
                "previous_version": "v2.0.0",
                "current_version": "v1.8.0",
                "rollback_duration": "2m 30s",
                "rollback_status": "completed"
            }
            
            rollback_result = manager.rollback_deployment(rollback_config)
            
            assert "rollback_id" in rollback_result
            assert rollback_result["current_version"] == "v1.8.0"
            assert rollback_result["rollback_status"] == "completed"


class TestModelMonitor:
    """Tests for model monitoring functionality"""
    
    def test_init_model_monitor(self):
        """Test model monitor initialization"""
        monitor = ModelMonitor(
            monitoring_backend="prometheus",
            alert_channels=["slack", "email", "pagerduty"],
            metrics_retention_days=90,
            enable_drift_detection=True,
            enable_bias_monitoring=True
        )
        
        assert monitor.monitoring_backend == "prometheus"
        assert len(monitor.alert_channels) == 3
        assert monitor.enable_drift_detection
        assert monitor.enable_bias_monitoring

    def test_performance_monitoring(self):
        """Test model performance monitoring"""
        monitor = ModelMonitor()
        
        performance_config = {
            "model_id": "model_123",
            "metrics": ["latency", "throughput", "error_rate", "cpu_usage", "memory_usage"],
            "monitoring_interval": "1m",
            "alert_thresholds": {
                "latency_p95": 200,
                "error_rate": 0.01,
                "cpu_usage": 80,
                "memory_usage": 85
            }
        }
        
        with patch.object(monitor, 'collect_performance_metrics') as mock_collect:
            mock_collect.return_value = {
                "timestamp": datetime.now().isoformat(),
                "model_id": "model_123",
                "metrics": {
                    "latency_p50": 45,
                    "latency_p95": 89,
                    "latency_p99": 156,
                    "throughput_rps": 150,
                    "error_rate": 0.003,
                    "cpu_usage": 65,
                    "memory_usage": 70
                },
                "alert_status": "healthy"
            }
            
            metrics = monitor.collect_performance_metrics(performance_config)
            
            assert "metrics" in metrics
            assert "alert_status" in metrics
            assert metrics["metrics"]["error_rate"] < 0.01

    def test_data_drift_detection(self, production_data, training_data):
        """Test data drift detection"""
        monitor = ModelMonitor(enable_drift_detection=True)
        
        drift_config = {
            "model_id": "model_123",
            "reference_data": training_data,
            "current_data": production_data,
            "drift_methods": ["ks_test", "chi2_test", "psi"],
            "drift_threshold": 0.1
        }
        
        with patch.object(monitor, 'detect_data_drift') as mock_drift:
            mock_drift.return_value = {
                "drift_detected": True,
                "drift_score": 0.15,
                "drift_features": [
                    {"feature": "age", "drift_score": 0.2, "method": "ks_test"},
                    {"feature": "income", "drift_score": 0.12, "method": "ks_test"},
                    {"feature": "category", "drift_score": 0.08, "method": "chi2_test"}
                ],
                "drift_summary": "Significant drift detected in 2 out of 10 features",
                "recommendation": "Consider model retraining"
            }
            
            drift_result = monitor.detect_data_drift(drift_config)
            
            assert "drift_detected" in drift_result
            assert drift_result["drift_detected"] is True
            assert "drift_features" in drift_result

    def test_model_bias_monitoring(self, model_predictions, sensitive_attributes):
        """Test model bias monitoring"""
        monitor = ModelMonitor(enable_bias_monitoring=True)
        
        bias_config = {
            "model_id": "model_123",
            "predictions": model_predictions,
            "sensitive_attributes": sensitive_attributes,
            "fairness_metrics": ["demographic_parity", "equalized_odds", "disparate_impact"],
            "bias_thresholds": {
                "demographic_parity": 0.1,
                "equalized_odds": 0.1,
                "disparate_impact": 0.8
            }
        }
        
        with patch.object(monitor, 'monitor_model_bias') as mock_bias:
            mock_bias.return_value = {
                "bias_detected": False,
                "fairness_metrics": {
                    "demographic_parity": 0.05,
                    "equalized_odds": 0.08,
                    "disparate_impact": 0.92
                },
                "group_metrics": {
                    "group_a": {"accuracy": 0.94, "precision": 0.92, "recall": 0.93},
                    "group_b": {"accuracy": 0.91, "precision": 0.89, "recall": 0.92}
                },
                "bias_report": "Model shows fair performance across demographic groups",
                "compliance_status": "compliant"
            }
            
            bias_result = monitor.monitor_model_bias(bias_config)
            
            assert "bias_detected" in bias_result
            assert "fairness_metrics" in bias_result
            assert bias_result["compliance_status"] == "compliant"

    def test_alert_generation(self):
        """Test alert generation system"""
        monitor = ModelMonitor(alert_channels=["slack", "email"])
        
        alert_config = {
            "alert_type": "performance_degradation",
            "severity": "high",
            "model_id": "model_123",
            "metric": "accuracy",
            "current_value": 0.85,
            "threshold": 0.9,
            "time_window": "1h"
        }
        
        with patch.object(monitor, 'generate_alert') as mock_alert:
            mock_alert.return_value = {
                "alert_id": "alert_999",
                "alert_type": "performance_degradation",
                "severity": "high",
                "message": "Model accuracy dropped to 85% (below 90% threshold)",
                "channels_notified": ["slack", "email"],
                "alert_timestamp": datetime.now().isoformat(),
                "alert_status": "sent"
            }
            
            alert_result = monitor.generate_alert(alert_config)
            
            assert "alert_id" in alert_result
            assert "channels_notified" in alert_result
            assert alert_result["alert_status"] == "sent"


@pytest.mark.integration
class TestModelManagerIntegration:
    """Integration tests for model management systems"""
    
    @pytest.mark.slow
    def test_end_to_end_model_lifecycle(self, trained_model, temp_dir):
        """Test complete model lifecycle management"""
        # Initialize components
        manager = ModelManager(enable_versioning=True, enable_monitoring=True)
        registry = ModelRegistry()
        deployment_manager = ModelDeploymentManager()
        monitor = ModelMonitor()
        
        # Register model
        with patch.object(registry, 'register_model') as mock_register:
            mock_register.return_value = {
                "model_id": "model_integration_001",
                "registry_uri": "s3://models/integration_test/1.0.0/"
            }
            
            registration_result = registry.register_model(trained_model)
            assert "model_id" in registration_result
        
        # Deploy model
        with patch.object(deployment_manager, 'deploy_to_kubernetes') as mock_deploy:
            mock_deploy.return_value = {
                "deployment_id": "deploy_integration_001",
                "service_endpoint": "http://test-model:8080"
            }
            
            deployment_result = deployment_manager.deploy_to_kubernetes({
                "model_id": registration_result["model_id"]
            })
            assert "deployment_id" in deployment_result
        
        # Monitor model
        with patch.object(monitor, 'collect_performance_metrics') as mock_monitor:
            mock_monitor.return_value = {
                "metrics": {"latency": 45, "error_rate": 0.01},
                "alert_status": "healthy"
            }
            
            monitoring_result = monitor.collect_performance_metrics({
                "model_id": registration_result["model_id"]
            })
            assert monitoring_result["alert_status"] == "healthy"

    def test_multi_cloud_deployment(self, trained_model):
        """Test multi-cloud deployment integration"""
        cloud_manager = CloudModelManager(
            cloud_providers=["aws", "gcp", "azure"]
        )
        
        multi_cloud_config = {
            "model_id": "model_123",
            "deployment_strategy": "multi_region",
            "aws_config": {"region": "us-east-1", "instance_type": "ml.m5.large"},
            "gcp_config": {"region": "us-central1", "machine_type": "n1-standard-2"},
            "azure_config": {"region": "eastus", "vm_size": "Standard_DS2_v2"}
        }
        
        with patch.object(cloud_manager, 'deploy_multi_cloud') as mock_deploy:
            mock_deploy.return_value = {
                "deployment_id": "multi_cloud_001",
                "deployments": {
                    "aws": {"endpoint": "https://aws-endpoint.com", "status": "active"},
                    "gcp": {"endpoint": "https://gcp-endpoint.com", "status": "active"},
                    "azure": {"endpoint": "https://azure-endpoint.com", "status": "active"}
                },
                "load_balancer": "https://global-lb.example.com"
            }
            
            deployment_result = cloud_manager.deploy_multi_cloud(multi_cloud_config)
            
            assert "deployment_id" in deployment_result
            assert len(deployment_result["deployments"]) == 3

    def test_edge_deployment_integration(self, optimized_model):
        """Test edge deployment integration"""
        edge_manager = EdgeModelManager(
            edge_devices=["nvidia_jetson", "raspberry_pi", "mobile"]
        )
        
        edge_config = {
            "model_id": "model_123",
            "target_devices": ["nvidia_jetson"],
            "optimization_config": {
                "quantization": "int8",
                "pruning_ratio": 0.3,
                "target_latency_ms": 50
            }
        }
        
        with patch.object(edge_manager, 'deploy_to_edge') as mock_edge_deploy:
            mock_edge_deploy.return_value = {
                "edge_deployment_id": "edge_001",
                "device_deployments": [
                    {
                        "device_id": "jetson_001",
                        "status": "deployed",
                        "performance": {"latency": 35, "throughput": 28}
                    }
                ],
                "sync_status": "synchronized"
            }
            
            edge_result = edge_manager.deploy_to_edge(edge_config)
            
            assert "edge_deployment_id" in edge_result
            assert len(edge_result["device_deployments"]) == 1


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
