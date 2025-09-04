"""
Simple performance tests for sub-100ms API response validation.
"""

import pytest
import aiohttp
import asyncio
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.utils.mock_api_server import ensure_api_server

@pytest.mark.performance
@pytest.mark.asyncio
async def test_health_endpoint_sub_100ms():
    """Test health endpoint responds in <100ms."""
    # Ensure API server is available
    await ensure_api_server()
    
    # Test multiple requests to get average
    response_times = []
    
    async with aiohttp.ClientSession() as session:
        for _ in range(10):
            start_time = time.time()
            async with session.get("http://localhost:8000/api/v1/health") as response:
                end_time = time.time()
                assert response.status == 200
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)
    
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    
    # Assert performance requirements
    assert avg_response_time < 100, f"Average response time {avg_response_time:.1f}ms exceeds 100ms limit"
    assert max_response_time < 200, f"Max response time {max_response_time:.1f}ms exceeds 200ms limit"

@pytest.mark.performance
@pytest.mark.asyncio
async def test_api_endpoints_performance():
    """Test multiple API endpoints for performance."""
    # Ensure API server is available
    await ensure_api_server()
    
    # Register a user first
    user_data = {
        "username": "perf_test_user",
        "email": "perf@test.com",
        "password": "PerfTest123!"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
            assert response.status == 200
            data = await response.json()
            token = data["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test different endpoints
        endpoints = [
            ("GET", "http://localhost:8000/api/v1/health", None),
            ("GET", "http://localhost:8000/api/v1/auth/verify", headers),
            ("GET", "http://localhost:8000/api/v1/analytics/performance", headers),
        ]
        
        for method, url, req_headers in endpoints:
            response_times = []
            
            for _ in range(5):
                start_time = time.time()
                if method == "GET":
                    async with session.get(url, headers=req_headers) as response:
                        end_time = time.time()
                        assert response.status == 200
                elif method == "POST":
                    async with session.post(url, headers=req_headers) as response:
                        end_time = time.time()
                        assert response.status == 200
                
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)
            
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 100, f"Endpoint {url} average response time {avg_response_time:.1f}ms exceeds 100ms"

@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_requests_performance():
    """Test concurrent requests performance."""
    # Ensure API server is available
    await ensure_api_server()
    
    async def make_request(session, url):
        start_time = time.time()
        async with session.get(url) as response:
            end_time = time.time()
            return (end_time - start_time) * 1000, response.status
    
    async with aiohttp.ClientSession() as session:
        # Test concurrent requests
        tasks = []
        for _ in range(20):  # 20 concurrent requests
            task = make_request(session, "http://localhost:8000/api/v1/health")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        response_times = [rt for rt, status in results]
        statuses = [status for rt, status in results]
        
        # All requests should succeed
        assert all(status == 200 for status in statuses), "Some concurrent requests failed"
        
        # Performance assertions
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 150, f"Concurrent requests average response time {avg_response_time:.1f}ms exceeds 150ms"
        assert max_response_time < 300, f"Concurrent requests max response time {max_response_time:.1f}ms exceeds 300ms"

@pytest.mark.performance
@pytest.mark.asyncio  
async def test_large_payload_performance():
    """Test performance with larger payloads."""
    # Ensure API server is available
    await ensure_api_server()
    
    # Register user
    user_data = {
        "username": "large_payload_user",
        "email": "large@test.com", 
        "password": "LargePayload123!"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
            assert response.status == 200
            data = await response.json()
            token = data["access_token"]
        
        # Test large content upload
        large_content_data = {
            "title": "Large Performance Test Audio",
            "type": "audio",
            "size": 20971520,  # 20MB
            "metadata": {
                "artist": "Performance Test Artist",
                "album": "Performance Test Album",
                "genre": "Electronic",
                "year": 2024,
                "description": "A" * 1000  # Large description
            }
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        start_time = time.time()
        async with session.post("http://localhost:8000/api/v1/content/upload",
                               json=large_content_data, headers=headers) as response:
            end_time = time.time()
            assert response.status == 200
            
        response_time_ms = (end_time - start_time) * 1000
        
        # Large payloads can take more time, but should still be reasonable
        assert response_time_ms < 500, f"Large payload response time {response_time_ms:.1f}ms exceeds 500ms limit"