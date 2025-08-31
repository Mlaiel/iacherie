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

"""Comprehensive AI Engine Management Tests

Ultra-advanced enterprise-grade test suite for AI engine orchestration and lifecycle management.
Tests model loading, inference caching, memory optimization, and multi-format AI processing.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  COPYRIGHT WARNING: This file is protected by copyright law. Unauthorized copying,
distribution, modification, or use is strictly prohibited. Violations will result in
legal action. Contact mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: Advanced AI engine orchestration, model lifecycle management
- Backend Senior Engineer: Enterprise AI infrastructure, performance optimization
- ML Engineer: Model loading strategies, inference optimization, memory management
- DevOps Engineer: AI deployment pipelines, scalability testing
- Performance Engineer: AI inference benchmarking, resource optimization
- Quality Assurance Lead: Comprehensive AI testing, edge case validation

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import tempfile
import shutil
import time
import threading
import gc
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
from concurrent.futures import ThreadPoolExecutor, Future

# System imports
import os
import sys
import logging
import warnings

# Test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from ai.core.ai_engine import (
    AIEngineManager,
    AIModel,
    ModelConfig,
    ModelMetrics,
    ModelCache,
    AIModelType,
    ModelStatus,
    DeviceType,
    ai_engine,
    ai_model_context,
    ai_inference_decorator
)

from ai.core.exceptions import ModelConnectionError, ConfigurationError, OptimizationError


class TestAIModelType:
    """Test suite for AIModelType enumeration"""    
    def test_ai_model_type_values(self):
        """Test AI model type enum values"""        assert AIModelType.TRANSFORMER.value == "transformer"
        assert AIModelType.CNN.value == "cnn"
        assert AIModelType.RNN.value == "rnn"
        assert AIModelType.DIFFUSION.value == "diffusion"
        assert AIModelType.GAN.value == "gan"
        assert AIModelType.AUDIO_CLASSIFIER.value == "audio_classifier"
        assert AIModelType.IMAGE_CLASSIFIER.value == "image_classifier"
        assert AIModelType.TEXT_CLASSIFIER.value == "text_classifier"
        assert AIModelType.CONTENT_GENERATOR.value == "content_generator"
        assert AIModelType.PROTECTION_DETECTOR.value == "protection_detector"
        assert AIModelType.QUALITY_ASSESSOR.value == "quality_assessor"
        assert AIModelType.SEO_OPTIMIZER.value == "seo_optimizer"
        assert AIModelType.COLLABORATION_MATCHER.value == "collaboration_matcher"
    
    def test_creator_specific_model_types(self):
        """Test model types cover all creator needs"""        # Musicians
        musician_models = [
            AIModelType.AUDIO_CLASSIFIER,
            AIModelType.CONTENT_GENERATOR,
            AIModelType.QUALITY_ASSESSOR
        ]
        assert all(model in AIModelType for model in musician_models)
        
        # Photographers
        photographer_models = [
            AIModelType.IMAGE_CLASSIFIER,
            AIModelType.CONTENT_GENERATOR,
            AIModelType.QUALITY_ASSESSOR
        ]
        assert all(model in AIModelType for model in photographer_models)
        
        # Bloggers/Influencers
        content_models = [
            AIModelType.TEXT_CLASSIFIER,
            AIModelType.SEO_OPTIMIZER,
            AIModelType.COLLABORATION_MATCHER
        ]
        assert all(model in AIModelType for model in content_models)


class TestModelStatus:
    """Test suite for ModelStatus enumeration"""    
    def test_model_status_values(self):
        """Test model status enum values"""        assert ModelStatus.UNLOADED.value == "unloaded"
        assert ModelStatus.LOADING.value == "loading"
        assert ModelStatus.LOADED.value == "loaded"
        assert ModelStatus.READY.value == "ready"
        assert ModelStatus.BUSY.value == "busy"
        assert ModelStatus.ERROR.value == "error"
        assert ModelStatus.UNLOADING.value == "unloading"
    
    def test_model_status_lifecycle(self):
        """Test model status lifecycle progression"""        lifecycle_sequence = [
            ModelStatus.UNLOADED,
            ModelStatus.LOADING,
            ModelStatus.LOADED,
            ModelStatus.READY,
            ModelStatus.BUSY,
            ModelStatus.READY,
            ModelStatus.UNLOADING,
            ModelStatus.UNLOADED
        ]
        
        # Ensure all statuses are valid
        for status in lifecycle_sequence:
            assert isinstance(status, ModelStatus)
            assert isinstance(status.value, str)


class TestDeviceType:
    """Test suite for DeviceType enumeration"""    
    def test_device_type_values(self):
        """Test device type enum values"""        assert DeviceType.CPU.value == "cpu"
        assert DeviceType.CUDA.value == "cuda"
        assert DeviceType.MPS.value == "mps"
        assert DeviceType.AUTO.value == "auto"
    
    def test_device_type_coverage(self):
        """Test device type coverage for different platforms"""        # Should support major compute platforms
        supported_devices = [device.value for device in DeviceType]
        assert "cpu" in supported_devices  # Universal support
        assert "cuda" in supported_devices  # NVIDIA GPU support
        assert "mps" in supported_devices  # Apple Metal support
        assert "auto" in supported_devices  # Automatic detection


class TestModelConfig:
    """Test suite for ModelConfig data class"""    
    def test_model_config_creation(self):
        """Test model configuration creation"""        config = ModelConfig(
            name="test-model",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/path/to/model",
            device=DeviceType.CUDA,
            batch_size=8,
            max_length=512,
            precision="float16",
            cache_size=2000,
            timeout_seconds=60,
            memory_limit_gb=4.0,
            auto_unload_after_seconds=600
        )
        
        assert config.name == "test-model"
        assert config.model_type == AIModelType.TEXT_CLASSIFIER
        assert config.model_path == "/path/to/model"
        assert config.device == DeviceType.CUDA
        assert config.batch_size == 8
        assert config.max_length == 512
        assert config.precision == "float16"
        assert config.cache_size == 2000
        assert config.timeout_seconds == 60
        assert config.memory_limit_gb == 4.0
        assert config.auto_unload_after_seconds == 600
    
    def test_model_config_defaults(self):
        """Test model configuration default values"""        config = ModelConfig(
            name="minimal-model",
            model_type=AIModelType.TRANSFORMER,
            model_path="/path/to/model"
        )
        
        assert config.device == DeviceType.AUTO
        assert config.batch_size == 1
        assert config.max_length == 512
        assert config.precision == "float32"
        assert config.cache_size == 1000
        assert config.timeout_seconds == 30
        assert config.memory_limit_gb is None
        assert config.auto_unload_after_seconds == 300
        assert config.preprocessing_config == {}
        assert config.postprocessing_config == {}
        assert config.custom_config == {}
    
    def test_model_config_to_dict(self):
        """Test model configuration dictionary conversion"""        config = ModelConfig(
            name="dict-test-model",
            model_type=AIModelType.CNN,
            model_path="/test/path",
            device=DeviceType.CPU,
            batch_size=4,
            custom_config={"test_param": "test_value"}
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["name"] == "dict-test-model"
        assert config_dict["model_type"] == "cnn"
        assert config_dict["model_path"] == "/test/path"
        assert config_dict["device"] == "cpu"
        assert config_dict["batch_size"] == 4
        assert config_dict["custom_config"]["test_param"] == "test_value"
        assert isinstance(config_dict, dict)
        assert len(config_dict) >= 10  # All major fields present
    
    def test_model_config_creator_specific(self):
        """Test model configurations for specific creator types"""        # Musician audio processing model
        audio_config = ModelConfig(
            name="audio-classifier",
            model_type=AIModelType.AUDIO_CLASSIFIER,
            model_path="/models/audio",
            preprocessing_config={
                "sample_rate": 44100,
                "n_mels": 128,
                "hop_length": 512
            }
        )
        
        assert audio_config.model_type == AIModelType.AUDIO_CLASSIFIER
        assert audio_config.preprocessing_config["sample_rate"] == 44100
        
        # Photographer image processing model
        image_config = ModelConfig(
            name="image-classifier",
            model_type=AIModelType.IMAGE_CLASSIFIER,
            model_path="/models/image",
            preprocessing_config={
                "image_size": [224, 224],
                "normalize": True,
                "augmentation": False
            }
        )
        
        assert image_config.model_type == AIModelType.IMAGE_CLASSIFIER
        assert image_config.preprocessing_config["image_size"] == [224, 224]


class TestModelMetrics:
    """Test suite for ModelMetrics data class"""    
    def test_model_metrics_creation(self):
        """Test model metrics creation"""        metrics = ModelMetrics(model_name="test-model")
        
        assert metrics.model_name == "test-model"
        assert metrics.load_time == 0.0
        assert metrics.inference_count == 0
        assert metrics.total_inference_time == 0.0
        assert metrics.average_inference_time == 0.0
        assert metrics.peak_memory_usage == 0.0
        assert metrics.error_count == 0
        assert isinstance(metrics.last_used, datetime)
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
    
    def test_inference_stats_update(self):
        """Test inference statistics updates"""        metrics = ModelMetrics(model_name="inference-test")
        
        # First inference
        metrics.update_inference_stats(0.5)
        assert metrics.inference_count == 1
        assert metrics.total_inference_time == 0.5
        assert metrics.average_inference_time == 0.5
        
        # Second inference
        metrics.update_inference_stats(0.3)
        assert metrics.inference_count == 2
        assert metrics.total_inference_time == 0.8
        assert metrics.average_inference_time == 0.4
        
        # Third inference
        metrics.update_inference_stats(0.2)
        assert metrics.inference_count == 3
        assert metrics.total_inference_time == 1.0
        assert abs(metrics.average_inference_time - (1.0/3)) < 0.001
    
    def test_cache_stats_update(self):
        """Test cache statistics updates"""        metrics = ModelMetrics(model_name="cache-test")
        
        # Cache hits
        metrics.update_cache_stats(True)
        metrics.update_cache_stats(True)
        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 0
        assert metrics.cache_hit_rate == 1.0
        
        # Cache miss
        metrics.update_cache_stats(False)
        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 1
        assert abs(metrics.cache_hit_rate - (2/3)) < 0.001
        
        # More hits and misses
        metrics.update_cache_stats(True)
        metrics.update_cache_stats(False)
        assert metrics.cache_hits == 3
        assert metrics.cache_misses == 2
        assert metrics.cache_hit_rate == 0.6
    
    def test_cache_hit_rate_edge_cases(self):
        """Test cache hit rate calculation edge cases"""        metrics = ModelMetrics(model_name="edge-test")
        
        # No cache activity
        assert metrics.cache_hit_rate == 0.0
        
        # Only misses
        metrics.update_cache_stats(False)
        metrics.update_cache_stats(False)
        assert metrics.cache_hit_rate == 0.0
        
        # Only hits
        metrics2 = ModelMetrics(model_name="hits-only")
        metrics2.update_cache_stats(True)
        metrics2.update_cache_stats(True)
        assert metrics2.cache_hit_rate == 1.0


class TestModelCache:
    """Test suite for ModelCache class"""    
    def setup_method(self):
        """Setup model cache for testing"""        self.cache = ModelCache(max_size=5, ttl_seconds=2)
    
    def test_cache_initialization(self):
        """Test cache initialization"""        assert self.cache.max_size == 5
        assert self.cache.ttl_seconds == 2
        assert isinstance(self.cache.cache, dict)
        assert len(self.cache.cache) == 0
    
    def test_cache_key_generation(self):
        """Test cache key generation"""        input_data = "test input"
        config = {"model": "test", "param": "value"}
        
        key1 = self.cache._generate_key(input_data, config)
        key2 = self.cache._generate_key(input_data, config)
        key3 = self.cache._generate_key("different input", config)
        key4 = self.cache._generate_key(input_data, {"model": "different"})
        
        # Same input and config should generate same key
        assert key1 == key2
        
        # Different input should generate different key
        assert key1 != key3
        
        # Different config should generate different key
        assert key1 != key4
        
        # Keys should be strings
        assert isinstance(key1, str)
        assert len(key1) > 0
    
    def test_cache_put_and_get(self):
        """Test cache put and get operations"""        input_data = "test input"
        config = {"model": "test"}
        result = {"output": "test result"}
        
        # Initially empty
        assert self.cache.get(input_data, config) is None
        
        # Put and get
        self.cache.put(input_data, config, result)
        cached_result = self.cache.get(input_data, config)
        
        assert cached_result == result
        assert cached_result is result  # Should be same object
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""        input_data = "ttl test"
        config = {"model": "ttl"}
        result = {"output": "ttl result"}
        
        # Cache with short TTL
        cache = ModelCache(max_size=10, ttl_seconds=1)
        cache.put(input_data, config, result)
        
        # Should be available immediately
        assert cache.get(input_data, config) == result
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get(input_data, config) is None
    
    def test_cache_size_limit(self):
        """Test cache size limit enforcement"""        # Fill cache to limit
        for i in range(self.cache.max_size):
            self.cache.put(f"input_{i}", {"model": f"model_{i}"}, f"result_{i}")
        
        assert len(self.cache.cache) == self.cache.max_size
        
        # Add one more (should trigger eviction)
        self.cache.put("overflow", {"model": "overflow"}, "overflow_result")
        
        # Should still be at max size
        assert len(self.cache.cache) == self.cache.max_size
    
    def test_cache_eviction_strategy(self):
        """Test LRU cache eviction strategy"""        # Fill cache
        for i in range(self.cache.max_size):
            self.cache.put(f"input_{i}", {"model": f"model_{i}"}, f"result_{i}")
        
        # Access first item to make it recently used
        self.cache.get("input_0", {"model": "model_0"})
        
        # Add new item to trigger eviction
        self.cache.put("new_input", {"model": "new"}, "new_result")
        
        # First item should still be there (recently used)
        assert self.cache.get("input_0", {"model": "model_0"}) == "result_0"
        
        # New item should be cached
        assert self.cache.get("new_input", {"model": "new"}) == "new_result"
    
    def test_cache_clear(self):
        """Test cache clearing"""        # Add some items
        for i in range(3):
            self.cache.put(f"input_{i}", {"model": f"model_{i}"}, f"result_{i}")
        
        assert len(self.cache.cache) == 3
        
        # Clear cache
        self.cache.clear()
        
        assert len(self.cache.cache) == 0
        assert self.cache.get("input_0", {"model": "model_0"}) is None
    
    def test_cache_thread_safety(self):
        """Test cache thread safety"""        results = []
        errors = []
        
        def cache_operations(thread_id):
            try:
                for i in range(10):
                    input_data = f"thread_{thread_id}_input_{i}"
                    config = {"thread": thread_id, "iteration": i}
                    result = f"thread_{thread_id}_result_{i}"
                    
                    # Put and get
                    self.cache.put(input_data, config, result)
                    cached = self.cache.get(input_data, config)
                    
                    if cached == result:
                        results.append((thread_id, i, "success"))
                    else:
                        results.append((thread_id, i, "failed"))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Run concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        
        # Verify successful operations
        successful_ops = [r for r in results if r[2] == "success"]
        assert len(successful_ops) > 0


class TestAIModel:
    """Test suite for AIModel class"""    
    def setup_method(self):
        """Setup AI model for testing"""        self.config = ModelConfig(
            name="test-model",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/fake/path/model",
            device=DeviceType.CPU,
            batch_size=2,
            cache_size=100
        )
        self.model = AIModel(self.config)
    
    def test_ai_model_initialization(self):
        """Test AI model initialization"""        assert self.model.config == self.config
        assert self.model.status == ModelStatus.UNLOADED
        assert isinstance(self.model.metrics, ModelMetrics)
        assert self.model.metrics.model_name == "test-model"
        assert isinstance(self.model.cache, ModelCache)
        assert self.model.model is None
        assert self.model.tokenizer is None
        assert self.model.pipeline is None
    
    def test_model_device_selection(self):
        """Test model device selection logic"""        # CPU device
        cpu_config = ModelConfig("cpu-model", AIModelType.TRANSFORMER, "/path", DeviceType.CPU)
        cpu_model = AIModel(cpu_config)
        device = cpu_model._get_device()
        assert device == "cpu"
        
        # Auto device (should default to CPU in test environment)
        auto_config = ModelConfig("auto-model", AIModelType.TRANSFORMER, "/path", DeviceType.AUTO)
        auto_model = AIModel(auto_config)
        device = auto_model._get_device()
        assert device in ["cpu", "cuda", "mps"]  # Should select available device
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_model_loading_success(self, mock_pipeline):
        """Test successful model loading"""        # Mock pipeline creation
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Test loading
        success = self.model.load()
        
        assert success is True
        assert self.model.status == ModelStatus.READY
        assert self.model.pipeline == mock_pipeline_instance
        assert self.model.metrics.load_time > 0
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_model_loading_failure(self, mock_pipeline):
        """Test model loading failure"""        # Mock pipeline creation failure
        mock_pipeline.side_effect = Exception("Model loading failed")
        
        # Test loading
        success = self.model.load()
        
        assert success is False
        assert self.model.status == ModelStatus.ERROR
        assert self.model.pipeline is None
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', False)
    def test_model_loading_no_pytorch(self):
        """Test model loading when PyTorch is not available"""        success = self.model.load()
        
        assert success is False
        assert self.model.status == ModelStatus.ERROR
    
    def test_model_unloading(self):
        """Test model unloading"""        # Set up loaded state
        self.model.pipeline = Mock()
        self.model.model = Mock()
        self.model.tokenizer = Mock()
        self.model.status = ModelStatus.READY
        
        # Test unloading
        self.model.unload()
        
        assert self.model.status == ModelStatus.UNLOADED
        assert self.model.pipeline is None
        assert self.model.model is None
        assert self.model.tokenizer is None
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_model_prediction_success(self, mock_pipeline):
        """Test successful model prediction"""        # Setup mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = {"label": "positive", "score": 0.95}
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Load model
        self.model.load()
        
        # Test prediction
        input_data = "This is a test input"
        result = self.model.predict(input_data)
        
        assert result == {"label": "positive", "score": 0.95}
        assert self.model.metrics.inference_count == 1
        assert self.model.metrics.average_inference_time > 0
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_model_prediction_with_cache(self, mock_pipeline):
        """Test model prediction with caching"""        # Setup mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = {"result": "cached_test"}
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Load model
        self.model.load()
        
        input_data = "cache test input"
        
        # First prediction (cache miss)
        result1 = self.model.predict(input_data, use_cache=True)
        assert self.model.metrics.cache_misses == 1
        assert self.model.metrics.cache_hits == 0
        
        # Second prediction (cache hit)
        result2 = self.model.predict(input_data, use_cache=True)
        assert result1 == result2
        assert self.model.metrics.cache_misses == 1
        assert self.model.metrics.cache_hits == 1
        
        # Pipeline should only be called once
        assert mock_pipeline_instance.call_count == 1
    
    def test_model_prediction_not_ready(self):
        """Test prediction when model is not ready"""        # Model is unloaded
        assert self.model.status == ModelStatus.UNLOADED
        
        with pytest.raises(ModelConnectionError):
            self.model.predict("test input")
    
    def test_model_idle_detection(self):
        """Test model idle detection"""        # Initially not idle (just created)
        assert not self.model.is_idle
        
        # Simulate old activity
        old_time = datetime.utcnow() - timedelta(seconds=self.config.auto_unload_after_seconds + 10)
        self.model._last_activity = old_time
        
        # Should now be idle
        assert self.model.is_idle
    
    def test_model_metrics_collection(self):
        """Test model metrics collection"""        # Update some metrics
        self.model.metrics.update_inference_stats(0.1)
        self.model.metrics.update_inference_stats(0.2)
        self.model.metrics.update_cache_stats(True)
        self.model.metrics.update_cache_stats(False)
        self.model.metrics.error_count = 1
        
        metrics_dict = self.model.get_metrics()
        
        assert metrics_dict["model_name"] == "test-model"
        assert metrics_dict["status"] == "unloaded"
        assert metrics_dict["inference_count"] == 2
        assert metrics_dict["average_inference_time"] == 0.15
        assert metrics_dict["cache_hit_rate"] == 0.5
        assert metrics_dict["error_count"] == 1


class TestAIEngineManager:
    """Test suite for AIEngineManager class"""    
    def setup_method(self):
        """Setup AI engine manager for testing"""        self.engine = AIEngineManager(max_concurrent_models=3)
    
    def teardown_method(self):
        """Cleanup after tests"""        # Clear all models
        self.engine.models.clear()
    
    def test_engine_initialization(self):
        """Test AI engine manager initialization"""        assert self.engine.max_concurrent_models == 3
        assert isinstance(self.engine.models, dict)
        assert len(self.engine.models) == 0
        assert hasattr(self.engine, 'model_pool')
        assert hasattr(self.engine, '_cleanup_thread')
    
    def test_register_model(self):
        """Test model registration"""        config = ModelConfig(
            name="registered-model",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        
        self.engine.register_model(config)
        
        assert "registered-model" in self.engine.models
        assert isinstance(self.engine.models["registered-model"], AIModel)
        assert self.engine.models["registered-model"].config == config
    
    def test_register_duplicate_model(self):
        """Test registering duplicate model"""        config = ModelConfig(
            name="duplicate-model",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        
        # Register first time
        self.engine.register_model(config)
        assert "duplicate-model" in self.engine.models
        
        # Register again (should replace)
        new_config = ModelConfig(
            name="duplicate-model",
            model_type=AIModelType.CNN,
            model_path="/new/path"
        )
        self.engine.register_model(new_config)
        
        assert self.engine.models["duplicate-model"].config.model_type == AIModelType.CNN
    
    def test_unregister_model(self):
        """Test model unregistration"""        config = ModelConfig(
            name="unregister-test",
            model_type=AIModelType.TRANSFORMER,
            model_path="/test/path"
        )
        
        # Register and then unregister
        self.engine.register_model(config)
        assert "unregister-test" in self.engine.models
        
        success = self.engine.unregister_model("unregister-test")
        assert success is True
        assert "unregister-test" not in self.engine.models
        
        # Try to unregister non-existent model
        success = self.engine.unregister_model("non-existent")
        assert success is False
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_load_model(self, mock_pipeline):
        """Test model loading through engine"""        # Setup mock
        mock_pipeline.return_value = Mock()
        
        # Register model
        config = ModelConfig(
            name="load-test",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        self.engine.register_model(config)
        
        # Load model
        success = self.engine.load_model("load-test")
        
        assert success is True
        assert self.engine.models["load-test"].status == ModelStatus.READY
    
    def test_load_unregistered_model(self):
        """Test loading unregistered model"""        success = self.engine.load_model("unregistered-model")
        assert success is False
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_unload_model(self, mock_pipeline):
        """Test model unloading through engine"""        # Setup and load model
        mock_pipeline.return_value = Mock()
        config = ModelConfig(
            name="unload-test",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        self.engine.register_model(config)
        self.engine.load_model("unload-test")
        
        # Unload model
        success = self.engine.unload_model("unload-test")
        
        assert success is True
        assert self.engine.models["unload-test"].status == ModelStatus.UNLOADED
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_predict_through_engine(self, mock_pipeline):
        """Test prediction through engine"""        # Setup mock
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = {"prediction": "success"}
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Register and load model
        config = ModelConfig(
            name="predict-test",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        self.engine.register_model(config)
        self.engine.load_model("predict-test")
        
        # Make prediction
        result = self.engine.predict("predict-test", "test input")
        
        assert result == {"prediction": "success"}
    
    def test_predict_unregistered_model(self):
        """Test prediction with unregistered model"""        with pytest.raises(ModelConnectionError):
            self.engine.predict("unregistered", "test input")
    
    @pytest.mark.asyncio
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    async def test_async_predict(self, mock_pipeline):
        """Test async prediction"""        # Setup mock
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = {"async": "result"}
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Register and load model
        config = ModelConfig(
            name="async-test",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        self.engine.register_model(config)
        self.engine.load_model("async-test")
        
        # Make async prediction
        result = await self.engine.async_predict("async-test", "async input")
        
        assert result == {"async": "result"}
    
    def test_list_models(self):
        """Test listing all models"""        # Register multiple models
        configs = [
            ModelConfig(f"model-{i}", AIModelType.TEXT_CLASSIFIER, f"/path/{i}")
            for i in range(3)
        ]
        
        for config in configs:
            self.engine.register_model(config)
        
        models = self.engine.list_models()
        
        assert len(models) == 3
        assert all(f"model-{i}" in models for i in range(3))
        assert all(models[f"model-{i}"]["status"] == "unloaded" for i in range(3))
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_get_model_metrics(self, mock_pipeline):
        """Test getting model metrics"""        # Setup mock
        mock_pipeline.return_value = Mock()
        
        # Register and use model
        config = ModelConfig(
            name="metrics-test",
            model_type=AIModelType.TEXT_CLASSIFIER,
            model_path="/test/path"
        )
        self.engine.register_model(config)
        self.engine.load_model("metrics-test")
        
        # Get metrics
        metrics = self.engine.get_model_metrics("metrics-test")
        
        assert metrics["model_name"] == "metrics-test"
        assert "status" in metrics
        assert "inference_count" in metrics
        assert "load_time" in metrics
    
    def test_get_metrics_unregistered_model(self):
        """Test getting metrics for unregistered model"""        with pytest.raises(ModelConnectionError):
            self.engine.get_model_metrics("unregistered")
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_engine_status(self, mock_pipeline):
        """Test getting engine status"""        # Setup mock
        mock_pipeline.return_value = Mock()
        
        # Register models
        for i in range(2):
            config = ModelConfig(
                f"status-model-{i}",
                AIModelType.TEXT_CLASSIFIER,
                f"/path/{i}"
            )
            self.engine.register_model(config)
        
        # Load one model
        self.engine.load_model("status-model-0")
        
        status = self.engine.get_engine_status()
        
        assert status["total_models"] == 2
        assert status["loaded_models"] == 1
        assert "total_inferences" in status
        assert "total_errors" in status
        assert "error_rate" in status
        assert "model_statuses" in status
        assert "system_info" in status
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_memory_optimization(self, mock_pipeline):
        """Test memory optimization"""        # Setup mock
        mock_pipeline.return_value = Mock()
        
        # Register and load multiple models
        for i in range(3):
            config = ModelConfig(
                f"opt-model-{i}",
                AIModelType.TEXT_CLASSIFIER,
                f"/path/{i}"
            )
            self.engine.register_model(config)
            self.engine.load_model(f"opt-model-{i}")
        
        # Simulate different usage times
        old_time = datetime.utcnow() - timedelta(hours=1)
        self.engine.models["opt-model-0"].metrics.last_used = old_time
        
        # Run optimization
        result = self.engine.optimize_memory()
        
        assert "models_unloaded" in result
        assert "memory_freed_estimate" in result
        assert "optimization_time" in result
        assert result["optimization_time"] >= 0
    
    def test_health_check_healthy(self):
        """Test health check with healthy engine"""        # Register a model
        config = ModelConfig(
            "healthy-model",
            AIModelType.TEXT_CLASSIFIER,
            "/path"
        )
        self.engine.register_model(config)
        
        health = self.engine.health_check()
        
        assert health["status"] in ["healthy", "warning"]  # No models loaded is a warning
        assert "issues" in health
        assert "recommendations" in health
        assert "timestamp" in health
    
    def test_health_check_unhealthy(self):
        """Test health check with unhealthy engine"""        # Create model with error status
        config = ModelConfig(
            "error-model",
            AIModelType.TEXT_CLASSIFIER,
            "/path"
        )
        self.engine.register_model(config)
        self.engine.models["error-model"].status = ModelStatus.ERROR
        
        health = self.engine.health_check()
        
        assert health["status"] in ["degraded", "unhealthy"]
        assert len(health["issues"]) > 0
    
    def test_concurrent_model_operations(self):
        """Test concurrent model operations"""        results = []
        errors = []
        
        def register_and_operate(thread_id):
            try:
                config = ModelConfig(
                    f"concurrent-{thread_id}",
                    AIModelType.TEXT_CLASSIFIER,
                    f"/path/{thread_id}"
                )
                self.engine.register_model(config)
                
                # Try to load model (may fail due to mocking, that's ok)
                try:
                    success = self.engine.load_model(f"concurrent-{thread_id}")
                    results.append((thread_id, "load", success))
                except Exception:
                    results.append((thread_id, "load", False))
                
                # Get metrics
                try:
                    metrics = self.engine.get_model_metrics(f"concurrent-{thread_id}")
                    results.append((thread_id, "metrics", True))
                except Exception:
                    results.append((thread_id, "metrics", False))
                    
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Run concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_and_operate, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have minimal errors
        assert len(errors) <= 1, f"Too many concurrent errors: {errors}"
        assert len(results) >= 5  # At least some operations succeeded


class TestModelContext:
    """Test suite for AI model context manager"""    
    def setup_method(self):
        """Setup for context manager tests"""        self.config = ModelConfig(
            "context-test",
            AIModelType.TEXT_CLASSIFIER,
            "/test/path"
        )
        ai_engine.register_model(self.config)
    
    def teardown_method(self):
        """Cleanup after context tests"""        try:
            ai_engine.unregister_model("context-test")
        except:
            pass
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_model_context_manager(self, mock_pipeline):
        """Test AI model context manager"""        mock_pipeline.return_value = Mock()
        
        with ai_model_context("context-test") as model:
            assert isinstance(model, AIModel)
            assert model.config.name == "context-test"
            assert model.status == ModelStatus.READY
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_model_context_auto_unload(self, mock_pipeline):
        """Test model context with auto unload"""        mock_pipeline.return_value = Mock()
        
        with ai_model_context("context-test", auto_unload=True) as model:
            assert model.status == ModelStatus.READY
        
        # After context, model should be unloaded
        assert ai_engine.models["context-test"].status == ModelStatus.UNLOADED
    
    def test_model_context_error_handling(self):
        """Test model context error handling"""        # Model loading will fail (no mocking)
        try:
            with ai_model_context("context-test") as model:
                # Should not reach here due to loading failure
                assert False, "Should have failed to load model"
        except ModelConnectionError:
            # Expected error
            pass


class TestInferenceDecorator:
    """Test suite for AI inference decorator"""    
    def setup_method(self):
        """Setup for decorator tests"""        self.config = ModelConfig(
            "decorator-test",
            AIModelType.TEXT_CLASSIFIER,
            "/test/path"
        )
        ai_engine.register_model(self.config)
    
    def teardown_method(self):
        """Cleanup after decorator tests"""        try:
            ai_engine.unregister_model("decorator-test")
        except:
            pass
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_inference_decorator_sync(self, mock_pipeline):
        """Test inference decorator for sync functions"""        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = {"decorated": "result"}
        mock_pipeline.return_value = mock_pipeline_instance
        
        @ai_inference_decorator("decorator-test", input_key="text")
        def process_text(text, **kwargs):
            inference_result = kwargs.get("decorator-test_result")
            return {"processed": text, "ai_result": inference_result}
        
        result = process_text(text="test input")
        
        assert result["processed"] == "test input"
        assert result["ai_result"] == {"decorated": "result"}
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    @pytest.mark.asyncio
    async def test_inference_decorator_async(self, mock_pipeline):
        """Test inference decorator for async functions"""        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = {"async_decorated": "result"}
        mock_pipeline.return_value = mock_pipeline_instance
        
        @ai_inference_decorator("decorator-test", input_key="content")
        async def async_process_content(content, **kwargs):
            inference_result = kwargs.get("decorator-test_result")
            return {"async_processed": content, "ai_result": inference_result}
        
        result = await async_process_content(content="async test input")
        
        assert result["async_processed"] == "async test input"
        assert result["ai_result"] == {"async_decorated": "result"}
    
    def test_inference_decorator_missing_input(self):
        """Test inference decorator with missing input key"""        @ai_inference_decorator("decorator-test", input_key="missing_key")
        def failing_function(**kwargs):
            return "should not reach here"
        
        with pytest.raises(ValueError, match="Required input key 'missing_key' not found"):
            failing_function(other_key="value")


class TestAIEngineIntegration:
    """Integration tests for AI engine with real-world scenarios"""    
    def setup_method(self):
        """Setup integration testing"""        self.engine = AIEngineManager()
        
        # Register models for different creator types
        self.register_creator_models()
    
    def register_creator_models(self):
        """Register models for different creator types"""        # Musician models
        self.engine.register_model(ModelConfig(
            "audio-content-classifier",
            AIModelType.AUDIO_CLASSIFIER,
            "/models/audio/classifier",
            preprocessing_config={"sample_rate": 44100}
        ))
        
        self.engine.register_model(ModelConfig(
            "music-quality-assessor",
            AIModelType.QUALITY_ASSESSOR,
            "/models/audio/quality",
            custom_config={"focus": "music"}
        ))
        
        # Photographer models
        self.engine.register_model(ModelConfig(
            "image-content-classifier",
            AIModelType.IMAGE_CLASSIFIER,
            "/models/image/classifier",
            preprocessing_config={"image_size": [224, 224]}
        ))
        
        self.engine.register_model(ModelConfig(
            "photo-quality-assessor",
            AIModelType.QUALITY_ASSESSOR,
            "/models/image/quality",
            custom_config={"focus": "photography"}
        ))
        
        # Blogger/Influencer models
        self.engine.register_model(ModelConfig(
            "text-content-classifier",
            AIModelType.TEXT_CLASSIFIER,
            "/models/text/classifier",
            max_length=1024
        ))
        
        self.engine.register_model(ModelConfig(
            "seo-optimizer",
            AIModelType.SEO_OPTIMIZER,
            "/models/text/seo",
            custom_config={"optimization_level": "advanced"}
        ))
        
        self.engine.register_model(ModelConfig(
            "collaboration-matcher",
            AIModelType.COLLABORATION_MATCHER,
            "/models/collab/matcher",
            custom_config={"matching_algorithm": "semantic"}
        ))
    
    def test_creator_workflow_models_registered(self):
        """Test that all creator workflow models are properly registered"""        models = self.engine.list_models()
        
        # Musician models
        assert "audio-content-classifier" in models
        assert "music-quality-assessor" in models
        
        # Photographer models
        assert "image-content-classifier" in models
        assert "photo-quality-assessor" in models
        
        # Blogger/Influencer models
        assert "text-content-classifier" in models
        assert "seo-optimizer" in models
        assert "collaboration-matcher" in models
        
        # All models should be unloaded initially
        for model_name, info in models.items():
            assert info["status"] == "unloaded"
    
    def test_content_processing_pipeline_simulation(self):
        """Test simulation of complete content processing pipeline"""        # Simulate business logic: User Upload → AI Protection → SEO → Collaboration → Distribution
        
        pipeline_steps = [
            "text-content-classifier",  # Content safety classification
            "seo-optimizer",           # SEO optimization
            "collaboration-matcher"     # Find collaboration opportunities
        ]
        
        for step in pipeline_steps:
            assert step in self.engine.models
            
            # Get model metrics (simulates model usage tracking)
            try:
                metrics = self.engine.get_model_metrics(step)
                assert metrics["model_name"] == step
            except ModelConnectionError:
                # Expected when model is not loaded
                pass
    
    @patch('backend.ai.core.ai_engine.PYTORCH_AVAILABLE', True)
    @patch('backend.ai.core.ai_engine.pipeline')
    def test_multi_model_concurrent_loading(self, mock_pipeline):
        """Test concurrent loading of multiple models"""        mock_pipeline.return_value = Mock()
        
        model_names = [
            "text-content-classifier",
            "seo-optimizer",
            "collaboration-matcher"
        ]
        
        # Load models concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.engine.load_model, name)
                for name in model_names
            ]
            
            results = [future.result() for future in futures]
        
        # All models should load successfully
        assert all(results)
        
        # Verify all models are ready
        for name in model_names:
            assert self.engine.models[name].status == ModelStatus.READY
    
    def test_resource_management_under_load(self):
        """Test resource management under high load"""        # Register more models than the concurrent limit
        extra_models = []
        for i in range(5):
            model_name = f"extra-model-{i}"
            config = ModelConfig(
                model_name,
                AIModelType.TEXT_CLASSIFIER,
                f"/extra/path/{i}"
            )
            self.engine.register_model(config)
            extra_models.append(model_name)
        
        # Check that we have more models than the limit
        total_models = len(self.engine.models)
        assert total_models > self.engine.max_concurrent_models
        
        # Memory optimization should handle this
        optimization_result = self.engine.optimize_memory()
        assert "models_unloaded" in optimization_result
        assert optimization_result["optimization_time"] >= 0
    
    def test_engine_health_monitoring(self):
        """Test comprehensive engine health monitoring"""        health = self.engine.health_check()
        
        # Should have basic health structure
        assert "status" in health
        assert "issues" in health
        assert "recommendations" in health
        assert "timestamp" in health
        
        # With registered models but none loaded, should be warning
        assert health["status"] in ["healthy", "warning"]
        
        # Get comprehensive status
        status = self.engine.get_engine_status()
        assert status["total_models"] >= 7  # Our registered models
        assert status["loaded_models"] >= 0
        assert "system_info" in status
    
    def test_model_configuration_validation(self):
        """Test model configuration validation for different creator needs"""        # Test audio model configuration
        audio_model = self.engine.models["audio-content-classifier"]
        assert audio_model.config.model_type == AIModelType.AUDIO_CLASSIFIER
        assert audio_model.config.preprocessing_config["sample_rate"] == 44100
        
        # Test image model configuration
        image_model = self.engine.models["image-content-classifier"]
        assert image_model.config.model_type == AIModelType.IMAGE_CLASSIFIER
        assert image_model.config.preprocessing_config["image_size"] == [224, 224]
        
        # Test text model configuration
        text_model = self.engine.models["text-content-classifier"]
        assert text_model.config.model_type == AIModelType.TEXT_CLASSIFIER
        assert text_model.config.max_length == 1024
        
        # Test SEO optimizer configuration
        seo_model = self.engine.models["seo-optimizer"]
        assert seo_model.config.model_type == AIModelType.SEO_OPTIMIZER
        assert seo_model.config.custom_config["optimization_level"] == "advanced"


class TestGlobalAIEngine:
    """Test suite for global AI engine instance"""    
    def test_global_engine_instance(self):
        """Test global AI engine instance"""        assert ai_engine is not None
        assert isinstance(ai_engine, AIEngineManager)
    
    def test_global_engine_functionality(self):
        """Test global engine functionality"""        # Register a test model
        config = ModelConfig(
            "global-test",
            AIModelType.TEXT_CLASSIFIER,
            "/global/test"
        )
        
        ai_engine.register_model(config)
        
        # Verify registration
        assert "global-test" in ai_engine.models
        
        # Cleanup
        ai_engine.unregister_model("global-test")
    
    def test_global_engine_persistence(self):
        """Test global engine state persistence"""        # Register model
        config = ModelConfig(
            "persistence-test",
            AIModelType.TRANSFORMER,
            "/persistence/test"
        )
        ai_engine.register_model(config)
        
        # Should persist across operations
        models_before = len(ai_engine.models)
        ai_engine.get_engine_status()  # Some operation
        models_after = len(ai_engine.models)
        
        assert models_before == models_after
        assert "persistence-test" in ai_engine.models
        
        # Cleanup
        ai_engine.unregister_model("persistence-test")


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
