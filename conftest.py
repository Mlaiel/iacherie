"""
Minimal pytest configuration for Ainflue platform tests.
Bypasses complex configuration to enable test execution.

Author: Copilot Assistant
Purpose: Enable unit test execution by providing minimal fixtures
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock Redis client for testing."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = 0
    redis_mock.incr.return_value = 1
    redis_mock.expire.return_value = True
    return redis_mock

@pytest.fixture
def mock_ai_model():
    """Mock AI model for testing."""
    mock = AsyncMock()
    mock.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 153  # 768 dimensions
    mock.predict.return_value = {'similarity': 0.95, 'confidence': 0.98}
    return mock

@pytest.fixture
def sample_audio_file():
    """Create sample audio file for testing."""
    return "/tmp/test_audio.mp3"

@pytest.fixture
def sample_video_file():
    """Create sample video file for testing."""
    return "/tmp/test_video.mp4"

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'TestPassword123!',
        'full_name': 'Test User',
        'country': 'US',
        'language': 'en'
    }

@pytest.fixture(autouse=True)
def setup_minimal_environment():
    """Setup minimal test environment."""
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['DEBUG'] = 'true'
    yield
    # Cleanup is optional for minimal setup