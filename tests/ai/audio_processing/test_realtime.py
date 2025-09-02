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

"""⚡ Real-time Tests - Industrial-Grade Real-time Audio Processing Testing Suite

Comprehensive testing for real-time audio processing including:
- RealtimeProcessor validation
- Low-latency processing
- Buffer management
- Stream processing
- Performance constraints

Created by Expert Team: Real-time Systems Engineer + Performance Specialist + Audio Engineer
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import time
import threading
import asyncio
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the audio processing module
try:
    from ai.audio_processing.realtime import (
        RealTimeAudioEngine, RealTimeConfig, RealTimeProcessor,
        AudioBuffer, PerformanceMetrics, AudioDeviceInfo,
        ProcessingLatency, BufferMode, AudioBackend,
        create_streaming_engine, create_gaming_engine, create_podcast_engine
    )
    from ai.audio_processing.core import AudioProcessor
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))
    from ai.audio_processing.realtime import (
        RealTimeAudioEngine, RealTimeConfig, RealTimeProcessor,
        AudioBuffer, PerformanceMetrics, AudioDeviceInfo,
        ProcessingLatency, BufferMode, AudioBackend,
        create_streaming_engine, create_gaming_engine, create_podcast_engine
    )
    from ai.audio_processing.core import AudioProcessor

from . import TEST_CONFIG, setup_test_environment


class TestRealtimeProcessor:
    """
    Industrial-grade testing for RealtimeProcessor class
    
    Test Coverage:
    - Real-time processing initialization
    - Low-latency audio processing
    - Buffer size optimization
    - Processing time constraints
    - Thread safety
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment before each test"""
        setup_test_environment()
        
        # Create real-time configuration
        self.config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=256,
            max_latency_ms=10.0,
            enable_monitoring=True
        )
        self.processor = RealtimeProcessor(config=self.config)
    
    def test_initialization(self):
        """
Test RealtimeProcessor initialization"""
        processor = RealtimeProcessor()
        
        assert processor is not None
        assert hasattr(processor, 'config')
        assert hasattr(processor, 'buffer_manager')
        assert hasattr(processor, 'latency_monitor')
        assert hasattr(processor, 'processing_chain')
    
    def test_buffer_size_optimization(self):
        """
Test buffer size optimization for low latency"""
        # Test different buffer sizes
        buffer_sizes = [64, 128, 256, 512, 1024]
        latencies = []
        
        for buffer_size in buffer_sizes:
            config = RealtimeConfig(
                sample_rate=44100,
                buffer_size=buffer_size,
                max_latency_ms=20.0
            )
            processor = RealtimeProcessor(config=config)
            
            # Simulate processing
            test_buffer = np.random.randn(buffer_size)
            
            start_time = time.perf_counter()
            processed = processor.process_buffer(test_buffer)
            end_time = time.perf_counter()
            
            processing_time_ms = (end_time - start_time) * 1000
            latencies.append(processing_time_ms)
            
            # Verify processing
            assert len(processed) == buffer_size
            assert processing_time_ms < config.max_latency_ms
        
        # Generally, smaller buffers should have lower latency
        assert latencies[0] <= latencies[-1] * 2  # Allow some tolerance
    
    def test_low_latency_processing(self):
        """
Test low-latency processing requirements"""
        # Configure for very low latency
        low_latency_config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=64,  # Very small buffer
            max_latency_ms=5.0  # Very strict latency requirement
        )
        processor = RealtimeProcessor(config=low_latency_config)
        
        # Test multiple buffers
        latencies = []
        
        for _ in range(100):
            test_buffer = np.random.randn(64)
            
            start_time = time.perf_counter()
            processed = processor.process_buffer(test_buffer)
            end_time = time.perf_counter()
            
            processing_time_ms = (end_time - start_time) * 1000
            latencies.append(processing_time_ms)
            
            # Each buffer must meet latency requirement
            assert processing_time_ms < low_latency_config.max_latency_ms
        
        # Average latency should be well below limit
        average_latency = np.mean(latencies)
        assert average_latency < low_latency_config.max_latency_ms * 0.5
    
    def test_thread_safety(self):
        """
