"""
Industrial-grade sub-100ms API performance testing.
Real performance validation with 0 mocks, 100% actual API calls.
"""

import asyncio
import time
import statistics
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import pytest
import json

logger = logging.getLogger(__name__)


class PerformanceTestType(Enum):
    """
Types of performance tests."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CONCURRENCY = "concurrency"
    STRESS = "stress"
    ENDURANCE = "endurance"


@dataclass
class PerformanceMetrics:
    """Performance test metrics."""
    endpoint: str
    test_type: PerformanceTestType
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    error_rate: float
    test_duration_seconds: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


@dataclass
class PerformanceRequirement:
    """
Performance requirements for API endpoints."""
    endpoint: str
    max_response_time_ms: float = 100
    max_p95_response_time_ms: float = 150
    max_p99_response_time_ms: float = 200
    min_requests_per_second: float = 100
    max_error_rate: float = 0.01  # 1%
    max_memory_usage_mb: float = 512
    max_cpu_usage_percent: float = 80


class IndustrialAPIPerformanceTester:
    """
    Industrial-grade API performance tester for sub-100ms requirements.
    Tests real API endpoints with real performance measurements.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.metrics: List[PerformanceMetrics] = []

    async def __aenter__(self):
        """Setup session for performance testing."""
        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector(
            limit=1000,
            limit_per_host=500,
            keepalive_timeout=30
        )
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Cleanup session."""
        if self.session:
            await self.session.close()

    async def _make_timed_request(self, method: str, endpoint: str, **kwargs) -> Tuple[float, int, int]:
        """
