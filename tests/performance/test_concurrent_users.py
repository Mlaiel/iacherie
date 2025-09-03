"""
Concurrent Users Performance Tests
=================================

Tests the platform's ability to handle multiple concurrent users
performing various actions simultaneously.
"""

import pytest
import asyncio
import aiohttp
import time
import random
import statistics
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class UserSession:
    """Represents a single user session for testing."""
    
    def __init__(self, user_id: int, base_url: str = "http://localhost:8000"):
        self.user_id = user_id
        self.base_url = base_url
        self.session_data = {}
        self.request_history = []
    
    async def perform_user_action(self, session: aiohttp.ClientSession, action: str) -> Dict[str, Any]:
        """Perform a specific user action."""
        start_time = time.time()
        
        try:
            if action == "health_check":
                async with session.get(f"{self.base_url}/api/v1/health") as response:
                    result = await self._process_response(response, action, start_time)
            
            elif action == "user_profile":
                # Simulate getting user profile
                async with session.get(f"{self.base_url}/api/v1/users/{self.user_id}") as response:
                    result = await self._process_response(response, action, start_time)
            
            elif action == "content_list":
                # Simulate getting content list
                async with session.get(f"{self.base_url}/api/v1/content") as response:
                    result = await self._process_response(response, action, start_time)
            
            elif action == "analytics":
                # Simulate analytics request
                async with session.get(f"{self.base_url}/api/v1/analytics/performance") as response:
                    result = await self._process_response(response, action, start_time)
            
            else:
                # Default to health check
                async with session.get(f"{self.base_url}/api/v1/health") as response:
                    result = await self._process_response(response, action, start_time)
            
            self.request_history.append(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            result = {
                "user_id": self.user_id,
                "action": action,
                "status_code": 0,
                "response_time_ms": (end_time - start_time) * 1000,
                "success": False,
                "error": str(e)
            }
            self.request_history.append(result)
            return result
    
    async def _process_response(self, response: aiohttp.ClientResponse, action: str, start_time: float) -> Dict[str, Any]:
        """Process HTTP response and return standardized result."""
        end_time = time.time()
        
        return {
            "user_id": self.user_id,
            "action": action,
            "status_code": response.status,
            "response_time_ms": (end_time - start_time) * 1000,
            "success": response.status == 200,
            "timestamp": start_time
        }


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_users_basic():
    """Test basic concurrent user scenarios."""
    concurrent_users = 25
    actions_per_user = 5
    
    async def simulate_user(user_id: int, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Simulate a single user's actions."""
        user = UserSession(user_id)
        actions = ["health_check", "user_profile", "content_list", "analytics", "health_check"]
        
        results = []
        for action in actions[:actions_per_user]:
            # Add random delay between actions (0.1-0.5 seconds)
            await asyncio.sleep(random.uniform(0.1, 0.5))
            result = await user.perform_user_action(session, action)
            results.append(result)
        
        return results
    
    # Execute concurrent users
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        connector=aiohttp.TCPConnector(limit=100)
    ) as session:
        
        start_time = time.time()
        
        tasks = [
            simulate_user(user_id, session) 
            for user_id in range(concurrent_users)
        ]
        
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
    
    # Analyze results
    all_results = []
    for user_result in user_results:
        if isinstance(user_result, list):
            all_results.extend(user_result)
    
    successful_requests = [r for r in all_results if r["success"]]
    total_requests = len(all_results)
    success_rate = len(successful_requests) / total_requests if total_requests > 0 else 0
    
    response_times = [r["response_time_ms"] for r in successful_requests]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0
    
    total_duration = end_time - start_time
    requests_per_second = total_requests / total_duration if total_duration > 0 else 0
    
    # Assertions
    assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2f}"
    assert avg_response_time < 200, f"Average response time too high: {avg_response_time:.2f}ms"
    assert p95_response_time < 500, f"P95 response time too high: {p95_response_time:.2f}ms"
    assert requests_per_second > 10, f"RPS too low: {requests_per_second:.2f}"
    
    logger.info(f"Concurrent users test completed - Users: {concurrent_users}, "
                f"Success rate: {success_rate:.2f}, Avg response time: {avg_response_time:.2f}ms, "
                f"RPS: {requests_per_second:.2f}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_users_mixed_workload():
    """Test concurrent users with mixed workload patterns."""
    light_users = 20  # Users making 2-3 requests
    heavy_users = 10  # Users making 8-10 requests
    
    async def simulate_light_user(user_id: int, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Simulate a light user's actions."""
        user = UserSession(user_id)
        actions = ["health_check", "user_profile"]
        
        results = []
        for action in actions:
            await asyncio.sleep(random.uniform(0.5, 1.0))  # Slower pace
            result = await user.perform_user_action(session, action)
            results.append(result)
        
        return results
    
    async def simulate_heavy_user(user_id: int, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Simulate a heavy user's actions."""
        user = UserSession(user_id + 1000)  # Different ID range
        actions = ["health_check", "user_profile", "content_list", "analytics", 
                  "content_list", "analytics", "user_profile", "health_check"]
        
        results = []
        for action in actions:
            await asyncio.sleep(random.uniform(0.1, 0.3))  # Faster pace
            result = await user.perform_user_action(session, action)
            results.append(result)
        
        return results
    
    # Execute mixed workload
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=60),
        connector=aiohttp.TCPConnector(limit=150)
    ) as session:
        
        start_time = time.time()
        
        # Create tasks for both user types
        light_tasks = [simulate_light_user(i, session) for i in range(light_users)]
        heavy_tasks = [simulate_heavy_user(i, session) for i in range(heavy_users)]
        
        all_tasks = light_tasks + heavy_tasks
        user_results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        end_time = time.time()
    
    # Analyze results
    light_results = []
    heavy_results = []
    
    for i, user_result in enumerate(user_results):
        if isinstance(user_result, list):
            if i < light_users:  # Light user results
                light_results.extend(user_result)
            else:  # Heavy user results
                heavy_results.extend(user_result)
    
    # Analyze light users
    light_successful = [r for r in light_results if r["success"]]
    light_success_rate = len(light_successful) / len(light_results) if light_results else 0
    light_avg_response_time = statistics.mean([r["response_time_ms"] for r in light_successful]) if light_successful else 0
    
    # Analyze heavy users
    heavy_successful = [r for r in heavy_results if r["success"]]
    heavy_success_rate = len(heavy_successful) / len(heavy_results) if heavy_results else 0
    heavy_avg_response_time = statistics.mean([r["response_time_ms"] for r in heavy_successful]) if heavy_successful else 0
    
    total_duration = end_time - start_time
    total_requests = len(light_results) + len(heavy_results)
    overall_rps = total_requests / total_duration if total_duration > 0 else 0
    
    # Assertions
    assert light_success_rate >= 0.95, f"Light users success rate too low: {light_success_rate:.2f}"
    assert heavy_success_rate >= 0.90, f"Heavy users success rate too low: {heavy_success_rate:.2f}"
    assert light_avg_response_time < 150, f"Light users response time too high: {light_avg_response_time:.2f}ms"
    assert heavy_avg_response_time < 250, f"Heavy users response time too high: {heavy_avg_response_time:.2f}ms"
    
    logger.info(f"Mixed workload test completed - Light users: {light_success_rate:.2f}, "
                f"Heavy users: {heavy_success_rate:.2f}, Overall RPS: {overall_rps:.2f}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_users_peak_load():
    """Test platform under peak concurrent user load."""
    peak_users = 100
    requests_per_user = 3
    max_concurrent_requests = 300
    
    async def simulate_peak_user(user_id: int, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Simulate a user during peak load."""
        user = UserSession(user_id)
        
        # Randomize actions to simulate real usage
        possible_actions = ["health_check", "user_profile", "content_list", "analytics"]
        actions = random.choices(possible_actions, k=requests_per_user)
        
        user_start_time = time.time()
        results = []
        
        for action in actions:
            result = await user.perform_user_action(session, action)
            results.append(result)
            # Very short delay between requests during peak
            await asyncio.sleep(random.uniform(0.05, 0.15))
        
        user_end_time = time.time()
        
        # Calculate user-level metrics
        successful_results = [r for r in results if r["success"]]
        user_success_rate = len(successful_results) / len(results) if results else 0
        user_avg_response_time = statistics.mean([r["response_time_ms"] for r in successful_results]) if successful_results else 0
        
        return {
            "user_id": user_id,
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "success_rate": user_success_rate,
            "avg_response_time_ms": user_avg_response_time,
            "session_duration": user_end_time - user_start_time,
            "individual_results": results
        }
    
    # Execute peak load test
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    
    async def controlled_user_simulation(user_id: int, session: aiohttp.ClientSession):
        """Run user simulation with concurrency control."""
        async with semaphore:
            return await simulate_peak_user(user_id, session)
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=45),
        connector=aiohttp.TCPConnector(limit=200)
    ) as session:
        
        start_time = time.time()
        
        tasks = [
            controlled_user_simulation(user_id, session)
            for user_id in range(peak_users)
        ]
        
        user_metrics = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
    
    # Analyze peak load results
    valid_metrics = [m for m in user_metrics if isinstance(m, dict)]
    
    # Overall metrics
    total_requests = sum(m["total_requests"] for m in valid_metrics)
    total_successful = sum(m["successful_requests"] for m in valid_metrics)
    overall_success_rate = total_successful / total_requests if total_requests > 0 else 0
    
    # Response time analysis
    all_individual_results = []
    for m in valid_metrics:
        all_individual_results.extend(m["individual_results"])
    
    successful_responses = [r for r in all_individual_results if r["success"]]
    response_times = [r["response_time_ms"] for r in successful_responses]
    
    if response_times:
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
    else:
        avg_response_time = median_response_time = p95_response_time = p99_response_time = 0
    
    total_duration = end_time - start_time
    requests_per_second = total_requests / total_duration if total_duration > 0 else 0
    
    # User experience metrics
    user_success_rates = [m["success_rate"] for m in valid_metrics if m["success_rate"] > 0]
    avg_user_success_rate = statistics.mean(user_success_rates) if user_success_rates else 0
    
    # Assertions for peak load
    assert overall_success_rate >= 0.85, f"Overall success rate too low under peak load: {overall_success_rate:.2f}"
    assert avg_user_success_rate >= 0.85, f"Average user success rate too low: {avg_user_success_rate:.2f}"
    assert avg_response_time < 500, f"Average response time too high under peak: {avg_response_time:.2f}ms"
    assert p95_response_time < 1000, f"P95 response time too high under peak: {p95_response_time:.2f}ms"
    assert requests_per_second > 50, f"RPS too low under peak load: {requests_per_second:.2f}"
    
    logger.info(f"Peak load test completed - Users: {peak_users}, "
                f"Overall success rate: {overall_success_rate:.2f}, "
                f"Avg response time: {avg_response_time:.2f}ms, "
                f"P95: {p95_response_time:.2f}ms, RPS: {requests_per_second:.2f}")


@pytest.mark.performance
@pytest.mark.slow
async def test_concurrent_users_endurance():
    """Test platform endurance with moderate concurrent load over extended time."""
    concurrent_users = 50
    test_duration_minutes = 2  # Shorter for testing, normally would be longer
    check_interval_seconds = 30
    
    test_duration_seconds = test_duration_minutes * 60
    checks_count = test_duration_seconds // check_interval_seconds
    
    async def long_running_user(user_id: int, session: aiohttp.ClientSession, duration: float) -> List[Dict[str, Any]]:
        """Simulate a user over an extended period."""
        user = UserSession(user_id)
        results = []
        
        start_time = time.time()
        while (time.time() - start_time) < duration:
            # Random action selection
            actions = ["health_check", "user_profile", "content_list", "analytics"]
            action = random.choice(actions)
            
            result = await user.perform_user_action(session, action)
            results.append(result)
            
            # Random interval between requests (1-5 seconds)
            await asyncio.sleep(random.uniform(1.0, 5.0))
        
        return results
    
    # Track performance over time
    performance_checkpoints = []
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        connector=aiohttp.TCPConnector(limit=100)
    ) as session:
        
        start_time = time.time()
        
        # Start long-running user tasks
        user_tasks = [
            long_running_user(user_id, session, test_duration_seconds)
            for user_id in range(concurrent_users)
        ]
        
        # Monitor performance at intervals
        async def monitor_performance():
            """Monitor performance during the test."""
            for check_num in range(checks_count):
                await asyncio.sleep(check_interval_seconds)
                
                checkpoint_time = time.time()
                checkpoint = {
                    "check_number": check_num + 1,
                    "elapsed_time": checkpoint_time - start_time,
                    "timestamp": checkpoint_time
                }
                performance_checkpoints.append(checkpoint)
                logger.info(f"Performance checkpoint {check_num + 1}/{checks_count} "
                           f"at {checkpoint['elapsed_time']:.1f}s")
        
        # Run monitoring and user simulation concurrently
        monitor_task = asyncio.create_task(monitor_performance())
        
        try:
            user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        end_time = time.time()
    
    # Analyze endurance test results
    all_results = []
    for user_result in user_results:
        if isinstance(user_result, list):
            all_results.extend(user_result)
    
    # Time-based analysis
    successful_requests = [r for r in all_results if r["success"]]
    total_requests = len(all_results)
    overall_success_rate = len(successful_requests) / total_requests if total_requests > 0 else 0
    
    # Response time analysis
    response_times = [r["response_time_ms"] for r in successful_requests]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    
    # Check for performance degradation over time
    time_buckets = {}
    for result in successful_requests:
        time_bucket = int((result["timestamp"] - start_time) // check_interval_seconds)
        if time_bucket not in time_buckets:
            time_buckets[time_bucket] = []
        time_buckets[time_bucket].append(result["response_time_ms"])
    
    bucket_avg_times = []
    for bucket_id in sorted(time_buckets.keys()):
        bucket_avg = statistics.mean(time_buckets[bucket_id])
        bucket_avg_times.append(bucket_avg)
    
    # Check for significant performance degradation
    if len(bucket_avg_times) >= 2:
        first_half_avg = statistics.mean(bucket_avg_times[:len(bucket_avg_times)//2])
        second_half_avg = statistics.mean(bucket_avg_times[len(bucket_avg_times)//2:])
        degradation_ratio = second_half_avg / first_half_avg if first_half_avg > 0 else 1
    else:
        degradation_ratio = 1.0
    
    total_duration = end_time - start_time
    requests_per_second = total_requests / total_duration if total_duration > 0 else 0
    
    # Assertions
    assert overall_success_rate >= 0.90, f"Endurance success rate too low: {overall_success_rate:.2f}"
    assert avg_response_time < 300, f"Average response time too high during endurance: {avg_response_time:.2f}ms"
    assert degradation_ratio <= 1.5, f"Performance degradation too high: {degradation_ratio:.2f}x"
    assert requests_per_second > 5, f"RPS too low during endurance: {requests_per_second:.2f}"
    
    logger.info(f"Endurance test completed - Duration: {total_duration/60:.1f}min, "
                f"Users: {concurrent_users}, Success rate: {overall_success_rate:.2f}, "
                f"Degradation: {degradation_ratio:.2f}x, RPS: {requests_per_second:.2f}")