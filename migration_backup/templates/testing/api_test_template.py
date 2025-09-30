"""
🧪 API TEST TEMPLATE - QA/TESTING EXPERT IMPLEMENTATION
=======================================================

Enterprise-grade API testing template with:
- Comprehensive test coverage (unit, integration, e2e)
- Performance and load testing
- Security testing (OWASP Top 10)
- Contract testing with Pact
- Test data management and factories
- CI/CD integration with reporting
- Mock server and test doubles
- Parallel test execution

Author: QA/Testing Expert
Version: 1.0.0
"""

import pytest
import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import hashlib
import httpx
import asyncpg
import redis.asyncio as redis
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from faker import Faker
import aiofiles
from jinja2 import Template
import yaml
from pathlib import Path
import requests_mock
from pydantic import BaseModel, Field
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pact
from pact import Consumer, Provider, Like, Term, EachLike
from locust import HttpUser, task, between
import allure
from allure_commons.types import AttachmentType
import pyotp
import jwt
import subprocess
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestEnvironment:
    """Test environment enumeration"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CONTRACT = "contract"


class TestStatus:
    """Test status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"
    BROKEN = "broken"


@dataclass
class TestConfig:
    """Test configuration"""
    # Environment settings
    environment: str = "test"
    base_url: str = "http://localhost:8000"
    database_url: str = "postgresql+asyncpg://test:test@localhost/test_db"
    redis_url: str = "redis://localhost:6379/1"
    
    # Test execution settings
    parallel_workers: int = 4
    test_timeout: int = 300  # seconds
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # Performance testing
    performance_threshold_ms: int = 1000
    load_test_users: int = 100
    load_test_duration: int = 300  # seconds
    
    # Security testing
    enable_security_tests: bool = True
    security_scan_timeout: int = 600
    
    # Test data
    test_data_path: str = "tests/data"
    enable_test_data_cleanup: bool = True
    
    # Reporting
    report_format: str = "allure"
    generate_coverage_report: bool = True
    coverage_threshold: float = 80.0
    
    # Mock settings
    enable_external_mocks: bool = True
    mock_delay_ms: int = 100
    
    # Contract testing
    pact_broker_url: Optional[str] = None
    pact_broker_token: Optional[str] = None


class TestDataFactory:
    """Test data factory using Faker"""
    
    def __init__(self):
        self.faker = Faker()
        Faker.seed(42)  # For reproducible tests
    
    def user_data(self, **overrides) -> Dict[str, Any]:
        """Generate user test data"""
        data = {
            "id": str(uuid.uuid4()),
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "phone": self.faker.phone_number(),
            "address": {
                "street": self.faker.street_address(),
                "city": self.faker.city(),
                "country": self.faker.country_code(),
                "postal_code": self.faker.postcode()
            },
            "profile": {
                "bio": self.faker.text(max_nb_chars=200),
                "avatar_url": self.faker.image_url(),
                "social_links": {
                    "twitter": f"@{self.faker.user_name()}",
                    "instagram": f"@{self.faker.user_name()}"
                }
            },
            "preferences": {
                "language": self.faker.language_code(),
                "timezone": str(self.faker.timezone()),
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            "created_at": self.faker.date_time_this_year().isoformat(),
            "updated_at": self.faker.date_time_this_month().isoformat(),
            "is_verified": self.faker.boolean(),
            "is_premium": self.faker.boolean(chance_of_getting_true=20)
        }
        data.update(overrides)
        return data
    
    def content_data(self, **overrides) -> Dict[str, Any]:
        """Generate content test data"""
        data = {
            "id": str(uuid.uuid4()),
            "title": self.faker.sentence(nb_words=6),
            "description": self.faker.text(max_nb_chars=500),
            "content": self.faker.text(max_nb_chars=2000),
            "type": self.faker.random_element(["video", "image", "audio", "text"]),
            "category": self.faker.random_element(["entertainment", "education", "music", "gaming"]),
            "tags": [self.faker.word() for _ in range(self.faker.random_int(1, 5))],
            "metadata": {
                "duration": self.faker.random_int(10, 3600),
                "resolution": f"{self.faker.random_int(720, 4320)}p",
                "file_size": self.faker.random_int(1000000, 100000000),
                "format": self.faker.file_extension()
            },
            "stats": {
                "views": self.faker.random_int(0, 1000000),
                "likes": self.faker.random_int(0, 50000),
                "comments": self.faker.random_int(0, 1000),
                "shares": self.faker.random_int(0, 500)
            },
            "created_at": self.faker.date_time_this_year().isoformat(),
            "published_at": self.faker.date_time_this_month().isoformat(),
            "is_published": self.faker.boolean(chance_of_getting_true=80),
            "is_monetized": self.faker.boolean(chance_of_getting_true=30)
        }
        data.update(overrides)
        return data
    
    def transaction_data(self, **overrides) -> Dict[str, Any]:
        """Generate transaction test data"""
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "amount": float(self.faker.pydecimal(left_digits=3, right_digits=2, positive=True)),
            "currency": self.faker.currency_code(),
            "type": self.faker.random_element(["purchase", "subscription", "tip", "refund"]),
            "status": self.faker.random_element(["pending", "completed", "failed", "cancelled"]),
            "payment_method": {
                "type": self.faker.random_element(["credit_card", "paypal", "crypto", "bank_transfer"]),
                "last_four": self.faker.credit_card_number()[-4:],
                "brand": self.faker.credit_card_provider()
            },
            "metadata": {
                "ip_address": self.faker.ipv4(),
                "user_agent": self.faker.user_agent(),
                "device_id": str(uuid.uuid4())
            },
            "created_at": self.faker.date_time_this_month().isoformat(),
            "updated_at": self.faker.date_time_this_week().isoformat()
        }
        data.update(overrides)
        return data


