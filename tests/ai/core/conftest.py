"""
Pytest Configuration for AI Core Module Tests

Advanced test configuration with fixtures, mocks, and test utilities.
Provides enterprise-grade testing infrastructure.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import tempfile
import shutil
import os
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List, Optional
import logging

# Configure test logging
logging.basicConfig(level=logging.DEBUG)

# Import test configuration
from . import TEST_CONFIG, TEST_DATA_CONFIG, MOCK_CREATORS

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def test_config():
    """Global test configuration fixture"""
    return TEST_CONFIG.copy()


@pytest.fixture(scope="session") 
def test_data_config():
    """Test data configuration fixture"""
    return TEST_DATA_CONFIG.copy()


@pytest.fixture(scope="session")
def mock_creators():
    """Mock creator data fixture"""
    return MOCK_CREATORS.copy()


@pytest.fixture
def temp_dir():
    """Temporary directory fixture"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file():
    """Temporary file fixture"""
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    yield temp_path
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_config_file():
    """Temporary configuration file fixture"""
    config_data = {
        "environment": "test",
        "debug_mode": True,
        "ai_engine": {
            "max_concurrent_models": 2,
            "memory_threshold_gb": 1.0
        },
        "validation": {
            "enable_security_validation": True,
            "min_quality_score": 70.0
        },
        "performance": {
            "monitoring_interval": 10
        }
    }
    
    fd, temp_path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w') as f:
        json.dump(config_data, f)
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_audio_file(temp_dir):
    """Mock audio file fixture"""
    audio_path = Path(temp_dir) / "test_audio.mp3"
    # Create a mock audio file (just bytes for testing)
    with open(audio_path, 'wb') as f:
        f.write(b"MOCK_AUDIO_DATA" * 1000)  # ~14KB mock file
    return str(audio_path)


@pytest.fixture
def mock_image_file(temp_dir):
    """Mock image file fixture"""
    image_path = Path(temp_dir) / "test_image.jpg"
    # Create a mock image file
    with open(image_path, 'wb') as f:
        f.write(b"MOCK_IMAGE_DATA" * 1000)  # ~14KB mock file
    return str(image_path)


@pytest.fixture
def mock_text_file(temp_dir):
    """Mock text file fixture"""
    text_path = Path(temp_dir) / "test_text.txt"
    with open(text_path, 'w') as f:
        f.write("This is a test text file for content validation testing.")
    return str(text_path)


@pytest.fixture
def sample_content_data():
    """Sample content data for testing"""
    return {
        "audio": {
            "type": "audio",
            "format": "mp3",
            "duration": 180,
            "file_size": 5242880,
            "metadata": {
                "title": "Test Audio Track",
                "artist": "Test Artist",
                "genre": "Electronic"
            }
        },
        "image": {
            "type": "image", 
            "format": "jpg",
            "resolution": "1920x1080",
            "file_size": 2097152,
            "metadata": {
                "title": "Test Image",
                "photographer": "Test Photographer",
                "location": "Test Location"
            }
        },
        "text": {
            "type": "text",
            "format": "plain",
            "word_count": 500,
            "file_size": 2048,
            "metadata": {
                "title": "Test Article",
                "author": "Test Author",
                "category": "Technology"
            }
        },
        "video": {
            "type": "video",
            "format": "mp4", 
            "duration": 300,
            "file_size": 52428800,
            "metadata": {
                "title": "Test Video",
                "creator": "Test Creator",
                "resolution": "1080p"
            }
        }
    }


@pytest.fixture
def mock_ai_model():
    """Mock AI model fixture"""
    model = MagicMock()
    model.name = "test_model"
    model.size_mb = 100
    model.predict.return_value = {"prediction": "test_result", "confidence": 0.95}
    model.is_loaded = True
    return model


@pytest.fixture
def mock_performance_data():
    """Mock performance data fixture"""
    return {
        "cpu_percent": 45.5,
        "memory_percent": 65.2,
        "disk_usage": 78.9,
        "response_time": 0.125,
        "throughput": 150.0,
        "error_rate": 0.01
    }


@pytest.fixture
def mock_metrics_data():
    """Mock metrics data fixture"""
    from datetime import datetime
    return {
        "timestamp": datetime.now(),
        "metrics": [
            {"name": "response_time", "value": 0.125, "unit": "seconds"},
            {"name": "cpu_usage", "value": 45.5, "unit": "percent"},
            {"name": "memory_usage", "value": 65.2, "unit": "percent"},
            {"name": "requests_count", "value": 100, "unit": "count"}
        ]
    }


@pytest.fixture
def mock_validation_result():
    """Mock validation result fixture"""
    class MockValidationResult:
        def __init__(self, is_valid=True, score=85.0, issues=None):
            self.is_valid = is_valid
            self.score = score
            self.issues = issues or []
            self.timestamp = "2025-08-01T12:00:00Z"
            
    return MockValidationResult


@pytest.fixture
def mock_processing_context():
    """Mock processing context fixture"""
    class MockProcessingContext:
        def __init__(self):
            self.content = {
                "type": "audio",
                "data": "mock_audio_data",
                "metadata": {"title": "Test Track"}
            }
            self.user_id = "test_user_123"
            self.creator_type = "musician"
            self.request_id = "req_123456"
            self.timestamp = "2025-08-01T12:00:00Z"
            
    return MockProcessingContext()


