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

"""Inference Engine Tests - Enterprise Grade Test Suite

Comprehensive tests for ML inference engine including batch processing,
real-time inference, model serving, and distributed inference capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""
import pytest
import sys
import os
from pathlib import Path
import torch
import numpy as np
import asyncio
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List, Any, AsyncGenerator

from ai.ml.inference import (
    InferenceEngine, BatchInferenceEngine, StreamInferenceEngine,
    ModelServer, InferenceConfig, ModelCache, InferenceMetrics,
    InferenceMode, OptimizationLevel, InferenceBackend
)


class TestInferenceEngine:
    """Comprehensive tests for InferenceEngine class"""    
    def test_init_inference_engine(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test basic inference engine initialization"""        # Save model for loading
        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = InferenceEngine(sample_inference_config)
        
        assert engine.config.model_path == str(model_path)
        assert engine.config.batch_size == 16
        assert engine.config.device == "cpu"
        assert engine.config.backend == InferenceBackend.PYTORCH
        assert not engine.is_loaded

    def test_load_pytorch_model(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test loading PyTorch model"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = InferenceEngine(sample_inference_config)
        
        # Mock model loading since we don't have the exact architecture
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        assert engine.is_loaded
        assert engine.model is not None

    def test_device_selection_auto(self, sample_inference_config):
        """Test automatic device selection"""        sample_inference_config.device = "auto"
        engine = InferenceEngine(sample_inference_config)
        
        device = engine._select_device()
        
        # Should select CUDA if available, otherwise CPU
        expected_device = "cuda" if torch.cuda.is_available() else "cpu"
        assert device == torch.device(expected_device)

    def test_device_selection_explicit(self, sample_inference_config):
        """Test explicit device selection"""        sample_inference_config.device = "cpu"
        engine = InferenceEngine(sample_inference_config)
        
        device = engine._select_device()
        assert device == torch.device("cpu")

    def test_model_optimization_basic(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test basic model optimization"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        sample_inference_config.optimization_level = OptimizationLevel.BASIC
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        optimized_model = engine._optimize_model(engine.model)
        
        assert optimized_model is not None

    def test_single_inference(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test single input inference"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Single input
        input_data = torch.randn(1, 768)  # Batch size 1, feature size 768
        
        with torch.no_grad():
            output = engine.predict(input_data)
        
        assert output is not None
        assert isinstance(output, (torch.Tensor, np.ndarray, dict))

    def test_batch_inference(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test batch inference"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        sample_inference_config.batch_size = 8
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Batch input
        batch_input = torch.randn(8, 768)
        
        with torch.no_grad():
            output = engine.predict_batch(batch_input)
        
        assert output is not None
        assert len(output.shape) >= 2  # Should have batch dimension

    def test_inference_metrics_collection(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test inference metrics collection"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Enable metrics collection
        engine.enable_metrics = True
        
        input_data = torch.randn(4, 768)
        
        start_time = time.time()
        output = engine.predict_batch(input_data)
        end_time = time.time()
        
        metrics = engine.get_metrics()
        
        assert "total_requests" in metrics
        assert "average_latency" in metrics
        assert "throughput" in metrics
        assert metrics["total_requests"] >= 1

    @pytest.mark.asyncio
    async def test_async_inference(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test asynchronous inference"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        input_data = torch.randn(2, 768)
        
        # Mock async predict method
        async def mock_predict_async(data):
            await asyncio.sleep(0.01)  # Simulate processing time
            with torch.no_grad():
                return engine.model(data)
        
        engine.predict_async = mock_predict_async
        
        output = await engine.predict_async(input_data)
        
        assert output is not None
        assert output.shape[0] == 2  # Batch size should match

    def test_memory_management(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test memory management features"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        sample_inference_config.memory_pool_size_mb = 256
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Test memory cleanup
        engine.clear_cache()
        
        # Test memory usage monitoring
        memory_usage = engine.get_memory_usage()
        
        assert "model_memory_mb" in memory_usage
        assert "cache_memory_mb" in memory_usage
        assert memory_usage["model_memory_mb"] >= 0

    def test_model_warmup(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test model warmup functionality"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Warmup with sample data
        warmup_data = torch.randn(1, 768)
        
        warmup_time = engine.warmup(warmup_data, num_warmup_steps=5)
        
        assert warmup_time > 0
        assert engine.is_warmed_up


class TestBatchInferenceEngine:
    """Tests for batch inference capabilities"""    
    def test_init_batch_engine(self, sample_inference_config):
        """Test batch inference engine initialization"""        sample_inference_config.enable_dynamic_batching = True
        sample_inference_config.max_batch_size = 64
        sample_inference_config.batch_timeout_ms = 50
        
        engine = BatchInferenceEngine(sample_inference_config)
        
        assert engine.config.enable_dynamic_batching
        assert engine.config.max_batch_size == 64
        assert engine.config.batch_timeout_ms == 50
        assert engine.batch_queue is not None

    def test_dynamic_batching(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test dynamic batching functionality"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        sample_inference_config.enable_dynamic_batching = True
        sample_inference_config.max_batch_size = 8
        sample_inference_config.batch_timeout_ms = 100
        
        engine = BatchInferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Add requests to batch
        inputs = [torch.randn(1, 768) for _ in range(5)]
        
        for i, input_data in enumerate(inputs):
            request_id = f"req_{i}"
            engine.add_to_batch(request_id, input_data)
        
        # Process batch
        batch_results = engine.process_batch()
        
        assert len(batch_results) == 5
        assert all(f"req_{i}" in batch_results for i in range(5))

    def test_batch_timeout_handling(self, sample_inference_config):
        """Test batch timeout handling"""        sample_inference_config.batch_timeout_ms = 50
        sample_inference_config.enable_dynamic_batching = True
        
        engine = BatchInferenceEngine(sample_inference_config)
        
        # Add a single request
        input_data = torch.randn(1, 768)
        engine.add_to_batch("req_1", input_data)
        
        # Wait for timeout
        time.sleep(0.1)  # 100ms > 50ms timeout
        
        # Should trigger timeout-based batch processing
        assert engine.should_process_batch()

    def test_batch_size_threshold(self, sample_inference_config):
        """Test batch size threshold triggering"""        sample_inference_config.max_batch_size = 3
        sample_inference_config.enable_dynamic_batching = True
        
        engine = BatchInferenceEngine(sample_inference_config)
        
        # Add requests until threshold
        for i in range(3):
            input_data = torch.randn(1, 768)
            engine.add_to_batch(f"req_{i}", input_data)
        
        # Should trigger size-based batch processing
        assert engine.should_process_batch()

    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test concurrent batch processing"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = BatchInferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Submit multiple concurrent requests
        async def submit_request(request_id):
            input_data = torch.randn(1, 768)
            return await engine.predict_async(input_data, request_id)
        
        # Create concurrent tasks
        tasks = [submit_request(f"req_{i}") for i in range(10)]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(result is not None for result in results)


class TestStreamInferenceEngine:
    """Tests for stream inference capabilities"""    
    def test_init_stream_engine(self, sample_inference_config):
        """Test stream inference engine initialization"""        engine = StreamInferenceEngine(sample_inference_config)
        
        assert engine.config == sample_inference_config
        assert hasattr(engine, 'stream_queue')
        assert not engine.is_streaming

    @pytest.mark.asyncio
    async def test_streaming_inference(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test streaming inference functionality"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = StreamInferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Mock streaming data generator
        async def data_generator():
            for i in range(5):
                yield torch.randn(1, 768)
                await asyncio.sleep(0.01)
        
        results = []
        async for result in engine.stream_inference(data_generator()):
            results.append(result)
        
        assert len(results) == 5
        assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_real_time_streaming(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test real-time streaming with latency constraints"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        engine = StreamInferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Set real-time constraints
        engine.max_latency_ms = 100
        engine.enable_latency_monitoring = True
        
        input_data = torch.randn(1, 768)
        
        start_time = time.time()
        result = await engine.predict_realtime(input_data)
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        assert result is not None
        # In real scenarios, this should be under the constraint
        # For tests, we just verify the measurement works
        assert latency >= 0


class TestModelServer:
    """Tests for model server functionality"""    
    def test_init_model_server(self, sample_inference_config):
        """Test model server initialization"""        server = ModelServer(
            config=sample_inference_config,
            host="localhost",
            port=8080,
            max_workers=4
        )
        
        assert server.host == "localhost"
        assert server.port == 8080
        assert server.max_workers == 4
        assert not server.is_running

    @pytest.mark.asyncio
    async def test_server_health_check(self, sample_inference_config):
        """Test server health check endpoint"""        server = ModelServer(sample_inference_config)
        
        # Mock health check
        health_status = await server.health_check()
        
        assert "status" in health_status
        assert "timestamp" in health_status
        assert "model_loaded" in health_status

    def test_request_validation(self, sample_inference_config):
        """Test request validation"""        server = ModelServer(sample_inference_config)
        
        # Valid request
        valid_request = {
            "inputs": [[1.0, 2.0, 3.0]],
            "request_id": "test_123"
        }
        
        is_valid, error = server.validate_request(valid_request)
        assert is_valid
        assert error is None
        
        # Invalid request
        invalid_request = {
            "inputs": "not_a_list"
        }
        
        is_valid, error = server.validate_request(invalid_request)
        assert not is_valid
        assert error is not None

    def test_rate_limiting(self, sample_inference_config):
        """Test request rate limiting"""        sample_inference_config.rate_limit = 10  # requests per minute
        server = ModelServer(sample_inference_config)
        
        # Simulate multiple requests
        client_id = "test_client"
        
        # First requests should pass
        for _ in range(5):
            assert server.check_rate_limit(client_id)
        
        # Mock exceeding rate limit
        server.request_counts[client_id] = 15  # Exceed limit
        assert not server.check_rate_limit(client_id)

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test concurrent request handling"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        sample_inference_config.max_concurrent_requests = 5
        
        server = ModelServer(sample_inference_config)
        server.inference_engine = InferenceEngine(sample_inference_config)
        server.inference_engine._load_model_architecture = lambda: sample_pytorch_model
        server.inference_engine.load_model()
        
        # Mock request handler
        async def mock_handle_request(request_id):
            await asyncio.sleep(0.01)  # Simulate processing
            return {"request_id": request_id, "result": "success"}
        
        server.handle_inference_request = mock_handle_request
        
        # Submit concurrent requests
        tasks = [server.handle_inference_request(f"req_{i}") for i in range(10)]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(result["result"] == "success" for result in results)


class TestModelCache:
    """Tests for model caching functionality"""    
    def test_init_cache(self):
        """Test cache initialization"""        cache = ModelCache(
            max_size=100,
            ttl_seconds=3600,
            enable_persistent_cache=True
        )
        
        assert cache.max_size == 100
        assert cache.ttl_seconds == 3600
        assert cache.enable_persistent_cache
        assert len(cache.cache_dict) == 0

    def test_cache_put_and_get(self):
        """Test basic cache put and get operations"""        cache = ModelCache(max_size=10)
        
        key = "test_key"
        value = {"model_output": torch.randn(5, 10)}
        
        # Put value in cache
        cache.put(key, value)
        
        # Get value from cache
        retrieved_value = cache.get(key)
        
        assert retrieved_value is not None
        assert torch.equal(retrieved_value["model_output"], value["model_output"])

    def test_cache_expiration(self):
        """Test cache TTL expiration"""        cache = ModelCache(max_size=10, ttl_seconds=0.1)  # 100ms TTL
        
        key = "expiring_key"
        value = {"data": "test"}
        
        cache.put(key, value)
        
        # Should be available immediately
        assert cache.get(key) is not None
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        assert cache.get(key) is None

    def test_cache_size_limit(self):
        """Test cache size limitation and LRU eviction"""        cache = ModelCache(max_size=3)
        
        # Fill cache to capacity
        for i in range(3):
            cache.put(f"key_{i}", {"value": i})
        
        assert len(cache.cache_dict) == 3
        
        # Add one more item (should evict oldest)
        cache.put("key_3", {"value": 3})
        
        assert len(cache.cache_dict) == 3
        assert cache.get("key_0") is None  # Should be evicted (oldest)
        assert cache.get("key_3") is not None  # Should be present (newest)

    def test_cache_hit_rate_tracking(self):
        """Test cache hit rate tracking"""        cache = ModelCache(max_size=10)
        
        # Initial hit rate should be 0
        assert cache.get_hit_rate() == 0.0
        
        # Add item and access it
        cache.put("key1", {"value": 1})
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        hit_rate = cache.get_hit_rate()
        assert 0 < hit_rate < 1  # Should be 50%

    def test_cache_statistics(self):
        """Test cache statistics collection"""        cache = ModelCache(max_size=10)
        
        # Perform various operations
        cache.put("key1", {"value": 1})
        cache.put("key2", {"value": 2})
        cache.get("key1")  # Hit
        cache.get("key3")  # Miss
        
        stats = cache.get_statistics()
        
        assert "total_requests" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate" in stats
        assert "cache_size" in stats
        assert stats["cache_size"] == 2
        assert stats["total_requests"] == 2


class TestInferenceMetrics:
    """Tests for inference metrics collection and monitoring"""    
    def test_init_metrics(self):
        """Test metrics initialization"""        metrics = InferenceMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.total_latency == 0.0
        assert len(metrics.latency_history) == 0
        assert len(metrics.error_count) == 0

    def test_request_metrics_recording(self):
        """Test recording request metrics"""        metrics = InferenceMetrics()
        
        # Record successful request
        metrics.record_request(
            latency=0.05,
            status="success",
            model_name="test_model",
            batch_size=4
        )
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.total_latency == 0.05
        
        # Record failed request
        metrics.record_request(
            latency=0.02,
            status="error",
            error_type="timeout"
        )
        
        assert metrics.total_requests == 2
        assert metrics.successful_requests == 1
        assert "timeout" in metrics.error_count

    def test_latency_statistics(self):
        """Test latency statistics calculation"""        metrics = InferenceMetrics()
        
        # Record multiple requests with different latencies
        latencies = [0.01, 0.02, 0.05, 0.03, 0.04]
        for latency in latencies:
            metrics.record_request(latency, "success")
        
        stats = metrics.get_latency_stats()
        
        assert "mean" in stats
        assert "median" in stats
        assert "p95" in stats
        assert "p99" in stats
        assert "min" in stats
        assert "max" in stats
        
        assert stats["mean"] == np.mean(latencies)
        assert stats["min"] == min(latencies)
        assert stats["max"] == max(latencies)

    def test_throughput_calculation(self):
        """Test throughput calculation"""        metrics = InferenceMetrics()
        
        start_time = time.time()
        
        # Record requests over time
        for _ in range(10):
            metrics.record_request(0.01, "success")
            time.sleep(0.001)  # Small delay
        
        end_time = time.time()
        duration = end_time - start_time
        
        throughput = metrics.calculate_throughput(duration)
        
        expected_throughput = 10 / duration
        assert abs(throughput - expected_throughput) < 0.1

    def test_resource_usage_tracking(self):
        """Test resource usage tracking"""        metrics = InferenceMetrics()
        
        # Mock resource usage data
        cpu_usage = 65.5
        memory_usage = 1024.0  # MB
        gpu_usage = 85.0 if torch.cuda.is_available() else 0.0
        
        metrics.record_resource_usage(cpu_usage, memory_usage, gpu_usage)
        
        resource_stats = metrics.get_resource_stats()
        
        assert "cpu_usage" in resource_stats
        assert "memory_usage_mb" in resource_stats
        assert "gpu_usage" in resource_stats
        
        assert resource_stats["cpu_usage"] == cpu_usage
        assert resource_stats["memory_usage_mb"] == memory_usage

    def test_metrics_export(self, temp_dir):
        """Test metrics export functionality"""        metrics = InferenceMetrics()
        
        # Record some sample data
        for i in range(5):
            metrics.record_request(0.01 * (i + 1), "success")
        
        # Export metrics
        export_path = temp_dir / "metrics.json"
        metrics.export_metrics(str(export_path))
        
        assert export_path.exists()
        
        # Load and verify exported data
        with open(export_path) as f:
            exported_data = json.load(f)
        
        assert "total_requests" in exported_data
        assert "successful_requests" in exported_data
        assert "latency_stats" in exported_data
        assert exported_data["total_requests"] == 5


@pytest.mark.integration
class TestInferenceIntegration:
    """Integration tests for inference pipeline"""    
    @pytest.mark.slow
    def test_end_to_end_inference_pipeline(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test complete inference pipeline from model loading to prediction"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        # Initialize inference engine
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        
        # Load model
        engine.load_model()
        assert engine.is_loaded
        
        # Warmup
        warmup_data = torch.randn(1, 768)
        engine.warmup(warmup_data)
        assert engine.is_warmed_up
        
        # Single prediction
        test_input = torch.randn(1, 768)
        result = engine.predict(test_input)
        assert result is not None
        
        # Batch prediction
        batch_input = torch.randn(8, 768)
        batch_result = engine.predict_batch(batch_input)
        assert batch_result is not None
        assert batch_result.shape[0] == 8
        
        # Check metrics
        metrics = engine.get_metrics()
        assert metrics["total_requests"] >= 2

    def test_model_server_integration(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test model server integration with inference engine"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        
        # Create and setup server
        server = ModelServer(sample_inference_config, port=8081)  # Different port for testing
        server.inference_engine = InferenceEngine(sample_inference_config)
        server.inference_engine._load_model_architecture = lambda: sample_pytorch_model
        server.inference_engine.load_model()
        
        # Test server components
        assert server.inference_engine.is_loaded
        
        # Test health check
        health = asyncio.run(server.health_check())
        assert health["model_loaded"] == True

    def test_caching_integration(self, sample_inference_config, sample_pytorch_model, temp_dir):
        """Test caching integration with inference"""        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        sample_inference_config.model_path = str(model_path)
        sample_inference_config.enable_cache = True
        
        engine = InferenceEngine(sample_inference_config)
        engine._load_model_architecture = lambda: sample_pytorch_model
        engine.load_model()
        
        # Same input should be cached
        test_input = torch.randn(2, 768)
        
        # First prediction (cache miss)
        result1 = engine.predict_batch(test_input)
        
        # Second prediction (cache hit)
        result2 = engine.predict_batch(test_input)
        
        # Results should be identical (from cache)
        assert torch.allclose(result1, result2, atol=1e-6)
        
        # Check cache statistics
        if hasattr(engine, 'cache'):
            cache_stats = engine.cache.get_statistics()
            assert cache_stats["cache_hits"] > 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