Test thread safety of real-time processing"""
        processed_buffers = []
        errors = []
        
        def process_worker(worker_id):
            try:
                for i in range(50):
                    test_buffer = np.random.randn(256) + worker_id * 0.1
                    processed = self.processor.process_buffer(test_buffer)
                    processed_buffers.append((worker_id, i, processed))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Create multiple worker threads
        threads = []
        for worker_id in range(4):
            thread = threading.Thread(target=process_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify thread safety
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(processed_buffers) == 4 * 50  # All buffers processed
        
        # Verify no corruption
        for worker_id, buffer_id, processed in processed_buffers:
            assert len(processed) == 256
            assert not np.any(np.isnan(processed))
            assert not np.any(np.isinf(processed))
    
    def test_processing_chain_performance(self):
        """Test processing chain performance under real-time constraints"""
        # Create processing chain with multiple stages
        def gain_stage(buffer):
        try:
            logger.info(f"Executing gain_stage")
            
            # Implementation for gain_stage
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing filter_stage")
            
            # Implementation for filter_stage
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing limiter_stage")
            
            # Implementation for limiter_stage
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"limiter_stage completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"limiter_stage failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"filter_stage completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"filter_stage failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"gain_stage completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"gain_stage failed: {e}")
            raise
        def filter_stage(buffer):
            # Simple high-pass filter
            return np.diff(buffer, prepend=buffer[0])
        
        def limiter_stage(buffer):
            return np.tanh(buffer)
        
        # Add stages to processing chain
        self.processor.add_processing_stage("gain", gain_stage)
        self.processor.add_processing_stage("filter", filter_stage)
        self.processor.add_processing_stage("limiter", limiter_stage)
        
        # Test processing chain
        test_buffer = np.random.randn(256)
        
        start_time = time.perf_counter()
        processed = self.processor.process_buffer(test_buffer)
        end_time = time.perf_counter()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        # Verify processing chain worked
        assert len(processed) == len(test_buffer)
        assert processing_time_ms < self.config.max_latency_ms
        
        # Verify processing stages were applied
        assert not np.array_equal(processed, test_buffer)  # Should be different
    
    def test_dynamic_buffer_adjustment(self):
        """Test dynamic buffer size adjustment based on performance"""
        # Start with large buffer
        adaptive_config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=1024,
            max_latency_ms=15.0,
            enable_adaptive_buffering=True
        )
        processor = RealtimeProcessor(config=adaptive_config)
        
        # Process multiple buffers and monitor performance
        processing_times = []
        
        for i in range(50):
            test_buffer = np.random.randn(processor.config.buffer_size)
            
            start_time = time.perf_counter()
            processed = processor.process_buffer(test_buffer)
            end_time = time.perf_counter()
            
            processing_time_ms = (end_time - start_time) * 1000
            processing_times.append(processing_time_ms)
            
            # Update performance stats
            processor.update_performance_stats(processing_time_ms)
        
        # Check if buffer size was adapted
        final_buffer_size = processor.config.buffer_size
        
        # If performance is good, buffer size might be reduced
        # If performance is poor, buffer size might be increased
        assert 64 <= final_buffer_size <= 2048  # Reasonable range


class TestBufferManager:
    """
    Industrial-grade testing for BufferManager class
    
    Test Coverage:
    - Buffer allocation and management
    - Circular buffer operations
    - Buffer overflow/underflow handling
    - Memory efficiency
    - Lock-free operations
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment"""
        setup_test_environment()
        self.buffer_size = 1024
        self.num_buffers = 8
        self.manager = BufferManager(
            buffer_size=self.buffer_size,
            num_buffers=self.num_buffers
        )
    
    def test_initialization(self):
        """
Test BufferManager initialization"""
        manager = BufferManager(buffer_size=512, num_buffers=4)
        
        assert manager is not None
        assert manager.buffer_size == 512
        assert manager.num_buffers == 4
        assert hasattr(manager, 'buffers')
        assert hasattr(manager, 'available_buffers')
        assert hasattr(manager, 'used_buffers')
    
    def test_buffer_allocation(self):
        """
