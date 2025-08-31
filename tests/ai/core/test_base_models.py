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
Comprehensive Tests for Base AI Models and Core Components
Enterprise-grade testing for foundational AI model classes

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
- Microservices + Audio + DevOps + IA Prompt Engineer
Email: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict, List
import json
import logging

from ai.core.base_models import (
    BaseAIModel,
    AudioModel,
    VideoModel,
    ImageModel,
    TextModel,
    ProtectionModel,
    BusinessIntelligenceModel,
    ModelConfig,
    ModelType,
    ModelProvider,
    ModelStatus,
    ModelMetrics,
    ProcessingResult,
    create_model,
    create_audio_model,
    create_video_model,
    create_image_model,
    create_text_model,
    create_protection_model,
    create_business_intelligence_model,
    MODEL_REGISTRY
)
from ai.core.exceptions import ModelError, ValidationError


class TestModelConfig:
    """Test suite for ModelConfig dataclass"""
    
    def test_model_config_creation_valid(self):
        """Test creating valid ModelConfig instances"""
        config = ModelConfig(
            name="test_model",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL,
            version="1.0.0",
            timeout=30,
            max_memory_mb=1024
        )
        
        assert config.name == "test_model"
        assert config.provider == ModelProvider.LOCAL
        assert config.model_type == ModelType.AUDIO_MODEL
        assert config.version == "1.0.0"
        assert config.timeout == 30
        assert config.max_memory_mb == 1024
        assert config.priority == 1  # default
        assert config.gpu_enabled is False  # default
        assert config.batch_size == 1  # default
        assert isinstance(config.config_params, dict)
    
    def test_model_config_defaults(self):
        """Test ModelConfig with default values"""
        config = ModelConfig(
            name="minimal_model",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.TEXT_MODEL
        )
        
        assert config.version == "1.0.0"
        assert config.timeout == 30
        assert config.max_memory_mb == 1024
        assert config.priority == 1
        assert config.gpu_enabled is False
        assert config.batch_size == 1
        assert config.config_params == {}
    
    def test_model_config_validation_empty_name(self):
        """Test ModelConfig validation with empty name"""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                name="",
                provider=ModelProvider.LOCAL,
                model_type=ModelType.AUDIO_MODEL
            )
        assert "Model name cannot be empty" in str(exc_info.value)
    
    def test_model_config_validation_negative_timeout(self):
        """Test ModelConfig validation with negative timeout"""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                name="test_model",
                provider=ModelProvider.LOCAL,
                model_type=ModelType.AUDIO_MODEL,
                timeout=-5
            )
        assert "Timeout must be positive" in str(exc_info.value)
    
    def test_model_config_validation_zero_memory(self):
        """Test ModelConfig validation with zero memory"""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                name="test_model",
                provider=ModelProvider.LOCAL,
                model_type=ModelType.AUDIO_MODEL,
                max_memory_mb=0
            )
        assert "Memory limit must be positive" in str(exc_info.value)
    
    def test_model_config_custom_params(self):
        """Test ModelConfig with custom parameters"""
        custom_params = {
            "learning_rate": 0.001,
            "batch_norm": True,
            "layers": [128, 64, 32]
        }
        
        config = ModelConfig(
            name="custom_model",
            provider=ModelProvider.GPU,
            model_type=ModelType.IMAGE_MODEL,
            config_params=custom_params
        )
        
        assert config.config_params == custom_params
        assert config.config_params["learning_rate"] == 0.001
        assert config.config_params["batch_norm"] is True
        assert config.config_params["layers"] == [128, 64, 32]


class TestModelMetrics:
    """Test suite for ModelMetrics dataclass"""
    
    def test_model_metrics_creation(self):
        """Test creating ModelMetrics instances"""
        metrics = ModelMetrics(model_name="test_model")
        
        assert metrics.model_name == "test_model"
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.0
        assert metrics.last_used is None
        assert metrics.memory_usage_mb == 0.0
        assert metrics.cpu_usage_percent == 0.0
        assert metrics.error_rate == 0.0
    
    def test_success_rate_calculation_zero_requests(self):
        """Test success rate with zero requests"""
        metrics = ModelMetrics(model_name="test_model")
        assert metrics.success_rate == 0.0
    
    def test_success_rate_calculation_with_requests(self):
        """Test success rate calculation with requests"""
        metrics = ModelMetrics(
            model_name="test_model",
            total_requests=100,
            successful_requests=95,
            failed_requests=5
        )
        assert metrics.success_rate == 95.0
    
    def test_success_rate_calculation_all_failed(self):
        """Test success rate with all failed requests"""
        metrics = ModelMetrics(
            model_name="test_model",
            total_requests=50,
            successful_requests=0,
            failed_requests=50
        )
        assert metrics.success_rate == 0.0


