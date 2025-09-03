"""
Load Scenarios Performance Tests
===============================

Tests various load scenarios to ensure the platform can handle different
traffic patterns and usage scenarios under various loads.
"""

import pytest
import asyncio
import aiohttp
import time
import random
import statistics
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.performance
@pytest.mark.asyncio
async def test_burst_load_scenario():
    """Test platform behavior under sudden burst of traffic."""
    base_url = "http://localhost:8000"
    burst_requests = 50
    burst_duration = 5  # seconds
    
    async def make_burst_request(session, request_id):
        """Make a single burst request."""
        try:
            start_time = time.time()
            async with session.get(f"{base_url}/api/v1/health") as response:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "status_code": response.status,
                    "response_time_ms": (end_time - start_time) * 1000,
                    "success": response.status == 200
                }
        except Exception as e:
            logger.warning(f"Burst request {request_id} failed: {e}")
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time_ms": 0,
                "success": False
            }
    
    # Execute burst load
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        connector=aiohttp.TCPConnector(limit=100)
    ) as session:
        
        start_time = time.time()
        tasks = [
            make_burst_request(session, i) 
            for i in range(burst_requests)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
    
    # Analyze results
    valid_results = [r for r in results if isinstance(r, dict)]
    successful_requests = [r for r in valid_results if r["success"]]
    response_times = [r["response_time_ms"] for r in successful_requests]
    
    total_duration = end_time - start_time
    success_rate = len(successful_requests) / len(valid_results) if valid_results else 0
    avg_response_time = statistics.mean(response_times) if response_times else 0
    
    # Assertions
    assert total_duration <= burst_duration + 5, f"Burst test took too long: {total_duration:.2f}s"
    assert success_rate >= 0.90, f"Success rate too low: {success_rate:.2f}"
    assert avg_response_time < 200, f"Average response time too high: {avg_response_time:.2f}ms"
    
    logger.info(f"Burst load test completed - Success rate: {success_rate:.2f}, "
                f"Avg response time: {avg_response_time:.2f}ms")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_sustained_load_scenario():
    """Test platform behavior under sustained load over time."""
    base_url = "http://localhost:8000"
    requests_per_second = 10
    duration_seconds = 30
    total_requests = requests_per_second * duration_seconds
    
    async def make_sustained_request(session, request_id):
        """Make a single sustained load request."""
        try:
            start_time = time.time()
            async with session.get(f"{base_url}/api/v1/health") as response:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "status_code": response.status,
                    "response_time_ms": (end_time - start_time) * 1000,
                    "timestamp": start_time,
                    "success": response.status == 200
                }
        except Exception as e:
            logger.warning(f"Sustained request {request_id} failed: {e}")
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time_ms": 0,
                "timestamp": time.time(),
                "success": False
            }
    
    # Execute sustained load with controlled rate
    results = []
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
        connector=aiohttp.TCPConnector(limit=50)
    ) as session:
        
        start_time = time.time()
        
        for i in range(total_requests):
            # Control request rate
            request_start = time.time()
            result = await make_sustained_request(session, i)
            results.append(result)
            
            # Rate limiting to maintain requests_per_second
            elapsed = time.time() - request_start
            sleep_time = (1.0 / requests_per_second) - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        end_time = time.time()
    
    # Analyze results
    successful_requests = [r for r in results if r["success"]]
    response_times = [r["response_time_ms"] for r in successful_requests]
    
    total_duration = end_time - start_time
    success_rate = len(successful_requests) / len(results) if results else 0
    avg_response_time = statistics.mean(response_times) if response_times else 0
    actual_rps = len(results) / total_duration if total_duration > 0 else 0
    
    # Assertions
    assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2f}"
    assert avg_response_time < 150, f"Average response time too high: {avg_response_time:.2f}ms"
    assert abs(actual_rps - requests_per_second) <= 2, f"RPS deviation too high: {actual_rps:.2f}"
    
    logger.info(f"Sustained load test completed - Success rate: {success_rate:.2f}, "
                f"Avg response time: {avg_response_time:.2f}ms, RPS: {actual_rps:.2f}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_spike_load_scenario():
    """Test platform recovery from traffic spikes."""
    base_url = "http://localhost:8000"
    
    # Baseline load
    baseline_requests = 20
    spike_requests = 100
    recovery_requests = 20
    
    async def make_request_batch(session, batch_name, num_requests):
        """Make a batch of requests and return metrics."""
        start_time = time.time()
        
        tasks = []
        for i in range(num_requests):
            async def make_request(req_id=i):
                try:
                    req_start = time.time()
                    async with session.get(f"{base_url}/api/v1/health") as response:
                        req_end = time.time()
                        return {
                            "status_code": response.status,
                            "response_time_ms": (req_end - req_start) * 1000,
                            "success": response.status == 200
                        }
                except Exception as e:
                    return {
                        "status_code": 0,
                        "response_time_ms": 0,
                        "success": False
                    }
            
            tasks.append(make_request())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_requests = [r for r in valid_results if r["success"]]
        
        return {
            "batch_name": batch_name,
            "duration": end_time - start_time,
            "total_requests": len(valid_results),
            "successful_requests": len(successful_requests),
            "success_rate": len(successful_requests) / len(valid_results) if valid_results else 0,
            "avg_response_time": statistics.mean([r["response_time_ms"] for r in successful_requests]) if successful_requests else 0
        }
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        connector=aiohttp.TCPConnector(limit=200)
    ) as session:
        
        # Test sequence: baseline -> spike -> recovery
        baseline_metrics = await make_request_batch(session, "baseline", baseline_requests)
        await asyncio.sleep(2)  # Brief pause
        
        spike_metrics = await make_request_batch(session, "spike", spike_requests)
        await asyncio.sleep(5)  # Recovery time
        
        recovery_metrics = await make_request_batch(session, "recovery", recovery_requests)
    
    # Assertions
    assert baseline_metrics["success_rate"] >= 0.95, f"Baseline success rate too low: {baseline_metrics['success_rate']:.2f}"
    assert spike_metrics["success_rate"] >= 0.85, f"Spike success rate too low: {spike_metrics['success_rate']:.2f}"
    assert recovery_metrics["success_rate"] >= 0.95, f"Recovery success rate too low: {recovery_metrics['success_rate']:.2f}"
    
    # Recovery should be similar to baseline
    response_time_recovery_ratio = recovery_metrics["avg_response_time"] / baseline_metrics["avg_response_time"] if baseline_metrics["avg_response_time"] > 0 else 1
    assert response_time_recovery_ratio <= 1.5, f"Recovery response time too high: {response_time_recovery_ratio:.2f}x baseline"
    
    logger.info(f"Spike load test completed - Baseline: {baseline_metrics['success_rate']:.2f}, "
                f"Spike: {spike_metrics['success_rate']:.2f}, Recovery: {recovery_metrics['success_rate']:.2f}")


