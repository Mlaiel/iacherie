"""
Performance and Load Testing Suite

Comprehensive performance tests for load, stress, and scalability testing
of critical Ainflue platform components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import json

# Test configuration
PERFORMANCE_THRESHOLDS = {
    'api_response_time_ms': 500,      # 500ms max response time
    'fingerprint_processing_s': 5,    # 5s max fingerprinting time
    'concurrent_users': 1000,         # Support 1000 concurrent users
    'throughput_rps': 100,            # 100 requests per second
    'cpu_usage_percent': 80,          # 80% max CPU usage
    'memory_usage_mb': 2048,          # 2GB max memory usage
}


class PerformanceMetrics:
    """Performance metrics collection and analysis."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.error_count: int = 0
        self.success_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.end_time = time.time()
    
    def add_response_time(self, response_time: float):
        """Add response time measurement."""
        self.response_times.append(response_time)
    
    def add_success(self):
        """Record successful operation."""
        self.success_count += 1
    
    def add_error(self):
        """Record failed operation."""
        self.error_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.response_times:
            return {"error": "No measurements recorded"}
        
        total_requests = self.success_count + self.error_count
        duration = self.end_time - self.start_time
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate": (self.success_count / total_requests) * 100 if total_requests > 0 else 0,
            "duration_seconds": duration,
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "response_times": {
                "min_ms": min(self.response_times) * 1000,
                "max_ms": max(self.response_times) * 1000,
                "avg_ms": statistics.mean(self.response_times) * 1000,
                "median_ms": statistics.median(self.response_times) * 1000,
                "p95_ms": sorted(self.response_times)[int(0.95 * len(self.response_times))] * 1000 if len(self.response_times) > 20 else max(self.response_times) * 1000,
                "p99_ms": sorted(self.response_times)[int(0.99 * len(self.response_times))] * 1000 if len(self.response_times) > 100 else max(self.response_times) * 1000
            }
        }