@pytest.fixture
def mock_database_connection():
    """Mock database connection fixture"""
    db_mock = MagicMock()
    db_mock.connect.return_value = True
    db_mock.execute.return_value = {"rows_affected": 1}
    db_mock.fetch.return_value = [{"id": 1, "name": "test"}]
    db_mock.close.return_value = True
    return db_mock


@pytest.fixture
def mock_redis_cache():
    """Mock Redis cache fixture"""
    cache_mock = MagicMock()
    cache_mock.get.return_value = None
    cache_mock.set.return_value = True
    cache_mock.delete.return_value = True
    cache_mock.exists.return_value = False
    return cache_mock


@pytest.fixture
def mock_external_api():
    """Mock external API fixture"""
    api_mock = MagicMock()
    api_mock.get.return_value = {"status": "success", "data": {"result": "test"}}
    api_mock.post.return_value = {"status": "success", "id": "123"}
    api_mock.put.return_value = {"status": "success"}
    api_mock.delete.return_value = {"status": "success"}
    return api_mock


@pytest.fixture
def event_loop():
    """Event loop fixture for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_test_client():
    """Async test client fixture"""
    from aiohttp import ClientSession
    async with ClientSession() as session:
        yield session


@pytest.fixture(scope="session")
def performance_benchmarks():
    """Performance benchmark thresholds"""
    return {
        "validation_max_time": 0.1,  # 100ms
        "ai_inference_max_time": 1.0,  # 1 second
        "pipeline_max_time": 5.0,  # 5 seconds
        "memory_max_usage": 500,  # 500MB
        "cpu_max_usage": 80.0  # 80%
    }


# Pytest configuration
def pytest_configure(config):
    """Pytest configuration hook"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Auto-mark slow tests
    for item in items:
        if "slow" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Auto-setup test environment for each test"""
    # Setup
    os.environ["AI_ENVIRONMENT"] = "test"
    os.environ["AI_DEBUG"] = "true"
    
    yield
    
    # Cleanup
    test_env_vars = [
        "AI_ENVIRONMENT", "AI_DEBUG", "AI_MAX_MODELS",
        "AI_MEMORY_THRESHOLD", "AI_MONITORING_INTERVAL"
    ]
    for var in test_env_vars:
        os.environ.pop(var, None)


@pytest.fixture
def capture_logs():
    """Capture logs during test execution"""
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    
    yield log_capture
    
    # Cleanup
    root_logger.removeHandler(handler)
    root_logger.setLevel(original_level)


# Error handling for tests
@pytest.fixture
def error_handler():
    """Error handling fixture for tests"""
    errors = []
    
    def handle_error(error):
        errors.append(str(error))
        
    yield handle_error, errors


# Mock patches for external dependencies
@pytest.fixture
def mock_torch():
    """Mock PyTorch for tests"""
    with patch('torch.cuda.is_available', return_value=True), \
         patch('torch.cuda.device_count', return_value=1), \
         patch('torch.cuda.get_device_name', return_value="Mock GPU"):
        yield


@pytest.fixture  
def mock_transformers():
    """Mock Transformers library for tests"""
    with patch('transformers.AutoModel.from_pretrained') as mock_model, \
         patch('transformers.AutoTokenizer.from_pretrained') as mock_tokenizer:
        
        mock_model.return_value = MagicMock()
        mock_tokenizer.return_value = MagicMock()
        yield mock_model, mock_tokenizer


@pytest.fixture
def mock_psutil():
    """Mock psutil for system monitoring tests"""
    with patch('psutil.cpu_percent', return_value=45.5), \
         patch('psutil.virtual_memory') as mock_memory, \
         patch('psutil.disk_usage') as mock_disk:
        
        # Mock memory object
        memory_mock = MagicMock()
        memory_mock.percent = 65.2
        memory_mock.total = 8589934592  # 8GB
        memory_mock.available = 2952790016  # ~2.75GB
        mock_memory.return_value = memory_mock
        
        # Mock disk object
        disk_mock = MagicMock()
        disk_mock.percent = 78.9
        disk_mock.total = 1000000000000  # 1TB
        disk_mock.free = 210000000000  # 210GB
        mock_disk.return_value = disk_mock
        
        yield


# Test data generators
@pytest.fixture
def generate_test_audio_content():
    """Generate test audio content"""
    def _generate(duration=180, format="mp3", quality="high"):
        return {
            "type": "audio",
            "format": format,
            "duration": duration,
            "file_size": duration * 1024 * 30,  # Approximate size
            "quality": quality,
            "metadata": {
                "title": f"Test Audio {duration}s",
                "artist": "Test Artist",
                "genre": "Test Genre"
            }
        }
    return _generate


@pytest.fixture
def generate_test_image_content():
    """Generate test image content"""
    def _generate(width=1920, height=1080, format="jpg"):
        return {
            "type": "image",
            "format": format,
            "resolution": f"{width}x{height}",
            "file_size": width * height * 3,  # Approximate size
            "metadata": {
                "title": f"Test Image {width}x{height}",
                "photographer": "Test Photographer",
                "location": "Test Location"
            }
        }
    return _generate


# Performance testing utilities
@pytest.fixture
def performance_tracker():
    """Performance tracking fixture"""
    import time
    import psutil
    
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            
        def start(self):
            self.start_time = time.time()
            self.start_memory = psutil.virtual_memory().percent
            
        def stop(self):
            self.end_time = time.time()
            self.end_memory = psutil.virtual_memory().percent
            
        def get_duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
            
        def get_memory_delta(self):
            if self.start_memory and self.end_memory:
                return self.end_memory - self.start_memory
            return None
            
    return PerformanceTracker()
