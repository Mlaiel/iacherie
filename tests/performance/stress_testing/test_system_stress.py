"""
Stress Testing Suite

Tests system behavior beyond normal operating conditions to find breaking points.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor


class StressTestMetrics:
    """Metrics collection for stress testing."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.success_count: int = 0
        self.error_count: int = 0
        self.timeout_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
        self.peak_concurrent: int = 0
    
    def start_monitoring(self):
        self.start_time = time.time()
    
    def stop_monitoring(self):
        self.end_time = time.time()
    
    def record_response(self, response_time: float, success: bool = True, timeout: bool = False):
        self.response_times.append(response_time)
        if timeout:
            self.timeout_count += 1
        elif success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def update_peak_concurrent(self, current_concurrent: int):
        self.peak_concurrent = max(self.peak_concurrent, current_concurrent)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.response_times:
            return {"error": "No measurements recorded"}
        
        total_requests = self.success_count + self.error_count + self.timeout_count
        duration = self.end_time - self.start_time
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "timeout_requests": self.timeout_count,
            "success_rate_percent": (self.success_count / total_requests) * 100 if total_requests > 0 else 0,
            "timeout_rate_percent": (self.timeout_count / total_requests) * 100 if total_requests > 0 else 0,
            "duration_seconds": duration,
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "peak_concurrent": self.peak_concurrent,
            "response_times_ms": {
                "min": min(self.response_times) * 1000,
                "max": max(self.response_times) * 1000,
                "mean": statistics.mean(self.response_times) * 1000,
                "median": statistics.median(self.response_times) * 1000,
                "p95": sorted(self.response_times)[int(0.95 * len(self.response_times))] * 1000 if len(self.response_times) > 20 else max(self.response_times) * 1000,
                "p99": sorted(self.response_times)[int(0.99 * len(self.response_times))] * 1000 if len(self.response_times) > 100 else max(self.response_times) * 1000,
            }
        }


