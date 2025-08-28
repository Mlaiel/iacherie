"""
Global pytest configuration and fixtures for Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from redis.asyncio import Redis
from httpx import AsyncClient
from fastapi.testclient import TestClient

from api.main import app
from config import settings
from database.schema import Base


# Test Database Configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_ainflue.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sync_client() -> Generator[TestClient, None, None]:
    """Create synchronous test client for simpler tests."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def mock_redis() -> AsyncMock:
    """Mock Redis client for testing."""
    redis_mock = AsyncMock(spec=Redis)
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = 0
    redis_mock.incr.return_value = 1
    redis_mock.expire.return_value = True
    return redis_mock


@pytest.fixture
def mock_youtube_api():
    """Mock YouTube API for testing."""
    mock = Mock()
    mock.search.return_value.list.return_value.execute.return_value = {
        'items': [
            {
                'id': {'videoId': 'test_video_id'},
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test Description',
                    'channelId': 'test_channel_id',
                    'publishedAt': '2025-01-01T00:00:00Z'
                }
            }
        ]
    }
    return mock


@pytest.fixture
def mock_stripe():
    """Mock Stripe API for testing."""
    mock = Mock()
    mock.PaymentIntent.create.return_value = Mock(
        id='pi_test_123',
        client_secret='pi_test_123_secret',
        status='requires_payment_method'
    )
    mock.Customer.create.return_value = Mock(
        id='cus_test_123',
        email='test@example.com'
    )
    return mock


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
    # Return path to a minimal audio file for testing
    return "/tmp/test_audio.mp3"


@pytest.fixture
def sample_video_file():
    """Create sample video file for testing."""
    # Return path to a minimal video file for testing
    return "/tmp/test_video.mp4"


@pytest.fixture
def sample_image_file():
    """Create sample image file for testing."""
    # Return path to a minimal image file for testing
    return "/tmp/test_image.jpg"


@pytest.fixture
def mock_platform_apis():
    """Mock all social media platform APIs."""
    return {
        'youtube': Mock(),
        'instagram': Mock(),
        'tiktok': Mock(),
        'spotify': Mock(),
        'twitter': Mock(),
        'facebook': Mock()
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Set test environment variables
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['DEBUG'] = 'true'
    os.environ['DATABASE_URL'] = TEST_DATABASE_URL
    
    # Mock sensitive credentials for testing
    os.environ['JWT_SECRET_KEY'] = 'test_jwt_secret_key_for_testing_only'
    os.environ['ENCRYPTION_KEY'] = 'test_encryption_key_for_testing_only'
    os.environ['PASSWORD_SALT'] = 'test_password_salt_for_testing_only'
    
    yield
    
    # Clean up environment variables
    test_vars = [
        'ENVIRONMENT', 'DEBUG', 'DATABASE_URL', 
        'JWT_SECRET_KEY', 'ENCRYPTION_KEY', 'PASSWORD_SALT'
    ]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]


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


@pytest.fixture
def test_content_data():
    """Sample content data for testing."""
    return {
        'title': 'Test Content',
        'description': 'Test content description',
        'content_type': 'audio',
        'file_url': 'https://example.com/test.mp3',
        'platform': 'youtube',
        'metadata': {
            'duration': 180,
            'genre': 'music',
            'language': 'en'
        }
    }


# Performance monitoring fixtures
@pytest.fixture
def performance_monitor():
    """Monitor test performance."""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    duration = end_time - start_time
    if duration > 1.0:  # Log slow tests
        print(f"Slow test detected: {duration:.2f}s")


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Cleanup test data after each test."""
    yield
    # Clean up any test files, cache entries, etc.
    test_files = [
        "/tmp/test_audio.mp3",
        "/tmp/test_video.mp4", 
        "/tmp/test_image.jpg"
    ]
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)