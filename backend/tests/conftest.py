"""Pytest Configuration and Shared Fixtures
import logging

==========================================

Shared pytest fixtures and configuration for all test modules.
Provides common setup/teardown for database, Redis, API clients, etc.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from typing import Dict, Any, AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime

# Conditional imports to avoid dependency issues
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

from . import (
    TEST_CONFIG, 
    TEST_DATA_DIR, 
    generate_test_user_data,
    generate_test_content_data,
    generate_test_api_key,
    generate_test_jwt_token,
    MOCK_DATABASE_DATA,
    logger
)

# Configure pytest
pytest_plugins = []

def pytest_configure(config) -> None:
    """Configure pytest settings"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

@pytest.fixture(scope="session")
def event_loop() -> None:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_config() -> Dict[str, Any]:
    """Test configuration fixture"""
    return TEST_CONFIG.copy()

@pytest.fixture(scope="session")
async def test_data_dir() -> Path:
    """Test data directory fixture"""
    return TEST_DATA_DIR

@pytest.fixture(scope="function")
async def temp_dir() -> AsyncGenerator[Path, None]:
    """Temporary directory fixture for each test"""
    temp_path = Path(tempfile.mkdtemp(prefix="ainflue_test_"))
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path)

@pytest.fixture(scope="session")
async def mock_database_pool() -> None:
    """Mock database connection pool"""
    pool_mock = AsyncMock()
    
    # Mock connection methods
    async def mock_acquire() -> None:
        conn_mock = AsyncMock()
        conn_mock.fetch.return_value = MOCK_DATABASE_DATA["users"][:5]
        conn_mock.fetchrow.return_value = MOCK_DATABASE_DATA["users"][0]
        conn_mock.execute.return_value = "INSERT 0 1"
        conn_mock.executemany.return_value = None
        return conn_mock
    
    pool_mock.acquire = mock_acquire
    pool_mock.close = AsyncMock()
    
    return pool_mock

@pytest.fixture(scope="session")
async def mock_redis_client() -> None:
    """Mock Redis client"""
    redis_mock = AsyncMock()
    
    # Mock Redis operations
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=True)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.hget = AsyncMock(return_value=None)
    redis_mock.hset = AsyncMock(return_value=True)
    redis_mock.hdel = AsyncMock(return_value=1)
    redis_mock.lpush = AsyncMock(return_value=1)
    redis_mock.rpop = AsyncMock(return_value=None)
    redis_mock.sadd = AsyncMock(return_value=1)
    redis_mock.srem = AsyncMock(return_value=1)
    redis_mock.smembers = AsyncMock(return_value=set())
    redis_mock.close = AsyncMock()
    
    return redis_mock

@pytest.fixture(scope="session")
async def mock_http_client() -> None:
    """Mock HTTP client for API testing"""
    
    class MockResponse:
    """MockResponse: class implementation"""
        def __init__(self, json_data, status=200, headers=None) -> None:
            self.json_data = json_data
            self.status = status
            self.headers = headers or {}
            
        async def json(self) -> None:
            return self.json_data
            
        async def text(self) -> None:
            return json.dumps(self.json_data)
            
        def __aenter__(self) -> None:
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
            pass
    
    client_mock = AsyncMock()
    
    # Mock HTTP methods
    async def mock_get(*args, **kwargs) -> None:
        return MockResponse({"success": True, "data": MOCK_DATABASE_DATA["users"]})
    
    async def mock_post(*args, **kwargs) -> None:
        return MockResponse({"success": True, "id": "12345"}, status=201)
    
    async def mock_put(*args, **kwargs) -> None:
        return MockResponse({"success": True, "updated": True})
    
    async def mock_delete(*args, **kwargs) -> None:
        return MockResponse({"success": True, "deleted": True})
    
    client_mock.get = mock_get
    client_mock.post = mock_post
    client_mock.put = mock_put
    client_mock.delete = mock_delete
    client_mock.close = AsyncMock()
    
    return client_mock

@pytest.fixture(scope="function")
async def mock_ai_service() -> None:
    """Mock AI service for testing"""
    service_mock = AsyncMock()
    
    # Mock AI operations
    service_mock.generate_content = AsyncMock(return_value={
        "content": "Generated test content",
        "confidence": 0.95,
        "metadata": {"model": "test-model", "tokens": 150}
    })
    
    service_mock.analyze_content = AsyncMock(return_value={
        "sentiment": "positive",
        "categories": ["technology", "innovation"],
        "quality_score": 0.88,
        "recommendations": ["Add more details", "Include examples"]
    })
    
    service_mock.process_media = AsyncMock(return_value={
        "processed": True,
        "format": "mp4",
        "quality": "1080p",
        "duration": 120,
        "thumbnail_url": "https://example.com/thumb.jpg"
    })
    
    return service_mock

