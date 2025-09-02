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
Comprehensive Test Suite for Base Neural Networks

Ultra-advanced industrial-grade tests for all base neural network functionality,
covering all scenarios, edge cases, performance, security, and business logic.

🎯 Expert Development Team:
✅ Lead Dev + AI Architect Developer
✅ Senior Backend Developer (Python/FastAPI/Django)  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Backend Security Specialist
✅ Microservices Architect
✅ Audio Developer
✅ DevOps Engineer
✅ AI Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import tempfile
import shutil
from pathlib import Path
import json
import time
import psutil
import threading
from unittest.mock import patch, MagicMock
from datetime import datetime

from ai.neural_networks.base_networks import (
    BaseNeuralNetwork,
    NetworkConfig,
    TrainingConfig,
    NetworkType,
    DeviceType,
    ModelRegistry,
    InferenceEngine
)


class TestNetworkImplementation(BaseNeuralNetwork):
    """
Test implementation of BaseNeuralNetwork for testing"""
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Simple feedforward architecture for testing
        layers = []
        input_dim = config.input_dim
        
        for hidden_dim in config.hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            if config.use_dropout:
                layers.append(nn.Dropout(config.dropout_rate))
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, config.output_dim))
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """
Initialize network weights"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        try:
            logger.info(f"Executing forward")
            
            # Implementation for forward
            # TODO: Add specific business logic here
        try:
                    # Request validation
                    if not predictions:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_compute_loss_request(predictions)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler compute_loss failed: {e}")
                    return {"status": "error", "message": str(e)}
            logger.info(f"forward completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"forward failed: {e}")
            raise
    def compute_loss(
        self, 
        predictions: torch.Tensor, 
        targets: torch.Tensor
    ) -> torch.Tensor:
        if self.config.output_dim == 1:
            # Regression
            return nn.MSELoss()(predictions.squeeze(), targets.float())
        else:
            # Classification
            return nn.CrossEntropyLoss()(predictions, targets.long())


@pytest.fixture(scope="session")
def temp_model_directory():
    """Create temporary directory for model testing"""
    temp_dir = tempfile.mkdtemp(prefix="neural_networks_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def basic_network_config():
    """Basic network configuration for testing"""
    return NetworkConfig(
        input_dim=100,
        hidden_dims=[64, 32],
        output_dim=10,
        network_type=NetworkType.CNN,
        learning_rate=0.001,
        batch_size=16,
        epochs=5,
        dropout_rate=0.1
    )


@pytest.fixture
def regression_network_config():
    """
Regression network configuration"""
    return NetworkConfig(
        input_dim=50,
        hidden_dims=[32, 16],
        output_dim=1,
        network_type=NetworkType.CNN,
        learning_rate=0.01,
        batch_size=32,
        epochs=10
    )


@pytest.fixture
def training_config():
    """
Training configuration for tests"""
    return TrainingConfig(
        train_split=0.7,
        validation_split=0.15,
        test_split=0.15,
        optimizer="adamw",
        scheduler="cosine_annealing",
        early_stopping_patience=3,
        log_interval=10,
        validation_interval=50
    )


@pytest.fixture
def sample_data():
    """Generate sample training data"""
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Classification data
    X_class = torch.randn(1000, 100)
    y_class = torch.randint(0, 10, (1000,))
    
    # Regression data
    X_reg = torch.randn(500, 50)
    y_reg = torch.randn(500)
    
    return {
        "classification": (X_class, y_class),
        "regression": (X_reg, y_reg)
    }


@pytest.fixture
def model_registry(temp_model_directory):
    """Create model registry for testing"""
    return ModelRegistry(temp_model_directory / "registry")


class TestNetworkConfig:
    """Test NetworkConfig functionality"""
    
    def test_config_creation(self):
        """
Test basic config creation"""
        config = NetworkConfig(
            input_dim=128,
            hidden_dims=[64, 32],
            output_dim=10,
            network_type=NetworkType.TRANSFORMER
        )
        
        assert config.input_dim == 128
        assert config.hidden_dims == [64, 32]
        assert config.output_dim == 10
        assert config.network_type == NetworkType.TRANSFORMER
        assert config.learning_rate == 0.001  # Default value
        assert config.batch_size == 32  # Default value
    
    def test_config_validation(self):
        """