Test buffer allocation and deallocation"""
        # Allocate buffer
        buffer = self.manager.allocate_buffer()
        
        assert buffer is not None
        assert len(buffer) == self.buffer_size
        assert isinstance(buffer, np.ndarray)
        
        # Check that buffer is tracked
        assert len(self.manager.available_buffers) == self.num_buffers - 1
        assert len(self.manager.used_buffers) == 1
        
        # Deallocate buffer
        self.manager.deallocate_buffer(buffer)
        
        assert len(self.manager.available_buffers) == self.num_buffers
        assert len(self.manager.used_buffers) == 0
    
    def test_buffer_pool_exhaustion(self):
        """
Test behavior when buffer pool is exhausted"""
        allocated_buffers = []
        
        # Allocate all buffers
        for i in range(self.num_buffers):
            buffer = self.manager.allocate_buffer()
            assert buffer is not None
            allocated_buffers.append(buffer)
        
        # Try to allocate one more (should fail gracefully)
        overflow_buffer = self.manager.allocate_buffer()
        
        # Should either return None or raise appropriate exception
        if overflow_buffer is not None:
        try:
            logger.info(f"Executing producer")
            
            # Implementation for producer
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"producer completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"producer failed: {e}")
            raise
        if overflow_buffer is not None:
            # If implementation creates new buffer, it should be valid
            assert len(overflow_buffer) == self.buffer_size
        
        # Clean up
        for buffer in allocated_buffers:
            self.manager.deallocate_buffer(buffer)
    
    def test_circular_buffer_operations(self):
        """
Test circular buffer operations"""
        circular_buffer = self.manager.create_circular_buffer(size=2048)
        
        # Test writing
        test_data = np.random.randn(512)
        bytes_written = circular_buffer.write(test_data)
        assert bytes_written == len(test_data)
        
        # Test reading
        read_data = circular_buffer.read(512)
        assert len(read_data) == 512
        np.testing.assert_array_equal(read_data, test_data)
        
        # Test wrap-around
        large_data = np.random.randn(1800)  # Larger than buffer
        bytes_written = circular_buffer.write(large_data)
        assert bytes_written <= 2048  # Should not exceed buffer size
    
    def test_lock_free_operations(self):
        """
Test lock-free buffer operations"""
        lock_free_queue = LockFreeQueue(capacity=16)
        
        # Test concurrent access
        def producer():
            for i in range(100):
                data = np.random.randn(256)
                while not lock_free_queue.push(data):
                    time.sleep(0.0001)  # Brief wait if queue full
        
        def consumer():
            consumed = []
            for i in range(100):
                while True:
                    data = lock_free_queue.pop()
                    if data is not None:
                        consumed.append(data)
                        break
                    time.sleep(0.0001)  # Brief wait if queue empty
            return consumed
        
        # Run producer and consumer concurrently
        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)
        
        producer_thread.start()
        consumer_thread.start()
        
        producer_thread.join()
        consumer_thread.join()
        
        # All items should be processed without deadlock
        assert True  # If we reach here, no deadlock occurred
    
    def test_memory_efficiency(self):
        """
Test memory efficiency of buffer management"""
        import psutil
        import gc
        
        # Measure initial memory
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss
        
        # Allocate and deallocate many buffers
        for cycle in range(10):
            buffers = []
            for i in range(self.num_buffers):
                buffer = self.manager.allocate_buffer()
                buffers.append(buffer)
                # Fill buffer with data
                buffer[:] = np.random.randn(self.buffer_size)
            
            # Deallocate all buffers
            for buffer in buffers:
                self.manager.deallocate_buffer(buffer)
        
        # Measure final memory
        gc.collect()
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (efficient reuse)
        max_expected_increase = 50 * 1024 * 1024  # 50 MB tolerance
        assert memory_increase < max_expected_increase


class TestStreamProcessor:
    """
    Industrial-grade testing for StreamProcessor class
    
    Test Coverage:
    - Continuous stream processing
    - Input/output stream management
    - Real-time callback handling
    - Stream synchronization
    - Error recovery
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment"""
        setup_test_environment()
        
        self.config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=512,
            max_latency_ms=12.0
        )
        self.stream_processor = StreamProcessor(config=self.config)
    
    def test_initialization(self):
        """