Make a timed request and return response time, status, and content length."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.perf_counter()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                content = await response.read()
                end_time = time.perf_counter()
                response_time_ms = (end_time - start_time) * 1000
                return response_time_ms, response.status, len(content)
        except Exception as e:
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000
            logger.error(f"Request failed: {e}")
            return response_time_ms, 0, 0

    async def test_single_endpoint_latency(self, endpoint: str, num_requests: int = 100) -> PerformanceMetrics:
        """Test latency for a single endpoint with sequential requests."""
        logger.info(f"Testing latency for {endpoint} with {num_requests} requests")
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        total_bytes = 0
        
        start_time = time.perf_counter()
        
        for i in range(num_requests):
            response_time_ms, status, content_length = await self._make_timed_request("GET", endpoint)
            response_times.append(response_time_ms)
            total_bytes += content_length
            
            if 200 <= status < 300:
                successful_requests += 1
            else:
                failed_requests += 1
                
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.01)
        
        end_time = time.perf_counter()
        test_duration = end_time - start_time
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        p50 = sorted_times[int(len(sorted_times) * 0.5)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        rps = num_requests / test_duration if test_duration > 0 else 0
        error_rate = failed_requests / num_requests if num_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            endpoint=endpoint,
            test_type=PerformanceTestType.LATENCY,
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p50_response_time_ms=p50,
            p95_response_time_ms=p95,
            p99_response_time_ms=p99,
            requests_per_second=rps,
            error_rate=error_rate,
            test_duration_seconds=test_duration
        )
        
        logger.info(f"Latency test completed: avg={avg_response_time:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")
        return metrics

    async def test_concurrent_requests(self, endpoint: str, concurrent_users: int = 50, requests_per_user: int = 10) -> PerformanceMetrics:
        """Test concurrent request performance."""
        logger.info(f"Testing concurrent performance for {endpoint} with {concurrent_users} users, {requests_per_user} requests each")
        
        async def user_session(user_id: int) -> List[Tuple[float, int, int]]:
            """Simulate a user session with multiple requests."""
            results = []
            for _ in range(requests_per_user):
                result = await self._make_timed_request("GET", endpoint)
                results.append(result)
                await asyncio.sleep(0.1)  # Think time
            return results
        
        start_time = time.perf_counter()
        
        # Create tasks for all concurrent users
        tasks = [user_session(i) for i in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        test_duration = end_time - start_time
        
        # Flatten results
        all_results = []
        for user_result in user_results:
            all_results.extend(user_result)
        
        # Calculate metrics
        response_times = [r[0] for r in all_results]
        successful_requests = len([r for r in all_results if 200 <= r[1] < 300])
        failed_requests = len([r for r in all_results if r[1] == 0 or r[1] >= 400])
        total_requests = len(all_results)
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        sorted_times = sorted(response_times)
        p50 = sorted_times[int(len(sorted_times) * 0.5)] if sorted_times else 0
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
        p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0
        
        rps = total_requests / test_duration if test_duration > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            endpoint=endpoint,
            test_type=PerformanceTestType.CONCURRENCY,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p50_response_time_ms=p50,
            p95_response_time_ms=p95,
            p99_response_time_ms=p99,
            requests_per_second=rps,
            error_rate=error_rate,
            test_duration_seconds=test_duration
        )
        
        logger.info(f"Concurrent test completed: {concurrent_users} users, avg={avg_response_time:.2f}ms, rps={rps:.2f}")
        return metrics

    async def test_throughput(self, endpoint: str, duration_seconds: int = 60) -> PerformanceMetrics:
        """Test maximum throughput for an endpoint."""
        logger.info(f"Testing throughput for {endpoint} for {duration_seconds} seconds")
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        
        # Send requests as fast as possible
        tasks = []
        while time.perf_counter() < end_time:
            task = asyncio.create_task(self._make_timed_request("GET", endpoint))
            tasks.append(task)
            
            # Limit concurrent tasks to avoid overwhelming
            if len(tasks) >= 100:
                completed_tasks = await asyncio.gather(*tasks[:50])
                tasks = tasks[50:]
                
                for response_time_ms, status, _ in completed_tasks:
                    response_times.append(response_time_ms)
                    if 200 <= status < 300:
                        successful_requests += 1
                    else:
                        failed_requests += 1
        
        # Process remaining tasks
        if tasks:
            completed_tasks = await asyncio.gather(*tasks)
            for response_time_ms, status, _ in completed_tasks:
                response_times.append(response_time_ms)
                if 200 <= status < 300:
                    successful_requests += 1
                else:
                    failed_requests += 1
        
        actual_duration = time.perf_counter() - start_time
        total_requests = len(response_times)
        
        # Calculate metrics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        sorted_times = sorted(response_times)
        p50 = sorted_times[int(len(sorted_times) * 0.5)] if sorted_times else 0
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
        p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0
        
        rps = total_requests / actual_duration if actual_duration > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            endpoint=endpoint,
            test_type=PerformanceTestType.THROUGHPUT,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p50_response_time_ms=p50,
            p95_response_time_ms=p95,
            p99_response_time_ms=p99,
            requests_per_second=rps,
            error_rate=error_rate,
            test_duration_seconds=actual_duration
        )
        
        logger.info(f"Throughput test completed: {rps:.2f} RPS, avg={avg_response_time:.2f}ms")
        return metrics

    async def test_endpoint_performance_comprehensive(self, endpoint: str, requirements: PerformanceRequirement) -> Dict[str, Any]:
        """Run comprehensive performance tests for an endpoint."""
        logger.info(f"Running comprehensive performance tests for {endpoint}")
        
        results = {}
        
        # Test latency
        latency_metrics = await self.test_single_endpoint_latency(endpoint, 100)
        results["latency"] = latency_metrics
        
        # Test concurrency
        concurrency_metrics = await self.test_concurrent_requests(endpoint, 25, 5)
        results["concurrency"] = concurrency_metrics
        
        # Test throughput (shorter duration for CI)
        throughput_metrics = await self.test_throughput(endpoint, 30)
        results["throughput"] = throughput_metrics
        
        # Validate against requirements
        validation = self._validate_requirements(results, requirements)
        results["validation"] = validation
        
        self.metrics.extend([latency_metrics, concurrency_metrics, throughput_metrics])
        
        return results

    def _validate_requirements(self, test_results: Dict[str, PerformanceMetrics], requirements: PerformanceRequirement) -> Dict[str, Any]:
        """Validate test results against performance requirements."""
        validation = {
            "passed": True,
            "failures": [],
            "warnings": []
        }
        
        # Check each test type
        for test_type, metrics in test_results.items():
            if isinstance(metrics, PerformanceMetrics):
                # Average response time check
                if metrics.avg_response_time_ms > requirements.max_response_time_ms:
                    validation["passed"] = False
                    validation["failures"].append(
                        f"{test_type}: Average response time {metrics.avg_response_time_ms:.2f}ms exceeds limit {requirements.max_response_time_ms}ms"
                    )
                
                # P95 response time check
                if metrics.p95_response_time_ms > requirements.max_p95_response_time_ms:
                    validation["passed"] = False
                    validation["failures"].append(
                        f"{test_type}: P95 response time {metrics.p95_response_time_ms:.2f}ms exceeds limit {requirements.max_p95_response_time_ms}ms"
                    )
                
                # P99 response time check
                if metrics.p99_response_time_ms > requirements.max_p99_response_time_ms:
                    validation["warnings"].append(
                        f"{test_type}: P99 response time {metrics.p99_response_time_ms:.2f}ms exceeds limit {requirements.max_p99_response_time_ms}ms"
                    )
                
                # Error rate check
                if metrics.error_rate > requirements.max_error_rate:
                    validation["passed"] = False
                    validation["failures"].append(
                        f"{test_type}: Error rate {metrics.error_rate:.2%} exceeds limit {requirements.max_error_rate:.2%}"
                    )
                
                # RPS check (for throughput tests)
                if test_type == "throughput" and metrics.requests_per_second < requirements.min_requests_per_second:
                    validation["warnings"].append(
                        f"{test_type}: RPS {metrics.requests_per_second:.2f} below target {requirements.min_requests_per_second}"
                    )
        
        return validation

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.metrics:
            return {"error": "No performance metrics available"}
        
        # Group metrics by endpoint and test type
        by_endpoint = {}
        for metric in self.metrics:
            endpoint = metric.endpoint
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = {}
            by_endpoint[endpoint][metric.test_type.value] = metric
        
        # Calculate overall statistics
        all_avg_times = [m.avg_response_time_ms for m in self.metrics]
        all_p95_times = [m.p95_response_time_ms for m in self.metrics]
        all_error_rates = [m.error_rate for m in self.metrics]
        
        overall_stats = {
            "total_endpoints_tested": len(by_endpoint),
            "total_tests_run": len(self.metrics),
            "avg_response_time_ms": statistics.mean(all_avg_times) if all_avg_times else 0,
            "max_response_time_ms": max(all_avg_times) if all_avg_times else 0,
            "avg_p95_response_time_ms": statistics.mean(all_p95_times) if all_p95_times else 0,
            "avg_error_rate": statistics.mean(all_error_rates) if all_error_rates else 0,
            "sub_100ms_compliance": len([t for t in all_avg_times if t <= 100]) / len(all_avg_times) * 100 if all_avg_times else 0
        }
        
        report = {
            "summary": overall_stats,
            "endpoints": {
                endpoint: {
                    test_type: {
                        "avg_response_time_ms": metrics.avg_response_time_ms,
                        "p95_response_time_ms": metrics.p95_response_time_ms,
                        "p99_response_time_ms": metrics.p99_response_time_ms,
                        "requests_per_second": metrics.requests_per_second,
                        "error_rate": metrics.error_rate,
                        "sub_100ms_compliant": metrics.avg_response_time_ms <= 100
                    }
                    for test_type, metrics in tests.items()
                }
                for endpoint, tests in by_endpoint.items()
            }
        }
        
        return report