Test config parameter validation"""
        # Valid config
        valid_config = NetworkConfig(
            input_dim=100,
            hidden_dims=[50, 25],
            output_dim=5,
            network_type=NetworkType.CNN,
            learning_rate=0.01,
            dropout_rate=0.2
        )
        assert valid_config.learning_rate == 0.01
        assert valid_config.dropout_rate == 0.2
    
    def test_device_type_enum(self):
        """
Test DeviceType enum functionality"""
        assert DeviceType.CPU.value == "cpu"
        assert DeviceType.CUDA.value == "cuda"
        assert DeviceType.MPS.value == "mps"
    
    def test_network_type_enum(self):
        """Test NetworkType enum functionality"""
        assert NetworkType.TRANSFORMER.value == "transformer"
        assert NetworkType.CNN.value == "convolutional"
        assert NetworkType.RNN.value == "recurrent"
        assert NetworkType.GAN.value == "generative_adversarial"


class TestTrainingConfig:
    """Test TrainingConfig functionality"""
    
    def test_training_config_creation(self):
        """
Test training config creation with defaults"""
        config = TrainingConfig()
        
        assert config.train_split == 0.8
        assert config.validation_split == 0.1
        assert config.test_split == 0.1
        assert config.optimizer == "adamw"
        assert config.scheduler == "cosine_annealing"
        assert config.early_stopping_patience == 10
    
    def test_training_config_custom(self):
        """Test custom training configuration"""
        config = TrainingConfig(
            train_split=0.7,
            validation_split=0.2,
            test_split=0.1,
            optimizer="sgd",
            scheduler="step",
            early_stopping_patience=5,
            use_data_augmentation=True,
            use_amp=False
        )
        
        assert config.train_split == 0.7
        assert config.validation_split == 0.2
        assert config.test_split == 0.1
        assert config.optimizer == "sgd"
        assert config.scheduler == "step"
        assert config.early_stopping_patience == 5
        assert config.use_data_augmentation is True
        assert config.use_amp is False
    
    def test_split_validation(self):
        """Test that splits sum to approximately 1.0"""
        config = TrainingConfig(
            train_split=0.6,
            validation_split=0.2,
            test_split=0.2
        )
        
        total_split = config.train_split + config.validation_split + config.test_split
        assert abs(total_split - 1.0) < 1e-6


class TestBaseNeuralNetwork:
    """
Test BaseNeuralNetwork functionality"""
    
    def test_network_initialization(self, basic_network_config):
        """
