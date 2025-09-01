#!/usr/bin/env python3
"""
Test script to verify the mock API server functionality.
"""

import asyncio
import aiohttp
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.utils.mock_api_server import ensure_api_server

async def test_mock_server():
    """
Test the mock server functionality."""
    print("🧪 Testing Mock API Server...")
    
    # Start the mock server
    mock_started = await ensure_api_server()
    
    if mock_started:
        print("✅ Mock server started successfully")
    else:
        print("ℹ️ Real server detected, using real server")
    
    # Test health endpoint
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test user registration
    try:
        user_data = {
            "username": "test_user_mock",
            "email": "test@mock.com",
            "password": "TestPassword123!"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8000/api/v1/auth/register", json=user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User registration passed: {data['user_id']}")
                    token = data['access_token']
                else:
                    print(f"❌ User registration failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test authenticated endpoint
    try:
        headers = {"Authorization": f"Bearer {token}"}
        content_data = {
            "title": "Test Audio",
            "type": "audio",
            "size": 1024
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8000/api/v1/content/upload", 
                                   json=content_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Content upload passed: {data['content_id']}")
                else:
                    print(f"❌ Content upload failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Content upload error: {e}")
        return False
    
    print("🎉 Mock API server test completed successfully!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mock_server())
    sys.exit(0 if success else 1)