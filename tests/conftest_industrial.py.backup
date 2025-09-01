"""
Enhanced conftest.py for industrial testing with automatic mock server setup.
"""

import pytest
import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.utils.mock_api_server import ensure_api_server, mock_server

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_environment():
    """Setup test environment with mock API server if needed."""
    logger.info("Setting up industrial testing environment...")
    
    # Ensure API server is available (real or mock)
    mock_started = await ensure_api_server()
    
    if mock_started:
        logger.info("Mock API server started for testing")
    else:
        logger.info("Using real API server for testing")
    
    yield
    
    # Cleanup
    if mock_started:
        mock_server.stop()
        logger.info("Mock API server stopped")

@pytest.fixture
def api_base_url():
    """Base URL for API testing."""
    return "http://localhost:8000"

@pytest.fixture
def test_user_data():
    """Test user data for registration/login."""
    return {
        "username": "test_user_industrial",
        "email": "test@ainflue-industrial.com",
        "password": "SecureTestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
def test_content_data():
    """Test content data for upload/processing."""
    return {
        "title": "Industrial Test Audio",
        "type": "audio",
        "genre": "test",
        "duration": 180,
        "size": 2048000
    }

@pytest.fixture(scope="session")
def performance_thresholds():
    """Performance thresholds for industrial testing."""
    return {
        "api_response_time_ms": 100,
        "load_test_success_rate": 0.95,
        "concurrent_users_10k": 10000,
        "requests_per_second": 1000,
        "security_score_min": 80.0,
        "chaos_resilience_min": 70.0
    }

@pytest.fixture
def industrial_test_config():
    """Configuration for industrial testing."""
    from tests.config.industrial_testing_config import IndustrialTestConfig
    return IndustrialTestConfig()

# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Performance monitoring
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import time
    import psutil
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            self.start_cpu = None
            self.end_cpu = None
            
        def start(self):
            self.start_time = time.time()
            self.start_memory = psutil.virtual_memory().percent
            self.start_cpu = psutil.cpu_percent()
            
        def stop(self):
            self.end_time = time.time()
            self.end_memory = psutil.virtual_memory().percent
            self.end_cpu = psutil.cpu_percent()
            
        def get_metrics(self):
            if self.start_time and self.end_time:
                return {
                    "duration_seconds": self.end_time - self.start_time,
                    "memory_usage_percent": self.end_memory,
                    "memory_delta": self.end_memory - self.start_memory if self.start_memory else 0,
                    "cpu_usage_percent": self.end_cpu,
                    "cpu_delta": self.end_cpu - self.start_cpu if self.start_cpu else 0
                }
            return {}
            
    return PerformanceMonitor()

@pytest.fixture
def test_logger():
    """Logger for test reporting."""
    return logging.getLogger("industrial_testing")

# Pytest hooks for industrial testing
def pytest_configure(config):
    """Configure pytest for industrial testing."""
    # Register custom markers
    config.addinivalue_line("markers", "industrial: Industrial-grade tests")
    config.addinivalue_line("markers", "zero_mocks: Tests with zero mocks for business logic")
    config.addinivalue_line("markers", "real_api: Tests using real API calls")
    config.addinivalue_line("markers", "load_10k: Load tests with 10K+ users")
    config.addinivalue_line("markers", "sub_100ms: Performance tests requiring <100ms response")

def pytest_collection_modifyitems(config, items):
    """Modify test collection for industrial testing."""
    # Add default markers based on file location
    for item in items:
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        if "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "industrial" in str(item.fspath):
            item.add_marker(pytest.mark.industrial)

def pytest_runtest_setup(item):
    """Setup for each test."""
    # Log test start
    logger.info(f"Starting test: {item.nodeid}")

def pytest_runtest_teardown(item, nextitem):
    """Teardown for each test."""
    # Log test completion
    logger.info(f"Completed test: {item.nodeid}")

# Coverage reporting for industrial testing
def pytest_sessionfinish(session, exitstatus):
    """Session finish hook for reporting."""
    if hasattr(session.config, '_coverage'):
        logger.info("Generating coverage report for industrial testing...")