Test basic network initialization"""
        network = TestNetworkImplementation(basic_network_config)
        
        assert network.config == basic_network_config
        assert network.name == "BaseNetwork"
        assert hasattr(network, 'device')
        assert hasattr(network, 'training_history')
        assert hasattr(network, 'metrics')
        assert network.model_version == "1.0.0"
        assert isinstance(network.created_at, datetime)
    
    def test_device_selection(self, basic_network_config):
        try:
            logger.info(f"Executing test_forward_pass")
            
            # Implementation for test_forward_pass
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_forward_pass completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_forward_pass failed: {e}")
            raise
        if torch.cuda.is_available():
            assert network.device.type == "cuda"
        elif torch.backends.mps.is_available():
            assert network.device.type == "mps"  
        else:
            assert network.device.type == "cpu"
    
    def test_forward_pass(self, basic_network_config, sample_data):
        """Test forward pass functionality"""
        network = TestNetworkImplementation(basic_network_config)
        network.eval()
        
        X, _ = sample_data["classification"]
        batch = X[:16]  # Use batch size from config
        
        with torch.no_grad():
            output = network.forward(batch)
        
        assert output.shape[0] == 16  # Batch size
        assert output.shape[1] == basic_network_config.output_dim
        assert torch.isfinite(output).all()
    
    def test_loss_computation_classification(self, basic_network_config, sample_data):
        """Test loss computation for classification"""
        network = TestNetworkImplementation(basic_network_config)
        network.eval()
        
        X, y = sample_data["classification"]
        batch_X, batch_y = X[:16], y[:16]
        
        with torch.no_grad():
            predictions = network.forward(batch_X)
            loss = network.compute_loss(predictions, batch_y)
        
        assert torch.isscalar(loss)
        assert loss.item() >= 0
        assert torch.isfinite(loss)
    
    def test_loss_computation_regression(self, regression_network_config, sample_data):
        """Test loss computation for regression"""
        network = TestNetworkImplementation(regression_network_config)
        network.eval()
        
        X, y = sample_data["regression"]
        batch_X, batch_y = X[:32], y[:32]
        
        with torch.no_grad():
            predictions = network.forward(batch_X)
            loss = network.compute_loss(predictions, batch_y)
        
        assert torch.isscalar(loss)
        assert loss.item() >= 0
        assert torch.isfinite(loss)
    
    def test_accuracy_computation_classification(self, basic_network_config, sample_data):
        """Test accuracy computation for classification"""
        network = TestNetworkImplementation(basic_network_config)
        
        X, y = sample_data["classification"]
        batch_X, batch_y = X[:16], y[:16]
        
        with torch.no_grad():
            predictions = network.forward(batch_X)
            accuracy = network.compute_accuracy(predictions, batch_y)
        
        assert 0.0 <= accuracy <= 1.0
        assert isinstance(accuracy, float)
    
    def test_accuracy_computation_regression(self, regression_network_config, sample_data):
        """Test R² score computation for regression"""
        network = TestNetworkImplementation(regression_network_config)
        
        X, y = sample_data["regression"]
        batch_X, batch_y = X[:32], y[:32]
        
        with torch.no_grad():
            predictions = network.forward(batch_X)
            r_squared = network.compute_accuracy(predictions, batch_y)
        
        # R² can be negative for very poor fits
        assert isinstance(r_squared, float)
        assert torch.isfinite(torch.tensor(r_squared))
    
    def test_optimizer_configuration(self, basic_network_config):
        """Test optimizer configuration"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Test AdamW (default)
        optimizer = network.configure_optimizer()
        assert isinstance(optimizer, optim.AdamW)
        assert optimizer.param_groups[0]['lr'] == basic_network_config.learning_rate
        
        # Test Adam
        basic_network_config.optimizer_type = "adam"
        optimizer = network.configure_optimizer()
        assert isinstance(optimizer, optim.Adam)
        
        # Test SGD
        basic_network_config.optimizer_type = "sgd"
        optimizer = network.configure_optimizer()
        assert isinstance(optimizer, optim.SGD)
        
        # Test invalid optimizer
        basic_network_config.optimizer_type = "invalid"
        with pytest.raises(ValueError):
            network.configure_optimizer()
    
    def test_scheduler_configuration(self, basic_network_config):
        """Test scheduler configuration"""
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        # Test cosine annealing
        scheduler = network.configure_scheduler(optimizer, 1000)
        assert isinstance(scheduler, optim.lr_scheduler.CosineAnnealingLR)
        
        # Test step scheduler
        basic_network_config.scheduler_type = "step"
        scheduler = network.configure_scheduler(optimizer, 1000)
        assert isinstance(scheduler, optim.lr_scheduler.StepLR)
        
        # Test exponential scheduler
        basic_network_config.scheduler_type = "exponential"
        scheduler = network.configure_scheduler(optimizer, 1000)
        assert isinstance(scheduler, optim.lr_scheduler.ExponentialLR)
        
        # Test no scheduler
        basic_network_config.scheduler_type = "none"
        scheduler = network.configure_scheduler(optimizer, 1000)
        assert scheduler is None
    
    def test_training_epoch(self, basic_network_config, sample_data):
        """Test single training epoch"""
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        X, y = sample_data["classification"]
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
        
        initial_loss = float('inf')
        for batch in dataloader:
            with torch.no_grad():
                predictions = network.forward(batch[0])
                initial_loss = network.compute_loss(predictions, batch[1]).item()
            break
        
        # Train one epoch
        metrics = network.train_epoch(dataloader, optimizer)
        
        assert 'loss' in metrics
        assert 'accuracy' in metrics
        assert 'learning_rate' in metrics
        assert isinstance(metrics['loss'], float)
        assert metrics['loss'] >= 0
        assert 0 <= metrics['accuracy'] <= 1
        assert metrics['learning_rate'] > 0
    
    def test_validation(self, basic_network_config, sample_data):
        """Test model validation"""
        network = TestNetworkImplementation(basic_network_config)
        
        X, y = sample_data["classification"]
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=16, shuffle=False)
        
        metrics = network.validate(dataloader)
        
        assert 'validation_loss' in metrics
        assert 'validation_accuracy' in metrics
        assert isinstance(metrics['validation_loss'], float)
        assert metrics['validation_loss'] >= 0
        assert 0 <= metrics['validation_accuracy'] <= 1
    
    def test_model_save_load(self, basic_network_config, temp_model_directory):
        try:
            logger.info(f"Executing test_gradient_clipping")
            
            # Implementation for test_gradient_clipping
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_gradient_clipping completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_gradient_clipping failed: {e}")
            raise
        basic_network_config.gradient_clipping = 1.0
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        X, y = sample_data["classification"]
        batch_X, batch_y = X[:16], y[:16]
        
        # Forward pass
        predictions = network.forward(batch_X)
        loss = network.compute_loss(predictions, batch_y)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Check gradients before clipping
        grad_norms_before = []
        for param in network.parameters():
            if param.grad is not None:
                grad_norms_before.append(param.grad.norm().item())
        
        # Apply gradient clipping
        torch.nn.utils.clip_grad_norm_(network.parameters(), basic_network_config.gradient_clipping)
        
        # Check gradients after clipping
        grad_norms_after = []
        for param in network.parameters():
            if param.grad is not None:
                grad_norms_after.append(param.grad.norm().item())
        
        # At least some gradients should be clipped if they were large
        total_norm = torch.sqrt(sum(norm**2 for norm in grad_norms_after))
        assert total_norm <= basic_network_config.gradient_clipping + 1e-6


