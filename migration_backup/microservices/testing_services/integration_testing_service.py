"""
Integration Testing Service for Ainflue Microservices
End-to-end testing and service integration validation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import httpx
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class TestStep:
    """Individual test step"""
    name: str
    service: str
    endpoint: str
    method: str = "GET"
    payload: Dict[str, Any] = None
    headers: Dict[str, str] = None
    expected_status: int = 200
    expected_response: Dict[str, Any] = None
    timeout: int = 30
    retry_count: int = 0


@dataclass 
class TestSuite:
    """Collection of integration tests"""
    name: str
    description: str
    steps: List[TestStep]
    setup_steps: List[TestStep] = None
    teardown_steps: List[TestStep] = None
    parallel: bool = False


@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    status: str  # passed, failed, error
    execution_time: float
    response_data: Any = None
    error_message: str = None
    step_results: List[Dict[str, Any]] = None


class IntegrationTestingService:
    """Enterprise integration testing service"""

    def __init__(self):
        self.test_suites = {}
        self.test_results = {}
        self.service_endpoints = {}
        self.global_headers = {}
        self.test_data = {}
        
    async def register_service_endpoint(self, service_name: str, base_url: str):
        """Register service endpoint for testing"""
        self.service_endpoints[service_name] = base_url
        logger.info(f"Registered service endpoint: {service_name} -> {base_url}")

    async def add_test_suite(self, test_suite: TestSuite):
        """Add test suite to the testing service"""
        self.test_suites[test_suite.name] = test_suite
        logger.info(f"Added test suite: {test_suite.name}")

    async def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            return {"error": f"Test suite {suite_name} not found"}
        
        suite = self.test_suites[suite_name]
        start_time = time.time()
        
        try:
            results = {
                "suite_name": suite_name,
                "description": suite.description,
                "started_at": datetime.utcnow().isoformat(),
                "setup_results": [],
                "test_results": [],
                "teardown_results": [],
                "summary": {
                    "total_tests": len(suite.steps),
                    "passed": 0,
                    "failed": 0,
                    "errors": 0
                }
            }
            
            # Run setup steps
            if suite.setup_steps:
                logger.info(f"Running setup for suite: {suite_name}")
                for step in suite.setup_steps:
                    result = await self._execute_test_step(step)
                    results["setup_results"].append(result.__dict__)
            
            # Run main tests
            if suite.parallel:
                # Run tests in parallel
                tasks = [self._execute_test_step(step) for step in suite.steps]
                test_results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Run tests sequentially
                test_results = []
                for step in suite.steps:
                    result = await self._execute_test_step(step)
                    test_results.append(result)
            
            # Process results
            for result in test_results:
                if isinstance(result, Exception):
                    test_result = TestResult(
                        test_name="unknown",
                        status="error",
                        execution_time=0,
                        error_message=str(result)
                    )
                else:
                    test_result = result
                
                results["test_results"].append(test_result.__dict__)
                
                # Update summary
                if test_result.status == "passed":
                    results["summary"]["passed"] += 1
                elif test_result.status == "failed":
                    results["summary"]["failed"] += 1
                else:
                    results["summary"]["errors"] += 1
            
            # Run teardown steps
            if suite.teardown_steps:
                logger.info(f"Running teardown for suite: {suite_name}")
                for step in suite.teardown_steps:
                    result = await self._execute_test_step(step)
                    results["teardown_results"].append(result.__dict__)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            results["execution_time"] = execution_time
            results["completed_at"] = datetime.utcnow().isoformat()
            
            # Store results
            self.test_results[suite_name] = results
            
            logger.info(
                f"Test suite {suite_name} completed: "
                f"{results['summary']['passed']} passed, "
                f"{results['summary']['failed']} failed, "
                f"{results['summary']['errors']} errors"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error running test suite {suite_name}: {str(e)}")
            return {
                "error": f"Failed to run test suite: {str(e)}",
                "suite_name": suite_name,
                "execution_time": time.time() - start_time
            }

    async def _execute_test_step(self, step: TestStep) -> TestResult:
        """Execute individual test step"""
        start_time = time.time()
        
        try:
            # Get service endpoint
            if step.service not in self.service_endpoints:
                return TestResult(
                    test_name=step.name,
                    status="error",
                    execution_time=time.time() - start_time,
                    error_message=f"Service endpoint not registered: {step.service}"
                )
            
            base_url = self.service_endpoints[step.service]
            url = f"{base_url.rstrip('/')}/{step.endpoint.lstrip('/')}"
            
            # Prepare headers
            headers = {**self.global_headers}
            if step.headers:
                headers.update(step.headers)
            
            # Make HTTP request
            async with httpx.AsyncClient(timeout=step.timeout) as client:
                if step.method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif step.method.upper() == "POST":
                    response = await client.post(url, json=step.payload, headers=headers)
                elif step.method.upper() == "PUT":
                    response = await client.put(url, json=step.payload, headers=headers)
                elif step.method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers)
                elif step.method.upper() == "PATCH":
                    response = await client.patch(url, json=step.payload, headers=headers)
                else:
                    return TestResult(
                        test_name=step.name,
                        status="error",
                        execution_time=time.time() - start_time,
                        error_message=f"Unsupported HTTP method: {step.method}"
                    )
            
            # Validate response
            status_valid = response.status_code == step.expected_status
            
            response_valid = True
            response_data = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            # Check expected response if provided
            if step.expected_response and isinstance(response_data, dict):
                response_valid = self._validate_response(response_data, step.expected_response)
            
            # Determine test result
            if status_valid and response_valid:
                status = "passed"
                error_message = None
            else:
                status = "failed"
                error_message = f"Status: expected {step.expected_status}, got {response.status_code}"
                if not response_valid:
                    error_message += f", Response validation failed"
            
            execution_time = time.time() - start_time
            
            result = TestResult(
                test_name=step.name,
                status=status,
                execution_time=execution_time,
                response_data=response_data,
                error_message=error_message
            )
            
            logger.debug(f"Test step {step.name}: {status} ({execution_time:.2f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing test step {step.name}: {str(e)}")
            
            return TestResult(
                test_name=step.name,
                status="error",
                execution_time=execution_time,
                error_message=str(e)
            )

    def _validate_response(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Validate response against expected structure"""
        try:
            for key, expected_value in expected.items():
                if key not in actual:
                    return False
                
                if isinstance(expected_value, dict) and isinstance(actual[key], dict):
                    if not self._validate_response(actual[key], expected_value):
                        return False
                elif expected_value != actual[key]:
                    return False
            
            return True
            
        except Exception:
            return False

    async def run_all_test_suites(self) -> Dict[str, Any]:
        """Run all registered test suites"""
        start_time = time.time()
        
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "suites": {},
            "summary": {
                "total_suites": len(self.test_suites),
                "passed_suites": 0,
                "failed_suites": 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_tests": 0
            }
        }
        
        for suite_name in self.test_suites:
            suite_result = await self.run_test_suite(suite_name)
            results["suites"][suite_name] = suite_result
            
            # Update summary
            if "summary" in suite_result:
                summary = suite_result["summary"]
                results["summary"]["total_tests"] += summary.get("total_tests", 0)
                results["summary"]["passed_tests"] += summary.get("passed", 0)
                results["summary"]["failed_tests"] += summary.get("failed", 0)
                results["summary"]["error_tests"] += summary.get("errors", 0)
                
                # Suite passed if no failures or errors
                if summary.get("failed", 0) == 0 and summary.get("errors", 0) == 0:
                    results["summary"]["passed_suites"] += 1
                else:
                    results["summary"]["failed_suites"] += 1
        
        results["execution_time"] = time.time() - start_time
        results["completed_at"] = datetime.utcnow().isoformat()
        
        return results

    async def get_test_results(self, suite_name: Optional[str] = None) -> Dict[str, Any]:
        """Get test results"""
        if suite_name:
            return self.test_results.get(suite_name, {})
        return self.test_results

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            return {
                "status": "healthy",
                "registered_services": len(self.service_endpoints),
                "test_suites": len(self.test_suites),
                "test_results": len(self.test_results),
                "services": list(self.service_endpoints.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Integration testing health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global integration testing service instance
integration_testing_service = IntegrationTestingService()


# Example test suites for Ainflue microservices
async def setup_ainflue_test_suites():
    """Setup standard Ainflue test suites"""
    
    # API Gateway Test Suite
    api_gateway_suite = TestSuite(
        name="api_gateway_integration",
        description="Test API Gateway functionality",
        steps=[
            TestStep(
                name="health_check",
                service="api_gateway",
                endpoint="/health",
                expected_status=200
            ),
            TestStep(
                name="authentication",
                service="api_gateway", 
                endpoint="/auth/token",
                method="POST",
                payload={"username": "test", "password": "test"},
                expected_status=200
            )
        ]
    )
    
    # AI Services Test Suite
    ai_services_suite = TestSuite(
        name="ai_services_integration",
        description="Test AI Services functionality",
        steps=[
            TestStep(
                name="ai_inference_health",
                service="ai_services",
                endpoint="/inference/health",
                expected_status=200
            ),
            TestStep(
                name="content_classification",
                service="ai_services",
                endpoint="/classification/analyze",
                method="POST",
                payload={"content": "test content", "type": "text"},
                expected_status=200
            )
        ]
    )
    
    # Content Services Test Suite
    content_services_suite = TestSuite(
        name="content_services_integration", 
        description="Test Content Services functionality",
        steps=[
            TestStep(
                name="upload_health",
                service="content_services",
                endpoint="/upload/health",
                expected_status=200
            ),
            TestStep(
                name="metadata_extraction",
                service="content_services",
                endpoint="/metadata/extract",
                method="POST",
                payload={"file_path": "/test/file.jpg"},
                expected_status=200
            )
        ]
    )
    
    # Add test suites
    await integration_testing_service.add_test_suite(api_gateway_suite)
    await integration_testing_service.add_test_suite(ai_services_suite)
    await integration_testing_service.add_test_suite(content_services_suite)


if __name__ == "__main__":
    async def test_integration_service():
        """Test integration testing service"""
        print("Testing Integration Testing Service...")
        
        # Register services
        await integration_testing_service.register_service_endpoint(
            "api_gateway", "http://localhost:8000"
        )
        await integration_testing_service.register_service_endpoint(
            "ai_services", "http://localhost:8001"
        )
        
        # Setup test suites
        await setup_ainflue_test_suites()
        
        # Health check
        health = await integration_testing_service.health_check()
        print(f"Health: {health}")
        
        print("Integration Testing Service ready!")
    
    asyncio.run(test_integration_service())