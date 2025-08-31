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
🔄 Pipeline Tests - Industrial-Grade Audio Processing Pipeline Testing Suite

Comprehensive testing for audio processing pipelines including:
- AudioPipeline orchestration
- Stage coordination and data flow
- Pipeline optimization
- Real-time processing workflows
- Error handling and recovery

Created by Expert Team: Pipeline Architect + DevOps Engineer + Backend Senior
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile
import time
import asyncio
import threading
import os
import psutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Import the audio processing module
try:
    from ai.audio_processing.pipeline import (
        AudioProcessingPipeline, PipelineConfig, PipelineResult, 
        StageResult, ProcessingMode, CacheStrategy, 
        PipelineStageBase, STANDARD_PIPELINES
    )
    from ai.audio_processing.core import AudioProcessor
    from ai.audio_processing.ml_models import MLModelManager
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.pipeline import (
        StageResult, ProcessingMode, CacheStrategy, 
        PipelineStageBase, STANDARD_PIPELINES
    )
    from ai.audio_processing.core import AudioProcessor
    from ai.audio_processing.ml_models import MLModelManager

from . import TEST_CONFIG, setup_test_environment


class TestPipelineStage:
    """
    Industrial-grade testing for PipelineStage class
    
    Test Coverage:
    - Stage initialization and configuration
    - Input/output validation
    - Stage execution
    - Error handling
    - Performance monitoring
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
    
    def test_stage_initialization(self):
        """Test PipelineStage initialization"""
        stage = PipelineStage(
            name="test_stage",
            processor_func=lambda x: x * 2,
            input_type=np.ndarray,
            output_type=np.ndarray
        )
        
        assert stage.name == "test_stage"
        assert stage.processor_func is not None
        assert stage.input_type == np.ndarray
        assert stage.output_type == np.ndarray
        assert stage.is_enabled is True
    
    def test_stage_execution(self):
        """Test stage execution"""
        def processing_function(data):
            return data + 10
        
        stage = PipelineStage(
            name="add_ten",
            processor_func=processing_function,
            input_type=(int, float, np.ndarray),
            output_type=(int, float, np.ndarray)
        )
        
        # Test with different input types
        test_inputs = [5, 3.14, np.array([1, 2, 3])]
        
        for input_data in test_inputs:
            result = stage.execute(input_data)
            
            assert isinstance(result, StageResult)
            assert result.success is True
            assert result.stage_name == "add_ten"
            
            if isinstance(input_data, np.ndarray):
                np.testing.assert_array_equal(result.output, input_data + 10)
            else:
                assert result.output == input_data + 10
    
    def test_stage_input_validation(self):
        """Test stage input validation"""
        stage = PipelineStage(
            name="strict_stage",
            processor_func=lambda x: x,
            input_type=str,
            output_type=str,
            validate_input=True
        )
        
        # Valid input
        valid_result = stage.execute("valid string")
        assert valid_result.success is True
        
        # Invalid input
        invalid_result = stage.execute(123)  # Should fail validation
        assert invalid_result.success is False
        assert "validation" in invalid_result.error_message.lower()
    
    def test_stage_error_handling(self):
        """Test stage error handling"""
        def failing_function(data):
            if data == "fail":
                raise ValueError("Intentional failure")
            return data
        
        stage = PipelineStage(
            name="error_prone",
            processor_func=failing_function,
            input_type=str,
            output_type=str
        )
        
        # Successful execution
        success_result = stage.execute("success")
        assert success_result.success is True
        
        # Failed execution
        error_result = stage.execute("fail")
        assert error_result.success is False
        assert error_result.error_message is not None
        assert "intentional failure" in error_result.error_message.lower()
    
    def test_stage_performance_monitoring(self):
        """Test stage performance monitoring"""
        def slow_function(data):
            time.sleep(0.1)  # Simulate processing time
            return data
        
        stage = PipelineStage(
            name="slow_stage",
            processor_func=slow_function,
            input_type=str,
            output_type=str,
            enable_profiling=True
        )
        
        result = stage.execute("test data")
        
        assert result.success is True
        assert result.execution_time_ms > 100  # Should be > 100ms due to sleep
        assert result.memory_usage_mb is not None
        assert result.execution_time_ms < 1000  # But not too slow
    
    def test_stage_async_execution(self):
        """Test asynchronous stage execution"""
        async def async_processor(data):
            await asyncio.sleep(0.05)
            return data.upper()
        
        stage = PipelineStage(
            name="async_stage",
            processor_func=async_processor,
            input_type=str,
            output_type=str,
            is_async=True
        )
        
        async def test_async():
            result = await stage.execute_async("hello")
            assert result.success is True
            assert result.output == "HELLO"
        
        # Run async test
        asyncio.run(test_async())


class TestAudioPipeline:
    """
    Industrial-grade testing for AudioPipeline class
    
    Test Coverage:
    - Pipeline construction and configuration
    - Multi-stage execution
    - Data flow management
    - Error propagation
    - Performance optimization
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        
        # Create sample stages
        self.load_stage = PipelineStage(
            name="load_audio",
            processor_func=lambda path: np.random.randn(44100),
            input_type=str,
            output_type=np.ndarray
        )
        
        self.normalize_stage = PipelineStage(
            name="normalize",
            processor_func=lambda audio: audio / np.max(np.abs(audio)),
            input_type=np.ndarray,
            output_type=np.ndarray
        )
        
        self.feature_stage = PipelineStage(
            name="extract_features",
            processor_func=lambda audio: {"mfcc": np.random.randn(13, 100)},
            input_type=np.ndarray,
            output_type=dict
        )
    
    def test_pipeline_initialization(self):
        """Test AudioPipeline initialization"""
        config = PipelineConfig(
            name="test_pipeline",
            parallel_execution=False,
            max_workers=4,
            timeout_seconds=30
        )
        
        pipeline = AudioPipeline(config=config)
        
        assert pipeline.config.name == "test_pipeline"
        assert pipeline.config.parallel_execution is False
        assert pipeline.config.max_workers == 4
        assert len(pipeline.stages) == 0
    
    def test_add_stage(self):
        """Test adding stages to pipeline"""
        pipeline = AudioPipeline()
        
        # Add stages
        pipeline.add_stage(self.load_stage)
        pipeline.add_stage(self.normalize_stage)
        pipeline.add_stage(self.feature_stage)
        
        assert len(pipeline.stages) == 3
        assert pipeline.stages[0].name == "load_audio"
        assert pipeline.stages[1].name == "normalize"
        assert pipeline.stages[2].name == "extract_features"
    
    def test_remove_stage(self):
        """Test removing stages from pipeline"""
        pipeline = AudioPipeline()
        pipeline.add_stage(self.load_stage)
        pipeline.add_stage(self.normalize_stage)
        
        # Remove stage
        success = pipeline.remove_stage("normalize")
        
        assert success is True
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].name == "load_audio"
        
        # Try to remove non-existent stage
        fail_success = pipeline.remove_stage("non_existent")
        assert fail_success is False
    
    def test_sequential_execution(self):
        """Test sequential pipeline execution"""
        pipeline = AudioPipeline()
        pipeline.add_stage(self.load_stage)
        pipeline.add_stage(self.normalize_stage)
        pipeline.add_stage(self.feature_stage)
        
        # Execute pipeline
        result = pipeline.execute("dummy_audio_path.wav")
        
        assert isinstance(result, ProcessingResult)
        assert result.success is True
        assert len(result.stage_results) == 3
        
        # Check stage execution order
        assert result.stage_results[0].stage_name == "load_audio"
        assert result.stage_results[1].stage_name == "normalize"
        assert result.stage_results[2].stage_name == "extract_features"
        
        # Final output should be features dictionary
        assert isinstance(result.final_output, dict)
        assert "mfcc" in result.final_output
    
    def test_pipeline_error_propagation(self):
        """Test error propagation in pipeline"""
        # Create a failing stage
        failing_stage = PipelineStage(
            name="failing_stage",
            processor_func=lambda x: 1/0,  # Division by zero
            input_type=np.ndarray,
            output_type=np.ndarray
        )
        
        pipeline = AudioPipeline()
        pipeline.add_stage(self.load_stage)
        pipeline.add_stage(failing_stage)
        pipeline.add_stage(self.feature_stage)  # Should not execute
        
        result = pipeline.execute("dummy_path.wav")
        
        assert result.success is False
        assert len(result.stage_results) == 2  # Only load and failing stage
        assert result.stage_results[1].success is False
        assert "division by zero" in result.stage_results[1].error_message.lower()
    
    def test_parallel_execution(self):
        """Test parallel pipeline execution"""
        # Create stages that can run in parallel
        stage1 = PipelineStage(
            name="parallel_1",
            processor_func=lambda audio: audio + 1,
            input_type=np.ndarray,
            output_type=np.ndarray
        )
        
        stage2 = PipelineStage(
            name="parallel_2",
            processor_func=lambda audio: audio * 2,
            input_type=np.ndarray,
            output_type=np.ndarray
        )
        
        config = PipelineConfig(parallel_execution=True, max_workers=2)
        pipeline = AudioPipeline(config=config)
        
        # Add load stage first (must be sequential)
        pipeline.add_stage(self.load_stage)
        
        # Add parallel stages
        pipeline.add_parallel_group([stage1, stage2])
        
        result = pipeline.execute("dummy_path.wav")
        
        assert result.success is True
        # Should have results from all stages
        stage_names = [sr.stage_name for sr in result.stage_results]
        assert "load_audio" in stage_names
        assert "parallel_1" in stage_names
        assert "parallel_2" in stage_names
    
    def test_pipeline_caching(self):
        """Test pipeline result caching"""
        config = PipelineConfig(enable_caching=True)
        pipeline = AudioPipeline(config=config)
        pipeline.add_stage(self.load_stage)
        pipeline.add_stage(self.normalize_stage)
        
        input_data = "cached_audio.wav"
        
        # First execution
        start_time = time.time()
        result1 = pipeline.execute(input_data)
        first_duration = time.time() - start_time
        
        # Second execution (should use cache)
        start_time = time.time()
        result2 = pipeline.execute(input_data)
        second_duration = time.time() - start_time
        
        assert result1.success is True
        assert result2.success is True
        assert second_duration < first_duration  # Cache should be faster
    
    def test_pipeline_metrics(self):
        """Test pipeline performance metrics"""
        config = PipelineConfig(collect_metrics=True)
        pipeline = AudioPipeline(config=config)
        pipeline.add_stage(self.load_stage)
        pipeline.add_stage(self.normalize_stage)
        pipeline.add_stage(self.feature_stage)
        
        result = pipeline.execute("test_audio.wav")
        
        assert result.success is True
        assert result.metrics is not None
        assert isinstance(result.metrics, PipelineMetrics)
        
        # Check metrics
        assert result.metrics.total_execution_time_ms > 0
        assert result.metrics.total_memory_usage_mb > 0
        assert result.metrics.stages_executed == 3
        assert len(result.metrics.stage_timings) == 3