class TestModelRegistry:
    """Test ModelRegistry functionality"""
    
    def test_registry_creation(self, temp_model_directory):
        """
Test registry creation"""
        registry_path = temp_model_directory / "test_registry"
        registry = ModelRegistry(registry_path)
        
        assert registry.registry_path.exists()
        assert isinstance(registry.models, dict)
    
    def test_model_registration(self, basic_network_config, temp_model_directory):
        """Test model registration"""
        registry = ModelRegistry(temp_model_directory / "registry")
        network = TestNetworkImplementation(basic_network_config)
        
        # Register model
        registry.register_model(
            name="test_model",
            model=network,
            description="Test model for unit tests",
            tags=["test", "classification"]
        )
        
        # Check registration
        model_info = registry.get_model("test_model")
        assert model_info is not None
        assert model_info["name"] == "test_model"
        assert model_info["description"] == "Test model for unit tests"
        assert "test" in model_info["tags"]
        assert "classification" in model_info["tags"]
        
        # Check model files exist
        model_path = registry.registry_path / "test_model"
        assert model_path.exists()
        assert (model_path / "model.pt").exists()
    
    def test_model_listing(self, basic_network_config, temp_model_directory):
        """Test model listing functionality"""
        registry = ModelRegistry(temp_model_directory / "registry")
        
        # Register multiple models
        for i in range(3):
            network = TestNetworkImplementation(basic_network_config)
            registry.register_model(
                name=f"model_{i}",
                model=network,
                tags=["test", f"model_{i}"]
            )
        
        # Test listing all models
        all_models = registry.list_models()
        assert len(all_models) == 3
        assert "model_0" in all_models
        assert "model_1" in all_models
        assert "model_2" in all_models
        
        # Test filtering by tag
        test_models = registry.list_models(tag="test")
        assert len(test_models) == 3
        
        specific_models = registry.list_models(tag="model_1")
        assert len(specific_models) == 1
        assert "model_1" in specific_models
    
    def test_model_removal(self, basic_network_config, temp_model_directory):
        """Test model removal"""
        registry = ModelRegistry(temp_model_directory / "registry")
        network = TestNetworkImplementation(basic_network_config)
        
        # Register model
        registry.register_model("temp_model", network)
        assert "temp_model" in registry.list_models()
        
        # Remove model
        registry.remove_model("temp_model")
        assert "temp_model" not in registry.list_models()
        assert not (registry.registry_path / "temp_model").exists()