@pytest.fixture(scope="function")
async def mock_payment_service() -> None:
    """Mock payment service for testing"""
    service_mock = AsyncMock()
    
    # Mock payment operations
    service_mock.create_payment = AsyncMock(return_value={
        "payment_id": "pay_12345",
        "status": "succeeded",
        "amount": 1000,
        "currency": "usd"
    })
    
    service_mock.process_refund = AsyncMock(return_value={
        "refund_id": "ref_12345",
        "status": "succeeded",
        "amount": 1000
    })
    
    service_mock.get_payment_status = AsyncMock(return_value={
        "payment_id": "pay_12345",
        "status": "succeeded"
    })
    
    return service_mock

@pytest.fixture(scope="function")
async def mock_notification_service() -> None:
    """Mock notification service for testing"""
    service_mock = AsyncMock()
    
    # Mock notification operations
    service_mock.send_email = AsyncMock(return_value={
        "message_id": "msg_12345",
        "status": "sent",
        "delivered": True
    })
    
    service_mock.send_push = AsyncMock(return_value={
        "notification_id": "notif_12345",
        "status": "delivered",
        "devices_reached": 1
    })
    
    service_mock.send_sms = AsyncMock(return_value={
        "sms_id": "sms_12345",
        "status": "delivered"
    })
    
    return service_mock

@pytest.fixture(scope="function")
async def mock_storage_service() -> None:
    """Mock storage service for testing"""
    service_mock = AsyncMock()
    
    # Mock storage operations
    service_mock.upload_file = AsyncMock(return_value={
        "file_id": "file_12345",
        "url": "https://storage.example.com/file_12345.jpg",
        "size": 1024000,
        "mime_type": "image/jpeg"
    })
    
    service_mock.delete_file = AsyncMock(return_value={
        "deleted": True,
        "file_id": "file_12345"
    })
    
    service_mock.get_file_info = AsyncMock(return_value={
        "file_id": "file_12345",
        "size": 1024000,
        "mime_type": "image/jpeg",
        "created_at": datetime.utcnow().isoformat()
    })
    
    return service_mock

@pytest.fixture(scope="function")
def mock_user_data() -> None:
    """Generate mock user data for testing"""
    return generate_test_user_data()

@pytest.fixture(scope="function")
def mock_content_data() -> None:
    """Generate mock content data for testing"""
    return generate_test_content_data()

@pytest.fixture(scope="function")
def mock_api_key() -> None:
    """Generate mock API key for testing"""
    return generate_test_api_key()

@pytest.fixture(scope="function")
def mock_jwt_token() -> None:
    """Generate mock JWT token for testing"""
    return generate_test_jwt_token()

@pytest.fixture(scope="function")
async def authenticated_user(mock_user_data, mock_jwt_token) -> None:
    """Mock authenticated user with JWT token"""
    return {
        "user": mock_user_data,
        "token": mock_jwt_token,
        "permissions": ["read", "write", "admin"]
    }

@pytest.fixture(scope="function", autouse=True)
async def setup_test_logging() -> None:
    """Setup test logging for each test"""
    # Create test-specific logger
    test_logger = logging.getLogger("test")
    test_logger.setLevel(logging.DEBUG)
    
    # Create handler if not exists
    if not test_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        test_logger.addHandler(handler)
    
    yield test_logger
    
    # Cleanup after test
    for handler in test_logger.handlers[:]:
        test_logger.removeHandler(handler)

@pytest.fixture(scope="function")
async def performance_timer() -> None:
    """Performance timing utility for tests"""
    import time
    
    class Timer:
    """Timer: class implementation"""
        def __init__(self) -> None:
            self.start_time = None
            self.end_time = None
            
        def start(self) -> None:
            self.start_time = time.time()
            
        def stop(self) -> None:
            self.end_time = time.time()
            
        @property
        def elapsed(self) -> None:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
    
    return Timer()

@pytest.fixture(scope="function")
async def mock_external_apis() -> None:
    """Mock external API responses"""
    return {
        "youtube_api": {
            "videos": {"items": [{"id": "test123", "snippet": {"title": "Test Video"}}]},
            "channels": {"items": [{"id": "channel123", "snippet": {"title": "Test Channel"}}]}
        },
        "instagram_api": {
            "media": {"data": [{"id": "media123", "media_type": "IMAGE", "media_url": "test.jpg"}]},
            "user": {"id": "user123", "username": "testuser"}
        },
        "tiktok_api": {
            "videos": {"data": [{"id": "video123", "title": "Test TikTok"}]},
            "user": {"data": {"display_name": "Test User"}}
        }
    }

# Cleanup fixtures
@pytest.fixture(scope="session", autouse=True)
async def cleanup_test_environment() -> None:
    """Cleanup test environment after all tests"""
    yield
    
    # Cleanup test data directory
    if TEST_DATA_DIR.exists():
        for item in TEST_DATA_DIR.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    
    logger.info("Test environment cleanup completed")

# Custom assertion helpers
def assert_valid_uuid(value: str) -> bool:
    """Assert that a string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

def assert_valid_email(email: str) -> bool:
    """Assert that a string is a valid email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def assert_valid_url(url: str) -> bool:
    """Assert that a string is a valid URL"""
    import re
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?$'
    return bool(re.match(pattern, url))

# Export custom helpers
__all__ = [
    "assert_valid_uuid",
    "assert_valid_email", 
    "assert_valid_url"
]