class TestDataFlowManager:
    """
    Industrial-grade testing for DataFlowManager class
    
    Test Coverage:
    - Data transformation between stages
    - Type checking and validation
    - Memory management
    - Data serialization/deserialization
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_dataflow_initialization(self):
        """Test DataFlowManager initialization"""
        manager = DataFlowManager()
        
        assert manager is not None
        assert hasattr(manager, 'type_registry')
        assert hasattr(manager, 'transformation_rules')
    
    def test_register_transformation(self):
        """Test registering data transformations"""
        manager = DataFlowManager()
        
        # Register transformation from numpy array to list
        def array_to_list(data):
            return data.tolist()
        
        manager.register_transformation(
            from_type=np.ndarray,
            to_type=list,
            transform_func=array_to_list
        )
        
        # Test transformation
        test_array = np.array([1, 2, 3, 4, 5])
        result = manager.transform_data(test_array, target_type=list)
        
        assert isinstance(result, list)
        assert result == [1, 2, 3, 4, 5]
    
    def test_automatic_type_conversion(self):
        """Test automatic type conversion"""
        manager = DataFlowManager()
        
        # Test built-in conversions
        test_cases = [
            (5, float, 5.0),
            ([1, 2, 3], np.ndarray, np.array([1, 2, 3])),
            ("123", int, 123),
            (3.14, str, "3.14")
        ]
        
        for input_data, target_type, expected in test_cases:
            result = manager.transform_data(input_data, target_type)
            
            if isinstance(expected, np.ndarray):
                np.testing.assert_array_equal(result, expected)
            else:
                assert result == expected
            assert isinstance(result, target_type)
    
    def test_data_validation(self):
        """Test data validation"""
        manager = DataFlowManager()
        
        # Add validation rules
        def validate_positive_array(data):
            if isinstance(data, np.ndarray):
                return np.all(data >= 0)
            return False
        
        manager.add_validation_rule(np.ndarray, validate_positive_array)
        
        # Test valid data
        valid_array = np.array([1, 2, 3, 4])
        assert manager.validate_data(valid_array) is True
        
        # Test invalid data
        invalid_array = np.array([-1, 2, 3, 4])
        assert manager.validate_data(invalid_array) is False
    
    def test_memory_efficient_transfer(self):
        """Test memory-efficient data transfer"""
        manager = DataFlowManager()
        
        # Create large data
        large_array = np.random.randn(1000000)  # 1M elements
        
        # Monitor memory usage
        initial_memory = psutil.Process().memory_info().rss
        
        # Transfer data (should use memory mapping or similar optimization)
        transferred = manager.transfer_data(large_array, copy=False)
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal for no-copy transfer
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
        np.testing.assert_array_equal(transferred, large_array)


class TestPipelineOptimizer:
    """
    Industrial-grade testing for PipelineOptimizer class
    
    Test Coverage:
    - Stage reordering optimization
    - Parallel execution optimization
    - Resource allocation optimization
    - Performance profiling
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_optimizer_initialization(self):
        """Test PipelineOptimizer initialization"""
        optimizer = PipelineOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimization_strategies')
        assert hasattr(optimizer, 'performance_history')
    
    def test_stage_dependency_analysis(self):
        """Test stage dependency analysis"""
        optimizer = PipelineOptimizer()
        
        # Create stages with dependencies
        stage_a = PipelineStage("stage_a", lambda x: x, str, str)
        stage_b = PipelineStage("stage_b", lambda x: x, str, str)
        stage_c = PipelineStage("stage_c", lambda x: x, str, str)
        
        # Define dependencies: C depends on B, B depends on A
        dependencies = {
            "stage_c": ["stage_b"],
            "stage_b": ["stage_a"],
            "stage_a": []
        }
        
        stages = [stage_c, stage_a, stage_b]  # Wrong order
        optimized_order = optimizer.optimize_stage_order(stages, dependencies)
        
        # Should reorder to A -> B -> C
        assert optimized_order[0].name == "stage_a"
        assert optimized_order[1].name == "stage_b"
        assert optimized_order[2].name == "stage_c"
    
    def test_parallel_execution_optimization(self):
        """Test parallel execution optimization"""
        optimizer = PipelineOptimizer()
        
        # Create independent stages that can run in parallel
        stage1 = PipelineStage("independent_1", lambda x: x, np.ndarray, np.ndarray)
        stage2 = PipelineStage("independent_2", lambda x: x, np.ndarray, np.ndarray)
        stage3 = PipelineStage("merger", lambda x: x, list, np.ndarray)
        
        stages = [stage1, stage2, stage3]
        dependencies = {
            "independent_1": [],
            "independent_2": [],
            "merger": ["independent_1", "independent_2"]
        }
        
        parallel_groups = optimizer.identify_parallel_groups(stages, dependencies)
        
        # Should identify that stage1 and stage2 can run in parallel
        assert len(parallel_groups) >= 1
        parallel_stage_names = {stage.name for group in parallel_groups for stage in group}
        assert "independent_1" in parallel_stage_names
        assert "independent_2" in parallel_stage_names
    
    def test_resource_allocation_optimization(self):
        """Test resource allocation optimization"""
        optimizer = PipelineOptimizer()
        
        # Create stages with different resource requirements
        cpu_intensive = PipelineStage(
            "cpu_heavy", 
            lambda x: x, 
            np.ndarray, 
            np.ndarray,
            metadata={"cpu_bound": True, "memory_mb": 100}
        )
        
        memory_intensive = PipelineStage(
            "memory_heavy",
            lambda x: x,
            np.ndarray,
            np.ndarray,
            metadata={"cpu_bound": False, "memory_mb": 1000}
        )
        
        io_intensive = PipelineStage(
            "io_heavy",
            lambda x: x,
            str,
            np.ndarray,
            metadata={"io_bound": True, "memory_mb": 50}
        )
        
        stages = [cpu_intensive, memory_intensive, io_intensive]
        
        # Get resource allocation recommendations
        allocation = optimizer.optimize_resource_allocation(stages)
        
        assert allocation is not None
        assert "worker_allocation" in allocation
        assert "memory_allocation" in allocation
        assert "execution_strategy" in allocation
    
    def test_performance_profiling(self):
        """Test performance profiling and optimization"""
        optimizer = PipelineOptimizer()
        
        # Create pipeline with known performance characteristics
        fast_stage = PipelineStage(
            "fast", 
            lambda x: x, 
            str, 
            str,
            metadata={"expected_time_ms": 10}
        )
        
        slow_stage = PipelineStage(
            "slow",
            lambda x: time.sleep(0.1) or x,
            str,
            str,
            metadata={"expected_time_ms": 100}
        )
        
        stages = [slow_stage, fast_stage]
        
        # Profile execution
        profile_results = optimizer.profile_pipeline_execution(stages, "test_input")
        
        assert profile_results is not None
        assert "stage_timings" in profile_results
        assert "bottlenecks" in profile_results
        assert "optimization_suggestions" in profile_results
        
        # Should identify slow stage as bottleneck
        bottlenecks = profile_results["bottlenecks"]
        assert any("slow" in bottleneck for bottleneck in bottlenecks)


