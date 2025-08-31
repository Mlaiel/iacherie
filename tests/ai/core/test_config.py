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
Comprehensive AI Core Configuration Tests

Ultra-advanced enterprise-grade test suite for AI core configuration management.
Tests environment-based configuration, validation, defaults, and business logic settings.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  COPYRIGHT WARNING: This file is protected by copyright law. Unauthorized copying,
distribution, modification, or use is strictly prohibited. Violations will result in
legal action. Contact mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: Advanced configuration architecture, environment management
- Backend Senior Engineer: Enterprise configuration patterns, deployment configuration
- DevOps Engineer: Environment configuration, infrastructure settings, scaling parameters
- Security Engineer: Security configuration, encryption settings, access control
- Performance Engineer: Performance configuration, optimization settings, monitoring
- Quality Assurance Lead: Configuration validation, testing patterns, edge cases

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, mock_open

# System imports
import sys
import logging

# Test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from ai.core.config import (
    AIEngineConfig,
    ValidationConfig,
    PerformanceConfig,
    MetricsConfig,
    PipelineConfig,
    CoreConfig,
    ConfigManager,
    load_config,
    save_config,
    get_config,
    update_config,
    config_manager
)


class TestAIEngineConfig:
    """Test suite for AIEngineConfig class"""
    
    def test_ai_engine_config_defaults(self):
        """Test AI engine configuration default values"""
        config = AIEngineConfig()
        
        assert config.max_concurrent_models == 5
        assert config.auto_cleanup_interval == 300
        assert config.memory_threshold_gb == 8.0
        assert config.default_device == "auto"
        assert config.model_cache_size == 1000
        assert config.inference_timeout == 30
        assert config.batch_size == 32
        assert config.enable_gpu is True
        assert config.enable_model_versioning is True
        assert config.model_repository_path == "./models"
    
    def test_ai_engine_config_customization(self):
        """Test AI engine configuration customization"""
        config = AIEngineConfig(
            max_concurrent_models=10,
            memory_threshold_gb=16.0,
            default_device="cuda",
            model_cache_size=2000,
            inference_timeout=60,
            batch_size=64,
            enable_gpu=False,
            model_repository_path="/custom/models"
        )
        
        assert config.max_concurrent_models == 10
        assert config.memory_threshold_gb == 16.0
        assert config.default_device == "cuda"
        assert config.model_cache_size == 2000
        assert config.inference_timeout == 60
        assert config.batch_size == 64
        assert config.enable_gpu is False
        assert config.model_repository_path == "/custom/models"
    
    def test_ai_engine_config_to_dict(self):
        """Test AI engine configuration dictionary conversion"""
        config = AIEngineConfig(
            max_concurrent_models=8,
            memory_threshold_gb=12.0,
            default_device="cpu"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["max_concurrent_models"] == 8
        assert config_dict["memory_threshold_gb"] == 12.0
        assert config_dict["default_device"] == "cpu"
        assert config_dict["auto_cleanup_interval"] == 300  # Default value
        assert isinstance(config_dict, dict)
        assert len(config_dict) == 10  # All fields present
    
    def test_ai_engine_config_performance_tuning(self):
        """Test AI engine configuration for different performance scenarios"""
        # High-performance configuration
        high_perf_config = AIEngineConfig(
            max_concurrent_models=20,
            memory_threshold_gb=32.0,
            model_cache_size=5000,
            batch_size=128,
            enable_gpu=True,
            inference_timeout=120
        )
        
        assert high_perf_config.max_concurrent_models == 20
        assert high_perf_config.memory_threshold_gb == 32.0
        assert high_perf_config.model_cache_size == 5000
        assert high_perf_config.batch_size == 128
        
        # Low-resource configuration
        low_resource_config = AIEngineConfig(
            max_concurrent_models=2,
            memory_threshold_gb=4.0,
            model_cache_size=500,
            batch_size=8,
            enable_gpu=False,
            default_device="cpu"
        )
        
        assert low_resource_config.max_concurrent_models == 2
        assert low_resource_config.memory_threshold_gb == 4.0
        assert low_resource_config.model_cache_size == 500
        assert low_resource_config.batch_size == 8
        assert low_resource_config.enable_gpu is False


class TestValidationConfig:
    """Test suite for ValidationConfig class"""
    
    def test_validation_config_defaults(self):
        """Test validation configuration default values"""
        config = ValidationConfig()
        
        assert config.enable_security_validation is True
        assert config.enable_quality_analysis is True
        assert config.enable_seo_validation is True
        assert config.enable_audio_validation is True
        assert config.enable_image_validation is True
        assert config.min_quality_score == 70.0
        assert config.min_safety_score == 80.0
        assert config.min_compliance_score == 85.0
        assert config.max_content_size_mb == 100.0
        assert ".mp3" in config.supported_formats
        assert ".jpg" in config.supported_formats
        assert ".png" in config.supported_formats
    
    def test_validation_config_customization(self):
        """Test validation configuration customization"""
        custom_formats = [".wav", ".flac", ".jpeg", ".tiff", ".mp4"]
        
        config = ValidationConfig(
            enable_security_validation=False,
            min_quality_score=85.0,
            min_safety_score=90.0,
            min_compliance_score=95.0,
            max_content_size_mb=500.0,
            supported_formats=custom_formats
        )
        
        assert config.enable_security_validation is False
        assert config.min_quality_score == 85.0
        assert config.min_safety_score == 90.0
        assert config.min_compliance_score == 95.0
        assert config.max_content_size_mb == 500.0
        assert config.supported_formats == custom_formats
    
    def test_validation_config_creator_specific(self):
        """Test validation configuration for specific creator types"""
        # Musicians configuration
        musician_config = ValidationConfig(
            enable_audio_validation=True,
            enable_image_validation=False,
            supported_formats=[".mp3", ".wav", ".flac", ".aac", ".ogg"],
            min_quality_score=80.0,
            max_content_size_mb=200.0
        )
        
        assert musician_config.enable_audio_validation is True
        assert musician_config.enable_image_validation is False
        assert ".mp3" in musician_config.supported_formats
        assert ".wav" in musician_config.supported_formats
        assert musician_config.min_quality_score == 80.0
        
        # Photographers configuration
        photographer_config = ValidationConfig(
            enable_audio_validation=False,
            enable_image_validation=True,
            supported_formats=[".jpg", ".jpeg", ".png", ".tiff", ".raw"],
            min_quality_score=85.0,
            max_content_size_mb=50.0
        )
        
        assert photographer_config.enable_audio_validation is False
        assert photographer_config.enable_image_validation is True
        assert ".jpg" in photographer_config.supported_formats
        assert ".raw" in photographer_config.supported_formats
        assert photographer_config.min_quality_score == 85.0
    
    def test_validation_config_to_dict(self):
        """Test validation configuration dictionary conversion"""
        config = ValidationConfig(
            min_quality_score=75.0,
            enable_seo_validation=False
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["min_quality_score"] == 75.0
        assert config_dict["enable_seo_validation"] is False
        assert config_dict["enable_security_validation"] is True  # Default
        assert "supported_formats" in config_dict
        assert isinstance(config_dict["supported_formats"], list)


class TestPerformanceConfig:
    """Test suite for PerformanceConfig class"""
    
    def test_performance_config_defaults(self):
        """Test performance configuration default values"""
        config = PerformanceConfig()
        
        assert config.monitoring_interval == 30
        assert config.history_size == 1000
        assert config.enable_auto_optimization is True
        assert config.enable_predictions is True
        assert config.cpu_warning_threshold == 70.0
        assert config.cpu_critical_threshold == 85.0
        assert config.memory_warning_threshold == 80.0
        assert config.memory_critical_threshold == 90.0
        assert config.disk_warning_threshold == 85.0
        assert config.disk_critical_threshold == 95.0
        assert config.response_time_warning == 2.0
        assert config.response_time_critical == 5.0
    
    def test_performance_config_thresholds(self):
        """Test performance configuration threshold settings"""
        # Conservative thresholds
        conservative_config = PerformanceConfig(
            cpu_warning_threshold=50.0,
            cpu_critical_threshold=70.0,
            memory_warning_threshold=60.0,
            memory_critical_threshold=80.0,
            response_time_warning=1.0,
            response_time_critical=3.0
        )
        
        assert conservative_config.cpu_warning_threshold == 50.0
        assert conservative_config.cpu_critical_threshold == 70.0
        assert conservative_config.memory_warning_threshold == 60.0
        assert conservative_config.memory_critical_threshold == 80.0
        assert conservative_config.response_time_warning == 1.0
        assert conservative_config.response_time_critical == 3.0
        
        # Aggressive thresholds
        aggressive_config = PerformanceConfig(
            cpu_warning_threshold=85.0,
            cpu_critical_threshold=95.0,
            memory_warning_threshold=90.0,
            memory_critical_threshold=95.0,
            response_time_warning=5.0,
            response_time_critical=10.0
        )
        
        assert aggressive_config.cpu_warning_threshold == 85.0
        assert aggressive_config.cpu_critical_threshold == 95.0
        assert aggressive_config.memory_warning_threshold == 90.0
        assert aggressive_config.memory_critical_threshold == 95.0
    
    def test_performance_config_monitoring_settings(self):
        """Test performance configuration monitoring settings"""
        config = PerformanceConfig(
            monitoring_interval=10,
            history_size=5000,
            enable_auto_optimization=False,
            enable_predictions=False
        )
        
        assert config.monitoring_interval == 10
        assert config.history_size == 5000
        assert config.enable_auto_optimization is False
        assert config.enable_predictions is False
    
    def test_performance_config_to_dict(self):
        """Test performance configuration dictionary conversion"""
        config = PerformanceConfig(
            monitoring_interval=15,
            cpu_warning_threshold=60.0
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["monitoring_interval"] == 15
        assert config_dict["cpu_warning_threshold"] == 60.0
        assert config_dict["history_size"] == 1000  # Default
        assert len(config_dict) == 12  # All fields present


class TestMetricsConfig:
    """Test suite for MetricsConfig class"""
    
    def test_metrics_config_defaults(self):
        """Test metrics configuration default values"""
        config = MetricsConfig()
        
        assert config.max_entries == 10000
        assert config.auto_flush_interval == 300
        assert config.enable_system_metrics is True
        assert config.enable_business_metrics is True
        assert config.metric_retention_days == 30
        assert config.export_format == "json"
        assert config.enable_prometheus_export is False
        assert config.prometheus_port == 9090
    
    def test_metrics_config_prometheus_setup(self):
        """Test metrics configuration with Prometheus export"""
        config = MetricsConfig(
            enable_prometheus_export=True,
            prometheus_port=8080,
            export_format="prometheus"
        )
        
        assert config.enable_prometheus_export is True
        assert config.prometheus_port == 8080
        assert config.export_format == "prometheus"
    
    def test_metrics_config_retention_policy(self):
        """Test metrics configuration retention policies"""
        # Short retention
        short_retention_config = MetricsConfig(
            max_entries=5000,
            metric_retention_days=7,
            auto_flush_interval=60
        )
        
        assert short_retention_config.max_entries == 5000
        assert short_retention_config.metric_retention_days == 7
        assert short_retention_config.auto_flush_interval == 60
        
        # Long retention
        long_retention_config = MetricsConfig(
            max_entries=50000,
            metric_retention_days=365,
            auto_flush_interval=3600
        )
        
        assert long_retention_config.max_entries == 50000
        assert long_retention_config.metric_retention_days == 365
        assert long_retention_config.auto_flush_interval == 3600
    
    def test_metrics_config_selective_metrics(self):
        """Test metrics configuration with selective metric collection"""
        config = MetricsConfig(
            enable_system_metrics=False,
            enable_business_metrics=True
        )
        
        assert config.enable_system_metrics is False
        assert config.enable_business_metrics is True
    
    def test_metrics_config_to_dict(self):
        """Test metrics configuration dictionary conversion"""
        config = MetricsConfig(
            max_entries=20000,
            enable_prometheus_export=True
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["max_entries"] == 20000
        assert config_dict["enable_prometheus_export"] is True
        assert config_dict["auto_flush_interval"] == 300  # Default
        assert len(config_dict) == 8  # All fields present


class TestPipelineConfig:
    """Test suite for PipelineConfig class"""
    
    def test_pipeline_config_defaults(self):
        """Test pipeline configuration default values"""
        config = PipelineConfig()
        
        assert config.max_concurrent_pipelines == 10
        assert config.stage_timeout_seconds == 300
        assert config.enable_stage_caching is True
        assert config.enable_parallel_processing is True
        assert config.retry_failed_stages is True
        assert config.max_retries == 3
        assert config.enable_stage_skipping is False
        assert "validation" in config.required_stages
        assert "ai_analysis" in config.required_stages
        assert "protection" in config.required_stages
    
    def test_pipeline_config_scaling(self):
        """Test pipeline configuration for different scaling scenarios"""
        # High-throughput configuration
        high_throughput_config = PipelineConfig(
            max_concurrent_pipelines=50,
            stage_timeout_seconds=600,
            enable_parallel_processing=True,
            max_retries=5
        )
        
        assert high_throughput_config.max_concurrent_pipelines == 50
        assert high_throughput_config.stage_timeout_seconds == 600
        assert high_throughput_config.enable_parallel_processing is True
        assert high_throughput_config.max_retries == 5
        
        # Conservative configuration
        conservative_config = PipelineConfig(
            max_concurrent_pipelines=3,
            stage_timeout_seconds=120,
            enable_parallel_processing=False,
            max_retries=1
        )
        
        assert conservative_config.max_concurrent_pipelines == 3
        assert conservative_config.stage_timeout_seconds == 120
        assert conservative_config.enable_parallel_processing is False
        assert conservative_config.max_retries == 1
    
    def test_pipeline_config_required_stages(self):
        """Test pipeline configuration required stages"""
        # Custom required stages
        custom_config = PipelineConfig(
            required_stages=["validation", "protection", "seo_enhancement", "distribution"]
        )
        
        assert "validation" in custom_config.required_stages
        assert "protection" in custom_config.required_stages
        assert "seo_enhancement" in custom_config.required_stages
        assert "distribution" in custom_config.required_stages
        assert len(custom_config.required_stages) == 4
        
        # Minimal required stages
        minimal_config = PipelineConfig(
            required_stages=["validation"]
        )
        
        assert minimal_config.required_stages == ["validation"]
    
    def test_pipeline_config_business_logic_coverage(self):
        """Test pipeline configuration covers business logic workflow"""
        # Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
        full_workflow_config = PipelineConfig(
            required_stages=[
                "upload",
                "validation", 
                "ai_analysis",
                "protection",
                "seo_enhancement",
                "collaboration_matching",
                "distribution_prep"
            ],
            enable_stage_caching=True,
            enable_parallel_processing=True
        )
        
        workflow_stages = full_workflow_config.required_stages
        assert "validation" in workflow_stages
        assert "ai_analysis" in workflow_stages
        assert "protection" in workflow_stages
        assert "seo_enhancement" in workflow_stages
        assert "collaboration_matching" in workflow_stages
        assert "distribution_prep" in workflow_stages
    
    def test_pipeline_config_to_dict(self):
        """Test pipeline configuration dictionary conversion"""
        config = PipelineConfig(
            max_concurrent_pipelines=20,
            enable_stage_skipping=True
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["max_concurrent_pipelines"] == 20
        assert config_dict["enable_stage_skipping"] is True
        assert config_dict["stage_timeout_seconds"] == 300  # Default
        assert "required_stages" in config_dict
        assert isinstance(config_dict["required_stages"], list)


class TestCoreConfig:
    """Test suite for CoreConfig class"""
    
    def test_core_config_defaults(self):
        """Test core configuration default values"""
        config = CoreConfig()
        
        assert config.environment == "development"
        assert config.debug_mode is False
        assert config.log_level == "INFO"
        assert config.enable_detailed_logging is True
        assert isinstance(config.ai_engine, AIEngineConfig)
        assert isinstance(config.validation, ValidationConfig)
        assert isinstance(config.performance, PerformanceConfig)
        assert isinstance(config.metrics, MetricsConfig)
        assert isinstance(config.pipeline, PipelineConfig)
        assert config.enable_encryption is True
        assert config.api_rate_limit == 1000
        assert config.max_request_size_mb == 50.0
        assert config.enable_monetization is True
        assert config.enable_collaboration is True
        assert config.enable_seo_optimization is True
        assert config.enable_content_protection is True
    
    def test_core_config_environment_specific(self):
        """Test core configuration for different environments"""
        # Development environment
        dev_config = CoreConfig(
            environment="development",
            debug_mode=True,
            log_level="DEBUG",
            enable_detailed_logging=True
        )
        
        assert dev_config.environment == "development"
        assert dev_config.debug_mode is True
        assert dev_config.log_level == "DEBUG"
        assert dev_config.enable_detailed_logging is True
        
        # Production environment
        prod_config = CoreConfig(
            environment="production",
            debug_mode=False,
            log_level="WARNING",
            enable_detailed_logging=False
        )
        
        assert prod_config.environment == "production"
        assert prod_config.debug_mode is False
        assert prod_config.log_level == "WARNING"
        assert prod_config.enable_detailed_logging is False
        
        # Testing environment
        test_config = CoreConfig(
            environment="testing",
            debug_mode=True,
            log_level="ERROR"
        )
        
        assert test_config.environment == "testing"
        assert test_config.debug_mode is True
        assert test_config.log_level == "ERROR"
    
    def test_core_config_business_features(self):
        """Test core configuration business feature toggles"""
        # All features enabled
        full_features_config = CoreConfig(
            enable_monetization=True,
            enable_collaboration=True,
            enable_seo_optimization=True,
            enable_content_protection=True
        )
        
        assert full_features_config.enable_monetization is True
        assert full_features_config.enable_collaboration is True
        assert full_features_config.enable_seo_optimization is True
        assert full_features_config.enable_content_protection is True
        
        # Minimal features
        minimal_features_config = CoreConfig(
            enable_monetization=False,
            enable_collaboration=False,
            enable_seo_optimization=False,
            enable_content_protection=True  # Always keep protection
        )
        
        assert minimal_features_config.enable_monetization is False
        assert minimal_features_config.enable_collaboration is False
        assert minimal_features_config.enable_seo_optimization is False
        assert minimal_features_config.enable_content_protection is True
    
    def test_core_config_security_settings(self):
        """Test core configuration security settings"""
        secure_config = CoreConfig(
            enable_encryption=True,
            api_rate_limit=500,
            max_request_size_mb=25.0
        )
        
        assert secure_config.enable_encryption is True
        assert secure_config.api_rate_limit == 500
        assert secure_config.max_request_size_mb == 25.0
        
        # High-security configuration
        high_security_config = CoreConfig(
            enable_encryption=True,
            api_rate_limit=100,
            max_request_size_mb=10.0
        )
        
        assert high_security_config.api_rate_limit == 100
        assert high_security_config.max_request_size_mb == 10.0
    
    def test_core_config_component_integration(self):
        """Test core configuration component integration"""
        # Custom component configurations
        custom_ai_engine = AIEngineConfig(max_concurrent_models=15)
        custom_validation = ValidationConfig(min_quality_score=90.0)
        custom_performance = PerformanceConfig(monitoring_interval=15)
        
        config = CoreConfig(
            ai_engine=custom_ai_engine,
            validation=custom_validation,
            performance=custom_performance
        )
        
        assert config.ai_engine.max_concurrent_models == 15
        assert config.validation.min_quality_score == 90.0
        assert config.performance.monitoring_interval == 15
    
    def test_core_config_to_dict(self):
        """Test core configuration dictionary conversion"""
        config = CoreConfig(
            environment="testing",
            debug_mode=True,
            enable_monetization=False
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["environment"] == "testing"
        assert config_dict["debug_mode"] is True
        assert config_dict["enable_monetization"] is False
        assert "ai_engine" in config_dict
        assert "validation" in config_dict
        assert "performance" in config_dict
        assert "metrics" in config_dict
        assert "pipeline" in config_dict
        assert isinstance(config_dict["ai_engine"], dict)
        assert isinstance(config_dict["validation"], dict)


class TestConfigManager:
    """Test suite for ConfigManager class"""
    
    def setup_method(self):
        """Setup config manager for testing"""
        self.config_manager = ConfigManager()
    
    def test_config_manager_initialization(self):
        """Test config manager initialization"""
        assert hasattr(self.config_manager, '_configs')
        assert isinstance(self.config_manager._configs, dict)
        assert hasattr(self.config_manager, '_config_paths')
    
    def test_config_manager_registration(self):
        """Test config manager configuration registration"""
        test_config = CoreConfig(environment="test")
        
        self.config_manager.register_config("test", test_config)
        
        assert "test" in self.config_manager._configs
        assert self.config_manager._configs["test"] == test_config
    
    def test_config_manager_retrieval(self):
        """Test config manager configuration retrieval"""
        test_config = CoreConfig(environment="retrieval_test")
        self.config_manager.register_config("retrieval", test_config)
        
        retrieved_config = self.config_manager.get_config("retrieval")
        
        assert retrieved_config == test_config
        assert retrieved_config.environment == "retrieval_test"
        
        # Test non-existent config
        non_existent = self.config_manager.get_config("non_existent")
        assert non_existent is None
    
    def test_config_manager_environment_loading(self):
        """Test config manager environment-based loading"""
        with patch.dict(os.environ, {
            'AI_CORE_ENVIRONMENT': 'production',
            'AI_CORE_DEBUG': 'false',
            'AI_CORE_LOG_LEVEL': 'ERROR'
        }):
            env_config = self.config_manager.load_from_environment()
            
            assert env_config.environment == "production"
            assert env_config.debug_mode is False
            assert env_config.log_level == "ERROR"
    
    def test_config_manager_file_operations(self):
        """Test config manager file save/load operations"""
        test_config = CoreConfig(
            environment="file_test",
            debug_mode=True,
            api_rate_limit=2000
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save config to file
            self.config_manager.save_to_file(test_config, temp_path)
            
            # Load config from file
            loaded_config = self.config_manager.load_from_file(temp_path)
            
            assert loaded_config.environment == "file_test"
            assert loaded_config.debug_mode is True
            assert loaded_config.api_rate_limit == 2000
        finally:
            os.unlink(temp_path)
    
    def test_config_manager_validation(self):
        """Test config manager configuration validation"""
        # Valid configuration
        valid_config = CoreConfig(
            environment="production",
            api_rate_limit=1000,
            max_request_size_mb=50.0
        )
        
        is_valid, errors = self.config_manager.validate_config(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid configuration
        invalid_config = CoreConfig(
            api_rate_limit=-100,  # Invalid negative rate limit
            max_request_size_mb=0  # Invalid zero size
        )
        
        is_valid, errors = self.config_manager.validate_config(invalid_config)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_config_manager_merging(self):
        """Test config manager configuration merging"""
        base_config = CoreConfig(
            environment="base",
            debug_mode=False,
            api_rate_limit=1000
        )
        
        override_config = CoreConfig(
            environment="override",
            debug_mode=True,
            enable_monetization=False
        )
        
        merged_config = self.config_manager.merge_configs(base_config, override_config)
        
        assert merged_config.environment == "override"  # Overridden
        assert merged_config.debug_mode is True  # Overridden
        assert merged_config.api_rate_limit == 1000  # From base
        assert merged_config.enable_monetization is False  # Overridden


class TestConfigurationFunctions:
    """Test suite for standalone configuration functions"""
    
    def test_load_config_function(self):
        """Test load_config standalone function"""
        test_config_data = {
            "environment": "function_test",
            "debug_mode": True,
            "log_level": "DEBUG",
            "ai_engine": {
                "max_concurrent_models": 8,
                "default_device": "cpu"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_config_data, temp_file)
            temp_path = temp_file.name
        
        try:
            loaded_config = load_config(temp_path)
            
            assert loaded_config.environment == "function_test"
            assert loaded_config.debug_mode is True
            assert loaded_config.log_level == "DEBUG"
            assert loaded_config.ai_engine.max_concurrent_models == 8
            assert loaded_config.ai_engine.default_device == "cpu"
        finally:
            os.unlink(temp_path)
    
    def test_save_config_function(self):
        """Test save_config standalone function"""
        test_config = CoreConfig(
            environment="save_test",
            debug_mode=False,
            api_rate_limit=1500
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save config
            success = save_config(test_config, temp_path)
            assert success is True
            
            # Verify file was created and contains correct data
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
                
            assert saved_data["environment"] == "save_test"
            assert saved_data["debug_mode"] is False
            assert saved_data["api_rate_limit"] == 1500
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_validate_config_function(self):
        """Test validate_config standalone function"""
        # Valid configuration
        valid_config = CoreConfig(
            environment="production",
            api_rate_limit=500,
            max_request_size_mb=25.0
        )
        
        is_valid, errors = validate_config(valid_config)
        assert is_valid is True
        assert errors == []
        
        # Configuration with warnings
        warning_config = CoreConfig(
            environment="development",
            api_rate_limit=10000,  # Very high rate limit
            max_request_size_mb=1000.0  # Very large request size
        )
        
        is_valid, errors = validate_config(warning_config)
        # Should still be valid but might have warnings
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
    
    def test_get_environment_config_function(self):
        """Test get_environment_config standalone function"""
        with patch.dict(os.environ, {
            'AI_CORE_ENVIRONMENT': 'staging',
            'AI_CORE_DEBUG': 'true',
            'AI_CORE_LOG_LEVEL': 'WARNING',
            'AI_CORE_MAX_CONCURRENT_MODELS': '12',
            'AI_CORE_API_RATE_LIMIT': '2000'
        }):
            env_config = get_environment_config()
            
            assert env_config.environment == "staging"
            assert env_config.debug_mode is True
            assert env_config.log_level == "WARNING"
            assert env_config.ai_engine.max_concurrent_models == 12
            assert env_config.api_rate_limit == 2000
    
    def test_merge_configs_function(self):
        """Test merge_configs standalone function"""
        config1 = CoreConfig(
            environment="base",
            debug_mode=False,
            ai_engine=AIEngineConfig(max_concurrent_models=5)
        )
        
        config2 = CoreConfig(
            environment="override",
            enable_monetization=False,
            ai_engine=AIEngineConfig(max_concurrent_models=10, default_device="cuda")
        )
        
        merged = merge_configs(config1, config2)
        
        assert merged.environment == "override"  # From config2
        assert merged.debug_mode is False  # From config1
        assert merged.enable_monetization is False  # From config2
        assert merged.ai_engine.max_concurrent_models == 10  # From config2
        assert merged.ai_engine.default_device == "cuda"  # From config2


class TestConfigurationValidation:
    """Test suite for configuration validation logic"""
    
    def test_configuration_boundary_values(self):
        """Test configuration with boundary values"""
        # Minimum values
        min_config = CoreConfig(
            api_rate_limit=1,
            max_request_size_mb=0.1,
            ai_engine=AIEngineConfig(
                max_concurrent_models=1,
                memory_threshold_gb=1.0,
                model_cache_size=10
            )
        )
        
        is_valid, errors = validate_config(min_config)
        assert is_valid is True  # Should accept minimum valid values
        
        # Maximum reasonable values
        max_config = CoreConfig(
            api_rate_limit=100000,
            max_request_size_mb=1000.0,
            ai_engine=AIEngineConfig(
                max_concurrent_models=100,
                memory_threshold_gb=128.0,
                model_cache_size=100000
            )
        )
        
        is_valid, errors = validate_config(max_config)
        assert is_valid is True  # Should accept maximum reasonable values
    
    def test_configuration_invalid_values(self):
        """Test configuration with invalid values"""
        # Negative values
        negative_config = CoreConfig(
            api_rate_limit=-1,
            max_request_size_mb=-5.0
        )
        
        is_valid, errors = validate_config(negative_config)
        assert is_valid is False
        assert len(errors) > 0
        
        # Zero values where positive required
        zero_config = CoreConfig(
            ai_engine=AIEngineConfig(
                max_concurrent_models=0,
                model_cache_size=0
            )
        )
        
        is_valid, errors = validate_config(zero_config)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_configuration_business_logic_validation(self):
        """Test configuration validation for business logic requirements"""
        # Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
        
        # Configuration without content protection (should be invalid for business)
        no_protection_config = CoreConfig(
            enable_content_protection=False,
            pipeline=PipelineConfig(
                required_stages=["validation", "ai_analysis"]  # Missing protection
            )
        )
        
        is_valid, errors = validate_config(no_protection_config)
        # Content protection is critical for business logic
        assert "protection" in str(errors).lower() or is_valid is False
        
        # Valid business configuration
        business_config = CoreConfig(
            enable_content_protection=True,
            enable_seo_optimization=True,
            enable_collaboration=True,
            enable_monetization=True,
            pipeline=PipelineConfig(
                required_stages=[
                    "validation", "ai_analysis", "protection", 
                    "seo_enhancement", "collaboration_matching"
                ]
            )
        )
        
        is_valid, errors = validate_config(business_config)
        assert is_valid is True


class TestConfigurationIntegration:
    """Integration tests for configuration system"""
    
    def test_configuration_environment_override(self):
        """Test configuration with environment variable overrides"""
        base_config = CoreConfig(
            environment="development",
            debug_mode=False,
            api_rate_limit=1000
        )
        
        with patch.dict(os.environ, {
            'AI_CORE_ENVIRONMENT': 'production',
            'AI_CORE_DEBUG': 'false',
            'AI_CORE_API_RATE_LIMIT': '500'
        }):
            env_config = get_environment_config()
            merged_config = merge_configs(base_config, env_config)
            
            assert merged_config.environment == "production"
            assert merged_config.debug_mode is False
            assert merged_config.api_rate_limit == 500
    
    def test_configuration_creator_workflows(self):
        """Test configuration for different creator workflows"""
        # Musician-focused configuration
        musician_config = CoreConfig(
            validation=ValidationConfig(
                enable_audio_validation=True,
                enable_image_validation=False,
                supported_formats=[".mp3", ".wav", ".flac"],
                min_quality_score=80.0
            ),
            pipeline=PipelineConfig(
                required_stages=["validation", "ai_analysis", "protection", "distribution_prep"]
            ),
            enable_monetization=True,
            enable_collaboration=True
        )
        
        is_valid, errors = validate_config(musician_config)
        assert is_valid is True
        assert musician_config.validation.enable_audio_validation is True
        
        # Photographer-focused configuration
        photographer_config = CoreConfig(
            validation=ValidationConfig(
                enable_audio_validation=False,
                enable_image_validation=True,
                supported_formats=[".jpg", ".png", ".tiff"],
                min_quality_score=85.0
            ),
            pipeline=PipelineConfig(
                required_stages=["validation", "ai_analysis", "protection", "seo_enhancement"]
            ),
            enable_content_protection=True
        )
        
        is_valid, errors = validate_config(photographer_config)
        assert is_valid is True
        assert photographer_config.validation.enable_image_validation is True
    
    def test_configuration_scaling_scenarios(self):
        """Test configuration for different scaling scenarios"""
        # Small-scale configuration
        small_scale_config = CoreConfig(
            ai_engine=AIEngineConfig(
                max_concurrent_models=2,
                memory_threshold_gb=4.0,
                model_cache_size=500
            ),
            pipeline=PipelineConfig(
                max_concurrent_pipelines=3,
                enable_parallel_processing=False
            ),
            performance=PerformanceConfig(
                monitoring_interval=60,
                history_size=500
            )
        )
        
        is_valid, errors = validate_config(small_scale_config)
        assert is_valid is True
        
        # Enterprise-scale configuration
        enterprise_config = CoreConfig(
            ai_engine=AIEngineConfig(
                max_concurrent_models=50,
                memory_threshold_gb=64.0,
                model_cache_size=10000
            ),
            pipeline=PipelineConfig(
                max_concurrent_pipelines=100,
                enable_parallel_processing=True
            ),
            performance=PerformanceConfig(
                monitoring_interval=10,
                history_size=10000
            ),
            metrics=MetricsConfig(
                enable_prometheus_export=True,
                max_entries=100000
            )
        )
        
        is_valid, errors = validate_config(enterprise_config)
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