Test StreamProcessor initialization"""
        processor = StreamProcessor()
        
        assert processor is not None
        assert hasattr(processor, 'input_stream')
        assert hasattr(processor, 'output_stream')
        assert hasattr(processor, 'callback_processor')
        assert hasattr(processor, 'is_running')
    
    def test_stream_callback_processing(self):
        """
Test stream callback processing"""
        processed_buffers = []
        
        def test_callback(input_buffer):
            # Simple processing: apply gain
            processed = input_buffer * 0.5
            processed_buffers.append(processed.copy())
            return processed
        
        # Set callback
        self.stream_processor.set_processing_callback(test_callback)
        
        # Simulate stream input
        for i in range(10):
            input_buffer = np.random.randn(512)
            output_buffer = self.stream_processor.process_stream_buffer(input_buffer)
            
            assert len(output_buffer) == 512
            assert not np.array_equal(output_buffer, input_buffer)  # Should be processed
        
        # Verify all buffers were processed
        assert len(processed_buffers) == 10
    
    def test_stream_synchronization(self):
        """
Test stream synchronization between input and output"""
        input_timestamps = []
        output_timestamps = []
        
        def timestamping_callback(input_buffer):
            input_timestamps.append(time.perf_counter())
            # Add small processing delay
            time.sleep(0.001)
            output_timestamps.append(time.perf_counter())
            return input_buffer
        
        self.stream_processor.set_processing_callback(timestamping_callback)
        
        # Process multiple buffers
        for i in range(20):
            input_buffer = np.random.randn(512)
            self.stream_processor.process_stream_buffer(input_buffer)
            time.sleep(0.01)  # Simulate real-time intervals
        
        # Analyze timing
        processing_delays = [out - inp for inp, out in zip(input_timestamps, output_timestamps)]
        
        # All processing delays should be within acceptable range
        max_delay = max(processing_delays)
        assert max_delay < 0.01  # Should be less than 10ms
        
        # Timing should be consistent
        delay_std = np.std(processing_delays)
        assert delay_std < 0.005  # Low jitter
    
    def test_stream_error_recovery(self):
        """
Test error recovery in stream processing"""
        error_count = 0
        recovery_count = 0
        
        def error_prone_callback(input_buffer):
            nonlocal error_count
            if len(input_buffer) > 0 and input_buffer[0] > 0.9:
                error_count += 1
                raise RuntimeError("Simulated processing error")
            return input_buffer * 0.8
        
        def error_handler(error, input_buffer):
            nonlocal recovery_count
            recovery_count += 1
            # Return safe fallback processing
            return input_buffer * 0.5
        
        # Configure error handling
        self.stream_processor.set_processing_callback(error_prone_callback)
        self.stream_processor.set_error_handler(error_handler)
        
        # Process buffers, some will trigger errors
        processed_count = 0
        for i in range(100):
            # Create input that may trigger error
            input_buffer = np.random.randn(512)
            if i % 10 == 0:
                input_buffer[0] = 0.95  # Trigger error condition
            
            try:
                output = self.stream_processor.process_stream_buffer(input_buffer)
                processed_count += 1
                assert len(output) == 512
            except Exception as e:
                pytest.fail(f"Unhandled error: {e}")
        
        # Verify error recovery
        assert processed_count == 100  # All buffers should be processed
        assert error_count > 0  # Some errors should have occurred
        assert recovery_count == error_count  # All errors should be recovered
    
    def test_continuous_stream_processing(self):
        """Test continuous stream processing over time"""
        duration_seconds = 2.0
        sample_rate = self.config.sample_rate
        buffer_size = self.config.buffer_size
        
        total_samples = int(duration_seconds * sample_rate)
        num_buffers = total_samples // buffer_size
        
        processed_samples = 0
        start_time = time.perf_counter()
        
        def counting_callback(input_buffer):
            nonlocal processed_samples
            processed_samples += len(input_buffer)
            return input_buffer
        
        self.stream_processor.set_processing_callback(counting_callback)
        
        # Simulate continuous processing
        for i in range(num_buffers):
            input_buffer = np.random.randn(buffer_size)
            self.stream_processor.process_stream_buffer(input_buffer)
            
            # Maintain real-time pace
            expected_time = i * buffer_size / sample_rate
            actual_time = time.perf_counter() - start_time
            if actual_time < expected_time:
                time.sleep(expected_time - actual_time)
        
        end_time = time.perf_counter()
        actual_duration = end_time - start_time
        
        # Verify continuous processing
        assert processed_samples >= total_samples * 0.9  # Allow some tolerance
        assert actual_duration >= duration_seconds * 0.95  # Should take expected time
        assert actual_duration <= duration_seconds * 1.1   # Not too much overhead


class TestLatencyMonitor:
    """
    Industrial-grade testing for LatencyMonitor class
    
    Test Coverage:
    - Latency measurement accuracy
    - Performance statistics
    - Latency threshold monitoring
    - Performance trend analysis
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment"""
        setup_test_environment()
        self.monitor = LatencyMonitor(max_samples=1000)
    
    def test_initialization(self):
        """