class TestProcessingResult:
    """Test suite for ProcessingResult dataclass"""
    
    def test_processing_result_creation_minimal(self):
        """Test creating minimal ProcessingResult"""
        result = ProcessingResult(
            success=True,
            data={"output": "test_result"}
        )
        
        assert result.success is True
        assert result.data == {"output": "test_result"}
        assert result.confidence == 0.0
        assert result.processing_time == 0.0
        assert result.model_version == ""
        assert result.metadata == {}
        assert result.error_message is None
        assert result.fingerprint is None
    
    def test_processing_result_creation_complete(self):
        """Test creating complete ProcessingResult"""
        metadata = {"source": "test", "timestamp": "2025-08-02"}
        
        result = ProcessingResult(
            success=True,
            data={"analysis": "complete"},
            confidence=0.95,
            processing_time=0.25,
            model_version="v1.2.0",
            metadata=metadata,
            fingerprint="abc123def456"
        )
        
        assert result.success is True
        assert result.data == {"analysis": "complete"}
        assert result.confidence == 0.95
        assert result.processing_time == 0.25
        assert result.model_version == "v1.2.0"
        assert result.metadata == metadata
        assert result.error_message is None
        assert result.fingerprint == "abc123def456"
    
    def test_processing_result_error(self):
        """Test ProcessingResult for error case"""
        result = ProcessingResult(
            success=False,
            data=None,
            error_message="Processing failed due to invalid input"
        )
        
        assert result.success is False
        assert result.data is None
        assert result.error_message == "Processing failed due to invalid input"