@pytest.mark.performance
@pytest.mark.slow
async def test_gradual_ramp_up_scenario():
    """Test platform behavior during gradual load ramp-up."""
    base_url = "http://localhost:8000"
    ramp_stages = [5, 10, 20, 30]  # Requests per batch
    stage_duration = 10  # seconds per stage
    
    stage_results = []
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=15),
        connector=aiohttp.TCPConnector(limit=100)
    ) as session:
        
        for stage_num, requests_count in enumerate(ramp_stages, 1):
            logger.info(f"Starting ramp stage {stage_num} with {requests_count} requests")
            
            stage_start = time.time()
            tasks = []
            
            for i in range(requests_count):
                async def make_ramp_request(req_id=i):
                    try:
                        req_start = time.time()
                        async with session.get(f"{base_url}/api/v1/health") as response:
                            req_end = time.time()
                            return {
                                "status_code": response.status,
                                "response_time_ms": (req_end - req_start) * 1000,
                                "success": response.status == 200
                            }
                    except Exception:
                        return {"status_code": 0, "response_time_ms": 0, "success": False}
                
                tasks.append(make_ramp_request())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            stage_end = time.time()
            
            valid_results = [r for r in results if isinstance(r, dict)]
            successful_requests = [r for r in valid_results if r["success"]]
            
            stage_metrics = {
                "stage": stage_num,
                "requests_count": requests_count,
                "duration": stage_end - stage_start,
                "success_rate": len(successful_requests) / len(valid_results) if valid_results else 0,
                "avg_response_time": statistics.mean([r["response_time_ms"] for r in successful_requests]) if successful_requests else 0
            }
            
            stage_results.append(stage_metrics)
            
            # Brief pause between stages
            await asyncio.sleep(2)
    
    # Assertions - performance should remain stable across stages
    for stage in stage_results:
        assert stage["success_rate"] >= 0.90, f"Stage {stage['stage']} success rate too low: {stage['success_rate']:.2f}"
        assert stage["avg_response_time"] < 300, f"Stage {stage['stage']} response time too high: {stage['avg_response_time']:.2f}ms"
    
    # Check that response times don't degrade significantly
    response_times = [stage["avg_response_time"] for stage in stage_results]
    max_response_time = max(response_times)
    min_response_time = min(response_times)
    degradation_ratio = max_response_time / min_response_time if min_response_time > 0 else 1
    
    assert degradation_ratio <= 2.0, f"Response time degradation too high: {degradation_ratio:.2f}x"
    
    logger.info(f"Ramp-up test completed - Stages: {len(stage_results)}, "
                f"Max degradation: {degradation_ratio:.2f}x")