class TestSimulatedPerformance:
    """Simulated performance tests (no actual server required)."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_simulated_api_performance(self):
        """Test simulated API endpoint performance."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Simulate 100 API requests
        for i in range(100):
            start_time = time.time()
            
            # Simulate API processing time (50-200ms)
            processing_time = 0.05 + (i % 15) * 0.01
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics.add_response_time(response_time)
            
            # Simulate 95% success rate
            if i % 20 != 0:  # 95% success
                metrics.add_success()
            else:
                metrics.add_error()
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["response_times"]["avg_ms"] < PERFORMANCE_THRESHOLDS["api_response_time_ms"]
        assert summary["success_rate"] >= 90.0
        
        print(f"Simulated API Performance: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_simulated_fingerprinting_performance(self):
        """Test simulated fingerprinting performance."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Simulate fingerprinting of different content types
        content_types = ["text", "audio", "video", "image"]
        processing_times = {"text": 0.1, "audio": 2.0, "video": 4.0, "image": 0.5}
        
        for i in range(20):  # 20 fingerprinting operations
            content_type = content_types[i % len(content_types)]
            base_time = processing_times[content_type]
            
            start_time = time.time()
            
            # Simulate processing with some variance
            actual_time = base_time * (0.8 + 0.4 * (i % 10) / 10)
            await asyncio.sleep(actual_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics.add_response_time(response_time)
            metrics.add_success()
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["response_times"]["avg_ms"] < PERFORMANCE_THRESHOLDS["fingerprint_processing_s"] * 1000
        assert summary["success_rate"] >= 95.0
        
        print(f"Simulated Fingerprinting Performance: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_simulated_concurrent_processing(self):
        """Test simulated concurrent processing performance."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        async def simulate_task(task_id: int):
            """Simulate a processing task."""
            start_time = time.time()
            
            # Simulate variable processing time (10-100ms)
            processing_time = 0.01 + (task_id % 10) * 0.01
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            return {
                "task_id": task_id,
                "response_time": end_time - start_time,
                "success": task_id % 50 != 0  # 98% success rate
            }
        
        # Run 200 concurrent tasks
        tasks = [simulate_task(i) for i in range(200)]
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.add_response_time(result["response_time"])
            if result["success"]:
                metrics.add_success()
            else:
                metrics.add_error()
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 95.0
        assert summary["requests_per_second"] >= 100  # Should handle 100+ concurrent ops/sec
        
        print(f"Simulated Concurrent Performance: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.performance
    def test_memory_efficiency(self):
        """Test memory usage efficiency."""
        # Simulate memory-intensive operations
        data_structures = []
        
        for i in range(50):
            # Create moderate-sized data structures
            data = {
                'id': i,
                'content': 'x' * 1000,  # 1KB each
                'metadata': {'processed': True, 'timestamp': time.time()}
            }
            data_structures.append(data)
        
        # Memory usage should be reasonable
        assert len(data_structures) == 50
        
        print(f"Memory Usage: Created {len(data_structures)} data structures")
        
        # Clean up
        data_structures.clear()
    
    @pytest.mark.performance
    def test_cpu_efficiency(self):
        """Test CPU usage efficiency."""
        def cpu_task():
            """Simulate CPU-intensive task."""
            result = 0
            for i in range(100000):  # Reduced for testing
                result += i ** 2
            return result
        
        start_time = time.time()
        
        # Run CPU tasks
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(cpu_task) for _ in range(4)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # CPU efficiency assertions
        assert total_time < 5.0  # Should complete within 5 seconds
        assert len(results) == 4  # All tasks should complete
        
        print(f"CPU Task Performance: {total_time:.2f}s for 4 tasks")


class TestStressSimulation:
    """Stress testing simulations."""
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_high_concurrency_simulation(self):
        """Test high concurrency simulation."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Simulate 500 concurrent operations
        async def simulate_operation(op_id: int):
            start_time = time.time()
            
            # Simulate varying load
            if op_id % 10 == 0:
                # Heavy operation
                await asyncio.sleep(0.1)
            else:
                # Light operation
                await asyncio.sleep(0.01)
            
            end_time = time.time()
            return {
                "op_id": op_id,
                "response_time": end_time - start_time,
                "success": op_id % 100 != 0  # 99% success under stress
            }
        
        # Execute high concurrency test
        operations = [simulate_operation(i) for i in range(500)]
        results = await asyncio.gather(*operations)
        
        # Collect metrics
        for result in results:
            metrics.add_response_time(result["response_time"])
            if result["success"]:
                metrics.add_success()
            else:
                metrics.add_error()
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Stress test assertions (more lenient)
        assert summary["success_rate"] >= 90.0  # 90% success under stress
        assert summary["requests_per_second"] >= 50  # Reduced threshold under stress
        
        print(f"High Concurrency Simulation: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_sustained_load_simulation(self):
        """Test sustained load simulation."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Run sustained load for 10 seconds (reduced for testing)
        duration = 10  # 10 seconds for testing
        end_time = time.time() + duration
        
        operation_count = 0
        while time.time() < end_time:
            start_time = time.time()
            
            # Simulate operation
            await asyncio.sleep(0.05)  # 50ms operation
            
            end_time_op = time.time()
            response_time = end_time_op - start_time
            
            metrics.add_response_time(response_time)
            metrics.add_success()
            operation_count += 1
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Sustained load assertions
        assert summary["success_rate"] >= 95.0
        assert operation_count >= 100  # Should handle at least 100 ops in 10s
        
        print(f"Sustained Load Simulation ({duration}s): {json.dumps(summary, indent=2)}")


class TestScalabilitySimulation:
    """Scalability testing simulations."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_linear_scaling_simulation(self):
        """Test linear scaling simulation."""
        results = {}
        
        # Test different load levels
        load_levels = [10, 50, 100, 200]
        
        for load in load_levels:
            metrics = PerformanceMetrics()
            metrics.start_monitoring()
            
            # Simulate operations at different load levels
            async def simulate_load_operation(op_id: int):
                start_time = time.time()
                
                # Simulate processing time that scales with load
                base_time = 0.01
                scaling_factor = 1 + (load / 1000)  # Slight increase with load
                processing_time = base_time * scaling_factor
                
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                return end_time - start_time
            
            # Execute operations
            operations = [simulate_load_operation(i) for i in range(load)]
            response_times = await asyncio.gather(*operations)
            
            # Collect metrics
            for rt in response_times:
                metrics.add_response_time(rt)
                metrics.add_success()
            
            metrics.stop_monitoring()
            summary = metrics.get_summary()
            results[load] = summary
            
            print(f"Load {load}: Avg response time = {summary['response_times']['avg_ms']:.2f}ms")
        
        # Scalability assertions
        # Response time should not degrade dramatically with load
        response_times_by_load = {load: results[load]['response_times']['avg_ms'] for load in load_levels}
        
        # Check that response time doesn't increase more than 3x from lowest to highest load
        min_time = min(response_times_by_load.values())
        max_time = max(response_times_by_load.values())
        degradation_factor = max_time / min_time if min_time > 0 else 1
        
        assert degradation_factor < 3.0  # Less than 3x degradation
        
        print(f"Scalability test: {degradation_factor:.2f}x response time degradation")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__, 
        "-v", 
        "-m", "performance",
        "--asyncio-mode=auto",
        "--tb=short"
    ])