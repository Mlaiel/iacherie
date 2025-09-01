"""
Simple integration tests that work with the mock server.
"""

import pytest
import aiohttp
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.utils.mock_api_server import ensure_api_server

@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_health_endpoint():
    """
Test API health endpoint integration."""
    # Ensure API server is available
    await ensure_api_server()
    
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/v1/health") as response:
            assert response.status == 200
            data = await response.json()
            assert "status" in data
            assert data["status"] == "healthy"

@pytest.mark.integration  
@pytest.mark.asyncio
async def test_user_registration_flow():
    """Test complete user registration flow."""
    # Ensure API server is available
    await ensure_api_server()
    
    user_data = {
        "username": "test_integration_user",
        "email": "integration@test.com", 
        "password": "TestPassword123!"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
            assert response.status == 200
            data = await response.json()
            assert "user_id" in data
            assert "access_token" in data
            
            token = data["access_token"]
            
        # Verify token
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get("http://localhost:8000/api/v1/auth/verify", headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert data["valid"] is True

@pytest.mark.integration
@pytest.mark.asyncio
async def test_content_upload_workflow():
    """Test content upload workflow integration."""
    # Ensure API server is available
    await ensure_api_server()
    
    # First register a user
    user_data = {
        "username": "content_creator",
        "email": "creator@test.com",
        "password": "CreatorPass123!"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
            assert response.status == 200
            data = await response.json()
            token = data["access_token"]
        
        # Upload content
        content_data = {
            "title": "Integration Test Audio",
            "type": "audio",
            "size": 5242880  # 5MB
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        async with session.post("http://localhost:8000/api/v1/content/upload", 
                               json=content_data, headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert "content_id" in data
            assert "upload_status" in data
            assert data["upload_status"] == "success"
            
            content_id = data["content_id"]
        
        # Retrieve content
        async with session.get(f"http://localhost:8000/api/v1/content/{content_id}", 
                              headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert data["title"] == "Integration Test Audio"

@pytest.mark.integration
@pytest.mark.asyncio  
async def test_analytics_performance_integration():
    """Test analytics performance integration."""
    # Ensure API server is available
    await ensure_api_server()
    
    # Register user first
    user_data = {
        "username": "analytics_user",
        "email": "analytics@test.com",
        "password": "AnalyticsPass123!"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
            assert response.status == 200
            data = await response.json()
            token = data["access_token"]
        
        # Get performance analytics
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get("http://localhost:8000/api/v1/analytics/performance", 
                              headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert "response_time_ms" in data
            assert "requests_per_second" in data
            assert "error_rate" in data
            # Verify performance metrics are within acceptable ranges
            assert data["response_time_ms"] < 100  # Sub-100ms requirement
            assert data["error_rate"] < 0.05  # Less than 5% error rate

@pytest.mark.integration
@pytest.mark.asyncio
async def test_monetization_revenue_integration():
    """Test monetization revenue calculation integration."""
    # Ensure API server is available
    await ensure_api_server()
    
    # Register user first
    user_data = {
        "username": "monetization_user", 
        "email": "monetization@test.com",
        "password": "MonetizationPass123!"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
            assert response.status == 200
            data = await response.json()
            token = data["access_token"]
        
        # Calculate revenue
        revenue_data = {
            "content_plays": 10000,
            "revenue_model": "stream_based",
            "platform": "spotify"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        async with session.post("http://localhost:8000/api/v1/monetization/revenue",
                               json=revenue_data, headers=headers) as response:
            assert response.status == 200
            data = await response.json()
            assert "revenue_id" in data
            assert "total_revenue" in data
            assert "currency" in data
            assert data["currency"] == "USD"
            assert data["total_revenue"] > 0