class TestErrorRecoveryManager:
    """
    Industrial-grade testing for ErrorRecoveryManager class
    
    Test Coverage:
    - Error detection and classification
    - Recovery strategies
    - Fallback mechanisms
    - Circuit breaker patterns
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
    
    def test_error_recovery_initialization(self):
        """Test ErrorRecoveryManager initialization"""
        manager = ErrorRecoveryManager()
        
        assert manager is not None
        assert hasattr(manager, 'recovery_strategies')
        assert hasattr(manager, 'error_history')
        assert hasattr(manager, 'circuit_breakers')
    
    def test_retry_strategy(self):
        """Test retry strategy for transient errors"""
        manager = ErrorRecoveryManager()
        
        # Create a function that fails twice then succeeds
        call_count = 0
        def flaky_function(data):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ConnectionError("Temporary network error")
            return data.upper()
        
        # Execute with retry strategy
        result = manager.execute_with_recovery(
            func=flaky_function,
            args=("hello",),
            strategy="retry",
            max_retries=3,
            retry_delay=0.01
        )
        
        assert result.success is True
        assert result.output == "HELLO"
        assert result.attempts == 3
        assert call_count == 3
    
    def test_fallback_strategy(self):
        """Test fallback strategy for persistent errors"""
        manager = ErrorRecoveryManager()
        
        def failing_primary(data):
            raise ValueError("Primary function always fails")
        
        def fallback_function(data):
            return f"fallback_{data}"
        
        # Register fallback
        manager.register_fallback(failing_primary, fallback_function)
        
        # Execute with fallback
        result = manager.execute_with_recovery(
            func=failing_primary,
            args=("test",),
            strategy="fallback"
        )
        
        assert result.success is True
        assert result.output == "fallback_test"
        assert result.used_fallback is True
    
    def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for failing services"""
        manager = ErrorRecoveryManager()
        
        def unreliable_service(data):
            raise RuntimeError("Service is down")
        
        # Configure circuit breaker
        manager.configure_circuit_breaker(
            service_name="test_service",
            failure_threshold=3,
            recovery_timeout=1.0
        )
        
        # Execute multiple times to trigger circuit breaker
        results = []
        for i in range(5):
            result = manager.execute_with_circuit_breaker(
                service_name="test_service",
                func=unreliable_service,
                args=(f"data_{i}",)
            )
            results.append(result)
        
        # First 3 should attempt and fail
        for i in range(3):
            assert results[i].success is False
            assert "service is down" in results[i].error_message.lower()
        
        # Next calls should be circuit breaker open (fast fail)
        for i in range(3, 5):
            assert results[i].success is False
            assert "circuit breaker" in results[i].error_message.lower()
    
    def test_error_classification(self):
        """Test error classification and appropriate recovery"""
        manager = ErrorRecoveryManager()
        
        # Test different error types
        error_cases = [
            (ConnectionError("Network timeout"), "transient"),
            (FileNotFoundError("File missing"), "permanent"),
            (MemoryError("Out of memory"), "resource"),
            (ValueError("Invalid input"), "validation"),
            (RuntimeError("Unknown error"), "unknown")
        ]
        
        for error, expected_category in error_cases:
            category = manager.classify_error(error)
            assert category == expected_category
    
    def test_recovery_strategy_selection(self):
        """Test automatic recovery strategy selection"""
        manager = ErrorRecoveryManager()
        
        # Test strategy selection based on error type
        strategy_cases = [
            (ConnectionError("Timeout"), "retry"),
            (FileNotFoundError("Missing"), "fallback"),
            (MemoryError("OOM"), "resource_management"),
            (ValueError("Invalid"), "validation_fix")
        ]
        
        for error, expected_strategy in strategy_cases:
            strategy = manager.select_recovery_strategy(error)
            assert strategy == expected_strategy


