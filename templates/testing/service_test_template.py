"""{{test_name}} Service Test Template for Ainflue Platform
{{test_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import pytest
import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
import json
import tempfile
import os
import uuid
from contextlib import asynccontextmanager

# Test framework imports
import pytest
from pytest_asyncio import fixture
from pytest_mock import MockerFixture
from freezegun import freeze_time
from faker import Faker
from httpx import AsyncClient
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession

# Application imports (adjust based on your project structure)
from core.config import get_settings
from core.database import get_async_session
from core.base_service import BaseService
from utils.exceptions import ServiceException, ValidationError
from monitoring.test_metrics import TestMetricsCollector
from tests.fixtures import create_test_user, create_test_data
from tests.utils import assert_service_response, mock_external_service

# Initialize test utilities
fake = Faker()
settings = get_settings()


class ServiceTestBase:
    """Base class for service testing with common utilities"""
    
    def __init__(self):
        self.test_data_factory = TestDataFactory()
        self.mock_manager = MockManager()
        self.metrics_collector = TestMetricsCollector()
        
    async def setup_test_environment(self):
        """Setup test environment"""
        # Setup test database
        self.test_db = await self._create_test_database()
        
        # Setup test Redis
        self.test_redis = await self._create_test_redis()
        
        # Setup test services
        self.test_services = await self._create_test_services()
        
    async def teardown_test_environment(self):
        """Cleanup test environment"""
        # Cleanup database
        if hasattr(self, 'test_db'):
            await self.test_db.close()
        
        # Cleanup Redis
        if hasattr(self, 'test_redis'):
            await self.test_redis.close()
        
        # Cleanup services
        if hasattr(self, 'test_services'):
            for service in self.test_services.values():
                if hasattr(service, 'cleanup'):
                    await service.cleanup()
    
    async def _create_test_database(self):
        """Create isolated test database"""
        # Implementation would create test DB session
        pass
    
    async def _create_test_redis(self):
        """Create test Redis connection"""
        # Implementation would create test Redis instance
        pass
    
    async def _create_test_services(self):
        """Create test service instances"""
        # Implementation would create service instances
        pass


class TestDataFactory:
    """Factory for creating test data"""
    
    def __init__(self):
        self.faker = Faker()
    
    def create_user_data(self, **overrides) -> Dict[str, Any]:
        """Create test user data"""
        user_data = {
            'user_id': str(uuid.uuid4()),
            'username': self.faker.user_name(),
            'email': self.faker.email(),
            'first_name': self.faker.first_name(),
            'last_name': self.faker.last_name(),
            'created_at': datetime.utcnow(),
            'is_active': True,
            'metadata': {}
        }
        user_data.update(overrides)
        return user_data
    
    def create_content_data(self, **overrides) -> Dict[str, Any]:
        """Create test content data"""
        content_data = {
            'content_id': str(uuid.uuid4()),
            'title': self.faker.sentence(),
            'description': self.faker.text(),
            'content_type': self.faker.random_element(['video', 'audio', 'image', 'text']),
            'author_id': str(uuid.uuid4()),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'published',
            'tags': [self.faker.word() for _ in range(3)],
            'metadata': {
                'views': self.faker.random_int(0, 10000),
                'likes': self.faker.random_int(0, 1000),
                'shares': self.faker.random_int(0, 500)
            }
        }
        content_data.update(overrides)
        return content_data
    
    def create_service_request(self, **overrides) -> Dict[str, Any]:
        """Create test service request"""
        request_data = {
            'request_id': str(uuid.uuid4()),
            'operation': 'test_operation',
            'parameters': {'test_param': 'test_value'},
            'user_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow(),
            'metadata': {}
        }
        request_data.update(overrides)
        return request_data
    
    def create_api_response(self, **overrides) -> Dict[str, Any]:
        """Create test API response"""
        response_data = {
            'status': 'success',
            'data': {'result': 'test_result'},
            'message': 'Operation completed successfully',
            'timestamp': datetime.utcnow(),
            'request_id': str(uuid.uuid4())
        }
        response_data.update(overrides)
        return response_data
    
    def create_error_response(self, **overrides) -> Dict[str, Any]:
        """Create test error response"""
        error_data = {
            'status': 'error',
            'error_code': 'TEST_ERROR',
            'error_message': 'Test error occurred',
            'timestamp': datetime.utcnow(),
            'request_id': str(uuid.uuid4()),
            'details': {}
        }
        error_data.update(overrides)
        return error_data


class MockManager:
    """Manager for creating and configuring mocks"""
    
    def __init__(self):
        self.active_mocks = {}
        self.patchers = []
    
    def create_async_mock(self, return_value=None, side_effect=None):
        """Create async mock with specified behavior"""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
    
    def create_service_mock(self, service_class, **method_returns):
        """Create mock for service class"""
        mock_service = Mock(spec=service_class)
        
        # Set up method return values
        for method_name, return_value in method_returns.items():
            if asyncio.iscoroutinefunction(getattr(service_class, method_name, None)):
                setattr(mock_service, method_name, self.create_async_mock(return_value))
            else:
                setattr(mock_service, method_name, Mock(return_value=return_value))
        
        return mock_service
    
    def create_database_mock(self, query_results=None):
        """Create database mock"""
        db_mock = AsyncMock()
        
        if query_results:
            # Configure query results
            for query, result in query_results.items():
                db_mock.execute.return_value.fetchall.return_value = result
        
        return db_mock
    
    def create_redis_mock(self, key_values=None):
        """Create Redis mock"""
        redis_mock = AsyncMock()
        
        if key_values:
            # Configure key-value responses
            async def get_side_effect(key):
                return key_values.get(key)
            
            redis_mock.get.side_effect = get_side_effect
        
        return redis_mock
    
    def create_http_client_mock(self, responses=None):
        """Create HTTP client mock"""
        client_mock = AsyncMock()
        
        if responses:
            # Configure HTTP responses
            for url, response in responses.items():
                mock_response = Mock()
                mock_response.status_code = response.get('status_code', 200)
                mock_response.json.return_value = response.get('json', {})
                mock_response.text = response.get('text', '')
                
                client_mock.get.return_value = mock_response
                client_mock.post.return_value = mock_response
                client_mock.put.return_value = mock_response
                client_mock.delete.return_value = mock_response
        
        return client_mock
    
    def cleanup_mocks(self):
        """Cleanup all active mocks"""
        for patcher in self.patchers:
            patcher.stop()
        self.patchers.clear()
        self.active_mocks.clear()


class ServiceTestAssertions:
    """Custom assertions for service testing"""
    
    @staticmethod
    def assert_service_response(response, expected_status='success', required_fields=None):
        """Assert service response structure and content"""
        assert 'status' in response
        assert response['status'] == expected_status
        
        if required_fields:
            for field in required_fields:
                assert field in response, f"Required field '{field}' missing from response"
    
    @staticmethod
    def assert_error_response(response, expected_error_code=None, expected_message=None):
        """Assert error response structure"""
        assert 'status' in response
        assert response['status'] == 'error'
        assert 'error_code' in response
        assert 'error_message' in response
        
        if expected_error_code:
            assert response['error_code'] == expected_error_code
        
        if expected_message:
            assert expected_message in response['error_message']
    
    @staticmethod
    def assert_performance_within_limits(execution_time, max_time):
        """Assert operation completed within time limits"""
        assert execution_time <= max_time, f"Operation took {execution_time}s, expected <= {max_time}s"
    
    @staticmethod
    def assert_database_called_with(mock_db, expected_query_pattern):
        """Assert database was called with expected query"""
        calls = mock_db.execute.call_args_list
        query_found = any(expected_query_pattern in str(call) for call in calls)
        assert query_found, f"Expected query pattern '{expected_query_pattern}' not found in database calls"
    
    @staticmethod
    def assert_cache_accessed(mock_redis, expected_keys):
        """Assert cache was accessed for expected keys"""
        for key in expected_keys:
            mock_redis.get.assert_any_call(key)
    
    @staticmethod
    def assert_external_service_called(mock_client, expected_url, method='GET'):
        """Assert external service was called"""
        method_mock = getattr(mock_client, method.lower())
        method_mock.assert_called()
        
        # Check if URL was called
        calls = method_mock.call_args_list
        url_found = any(expected_url in str(call) for call in calls)
        assert url_found, f"Expected URL '{expected_url}' not found in {method} calls"


class {{test_class_name}}(ServiceTestBase, unittest.IsolatedAsyncioTestCase):
    """
    Comprehensive service test template for {{test_description}}.
    
    Features:
    - Async/await test support
    - Service isolation and mocking
    - Database transaction rollback
    - Redis cache mocking
    - HTTP client mocking
    - Performance benchmarking
    - Error condition testing
    - Integration test support
    - Custom assertions
    - Test data factories
    - Cleanup and teardown
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.test_data = TestDataFactory()
        cls.mock_manager = MockManager()
        cls.assertions = ServiceTestAssertions()
        cls.metrics = TestMetricsCollector()
    
    async def asyncSetUp(self):
        """Set up each test"""
        await self.setup_test_environment()
        
        # Create test service instance
        self.service = self._create_service_under_test()
        
        # Setup common mocks
        self.db_mock = self.mock_manager.create_database_mock()
        self.redis_mock = self.mock_manager.create_redis_mock()
        self.http_mock = self.mock_manager.create_http_client_mock()
        
        # Track test start time
        self.test_start_time = datetime.utcnow()
    
    async def asyncTearDown(self):
        """Clean up after each test"""
        await self.teardown_test_environment()
        self.mock_manager.cleanup_mocks()
        
        # Record test metrics
        test_duration = (datetime.utcnow() - self.test_start_time).total_seconds()
        await self.metrics.record_test_completed(
            test_name=self._testMethodName,
            duration=test_duration,
            status='passed'  # This would be updated based on actual result
        )
    
    def _create_service_under_test(self):
        """Create the service instance being tested"""
        # Override this method to return your specific service
        return Mock(spec=BaseService)
    
    # Test Methods Template
    
    async def test_service_initialization(self):
        """Test service initialization"""
        # Test successful initialization
        service = self._create_service_under_test()
        
        # Assert service is properly initialized
        assert service is not None
        assert hasattr(service, 'name')
        
        # Test initialization with custom config
        config = {'test_setting': 'test_value'}
        service_with_config = self._create_service_under_test()
        
        # Verify config is applied
        # Add specific assertions based on your service
    
    async def test_service_basic_operation(self):
        """Test basic service operation"""
        # Arrange
        test_request = self.test_data.create_service_request()
        expected_response = self.test_data.create_api_response()
        
        # Configure mocks
        self.service.process_request = self.mock_manager.create_async_mock(
            return_value=expected_response
        )
        
        # Act
        start_time = datetime.utcnow()
        result = await self.service.process_request(test_request)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Assert
        self.assertions.assert_service_response(result)
        self.assertions.assert_performance_within_limits(execution_time, 1.0)
    
    async def test_service_with_database_interaction(self):
        """Test service operation with database interaction"""
        # Arrange
        test_user_data = self.test_data.create_user_data()
        
        # Configure database mock
        self.db_mock.execute.return_value.fetchone.return_value = test_user_data
        
        # Patch database session
        with patch('core.database.get_async_session', return_value=self.db_mock):
            # Act
            result = await self.service.get_user(test_user_data['user_id'])
            
            # Assert
            assert result is not None
            self.assertions.assert_database_called_with(self.db_mock, 'SELECT')
    
    async def test_service_with_cache_interaction(self):
        """Test service operation with cache interaction"""
        # Arrange
        cache_key = "test:cache:key"
        cached_value = {"cached": "data"}
        
        # Configure Redis mock
        self.redis_mock.get.return_value = json.dumps(cached_value)
        
        # Patch Redis client
        with patch('aioredis.from_url', return_value=self.redis_mock):
            # Act
            result = await self.service.get_cached_data(cache_key)
            
            # Assert
            assert result == cached_value
            self.assertions.assert_cache_accessed(self.redis_mock, [cache_key])
    
    async def test_service_with_external_api_call(self):
        """Test service operation with external API call"""
        # Arrange
        external_url = "https://api.example.com/data"
        expected_response = {"external": "data"}
        
        # Configure HTTP client mock
        responses = {
            external_url: {
                'status_code': 200,
                'json': expected_response
            }
        }
        http_mock = self.mock_manager.create_http_client_mock(responses)
        
        # Patch HTTP client
        with patch('httpx.AsyncClient', return_value=http_mock):
            # Act
            result = await self.service.fetch_external_data(external_url)
            
            # Assert
            assert result == expected_response
            self.assertions.assert_external_service_called(http_mock, external_url)
    
    async def test_service_error_handling(self):
        """Test service error handling"""
        # Test validation error
        invalid_request = {'invalid': 'data'}
        
        with pytest.raises(ValidationError):
            await self.service.process_request(invalid_request)
        
        # Test service error
        self.service.process_request = self.mock_manager.create_async_mock(
            side_effect=ServiceException("Test service error")
        )
        
        with pytest.raises(ServiceException):
            await self.service.process_request({})
    
    async def test_service_concurrent_operations(self):
        """Test service under concurrent load"""
        # Arrange
        num_concurrent_requests = 10
        requests = [
            self.test_data.create_service_request()
            for _ in range(num_concurrent_requests)
        ]
        
        # Configure service mock
        self.service.process_request = self.mock_manager.create_async_mock(
            return_value=self.test_data.create_api_response()
        )
        
        # Act
        start_time = datetime.utcnow()
        tasks = [self.service.process_request(req) for req in requests]
        results = await asyncio.gather(*tasks)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Assert
        assert len(results) == num_concurrent_requests
        for result in results:
            self.assertions.assert_service_response(result)
        
        # Check performance (all requests should complete within reasonable time)
        self.assertions.assert_performance_within_limits(execution_time, 5.0)
    
    async def test_service_rate_limiting(self):
        """Test service rate limiting"""
        # Arrange
        rate_limit = 5  # 5 requests per minute
        requests = [
            self.test_data.create_service_request()
            for _ in range(rate_limit + 2)
        ]
        
        # Act & Assert
        # First 5 requests should succeed
        for i in range(rate_limit):
            result = await self.service.process_request(requests[i])
            self.assertions.assert_service_response(result)
        
        # Additional requests should be rate limited
        with pytest.raises(ServiceException) as exc_info:
            await self.service.process_request(requests[rate_limit])
        
        assert "rate limit" in str(exc_info.value).lower()
    
    async def test_service_timeout_handling(self):
        """Test service timeout handling"""
        # Arrange
        slow_operation = self.mock_manager.create_async_mock(
            side_effect=asyncio.sleep(10)  # Simulate slow operation
        )
        self.service.slow_operation = slow_operation
        
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                self.service.slow_operation(),
                timeout=1.0  # 1 second timeout
            )
    
    async def test_service_data_validation(self):
        """Test service input data validation"""
        # Test valid data
        valid_data = self.test_data.create_service_request()
        result = await self.service.validate_input(valid_data)
        assert result is True
        
        # Test invalid data types
        invalid_data = {
            'request_id': 123,  # Should be string
            'operation': None,  # Should be string
            'parameters': 'invalid'  # Should be dict
        }
        
        with pytest.raises(ValidationError):
            await self.service.validate_input(invalid_data)
        
        # Test missing required fields
        incomplete_data = {'request_id': str(uuid.uuid4())}
        
        with pytest.raises(ValidationError):
            await self.service.validate_input(incomplete_data)
    
    async def test_service_cleanup(self):
        """Test service cleanup"""
        # Arrange
        self.service.cleanup = self.mock_manager.create_async_mock()
        
        # Act
        await self.service.cleanup()
        
        # Assert
        self.service.cleanup.assert_called_once()
    
    # Parameterized Tests
    
    @pytest.mark.parametrize("input_data,expected_output", [
        ({"type": "A", "value": 1}, {"result": "A1"}),
        ({"type": "B", "value": 2}, {"result": "B2"}),
        ({"type": "C", "value": 3}, {"result": "C3"}),
    ])
    async def test_service_with_parameters(self, input_data, expected_output):
        """Test service with parameterized inputs"""
        # Configure mock
        self.service.transform_data = self.mock_manager.create_async_mock(
            return_value=expected_output
        )
        
        # Act
        result = await self.service.transform_data(input_data)
        
        # Assert
        assert result == expected_output
    
    # Integration Tests
    
    @pytest.mark.integration
    async def test_service_integration_flow(self):
        """Test complete service integration flow"""
        # This test would use real dependencies (database, Redis, etc.)
        # Mark with @pytest.mark.integration to run separately
        
        # Arrange
        test_data = self.test_data.create_content_data()
        
        # Act - Full flow from request to response
        create_result = await self.service.create_content(test_data)
        retrieved_result = await self.service.get_content(create_result['content_id'])
        update_data = {'title': 'Updated Title'}
        update_result = await self.service.update_content(
            create_result['content_id'], 
            update_data
        )
        
        # Assert
        self.assertions.assert_service_response(create_result)
        self.assertions.assert_service_response(retrieved_result)
        self.assertions.assert_service_response(update_result)
        
        assert retrieved_result['data']['title'] == test_data['title']
        assert update_result['data']['title'] == update_data['title']
    
    # Performance Tests
    
    @pytest.mark.performance
    async def test_service_performance_benchmark(self):
        """Test service performance benchmarks"""
        # Arrange
        num_operations = 100
        max_avg_time = 0.1  # 100ms average
        
        # Act
        start_time = datetime.utcnow()
        
        tasks = []
        for _ in range(num_operations):
            task = asyncio.create_task(
                self.service.benchmark_operation()
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        avg_time = total_time / num_operations
        
        # Assert
        assert avg_time <= max_avg_time, f"Average time {avg_time}s exceeds limit {max_avg_time}s"
        
        # Record benchmark results
        await self.metrics.record_performance_benchmark(
            operation_name="benchmark_operation",
            num_operations=num_operations,
            total_time=total_time,
            avg_time=avg_time
        )


# Test Fixtures (can be moved to conftest.py)

@pytest.fixture
async def test_service():
    """Fixture for creating test service instance"""
    service = Mock(spec=BaseService)
    yield service
    
    # Cleanup
    if hasattr(service, 'cleanup'):
        await service.cleanup()


@pytest.fixture
async def test_database():
    """Fixture for test database session"""
    # Create test database session
    # This would create an actual test database or use SQLite in memory
    db_session = Mock(spec=AsyncSession)
    yield db_session
    
    # Cleanup
    await db_session.close()


@pytest.fixture
async def test_redis():
    """Fixture for test Redis connection"""
    # Create test Redis connection
    redis_client = Mock()
    yield redis_client
    
    # Cleanup
    await redis_client.close()


@pytest.fixture
def test_data_factory():
    """Fixture for test data factory"""
    return TestDataFactory()


@pytest.fixture
def mock_manager():
    """Fixture for mock manager"""
    manager = MockManager()
    yield manager
    manager.cleanup_mocks()


# Custom Pytest Markers
pytestmark = [
    pytest.mark.asyncio,  # Mark all tests as async
]


# Performance Test Configuration
@pytest.mark.performance
class PerformanceTestConfig:
    """Configuration for performance tests"""
    MAX_RESPONSE_TIME = 1.0  # seconds
    MAX_MEMORY_USAGE = 100 * 1024 * 1024  # 100MB
    MAX_CPU_USAGE = 0.8  # 80%


# Test Utilities

def skip_if_no_redis():
    """Skip test if Redis is not available"""
    try:
        import redis
        r = redis.Redis()
        r.ping()
        return False
    except:
        return True


def skip_if_no_database():
    """Skip test if database is not available"""
    try:
        # Test database connection
        return False
    except:
        return True


# Example usage:
# @pytest.mark.skipif(skip_if_no_redis(), reason="Redis not available")
# async def test_redis_dependent_feature(self):
#     pass