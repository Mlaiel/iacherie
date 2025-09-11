"""Test Configuration for MongoDB Module
=====================================

Configuration and fixtures for MongoDB testing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import pytest
import asyncio
import os
from typing import Dict, Any, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path

# Add project root to Python path
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MongoDB modules
try:
    from mongodb.connection import MongoDBConnection, MongoDBConfig
    from mongodb.models import BaseModel
    from mongodb.collections import CollectionManager
    MONGODB_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"MongoDB modules not available: {e}")
    MONGODB_MODULES_AVAILABLE = False

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Environment setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["MONGODB_TEST_MODE"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup after tests
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "MONGODB_TEST_MODE" in os.environ:
        del os.environ["MONGODB_TEST_MODE"]

@pytest.fixture
def mock_mongodb_config() -> MongoDBConfig:
    """Mock MongoDB configuration for testing."""
    if MONGODB_MODULES_AVAILABLE:
        return MongoDBConfig(
            host="localhost",
            port=27017,
            database="ainflue_test",
            username="test_user",
            password="test_pass",
            connection_timeout=10,
            server_selection_timeout=10
        )
    else:
        # Return a mock object if modules not available
        mock = MagicMock()
        mock.host = "localhost"
        mock.port = 27017
        mock.database = "ainflue_test"
        return mock

@pytest.fixture
async def mock_mongodb_connection(mock_mongodb_config):
    """Mock MongoDB connection for testing."""
    if MONGODB_MODULES_AVAILABLE:
        connection = MongoDBConnection(mock_mongodb_config)
        # Mock the actual connection methods
        connection.client = AsyncMock()
        connection.database = AsyncMock()
        connection.is_connected = True
        return connection
    else:
        mock = AsyncMock()
        mock.config = mock_mongodb_config
        mock.is_connected = True
        return mock

@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "created_at": "2024-01-01T00:00:00Z",
        "is_active": True,
        "profile": {
            "bio": "Test user bio",
            "followers": 100,
            "following": 50
        }
    }

@pytest.fixture
def sample_content_data() -> Dict[str, Any]:
    """Sample content data for testing."""
    return {
        "title": "Test Content",
        "description": "Test content description",
        "content_type": "video",
        "tags": ["test", "content"],
        "metadata": {
            "duration": 120,
            "resolution": "1080p",
            "file_size": 1024000
        },
        "created_at": "2024-01-01T00:00:00Z",
        "is_published": True
    }

@pytest.mark.asyncio
class AsyncTestCase:
    """Base class for async test cases."""
    
    async def setup_method(self):
        """Setup for each test method."""
        pass
    
    async def teardown_method(self):
        """Cleanup for each test method."""
        pass

class MongoDBTestCase(AsyncTestCase):
    """Base class for MongoDB test cases."""
    
    def __init__(self):
        self.connection = None
        self.config = None
    
    async def setup_method(self):
        """Setup MongoDB test environment."""
        await super().setup_method()
        # Additional MongoDB-specific setup
        pass
    
    async def teardown_method(self):
        """Cleanup MongoDB test environment."""
        # Cleanup MongoDB-specific resources
        await super().teardown_method()

# Test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add integration marker
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker
        if "performance" in item.name.lower() or "benchmark" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        
        # Add security marker
        if "security" in item.name.lower() or "auth" in item.name.lower():
            item.add_marker(pytest.mark.security)
        
        # Add slow marker for tests that might take longer
        if any(keyword in item.name.lower() for keyword in ["slow", "large", "bulk", "stress"]):
            item.add_marker(pytest.mark.slow)