Test LatencyMonitor initialization"""
        monitor = LatencyMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'latency_samples')
        assert hasattr(monitor, 'statistics')
        assert hasattr(monitor, 'thresholds')
    
    def test_latency_measurement(self):
        """
Test latency measurement accuracy"""
        # Simulate known processing delays
        known_delays = [0.001, 0.002, 0.005, 0.010, 0.003]  # Known delays in seconds
        
        for delay in known_delays:
            start_time = time.perf_counter()
            time.sleep(delay)
            end_time = time.perf_counter()
            
            measured_latency = self.monitor.record_latency(start_time, end_time)
            
            # Allow 1ms tolerance for measurement accuracy
            assert abs(measured_latency - delay * 1000) < 1.0  # Convert to ms
    
    def test_statistics_calculation(self):
        try:
            logger.info(f"Executing alert_handler")
            
            # Implementation for alert_handler
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"alert_handler completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"alert_handler failed: {e}")
            raise
            end_time = time.perf_counter()
            
            measured_latency = self.monitor.record_latency(start_time, end_time)
            
            # Allow 1ms tolerance for measurement accuracy
            assert abs(measured_latency - delay * 1000) < 1.0  # Convert to ms
    
    def test_statistics_calculation(self):
        """
Test latency statistics calculation"""
        # Record known latency values
        test_latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]  # ms
        
        for latency_ms in test_latencies:
            self.monitor.add_latency_sample(latency_ms)
        
        stats = self.monitor.get_statistics()
        
        # Verify statistics
        assert abs(stats['mean'] - 5.5) < 0.1
        assert abs(stats['median'] - 5.5) < 0.1
        assert stats['min'] == 1.0
        assert stats['max'] == 10.0
        assert abs(stats['std'] - np.std(test_latencies)) < 0.1
        assert stats['p95'] >= 9.0  # 95th percentile
        assert stats['p99'] >= 9.5  # 99th percentile
    
    def test_threshold_monitoring(self):
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "monitor_callback",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric monitor_callback collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection monitor_callback failed: {e}")
                    return None
        assert stats['max'] == 10.0
        assert abs(stats['std'] - np.std(test_latencies)) < 0.1
        assert stats['p95'] >= 9.0  # 95th percentile
        assert stats['p99'] >= 9.5  # 99th percentile
    
    def test_threshold_monitoring(self):
        """
