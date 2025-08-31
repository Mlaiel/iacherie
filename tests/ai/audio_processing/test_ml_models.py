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
🧪 ML Models Tests - Industrial-Grade Machine Learning Testing Suite

Comprehensive testing for ML models and neural networks including:
- MLModelManager validation
- AudioCNN1D/2D testing
- AudioLSTM validation
- AudioTransformer testing
- Model training and inference
- Performance benchmarking

Created by Expert Team: ML Engineer + AI Architect + Backend Senior
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import time
import psutil
import os
import torch
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from sklearn.metrics import accuracy_score, classification_report

# Import the audio processing module
try:
    from ai.audio_processing.ml_models import (
        MLModelManager, AudioCNN1D, AudioCNN2D, AudioLSTM, 
        AudioTransformer, ModelType, ModelArchitecture, 
        ModelConfig, PredictionResult
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.ml_models import (
        MLModelManager, AudioCNN1D, AudioCNN2D, AudioLSTM, 
        AudioTransformer, ModelType, ModelArchitecture, 
        ModelConfig, PredictionResult
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestMLModelManager:
    """
    Industrial-grade testing for MLModelManager class
    
    Test Coverage:
    - Model loading and management
    - Model registry operations
    - Training pipeline coordination
    - Inference optimization
    - Model versioning
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        
        # Create temporary model directory
        self.temp_model_dir = tempfile.mkdtemp()
        self.manager = MLModelManager(model_dir=self.temp_model_dir)
        self.processor = AudioProcessor()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_model_dir):
            shutil.rmtree(self.temp_model_dir)
    
    def test_initialization(self):
        """Test MLModelManager initialization"""
        manager = MLModelManager(model_dir=self.temp_model_dir)
        assert manager is not None
        assert hasattr(manager, 'model_dir')
        assert hasattr(manager, 'models')
        assert hasattr(manager, 'model_configs')
        assert os.path.exists(self.temp_model_dir)
    
    def test_register_model(self):
        """Test model registration"""
        # Create simple test model
        test_model = AudioCNN1D(
            input_channels=1,
            num_classes=10,
            sequence_length=1024
        )
        
        # Register model
        success = self.manager.register_model(
            model_name="test_cnn1d",
            model=test_model,
            model_type=ModelType.GENRE_CLASSIFICATION
        )
        
        assert success is True
        assert "test_cnn1d" in self.manager.models
        assert self.manager.models["test_cnn1d"] == test_model
    
    def test_load_model(self):
        """Test model loading"""
        # Create and register model
        test_model = AudioCNN1D(input_channels=1, num_classes=5)
        self.manager.register_model("test_model", test_model, ModelType.MOOD_DETECTION)
        
        # Load model
        loaded_model = self.manager.load_model("test_model")
        
        assert loaded_model is not None
        assert loaded_model == test_model
        assert isinstance(loaded_model, AudioCNN1D)
    
    def test_save_and_load_model_state(self):
        """Test model state saving and loading"""
        # Create model
        model = AudioCNN1D(input_channels=1, num_classes=3)
        self.manager.register_model("save_test", model, ModelType.INSTRUMENT_RECOGNITION)
        
        # Save model state
        save_path = os.path.join(self.temp_model_dir, "save_test.pth")
        success = self.manager.save_model("save_test", save_path)
        assert success is True
        assert os.path.exists(save_path)
        
        # Create new model and load state
        new_model = AudioCNN1D(input_channels=1, num_classes=3)
        self.manager.register_model("load_test", new_model, ModelType.INSTRUMENT_RECOGNITION)
        
        load_success = self.manager.load_model_state("load_test", save_path)
        assert load_success is True
    
    def test_list_models(self):
        """Test model listing"""
        # Register multiple models
        models = [
            ("model1", AudioCNN1D(input_channels=1, num_classes=5)),
            ("model2", AudioCNN2D(input_channels=1, num_classes=3)),
            ("model3", AudioLSTM(input_size=128, hidden_size=64, num_classes=7))
        ]
        
        for name, model in models:
            self.manager.register_model(name, model, ModelType.GENRE_CLASSIFICATION)
        
        model_list = self.manager.list_models()
        
        assert len(model_list) == len(models)
        for name, _ in models:
            assert name in model_list
    
    def test_get_model_info(self):
        """Test model information retrieval"""
        model = AudioCNN1D(input_channels=1, num_classes=10)
        self.manager.register_model("info_test", model, ModelType.GENRE_CLASSIFICATION)
        
        info = self.manager.get_model_info("info_test")
        
        assert info is not None
        assert isinstance(info, dict)
        assert "model_type" in info
        assert "architecture" in info
        assert "parameters" in info
        assert "created_at" in info
    
    def test_model_prediction(self):
        """Test model prediction through manager"""
        # Create simple model
        model = AudioCNN1D(input_channels=1, num_classes=3)
        self.manager.register_model("pred_test", model, ModelType.MOOD_DETECTION)
        
        # Create sample input
        sample_input = torch.randn(1, 1, 1024)  # Batch, channels, sequence
        
        # Predict
        prediction = self.manager.predict("pred_test", sample_input)
        
        assert prediction is not None
        assert isinstance(prediction, PredictionResult)
        assert prediction.predictions.shape[0] == 1  # Batch size
        assert prediction.predictions.shape[1] == 3  # Number of classes
        assert 0.0 <= prediction.confidence <= 1.0
    
    def test_batch_prediction(self):
        """Test batch prediction"""
        model = AudioCNN1D(input_channels=1, num_classes=5)
        self.manager.register_model("batch_test", model, ModelType.INSTRUMENT_RECOGNITION)
        
        # Create batch input
        batch_size = 8
        batch_input = torch.randn(batch_size, 1, 1024)
        
        # Batch predict
        predictions = self.manager.predict_batch("batch_test", batch_input)
        
        assert predictions is not None
        assert len(predictions) == batch_size
        for pred in predictions:
            assert isinstance(pred, PredictionResult)
            assert pred.predictions.shape[0] == 1  # Individual prediction
            assert pred.predictions.shape[1] == 5  # Number of classes


class TestAudioCNN1D:
    """
    Industrial-grade testing for AudioCNN1D class
    
    Test Coverage:
    - Model architecture validation
    - Forward pass testing
    - Training capability
    - Gradient flow verification
    - Input shape handling
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_initialization(self):
        """Test AudioCNN1D initialization"""
        model = AudioCNN1D(
            input_channels=1,
            num_classes=10,
            sequence_length=1024
        )
        
        assert model is not None
        assert hasattr(model, 'conv_layers')
        assert hasattr(model, 'classifier')
        assert model.num_classes == 10
        assert model.input_channels == 1
    
    def test_forward_pass(self):
        """Test forward pass with various input sizes"""
        model = AudioCNN1D(input_channels=1, num_classes=5, sequence_length=1024)
        
        # Test different batch sizes
        for batch_size in [1, 4, 8]:
            input_tensor = torch.randn(batch_size, 1, 1024)
            output = model(input_tensor)
            
            assert output.shape == (batch_size, 5)  # Batch size, num_classes
            assert not torch.isnan(output).any()
            assert not torch.isinf(output).any()
    
    def test_different_input_channels(self):
        """Test model with different input channels"""
        # Mono audio
        mono_model = AudioCNN1D(input_channels=1, num_classes=3)
        mono_input = torch.randn(2, 1, 1024)
        mono_output = mono_model(mono_input)
        assert mono_output.shape == (2, 3)
        
        # Stereo audio
        stereo_model = AudioCNN1D(input_channels=2, num_classes=3)
        stereo_input = torch.randn(2, 2, 1024)
        stereo_output = stereo_model(stereo_input)
        assert stereo_output.shape == (2, 3)
    
    def test_gradient_flow(self):
        """Test gradient computation"""
        model = AudioCNN1D(input_channels=1, num_classes=3)
        input_tensor = torch.randn(4, 1, 1024, requires_grad=True)
        target = torch.randint(0, 3, (4,))
        
        # Forward pass
        output = model(input_tensor)
        loss = torch.nn.CrossEntropyLoss()(output, target)
        
        # Backward pass
        loss.backward()
        
        # Check gradients exist
        for param in model.parameters():
            assert param.grad is not None
            assert not torch.isnan(param.grad).any()
    
    def test_model_training_mode(self):
        """Test training vs evaluation mode"""
        model = AudioCNN1D(input_channels=1, num_classes=5)
        input_tensor = torch.randn(2, 1, 1024)
        
        # Training mode
        model.train()
        train_output = model(input_tensor)
        
        # Evaluation mode
        model.eval()
        eval_output = model(input_tensor)
        
        # Outputs should be different due to dropout
        assert train_output.shape == eval_output.shape
        # Note: With dropout, outputs may differ between train/eval modes
    
    def test_parameter_count(self):
        """Test parameter count is reasonable"""
        model = AudioCNN1D(input_channels=1, num_classes=10)
        
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        assert total_params > 0
        assert trainable_params == total_params  # All params should be trainable
        assert total_params < 10_000_000  # Should be reasonable size (< 10M params)


class TestAudioCNN2D:
    """
    Industrial-grade testing for AudioCNN2D class
    
    Test Coverage:
    - 2D convolution architecture
    - Spectrogram input handling
    - Multi-scale feature extraction
    - Spatial attention mechanisms
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_initialization(self):
        """Test AudioCNN2D initialization"""
        model = AudioCNN2D(
            input_channels=1,
            num_classes=8,
            input_height=128,
            input_width=128
        )
        
        assert model is not None
        assert hasattr(model, 'conv_layers')
        assert hasattr(model, 'classifier')
        assert model.num_classes == 8
        assert model.input_channels == 1
    
    def test_forward_pass_2d(self):
        """Test forward pass with 2D inputs (spectrograms)"""
        model = AudioCNN2D(
            input_channels=1, 
            num_classes=6,
            input_height=128,
            input_width=128
        )
        
        # Test with spectrogram-like input
        batch_size = 3
        input_tensor = torch.randn(batch_size, 1, 128, 128)
        output = model(input_tensor)
        
        assert output.shape == (batch_size, 6)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
    
    def test_variable_input_sizes(self):
        """Test model with variable input sizes"""
        model = AudioCNN2D(input_channels=1, num_classes=4)
        
        # Test different spectrogram sizes
        sizes = [(64, 64), (128, 128), (256, 128)]
        
        for height, width in sizes:
            input_tensor = torch.randn(2, 1, height, width)
            output = model(input_tensor)
            assert output.shape == (2, 4)
    
    def test_multi_channel_input(self):
        """Test with multi-channel spectrograms"""
        # Multi-channel model (e.g., for mel-spectrograms with different scales)
        model = AudioCNN2D(input_channels=3, num_classes=5)
        
        input_tensor = torch.randn(2, 3, 128, 128)
        output = model(input_tensor)
        
        assert output.shape == (2, 5)
        assert not torch.isnan(output).any()
    
    def test_spatial_pooling(self):
        """Test spatial pooling layers"""
        model = AudioCNN2D(input_channels=1, num_classes=3)
        
        # Large input to test pooling
        large_input = torch.randn(1, 1, 512, 512)
        output = model(large_input)
        
        assert output.shape == (1, 3)  # Should handle large inputs


class TestAudioLSTM:
    """
    Industrial-grade testing for AudioLSTM class
    
    Test Coverage:
    - LSTM architecture validation
    - Sequence processing
    - Hidden state management
    - Bidirectional processing
    - Variable sequence lengths
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_initialization(self):
        """Test AudioLSTM initialization"""
        model = AudioLSTM(
            input_size=128,
            hidden_size=64,
            num_layers=2,
            num_classes=7,
            bidirectional=True
        )
        
        assert model is not None
        assert hasattr(model, 'lstm')
        assert hasattr(model, 'classifier')
        assert model.hidden_size == 64
        assert model.num_layers == 2
        assert model.bidirectional is True
    
    def test_forward_pass_lstm(self):
        """Test LSTM forward pass"""
        model = AudioLSTM(
            input_size=128,
            hidden_size=64,
            num_classes=5
        )
        
        # Test with sequence input (batch, sequence, features)
        batch_size, seq_len, input_size = 4, 100, 128
        input_tensor = torch.randn(batch_size, seq_len, input_size)
        
        output = model(input_tensor)
        
        assert output.shape == (batch_size, 5)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
    
    def test_bidirectional_lstm(self):
        """Test bidirectional LSTM"""
        # Unidirectional
        uni_model = AudioLSTM(
            input_size=64, hidden_size=32, num_classes=3, bidirectional=False
        )
        
        # Bidirectional
        bi_model = AudioLSTM(
            input_size=64, hidden_size=32, num_classes=3, bidirectional=True
        )
        
        input_tensor = torch.randn(2, 50, 64)
        
        uni_output = uni_model(input_tensor)
        bi_output = bi_model(input_tensor)
        
        assert uni_output.shape == (2, 3)
        assert bi_output.shape == (2, 3)
        
        # Bidirectional should have more parameters
        uni_params = sum(p.numel() for p in uni_model.parameters())
        bi_params = sum(p.numel() for p in bi_model.parameters())
        assert bi_params > uni_params
    
    def test_variable_sequence_lengths(self):
        """Test LSTM with variable sequence lengths"""
        model = AudioLSTM(input_size=64, hidden_size=32, num_classes=4)
        
        # Test different sequence lengths
        for seq_len in [25, 50, 100, 200]:
            input_tensor = torch.randn(2, seq_len, 64)
            output = model(input_tensor)
            assert output.shape == (2, 4)
    
    def test_lstm_hidden_state(self):
        """Test LSTM hidden state handling"""
        model = AudioLSTM(input_size=32, hidden_size=16, num_classes=2)
        
        # Test with and without initial hidden state
        input_tensor = torch.randn(3, 30, 32)
        
        # Without initial hidden state
        output1 = model(input_tensor)
        
        # With initial hidden state
        batch_size = 3
        h0 = torch.zeros(model.num_layers, batch_size, model.hidden_size)
        c0 = torch.zeros(model.num_layers, batch_size, model.hidden_size)
        output2 = model(input_tensor, (h0, c0))
        
        assert output1.shape == output2.shape == (3, 2)
    
    def test_lstm_gradient_flow(self):
        """Test LSTM gradient flow"""
        model = AudioLSTM(input_size=32, hidden_size=16, num_classes=3)
        input_tensor = torch.randn(2, 25, 32, requires_grad=True)
        target = torch.randint(0, 3, (2,))
        
        output = model(input_tensor)
        loss = torch.nn.CrossEntropyLoss()(output, target)
        loss.backward()
        
        # Check gradients in LSTM layers
        for name, param in model.named_parameters():
            if param.requires_grad:
                assert param.grad is not None
                assert not torch.isnan(param.grad).any()


class TestAudioTransformer:
    """
    Industrial-grade testing for AudioTransformer class
    
    Test Coverage:
    - Transformer architecture validation
    - Self-attention mechanisms
    - Positional encoding
    - Multi-head attention
    - Sequence modeling capability
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_initialization(self):
        """Test AudioTransformer initialization"""
        model = AudioTransformer(
            input_dim=128,
            model_dim=256,
            num_heads=8,
            num_layers=6,
            num_classes=10
        )
        
        assert model is not None
        assert hasattr(model, 'transformer')
        assert hasattr(model, 'classifier')
        assert hasattr(model, 'positional_encoding')
        assert model.model_dim == 256
        assert model.num_heads == 8
        assert model.num_layers == 6
    
    def test_forward_pass_transformer(self):
        """Test Transformer forward pass"""
        model = AudioTransformer(
            input_dim=64,
            model_dim=128,
            num_heads=4,
            num_layers=2,
            num_classes=5
        )
        
        # Test with sequence input
        batch_size, seq_len, input_dim = 3, 50, 64
        input_tensor = torch.randn(batch_size, seq_len, input_dim)
        
        output = model(input_tensor)
        
        assert output.shape == (batch_size, 5)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
    
    def test_attention_mechanisms(self):
        """Test attention mechanisms"""
        model = AudioTransformer(
            input_dim=32,
            model_dim=64,
            num_heads=2,
            num_layers=1,
            num_classes=3
        )
        
        input_tensor = torch.randn(2, 20, 32)
        
        # Forward pass should work with attention
        output = model(input_tensor)
        assert output.shape == (2, 3)
        
        # Test attention weights (if available)
        if hasattr(model, 'get_attention_weights'):
            attention_weights = model.get_attention_weights(input_tensor)
            assert attention_weights is not None
    
    def test_positional_encoding(self):
        """Test positional encoding"""
        model = AudioTransformer(
            input_dim=64,
            model_dim=128,
            num_heads=4,
            num_layers=2,
            num_classes=4
        )
        
        # Test different sequence lengths
        for seq_len in [10, 50, 100]:
            input_tensor = torch.randn(1, seq_len, 64)
            output = model(input_tensor)
            assert output.shape == (1, 4)
    
    def test_transformer_scalability(self):
        """Test Transformer scalability"""
        # Small model
        small_model = AudioTransformer(
            input_dim=32, model_dim=64, num_heads=2, num_layers=1, num_classes=3
        )
        
        # Large model
        large_model = AudioTransformer(
            input_dim=128, model_dim=512, num_heads=8, num_layers=6, num_classes=10
        )
        
        # Both should work
        small_input = torch.randn(1, 25, 32)
        large_input = torch.randn(1, 100, 128)
        
        small_output = small_model(small_input)
        large_output = large_model(large_input)
        
        assert small_output.shape == (1, 3)
        assert large_output.shape == (1, 10)


class TestModelConfig:
    """Test ModelConfig data structure"""
    
    def test_config_creation(self):
        """Test ModelConfig creation"""
        config = ModelConfig(
            architecture=ModelArchitecture.CNN1D,
            input_dim=128,
            num_classes=10,
            learning_rate=0.001,
            batch_size=32
        )
        
        assert config.architecture == ModelArchitecture.CNN1D
        assert config.input_dim == 128
        assert config.num_classes == 10
        assert config.learning_rate == 0.001
        assert config.batch_size == 32
    
    def test_config_validation(self):
        """Test config validation"""
        # Valid config
        valid_config = ModelConfig(
            architecture=ModelArchitecture.LSTM,
            input_dim=64,
            num_classes=5,
            learning_rate=0.01
        )
        assert valid_config.is_valid()
        
        # Invalid config
        with pytest.raises(ValueError):
            ModelConfig(
                architecture=ModelArchitecture.CNN2D,
                input_dim=-1,  # Invalid
                num_classes=5,
                learning_rate=0.01
            )


class TestPredictionResult:
    """Test PredictionResult data structure"""
    
    def test_prediction_result_creation(self):
        """Test PredictionResult creation"""
        predictions = torch.softmax(torch.randn(1, 5), dim=1)
        
        result = PredictionResult(
            predictions=predictions,
            confidence=0.85,
            predicted_class=2,
            class_probabilities=predictions[0].tolist()
        )
        
        assert torch.equal(result.predictions, predictions)
        assert result.confidence == 0.85
        assert result.predicted_class == 2
        assert len(result.class_probabilities) == 5
    
    def test_prediction_result_methods(self):
        """Test PredictionResult utility methods"""
        predictions = torch.tensor([[0.1, 0.2, 0.6, 0.05, 0.05]])
        
        result = PredictionResult(
            predictions=predictions,
            confidence=0.6,
            predicted_class=2,
            class_probabilities=predictions[0].tolist()
        )
        
        # Test top-k predictions
        if hasattr(result, 'get_top_k'):
            top_k = result.get_top_k(k=3)
            assert len(top_k) == 3
            assert top_k[0][0] == 2  # Highest probability class


class TestMLIntegration:
    """
    Integration tests for ML models workflow
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        
        # Create temporary model directory
        self.temp_model_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_model_dir):
            shutil.rmtree(self.temp_model_dir)
    
    def test_complete_ml_workflow(self):
        """Test complete ML workflow"""
        # Initialize components
        processor = AudioProcessor()
        manager = MLModelManager(model_dir=self.temp_model_dir)
        
        # Create and register model
        model = AudioCNN1D(input_channels=1, num_classes=3)
        manager.register_model("workflow_test", model, ModelType.MOOD_DETECTION)
        
        # Load audio and extract features
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        audio_data, sample_rate = processor.load_audio(str(audio_file))
        
        # Convert to model input format
        # Simulate feature extraction (would normally use real features)
        features = torch.randn(1, 1, 1024)
        
        # Predict
        prediction = manager.predict("workflow_test", features)
        
        # Verify workflow
        assert prediction is not None
        assert isinstance(prediction, PredictionResult)
        assert prediction.predictions.shape == (1, 3)
        assert 0.0 <= prediction.confidence <= 1.0
    
    def test_model_ensemble(self):
        """Test ensemble prediction with multiple models"""
        manager = MLModelManager(model_dir=self.temp_model_dir)
        
        # Create multiple models
        models = [
            ("cnn1d", AudioCNN1D(input_channels=1, num_classes=5)),
            ("cnn2d", AudioCNN2D(input_channels=1, num_classes=5)),
            ("lstm", AudioLSTM(input_size=128, hidden_size=32, num_classes=5))
        ]
        
        for name, model in models:
            manager.register_model(name, model, ModelType.GENRE_CLASSIFICATION)
        
        # Create inputs for each model
        cnn1d_input = torch.randn(1, 1, 1024)
        cnn2d_input = torch.randn(1, 1, 128, 128)
        lstm_input = torch.randn(1, 50, 128)
        
        # Get predictions
        cnn1d_pred = manager.predict("cnn1d", cnn1d_input)
        cnn2d_pred = manager.predict("cnn2d", cnn2d_input)
        lstm_pred = manager.predict("lstm", lstm_input)
        
        # All should produce valid predictions
        for pred in [cnn1d_pred, cnn2d_pred, lstm_pred]:
            assert pred is not None
            assert pred.predictions.shape[1] == 5  # 5 classes
    
    def test_model_performance_benchmarking(self):
        """Test model performance benchmarking"""
        # Test different model architectures
        models = [
            ("cnn1d_small", AudioCNN1D(input_channels=1, num_classes=3)),
            ("lstm_small", AudioLSTM(input_size=64, hidden_size=16, num_classes=3))
        ]
        
        batch_size = 10
        
        for name, model in models:
            # Measure inference time
            if isinstance(model, AudioCNN1D):
                input_tensor = torch.randn(batch_size, 1, 1024)
            else:  # LSTM
                input_tensor = torch.randn(batch_size, 25, 64)
            
            start_time = time.time()
            with torch.no_grad():
                output = model(input_tensor)
            end_time = time.time()
            
            inference_time_ms = (end_time - start_time) * 1000
            
            assert output.shape[0] == batch_size
            assert inference_time_ms < 1000  # Should be fast (< 1 second)


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