class MockAIModel(BaseAIModel):
    """Mock implementation of BaseAIModel for testing"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.connect_called = False
        self.disconnect_called = False
        self.process_called = False
        self.should_fail_connect = False
        self.should_fail_process = False
    
    async def connect(self) -> bool:
        """Mock connect implementation"""
        self.connect_called = True
        if self.should_fail_connect:
            self.status = ModelStatus.ERROR
            return False
        
        self.status = ModelStatus.READY
        self._is_connected = True
        return True
    
    async def disconnect(self) -> bool:
        """Mock disconnect implementation"""
        self.disconnect_called = True
        self._is_connected = False
        self.status = ModelStatus.MAINTENANCE
        return True
    
    async def process(self, input_data: Any, **kwargs) -> Any:
        """Mock process implementation"""
        self.process_called = True
        if self.should_fail_process:
            raise ModelError("Mock processing error")
        
        return {"processed": input_data, "kwargs": kwargs}


class TestBaseAIModel:
    """Test suite for BaseAIModel abstract class"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture for mock model configuration"""



        return ModelConfig(
            name="mock_model",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
    
    @pytest.fixture
    def mock_model(self, mock_config):
        """Fixture for mock AI model"""



        return MockAIModel(mock_config)
    
    def test_base_model_initialization(self, mock_model, mock_config):
        """Test BaseAIModel initialization"""
        assert mock_model.config == mock_config
        assert mock_model.model_type == ModelType.AUDIO_MODEL
        assert mock_model.provider == ModelProvider.LOCAL
        assert mock_model.status == ModelStatus.INITIALIZING
        assert isinstance(mock_model.metrics, ModelMetrics)
        assert mock_model.metrics.model_name == "mock_model"
        assert mock_model.model_name == "mock_model"
        assert mock_model.is_connected is False
        assert hasattr(mock_model, 'logger')
    
    @pytest.mark.asyncio
    async def test_model_connect_success(self, mock_model):
        """Test successful model connection"""
        result = await mock_model.connect()
        
        assert result is True
        assert mock_model.connect_called is True
        assert mock_model.is_connected is True
        assert mock_model.status == ModelStatus.READY
    
    @pytest.mark.asyncio
    async def test_model_connect_failure(self, mock_model):
        """Test failed model connection"""
        mock_model.should_fail_connect = True
        result = await mock_model.connect()
        
        assert result is False
        assert mock_model.connect_called is True
        assert mock_model.is_connected is False
        assert mock_model.status == ModelStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_model_disconnect(self, mock_model):
        """Test model disconnection"""
        # First connect
        await mock_model.connect()
        assert mock_model.is_connected is True
        
        # Then disconnect
        result = await mock_model.disconnect()
        
        assert result is True
        assert mock_model.disconnect_called is True
        assert mock_model.is_connected is False
        assert mock_model.status == ModelStatus.MAINTENANCE
    
    @pytest.mark.asyncio
    async def test_model_cleanup(self, mock_model):
        """Test model cleanup"""
        await mock_model.connect()
        await mock_model.cleanup()
        
        assert mock_model.disconnect_called is True
        assert mock_model.is_connected is False
    
    @pytest.mark.asyncio
    async def test_model_process_success(self, mock_model):
        """Test successful model processing"""
        test_data = {"input": "test"}
        test_kwargs = {"param1": "value1", "param2": 42}
        
        result = await mock_model.process(test_data, **test_kwargs)
        
        assert mock_model.process_called is True
        assert result["processed"] == test_data
        assert result["kwargs"] == test_kwargs
    
    @pytest.mark.asyncio
    async def test_model_process_failure(self, mock_model):
        """Test failed model processing"""
        mock_model.should_fail_process = True
        
        with pytest.raises(ModelError) as exc_info:
            await mock_model.process({"input": "test"})
        
        assert "Mock processing error" in str(exc_info.value)
        assert mock_model.process_called is True
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_model):
        """Test health check with healthy model"""
        await mock_model.connect()
        
        health = await mock_model.health_check()
        
        assert health["model_name"] == "mock_model"
        assert health["status"] == ModelStatus.READY.value
        assert health["is_connected"] is True
        assert "memory_usage_mb" in health
        assert "success_rate" in health
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_health_check_error(self, mock_model):
        """Test health check with error handling"""
        # Mock an error in health check
        with patch.object(mock_model, 'model_name', side_effect=Exception("Test error")):
            health = await mock_model.health_check()
        
        assert health["status"] == "error"
        assert "Test error" in health["error"]
        assert "timestamp" in health
    
    def test_update_metrics_success(self, mock_model):
        """Test updating metrics for successful operation"""
        initial_time = mock_model.metrics.total_requests
        
        mock_model.update_metrics(success=True, response_time=0.5)
        
        assert mock_model.metrics.total_requests == initial_time + 1
        assert mock_model.metrics.successful_requests == 1
        assert mock_model.metrics.failed_requests == 0
        assert mock_model.metrics.average_response_time == 0.5
        assert mock_model.metrics.error_rate == 0.0
        assert mock_model.metrics.last_used is not None
    
    def test_update_metrics_failure(self, mock_model):
        """Test updating metrics for failed operation"""
        mock_model.update_metrics(success=False, response_time=1.0)
        
        assert mock_model.metrics.total_requests == 1
        assert mock_model.metrics.successful_requests == 0
        assert mock_model.metrics.failed_requests == 1
        assert mock_model.metrics.average_response_time == 1.0
        assert mock_model.metrics.error_rate == 100.0
    
    def test_update_metrics_multiple_operations(self, mock_model):
        """Test updating metrics over multiple operations"""
        # First operation (success)
        mock_model.update_metrics(success=True, response_time=0.5)
        # Second operation (failure)
        mock_model.update_metrics(success=False, response_time=1.5)
        # Third operation (success)
        mock_model.update_metrics(success=True, response_time=0.3)
        
        assert mock_model.metrics.total_requests == 3
        assert mock_model.metrics.successful_requests == 2
        assert mock_model.metrics.failed_requests == 1
        assert abs(mock_model.metrics.average_response_time - 0.767) < 0.01  # (0.5+1.5+0.3)/3
        assert abs(mock_model.metrics.error_rate - 33.33) < 0.01  # 1/3 * 100
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, mock_model):
        """Test getting model metrics"""
        metrics = await mock_model.get_metrics()
        
        assert isinstance(metrics, ModelMetrics)
        assert metrics.model_name == "mock_model"
        assert metrics.total_requests == 0
    
    @pytest.mark.asyncio
    async def test_reset_metrics(self, mock_model):
        """Test resetting model metrics"""
        # Add some metrics
        mock_model.update_metrics(success=True, response_time=0.5)
        assert mock_model.metrics.total_requests == 1
        
        # Reset metrics
        await mock_model.reset_metrics()
        
        assert mock_model.metrics.total_requests == 0
        assert mock_model.metrics.successful_requests == 0
        assert mock_model.metrics.failed_requests == 0
    
    def test_string_representations(self, mock_model):
        """Test string representations of the model"""
        str_repr = str(mock_model)
        repr_repr = repr(mock_model)
        
        assert "MockAIModel" in str_repr
        assert "mock_model" in str_repr
        assert "audio_model" in str_repr
        assert str_repr == repr_repr