class TestInferenceEngine:
    """Test InferenceEngine functionality"""
    
    def test_engine_creation(self, basic_network_config, sample_data):
        """
Test inference engine creation"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Train network briefly to have meaningful weights
        X, y = sample_data["classification"]
        dataset = TensorDataset(X[:100], y[:100])
        dataloader = DataLoader(dataset, batch_size=16)
        optimizer = network.configure_optimizer()
        
        network.train_epoch(dataloader, optimizer)
        
        # Create inference engine
        engine = InferenceEngine(network, batch_size=8, use_jit=False)  # Disable JIT for testing
        
        assert engine.model == network
        assert engine.batch_size == 8
        assert engine.device == network.device
    
    def test_single_prediction(self, basic_network_config, sample_data):
        """Test single sample prediction"""
        network = TestNetworkImplementation(basic_network_config)
        engine = InferenceEngine(network, use_jit=False)
        
        X, _ = sample_data["classification"]
        sample = X[0]
        
        # Test tensor input
        prediction = engine.predict(sample, return_numpy=True)
        assert isinstance(prediction, np.ndarray)
        assert prediction.shape == (1, basic_network_config.output_dim)
        
        # Test numpy input
        sample_numpy = sample.numpy()
        prediction_numpy = engine.predict(sample_numpy, return_numpy=True)
        assert isinstance(prediction_numpy, np.ndarray)
        assert prediction_numpy.shape == (1, basic_network_config.output_dim)
        
        # Test tensor output
        prediction_tensor = engine.predict(sample, return_numpy=False)
        assert isinstance(prediction_tensor, torch.Tensor)
        assert prediction_tensor.shape == (1, basic_network_config.output_dim)
    
    def test_batch_prediction(self, basic_network_config, sample_data):
        """Test batch prediction"""
        network = TestNetworkImplementation(basic_network_config)
        engine = InferenceEngine(network, use_jit=False)
        
        X, _ = sample_data["classification"]
        batch = X[:50]  # Test with 50 samples
        
        # Test batch prediction with default batch size
        predictions = engine.batch_predict(batch)
        assert isinstance(predictions, np.ndarray)
        assert predictions.shape == (50, basic_network_config.output_dim)
        
        # Test with custom batch size
        predictions_custom = engine.batch_predict(batch, batch_size=16)
        assert predictions_custom.shape == (50, basic_network_config.output_dim)
        
        # Results should be similar regardless of batch size
        np.testing.assert_allclose(predictions, predictions_custom, rtol=1e-5)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_inference(self, basic_network_config, sample_data):
        try:
            logger.info(f"Executing test_forward_pass_performance")
            
            # Implementation for test_forward_pass_performance
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_forward_pass_performance completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_forward_pass_performance failed: {e}")
            raise
        batch = X[:32]
        
        # Warm up
        with torch.no_grad():
            for _ in range(5):
                _ = network.forward(batch)
        
        # Measure performance
        times = []
        with torch.no_grad():
            for _ in range(100):
                start_time = time.time()
                _ = network.forward(batch)
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        
        print(f"Forward pass: {avg_time:.2f}±{std_time:.2f}ms")
        
        # Performance should be reasonable (adjust threshold as needed)
        assert avg_time < 100  # Less than 100ms for this simple network
    
    def test_training_step_performance(self, basic_network_config, sample_data):
        """Test training step performance"""
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        X, y = sample_data["classification"]
        batch_X, batch_y = X[:16], y[:16]
        
        # Warm up
        for _ in range(5):
            optimizer.zero_grad()
            predictions = network.forward(batch_X)
            loss = network.compute_loss(predictions, batch_y)
            loss.backward()
            optimizer.step()
        
        # Measure performance
        times = []
        for _ in range(50):
            start_time = time.time()
            
            optimizer.zero_grad()
            predictions = network.forward(batch_X)
            loss = network.compute_loss(predictions, batch_y)
            loss.backward()
            optimizer.step()
            
            end_time = time.time()
            times.append((end_time - start_time) * 1000)
        
        avg_time = np.mean(times)
        print(f"Training step: {avg_time:.2f}ms")
        
        # Training step should be reasonable
        assert avg_time < 200
    
    def test_memory_usage(self, basic_network_config, sample_data):
        """Test memory usage during training"""
        import gc
        
        # Measure initial memory
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        X, y = sample_data["classification"]
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # Train for a few steps
        for i, (batch_X, batch_y) in enumerate(dataloader):
            if i >= 10:  # Only train for 10 batches
                break
            
            optimizer.zero_grad()
            predictions = network.forward(batch_X)
            loss = network.compute_loss(predictions, batch_y)
            loss.backward()
            optimizer.step()
        
        # Measure final memory
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = final_memory - initial_memory
        print(f"Memory increase: {memory_increase:.1f}MB")
        
        # Memory usage should be reasonable for this small network
        assert memory_increase < 500  # Less than 500MB increase


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_input(self, basic_network_config):
        """
