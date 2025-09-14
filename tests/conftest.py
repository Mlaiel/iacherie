"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop() -> None:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_database() -> None:
    """Mock database for testing"""
    # TODO: Setup mock database
    return None


@pytest.fixture
def mock_api_client() -> None:
    """Mock API client for testing"""
    # TODO: Setup mock API client
    return None


@pytest.fixture
def sample_audio_file() -> None:
    """Sample audio file for testing"""
    # TODO: Provide sample audio file
    return None


@pytest.fixture
def sample_video_file() -> None:
    """Sample video file for testing"""
    # TODO: Provide sample video file
    return None


def pytest_configure(config) -> None:
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