class TestDatabase:
    """Test database management"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        
    async def setup(self):
        """Setup test database"""
        self.engine = create_async_engine(
            self.config.database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def cleanup(self):
        """Cleanup test database"""
        if self.engine:
            await self.engine.dispose()
    
    async def create_session(self) -> AsyncSession:
        """Create database session"""
        return self.session_factory()
    
    async def execute_sql_file(self, file_path: str):
        """Execute SQL file"""
        async with aiofiles.open(file_path, 'r') as f:
            sql = await f.read()
        
        async with self.engine.begin() as conn:
            await conn.execute(sa.text(sql))
    
    async def truncate_tables(self, tables: List[str]):
        """Truncate specified tables"""
        async with self.engine.begin() as conn:
            for table in tables:
                await conn.execute(sa.text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))


class ApiTestClient:
    """Enhanced API test client"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.client = None
        self.auth_token = None
        self.session_data = {}
        
    async def setup(self):
        """Setup test client"""
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.test_timeout,
            follow_redirects=True
        )
    
    async def cleanup(self):
        """Cleanup test client"""
        if self.client:
            await self.client.aclose()
    
    async def authenticate(self, username: str, password: str) -> str:
        """Authenticate and store token"""
        response = await self.client.post("/auth/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            self.client.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
            return self.auth_token
        
        raise Exception(f"Authentication failed: {response.text}")
    
    async def request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make request with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.retry_count):
            try:
                response = await self.client.request(method, url, **kwargs)
                return response
            except Exception as e:
                last_exception = e
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        raise last_exception
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET request"""
        return await self.request_with_retry("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST request"""
        return await self.request_with_retry("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT request"""
        return await self.request_with_retry("PUT", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> httpx.Response:
        """PATCH request"""
        return await self.request_with_retry("PATCH", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE request"""
        return await self.request_with_retry("DELETE", url, **kwargs)


class MockServer:
    """Mock server for external dependencies"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.mocks = {}
        self.request_log = []
    
    def add_mock(self, method: str, url: str, response_data: Dict[str, Any], status_code: int = 200):
        """Add mock response"""
        key = f"{method.upper()}:{url}"
        self.mocks[key] = {
            "response_data": response_data,
            "status_code": status_code,
            "delay_ms": self.config.mock_delay_ms
        }
    
    def get_mock_response(self, method: str, url: str):
        """Get mock response"""
        key = f"{method.upper()}:{url}"
        return self.mocks.get(key)
    
    def log_request(self, method: str, url: str, headers: Dict, body: Any):
        """Log mock request"""
        self.request_log.append({
            "method": method,
            "url": url,
            "headers": headers,
            "body": body,
            "timestamp": datetime.utcnow().isoformat()
        })


class SecurityTester:
    """Security testing utilities"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.vulnerabilities = []
    
    async def test_sql_injection(self, client: ApiTestClient, endpoint: str, params: Dict[str, str]):
        """Test for SQL injection vulnerabilities"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' /*"
        ]
        
        vulnerabilities = []
        
        for param_name, param_value in params.items():
            for payload in sql_payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    response = await client.get(endpoint, params=test_params)
                    
                    # Check for SQL error messages
                    error_indicators = [
                        "SQL syntax error",
                        "mysql_fetch_array",
                        "ORA-01756",
                        "Microsoft OLE DB Provider",
                        "PostgreSQL query failed"
                    ]
                    
                    response_text = response.text.lower()
                    for indicator in error_indicators:
                        if indicator.lower() in response_text:
                            vulnerabilities.append({
                                "type": "SQL Injection",
                                "endpoint": endpoint,
                                "parameter": param_name,
                                "payload": payload,
                                "response": response.text[:500]
                            })
                            break
                            
                except Exception as e:
                    # Unexpected errors might indicate vulnerabilities
                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "endpoint": endpoint,
                        "parameter": param_name,
                        "payload": payload,
                        "error": str(e)
                    })
        
        return vulnerabilities
    
    async def test_xss(self, client: ApiTestClient, endpoint: str, params: Dict[str, str]):
        """Test for XSS vulnerabilities"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>"
        ]
        
        vulnerabilities = []
        
        for param_name, param_value in params.items():
            for payload in xss_payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    response = await client.get(endpoint, params=test_params)
                    
                    if payload in response.text:
                        vulnerabilities.append({
                            "type": "XSS",
                            "endpoint": endpoint,
                            "parameter": param_name,
                            "payload": payload,
                            "response": response.text[:500]
                        })
                        
                except Exception as e:
                    pass  # XSS tests shouldn't cause exceptions
        
        return vulnerabilities
    
    async def test_authentication_bypass(self, client: ApiTestClient, protected_endpoints: List[str]):
        """Test for authentication bypass"""
        vulnerabilities = []
        
        # Test without authentication
        for endpoint in protected_endpoints:
            try:
                # Remove auth headers
                headers = client.client.headers.copy()
                if "Authorization" in headers:
                    del headers["Authorization"]
                
                response = await client.get(endpoint, headers=headers)
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "Authentication Bypass",
                        "endpoint": endpoint,
                        "description": "Endpoint accessible without authentication"
                    })
                    
            except Exception as e:
                pass
        
        return vulnerabilities


class PerformanceTester:
    """Performance testing utilities"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.metrics = {}
    
    async def test_response_time(self, client: ApiTestClient, endpoint: str, num_requests: int = 10):
        """Test response time"""
        response_times = []
        
        for _ in range(num_requests):
            start_time = time.time()
            response = await client.get(endpoint)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            response_times.append(response_time_ms)
        
        metrics = {
            "endpoint": endpoint,
            "num_requests": num_requests,
            "avg_response_time_ms": statistics.mean(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "median_response_time_ms": statistics.median(response_times),
            "p95_response_time_ms": np.percentile(response_times, 95),
            "p99_response_time_ms": np.percentile(response_times, 99),
            "threshold_violations": len([t for t in response_times if t > self.config.performance_threshold_ms])
        }
        
        return metrics
    
    async def test_concurrent_requests(self, client: ApiTestClient, endpoint: str, concurrency: int = 10):
        """Test concurrent requests"""
        async def make_request():
            start_time = time.time()
            response = await client.get(endpoint)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time_ms": (end_time - start_time) * 1000
            }
        
        start_time = time.time()
        tasks = [make_request() for _ in range(concurrency)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = [r for r in results if isinstance(r, dict) and r["status_code"] == 200]
        failed_requests = len(results) - len(successful_requests)
        
        if successful_requests:
            response_times = [r["response_time_ms"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
        else:
            avg_response_time = 0
        
        metrics = {
            "endpoint": endpoint,
            "concurrency": concurrency,
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": failed_requests,
            "success_rate": len(successful_requests) / len(results) * 100,
            "total_time_s": total_time,
            "requests_per_second": len(results) / total_time,
            "avg_response_time_ms": avg_response_time
        }
        
        return metrics


class ContractTester:
    """Contract testing with Pact"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.pact = None
    
    def setup_consumer_pact(self, consumer_name: str, provider_name: str):
        """Setup consumer pact"""
        self.pact = Consumer(consumer_name).has_pact_with(Provider(provider_name))
        self.pact.start()
    
    def add_interaction(self, description: str, request: Dict, response: Dict):
        """Add pact interaction"""
        self.pact.given(description).upon_receiving(description).with_request(
            method=request.get("method", "GET"),
            path=request.get("path"),
            headers=request.get("headers", {}),
            body=request.get("body")
        ).will_respond_with(
            status=response.get("status", 200),
            headers=response.get("headers", {}),
            body=response.get("body")
        )
    
    def verify_pact(self):
        """Verify pact"""
        self.pact.stop()


class TestReporter:
    """Test reporting utilities"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results = []
    
    def add_result(self, test_name: str, status: str, duration: float, details: Dict = None):
        """Add test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.results.append(result)
    
    def generate_report(self, output_path: str):
        """Generate test report"""
        summary = {
            "total_tests": len(self.results),
            "passed": len([r for r in self.results if r["status"] == TestStatus.PASSED]),
            "failed": len([r for r in self.results if r["status"] == TestStatus.FAILED]),
            "skipped": len([r for r in self.results if r["status"] == TestStatus.SKIPPED]),
            "total_duration_ms": sum(r["duration_ms"] for r in self.results),
            "test_results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)


# Test fixtures and utilities
@pytest.fixture
async def test_config():
    """Test configuration fixture"""
    return TestConfig()


@pytest.fixture
async def test_database(test_config):
    """Test database fixture"""
    db = TestDatabase(test_config)
    await db.setup()
    yield db
    await db.cleanup()


@pytest.fixture
async def api_client(test_config):
    """API client fixture"""
    client = ApiTestClient(test_config)
    await client.setup()
    yield client
    await client.cleanup()


@pytest.fixture
def test_data_factory():
    """Test data factory fixture"""
    return TestDataFactory()


@pytest.fixture
def mock_server(test_config):
    """Mock server fixture"""
    return MockServer(test_config)


# Test classes and examples
class TestUserAPI:
    """User API test suite"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, api_client: ApiTestClient, test_data_factory: TestDataFactory):
        """Test successful user creation"""
        user_data = test_data_factory.user_data()
        
        response = await api_client.post("/api/users", json=user_data)
        
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["email"] == user_data["email"]
        assert "id" in response_data
        assert "password" not in response_data  # Sensitive data should not be returned
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, api_client: ApiTestClient, test_data_factory: TestDataFactory):
        """Test user creation with invalid email"""
        user_data = test_data_factory.user_data(email="invalid-email")
        
        response = await api_client.post("/api/users", json=user_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "email" in error_data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, api_client: ApiTestClient, test_data_factory: TestDataFactory):
        """Test get user by ID"""
        # Create user first
        user_data = test_data_factory.user_data()
        create_response = await api_client.post("/api/users", json=user_data)
        created_user = create_response.json()
        
        # Get user by ID
        response = await api_client.get(f"/api/users/{created_user['id']}")
        
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == created_user["id"]
        assert user["email"] == user_data["email"]
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, api_client: ApiTestClient, test_data_factory: TestDataFactory):
        """Test update user profile"""
        # Create and authenticate user
        user_data = test_data_factory.user_data()
        create_response = await api_client.post("/api/users", json=user_data)
        created_user = create_response.json()
        
        await api_client.authenticate(user_data["username"], "password123")
        
        # Update profile
        update_data = {"profile": {"bio": "Updated bio"}}
        response = await api_client.patch(f"/api/users/{created_user['id']}", json=update_data)
        
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["profile"]["bio"] == "Updated bio"
    
    @pytest.mark.asyncio
    async def test_delete_user(self, api_client: ApiTestClient, test_data_factory: TestDataFactory):
        """Test delete user"""
        # Create and authenticate user
        user_data = test_data_factory.user_data()
        create_response = await api_client.post("/api/users", json=user_data)
        created_user = create_response.json()
        
        await api_client.authenticate(user_data["username"], "password123")
        
        # Delete user
        response = await api_client.delete(f"/api/users/{created_user['id']}")
        
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = await api_client.get(f"/api/users/{created_user['id']}")
        assert get_response.status_code == 404


class TestSecurityAPI:
    """Security testing suite"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, api_client: ApiTestClient):
        """Test SQL injection protection"""
        security_tester = SecurityTester(TestConfig())
        
        vulnerabilities = await security_tester.test_sql_injection(
            api_client,
            "/api/users",
            {"search": "test"}
        )
        
        assert len(vulnerabilities) == 0, f"SQL injection vulnerabilities found: {vulnerabilities}"
    
    @pytest.mark.asyncio
    async def test_xss_protection(self, api_client: ApiTestClient):
        """Test XSS protection"""
        security_tester = SecurityTester(TestConfig())
        
        vulnerabilities = await security_tester.test_xss(
            api_client,
            "/api/content",
            {"title": "test"}
        )
        
        assert len(vulnerabilities) == 0, f"XSS vulnerabilities found: {vulnerabilities}"
    
    @pytest.mark.asyncio
    async def test_authentication_required(self, api_client: ApiTestClient):
        """Test authentication is required for protected endpoints"""
        protected_endpoints = [
            "/api/users/profile",
            "/api/content/create",
            "/api/payments/history"
        ]
        
        security_tester = SecurityTester(TestConfig())
        vulnerabilities = await security_tester.test_authentication_bypass(api_client, protected_endpoints)
        
        assert len(vulnerabilities) == 0, f"Authentication bypass vulnerabilities: {vulnerabilities}"


class TestPerformanceAPI:
    """Performance testing suite"""
    
    @pytest.mark.asyncio
    async def test_response_time_compliance(self, api_client: ApiTestClient):
        """Test API response time compliance"""
        performance_tester = PerformanceTester(TestConfig())
        
        metrics = await performance_tester.test_response_time(api_client, "/api/health", 20)
        
        assert metrics["avg_response_time_ms"] < 1000, f"Average response time too high: {metrics['avg_response_time_ms']}ms"
        assert metrics["p95_response_time_ms"] < 2000, f"95th percentile response time too high: {metrics['p95_response_time_ms']}ms"
    
    @pytest.mark.asyncio
    async def test_concurrent_load(self, api_client: ApiTestClient):
        """Test concurrent load handling"""
        performance_tester = PerformanceTester(TestConfig())
        
        metrics = await performance_tester.test_concurrent_requests(api_client, "/api/health", 50)
        
        assert metrics["success_rate"] >= 95, f"Success rate too low: {metrics['success_rate']}%"
        assert metrics["requests_per_second"] >= 10, f"Throughput too low: {metrics['requests_per_second']} req/s"


# Load testing with Locust
class APILoadTestUser(HttpUser):
    """Load test user for Locust"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup for load test user"""
        # Authenticate
        response = self.client.post("/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def get_users(self):
        """Get users list"""
        self.client.get("/api/users")
    
    @task(2)
    def get_content(self):
        """Get content list"""
        self.client.get("/api/content")
    
    @task(1)
    def create_content(self):
        """Create content"""
        content_data = {
            "title": "Load test content",
            "description": "Content created during load test",
            "type": "text"
        }
        self.client.post("/api/content", json=content_data)


# Contract testing example
class TestUserServiceContract:
    """Contract test for user service"""
    
    def setup_method(self):
        """Setup contract test"""
        self.contract_tester = ContractTester(TestConfig())
        self.contract_tester.setup_consumer_pact("frontend", "user-service")
    
    def test_get_user_contract(self):
        """Test get user contract"""
        self.contract_tester.add_interaction(
            "get user by ID",
            {
                "method": "GET",
                "path": "/api/users/123",
                "headers": {"Authorization": "Bearer token"}
            },
            {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "id": Like("123"),
                    "username": Like("testuser"),
                    "email": Like("test@example.com"),
                    "created_at": Term(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", "2023-01-01T00:00:00")
                }
            }
        )
        
        self.contract_tester.verify_pact()


# Test runner and CLI
async def run_test_suite(config: TestConfig):
    """Run complete test suite"""
    reporter = TestReporter(config)
    
    # Setup test environment
    test_db = TestDatabase(config)
    await test_db.setup()
    
    api_client = ApiTestClient(config)
    await api_client.setup()
    
    try:
        # Run different test categories
        test_suites = [
            ("Unit Tests", "pytest tests/unit/"),
            ("Integration Tests", "pytest tests/integration/"),
            ("API Tests", "pytest tests/api/"),
            ("Security Tests", "pytest tests/security/ -m security"),
            ("Performance Tests", "pytest tests/performance/ -m performance")
        ]
        
        for suite_name, command in test_suites:
            print(f"Running {suite_name}...")
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=config.test_timeout
                )
                
                duration = time.time() - start_time
                status = TestStatus.PASSED if result.returncode == 0 else TestStatus.FAILED
                
                reporter.add_result(
                    suite_name,
                    status,
                    duration,
                    {
                        "command": command,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
                )
                
                print(f"{suite_name}: {status} ({duration:.2f}s)")
                
            except subprocess.TimeoutExpired:
                reporter.add_result(
                    suite_name,
                    TestStatus.FAILED,
                    config.test_timeout,
                    {"error": "Test suite timed out"}
                )
                print(f"{suite_name}: TIMEOUT")
        
        # Generate report
        reporter.generate_report("test_results.json")
        
    finally:
        await api_client.cleanup()
        await test_db.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        config = TestConfig(**config_data)
    else:
        config = TestConfig()
    
    asyncio.run(run_test_suite(config))