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

"""Comprehensive Performance, Load and Stress Tests
Tests system performance under various load conditions and stress scenarios.

Author: AI Assistant
Purpose: Complete performance testing for load and stress scenarios
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import random
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock system components for performance testing
class MockSystemComponent:
    """Mock system component for testing"""
    
    def __init__(self, name: str, base_latency: float = 0.01):
        self.name = name
        self.base_latency = base_latency
        self.call_count = 0
        self.error_count = 0
        self.max_concurrent = 0
        self.current_concurrent = 0
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate processing a request"""
        self.current_concurrent += 1
        self.max_concurrent = max(self.max_concurrent, self.current_concurrent)
        self.call_count += 1
        
        # Simulate variable latency based on load
        load_factor = min(self.current_concurrent / 100, 2.0)  # Up to 2x slowdown
        actual_latency = self.base_latency * (1 + load_factor)
        
        # Add random variation
        actual_latency *= random.uniform(0.8, 1.2)
        
        # Simulate occasional errors under high load
        if self.current_concurrent > 200 and random.random() < 0.05:
            self.error_count += 1
            self.current_concurrent -= 1
            raise Exception(f"System overload in {self.name}")
        
        await asyncio.sleep(actual_latency)
        
        self.current_concurrent -= 1
        
        return {
            "component": self.name,
            "request_id": request_data.get("id", "unknown"),
            "processed_at": time.time(),
            "latency": actual_latency
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get component statistics"""
        return {
            "name": self.name,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.call_count, 1),
            "max_concurrent": self.max_concurrent
        }


class MockLoadBalancer:
    """Mock load balancer for testing"""
    
    def __init__(self, components: List[MockSystemComponent]):
        self.components = components
        self.current_index = 0
    
    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to next available component (round-robin)"""
        component = self.components[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.components)
        
        return await component.process_request(request_data)


class PerformanceTestHarness:
    """Test harness for performance testing"""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    async def run_load_test(self, 
                           target_function,
                           request_generator,
                           concurrent_users: int,
                           duration_seconds: int) -> Dict[str, Any]:
        """Run a load test with specified parameters"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # Track metrics
        request_times = []
        error_count = 0
        total_requests = 0
        
        async def user_session():
            """Simulate a user session"""
            session_requests = 0
            session_errors = 0
            
            while time.time() < end_time:
                try:
                    request_start = time.time()
                    request_data = request_generator()
                    
                    await target_function(request_data)
                    
                    request_end = time.time()
                    request_times.append(request_end - request_start)
                    session_requests += 1
                    
                    # Simulate think time between requests
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                except Exception as e:
                    session_errors += 1
                    self.errors.append(str(e))
            
            return session_requests, session_errors
        
        # Run concurrent user sessions
        tasks = [user_session() for _ in range(concurrent_users)]
        session_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in session_results:
            if isinstance(result, tuple):
                requests, errors = result
                total_requests += requests
                error_count += errors
            else:
                error_count += 1
        
        total_time = time.time() - start_time
        
        return {
            "duration": total_time,
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "error_count": error_count,
            "error_rate": error_count / max(total_requests, 1),
            "requests_per_second": total_requests / total_time,
            "avg_response_time": statistics.mean(request_times) if request_times else 0,
            "p95_response_time": statistics.quantiles(request_times, n=20)[18] if len(request_times) >= 20 else 0,
            "p99_response_time": statistics.quantiles(request_times, n=100)[98] if len(request_times) >= 100 else 0,
            "min_response_time": min(request_times) if request_times else 0,
            "max_response_time": max(request_times) if request_times else 0
        }


class TestBasicPerformance:
    """Basic performance tests for individual components"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_component_latency(self):
        """Test single component response latency"""
        component = MockSystemComponent("test_api", base_latency=0.01)
        
        # Test single request
        start_time = time.time()
        result = await component.process_request({"id": "test_001"})
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Assert reasonable latency
        assert latency < 0.1  # Should be under 100ms
        assert result["component"] == "test_api"
        assert result["request_id"] == "test_001"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_component_throughput(self):
        """Test component throughput under sequential load"""
        component = MockSystemComponent("throughput_test", base_latency=0.005)
        
        num_requests = 100
        start_time = time.time()
        
        tasks = []
        for i in range(num_requests):
            task = component.process_request({"id": f"req_{i}"})
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        throughput = num_requests / total_time
        
        # Assert acceptable throughput
        assert len(results) == num_requests
        assert throughput > 50  # Should handle at least 50 requests/second
        
        # Verify all requests succeeded
        for result in results:
            assert "component" in result
            assert "request_id" in result
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test handling concurrent requests to single component"""
        component = MockSystemComponent("concurrent_test", base_latency=0.02)
        
        concurrent_requests = 50
        
        async def make_request(request_id: int):
            return await component.process_request({"id": f"concurrent_{request_id}"})
        
        start_time = time.time()
        tasks = [make_request(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # All requests should complete
        assert len(results) == concurrent_requests
        
        # Should handle concurrency efficiently (not sequential)
        expected_sequential_time = concurrent_requests * 0.02
        assert total_time < expected_sequential_time * 0.5  # At least 50% faster than sequential
        
        # Verify component tracked concurrency
        stats = component.get_stats()
        assert stats["max_concurrent"] > 1


class TestLoadTesting:
    """Load testing scenarios"""
    
    @pytest.fixture
    def test_harness(self):
        return PerformanceTestHarness()
    
    @pytest.fixture
    def mock_api_component(self):
        return MockSystemComponent("api_server", base_latency=0.015)
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_light_load(self, test_harness, mock_api_component):
        """Test system under light load"""
        
        def request_generator():
            return {"id": f"light_load_{random.randint(1000, 9999)}"}
        
        results = await test_harness.run_load_test(
            target_function=mock_api_component.process_request,
            request_generator=request_generator,
            concurrent_users=10,
            duration_seconds=5
        )
        
        # Performance assertions for light load
        assert results["error_rate"] < 0.01  # Less than 1% errors
        assert results["avg_response_time"] < 0.1  # Average under 100ms
        assert results["requests_per_second"] > 50  # At least 50 RPS
        
        # Component should handle load well
        stats = mock_api_component.get_stats()
        assert stats["error_rate"] < 0.01
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_moderate_load(self, test_harness, mock_api_component):
        """Test system under moderate load"""
        
        def request_generator():
            return {"id": f"moderate_load_{random.randint(1000, 9999)}"}
        
        results = await test_harness.run_load_test(
            target_function=mock_api_component.process_request,
            request_generator=request_generator,
            concurrent_users=50,
            duration_seconds=10
        )
        
        # Performance assertions for moderate load
        assert results["error_rate"] < 0.05  # Less than 5% errors
        assert results["avg_response_time"] < 0.2  # Average under 200ms
        assert results["requests_per_second"] > 100  # At least 100 RPS
        assert results["p95_response_time"] < 0.5  # 95th percentile under 500ms
        
        # Verify sustained performance
        assert results["total_requests"] > 500  # Reasonable number of requests
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_heavy_load(self, test_harness, mock_api_component):
        """Test system under heavy load"""
        
        def request_generator():
            return {"id": f"heavy_load_{random.randint(1000, 9999)}"}
        
        results = await test_harness.run_load_test(
            target_function=mock_api_component.process_request,
            request_generator=request_generator,
            concurrent_users=100,
            duration_seconds=15
        )
        
        # Performance assertions for heavy load (more relaxed)
        assert results["error_rate"] < 0.1  # Less than 10% errors
        assert results["avg_response_time"] < 0.5  # Average under 500ms
        assert results["requests_per_second"] > 75  # At least 75 RPS
        assert results["p99_response_time"] < 2.0  # 99th percentile under 2s
        
        # System should still be functional under heavy load
        stats = mock_api_component.get_stats()
        assert stats["call_count"] > 100


class TestStressTesting:
    """Stress testing scenarios"""
    
    @pytest.fixture
    def stress_components(self):
        """Create multiple components for stress testing"""
        return [
            MockSystemComponent("stress_api_1", base_latency=0.01),
            MockSystemComponent("stress_api_2", base_latency=0.015),
            MockSystemComponent("stress_api_3", base_latency=0.012)
        ]
    
    @pytest.fixture
    def load_balancer(self, stress_components):
        return MockLoadBalancer(stress_components)
    
    @pytest.mark.stress
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_spike_load(self, stress_components):
        """Test system response to sudden load spikes"""
        component = stress_components[0]
        
        # Normal load phase
        normal_load_tasks = []
        for i in range(20):
            task = component.process_request({"id": f"normal_{i}"})
            normal_load_tasks.append(task)
        
        # Execute normal load
        normal_results = await asyncio.gather(*normal_load_tasks)
        normal_avg_time = sum(r["latency"] for r in normal_results) / len(normal_results)
        
        # Spike load phase
        spike_load_tasks = []
        for i in range(200):  # 10x spike
            task = component.process_request({"id": f"spike_{i}"})
            spike_load_tasks.append(task)
        
        spike_start = time.time()
        spike_results = await asyncio.gather(*spike_load_tasks, return_exceptions=True)
        spike_end = time.time()
        
        # Analyze spike results
        successful_spikes = [r for r in spike_results if not isinstance(r, Exception)]
        failed_spikes = [r for r in spike_results if isinstance(r, Exception)]
        
        spike_avg_time = sum(r["latency"] for r in successful_spikes) / len(successful_spikes) if successful_spikes else 0
        
        # Performance assertions for spike handling
        success_rate = len(successful_spikes) / len(spike_load_tasks)
        assert success_rate > 0.8  # At least 80% success rate during spike
        
        # Latency should increase but not be excessive
        if spike_avg_time > 0:
            latency_increase = spike_avg_time / normal_avg_time
            assert latency_increase < 10  # No more than 10x increase
        
        # System should recover (not crash)
        stats = component.get_stats()
        assert stats["call_count"] > 0
    
    @pytest.mark.stress
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_sustained_stress(self, load_balancer, stress_components):
        """Test system under sustained high stress"""
        
        async def stress_user():
            """Simulate aggressive user behavior"""
            requests_made = 0
            errors = 0
            
            for _ in range(50):  # Each user makes 50 requests
                try:
                    request_data = {
                        "id": f"stress_{random.randint(10000, 99999)}",
                        "payload": "x" * random.randint(100, 1000)  # Variable payload size
                    }
                    
                    await load_balancer.route_request(request_data)
                    requests_made += 1
                    
                    # Minimal think time for stress
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                    
                except Exception:
                    errors += 1
            
            return requests_made, errors
        
        # Launch many aggressive users
        num_stress_users = 150
        start_time = time.time()
        
        tasks = [stress_user() for _ in range(num_stress_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Aggregate results
        total_requests = 0
        total_errors = 0
        
        for result in results:
            if isinstance(result, tuple):
                requests, errors = result
                total_requests += requests
                total_errors += errors
            else:
                total_errors += 1
        
        # Stress test assertions
        error_rate = total_errors / max(total_requests, 1)
        throughput = total_requests / total_duration
        
        assert error_rate < 0.2  # Less than 20% errors under extreme stress
        assert throughput > 200  # Maintain reasonable throughput
        assert total_requests > 1000  # Significant load was applied
        
        # Verify all components handled some load
        for component in stress_components:
            stats = component.get_stats()
            assert stats["call_count"] > 0
    
    @pytest.mark.stress
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_memory_stress(self, stress_components):
        """Test system behavior under memory stress conditions"""
        component = stress_components[0]
        
        # Create requests with large payloads to simulate memory pressure
        large_payload = "x" * 10000  # 10KB payload
        
        memory_stress_tasks = []
        for i in range(100):
            request_data = {
                "id": f"memory_stress_{i}",
                "large_payload": large_payload,
                "metadata": {
                    "created_at": time.time(),
                    "index": i,
                    "type": "memory_stress_test"
                }
            }
            task = component.process_request(request_data)
            memory_stress_tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*memory_stress_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze memory stress results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful_results) / len(results)
        processing_time = end_time - start_time
        
        # Memory stress assertions
        assert success_rate > 0.9  # Should handle large payloads well
        assert processing_time < 30  # Should complete within reasonable time
        
        # Verify component stats
        stats = component.get_stats()
        assert stats["call_count"] >= len(successful_results)


class TestScalabilityTesting:
    """Scalability testing scenarios"""
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_horizontal_scaling(self):
        """Test performance improvement with horizontal scaling"""
        
        # Test with single component
        single_component = MockSystemComponent("single_scale_test", base_latency=0.02)
        
        async def test_single_component():
            tasks = [single_component.process_request({"id": f"single_{i}"}) for i in range(100)]
            start_time = time.time()
            await asyncio.gather(*tasks)
            return time.time() - start_time
        
        single_time = await test_single_component()
        
        # Test with multiple components
        multi_components = [
            MockSystemComponent(f"multi_scale_test_{i}", base_latency=0.02) 
            for i in range(3)
        ]
        load_balancer = MockLoadBalancer(multi_components)
        
        async def test_multiple_components():
            tasks = [load_balancer.route_request({"id": f"multi_{i}"}) for i in range(100)]
            start_time = time.time()
            await asyncio.gather(*tasks)
            return time.time() - start_time
        
        multi_time = await test_multiple_components()
        
        # Scaling assertions
        improvement_factor = single_time / multi_time
        assert improvement_factor > 1.5  # Should be at least 50% faster with 3 components
        
        # Verify load distribution
        total_calls = sum(comp.get_stats()["call_count"] for comp in multi_components)
        assert total_calls >= 100
        
        # Each component should handle some requests
        for component in multi_components:
            assert component.get_stats()["call_count"] > 0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_load_distribution(self):
        """Test load distribution across multiple components"""
        components = [
            MockSystemComponent(f"dist_test_{i}", base_latency=0.01) 
            for i in range(5)
        ]
        load_balancer = MockLoadBalancer(components)
        
        # Send 500 requests through load balancer
        tasks = []
        for i in range(500):
            task = load_balancer.route_request({"id": f"dist_{i}"})
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Analyze load distribution
        call_counts = [comp.get_stats()["call_count"] for comp in components]
        total_calls = sum(call_counts)
        
        assert total_calls == 500
        
        # Check distribution fairness (should be roughly equal)
        expected_per_component = 500 / 5
        for count in call_counts:
            # Allow 20% variance in distribution
            assert abs(count - expected_per_component) < expected_per_component * 0.2


class TestFailureScenarios:
    """Test system behavior under failure conditions"""
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_component_failure_recovery(self):
        """Test system recovery from component failures"""
        
        class FailingComponent(MockSystemComponent):
            def __init__(self, name: str, failure_rate: float = 0.1):
                super().__init__(name, base_latency=0.01)
                self.failure_rate = failure_rate
                self.recovery_time = time.time() + 2  # Recover after 2 seconds
            
            async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
                # Simulate temporary failures
                if time.time() < self.recovery_time and random.random() < self.failure_rate:
                    self.error_count += 1
                    raise Exception(f"Component {self.name} temporarily unavailable")
                
                return await super().process_request(request_data)
        
        failing_component = FailingComponent("failing_test", failure_rate=0.3)
        
        # Test requests over time to see recovery
        results = []
        errors = []
        
        for i in range(100):
            try:
                result = await failing_component.process_request({"id": f"recovery_{i}"})
                results.append(result)
            except Exception as e:
                errors.append(str(e))
            
            await asyncio.sleep(0.05)  # Small delay between requests
        
        # Recovery assertions
        stats = failing_component.get_stats()
        
        # Should have some successful requests after recovery period
        assert len(results) > 0
        
        # Error rate should decrease over time as component recovers
        initial_errors = len([e for e in errors[:20] if e])  # First 20 requests
        later_errors = len([e for e in errors[-20:] if e])   # Last 20 requests
        
        # Later period should have fewer errors (recovery)
        assert later_errors <= initial_errors
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_cascading_failure_prevention(self):
        """Test prevention of cascading failures"""
        
        # Create a chain of dependent components
        components = []
        for i in range(3):
            if i == 1:  # Make middle component prone to failure under load
                comp = MockSystemComponent(f"cascade_{i}", base_latency=0.01)
                # Override to fail under high load
                original_process = comp.process_request
                
                async def failing_process(request_data):
                    if comp.current_concurrent > 10:
                        comp.error_count += 1
                        raise Exception("Overloaded component")
                    return await original_process(request_data)
                
                comp.process_request = failing_process
            else:
                comp = MockSystemComponent(f"cascade_{i}", base_latency=0.01)
            
            components.append(comp)
        
        # Simulate high load to trigger failure in middle component
        tasks = []
        for i in range(50):
            # Route through components (simulate dependency chain)
            async def process_chain(request_id: int):
                try:
                    # Process through each component in sequence
                    data = {"id": f"cascade_{request_id}"}
                    for comp in components:
                        data = await comp.process_request(data)
                    return data
                except Exception as e:
                    return {"error": str(e)}
            
            tasks.append(process_chain(i))
        
        results = await asyncio.gather(*tasks)
        
        # Analyze cascading behavior
        successful_results = [r for r in results if "error" not in r]
        failed_results = [r for r in results if "error" in r]
        
        # Some requests should succeed despite middle component issues
        success_rate = len(successful_results) / len(results)
        
        # Should have partial success (not complete cascade failure)
        assert success_rate > 0.3  # At least 30% should succeed
        
        # First and last components should still be functional
        first_comp_stats = components[0].get_stats()
        last_comp_stats = components[2].get_stats()
        
        assert first_comp_stats["call_count"] > 0
        # Last component might have fewer calls due to middle failures
        # but should still be functional when reached


class TestPerformanceRegression:
    """Performance regression testing"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_baseline(self):
        """Establish performance baseline metrics"""
        component = MockSystemComponent("baseline_test", base_latency=0.01)
        
        # Standard test load
        num_requests = 100
        concurrent_requests = 20
        
        async def baseline_test():
            tasks = [
                component.process_request({"id": f"baseline_{i}"}) 
                for i in range(num_requests)
            ]
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            return {
                "total_time": end_time - start_time,
                "requests": len(results),
                "throughput": len(results) / (end_time - start_time),
                "avg_latency": sum(r["latency"] for r in results) / len(results),
                "error_rate": component.get_stats()["error_rate"]
            }
        
        baseline_metrics = await baseline_test()
        
        # Define baseline performance expectations
        baseline_expectations = {
            "min_throughput": 50,  # requests per second
            "max_avg_latency": 0.1,  # seconds
            "max_error_rate": 0.01,  # 1%
            "max_total_time": 5.0  # seconds
        }
        
        # Validate baseline meets expectations
        assert baseline_metrics["throughput"] >= baseline_expectations["min_throughput"]
        assert baseline_metrics["avg_latency"] <= baseline_expectations["max_avg_latency"]
        assert baseline_metrics["error_rate"] <= baseline_expectations["max_error_rate"]
        assert baseline_metrics["total_time"] <= baseline_expectations["max_total_time"]
        
        # Store baseline for comparison (in real implementation, save to file/database)
        return baseline_metrics


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short", "-m", "performance or stress"])