Test latency threshold monitoring"""
        # Set thresholds
        warning_threshold = 5.0  # ms
        critical_threshold = 10.0  # ms
        
        self.monitor.set_thresholds(
            warning_ms=warning_threshold,
            critical_ms=critical_threshold
        )
        
        # Test different latency levels
        test_cases = [
            (3.0, 'normal'),
            (6.0, 'warning'),
            (12.0, 'critical'),
            (4.0, 'normal'),
            (8.0, 'warning'),
            (15.0, 'critical')
        ]
        
        alerts = []
        
        def alert_handler(level, latency, message):
            alerts.append((level, latency, message))
        
        self.monitor.set_alert_handler(alert_handler)
        
        for latency, expected_level in test_cases:
            self.monitor.add_latency_sample(latency)
        
        # Verify threshold detection
        warning_alerts = [a for a in alerts if a[0] == 'warning']
        critical_alerts = [a for a in alerts if a[0] == 'critical']
        
        assert len(warning_alerts) >= 2  # Should detect warning cases
        assert len(critical_alerts) >= 2  # Should detect critical cases
    
    def test_performance_trend_analysis(self):
        """
Test performance trend analysis"""
        # Simulate degrading performance
        base_latency = 2.0
        
        for i in range(100):
            # Gradually increasing latency
            latency = base_latency + (i / 100) * 3.0  # Increase from 2ms to 5ms
            noise = np.random.normal(0, 0.2)  # Add some noise
            self.monitor.add_latency_sample(latency + noise)
        
        trend_analysis = self.monitor.analyze_trends(window_size=20)
        
        # Verify trend detection
        assert trend_analysis is not None
        assert 'trend_direction' in trend_analysis
        assert 'trend_magnitude' in trend_analysis
        assert 'confidence' in trend_analysis
        
        # Should detect increasing trend
        assert trend_analysis['trend_direction'] == 'increasing'
        assert trend_analysis['trend_magnitude'] > 0
    
    def test_real_time_monitoring(self):
        """
Test real-time latency monitoring"""
        monitoring_results = []
        
        def monitor_callback(stats):
            monitoring_results.append(stats.copy())
        
        # Enable real-time monitoring
        self.monitor.enable_real_time_monitoring(
            callback=monitor_callback,
            update_interval_ms=100
        )
        
        # Generate latency samples over time
        for i in range(50):
            latency = 2.0 + np.random.normal(0, 0.5)  # 2ms ± 0.5ms
            self.monitor.add_latency_sample(latency)
            time.sleep(0.05)  # 50ms intervals
        
        # Stop monitoring
        self.monitor.disable_real_time_monitoring()
        
        # Verify real-time updates
        assert len(monitoring_results) > 0
        
        # Check that statistics are updated
        for result in monitoring_results:
            assert 'mean' in result
            assert 'sample_count' in result
            assert result['sample_count'] > 0


class TestRealtimeConfig:
    """
Test RealtimeConfig data structure"""
    
    def test_config_creation(self):
        """
Test RealtimeConfig creation"""
        config = RealtimeConfig(
            sample_rate=48000,
            buffer_size=128,
            max_latency_ms=8.0,
            enable_monitoring=True,
            enable_adaptive_buffering=True
        )
        
        assert config.sample_rate == 48000
        assert config.buffer_size == 128
        assert config.max_latency_ms == 8.0
        assert config.enable_monitoring is True
        assert config.enable_adaptive_buffering is True
    
    def test_config_validation(self):
        """
Test config validation"""
        # Valid config
        valid_config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=256,
            max_latency_ms=10.0
        )
        assert valid_config.is_valid()
        
        # Invalid configs
        with pytest.raises(ValueError):
            RealtimeConfig(sample_rate=0)  # Invalid sample rate
        
        with pytest.raises(ValueError):
            RealtimeConfig(buffer_size=0)  # Invalid buffer size
        
        with pytest.raises(ValueError):
            RealtimeConfig(max_latency_ms=-1)  # Invalid latency


class TestAudioStream:
    """
