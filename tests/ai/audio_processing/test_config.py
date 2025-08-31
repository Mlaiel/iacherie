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
 Config Tests - Industrial-Grade Configuration Management Testing Suite

Comprehensive testing for configuration management including:
- ConfigManager validation
- Configuration loading and validation
- Environment-specific configurations
- Configuration merging and inheritance
- Runtime configuration updates

Created by Expert Team: DevOps Engineer + Configuration Specialist + Backend Senior
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import os
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the audio processing module
try:
    from ai.audio_processing.config import (
        AudioProcessingConfig, ConfigurationManager, Environment, LogLevel,
        get_config, set_config, load_config, save_config, get_template,
        create_config_from_template, initialize_config
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from ai.audio_processing.config import (
        AudioProcessingConfig, ConfigurationManager, Environment, LogLevel,
        get_config, set_config, load_config, save_config, get_template,
        create_config_from_template, initialize_config
    )

from . import TEST_CONFIG, setup_test_environment


class TestConfigManager:
    """
    Industrial-grade testing for ConfigManager class
    
    Test Coverage:
    - Configuration initialization
    - Configuration loading from multiple sources
    - Configuration validation
    - Environment-specific overrides
    - Runtime configuration updates
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        
        # Create temporary config directory
        self.temp_config_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(config_dir=self.temp_config_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_config_dir):
            shutil.rmtree(self.temp_config_dir)
    
    def test_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()
        
        assert manager is not None
        assert hasattr(manager, 'configs')
        assert hasattr(manager, 'validators')
        assert hasattr(manager, 'environment')
        assert hasattr(manager, 'config_loader')
    
    def test_load_default_configuration(self):
        """Test loading default configuration"""
        # Load default configuration
        config = self.config_manager.load_default_config()
        
        # Verify default configuration structure
        assert isinstance(config, dict)
        assert "audio" in config
        assert "processing" in config
        assert "ml_models" in config
        assert "quality" in config
        assert "realtime" in config
        assert "security" in config
        assert "performance" in config
        
        # Verify audio configuration
        audio_config = config["audio"]
        assert "sample_rate" in audio_config
        assert "channels" in audio_config
        assert "bit_depth" in audio_config
        assert "supported_formats" in audio_config
        
        # Verify processing configuration
        processing_config = config["processing"]
        assert "buffer_size" in processing_config
        assert "window_size" in processing_config
        assert "overlap_ratio" in processing_config
        assert "enable_preprocessing" in processing_config
    
    def test_load_config_from_file(self):
        """Test loading configuration from file"""
        # Create test configuration file
        test_config = {
            "audio": {
                "sample_rate": 48000,
                "channels": 2,
                "bit_depth": 24
            },
            "processing": {
                "buffer_size": 1024,
                "enable_noise_reduction": True
            }
        }
        
        config_file = os.path.join(self.temp_config_dir, "test_config.json")
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Load configuration from file
        loaded_config = self.config_manager.load_config_from_file(config_file)
        
        # Verify loaded configuration
        assert loaded_config["audio"]["sample_rate"] == 48000
        assert loaded_config["audio"]["channels"] == 2
        assert loaded_config["processing"]["buffer_size"] == 1024
        assert loaded_config["processing"]["enable_noise_reduction"] is True
    
    def test_load_config_from_yaml(self):
        """Test loading configuration from YAML file"""
        # Create test YAML configuration
        yaml_config = """
        audio:
          sample_rate: 44100
          channels: 1
          bit_depth: 16
          supported_formats:
            - wav
            - mp3
            - flac
        
        processing:
          buffer_size: 512
          window_size: 2048
          overlap_ratio: 0.5
          
        ml_models:
          default_model: "cnn1d"
          model_path: "/models"
          cache_models: true
        """
        
        yaml_file = os.path.join(self.temp_config_dir, "test_config.yaml")
        with open(yaml_file, 'w') as f:
            f.write(yaml_config)
        
        # Load YAML configuration
        loaded_config = self.config_manager.load_config_from_file(yaml_file)
        
        # Verify YAML configuration
        assert loaded_config["audio"]["sample_rate"] == 44100
        assert loaded_config["processing"]["overlap_ratio"] == 0.5
        assert "wav" in loaded_config["audio"]["supported_formats"]
        assert loaded_config["ml_models"]["cache_models"] is True
    
    def test_environment_specific_config(self):
        """Test environment-specific configuration loading"""
        # Create base configuration
        base_config = {
            "audio": {"sample_rate": 44100},
            "processing": {"buffer_size": 512}
        }
        
        # Create development environment config
        dev_config = {
            "audio": {"sample_rate": 22050},  # Lower for development
            "processing": {"enable_debug": True}
        }
        
        # Create production environment config
        prod_config = {
            "processing": {"buffer_size": 1024},  # Larger for production
            "performance": {"max_threads": 8}
        }
        
        # Save configurations
        base_file = os.path.join(self.temp_config_dir, "base.json")
        dev_file = os.path.join(self.temp_config_dir, "development.json")
        prod_file = os.path.join(self.temp_config_dir, "production.json")
        
        for config, file_path in [(base_config, base_file), 
                                 (dev_config, dev_file), 
                                 (prod_config, prod_file)]:
            with open(file_path, 'w') as f:
                json.dump(config, f)
        
        # Load development configuration
        dev_merged = self.config_manager.load_environment_config("development", base_file)
        assert dev_merged["audio"]["sample_rate"] == 22050  # Overridden
        assert dev_merged["processing"]["buffer_size"] == 512  # From base
        assert dev_merged["processing"]["enable_debug"] is True  # From dev
        
        # Load production configuration
        prod_merged = self.config_manager.load_environment_config("production", base_file)
        assert prod_merged["audio"]["sample_rate"] == 44100  # From base
        assert prod_merged["processing"]["buffer_size"] == 1024  # Overridden
        assert prod_merged["performance"]["max_threads"] == 8  # From prod
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid configuration
        valid_config = {
            "audio": {
                "sample_rate": 44100,
                "channels": 2,
                "bit_depth": 16
            },
            "processing": {
                "buffer_size": 512,
                "window_size": 2048
            }
        }
        
        # Validate configuration
        validation_result = self.config_manager.validate_config(valid_config)
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0
        
        # Invalid configuration
        invalid_config = {
            "audio": {
                "sample_rate": 0,  # Invalid
                "channels": -1,    # Invalid
                "bit_depth": 7     # Invalid
            },
            "processing": {
                "buffer_size": 0   # Invalid
            }
        }
        
        # Validate invalid configuration
        invalid_result = self.config_manager.validate_config(invalid_config)
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) > 0
        assert any("sample_rate" in error for error in invalid_result.errors)
        assert any("channels" in error for error in invalid_result.errors)
    
    def test_runtime_config_updates(self):
        """Test runtime configuration updates"""
        # Load initial configuration
        initial_config = {
            "processing": {
                "buffer_size": 512,
                "enable_effects": False
            }
        }
        
        self.config_manager.set_config(initial_config)
        
        # Update configuration at runtime
        updates = {
            "processing": {
                "buffer_size": 1024,
                "enable_effects": True,
                "new_parameter": "added"
            }
        }
        
        # Apply updates
        update_result = self.config_manager.update_config(updates)
        assert update_result.success is True
        
        # Verify updates
        current_config = self.config_manager.get_config()
        assert current_config["processing"]["buffer_size"] == 1024
        assert current_config["processing"]["enable_effects"] is True
        assert current_config["processing"]["new_parameter"] == "added"
    
    def test_config_change_notifications(self):
        """Test configuration change notifications"""
        change_notifications = []
        
        def config_change_handler(section, key, old_value, new_value):
            change_notifications.append({
                "section": section,
                "key": key,
                "old_value": old_value,
                "new_value": new_value
            })
        
        # Register change handler
        self.config_manager.add_change_listener(config_change_handler)
        
        # Set initial configuration
        initial_config = {"audio": {"sample_rate": 44100}}
        self.config_manager.set_config(initial_config)
        
        # Update configuration
        self.config_manager.update_config({"audio": {"sample_rate": 48000}})
        
        # Verify notifications
        assert len(change_notifications) > 0
        
        # Find the sample_rate change notification
        sample_rate_change = next(
            (n for n in change_notifications 
             if n["section"] == "audio" and n["key"] == "sample_rate"), 
            None
        )
        
        assert sample_rate_change is not None
        assert sample_rate_change["old_value"] == 44100
        assert sample_rate_change["new_value"] == 48000


class TestAudioConfig:
    """
    Industrial-grade testing for AudioConfig class
    
    Test Coverage:
    - Audio parameter validation
    - Format support validation
    - Quality settings validation
    - Compatibility checks
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_audio_config_creation(self):
        """Test AudioConfig creation and validation"""
        config = AudioConfig(
            sample_rate=44100,
            channels=2,
            bit_depth=16,
            supported_formats=["wav", "mp3", "flac"],
            default_format="wav"
        )
        
        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.bit_depth == 16
        assert "wav" in config.supported_formats
        assert config.default_format == "wav"
    
    def test_sample_rate_validation(self):
        """Test sample rate validation"""
        # Valid sample rates
        valid_rates = [8000, 16000, 22050, 44100, 48000, 96000, 192000]
        
        for rate in valid_rates:
            config = AudioConfig(sample_rate=rate)
            assert config.sample_rate == rate
            assert config.is_valid()
        
        # Invalid sample rates
        invalid_rates = [0, -1, 999, 1000000]
        
        for rate in invalid_rates:
            with pytest.raises(ValueError):
                AudioConfig(sample_rate=rate)
    
    def test_channel_configuration(self):
        """Test channel configuration validation"""
        # Valid channel configurations
        valid_channels = [1, 2, 6, 8]  # Mono, stereo, 5.1, 7.1
        
        for channels in valid_channels:
            config = AudioConfig(channels=channels)
            assert config.channels == channels
        
        # Invalid channel configurations
        invalid_channels = [0, -1, 999]
        
        for channels in invalid_channels:
            with pytest.raises(ValueError):
                AudioConfig(channels=channels)
    
    def test_bit_depth_validation(self):
        """Test bit depth validation"""
        # Valid bit depths
        valid_depths = [8, 16, 24, 32]
        
        for depth in valid_depths:
            config = AudioConfig(bit_depth=depth)
            assert config.bit_depth == depth
        
        # Invalid bit depths
        invalid_depths = [0, 7, 15, 33, 64]
        
        for depth in invalid_depths:
            with pytest.raises(ValueError):
                AudioConfig(bit_depth=depth)
    
    def test_format_support_validation(self):
        """Test format support validation"""
        # Valid formats
        valid_formats = ["wav", "mp3", "flac", "ogg", "aac", "m4a"]
        
        config = AudioConfig(supported_formats=valid_formats)
        assert all(fmt in config.supported_formats for fmt in valid_formats)
        
        # Invalid formats
        invalid_formats = ["unknown", "xyz", ""]
        
        with pytest.raises(ValueError):
            AudioConfig(supported_formats=invalid_formats)
    
    def test_quality_settings(self):
        """Test audio quality settings"""
        # High quality configuration
        high_quality = AudioConfig(
            sample_rate=96000,
            channels=2,
            bit_depth=24,
            quality_preset="high"
        )
        
        assert high_quality.get_quality_score() > 0.8
        
        # Low quality configuration
        low_quality = AudioConfig(
            sample_rate=22050,
            channels=1,
            bit_depth=8,
            quality_preset="low"
        )
        
        assert low_quality.get_quality_score() < 0.5
        assert high_quality.get_quality_score() > low_quality.get_quality_score()


class TestProcessingConfig:
    """
    Industrial-grade testing for ProcessingConfig class
    
    Test Coverage:
    - Processing parameter validation
    - Algorithm configuration
    - Performance settings
    - Feature extraction settings
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_processing_config_creation(self):
        """Test ProcessingConfig creation"""
        config = ProcessingConfig(
            buffer_size=1024,
            window_size=2048,
            overlap_ratio=0.5,
            enable_preprocessing=True,
            enable_noise_reduction=True
        )
        
        assert config.buffer_size == 1024
        assert config.window_size == 2048
        assert config.overlap_ratio == 0.5
        assert config.enable_preprocessing is True
        assert config.enable_noise_reduction is True
    
    def test_buffer_size_validation(self):
        """Test buffer size validation"""
        # Valid buffer sizes (powers of 2)
        valid_sizes = [64, 128, 256, 512, 1024, 2048, 4096]
        
        for size in valid_sizes:
            config = ProcessingConfig(buffer_size=size)
            assert config.buffer_size == size
        
        # Invalid buffer sizes
        invalid_sizes = [0, 63, 129, 1023]
        
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                ProcessingConfig(buffer_size=size)
    
    def test_window_function_validation(self):
        """Test window function validation"""
        # Valid window functions
        valid_windows = ["hann", "hamming", "blackman", "bartlett", "rectangular"]
        
        for window in valid_windows:
            config = ProcessingConfig(window_function=window)
            assert config.window_function == window
        
        # Invalid window function
        with pytest.raises(ValueError):
            ProcessingConfig(window_function="invalid_window")
    
    def test_overlap_ratio_validation(self):
        """Test overlap ratio validation"""
        # Valid overlap ratios
        valid_ratios = [0.0, 0.25, 0.5, 0.75, 0.875]
        
        for ratio in valid_ratios:
            config = ProcessingConfig(overlap_ratio=ratio)
            assert config.overlap_ratio == ratio
        
        # Invalid overlap ratios
        invalid_ratios = [-0.1, 1.0, 1.5]
        
        for ratio in invalid_ratios:
            with pytest.raises(ValueError):
                ProcessingConfig(overlap_ratio=ratio)
    
    def test_feature_extraction_config(self):
        """Test feature extraction configuration"""
        config = ProcessingConfig(
            enable_mfcc=True,
            mfcc_coefficients=13,
            enable_spectral_features=True,
            enable_temporal_features=True,
            feature_normalization="z_score"
        )
        
        assert config.enable_mfcc is True
        assert config.mfcc_coefficients == 13
        assert config.enable_spectral_features is True
        assert config.feature_normalization == "z_score"
        
        # Validate feature extraction settings
        assert config.is_feature_extraction_valid()


class TestMLModelConfig:
    """
    Industrial-grade testing for MLModelConfig class
    
    Test Coverage:
    - Model parameter validation
    - Training configuration
    - Model architecture settings
    - Performance tuning parameters
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_ml_model_config_creation(self):
        """Test MLModelConfig creation"""
        config = MLModelConfig(
            model_type="cnn1d",
            model_path="/models",
            input_dim=128,
            num_classes=10,
            batch_size=32,
            learning_rate=0.001
        )
        
        assert config.model_type == "cnn1d"
        assert config.model_path == "/models"
        assert config.input_dim == 128
        assert config.num_classes == 10
        assert config.batch_size == 32
        assert config.learning_rate == 0.001
    
    def test_model_architecture_validation(self):
        """Test model architecture validation"""
        # Valid architectures
        valid_architectures = ["cnn1d", "cnn2d", "lstm", "transformer", "resnet"]
        
        for arch in valid_architectures:
            config = MLModelConfig(model_type=arch)
            assert config.model_type == arch
            assert config.is_architecture_supported()
        
        # Invalid architecture
        with pytest.raises(ValueError):
            MLModelConfig(model_type="invalid_architecture")
    
    def test_training_parameters_validation(self):
        """Test training parameters validation"""
        # Valid training parameters
        config = MLModelConfig(
            batch_size=32,
            learning_rate=0.001,
            epochs=100,
            validation_split=0.2,
            early_stopping_patience=10
        )
        
        assert config.is_training_config_valid()
        
        # Invalid training parameters
        invalid_configs = [
            {"batch_size": 0},
            {"learning_rate": -0.001},
            {"epochs": 0},
            {"validation_split": 1.5}
        ]
        
        for invalid_params in invalid_configs:
            with pytest.raises(ValueError):
                MLModelConfig(**invalid_params)
    
    def test_hyperparameter_optimization(self):
        """Test hyperparameter optimization configuration"""
        config = MLModelConfig(
            enable_hyperparameter_tuning=True,
            tuning_method="grid_search",
            parameter_ranges={
                "learning_rate": [0.0001, 0.001, 0.01],
                "batch_size": [16, 32, 64],
                "hidden_size": [64, 128, 256]
            }
        )
        
        assert config.enable_hyperparameter_tuning is True
        assert config.tuning_method == "grid_search"
        assert "learning_rate" in config.parameter_ranges
        assert len(config.parameter_ranges["batch_size"]) == 3


class TestSecurityConfig:
    """
    Industrial-grade testing for SecurityConfig class
    
    Test Coverage:
    - Security parameter validation
    - Encryption settings
    - Access control configuration
    - Audit logging settings
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_security_config_creation(self):
        """Test SecurityConfig creation"""
        config = SecurityConfig(
            enable_encryption=True,
            encryption_algorithm="AES-256",
            enable_access_control=True,
            enable_audit_logging=True,
            max_file_size_mb=100
        )
        
        assert config.enable_encryption is True
        assert config.encryption_algorithm == "AES-256"
        assert config.enable_access_control is True
        assert config.enable_audit_logging is True
        assert config.max_file_size_mb == 100
    
    def test_encryption_algorithm_validation(self):
        """Test encryption algorithm validation"""
        # Valid encryption algorithms
        valid_algorithms = ["AES-128", "AES-256", "ChaCha20", "RSA-2048"]
        
        for algorithm in valid_algorithms:
            config = SecurityConfig(encryption_algorithm=algorithm)
            assert config.encryption_algorithm == algorithm
            assert config.is_encryption_secure()
        
        # Invalid encryption algorithm
        with pytest.raises(ValueError):
            SecurityConfig(encryption_algorithm="WEAK_CIPHER")
    
    def test_access_control_validation(self):
        """Test access control validation"""
        config = SecurityConfig(
            enable_access_control=True,
            allowed_users=["user1", "user2"],
            allowed_roles=["admin", "operator"],
            session_timeout_minutes=30
        )
        
        assert config.enable_access_control is True
        assert "user1" in config.allowed_users
        assert "admin" in config.allowed_roles
        assert config.session_timeout_minutes == 30
        assert config.is_access_control_valid()
    
    def test_file_size_limits(self):
        """Test file size limit validation"""
        # Valid file size limits
        valid_limits = [1, 10, 100, 1000]  # MB
        
        for limit in valid_limits:
            config = SecurityConfig(max_file_size_mb=limit)
            assert config.max_file_size_mb == limit
        
        # Invalid file size limits
        invalid_limits = [0, -1, 10000]  # Too small, negative, too large
        
        for limit in invalid_limits:
            with pytest.raises(ValueError):
                SecurityConfig(max_file_size_mb=limit)


class TestPerformanceConfig:
    """
    Industrial-grade testing for PerformanceConfig class
    
    Test Coverage:
    - Performance parameter validation
    - Resource allocation settings
    - Optimization configuration
    - Monitoring settings
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_performance_config_creation(self):
        """Test PerformanceConfig creation"""
        config = PerformanceConfig(
            max_threads=8,
            max_memory_mb=2048,
            enable_gpu_acceleration=True,
            cache_size_mb=512,
            enable_performance_monitoring=True
        )
        
        assert config.max_threads == 8
        assert config.max_memory_mb == 2048
        assert config.enable_gpu_acceleration is True
        assert config.cache_size_mb == 512
        assert config.enable_performance_monitoring is True
    
    def test_thread_count_validation(self):
        """Test thread count validation"""
        import multiprocessing
        
        # Valid thread counts
        cpu_count = multiprocessing.cpu_count()
        valid_counts = [1, 2, 4, cpu_count, cpu_count * 2]
        
        for count in valid_counts:
            if count <= cpu_count * 4:  # Reasonable upper limit
                config = PerformanceConfig(max_threads=count)
                assert config.max_threads == count
        
        # Invalid thread counts
        invalid_counts = [0, -1, cpu_count * 10]
        
        for count in invalid_counts:
            with pytest.raises(ValueError):
                PerformanceConfig(max_threads=count)
    
    def test_memory_limit_validation(self):
        """Test memory limit validation"""
        # Valid memory limits (MB)
        valid_limits = [128, 512, 1024, 2048, 4096]
        
        for limit in valid_limits:
            config = PerformanceConfig(max_memory_mb=limit)
            assert config.max_memory_mb == limit
        
        # Invalid memory limits
        invalid_limits = [0, -1, 1000000]  # Too small, negative, too large
        
        for limit in invalid_limits:
            with pytest.raises(ValueError):
                PerformanceConfig(max_memory_mb=limit)
    
    def test_optimization_settings(self):
        """Test optimization settings"""
        config = PerformanceConfig(
            enable_vectorization=True,
            enable_parallel_processing=True,
            optimization_level="O3",
            enable_profiling=True
        )
        
        assert config.enable_vectorization is True
        assert config.enable_parallel_processing is True
        assert config.optimization_level == "O3"
        assert config.enable_profiling is True
        assert config.is_optimization_valid()


class TestConfigValidator:
    """Test ConfigValidator functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.validator = ConfigValidator()
    
    def test_validation_rules(self):
        """Test validation rules"""
        # Add custom validation rule
        def validate_positive_number(value):
            return isinstance(value, (int, float)) and value > 0
        
        self.validator.add_rule("positive_number", validate_positive_number)
        
        # Test validation
        assert self.validator.validate("positive_number", 5) is True
        assert self.validator.validate("positive_number", -1) is False
        assert self.validator.validate("positive_number", "invalid") is False
    
    def test_schema_validation(self):
        """Test schema-based validation"""
        # Define schema
        schema = {
            "audio": {
                "sample_rate": {"type": "int", "min": 8000, "max": 192000},
                "channels": {"type": "int", "min": 1, "max": 8}
            },
            "processing": {
                "buffer_size": {"type": "int", "power_of_2": True}
            }
        }
        
        self.validator.set_schema(schema)
        
        # Valid configuration
        valid_config = {
            "audio": {"sample_rate": 44100, "channels": 2},
            "processing": {"buffer_size": 1024}
        }
        
        validation_result = self.validator.validate_config(valid_config)
        assert validation_result.is_valid is True
        
        # Invalid configuration
        invalid_config = {
            "audio": {"sample_rate": 999, "channels": 10},
            "processing": {"buffer_size": 1000}  # Not power of 2
        }
        
        invalid_result = self.validator.validate_config(invalid_config)
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) > 0


class TestConfigMerger:
    """Test ConfigMerger functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.merger = ConfigMerger()
    
    def test_simple_merge(self):
        """Test simple configuration merging"""
        base_config = {
            "audio": {"sample_rate": 44100, "channels": 2},
            "processing": {"buffer_size": 512}
        }
        
        override_config = {
            "audio": {"sample_rate": 48000},  # Override
            "ml_models": {"default_model": "cnn1d"}  # Add new
        }
        
        merged = self.merger.merge(base_config, override_config)
        
        # Verify merge results
        assert merged["audio"]["sample_rate"] == 48000  # Overridden
        assert merged["audio"]["channels"] == 2  # Preserved
        assert merged["processing"]["buffer_size"] == 512  # Preserved
        assert merged["ml_models"]["default_model"] == "cnn1d"  # Added
    
    def test_deep_merge(self):
        """Test deep configuration merging"""
        base_config = {
            "nested": {
                "level1": {
                    "level2": {
                        "param1": "value1",
                        "param2": "value2"
                    }
                }
            }
        }
        
        override_config = {
            "nested": {
                "level1": {
                    "level2": {
                        "param2": "new_value2",  # Override
                        "param3": "value3"       # Add
                    }
                }
            }
        }
        
        merged = self.merger.deep_merge(base_config, override_config)
        
        # Verify deep merge
        assert merged["nested"]["level1"]["level2"]["param1"] == "value1"  # Preserved
        assert merged["nested"]["level1"]["level2"]["param2"] == "new_value2"  # Overridden
        assert merged["nested"]["level1"]["level2"]["param3"] == "value3"  # Added
    
    def test_list_merge_strategies(self):
        """Test different list merge strategies"""
        base_config = {"formats": ["wav", "mp3"]}
        override_config = {"formats": ["flac", "ogg"]}
        
        # Replace strategy
        replaced = self.merger.merge(base_config, override_config, list_strategy="replace")
        assert replaced["formats"] == ["flac", "ogg"]
        
        # Append strategy
        appended = self.merger.merge(base_config, override_config, list_strategy="append")
        assert set(appended["formats"]) == {"wav", "mp3", "flac", "ogg"}
        
        # Union strategy (no duplicates)
        union = self.merger.merge(
            {"formats": ["wav", "mp3", "wav"]}, 
            {"formats": ["mp3", "flac"]}, 
            list_strategy="union"
        )
        assert set(union["formats"]) == {"wav", "mp3", "flac"}


class TestConfigIntegration:
    """
    Integration tests for complete configuration workflows
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_config_workflow(self):
        """Test complete configuration workflow"""
        # Create configuration manager
        manager = ConfigManager(config_dir=self.temp_dir)
        
        # Create comprehensive configuration
        complete_config = {
            "audio": {
                "sample_rate": 44100,
                "channels": 2,
                "bit_depth": 16,
                "supported_formats": ["wav", "mp3", "flac"]
            },
            "processing": {
                "buffer_size": 1024,
                "window_size": 2048,
                "overlap_ratio": 0.5,
                "enable_preprocessing": True
            },
            "ml_models": {
                "default_model": "cnn1d",
                "model_path": "/models",
                "batch_size": 32,
                "learning_rate": 0.001
            },
            "quality": {
                "enable_perceptual": True,
                "enable_objective": True,
                "quality_threshold": 0.8
            },
            "realtime": {
                "buffer_size": 256,
                "max_latency_ms": 10.0,
                "enable_monitoring": True
            },
            "security": {
                "enable_encryption": True,
                "encryption_algorithm": "AES-256",
                "max_file_size_mb": 100
            },
            "performance": {
                "max_threads": 4,
                "max_memory_mb": 1024,
                "enable_gpu_acceleration": False
            }
        }
        
        # Save configuration
        config_file = os.path.join(self.temp_dir, "complete_config.json")
        with open(config_file, 'w') as f:
            json.dump(complete_config, f, indent=2)
        
        # Load and validate configuration
        loaded_config = manager.load_config_from_file(config_file)
        validation_result = manager.validate_config(loaded_config)
        
        # Verify complete workflow
        assert validation_result.is_valid is True
        assert loaded_config["audio"]["sample_rate"] == 44100
        assert loaded_config["processing"]["buffer_size"] == 1024
        assert loaded_config["ml_models"]["default_model"] == "cnn1d"
        assert loaded_config["security"]["enable_encryption"] is True
    
    def test_multi_environment_config(self):
        """Test multi-environment configuration management"""
        manager = ConfigManager(config_dir=self.temp_dir)
        
        # Base configuration
        base_config = {
            "audio": {"sample_rate": 44100, "channels": 2},
            "processing": {"buffer_size": 512},
            "performance": {"max_threads": 2}
        }
        
        # Development overrides
        dev_overrides = {
            "audio": {"sample_rate": 22050},  # Lower quality for dev
            "processing": {"enable_debug": True},
            "performance": {"enable_profiling": True}
        }
        
        # Production overrides
        prod_overrides = {
            "processing": {"buffer_size": 1024},  # Larger buffer for prod
            "performance": {"max_threads": 8},
            "security": {"enable_encryption": True}
        }
        
        # Save configurations
        base_file = os.path.join(self.temp_dir, "base.json")
        dev_file = os.path.join(self.temp_dir, "development.json")
        prod_file = os.path.join(self.temp_dir, "production.json")
        
        for config, file_path in [
            (base_config, base_file),
            (dev_overrides, dev_file),
            (prod_overrides, prod_file)
        ]:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Test development environment
        dev_config = manager.load_environment_config("development", base_file)
        assert dev_config["audio"]["sample_rate"] == 22050
        assert dev_config["processing"]["enable_debug"] is True
        assert dev_config["performance"]["max_threads"] == 2  # From base
        
        # Test production environment
        prod_config = manager.load_environment_config("production", base_file)
        assert prod_config["audio"]["sample_rate"] == 44100  # From base
        assert prod_config["processing"]["buffer_size"] == 1024
        assert prod_config["performance"]["max_threads"] == 8
        assert prod_config["security"]["enable_encryption"] is True


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
