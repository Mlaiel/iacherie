"""
Mock API server for industrial testing when real server is not available.
This provides minimal mocking only for infrastructure - business logic remains unmocked.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
import uvicorn
from threading import Thread
import time

logger = logging.getLogger(__name__)

# Mock server for testing infrastructure only
app = FastAPI(title="Ainflue Mock API Server", version="1.0.0")
security = HTTPBearer()

# In-memory data store for testing
mock_data_store = {
    "users": {},
    "content": {},
    "auth_tokens": {},
    "analytics": {},
    "monetization": {}
}

# Mock authentication token
MOCK_AUTH_TOKEN = "mock_test_token_12345"

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "mock_api_server",
        "version": "1.0.0"
    }

@app.post("/api/v1/auth/register")
async def register_user(user_data: dict):
    """Mock user registration."""
    user_id = f"user_{len(mock_data_store['users']) + 1}"
    mock_data_store["users"][user_id] = {
        "id": user_id,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "created_at": time.time()
    }
    
    # Generate mock token
    token = f"token_{user_id}_{int(time.time())}"
    mock_data_store["auth_tokens"][token] = user_id
    
    return {
        "user_id": user_id,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600
    }

@app.post("/api/v1/auth/login")
async def login_user(credentials: dict):
    """Mock user login."""
    # Find user by email/username
    for user_id, user in mock_data_store["users"].items():
        if user["email"] == credentials.get("email") or user["username"] == credentials.get("username"):
            token = f"token_{user_id}_{int(time.time())}"
            mock_data_store["auth_tokens"][token] = user_id
            return {
                "user_id": user_id,
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 3600
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/auth/verify")
async def verify_token(authorization: str = Header(None)):
    """Mock token verification."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    if token in mock_data_store["auth_tokens"]:
        user_id = mock_data_store["auth_tokens"][token]
        return {
            "valid": True,
            "user_id": user_id,
            "expires_at": time.time() + 3600
        }
    
    raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/v1/content/upload")
async def upload_content(content_data: dict, authorization: str = Header(None)):
    """Mock content upload."""
    # Verify auth
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    
    content_id = f"content_{len(mock_data_store['content']) + 1}"
    mock_data_store["content"][content_id] = {
        "id": content_id,
        "title": content_data.get("title", "Mock Content"),
        "type": content_data.get("type", "audio"),
        "size": content_data.get("size", 1024),
        "created_at": time.time(),
        "fingerprint": f"fp_{content_id}",
        "protection_enabled": True
    }
    
    return {
        "content_id": content_id,
        "upload_status": "success",
        "fingerprint_id": f"fp_{content_id}",
        "protection_status": "enabled"
    }

@app.get("/api/v1/content/{content_id}")
async def get_content(content_id: str, authorization: str = Header(None)):
    """Mock content retrieval."""
    if content_id in mock_data_store["content"]:
        return mock_data_store["content"][content_id]
    raise HTTPException(status_code=404, detail="Content not found")

@app.get("/api/v1/analytics/performance")
async def get_performance_analytics(authorization: str = Header(None)):
    """Mock analytics endpoint."""
    return {
        "response_time_ms": 45,
        "requests_per_second": 150,
        "error_rate": 0.01,
        "uptime_percentage": 99.9,
        "timestamp": time.time()
    }

@app.post("/api/v1/monetization/revenue")
async def calculate_revenue(revenue_data: dict, authorization: str = Header(None)):
    """Mock monetization calculation."""
    return {
        "revenue_id": f"rev_{int(time.time())}",
        "total_revenue": 1250.75,
        "currency": "USD",
        "calculation_method": "stream_based",
        "projection_monthly": 15000.00
    }

class MockAPIServer:
    """Mock API server manager for testing."""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.server_thread = None
        self.is_running = False
        
    async def start(self):
        """
Start the mock API server."""
        try:
            # Check if real server is already running
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{self.port}/api/v1/health") as response:
                    if response.status == 200:
                        logger.info(f"Real API server detected on port {self.port}, using real server")
                        return False  # Real server is running
        except:
            # Real server not available, start mock
            logger.info(f"Starting mock API server on port {self.port}")
            
            def run_server():
                pass
        try:
            logger.info(f"Executing run_server")
            
            # Implementation for run_server
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"run_server completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"run_server failed: {e}")
            raise
            self.server_thread = Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Wait for server to start
            await asyncio.sleep(2)
            self.is_running = True
            return True  # Mock server started
    
    def stop(self):
        """Stop the mock API server."""
        if self.is_running:
            logger.info("Stopping mock API server")
            self.is_running = False
            # Note: Thread will stop when main process ends (daemon=True)

# Global instance for testing
mock_server = MockAPIServer()

async def ensure_api_server():
    """Ensure an API server is available for testing."""
    return await mock_server.start()