Test AudioStream implementation"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment"""
        setup_test_environment()
    
    def test_stream_creation(self):
        """
Test audio stream creation"""
        stream = AudioStream(
            sample_rate=44100,
            channels=2,
            buffer_size=512
        )
        
        assert stream is not None
        assert stream.sample_rate == 44100
        assert stream.channels == 2
        assert stream.buffer_size == 512
        assert hasattr(stream, 'input_callback')
        assert hasattr(stream, 'output_callback')
    
    def test_stream_data_flow(self):
        """
Test stream data flow"""
        received_data = []
        
        def data_callback(input_data, frame_count, time_info, status):
            received_data.append(input_data.copy())
            # Echo input to output
            return input_data, 'continue'
        
        stream = AudioStream(
            sample_rate=44100,
            channels=1,
            buffer_size=256
        )
        stream.set_callback(data_callback)
        
        # Simulate stream operation
        for i in range(10):
            test_data = np.random.randn(256).astype(np.float32)
            stream.write(test_data)
            stream.read()
        
        # Verify data flow
        assert len(received_data) > 0


class TestRealtimeIntegration:
    """
    Integration tests for complete real-time processing workflows
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
Setup test environment"""
        setup_test_environment()
    
    def test_complete_realtime_workflow(self):
        """
Test complete real-time processing workflow"""
        # Configure real-time system
        config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=256,
            max_latency_ms=8.0,
            enable_monitoring=True
        )
        
        # Initialize components
        processor = RealtimeProcessor(config=config)
        buffer_manager = BufferManager(buffer_size=256, num_buffers=8)
        latency_monitor = LatencyMonitor()
        
        # Set up processing chain
        def echo_effect(buffer):
            # Simple echo effect
            delayed = np.roll(buffer, 50)
            return buffer + 0.3 * delayed
        
        processor.add_processing_stage("echo", echo_effect)
        
        # Process audio stream
        total_processed = 0
        max_latency = 0
        
        for i in range(100):
            # Get buffer from pool
            input_buffer = buffer_manager.allocate_buffer()
            input_buffer[:] = np.random.randn(256)
            
            # Process with latency monitoring
            start_time = time.perf_counter()
            processed_buffer = processor.process_buffer(input_buffer)
            end_time = time.perf_counter()
            
            # Record latency
            latency_ms = latency_monitor.record_latency(start_time, end_time)
            max_latency = max(max_latency, latency_ms)
            
            # Return buffer to pool
            buffer_manager.deallocate_buffer(input_buffer)
            
            total_processed += len(processed_buffer)
            
            # Verify real-time constraints
            assert latency_ms < config.max_latency_ms
        
        # Verify overall performance
        assert total_processed == 100 * 256
        assert max_latency < config.max_latency_ms
        
        # Check latency statistics
        stats = latency_monitor.get_statistics()
        assert stats['mean'] < config.max_latency_ms * 0.5  # Average should be well below limit
    
    def test_stress_test_realtime_processing(self):
        """Stress test real-time processing under load"""
        config = RealtimeConfig(
            sample_rate=44100,
            buffer_size=128,  # Small buffer for stress
            max_latency_ms=5.0  # Tight constraint
        )
        
        processor = RealtimeProcessor(config=config)
        
        # Add computationally intensive processing
        def intensive_processing(buffer):
            # Multiple processing stages
            result = buffer.copy()
            
            # Apply multiple filters
            for _ in range(3):
                result = np.convolve(result, [0.25, 0.5, 0.25], mode='same')
            
            # Apply non-linear processing
            result = np.tanh(result * 1.5)
            
            return result
        
        processor.add_processing_stage("intensive", intensive_processing)
        
        # Stress test
        failed_count = 0
        latencies = []
        
        for i in range(500):  # Many iterations
            input_buffer = np.random.randn(128)
            
            start_time = time.perf_counter()
            try:
                processed = processor.process_buffer(input_buffer)
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                if latency_ms >= config.max_latency_ms:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                print(f"Processing failed: {e}")
        
        # Verify stress test results
        success_rate = (500 - failed_count) / 500
        assert success_rate >= 0.95  # At least 95% success rate
        
        if latencies:
            avg_latency = np.mean(latencies)
            assert avg_latency < config.max_latency_ms * 0.8  # Average well below limit


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