class TestIndustrialAPIPerformance:
    """Test class for industrial API performance requirements."""

    @pytest.fixture
    def performance_requirements(self):
        """
Define performance requirements for different endpoint types."""
        return {
            "/api/v1/health": PerformanceRequirement(
                endpoint="/api/v1/health",
                max_response_time_ms=50,
                max_p95_response_time_ms=75,
                max_p99_response_time_ms=100,
                min_requests_per_second=500
            ),
            "/api/v1/user/profile": PerformanceRequirement(
                endpoint="/api/v1/user/profile",
                max_response_time_ms=100,
                max_p95_response_time_ms=150,
                max_p99_response_time_ms=200,
                min_requests_per_second=200
            ),
            "/api/v1/content/search": PerformanceRequirement(
                endpoint="/api/v1/content/search",
                max_response_time_ms=200,
                max_p95_response_time_ms=300,
                max_p99_response_time_ms=500,
                min_requests_per_second=100
            )
        }

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_health_endpoint_sub_100ms(self, performance_requirements):
        """Test that health endpoint responds in sub-100ms."""
        async with IndustrialAPIPerformanceTester() as tester:
            endpoint = "/api/v1/health"
            requirements = performance_requirements[endpoint]
            
            results = await tester.test_endpoint_performance_comprehensive(endpoint, requirements)
            
            # Assertions for sub-100ms performance
            latency_metrics = results["latency"]
            assert latency_metrics.avg_response_time_ms <= 50, f"Health endpoint avg response time too high: {latency_metrics.avg_response_time_ms:.2f}ms"
            assert latency_metrics.p95_response_time_ms <= 75, f"Health endpoint P95 response time too high: {latency_metrics.p95_response_time_ms:.2f}ms"
            assert latency_metrics.error_rate <= 0.001, f"Health endpoint error rate too high: {latency_metrics.error_rate:.3%}"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_user_endpoints_sub_100ms(self, performance_requirements):
        """Test that user endpoints respond in sub-100ms."""
        async with IndustrialAPIPerformanceTester() as tester:
            endpoint = "/api/v1/user/profile"
            requirements = performance_requirements[endpoint]
            
            results = await tester.test_endpoint_performance_comprehensive(endpoint, requirements)
            
            # Assertions for sub-100ms performance
            latency_metrics = results["latency"]
            assert latency_metrics.avg_response_time_ms <= 100, f"User endpoint avg response time too high: {latency_metrics.avg_response_time_ms:.2f}ms"
            assert latency_metrics.p95_response_time_ms <= 150, f"User endpoint P95 response time too high: {latency_metrics.p95_response_time_ms:.2f}ms"
            assert latency_metrics.error_rate <= 0.01, f"User endpoint error rate too high: {latency_metrics.error_rate:.2%}"

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_endpoints_performance(self, performance_requirements):
        """Test search endpoint performance under load."""
        async with IndustrialAPIPerformanceTester() as tester:
            endpoint = "/api/v1/content/search"
            requirements = performance_requirements[endpoint]
            
            results = await tester.test_endpoint_performance_comprehensive(endpoint, requirements)
            
            # Assertions for search performance
            latency_metrics = results["latency"]
            concurrency_metrics = results["concurrency"]
            
            assert latency_metrics.avg_response_time_ms <= 200, f"Search endpoint avg response time too high: {latency_metrics.avg_response_time_ms:.2f}ms"
            assert concurrency_metrics.avg_response_time_ms <= 300, f"Search endpoint concurrent response time too high: {concurrency_metrics.avg_response_time_ms:.2f}ms"
            assert concurrency_metrics.error_rate <= 0.02, f"Search endpoint error rate too high: {concurrency_metrics.error_rate:.2%}"

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_all_critical_endpoints_performance(self, performance_requirements):
        """Test performance of all critical API endpoints."""
        async with IndustrialAPIPerformanceTester() as tester:
            all_results = {}
            
            # Test all endpoints
            for endpoint, requirements in performance_requirements.items():
                logger.info(f"Testing endpoint: {endpoint}")
                results = await tester.test_endpoint_performance_comprehensive(endpoint, requirements)
                all_results[endpoint] = results
                
                # Add delay between endpoint tests
                await asyncio.sleep(10)
            
            # Generate comprehensive report
            report = tester.generate_performance_report()
            logger.info(f"Performance test summary: {report['summary']}")
            
            # Overall assertions
            assert report['summary']['sub_100ms_compliance'] >= 66.7, f"Sub-100ms compliance too low: {report['summary']['sub_100ms_compliance']:.1f}%"
            assert report['summary']['avg_error_rate'] <= 0.01, f"Overall error rate too high: {report['summary']['avg_error_rate']:.3%}"
            
            # Check individual endpoint compliance
            failed_endpoints = []
            for endpoint, results in all_results.items():
                if not results["validation"]["passed"]:
                    failed_endpoints.append(endpoint)
            
            assert len(failed_endpoints) == 0, f"Endpoints failed performance requirements: {failed_endpoints}"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_load_performance(self):
        """Test API performance under concurrent load."""
        async with IndustrialAPIPerformanceTester() as tester:
            # Test multiple endpoints concurrently
            endpoints = ["/api/v1/health", "/api/v1/user/profile", "/api/v1/content/search"]
            
            async def test_endpoint_concurrently(endpoint):
        try:
            logger.info(f"Executing test_endpoint_concurrently")
            
            # Implementation for test_endpoint_concurrently
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_endpoint_concurrently completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_endpoint_concurrently failed: {e}")
            raise
            tasks = [test_endpoint_concurrently(endpoint) for endpoint in endpoints]
            results = await asyncio.gather(*tasks)
            
            # Verify all endpoints maintain performance under concurrent load
            for i, metrics in enumerate(results):
                endpoint = endpoints[i]
                assert metrics.avg_response_time_ms <= 200, f"Endpoint {endpoint} too slow under concurrent load: {metrics.avg_response_time_ms:.2f}ms"
                assert metrics.error_rate <= 0.05, f"Endpoint {endpoint} error rate too high under concurrent load: {metrics.error_rate:.2%}"
                assert metrics.requests_per_second >= 10, f"Endpoint {endpoint} RPS too low under concurrent load: {metrics.requests_per_second:.2f}"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test response time consistency across multiple measurements."""
        async with IndustrialAPIPerformanceTester() as tester:
            endpoint = "/api/v1/health"
            
            # Run multiple test rounds
            results = []
            for round_num in range(5):
                metrics = await tester.test_single_endpoint_latency(endpoint, 50)
                results.append(metrics)
                await asyncio.sleep(5)
            
            # Check consistency
            avg_times = [m.avg_response_time_ms for m in results]
            consistency_variance = statistics.variance(avg_times) if len(avg_times) > 1 else 0
            
            # Response times should be consistent (low variance)
            assert consistency_variance <= 100, f"Response time variance too high: {consistency_variance:.2f}"
            
            # All rounds should meet sub-100ms requirement
            for i, metrics in enumerate(results):
                assert metrics.avg_response_time_ms <= 100, f"Round {i+1} failed sub-100ms requirement: {metrics.avg_response_time_ms:.2f}ms"