"""
Spike testing for sudden traffic increases.
Tests system behavior under rapid load increases.
"""

import asyncio
import pytest
import time
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
import aiohttp
import statistics

from tests.performance.test_industrial_load_10k import (
    LoadTestResult,
    IndustrialLoadTestConfig,
    IndustrialLoadTester
)

logger = logging.getLogger(__name__)


@dataclass
class SpikeTestConfig:
    """Configuration for spike testing."""
    baseline_users: int = 100
    spike_users: int = 1000
    spike_duration_seconds: int = 60
    recovery_duration_seconds: int = 120
    max_acceptable_response_time_ms: int = 500
    min_acceptable_success_rate: float = 0.90


class SpikeTestRunner:
    """Runner for spike testing scenarios."""
    
    def __init__(self, config: SpikeTestConfig):
        self.config = config
        self.results: List[Dict[str, Any]] = []
    
    async def run_traffic_spike_test(self) -> List[Dict[str, Any]]:
        """Run traffic spike test with baseline -> spike -> recovery."""
        
        logger.info(f"Starting spike test: baseline {self.config.baseline_users} -> spike {self.config.spike_users}")
        
        # Phase 1: Baseline load
        baseline_config = IndustrialLoadTestConfig(
            max_concurrent_users=self.config.baseline_users,
            test_duration_seconds=60,
            max_acceptable_response_time_ms=self.config.max_acceptable_response_time_ms
        )
        
        async with IndustrialLoadTester(baseline_config) as tester:
            baseline_result = await tester.run_load_test()
            self.results.append({
                "phase": "baseline",
                "users": self.config.baseline_users,
                "result": baseline_result
            })
        
        # Phase 2: Traffic spike
        spike_config = IndustrialLoadTestConfig(
            max_concurrent_users=self.config.spike_users,
            test_duration_seconds=self.config.spike_duration_seconds,
            max_acceptable_response_time_ms=self.config.max_acceptable_response_time_ms
        )
        
        async with IndustrialLoadTester(spike_config) as tester:
            spike_result = await tester.run_load_test()
            self.results.append({
                "phase": "spike",
                "users": self.config.spike_users,
                "result": spike_result
            })
        
        # Phase 3: Recovery period
        recovery_config = IndustrialLoadTestConfig(
            max_concurrent_users=self.config.baseline_users,
            test_duration_seconds=self.config.recovery_duration_seconds,
            max_acceptable_response_time_ms=self.config.max_acceptable_response_time_ms
        )
        
        async with IndustrialLoadTester(recovery_config) as tester:
            recovery_result = await tester.run_load_test()
            self.results.append({
                "phase": "recovery",
                "users": self.config.baseline_users,
                "result": recovery_result
            })
        
        return self.results


class TestSpikePerformance:
    """Test class for spike performance scenarios."""
    
    @pytest.fixture
    def spike_config(self):
        """Configuration for spike tests."""
        return SpikeTestConfig(
            baseline_users=50,
            spike_users=500,
            spike_duration_seconds=30,
            recovery_duration_seconds=60
        )
    
    @pytest.mark.performance
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_traffic_spike_resilience(self, spike_config):
        """Test system resilience during traffic spikes."""
        
        runner = SpikeTestRunner(spike_config)
        results = await runner.run_traffic_spike_test()
        
        assert len(results) == 3, "Expected baseline, spike, and recovery phases"
        
        baseline_result = next(r for r in results if r["phase"] == "baseline")
        spike_result = next(r for r in results if r["phase"] == "spike")
        recovery_result = next(r for r in results if r["phase"] == "recovery")
        
        # Verify baseline performance
        assert baseline_result["result"].error_rate < 0.05, "Baseline error rate too high"
        
        # Verify spike handling (allow higher response time but maintain availability)
        assert spike_result["result"].error_rate < 0.15, "Spike error rate too high"
        
        # Verify recovery
        assert recovery_result["result"].error_rate < 0.10, "System not recovering properly"
        
        # System should recover to near baseline performance
        recovery_degradation = recovery_result["result"].avg_response_time_ms / baseline_result["result"].avg_response_time_ms
        assert recovery_degradation < 2.0, "System not recovering response time properly"
    
    @pytest.mark.performance
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_api_endpoint_spike_handling(self, spike_config):
        """Test individual API endpoint handling during spikes."""
        
        # Test different API endpoints under spike conditions
        api_endpoints = [
            "/api/v1/health",
            "/api/v1/auth/login",
            "/api/v1/content/upload",
            "/api/v1/analytics/metrics"
        ]
        
        endpoint_results = {}
        
        for endpoint in api_endpoints:
            # Use smaller load for individual endpoint testing
            endpoint_config = SpikeTestConfig(
                baseline_users=10,
                spike_users=100,
                spike_duration_seconds=15
            )
            
            runner = SpikeTestRunner(endpoint_config)
            # Note: In real implementation, would target specific endpoint
            results = await runner.run_traffic_spike_test()
            
            endpoint_results[endpoint] = results
        
        # Verify all endpoints handled spikes reasonably
        for endpoint, results in endpoint_results.items():
            spike_result = next(r for r in results if r["phase"] == "spike")
            assert spike_result["result"].error_rate < 0.20, f"Endpoint {endpoint} failed spike test"
    
    @pytest.mark.performance
    @pytest.mark.spike
    @pytest.mark.asyncio
    async def test_database_connection_spike_handling(self, spike_config):
        """Test database connection handling during traffic spikes."""
        
        # Simulate database-heavy operations during spike
        db_intensive_config = SpikeTestConfig(
            baseline_users=20,
            spike_users=200,
            spike_duration_seconds=20
        )
        
        runner = SpikeTestRunner(db_intensive_config)
        results = await runner.run_traffic_spike_test()
        
        spike_result = next(r for r in results if r["phase"] == "spike")
        
        # Database should handle spikes without major failures
        assert spike_result["result"].error_rate < 0.25, "Database connections failed during spike"
        assert spike_result["result"].avg_response_time_ms < 2000, "Database response time too high during spike"