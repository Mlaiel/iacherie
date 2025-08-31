"""
Test Configuration and Shared Fixtures

Provides shared test configuration, fixtures, and utilities for comprehensive monitoring tests.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import pytest
import pytest_asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import tempfile
import shutil
from pathlib import Path

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test data constants
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_REPORTS_DIR = Path(__file__).parent / "test_reports"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_metrics_data():
    """Generate sample metrics data for testing."""
    return {
        "ai_performance": {
            "model_inference_time": 0.25,
            "model_accuracy": 0.95,
            "throughput": 1000,
            "error_rate": 0.01
        },
        "business_metrics": {
            "revenue": 15000.0,
            "active_users": 5000,
            "conversion_rate": 0.12,
            "retention_rate": 0.85
        },
        "system_health": {
            "cpu_usage": 65.5,
            "memory_usage": 78.2,
            "disk_usage": 45.0,
            "network_latency": 12.5
        }
    }

@pytest.fixture
def sample_content_data():
    """Generate sample content data for testing."""
    return {
        "content_id": "content_123",
        "user_id": "user_456",
        "content_type": "audio",
        "size_bytes": 5242880,
        "duration_seconds": 180,
        "upload_timestamp": datetime.utcnow(),
        "processing_stages": [
            "upload", "protection", "seo", "collaboration", "distribution"
        ],
        "metadata": {
            "title": "Test Audio Content",
            "description": "Sample audio for testing",
            "tags": ["music", "test", "demo"]
        }
    }

@pytest.fixture
def sample_business_data():
    """Generate sample business data for testing."""
    return {
        "revenue_data": [
            {"date": "2025-01-01", "amount": 1000.0, "source": "subscription"},
            {"date": "2025-01-02", "amount": 750.0, "source": "advertising"},
            {"date": "2025-01-03", "amount": 500.0, "source": "premium_features"}
        ],
        "user_engagement": {
            "daily_active_users": 1500,
            "session_duration": 1800,
            "page_views": 25000,
            "bounce_rate": 0.25
        },
        "creator_metrics": {
            "total_creators": 800,
            "active_creators": 650,
            "content_uploads": 120,
            "collaboration_requests": 45
        }
    }

@pytest.fixture
def sample_anomaly_data():
    """Generate sample anomaly data for testing."""
    import numpy as np
    
    # Normal data with some anomalies
    normal_data = np.random.normal(100, 15, 1000)
    anomalies = [500, -50, 1000, 2000]  # Clear outliers
    
    return {
        "normal_data": normal_data.tolist(),
        "data_with_anomalies": np.concatenate([normal_data, anomalies]).tolist(),
        "expected_anomalies": len(anomalies),
        "threshold": 3.0  # Standard deviations
    }

@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.exists.return_value = False
    mock_redis.delete.return_value = 1
    mock_redis.expire.return_value = True
    return mock_redis

@pytest.fixture
def mock_database_session():
    """Create a mock database session for testing."""
    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock()
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    return mock_session

@pytest.fixture
def mock_metrics_collector():
    """Create a mock metrics collector for testing."""
    from ai.core.metrics import MetricsCollector
    
    collector = AsyncMock(spec=MetricsCollector)
    collector.record_metric.return_value = None
    collector.get_metrics.return_value = []
    collector.clear_metrics.return_value = None
    return collector

@pytest.fixture
def performance_test_config():
    """Configuration for performance testing."""
    return {
        "max_response_time": 1.0,  # seconds
        "max_memory_usage": 100,   # MB
        "max_cpu_usage": 80,       # percentage
        "concurrent_requests": 10,
        "test_duration": 30        # seconds
    }

@pytest.fixture
def alert_test_config():
    """Configuration for alert testing."""
    return {
        "alert_channels": ["email", "slack", "webhook"],
        "severity_levels": ["info", "warning", "error", "critical"],
        "notification_timeout": 5.0,  # seconds
        "escalation_delay": 60.0      # seconds
    }

@pytest.fixture
def health_check_endpoints():
    """Sample health check endpoints for testing."""
    return {
        "database": "postgresql://test:test@localhost:5432/test",
        "redis": "redis://localhost:6379/0",
        "api_endpoints": [
            "http://localhost:8000/health",
            "http://localhost:8000/api/v1/status"
        ],
        "ai_models": [
            "content_generator",
            "content_protector",
            "seo_optimizer"
        ]
    }

@pytest.fixture
async def monitoring_system_setup():
    """Set up a complete monitoring system for integration tests."""
    from ai.monitoring import MonitoringIntegrationHub
    
    # Initialize monitoring components
    hub = MonitoringIntegrationHub()
    await hub.initialize()
    
    yield hub
    
    # Cleanup
    await hub.shutdown()

@pytest.fixture
def test_time_range():
    """Generate a test time range for time-based tests."""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    return {
        "start_time": start_time,
        "end_time": end_time,
        "duration_hours": 24
    }

@pytest.fixture
def real_data_samples():
    """Provide real-world data samples for comprehensive testing."""
    return {
        "audio_file_sizes": [2048000, 5242880, 10485760, 20971520],  # Various audio sizes
        "processing_times": [0.5, 1.2, 2.8, 5.5, 12.0],  # Realistic processing times
        "user_sessions": [300, 1800, 3600, 7200],  # Session durations in seconds
        "revenue_amounts": [9.99, 19.99, 49.99, 99.99, 199.99],  # Subscription tiers
        "error_rates": [0.001, 0.005, 0.01, 0.02, 0.05]  # Acceptable error rates
    }

# Test data creation utilities
def create_test_report_data():
    """Create comprehensive test report data."""
    return {
        "report_id": "test_report_001",
        "generated_at": datetime.utcnow(),
        "report_type": "comprehensive",
        "data_sources": ["ai_performance", "business_metrics", "system_health"],
        "metrics_count": 1500,
        "anomalies_detected": 5,
        "alerts_triggered": 2
    }

def create_test_ai_model_data():
    """Create AI model test data."""
    return {
        "model_id": "test_model_001",
        "model_type": "content_generator",
        "version": "1.2.3",
        "deployment_date": datetime.utcnow() - timedelta(days=30),
        "performance_metrics": {
            "accuracy": 0.95,
            "precision": 0.92,
            "recall": 0.88,
            "f1_score": 0.90
        },
        "resource_usage": {
            "memory_mb": 512,
            "cpu_cores": 2,
            "gpu_memory_mb": 1024
        }
    }

# Performance testing utilities
class PerformanceValidator:
    """Utility class for validating performance metrics."""
    
    @staticmethod
    def validate_response_time(response_time: float, max_time: float = 1.0) -> bool:
        """Validate response time is within acceptable limits."""
        return response_time <= max_time
    
    @staticmethod
    def validate_memory_usage(memory_mb: float, max_memory: float = 100.0) -> bool:
        """Validate memory usage is within acceptable limits."""
        return memory_mb <= max_memory
    
    @staticmethod
    def validate_throughput(requests_per_second: float, min_throughput: float = 100.0) -> bool:
        """Validate throughput meets minimum requirements."""
        return requests_per_second >= min_throughput

# Test data generators
class TestDataGenerator:
    """Generate realistic test data for various scenarios."""
    
    @staticmethod
    def generate_time_series_data(
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 5,
        base_value: float = 100.0,
        variance: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Generate time series data for testing."""
        import random
        
        data = []
        current_time = start_time
        
        while current_time <= end_time:
            value = base_value + random.uniform(-variance, variance)
            data.append({
                "timestamp": current_time,
                "value": value
            })
            current_time += timedelta(minutes=interval_minutes)
        
        return data
    
    @staticmethod
    def generate_user_activity_data(num_users: int = 1000) -> List[Dict[str, Any]]:
        """Generate user activity data for testing."""
        import random
        
        activities = []
        for i in range(num_users):
            activities.append({
                "user_id": f"user_{i:04d}",
                "session_duration": random.randint(300, 7200),
                "pages_viewed": random.randint(5, 50),
                "actions_performed": random.randint(1, 20),
                "last_active": datetime.utcnow() - timedelta(
                    hours=random.randint(0, 48)
                )
            })
        
        return activities
