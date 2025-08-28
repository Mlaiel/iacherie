"""
Spike Testing Suite

Tests system behavior under sudden load spikes and traffic bursts.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Tuple


class SpikeTestMetrics:
    """Metrics collection for spike testing."""
    
    def __init__(self):
        self.timeline: List[Tuple[float, str, Dict]] = []  # (timestamp, event_type, data)
        self.response_times: List[float] = []
        self.success_count: int = 0
        self.error_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
        self.spike_start: float = 0
        self.spike_end: float = 0
    
    def start_monitoring(self):
        self.start_time = time.time()
        self.record_event("test_start", {})
    
    def stop_monitoring(self):
        self.end_time = time.time()
        self.record_event("test_end", {})
    
    def record_spike_start(self):
        self.spike_start = time.time()
        self.record_event("spike_start", {})
    
    def record_spike_end(self):
        self.spike_end = time.time()
        self.record_event("spike_end", {})
    
    def record_event(self, event_type: str, data: Dict):
        self.timeline.append((time.time(), event_type, data))
    
    def record_response(self, response_time: float, success: bool = True):
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        self.record_event("response", {
            "response_time": response_time,
            "success": success
        })
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.response_times:
            return {"error": "No measurements recorded"}
        
        total_requests = self.success_count + self.error_count
        duration = self.end_time - self.start_time
        spike_duration = self.spike_end - self.spike_start if self.spike_end > 0 else 0
        
        # Analyze pre-spike, during-spike, and post-spike performance
        pre_spike_responses = []
        during_spike_responses = []
        post_spike_responses = []
        
        for timestamp, event_type, data in self.timeline:
            if event_type == "response":
                if self.spike_start > 0:
                    if timestamp < self.spike_start:
                        pre_spike_responses.append(data["response_time"])
                    elif self.spike_end > 0 and timestamp <= self.spike_end:
                        during_spike_responses.append(data["response_time"])
                    elif self.spike_end > 0 and timestamp > self.spike_end:
                        post_spike_responses.append(data["response_time"])
        
        def calc_stats(times):
            if not times:
                return {"count": 0}
            return {
                "count": len(times),
                "mean_ms": statistics.mean(times) * 1000,
                "median_ms": statistics.median(times) * 1000,
                "max_ms": max(times) * 1000,
                "p95_ms": sorted(times)[int(0.95 * len(times))] * 1000 if len(times) > 20 else max(times) * 1000
            }
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate_percent": (self.success_count / total_requests) * 100 if total_requests > 0 else 0,
            "duration_seconds": duration,
            "spike_duration_seconds": spike_duration,
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "overall_response_times_ms": {
                "min": min(self.response_times) * 1000,
                "max": max(self.response_times) * 1000,
                "mean": statistics.mean(self.response_times) * 1000,
                "median": statistics.median(self.response_times) * 1000,
                "p95": sorted(self.response_times)[int(0.95 * len(self.response_times))] * 1000 if len(self.response_times) > 20 else max(self.response_times) * 1000,
            },
            "phase_analysis": {
                "pre_spike": calc_stats(pre_spike_responses),
                "during_spike": calc_stats(during_spike_responses),
                "post_spike": calc_stats(post_spike_responses)
            }
        }


class TestTrafficSpikes:
    """Traffic spike testing scenarios."""
    
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_sudden_traffic_spike(self):
        """Test system response to sudden traffic increase."""
        metrics = SpikeTestMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        baseline_load = 20  # 20 concurrent requests
        spike_load = 200    # 200 concurrent requests (10x increase)
        spike_duration = 10 # 10 seconds
        
        max_spike_response_time_ms = 2000
        min_success_rate_during_spike = 80.0
        recovery_time_tolerance_s = 5.0
        
        async def baseline_operation(operation_id: int):
            """Normal baseline operation."""
            start_time = time.time()
            await asyncio.sleep(0.05)  # 50ms normal processing
            end_time = time.time()
            return {
                "operation_id": operation_id,
                "response_time": end_time - start_time,
                "success": True,
                "phase": "baseline"
            }
        
        async def spike_operation(operation_id: int):
            """Operation during traffic spike."""
            start_time = time.time()
            
            # System is stressed during spike
            base_time = 0.1  # 100ms under load
            stress_factor = 1 + (operation_id % 20) / 20  # Variable stress
            processing_time = base_time * stress_factor
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 85% success rate during spike
            success = operation_id % 7 != 0
            
            return {
                "operation_id": operation_id,
                "response_time": response_time,
                "success": success,
                "phase": "spike"
            }
        
        # Phase 1: Baseline load
        baseline_tasks = [baseline_operation(i) for i in range(baseline_load)]
        baseline_results = await asyncio.gather(*baseline_tasks)
        
        for result in baseline_results:
            metrics.record_response(result["response_time"], result["success"])
        
        # Phase 2: Sudden spike
        metrics.record_spike_start()
        spike_start_time = time.time()
        
        # Generate spike load
        spike_tasks = [spike_operation(i) for i in range(spike_load)]
        spike_results = await asyncio.gather(*spike_tasks)
        
        for result in spike_results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.record_spike_end()
        
        # Phase 3: Recovery period
        await asyncio.sleep(1)  # Brief pause for recovery
        recovery_tasks = [baseline_operation(i + 1000) for i in range(baseline_load)]
        recovery_results = await asyncio.gather(*recovery_tasks)
        
        for result in recovery_results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Spike test assertions
        spike_stats = summary["phase_analysis"]["during_spike"]
        assert spike_stats["count"] > 0
        
        # During spike, allow degraded but not broken performance
        spike_success_count = sum(1 for r in spike_results if r["success"])
        spike_success_rate = (spike_success_count / len(spike_results)) * 100
        assert spike_success_rate >= min_success_rate_during_spike
        
        if spike_stats["p95_ms"] > 0:
            assert spike_stats["p95_ms"] <= max_spike_response_time_ms
        
        # System should recover after spike
        post_spike_stats = summary["phase_analysis"]["post_spike"]
        if post_spike_stats["count"] > 0:
            recovery_success_count = sum(1 for r in recovery_results if r["success"])
            recovery_success_rate = (recovery_success_count / len(recovery_results)) * 100
            assert recovery_success_rate >= 95.0  # Should recover to 95%+
        
        print(f"Traffic Spike Test: {summary}")
    
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_burst_pattern_spike(self):
        """Test system with burst traffic patterns."""
        metrics = SpikeTestMetrics()
        metrics.start_monitoring()
        
        # Burst pattern: quiet -> burst -> quiet -> burst
        burst_cycles = 3
        operations_per_burst = 50
        quiet_operations = 10
        
        max_burst_response_time_ms = 1000
        min_burst_success_rate = 85.0
        
        async def quiet_operation(operation_id: int):
            """Operation during quiet period."""
            start_time = time.time()
            await asyncio.sleep(0.03)  # 30ms quiet processing
            end_time = time.time()
            return {
                "operation_id": operation_id,
                "response_time": end_time - start_time,
                "success": True,
                "phase": "quiet"
            }
        
        async def burst_operation(operation_id: int, burst_intensity: float):
            """Operation during burst period."""
            start_time = time.time()
            
            # Processing time varies with burst intensity
            base_time = 0.05
            intensity_factor = 1 + burst_intensity
            processing_time = base_time * intensity_factor
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Success rate decreases with intensity
            failure_prob = burst_intensity * 0.1  # Up to 10% failure at max intensity
            success = (operation_id % 100) / 100.0 > failure_prob
            
            return {
                "operation_id": operation_id,
                "response_time": response_time,
                "success": success,
                "phase": "burst",
                "intensity": burst_intensity
            }
        
        all_results = []
        
        for cycle in range(burst_cycles):
            # Quiet period
            quiet_tasks = [quiet_operation(cycle * 1000 + i) for i in range(quiet_operations)]
            quiet_results = await asyncio.gather(*quiet_tasks)
            all_results.extend(quiet_results)
            
            # Burst period
            burst_intensity = 0.5 + (cycle * 0.3)  # Increasing intensity each cycle
            metrics.record_spike_start()
            
            burst_tasks = [
                burst_operation(cycle * 1000 + 100 + i, burst_intensity) 
                for i in range(operations_per_burst)
            ]
            burst_results = await asyncio.gather(*burst_tasks)
            all_results.extend(burst_results)
            
            metrics.record_spike_end()
            
            # Brief pause between cycles
            await asyncio.sleep(0.1)
        
        # Collect all metrics
        for result in all_results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Burst pattern assertions
        burst_results = [r for r in all_results if r["phase"] == "burst"]
        quiet_results = [r for r in all_results if r["phase"] == "quiet"]
        
        # Burst performance should be acceptable
        burst_success_count = sum(1 for r in burst_results if r["success"])
        burst_success_rate = (burst_success_count / len(burst_results)) * 100
        assert burst_success_rate >= min_burst_success_rate
        
        # Burst response times should be reasonable
        burst_response_times = [r["response_time"] * 1000 for r in burst_results]
        if burst_response_times:
            max_burst_time = max(burst_response_times)
            assert max_burst_time <= max_burst_response_time_ms
        
        # Quiet periods should maintain good performance
        quiet_success_count = sum(1 for r in quiet_results if r["success"])
        quiet_success_rate = (quiet_success_count / len(quiet_results)) * 100
        assert quiet_success_rate >= 98.0
        
        print(f"Burst Pattern Test: {summary}")
    
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_flash_crowd_simulation(self):
        """Test system response to flash crowd events."""
        metrics = SpikeTestMetrics()
        metrics.start_monitoring()
        
        # Flash crowd: rapid arrival of many users
        crowd_size = 300
        arrival_window_seconds = 2  # All users arrive within 2 seconds
        max_flash_response_time_ms = 3000
        min_flash_success_rate = 75.0
        
        async def flash_user_simulation(user_id: int, arrival_delay: float):
            """Simulate user arriving during flash crowd."""
            # Wait for arrival time
            await asyncio.sleep(arrival_delay)
            
            start_time = time.time()
            
            # Processing time increases with concurrent load
            base_time = 0.08
            congestion_factor = 1 + (user_id / crowd_size)  # Increases with user ID
            processing_time = base_time * congestion_factor
            
            # Add some randomness for realistic load
            import random
            processing_time *= (0.8 + random.random() * 0.4)  # ±20% variance
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time - arrival_delay  # Exclude arrival delay
            
            # Success rate decreases with congestion
            congestion_failure_rate = min(0.25, user_id / crowd_size * 0.3)
            success = random.random() > congestion_failure_rate
            
            return {
                "user_id": user_id,
                "arrival_delay": arrival_delay,
                "response_time": response_time,
                "success": success,
                "congestion_factor": congestion_factor
            }
        
        # Calculate arrival times (concentrated in arrival window)
        import random
        arrival_times = []
        for i in range(crowd_size):
            # Most users arrive early in the window (realistic flash crowd pattern)
            progress = i / crowd_size
            # Exponential decay - more users arrive early
            arrival_time = arrival_window_seconds * (1 - (1 - progress) ** 2)
            arrival_times.append(arrival_time)
        
        metrics.record_spike_start()
        
        # Execute flash crowd simulation
        tasks = [
            flash_user_simulation(i, arrival_times[i]) 
            for i in range(crowd_size)
        ]
        
        flash_results = await asyncio.gather(*tasks)
        
        metrics.record_spike_end()
        
        # Collect metrics
        for result in flash_results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Flash crowd assertions
        flash_success_count = sum(1 for r in flash_results if r["success"])
        flash_success_rate = (flash_success_count / len(flash_results)) * 100
        assert flash_success_rate >= min_flash_success_rate
        
        # Response times should be reasonable even under flash crowd
        max_response_time = max(r["response_time"] * 1000 for r in flash_results)
        assert max_response_time <= max_flash_response_time_ms
        
        # Should handle the full crowd
        assert len(flash_results) == crowd_size
        
        print(f"Flash Crowd Test: {summary}")


class TestResourceSpikes:
    """Resource usage spike testing."""
    
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_memory_usage_spike(self):
        """Test system during sudden memory usage spike."""
        metrics = SpikeTestMetrics()
        metrics.start_monitoring()
        
        # Memory spike parameters
        normal_operations = 30
        memory_spike_operations = 100
        max_spike_response_time_ms = 1500
        
        async def normal_memory_operation(operation_id: int):
            """Normal memory usage operation."""
            start_time = time.time()
            
            # Small memory allocation
            data = {"id": operation_id, "data": "x" * 100}  # 100 bytes
            await asyncio.sleep(0.02)  # 20ms processing
            
            end_time = time.time()
            del data  # Cleanup
            
            return {
                "operation_id": operation_id,
                "response_time": end_time - start_time,
                "success": True,
                "phase": "normal"
            }
        
        async def memory_spike_operation(operation_id: int):
            """Memory-intensive operation during spike."""
            start_time = time.time()
            
            try:
                # Larger memory allocation
                large_data = []
                for i in range(500):  # Reduced for testing
                    large_data.append({"id": f"{operation_id}_{i}", "data": "x" * 200})
                
                # Processing time increases with memory pressure
                processing_time = 0.05 + (operation_id % 10) * 0.01
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                del large_data  # Cleanup
                
                # Simulate memory pressure failures (90% success)
                success = operation_id % 10 != 0
                
                return {
                    "operation_id": operation_id,
                    "response_time": end_time - start_time,
                    "success": success,
                    "phase": "spike"
                }
                
            except MemoryError:
                end_time = time.time()
                return {
                    "operation_id": operation_id,
                    "response_time": end_time - start_time,
                    "success": False,
                    "phase": "spike"
                }
        
        # Phase 1: Normal operations
        normal_tasks = [normal_memory_operation(i) for i in range(normal_operations)]
        normal_results = await asyncio.gather(*normal_tasks)
        
        for result in normal_results:
            metrics.record_response(result["response_time"], result["success"])
        
        # Phase 2: Memory spike
        metrics.record_spike_start()
        
        spike_tasks = [memory_spike_operation(i) for i in range(memory_spike_operations)]
        spike_results = await asyncio.gather(*spike_tasks, return_exceptions=True)
        
        # Handle any exceptions
        for result in spike_results:
            if isinstance(result, Exception):
                metrics.record_response(1.0, False)  # Record exception as failure
            else:
                metrics.record_response(result["response_time"], result["success"])
        
        metrics.record_spike_end()
        
        # Phase 3: Recovery
        recovery_tasks = [normal_memory_operation(i + 2000) for i in range(normal_operations)]
        recovery_results = await asyncio.gather(*recovery_tasks)
        
        for result in recovery_results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Memory spike assertions
        valid_spike_results = [r for r in spike_results if not isinstance(r, Exception)]
        spike_success_count = sum(1 for r in valid_spike_results if r["success"])
        spike_success_rate = (spike_success_count / len(valid_spike_results)) * 100 if valid_spike_results else 0
        
        assert spike_success_rate >= 80.0  # 80% success during memory spike
        
        # Check recovery
        recovery_success_count = sum(1 for r in recovery_results if r["success"])
        recovery_success_rate = (recovery_success_count / len(recovery_results)) * 100
        assert recovery_success_rate >= 95.0  # Should recover well
        
        print(f"Memory Spike Test: {summary}")
    
    @pytest.mark.spike
    def test_cpu_usage_spike(self):
        """Test system during CPU usage spike."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        metrics = SpikeTestMetrics()
        metrics.start_monitoring()
        
        # CPU spike parameters
        normal_cpu_tasks = 20
        spike_cpu_tasks = 80
        max_cpu_task_time_s = 2.0
        
        def normal_cpu_task(task_id: int):
            """Normal CPU usage task."""
            start_time = time.time()
            
            # Light computation
            result = 0
            for i in range(10000):
                result += i ** 2
            
            end_time = time.time()
            
            return {
                "task_id": task_id,
                "response_time": end_time - start_time,
                "success": True,
                "phase": "normal",
                "result": result
            }
        
        def cpu_spike_task(task_id: int):
            """CPU-intensive task during spike."""
            start_time = time.time()
            
            # Heavy computation
            result = 0
            computation_size = 100000 + (task_id % 10) * 10000
            
            for i in range(computation_size):
                result += i ** 2
                # Occasional yield to prevent complete system lock
                if i % 25000 == 0:
                    time.sleep(0.001)
            
            end_time = time.time()
            
            # Simulate CPU pressure failures (85% success)
            success = task_id % 7 != 0
            
            return {
                "task_id": task_id,
                "response_time": end_time - start_time,
                "success": success,
                "phase": "spike",
                "result": result
            }
        
        all_results = []
        
        # Phase 1: Normal CPU load
        with ThreadPoolExecutor(max_workers=4) as executor:
            normal_futures = [executor.submit(normal_cpu_task, i) for i in range(normal_cpu_tasks)]
            for future in as_completed(normal_futures):
                result = future.result()
                all_results.append(result)
                metrics.record_response(result["response_time"], result["success"])
        
        # Phase 2: CPU spike
        metrics.record_spike_start()
        
        with ThreadPoolExecutor(max_workers=8) as executor:  # More workers for spike
            spike_futures = [executor.submit(cpu_spike_task, i) for i in range(spike_cpu_tasks)]
            for future in as_completed(spike_futures):
                result = future.result()
                all_results.append(result)
                metrics.record_response(result["response_time"], result["success"])
        
        metrics.record_spike_end()
        
        # Phase 3: Recovery
        with ThreadPoolExecutor(max_workers=4) as executor:
            recovery_futures = [executor.submit(normal_cpu_task, i + 3000) for i in range(normal_cpu_tasks)]
            for future in as_completed(recovery_futures):
                result = future.result()
                all_results.append(result)
                metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # CPU spike assertions
        spike_results = [r for r in all_results if r["phase"] == "spike"]
        spike_success_count = sum(1 for r in spike_results if r["success"])
        spike_success_rate = (spike_success_count / len(spike_results)) * 100
        
        assert spike_success_rate >= 80.0  # 80% success during CPU spike
        
        # Tasks should complete within reasonable time even under load
        max_spike_time = max(r["response_time"] for r in spike_results)
        assert max_spike_time <= max_cpu_task_time_s
        
        print(f"CPU Spike Test: {summary}")