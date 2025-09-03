"""
Memory and resource spike testing.
Tests system behavior under sudden resource consumption increases.
"""

import asyncio
import pytest
import time
import logging
import psutil
import gc
from typing import Dict, List, Any
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class ResourceSpikeConfig:
    """Configuration for resource spike testing."""
    baseline_memory_mb: float = 100.0
    spike_memory_mb: float = 1000.0
    spike_duration_seconds: int = 30
    max_acceptable_memory_mb: float = 2000.0
    max_acceptable_cpu_percent: float = 90.0


class ResourceSpikeTestRunner:
    """Runner for resource spike testing scenarios."""
    
    def __init__(self, config: ResourceSpikeConfig):
        self.config = config
        self.memory_allocations = []
        self.cpu_intensive_tasks = []
    
    def allocate_memory_spike(self):
        """Allocate memory to simulate memory spike."""
        
        # Calculate memory to allocate
        spike_memory_bytes = int((self.config.spike_memory_mb - self.config.baseline_memory_mb) * 1024 * 1024)
        
        # Allocate memory in chunks
        chunk_size = 1024 * 1024  # 1MB chunks
        num_chunks = spike_memory_bytes // chunk_size
        
        logger.info(f"Allocating {num_chunks} chunks of {chunk_size} bytes")
        
        for i in range(num_chunks):
            chunk = bytearray(chunk_size)
            # Fill with some data to ensure allocation
            for j in range(0, chunk_size, 1024):
                chunk[j:j+100] = b'X' * 100
            self.memory_allocations.append(chunk)
    
    def release_memory_spike(self):
        """Release allocated memory."""
        self.memory_allocations.clear()
        gc.collect()
    
    def cpu_intensive_task(self, duration_seconds: int):
        """Run CPU intensive task for specified duration."""
        
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            # CPU intensive calculation
            result = sum(i * i for i in range(1000))
            # Small sleep to prevent complete CPU lockup
            time.sleep(0.001)
    
    def monitor_resources(self, duration_seconds: int) -> Dict[str, Any]:
        """Monitor system resources for specified duration."""
        
        process = psutil.Process()
        measurements = []
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        while time.time() < end_time:
            try:
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                measurement = {
                    "timestamp": time.time(),
                    "memory_mb": memory_info.rss / (1024 * 1024),
                    "cpu_percent": cpu_percent,
                    "virtual_memory_mb": memory_info.vms / (1024 * 1024)
                }
                measurements.append(measurement)
                
                time.sleep(0.5)  # Measure every 500ms
                
            except Exception as e:
                logger.warning(f"Error measuring resources: {e}")
        
        if not measurements:
            return {"error": "No measurements collected"}
        
        # Calculate statistics
        memory_values = [m["memory_mb"] for m in measurements]
        cpu_values = [m["cpu_percent"] for m in measurements if m["cpu_percent"] is not None]
        
        return {
            "measurements": measurements,
            "avg_memory_mb": sum(memory_values) / len(memory_values),
            "max_memory_mb": max(memory_values),
            "min_memory_mb": min(memory_values),
            "avg_cpu_percent": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "max_cpu_percent": max(cpu_values) if cpu_values else 0,
            "duration_seconds": duration_seconds
        }


class TestResourceSpikes:
    """Test class for resource spike scenarios."""
    
    @pytest.fixture
    def resource_config(self):
        """Configuration for resource spike tests."""
        return ResourceSpikeConfig(
            baseline_memory_mb=50.0,
            spike_memory_mb=500.0,
            spike_duration_seconds=10,
            max_acceptable_memory_mb=1000.0
        )
    
    @pytest.mark.performance
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_memory_spike_handling(self, resource_config):
        """Test system handling of memory spikes."""
        
        runner = ResourceSpikeTestRunner(resource_config)
        
        # Phase 1: Baseline measurement
        baseline_stats = runner.monitor_resources(5)
        
        # Phase 2: Memory spike
        runner.allocate_memory_spike()
        spike_stats = runner.monitor_resources(resource_config.spike_duration_seconds)
        
        # Phase 3: Recovery
        runner.release_memory_spike()
        recovery_stats = runner.monitor_resources(5)
        
        # Verify memory spike behavior
        assert spike_stats["max_memory_mb"] > baseline_stats["avg_memory_mb"], "Memory spike not detected"
        assert spike_stats["max_memory_mb"] < resource_config.max_acceptable_memory_mb, "Memory usage exceeded limits"
        
        # Verify recovery
        memory_recovered = recovery_stats["avg_memory_mb"] < spike_stats["max_memory_mb"] * 0.8
        assert memory_recovered, "Memory not properly released after spike"
    
    @pytest.mark.performance
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_cpu_spike_handling(self, resource_config):
        """Test system handling of CPU spikes."""
        
        runner = ResourceSpikeTestRunner(resource_config)
        
        # Phase 1: Baseline measurement
        baseline_monitoring = asyncio.create_task(
            asyncio.to_thread(runner.monitor_resources, 3)
        )
        baseline_stats = await baseline_monitoring
        
        # Phase 2: CPU spike
        spike_monitoring = asyncio.create_task(
            asyncio.to_thread(runner.monitor_resources, resource_config.spike_duration_seconds)
        )
        cpu_task = asyncio.create_task(
            asyncio.to_thread(runner.cpu_intensive_task, resource_config.spike_duration_seconds)
        )
        
        spike_stats, _ = await asyncio.gather(spike_monitoring, cpu_task)
        
        # Phase 3: Recovery measurement
        recovery_monitoring = asyncio.create_task(
            asyncio.to_thread(runner.monitor_resources, 3)
        )
        recovery_stats = await recovery_monitoring
        
        # Verify CPU spike behavior
        assert spike_stats["max_cpu_percent"] > baseline_stats["avg_cpu_percent"], "CPU spike not detected"
        assert spike_stats["max_cpu_percent"] < resource_config.max_acceptable_cpu_percent, "CPU usage exceeded limits"
        
        # Verify system remained responsive during spike
        assert spike_stats["avg_cpu_percent"] < 95, "System became unresponsive"
    
    @pytest.mark.performance
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_concurrent_resource_spikes(self, resource_config):
        """Test system handling of concurrent memory and CPU spikes."""
        
        runner = ResourceSpikeTestRunner(resource_config)
        
        # Concurrent spike test
        monitoring_task = asyncio.create_task(
            asyncio.to_thread(runner.monitor_resources, resource_config.spike_duration_seconds)
        )
        
        # Start memory spike
        memory_task = asyncio.create_task(
            asyncio.to_thread(runner.allocate_memory_spike)
        )
        
        # Start CPU spike
        cpu_task = asyncio.create_task(
            asyncio.to_thread(runner.cpu_intensive_task, resource_config.spike_duration_seconds)
        )
        
        # Wait for all tasks
        stats, _, _ = await asyncio.gather(monitoring_task, memory_task, cpu_task)
        
        # Cleanup
        runner.release_memory_spike()
        
        # Verify system handled concurrent spikes
        assert stats["max_memory_mb"] > 0, "Memory monitoring failed"
        assert stats["max_cpu_percent"] > 0, "CPU monitoring failed"
        
        # System should not completely fail
        total_resource_pressure = (stats["max_memory_mb"] / resource_config.max_acceptable_memory_mb) + \
                                 (stats["max_cpu_percent"] / 100.0)
        assert total_resource_pressure < 1.8, "System overwhelmed by concurrent spikes"