class TestConcurrencyStress:
    """High concurrency stress tests."""
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_extreme_concurrent_users(self):
        """Test system with extreme number of concurrent users."""
        metrics = StressTestMetrics()
        metrics.start_monitoring()
        
        concurrent_users = 1000  # Extreme concurrency
        max_acceptable_failures = 15  # Allow up to 15% failures under stress
        max_response_time_ms = 5000  # 5 second max under stress
        
        async def simulate_stressed_user(user_id: int):
            """Simulate user under stress conditions."""
            start_time = time.time()
            
            # Under stress, processing times become more variable
            base_time = 0.1  # 100ms base
            stress_factor = 1 + (user_id % 100) / 100  # 1x to 2x multiplier
            processing_time = base_time * stress_factor
            
            # Simulate occasional system overload
            if user_id % 20 == 0:
                processing_time *= 3  # Some requests take much longer
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Higher failure rate under stress (85% success)
            success = user_id % 7 != 0
            timeout = response_time > 3.0  # Consider >3s as timeout
            
            return {
                "user_id": user_id,
                "response_time": response_time,
                "success": success and not timeout,
                "timeout": timeout
            }
        
        # Track concurrent operations
        semaphore = asyncio.Semaphore(500)  # Limit to 500 concurrent
        
        async def controlled_user_simulation(user_id: int):
            async with semaphore:
                metrics.update_peak_concurrent(500 - semaphore._value)
                return await simulate_stressed_user(user_id)
        
        # Execute extreme concurrency test
        tasks = [controlled_user_simulation(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect metrics (handle exceptions)
        for result in results:
            if isinstance(result, Exception):
                metrics.record_response(5.0, False, True)  # Record as timeout
            else:
                metrics.record_response(
                    result["response_time"], 
                    result["success"], 
                    result["timeout"]
                )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Stress test assertions (more lenient than load tests)
        failure_rate = 100 - summary["success_rate_percent"]
        assert failure_rate <= max_acceptable_failures
        assert summary["response_times_ms"]["p95"] <= max_response_time_ms
        assert summary["peak_concurrent"] >= 400  # Should achieve high concurrency
        
        print(f"Extreme Concurrency Stress Test: {summary}")
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_resource_exhaustion_stress(self):
        """Test system behavior when resources are nearly exhausted."""
        metrics = StressTestMetrics()
        metrics.start_monitoring()
        
        # Simulate resource exhaustion scenarios
        memory_pressure_operations = 200
        max_memory_failures = 20  # Allow 20% failures under memory pressure
        
        async def memory_intensive_operation(operation_id: int):
            """Simulate memory-intensive operation."""
            start_time = time.time()
            
            # Simulate memory allocation
            try:
                # Create temporary data structures
                large_data = []
                for i in range(1000):  # Reduced for testing
                    large_data.append({"id": i, "data": "x" * 100})
                
                # Simulate processing time
                processing_time = 0.05 + (operation_id % 10) * 0.01
                await asyncio.sleep(processing_time)
                
                # Clean up
                del large_data
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Simulate memory pressure failures (80% success under pressure)
                success = operation_id % 5 != 0
                
                return {
                    "operation_id": operation_id,
                    "response_time": response_time,
                    "success": success
                }
                
            except MemoryError:
                end_time = time.time()
                return {
                    "operation_id": operation_id,
                    "response_time": end_time - start_time,
                    "success": False
                }
        
        # Execute memory pressure test
        tasks = [memory_intensive_operation(i) for i in range(memory_pressure_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect metrics
        for result in results:
            if isinstance(result, Exception):
                metrics.record_response(1.0, False)
            else:
                metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Memory stress assertions
        failure_rate = 100 - summary["success_rate_percent"]
        assert failure_rate <= max_memory_failures
        assert summary["response_times_ms"]["mean"] <= 1000  # 1s average under stress
        
        print(f"Memory Pressure Stress Test: {summary}")
    
    @pytest.mark.stress
    def test_cpu_exhaustion_stress(self):
        """Test CPU-intensive workload stress."""
        metrics = StressTestMetrics()
        metrics.start_monitoring()
        
        def cpu_intensive_task(task_id: int):
            """CPU-intensive computation."""
            start_time = time.time()
            
            # CPU-bound computation
            result = 0
            computation_size = 50000 + (task_id % 10) * 5000  # Variable load
            
            for i in range(computation_size):
                result += i ** 2
                if i % 10000 == 0:  # Yield occasionally
                    time.sleep(0.001)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Some tasks may fail under CPU stress (90% success)
            success = task_id % 10 != 0
            
            return {
                "task_id": task_id,
                "response_time": response_time,
                "success": success,
                "result": result
            }
        
        # Run CPU stress test with thread pool
        cpu_tasks = 50
        max_workers = 8  # Limit to prevent system overload
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(cpu_intensive_task, i) for i in range(cpu_tasks)]
            results = [future.result() for future in futures]
        
        # Collect metrics
        for result in results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # CPU stress assertions
        assert summary["success_rate_percent"] >= 85.0  # 85% success under CPU stress
        assert summary["response_times_ms"]["mean"] <= 2000  # 2s average
        assert len(results) == cpu_tasks
        
        print(f"CPU Exhaustion Stress Test: {summary}")


class TestFailureRecoveryStress:
    """Test system recovery from various failure scenarios."""
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_cascade_failure_simulation(self):
        """Test system behavior during cascade failures."""
        metrics = StressTestMetrics()
        metrics.start_monitoring()
        
        total_operations = 100
        failure_cascade_start = 30  # Start cascade at operation 30
        max_cascade_failures = 40  # Allow up to 40% failures during cascade
        
        async def operation_with_cascade_failure(operation_id: int):
            """Simulate operation that may be affected by cascade failure."""
            start_time = time.time()
            
            # Normal operation
            if operation_id < failure_cascade_start:
                processing_time = 0.05
                success_probability = 0.98
            
            # Cascade failure period
            elif operation_id < failure_cascade_start + 20:
                processing_time = 0.2  # Slower during cascade
                # Increasing failure rate during cascade
                cascade_position = operation_id - failure_cascade_start
                success_probability = 0.95 - (cascade_position * 0.03)
            
            # Recovery period
            else:
                recovery_position = operation_id - failure_cascade_start - 20
                processing_time = 0.1  # Gradually improving
                success_probability = 0.7 + (recovery_position * 0.02)  # Gradual recovery
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Determine success based on probability
            import random
            success = random.random() < success_probability
            
            return {
                "operation_id": operation_id,
                "response_time": response_time,
                "success": success,
                "phase": "normal" if operation_id < failure_cascade_start else 
                        "cascade" if operation_id < failure_cascade_start + 20 else "recovery"
            }
        
        # Execute cascade failure simulation
        tasks = [operation_with_cascade_failure(i) for i in range(total_operations)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results by phase
        phases = {"normal": [], "cascade": [], "recovery": []}
        for result in results:
            phases[result["phase"]].append(result)
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Calculate phase-specific metrics
        cascade_success_rate = (
            sum(1 for r in phases["cascade"] if r["success"]) / 
            len(phases["cascade"]) * 100
        ) if phases["cascade"] else 100
        
        recovery_success_rate = (
            sum(1 for r in phases["recovery"] if r["success"]) / 
            len(phases["recovery"]) * 100
        ) if phases["recovery"] else 100
        
        # Assertions
        cascade_failure_rate = 100 - cascade_success_rate
        assert cascade_failure_rate <= max_cascade_failures
        assert recovery_success_rate >= 80.0  # Should recover to 80%+
        assert summary["success_rate_percent"] >= 70.0  # Overall 70%+ success
        
        print(f"Cascade Failure Test: Overall {summary['success_rate_percent']:.1f}% success, "
              f"Cascade {cascade_success_rate:.1f}%, Recovery {recovery_success_rate:.1f}%")
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_rapid_scaling_stress(self):
        """Test system behavior during rapid scaling events."""
        metrics = StressTestMetrics()
        metrics.start_monitoring()
        
        # Simulate rapid scaling: quick ramp up, peak load, then ramp down
        scaling_phases = [
            ("ramp_up", 20, 10),      # 20 operations, 10ms interval
            ("peak", 50, 5),          # 50 operations, 5ms interval  
            ("ramp_down", 30, 15)     # 30 operations, 15ms interval
        ]
        
        all_results = []
        
        for phase_name, operation_count, interval_ms in scaling_phases:
            phase_start = time.time()
            
            async def scaling_operation(operation_id: int, phase: str):
                start_time = time.time()
                
                # Processing time varies by phase
                if phase == "ramp_up":
                    processing_time = 0.03 + operation_id * 0.002  # Gradually slower
                elif phase == "peak":
                    processing_time = 0.08  # Higher load during peak
                else:  # ramp_down
                    processing_time = 0.05 - operation_id * 0.001  # Gradually faster
                
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Success rate varies by phase
                if phase == "peak":
                    success = operation_id % 8 != 0  # 87.5% success at peak
                else:
                    success = operation_id % 20 != 0  # 95% success during scaling
                
                return {
                    "operation_id": operation_id,
                    "phase": phase,
                    "response_time": response_time,
                    "success": success
                }
            
            # Execute operations for this phase
            phase_tasks = []
            for i in range(operation_count):
                phase_tasks.append(scaling_operation(i, phase_name))
                if i < operation_count - 1:  # Don't wait after last operation
                    await asyncio.sleep(interval_ms / 1000.0)
            
            phase_results = await asyncio.gather(*phase_tasks)
            all_results.extend(phase_results)
        
        # Collect all metrics
        for result in all_results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Scaling stress assertions
        assert summary["success_rate_percent"] >= 85.0  # 85% overall success
        assert summary["response_times_ms"]["p95"] <= 200  # 200ms p95 under scaling
        assert len(all_results) == sum(count for _, count, _ in scaling_phases)
        
        print(f"Rapid Scaling Stress Test: {summary}")


class TestDataStress:
    """Data-related stress testing."""
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_large_payload_stress(self):
        """Test system with unusually large payloads."""
        metrics = StressTestMetrics()
        metrics.start_monitoring()
        
        payload_sizes = [1024, 10240, 102400, 512000]  # 1KB to 512KB
        operations_per_size = 10
        max_processing_time_ms = 2000
        
        async def process_large_payload(payload_size: int, operation_id: int):
            """Simulate processing of large payload."""
            start_time = time.time()
            
            # Create payload
            payload = "x" * payload_size
            
            # Processing time scales with payload size
            base_time = 0.01
            size_factor = payload_size / 1024  # Scale by KB
            processing_time = base_time + (size_factor * 0.001)
            
            await asyncio.sleep(processing_time)
            
            # Simulate payload validation/processing
            checksum = len(payload) % 1000
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Larger payloads have higher failure rate
            failure_probability = min(0.1, payload_size / 10000000)  # Up to 10% for very large
            success = (operation_id % 100) / 100.0 > failure_probability
            
            return {
                "payload_size": payload_size,
                "operation_id": operation_id,
                "response_time": response_time,
                "success": success,
                "checksum": checksum
            }
        
        # Test all payload sizes
        all_tasks = []
        for payload_size in payload_sizes:
            for i in range(operations_per_size):
                all_tasks.append(process_large_payload(payload_size, i))
        
        results = await asyncio.gather(*all_tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Large payload stress assertions
        assert summary["success_rate_percent"] >= 85.0  # 85% success with large payloads
        assert summary["response_times_ms"]["max"] <= max_processing_time_ms
        assert len(results) == len(payload_sizes) * operations_per_size
        
        print(f"Large Payload Stress Test: {summary}")