Test behavior with empty input"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Empty tensor should raise appropriate error
        with pytest.raises((RuntimeError, ValueError)):
            empty_input = torch.empty(0, basic_network_config.input_dim)
            network.forward(empty_input)
    
    def test_mismatched_dimensions(self, basic_network_config):
        """
Test behavior with incorrect input dimensions"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Wrong input dimension
        with pytest.raises(RuntimeError):
            wrong_input = torch.randn(16, basic_network_config.input_dim + 10)
            network.forward(wrong_input)
    
    def test_nan_input(self, basic_network_config):
        """
Test behavior with NaN input"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Input with NaN values
        nan_input = torch.randn(16, basic_network_config.input_dim)
        nan_input[0, 0] = float('nan')
        
        output = network.forward(nan_input)
        # Output should contain NaN
        assert torch.isnan(output).any()
    
    def test_infinite_input(self, basic_network_config):
        """
Test behavior with infinite input"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Input with infinite values
        inf_input = torch.randn(16, basic_network_config.input_dim)
        inf_input[0, 0] = float('inf')
        
        output = network.forward(inf_input)
        # Should handle gracefully
        assert output.shape == (16, basic_network_config.output_dim)
    
    def test_extreme_learning_rates(self, basic_network_config, sample_data):
        """
Test with extreme learning rates"""
        X, y = sample_data["classification"]
        batch_X, batch_y = X[:16], y[:16]
        
        # Very high learning rate
        basic_network_config.learning_rate = 100.0
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        # Should handle without crashing (might not converge)
        optimizer.zero_grad()
        predictions = network.forward(batch_X)
        loss = network.compute_loss(predictions, batch_y)
        loss.backward()
        optimizer.step()
        
        # Very low learning rate
        basic_network_config.learning_rate = 1e-10
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        
        # Should handle without crashing
        optimizer.zero_grad()
        predictions = network.forward(batch_X)
        loss = network.compute_loss(predictions, batch_y)
        loss.backward()
        optimizer.step()
    
    def test_zero_batch_size(self, basic_network_config):
        """Test with zero batch size configuration"""
        basic_network_config.batch_size = 0
        
        # Should still create network (batch size is just a config parameter)
        network = TestNetworkImplementation(basic_network_config)
        assert network.config.batch_size == 0


class TestSecurityAndRobustness:
    """
Security and robustness tests"""
    
    def test_model_file_integrity(self, basic_network_config, temp_model_directory):
        """