class TestSpecializedModels:
    """Test suite for specialized model classes"""
    
    def test_audio_model_creation_valid(self):
        """Test creating valid AudioModel"""
        config = ModelConfig(
            name="audio_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = AudioModel(config)
        assert isinstance(model, AudioModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.AUDIO_MODEL
    
    def test_audio_model_creation_invalid_type(self):
        """Test creating AudioModel with invalid type"""
        config = ModelConfig(
            name="invalid_audio",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.VIDEO_MODEL  # Wrong type
        )
        
        with pytest.raises(ValidationError) as exc_info:
            AudioModel(config)
        assert "AudioModel requires AUDIO_MODEL type" in str(exc_info.value)
    
    def test_video_model_creation_valid(self):
        """Test creating valid VideoModel"""
        config = ModelConfig(
            name="video_test",
            provider=ModelProvider.GPU,
            model_type=ModelType.VIDEO_MODEL
        )
        
        model = VideoModel(config)
        assert isinstance(model, VideoModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.VIDEO_MODEL
    
    def test_video_model_creation_invalid_type(self):
        """Test creating VideoModel with invalid type"""
        config = ModelConfig(
            name="invalid_video",
            provider=ModelProvider.GPU,
            model_type=ModelType.IMAGE_MODEL  # Wrong type
        )
        
        with pytest.raises(ValidationError) as exc_info:
            VideoModel(config)
        assert "VideoModel requires VIDEO_MODEL type" in str(exc_info.value)
    
    def test_image_model_creation_valid(self):
        """Test creating valid ImageModel"""
        config = ModelConfig(
            name="image_test",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.IMAGE_MODEL
        )
        
        model = ImageModel(config)
        assert isinstance(model, ImageModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.IMAGE_MODEL
    
    def test_image_model_creation_invalid_type(self):
        """Test creating ImageModel with invalid type"""
        config = ModelConfig(
            name="invalid_image",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.TEXT_MODEL  # Wrong type
        )
        
        with pytest.raises(ValidationError) as exc_info:
            ImageModel(config)
        assert "ImageModel requires IMAGE_MODEL type" in str(exc_info.value)
    
    def test_text_model_creation_valid_text_type(self):
        """Test creating valid TextModel with TEXT_MODEL type"""
        config = ModelConfig(
            name="text_test",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.TEXT_MODEL
        )
        
        model = TextModel(config)
        assert isinstance(model, TextModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.TEXT_MODEL
    
    def test_text_model_creation_valid_generation_type(self):
        """Test creating valid TextModel with TEXT_GENERATION type"""
        config = ModelConfig(
            name="generation_test",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.TEXT_GENERATION
        )
        
        model = TextModel(config)
        assert isinstance(model, TextModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.TEXT_GENERATION
    
    def test_text_model_creation_invalid_type(self):
        """Test creating TextModel with invalid type"""
        config = ModelConfig(
            name="invalid_text",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.AUDIO_MODEL  # Wrong type
        )
        
        with pytest.raises(ValidationError) as exc_info:
            TextModel(config)
        assert "TextModel requires TEXT_MODEL or TEXT_GENERATION type" in str(exc_info.value)
    
    def test_protection_model_creation_valid(self):
        """Test creating valid ProtectionModel"""
        config = ModelConfig(
            name="protection_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.PROTECTION_MODEL
        )
        
        model = ProtectionModel(config)
        assert isinstance(model, ProtectionModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.PROTECTION_MODEL
    
    def test_protection_model_creation_invalid_type(self):
        """Test creating ProtectionModel with invalid type"""
        config = ModelConfig(
            name="invalid_protection",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.BUSINESS_INTELLIGENCE  # Wrong type
        )
        
        with pytest.raises(ValidationError) as exc_info:
            ProtectionModel(config)
        assert "ProtectionModel requires PROTECTION_MODEL type" in str(exc_info.value)
    
    def test_business_intelligence_model_creation_valid(self):
        """Test creating valid BusinessIntelligenceModel"""
        config = ModelConfig(
            name="bi_test",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.BUSINESS_INTELLIGENCE
        )
        
        model = BusinessIntelligenceModel(config)
        assert isinstance(model, BusinessIntelligenceModel)
        assert isinstance(model, BaseAIModel)
        assert model.model_type == ModelType.BUSINESS_INTELLIGENCE
    
    def test_business_intelligence_model_creation_invalid_type(self):
        """Test creating BusinessIntelligenceModel with invalid type"""
        config = ModelConfig(
            name="invalid_bi",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.MULTIMODAL  # Wrong type
        )
        
        with pytest.raises(ValidationError) as exc_info:
            BusinessIntelligenceModel(config)
        assert "BusinessIntelligenceModel requires BUSINESS_INTELLIGENCE type" in str(exc_info.value)


class TestFactoryFunctions:
    """Test suite for model factory functions"""
    
    def test_create_audio_model(self):
        """Test create_audio_model factory function"""
        config = ModelConfig(
            name="factory_audio",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = create_audio_model(config)
        assert isinstance(model, AudioModel)
        assert model.model_name == "factory_audio"
    
    def test_create_video_model(self):
        """Test create_video_model factory function"""
        config = ModelConfig(
            name="factory_video",
            provider=ModelProvider.GPU,
            model_type=ModelType.VIDEO_MODEL
        )
        
        model = create_video_model(config)
        assert isinstance(model, VideoModel)
        assert model.model_name == "factory_video"
    
    def test_create_image_model(self):
        """Test create_image_model factory function"""
        config = ModelConfig(
            name="factory_image",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.IMAGE_MODEL
        )
        
        model = create_image_model(config)
        assert isinstance(model, ImageModel)
        assert model.model_name == "factory_image"
    
    def test_create_text_model(self):
        """Test create_text_model factory function"""
        config = ModelConfig(
            name="factory_text",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.TEXT_MODEL
        )
        
        model = create_text_model(config)
        assert isinstance(model, TextModel)
        assert model.model_name == "factory_text"
    
    def test_create_protection_model(self):
        """Test create_protection_model factory function"""
        config = ModelConfig(
            name="factory_protection",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.PROTECTION_MODEL
        )
        
        model = create_protection_model(config)
        assert isinstance(model, ProtectionModel)
        assert model.model_name == "factory_protection"
    
    def test_create_business_intelligence_model(self):
        """Test create_business_intelligence_model factory function"""
        config = ModelConfig(
            name="factory_bi",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.BUSINESS_INTELLIGENCE
        )
        
        model = create_business_intelligence_model(config)
        assert isinstance(model, BusinessIntelligenceModel)
        assert model.model_name == "factory_bi"
    
    @pytest.mark.asyncio
    async def test_create_model_audio(self):
        """Test create_model function for audio model"""
        config = ModelConfig(
            name="generic_audio",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = await create_model(config)
        assert isinstance(model, AudioModel)
        assert model.model_name == "generic_audio"
    
    @pytest.mark.asyncio
    async def test_create_model_video(self):
        """Test create_model function for video model"""
        config = ModelConfig(
            name="generic_video",
            provider=ModelProvider.GPU,
            model_type=ModelType.VIDEO_MODEL
        )
        
        model = await create_model(config)
        assert isinstance(model, VideoModel)
        assert model.model_name == "generic_video"
    
    @pytest.mark.asyncio
    async def test_create_model_text_generation(self):
        """Test create_model function for text generation model"""
        config = ModelConfig(
            name="generic_text_gen",
            provider=ModelProvider.CLOUD,
            model_type=ModelType.TEXT_GENERATION
        )
        
        model = await create_model(config)
        assert isinstance(model, TextModel)
        assert model.model_name == "generic_text_gen"
    
    @pytest.mark.asyncio
    async def test_create_model_unsupported_type(self):
        """Test create_model function with unsupported type"""
        config = ModelConfig(
            name="unsupported",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.MULTIMODAL  # Not in registry
        )
        
        with pytest.raises(ModelError) as exc_info:
            await create_model(config)
        assert "Unsupported model type" in str(exc_info.value)


class TestModelRegistry:
    """Test suite for MODEL_REGISTRY"""
    
    def test_model_registry_completeness(self):
        """Test that MODEL_REGISTRY contains all expected model types"""
        expected_types = {
            ModelType.AUDIO_MODEL,
            ModelType.VIDEO_MODEL,
            ModelType.IMAGE_MODEL,
            ModelType.TEXT_MODEL,
            ModelType.TEXT_GENERATION,
            ModelType.PROTECTION_MODEL,
            ModelType.BUSINESS_INTELLIGENCE
        }
        
        registry_types = set(MODEL_REGISTRY.keys())
        assert registry_types == expected_types
    
    def test_model_registry_factory_functions(self):
        """Test that MODEL_REGISTRY contains correct factory functions"""
        assert MODEL_REGISTRY[ModelType.AUDIO_MODEL] == create_audio_model
        assert MODEL_REGISTRY[ModelType.VIDEO_MODEL] == create_video_model
        assert MODEL_REGISTRY[ModelType.IMAGE_MODEL] == create_image_model
        assert MODEL_REGISTRY[ModelType.TEXT_MODEL] == create_text_model
        assert MODEL_REGISTRY[ModelType.TEXT_GENERATION] == create_text_model
        assert MODEL_REGISTRY[ModelType.PROTECTION_MODEL] == create_protection_model
        assert MODEL_REGISTRY[ModelType.BUSINESS_INTELLIGENCE] == create_business_intelligence_model


class TestEnums:
    """Test suite for enum classes"""
    
    def test_model_type_enum_values(self):
        """Test ModelType enum has expected values"""
        expected_values = {
            "audio_model",
            "video_model",
            "image_model",
            "text_model",
            "text_generation",
            "protection_model",
            "business_intelligence",
            "multimodal"
        }
        
        actual_values = {item.value for item in ModelType}
        assert actual_values == expected_values
    
    def test_model_provider_enum_values(self):
        """Test ModelProvider enum has expected values"""
        expected_values = {
            "local",
            "cloud",
            "gpu",
            "edge",
            "hybrid"
        }
        
        actual_values = {item.value for item in ModelProvider}
        assert actual_values == expected_values
    
    def test_model_status_enum_values(self):
        """Test ModelStatus enum has expected values"""
        expected_values = {
            "initializing",
            "ready",
            "loading",
            "processing",
            "error",
            "maintenance"
        }
        
        actual_values = {item.value for item in ModelStatus}
        assert actual_values == expected_values


class TestIntegrationScenarios:
    """Integration test scenarios for base models"""
    
    @pytest.mark.asyncio
    async def test_full_model_lifecycle(self):
        """Test complete model lifecycle"""
        config = ModelConfig(
            name="lifecycle_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL,
            timeout=60,
            max_memory_mb=2048
        )
        
        # Create model
        model = MockAIModel(config)
        assert model.status == ModelStatus.INITIALIZING
        
        # Connect model
        connected = await model.connect()
        assert connected is True
        assert model.status == ModelStatus.READY
        assert model.is_connected is True
        
        # Process data
        test_data = {"audio": "sample_data"}
        result = await model.process(test_data, param="value")
        assert result["processed"] == test_data
        assert result["kwargs"]["param"] == "value"
        
        # Check health
        health = await model.health_check()
        assert health["status"] == ModelStatus.READY.value
        assert health["is_connected"] is True
        
        # Update metrics
        model.update_metrics(success=True, response_time=0.1)
        assert model.metrics.total_requests == 1
        assert model.metrics.successful_requests == 1
        
        # Cleanup
        await model.cleanup()
        assert model.is_connected is False
    
    @pytest.mark.asyncio
    async def test_error_handling_scenario(self):
        """Test error handling throughout model lifecycle"""
        config = ModelConfig(
            name="error_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = MockAIModel(config)
        
        # Test connection failure
        model.should_fail_connect = True
        connected = await model.connect()
        assert connected is False
        assert model.status == ModelStatus.ERROR
        
        # Test processing failure
        model.should_fail_connect = False
        model.should_fail_process = True
        await model.connect()
        
        with pytest.raises(ModelError):
            await model.process({"data": "test"})
        
        # Update metrics for failure
        model.update_metrics(success=False, response_time=1.0)
        assert model.metrics.failed_requests == 1
        assert model.metrics.error_rate == 100.0
    
    @pytest.mark.asyncio
    async def test_concurrent_model_operations(self):
        """Test concurrent operations on model"""
        config = ModelConfig(
            name="concurrent_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = MockAIModel(config)
        await model.connect()
        
        # Run multiple concurrent operations
        tasks = []
        for i in range(10):
            task = model.process({"data": f"test_{i}"})
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Verify all results
        assert len(results) == 10
        for i, result in enumerate(results):
            assert result["processed"]["data"] == f"test_{i}"
        
        # Update metrics for all operations
        for _ in range(10):
            model.update_metrics(success=True, response_time=0.05)
        
        assert model.metrics.total_requests == 10
        assert model.metrics.successful_requests == 10
        assert model.metrics.error_rate == 0.0


class TestPerformanceMetrics:
    """Performance and benchmark tests for base models"""
    
    @pytest.mark.asyncio
    async def test_model_creation_performance(self):
        """Test performance of model creation"""
        start_time = datetime.now()
        
        configs = []
        for i in range(100):
            config = ModelConfig(
                name=f"perf_test_{i}",
                provider=ModelProvider.LOCAL,
                model_type=ModelType.AUDIO_MODEL
            )
            configs.append(config)
        
        models = []
        for config in configs:
            model = MockAIModel(config)
            models.append(model)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should create 100 models in under 1 second
        assert duration < 1.0
        assert len(models) == 100
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test performance of concurrent health checks"""
        config = ModelConfig(
            name="health_perf_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = MockAIModel(config)
        await model.connect()
        
        start_time = datetime.now()
        
        # Run 50 concurrent health checks
        health_tasks = [model.health_check() for _ in range(50)]
        health_results = await asyncio.gather(*health_tasks)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete 50 health checks in under 1 second
        assert duration < 1.0
        assert len(health_results) == 50
        assert all(health["model_name"] == "health_perf_test" for health in health_results)
    
    def test_metrics_update_performance(self):
        """Test performance of metrics updates"""
        config = ModelConfig(
            name="metrics_perf_test",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.AUDIO_MODEL
        )
        
        model = MockAIModel(config)
        
        start_time = datetime.now()
        
        # Update metrics 1000 times
        for i in range(1000):
            success = i % 10 != 0  # 90% success rate
            response_time = 0.1 + (i % 5) * 0.05  # Varying response times
            model.update_metrics(success=success, response_time=response_time)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should update 1000 metrics in under 0.1 seconds
        assert duration < 0.1
        assert model.metrics.total_requests == 1000
        assert model.metrics.successful_requests == 900  # 90%
        assert model.metrics.failed_requests == 100  # 10%
        assert abs(model.metrics.error_rate - 10.0) < 0.1


@pytest.mark.asyncio
async def test_module_imports():
    """Test that all module imports work correctly"""
    # Test all required classes are importable
    assert BaseAIModel is not None
    assert AudioModel is not None
    assert VideoModel is not None
    assert ImageModel is not None
    assert TextModel is not None
    assert ProtectionModel is not None
    assert BusinessIntelligenceModel is not None
    assert ModelConfig is not None
    assert ModelMetrics is not None
    assert ProcessingResult is not None
    
    # Test enums
    assert ModelType is not None
    assert ModelProvider is not None
    assert ModelStatus is not None
    
    # Test factory functions
    assert create_model is not None
    assert create_audio_model is not None
    assert create_video_model is not None
    assert create_image_model is not None
    assert create_text_model is not None
    assert create_protection_model is not None
    assert create_business_intelligence_model is not None
    
    # Test registry
    assert MODEL_REGISTRY is not None
    assert len(MODEL_REGISTRY) > 0


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=backend.ai.core.base_models",
        "--cov-report=term-missing"
    ])