class TestPipelineConfig:
    """Test PipelineConfig data structure"""
    
    def test_config_creation(self):
        """Test PipelineConfig creation"""
        config = PipelineConfig(
            name="test_pipeline",
            parallel_execution=True,
            max_workers=8,
            timeout_seconds=60,
            enable_caching=True,
            collect_metrics=True
        )
        
        assert config.name == "test_pipeline"
        assert config.parallel_execution is True
        assert config.max_workers == 8
        assert config.timeout_seconds == 60
        assert config.enable_caching is True
        assert config.collect_metrics is True
    
    def test_config_validation(self):
        """Test config validation"""
        # Valid config
        valid_config = PipelineConfig(
            name="valid",
            max_workers=4,
            timeout_seconds=30
        )
        assert valid_config.is_valid()
        
        # Invalid config
        with pytest.raises(ValueError):
            PipelineConfig(
                name="",  # Empty name
                max_workers=0,  # Invalid worker count
                timeout_seconds=-1  # Invalid timeout
            )


class TestPipelineIntegration:
    """
    Integration tests for complete pipeline workflows
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment"""
        setup_test_environment()
        self.test_data_dir = TEST_CONFIG["test_data_dir"]
        
        # Create audio processor
        self.processor = AudioProcessor()
    
    def test_complete_audio_processing_pipeline(self):
        """Test complete audio processing pipeline"""
        # Create realistic audio processing pipeline
        load_stage = PipelineStage(
            name="load",
            processor_func=lambda path: self.processor.load_audio(str(path)),
            input_type=str,
            output_type=tuple
        )
        
        normalize_stage = PipelineStage(
            name="normalize",
            processor_func=lambda data: (data[0] / np.max(np.abs(data[0])), data[1]),
            input_type=tuple,
            output_type=tuple
        )
        
        extract_features_stage = PipelineStage(
            name="features",
            processor_func=lambda data: self.processor.extract_features(data[0], data[1]),
            input_type=tuple,
            output_type=dict
        )
        
        # Create pipeline
        config = PipelineConfig(
            name="audio_processing",
            collect_metrics=True,
            enable_caching=False
        )
        pipeline = AudioPipeline(config=config)
        
        # Add stages
        pipeline.add_stage(load_stage)
        pipeline.add_stage(normalize_stage)
        pipeline.add_stage(extract_features_stage)
        
        # Execute pipeline
        audio_file = self.test_data_dir / "pure_tone_440hz.wav"
        result = pipeline.execute(str(audio_file))
        
        # Verify results
        assert result.success is True
        assert len(result.stage_results) == 3
        assert isinstance(result.final_output, dict)
        assert "mfcc" in result.final_output
        assert result.metrics.total_execution_time_ms > 0
    
    def test_parallel_processing_pipeline(self):
        """Test parallel processing pipeline"""
        # Create stages that can run in parallel
        feature_extractors = []
        
        for feature_type in ["mfcc", "spectral_centroid", "zero_crossing_rate"]:
            stage = PipelineStage(
                name=f"extract_{feature_type}",
                processor_func=lambda audio, ft=feature_type: {ft: np.random.randn(100)},
                input_type=np.ndarray,
                output_type=dict
            )
            feature_extractors.append(stage)
        
        # Create pipeline with parallel execution
        config = PipelineConfig(
            name="parallel_features",
            parallel_execution=True,
            max_workers=3
        )
        pipeline = AudioPipeline(config=config)
        
        # Add load stage
        load_stage = PipelineStage(
            name="load",
            processor_func=lambda path: np.random.randn(44100),
            input_type=str,
            output_type=np.ndarray
        )
        pipeline.add_stage(load_stage)
        
        # Add parallel feature extraction stages
        pipeline.add_parallel_group(feature_extractors)
        
        # Add merger stage
        merge_stage = PipelineStage(
            name="merge_features",
            processor_func=lambda results: {k: v for d in results for k, v in d.items()},
            input_type=list,
            output_type=dict
        )
        pipeline.add_stage(merge_stage)
        
        # Execute pipeline
        result = pipeline.execute("dummy_audio.wav")
        
        # Verify parallel execution worked
        assert result.success is True
        assert isinstance(result.final_output, dict)
        assert len(result.final_output) == 3  # Should have all 3 feature types
    
    def test_pipeline_with_ml_models(self):
        """Test pipeline integration with ML models"""
        # Create ML model stage
        def mock_ml_prediction(features):
            # Simulate ML model prediction
            return {
                "genre": "rock",
                "confidence": 0.85,
                "probabilities": [0.1, 0.85, 0.05]
            }
        
        ml_stage = PipelineStage(
            name="genre_classification",
            processor_func=mock_ml_prediction,
            input_type=dict,
            output_type=dict
        )
        
        # Create complete pipeline
        pipeline = AudioPipeline()
        
        # Add stages
        pipeline.add_stage(PipelineStage(
            "load", lambda p: np.random.randn(44100), str, np.ndarray
        ))
        pipeline.add_stage(PipelineStage(
            "features", lambda a: {"mfcc": np.random.randn(13, 100)}, np.ndarray, dict
        ))
        pipeline.add_stage(ml_stage)
        
        # Execute
        result = pipeline.execute("test_audio.wav")
        
        assert result.success is True
        assert "genre" in result.final_output
        assert "confidence" in result.final_output
        assert result.final_output["genre"] == "rock"
    
    def test_error_recovery_in_pipeline(self):
        """Test error recovery mechanisms in pipeline"""
        # Create pipeline with error recovery
        recovery_manager = ErrorRecoveryManager()
        
        config = PipelineConfig(
            name="error_recovery_test",
            enable_error_recovery=True
        )
        pipeline = AudioPipeline(config=config, error_manager=recovery_manager)
        
        # Add stages with potential failures
        unreliable_stage = PipelineStage(
            name="unreliable",
            processor_func=lambda x: 1/0 if x == "fail" else x.upper(),
            input_type=str,
            output_type=str
        )
        
        # Register fallback for unreliable stage
        def fallback_processor(data):
            return f"fallback_{data}"
        
        recovery_manager.register_fallback(unreliable_stage.processor_func, fallback_processor)
        
        pipeline.add_stage(unreliable_stage)
        
        # Test with failing input
        result = pipeline.execute("fail")
        
        # Should succeed with fallback
        assert result.success is True
        assert result.final_output == "fallback_fail"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
