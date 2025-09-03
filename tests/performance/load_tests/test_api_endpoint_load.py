"""
API endpoint load testing.
Comprehensive load testing for all major API endpoints.
"""

import asyncio
import pytest
import time
import logging
from typing import Dict, List, Any
import aiohttp
import statistics
from concurrent.futures import ThreadPoolExecutor

from tests.performance.test_industrial_load_10k import (
    LoadTestResult,
    IndustrialLoadTestConfig,
    IndustrialLoadTester
)

logger = logging.getLogger(__name__)


class APIEndpointLoadTester:
    """Load tester specifically for API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=1000)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def load_test_endpoint(self, endpoint: str, concurrent_requests: int, duration_seconds: int) -> Dict[str, Any]:
        """Load test a specific endpoint."""
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        request_times = []
        successful_requests = 0
        failed_requests = 0
        
        async def make_request():
            try:
                request_start = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    await response.text()
                    request_duration = (time.time() - request_start) * 1000  # Convert to ms
                    return {"success": response.status < 400, "duration_ms": request_duration}
            except Exception as e:
                return {"success": False, "duration_ms": 0, "error": str(e)}
        
        # Generate load for specified duration
        tasks = []
        while time.time() < end_time:
            # Create batch of concurrent requests
            batch = [make_request() for _ in range(concurrent_requests)]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, dict):
                    if result["success"]:
                        successful_requests += 1
                        request_times.append(result["duration_ms"])
                    else:
                        failed_requests += 1
                else:
                    failed_requests += 1
            
            # Small delay between batches
            await asyncio.sleep(0.1)
        
        # Calculate statistics
        total_requests = successful_requests + failed_requests
        avg_response_time = statistics.mean(request_times) if request_times else 0
        p95_response_time = statistics.quantiles(request_times, n=20)[18] if len(request_times) >= 20 else avg_response_time
        p99_response_time = statistics.quantiles(request_times, n=100)[98] if len(request_times) >= 100 else avg_response_time
        
        return {
            "endpoint": endpoint,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "error_rate": failed_requests / total_requests if total_requests > 0 else 0,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": p95_response_time,
            "p99_response_time_ms": p99_response_time,
            "requests_per_second": total_requests / duration_seconds,
            "duration_seconds": duration_seconds
        }


class TestAPIEndpointLoad:
    """Test class for API endpoint load testing."""
    
    @pytest.mark.performance
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_health_endpoint_load(self):
        """Test health endpoint under load."""
        
        async with APIEndpointLoadTester() as tester:
            result = await tester.load_test_endpoint(
                endpoint="/api/v1/health",
                concurrent_requests=100,
                duration_seconds=30
            )
            
            # Health endpoint should handle high load well
            assert result["error_rate"] < 0.01, f"Health endpoint error rate too high: {result['error_rate']}"
            assert result["avg_response_time_ms"] < 50, f"Health endpoint response time too high: {result['avg_response_time_ms']}"
            assert result["requests_per_second"] > 500, f"Health endpoint RPS too low: {result['requests_per_second']}"
    
    @pytest.mark.performance
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_authentication_endpoint_load(self):
        """Test authentication endpoint under load."""
        
        async with APIEndpointLoadTester() as tester:
            result = await tester.load_test_endpoint(
                endpoint="/api/v1/auth/login",
                concurrent_requests=50,
                duration_seconds=20
            )
            
            # Auth endpoint should handle moderate load
            assert result["error_rate"] < 0.05, f"Auth endpoint error rate too high: {result['error_rate']}"
            assert result["avg_response_time_ms"] < 200, f"Auth endpoint response time too high: {result['avg_response_time_ms']}"
            assert result["requests_per_second"] > 100, f"Auth endpoint RPS too low: {result['requests_per_second']}"
    
    @pytest.mark.performance
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_content_upload_endpoint_load(self):
        """Test content upload endpoint under load."""
        
        async with APIEndpointLoadTester() as tester:
            result = await tester.load_test_endpoint(
                endpoint="/api/v1/content/upload",
                concurrent_requests=20,
                duration_seconds=15
            )
            
            # Upload endpoint - more resource intensive
            assert result["error_rate"] < 0.10, f"Upload endpoint error rate too high: {result['error_rate']}"
            assert result["avg_response_time_ms"] < 1000, f"Upload endpoint response time too high: {result['avg_response_time_ms']}"
            assert result["requests_per_second"] > 10, f"Upload endpoint RPS too low: {result['requests_per_second']}"
    
    @pytest.mark.performance
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_analytics_endpoint_load(self):
        """Test analytics endpoint under load."""
        
        async with APIEndpointLoadTester() as tester:
            result = await tester.load_test_endpoint(
                endpoint="/api/v1/analytics/metrics",
                concurrent_requests=30,
                duration_seconds=20
            )
            
            # Analytics endpoint - database intensive
            assert result["error_rate"] < 0.08, f"Analytics endpoint error rate too high: {result['error_rate']}"
            assert result["avg_response_time_ms"] < 500, f"Analytics endpoint response time too high: {result['avg_response_time_ms']}"
            assert result["requests_per_second"] > 50, f"Analytics endpoint RPS too low: {result['requests_per_second']}"
    
    @pytest.mark.performance
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_concurrent_multi_endpoint_load(self):
        """Test multiple endpoints under concurrent load."""
        
        endpoints = [
            {"endpoint": "/api/v1/health", "concurrent": 50, "duration": 15},
            {"endpoint": "/api/v1/auth/login", "concurrent": 25, "duration": 15},
            {"endpoint": "/api/v1/content/upload", "concurrent": 10, "duration": 15},
            {"endpoint": "/api/v1/analytics/metrics", "concurrent": 20, "duration": 15}
        ]
        
        async with APIEndpointLoadTester() as tester:
            # Run all endpoint tests concurrently
            tasks = []
            for config in endpoints:
                task = tester.load_test_endpoint(
                    endpoint=config["endpoint"],
                    concurrent_requests=config["concurrent"],
                    duration_seconds=config["duration"]
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
        
        # Verify all endpoints performed acceptably under concurrent load
        for result in results:
            endpoint = result["endpoint"]
            
            # Relaxed thresholds for concurrent testing
            if endpoint == "/api/v1/health":
                assert result["error_rate"] < 0.02, f"Health endpoint failed under concurrent load: {result['error_rate']}"
                assert result["avg_response_time_ms"] < 100, f"Health endpoint response degraded: {result['avg_response_time_ms']}"
            elif endpoint == "/api/v1/auth/login":
                assert result["error_rate"] < 0.10, f"Auth endpoint failed under concurrent load: {result['error_rate']}"
                assert result["avg_response_time_ms"] < 400, f"Auth endpoint response degraded: {result['avg_response_time_ms']}"
            elif endpoint == "/api/v1/content/upload":
                assert result["error_rate"] < 0.15, f"Upload endpoint failed under concurrent load: {result['error_rate']}"
                assert result["avg_response_time_ms"] < 2000, f"Upload endpoint response degraded: {result['avg_response_time_ms']}"
            elif endpoint == "/api/v1/analytics/metrics":
                assert result["error_rate"] < 0.12, f"Analytics endpoint failed under concurrent load: {result['error_rate']}"
                assert result["avg_response_time_ms"] < 800, f"Analytics endpoint response degraded: {result['avg_response_time_ms']}"