Test model file integrity checks"""
        network = TestNetworkImplementation(basic_network_config)
        save_path = temp_model_directory / "integrity_test"
        
        # Save model
        network.save_model(save_path)
        
        # Corrupt model file
        model_file = save_path / "model.pt"
        with open(model_file, 'r+b') as f:
            f.seek(10)
            f.write(b'corrupted_data')
        
        # Loading should fail gracefully
        with pytest.raises(Exception):  # Could be various exceptions
            TestNetworkImplementation.load_model(save_path)
    
    def test_adversarial_inputs(self, basic_network_config):
        """Test with adversarial/malicious inputs"""
        network = TestNetworkImplementation(basic_network_config)
        
        # Very large values
        large_input = torch.full(
            (16, basic_network_config.input_dim), 
            1e6
        )
        output = network.forward(large_input)
        assert output.shape == (16, basic_network_config.output_dim)
        
        # Very small values
        small_input = torch.full(
            (16, basic_network_config.input_dim), 
            1e-6
        )
        output = network.forward(small_input)
        assert output.shape == (16, basic_network_config.output_dim)
    
    def test_concurrent_access(self, basic_network_config, sample_data):
        try:
            logger.info(f"Executing run_inference")
            
            # Implementation for run_inference
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"run_inference completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"run_inference failed: {e}")
            raise
        assert output.shape == (16, basic_network_config.output_dim)
    
    def test_concurrent_access(self, basic_network_config, sample_data):
        """
Test concurrent access to model"""
        network = TestNetworkImplementation(basic_network_config)
        network.eval()
        
        X, _ = sample_data["classification"]
        results = []
        exceptions = []
        
        def run_inference(thread_id):
            try:
                batch = X[thread_id*10:(thread_id+1)*10]
                with torch.no_grad():
                    output = network.forward(batch)
                results.append(output)
            except Exception as e:
                exceptions.append(e)
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=run_inference, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should not have exceptions
        assert len(exceptions) == 0
        assert len(results) == 5


class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_end_to_end_training_pipeline(self, basic_network_config, sample_data, temp_model_directory):
        """
Test complete training pipeline"""
        # Setup
        network = TestNetworkImplementation(basic_network_config)
        optimizer = network.configure_optimizer()
        scheduler = network.configure_scheduler(optimizer, 100)
        
        X, y = sample_data["classification"]
        
        # Split data
        train_size = int(0.8 * len(X))
        val_size = len(X) - train_size
        
        train_dataset = TensorDataset(X[:train_size], y[:train_size])
        val_dataset = TensorDataset(X[train_size:], y[train_size:])
        
        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        
        # Training loop
        best_val_loss = float('inf')
        for epoch in range(3):  # Train for 3 epochs
            # Train
            train_metrics = network.train_epoch(train_loader, optimizer, scheduler)
            
            # Validate
            val_metrics = network.validate(val_loader)
            
            # Update metrics
            network.metrics['loss'].append(train_metrics['loss'])
            network.metrics['validation_loss'].append(val_metrics['validation_loss'])
            
            # Early stopping check
            if val_metrics['validation_loss'] < best_val_loss:
                best_val_loss = val_metrics['validation_loss']
        
        # Save model
        model_path = temp_model_directory / "trained_model"
        network.save_model(model_path)
        
        # Load and test
        loaded_network = TestNetworkImplementation.load_model(model_path)
        
        # Test inference
        engine = InferenceEngine(loaded_network, use_jit=False)
        test_input = X[:5]
        predictions = engine.predict(test_input)
        
        assert predictions.shape == (5, basic_network_config.output_dim)
        assert len(loaded_network.metrics['loss']) == 3
    
    def test_model_registry_integration(self, basic_network_config, sample_data, temp_model_directory):
        """Test model registry with training and inference"""
        registry = ModelRegistry(temp_model_directory / "registry")
        
        # Train multiple models
        for i in range(2):
            network = TestNetworkImplementation(basic_network_config)
            
            # Quick training
            X, y = sample_data["classification"]
            dataset = TensorDataset(X[:100], y[:100])
            dataloader = DataLoader(dataset, batch_size=16)
            optimizer = network.configure_optimizer()
            
            train_metrics = network.train_epoch(dataloader, optimizer)
            
            # Register model
            registry.register_model(
                name=f"model_v{i+1}",
                model=network,
                description=f"Version {i+1} of test model",
                tags=["test", "classification", f"v{i+1}"]
            )
        
        # Test registry functionality
        models = registry.list_models()
        assert len(models) == 2
        assert "model_v1" in models
        assert "model_v2" in models
        
        # Test model retrieval and inference
        for model_name in models:
            model_info = registry.get_model(model_name)
            assert model_info is not None
            assert "test" in model_info["tags"]


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
