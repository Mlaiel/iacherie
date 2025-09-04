"""Testing - API Testing Utilities
Consolidated testing functionality for API validation and quality assurance.

This module consolidates testing from:
- Unit tests for API endpoints
- Integration tests for end-to-end workflows
- Load testing and performance validation
- Mock data generation for testing
- Test fixtures and utilities
- API contract testing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import json
import uuid
import random
import string
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from httpx import AsyncClient
import faker
from unittest.mock import Mock, patch

# ========================================
# TESTING ENUMS
# ========================================

class TestDataType(str, Enum):
    """Types of test data"""
    USER = "user"
    CONTENT = "content"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    ALERT = "alert"

class TestScenario(str, Enum):
    """Test scenario types"""
    HAPPY_PATH = "happy_path"
    ERROR_HANDLING = "error_handling"
    EDGE_CASES = "edge_cases"
    SECURITY = "security"
    PERFORMANCE = "performance"

# ========================================
# TEST DATA GENERATORS
# ========================================

class TestDataGenerator:
    """Generate realistic test data for API testing"""
    
    def __init__(self):
        self.faker = faker.Faker()
        self.faker.add_provider(faker.providers.internet)
        self.faker.add_provider(faker.providers.person)
        self.faker.add_provider(faker.providers.company)
        
    def generate_user_data(self, **overrides) -> Dict[str, Any]:
        """Generate realistic user test data"""
        creator_types = ["musician", "blogger", "photographer", "influencer", "comedian", "writer"]
        
        data = {
            "id": str(uuid.uuid4()),
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "creator_type": random.choice(creator_types),
            "bio": self.faker.text(max_nb_chars=200),
            "website": self.faker.url(),
            "avatar_url": self.faker.image_url(),
            "verification_status": random.choice(["unverified", "pending", "verified"]),
            "subscription_tier": random.choice(["free", "basic", "premium", "enterprise"]),
            "created_at": self.faker.date_time_between(start_date="-2y", end_date="now").isoformat(),
            "last_active": self.faker.date_time_between(start_date="-1d", end_date="now").isoformat()
        }
        
        data.update(overrides)
        return data
    
    def generate_content_data(self, **overrides) -> Dict[str, Any]:
        """Generate realistic content test data"""
        content_types = ["audio", "video", "image", "text", "document"]
        
        data = {
            "id": str(uuid.uuid4()),
            "title": self.faker.sentence(nb_words=4)[:-1],  # Remove trailing period
            "description": self.faker.text(max_nb_chars=500),
            "content_type": random.choice(content_types),
            "file_size": random.randint(100000, 50000000),  # 100KB to 50MB
            "mime_type": self._get_mime_type_for_content_type(overrides.get("content_type", random.choice(content_types))),
            "duration": random.randint(30, 3600) if overrides.get("content_type") in ["audio", "video"] else None,
            "dimensions": f"{random.randint(720, 4096)}x{random.randint(480, 2160)}" if overrides.get("content_type") in ["image", "video"] else None,
            "creator_id": str(uuid.uuid4()),
            "tags": [self.faker.word() for _ in range(random.randint(1, 5))],
            "is_public": random.choice([True, False]),
            "view_count": random.randint(0, 100000),
            "like_count": random.randint(0, 10000),
            "created_at": self.faker.date_time_between(start_date="-1y", end_date="now").isoformat(),
            "updated_at": self.faker.date_time_between(start_date="-30d", end_date="now").isoformat()
        }
        
        data.update(overrides)
        return data
    
    def generate_collaboration_data(self, **overrides) -> Dict[str, Any]:
        """Generate realistic collaboration test data"""
        statuses = ["draft", "active", "completed", "cancelled"]
        
        data = {
            "id": str(uuid.uuid4()),
            "title": f"Collaboration: {self.faker.sentence(nb_words=3)[:-1]}",
            "description": self.faker.text(max_nb_chars=1000),
            "status": random.choice(statuses),
            "creator_id": str(uuid.uuid4()),
            "budget": round(random.uniform(100, 5000), 2),
            "deadline": (datetime.now() + timedelta(days=random.randint(7, 90))).isoformat(),
            "requirements": [self.faker.sentence(nb_words=5)[:-1] for _ in range(random.randint(2, 5))],
            "created_at": self.faker.date_time_between(start_date="-3m", end_date="now").isoformat(),
            "updated_at": self.faker.date_time_between(start_date="-7d", end_date="now").isoformat()
        }
        
        data.update(overrides)
        return data
    
    def generate_analytics_data(self, content_id: str = None, **overrides) -> Dict[str, Any]:
        """Generate realistic analytics test data"""
        base_views = random.randint(100, 50000)
        
        data = {
            "content_id": content_id or str(uuid.uuid4()),
            "views": base_views,
            "likes": int(base_views * random.uniform(0.05, 0.25)),
            "shares": int(base_views * random.uniform(0.01, 0.10)),
            "comments": int(base_views * random.uniform(0.005, 0.05)),
            "engagement_rate": round(random.uniform(2.0, 25.0), 2),
            "reach": int(base_views * random.uniform(1.2, 3.0)),
            "impressions": int(base_views * random.uniform(2.0, 10.0)),
            "revenue": round(random.uniform(0, base_views * 0.01), 2),
            "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
            "period_end": datetime.now().isoformat()
        }
        
        data.update(overrides)
        return data
    
    def generate_payment_data(self, **overrides) -> Dict[str, Any]:
        """Generate realistic payment test data"""
        payment_methods = ["stripe_card", "stripe_bank", "paypal", "wise_transfer", "crypto"]
        currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
        statuses = ["pending", "processing", "completed", "failed", "refunded"]
        
        data = {
            "id": str(uuid.uuid4()),
            "amount": round(random.uniform(10, 1000), 2),
            "currency": random.choice(currencies),
            "payment_method": random.choice(payment_methods),
            "status": random.choice(statuses),
            "description": f"Payment for {self.faker.sentence(nb_words=3)[:-1]}",
            "user_id": str(uuid.uuid4()),
            "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
            "created_at": self.faker.date_time_between(start_date="-1m", end_date="now").isoformat(),
            "updated_at": self.faker.date_time_between(start_date="-1d", end_date="now").isoformat()
        }
        
        data.update(overrides)
        return data
    
    def _get_mime_type_for_content_type(self, content_type: str) -> str:
        """Get appropriate MIME type for content type"""
        mime_types = {
            "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/aac"],
            "video": ["video/mp4", "video/mpeg", "video/quicktime", "video/webm"],
            "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
            "text": ["text/plain", "text/markdown", "text/html"],
            "document": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        }
        
        return random.choice(mime_types.get(content_type, ["application/octet-stream"]))
    
    def generate_bulk_data(self, data_type: TestDataType, count: int = 10, **overrides) -> List[Dict[str, Any]]:
        """Generate bulk test data"""
        generators = {
            TestDataType.USER: self.generate_user_data,
            TestDataType.CONTENT: self.generate_content_data,
            TestDataType.COLLABORATION: self.generate_collaboration_data,
            TestDataType.ANALYTICS: self.generate_analytics_data,
            TestDataType.PAYMENT: self.generate_payment_data
        }
        
        generator = generators.get(data_type)
        if not generator:
            raise ValueError(f"No generator for data type: {data_type}")
        
        return [generator(**overrides) for _ in range(count)]

# ========================================
# TEST FIXTURES
# ========================================

class TestFixtures:
    """Common test fixtures and setup utilities"""
    
    def __init__(self):
        self.data_generator = TestDataGenerator()
        self._mock_database = {}
        self._mock_redis = {}
    
    def create_test_user(self, **overrides) -> Dict[str, Any]:
        """Create a test user with authentication token"""
        user_data = self.data_generator.generate_user_data(**overrides)
        
        # Generate JWT token (mock)
        token = f"test_token_{uuid.uuid4().hex[:16]}"
        
        return {
            "user": user_data,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        }
    
    def create_test_content(self, creator_id: str = None, **overrides) -> Dict[str, Any]:
        """Create test content"""
        if not creator_id:
            creator_id = str(uuid.uuid4())
        
        return self.data_generator.generate_content_data(creator_id=creator_id, **overrides)
    
    def mock_external_services(self):
        """Setup mocks for external services"""
        # Mock Redis
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.set.return_value = True
        redis_mock.delete.return_value = 1
        
        # Mock email service
        email_mock = Mock()
        email_mock.send_email.return_value = {"message_id": "test_message_id"}
        
        # Mock payment service
        payment_mock = Mock()
        payment_mock.process_payment.return_value = {
            "status": "completed",
            "transaction_id": f"txn_{uuid.uuid4().hex[:16]}"
        }
        
        return {
            "redis": redis_mock,
            "email": email_mock,
            "payment": payment_mock
        }

# ========================================
# API TEST CLIENT
# ========================================

class APITestClient:
    """Enhanced test client for API testing"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.client = TestClient(app)
        self.fixtures = TestFixtures()
        self.async_client = None
    
    async def get_async_client(self) -> AsyncClient:
        """Get async test client"""
        if not self.async_client:
            self.async_client = AsyncClient(app=self.app, base_url="http://test")
        return self.async_client
    
    def authenticate_user(self, user_data: Dict[str, Any] = None) -> Dict[str, str]:
        """Authenticate a test user and return headers"""
        if not user_data:
            user_data = self.fixtures.create_test_user()
        
        return user_data["headers"]
    
    def test_endpoint(
        self, 
        method: str, 
        path: str, 
        expected_status: int = 200,
        auth_required: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Test an API endpoint with standard assertions"""
        
        if auth_required and "headers" not in kwargs:
            kwargs["headers"] = self.authenticate_user()
        
        response = getattr(self.client, method.lower())(path, **kwargs)
        
        # Standard assertions
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            if data.get("success"):
                assert "data" in data or "message" in data
        
        return response.json() if response.content else {}

# ========================================
# PERFORMANCE TESTING
# ========================================

class PerformanceTestRunner:
    """Performance testing utilities"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.client = APITestClient(app)
    
    async def load_test_endpoint(
        self, 
        method: str, 
        path: str, 
        concurrent_users: int = 10,
        requests_per_user: int = 100,
        **request_kwargs
    ) -> Dict[str, Any]:
        """Run load test on an endpoint"""
        
        async def make_request(session: AsyncClient):
            """Make a single request"""
            start_time = datetime.now()
            try:
                response = await getattr(session, method.lower())(path, **request_kwargs)
                end_time = datetime.now()
                return {
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time).total_seconds(),
                    "success": response.status_code < 400
                }
            except Exception as e:
                end_time = datetime.now()
                return {
                    "status_code": 0,
                    "response_time": (end_time - start_time).total_seconds(),
                    "success": False,
                    "error": str(e)
                }
        
        async def user_session(user_id: int):
            """Simulate a user session"""
            async with AsyncClient(app=self.app, base_url="http://test") as session:
                results = []
                for _ in range(requests_per_user):
                    result = await make_request(session)
                    results.append(result)
                    await asyncio.sleep(0.1)  # Small delay between requests
                return results
        
        # Run concurrent user sessions
        start_time = datetime.now()
        tasks = [user_session(i) for i in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # Flatten results
        results = [result for user_results in all_results for result in user_results]
        
        # Calculate statistics
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in results]
        
        return {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(results) - len(successful_requests),
            "success_rate": len(successful_requests) / len(results) * 100,
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "total_duration": (end_time - start_time).total_seconds(),
            "requests_per_second": len(results) / (end_time - start_time).total_seconds()
        }

# ========================================
# CONTRACT TESTING
# ========================================

class APIContractTester:
    """API contract testing utilities"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.client = APITestClient(app)
    
    def validate_response_schema(self, response: Dict[str, Any], expected_schema: Dict[str, Any]) -> List[str]:
        """Validate response against expected schema"""
        errors = []
        
        def validate_field(data, schema, path=""):
            if isinstance(schema, dict):
                if "type" in schema:
                    expected_type = schema["type"]
                    if expected_type == "string" and not isinstance(data, str):
                        errors.append(f"{path}: expected string, got {type(data).__name__}")
                    elif expected_type == "integer" and not isinstance(data, int):
                        errors.append(f"{path}: expected integer, got {type(data).__name__}")
                    elif expected_type == "number" and not isinstance(data, (int, float)):
                        errors.append(f"{path}: expected number, got {type(data).__name__}")
                    elif expected_type == "boolean" and not isinstance(data, bool):
                        errors.append(f"{path}: expected boolean, got {type(data).__name__}")
                    elif expected_type == "array" and not isinstance(data, list):
                        errors.append(f"{path}: expected array, got {type(data).__name__}")
                    elif expected_type == "object" and not isinstance(data, dict):
                        errors.append(f"{path}: expected object, got {type(data).__name__}")
                
                if "properties" in schema and isinstance(data, dict):
                    for prop, prop_schema in schema["properties"].items():
                        if prop in data:
                            validate_field(data[prop], prop_schema, f"{path}.{prop}")
                        elif schema.get("required", []) and prop in schema["required"]:
                            errors.append(f"{path}.{prop}: required field missing")
        
        validate_field(response, expected_schema)
        return errors
    
    def test_endpoint_contract(self, method: str, path: str, expected_schema: Dict[str, Any]) -> bool:
        """Test endpoint against contract"""
        response_data = self.client.test_endpoint(method, path)
        errors = self.validate_response_schema(response_data, expected_schema)
        
        if errors:
            print(f"Contract validation errors for {method.upper()} {path}:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True

# ========================================
# TEST SUITES
# ========================================

class APITestSuite:
    """Complete API test suite"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.client = APITestClient(app)
        self.performance_runner = PerformanceTestRunner(app)
        self.contract_tester = APIContractTester(app)
        self.fixtures = TestFixtures()
    
    def run_smoke_tests(self) -> Dict[str, bool]:
        """Run basic smoke tests"""
        results = {}
        
        # Test health endpoint
        try:
            response = self.client.test_endpoint("GET", "/health", auth_required=False)
            results["health_check"] = True
        except Exception as e:
            results["health_check"] = False
            print(f"Health check failed: {e}")
        
        # Test authentication
        try:
            user = self.fixtures.create_test_user()
            self.client.test_endpoint("GET", "/api/v1/auth/me", headers=user["headers"])
            results["authentication"] = True
        except Exception as e:
            results["authentication"] = False
            print(f"Authentication test failed: {e}")
        
        return results
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        results = {
            "smoke_tests": self.run_smoke_tests(),
            "endpoint_tests": {},
            "performance_tests": {},
            "contract_tests": {}
        }
        
        # Define endpoints to test
        endpoints = [
            ("GET", "/api/v1/content"),
            ("POST", "/api/v1/content"),
            ("GET", "/api/v1/collaborations"),
            ("POST", "/api/v1/collaborations"),
            ("GET", "/api/v1/analytics/dashboard")
        ]
        
        # Test each endpoint
        for method, path in endpoints:
            try:
                self.client.test_endpoint(method, path)
                results["endpoint_tests"][f"{method} {path}"] = True
            except Exception as e:
                results["endpoint_tests"][f"{method} {path}"] = False
                print(f"Endpoint test failed for {method} {path}: {e}")
        
        return results

# ========================================
# EXPORTS
# ========================================

__all__ = [
    "TestDataType",
    "TestScenario",
    "TestDataGenerator",
    "TestFixtures",
    "APITestClient",
    "PerformanceTestRunner",
    "APIContractTester",
    "APITestSuite"
]