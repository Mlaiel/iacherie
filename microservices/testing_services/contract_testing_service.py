"""
Contract Testing Service - Enterprise API Contract Validation
Ainflue Platform - Microservices Architecture

© FAHED MLAIEL 2024-2025 - CONFIDENTIAL ENTERPRISE MODULE
"""

import asyncio
import aiohttp
import json
import jsonschema
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import yaml
from pathlib import Path

class ContractTestType(Enum):
    """Contract test types"""
    CONSUMER_DRIVEN = "consumer_driven"
    PROVIDER_DRIVEN = "provider_driven"
    SCHEMA_VALIDATION = "schema_validation"
    API_COMPATIBILITY = "api_compatibility"

class ContractStatus(Enum):
    """Contract validation status"""
    VALID = "valid"
    INVALID = "invalid"
    INCOMPATIBLE = "incompatible"
    SCHEMA_MISMATCH = "schema_mismatch"
    BREAKING_CHANGE = "breaking_change"

@dataclass
class ServiceContract:
    """Service contract definition"""
    service_name: str
    version: str
    endpoints: Dict[str, Dict]
    schemas: Dict[str, Dict]
    dependencies: List[str]
    provider_url: str
    contract_file: str

@dataclass
class ContractTest:
    """Contract test definition"""
    test_id: str
    consumer_service: str
    provider_service: str
    test_type: ContractTestType
    endpoint: str
    method: str
    request_schema: Dict
    response_schema: Dict
    test_data: List[Dict]
    expected_status_codes: List[int]

@dataclass
class ContractTestResult:
    """Contract test result"""
    test_id: str
    contract_test: ContractTest
    status: ContractStatus
    passed: bool
    failures: List[str]
    response_time: float
    executed_at: datetime
    details: Dict[str, Any]

class ContractTestingService:
    """
    Enterprise Contract Testing Service
    
    Provides comprehensive API contract validation and testing
    for microservices communication with schema validation,
    compatibility testing, and breaking change detection.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.contracts = {}
        self.test_results = {}
        self.schema_validator = None
        
    async def initialize(self) -> bool:
        """Initialize contract testing service"""
        try:
            self.logger.info("Initializing Contract Testing Service...")
            
            # Load service contracts
            await self._load_service_contracts()
            
            # Initialize schema validator
            self._init_schema_validator()
            
            # Setup contract monitoring
            await self._setup_contract_monitoring()
            
            self.logger.info("Contract Testing Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Contract Testing Service: {e}")
            return False
    
    async def _load_service_contracts(self):
        """Load service contracts from configuration"""
        # Default contracts for Ainflue services
        self.contracts = {
            "api_gateway": ServiceContract(
                service_name="api_gateway",
                version="1.0.0",
                endpoints={
                    "/api/v1/content/upload": {
                        "method": "POST",
                        "request_schema": "content_upload_request",
                        "response_schema": "content_upload_response"
                    },
                    "/api/v1/auth/login": {
                        "method": "POST",
                        "request_schema": "auth_login_request",
                        "response_schema": "auth_login_response"
                    },
                    "/api/v1/analytics/metrics": {
                        "method": "GET",
                        "request_schema": "analytics_request",
                        "response_schema": "analytics_response"
                    }
                },
                schemas={
                    "content_upload_request": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "content_type": {"type": "string"},
                            "metadata": {"type": "object"}
                        },
                        "required": ["file", "content_type"]
                    },
                    "content_upload_response": {
                        "type": "object",
                        "properties": {
                            "upload_id": {"type": "string"},
                            "status": {"type": "string"},
                            "url": {"type": "string"}
                        },
                        "required": ["upload_id", "status"]
                    }
                },
                dependencies=["content_services", "ai_services"],
                provider_url="http://localhost:8000",
                contract_file="api_gateway_contract.json"
            ),
            "ai_services": ServiceContract(
                service_name="ai_services",
                version="1.0.0",
                endpoints={
                    "/ai/v1/inference": {
                        "method": "POST",
                        "request_schema": "ai_inference_request",
                        "response_schema": "ai_inference_response"
                    },
                    "/ai/v1/training/start": {
                        "method": "POST",
                        "request_schema": "ai_training_request",
                        "response_schema": "ai_training_response"
                    },
                    "/ai/v1/models": {
                        "method": "GET",
                        "request_schema": "ai_models_request",
                        "response_schema": "ai_models_response"
                    }
                },
                schemas={
                    "ai_inference_request": {
                        "type": "object",
                        "properties": {
                            "model_id": {"type": "string"},
                            "input_data": {"type": "object"},
                            "parameters": {"type": "object"}
                        },
                        "required": ["model_id", "input_data"]
                    },
                    "ai_inference_response": {
                        "type": "object",
                        "properties": {
                            "prediction": {"type": "object"},
                            "confidence": {"type": "number"},
                            "processing_time": {"type": "number"}
                        },
                        "required": ["prediction", "confidence"]
                    }
                },
                dependencies=["data_services"],
                provider_url="http://localhost:8001",
                contract_file="ai_services_contract.json"
            ),
            "content_services": ServiceContract(
                service_name="content_services",
                version="1.0.0",
                endpoints={
                    "/content/v1/process": {
                        "method": "POST",
                        "request_schema": "content_process_request",
                        "response_schema": "content_process_response"
                    },
                    "/content/v1/optimize": {
                        "method": "POST",
                        "request_schema": "content_optimize_request",
                        "response_schema": "content_optimize_response"
                    }
                },
                schemas={
                    "content_process_request": {
                        "type": "object",
                        "properties": {
                            "content_id": {"type": "string"},
                            "operation": {"type": "string"},
                            "parameters": {"type": "object"}
                        },
                        "required": ["content_id", "operation"]
                    },
                    "content_process_response": {
                        "type": "object",
                        "properties": {
                            "result_id": {"type": "string"},
                            "status": {"type": "string"},
                            "output_url": {"type": "string"}
                        },
                        "required": ["result_id", "status"]
                    }
                },
                dependencies=["data_services"],
                provider_url="http://localhost:8002",
                contract_file="content_services_contract.json"
            )
        }
    
    def _init_schema_validator(self):
        """Initialize JSON schema validator"""
        self.schema_validator = jsonschema.Draft7Validator
        
    async def _setup_contract_monitoring(self):
        """Setup contract monitoring and validation"""
        self.contract_versions = {}
        self.breaking_changes = []
        
    async def run_contract_tests(self, consumer: str, provider: str) -> List[ContractTestResult]:
        """
        Run contract tests between consumer and provider services
        
        Args:
            consumer: Consumer service name
            provider: Provider service name
            
        Returns:
            List[ContractTestResult]: Contract test results
        """
        try:
            self.logger.info(f"Running contract tests: {consumer} -> {provider}")
            
            # Get contracts
            consumer_contract = self.contracts.get(consumer)
            provider_contract = self.contracts.get(provider)
            
            if not provider_contract:
                raise ValueError(f"Provider contract not found: {provider}")
            
            # Generate contract tests
            contract_tests = self._generate_contract_tests(consumer, provider_contract)
            
            # Execute tests
            results = []
            for test in contract_tests:
                result = await self._execute_contract_test(test)
                results.append(result)
                self.test_results[result.test_id] = result
            
            self.logger.info(f"Contract tests completed: {len(results)} tests executed")
            return results
            
        except Exception as e:
            self.logger.error(f"Contract testing failed: {e}")
            raise
    
    def _generate_contract_tests(self, consumer: str, provider_contract: ServiceContract) -> List[ContractTest]:
        """Generate contract tests for provider endpoints"""
        tests = []
        
        for endpoint, config in provider_contract.endpoints.items():
            test_id = f"contract_{consumer}_{provider_contract.service_name}_{endpoint.replace('/', '_')}"
            
            # Get schemas
            request_schema = provider_contract.schemas.get(config["request_schema"], {})
            response_schema = provider_contract.schemas.get(config["response_schema"], {})
            
            # Generate test data
            test_data = self._generate_test_data(request_schema)
            
            test = ContractTest(
                test_id=test_id,
                consumer_service=consumer,
                provider_service=provider_contract.service_name,
                test_type=ContractTestType.SCHEMA_VALIDATION,
                endpoint=endpoint,
                method=config["method"],
                request_schema=request_schema,
                response_schema=response_schema,
                test_data=[test_data],
                expected_status_codes=[200, 201, 202]
            )
            tests.append(test)
        
        return tests
    
    def _generate_test_data(self, schema: Dict) -> Dict:
        """Generate test data based on schema"""
        test_data = {}
        
        if schema.get("type") == "object" and "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                if prop_schema.get("type") == "string":
                    test_data[prop] = f"test_{prop}"
                elif prop_schema.get("type") == "number":
                    test_data[prop] = 123.45
                elif prop_schema.get("type") == "integer":
                    test_data[prop] = 123
                elif prop_schema.get("type") == "boolean":
                    test_data[prop] = True
                elif prop_schema.get("type") == "object":
                    test_data[prop] = {"test": "data"}
                elif prop_schema.get("type") == "array":
                    test_data[prop] = ["test", "array"]
        
        return test_data
    
    async def _execute_contract_test(self, test: ContractTest) -> ContractTestResult:
        """Execute individual contract test"""
        start_time = datetime.now()
        failures = []
        
        try:
            # Get provider contract
            provider_contract = self.contracts[test.provider_service]
            
            # Validate request schema
            for test_data in test.test_data:
                try:
                    validator = self.schema_validator(test.request_schema)
                    validator.validate(test_data)
                except jsonschema.ValidationError as e:
                    failures.append(f"Request schema validation failed: {e.message}")
            
            # Execute HTTP request
            async with aiohttp.ClientSession() as session:
                url = f"{provider_contract.provider_url}{test.endpoint}"
                
                for test_data in test.test_data:
                    request_start = datetime.now()
                    
                    try:
                        async with session.request(
                            test.method,
                            url,
                            json=test_data if test.method in ["POST", "PUT", "PATCH"] else None,
                            params=test_data if test.method == "GET" else None,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            
                            response_time = (datetime.now() - request_start).total_seconds()
                            
                            # Check status code
                            if response.status not in test.expected_status_codes:
                                failures.append(f"Unexpected status code: {response.status}")
                            
                            # Validate response schema
                            try:
                                response_data = await response.json()
                                validator = self.schema_validator(test.response_schema)
                                validator.validate(response_data)
                            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                                failures.append(f"Response schema validation failed: {str(e)}")
                            
                    except aiohttp.ClientError as e:
                        failures.append(f"HTTP request failed: {str(e)}")
                        response_time = 0
            
            # Determine status
            if failures:
                status = ContractStatus.INVALID
                passed = False
            else:
                status = ContractStatus.VALID
                passed = True
            
            return ContractTestResult(
                test_id=test.test_id,
                contract_test=test,
                status=status,
                passed=passed,
                failures=failures,
                response_time=response_time,
                executed_at=start_time,
                details={
                    "test_data_count": len(test.test_data),
                    "endpoint": test.endpoint,
                    "method": test.method
                }
            )
            
        except Exception as e:
            return ContractTestResult(
                test_id=test.test_id,
                contract_test=test,
                status=ContractStatus.INVALID,
                passed=False,
                failures=[f"Test execution failed: {str(e)}"],
                response_time=0,
                executed_at=start_time,
                details={"error": str(e)}
            )
    
    async def validate_contract_compatibility(self, service: str, new_version: str) -> Dict[str, Any]:
        """Validate contract compatibility for new service version"""
        try:
            current_contract = self.contracts.get(service)
            if not current_contract:
                raise ValueError(f"Service contract not found: {service}")
            
            # This would typically load the new contract from file
            # For demo, we'll simulate compatibility check
            compatibility_result = {
                "service": service,
                "current_version": current_contract.version,
                "new_version": new_version,
                "compatible": True,
                "breaking_changes": [],
                "new_endpoints": [],
                "deprecated_endpoints": [],
                "schema_changes": []
            }
            
            # Simulate breaking change detection
            if new_version.startswith("2."):
                compatibility_result["compatible"] = False
                compatibility_result["breaking_changes"] = [
                    "Removed required field 'legacy_id' from request schema",
                    "Changed response format for /api/v1/data endpoint"
                ]
            
            return compatibility_result
            
        except Exception as e:
            self.logger.error(f"Contract compatibility validation failed: {e}")
            raise
    
    async def run_consumer_driven_tests(self, consumer: str) -> List[ContractTestResult]:
        """Run consumer-driven contract tests"""
        results = []
        
        # Get consumer contract
        consumer_contract = self.contracts.get(consumer)
        if not consumer_contract:
            self.logger.warning(f"Consumer contract not found: {consumer}")
            return results
        
        # Test against all dependencies
        for provider in consumer_contract.dependencies:
            provider_results = await self.run_contract_tests(consumer, provider)
            results.extend(provider_results)
        
        return results
    
    async def generate_contract_report(self) -> Dict[str, Any]:
        """Generate comprehensive contract testing report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Group results by service
        service_results = {}
        for result in self.test_results.values():
            service = result.contract_test.provider_service
            if service not in service_results:
                service_results[service] = {"passed": 0, "failed": 0, "total": 0}
            
            service_results[service]["total"] += 1
            if result.passed:
                service_results[service]["passed"] += 1
            else:
                service_results[service]["failed"] += 1
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            "service_results": service_results,
            "contract_coverage": {
                "services_tested": len(service_results),
                "total_services": len(self.contracts),
                "coverage_percentage": f"{(len(service_results)/len(self.contracts)*100):.1f}%"
            },
            "failures": [
                {
                    "test_id": result.test_id,
                    "service": result.contract_test.provider_service,
                    "endpoint": result.contract_test.endpoint,
                    "failures": result.failures
                }
                for result in self.test_results.values() if not result.passed
            ],
            "recommendations": self._generate_contract_recommendations()
        }
        
        return report
    
    def _generate_contract_recommendations(self) -> List[str]:
        """Generate contract testing recommendations"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results.values() if not r.passed]
        
        if failed_tests:
            recommendations.append("Fix failing contract tests before deployment")
        
        if len(self.contracts) < 5:
            recommendations.append("Add more service contracts for better coverage")
        
        schema_failures = [r for r in failed_tests if any("schema" in f for f in r.failures)]
        if schema_failures:
            recommendations.append("Review and update API schemas")
        
        if not recommendations:
            recommendations.append("Contract testing is performing well")
        
        return recommendations
    
    def get_contract(self, service: str) -> Optional[ServiceContract]:
        """Get service contract"""
        return self.contracts.get(service)
    
    def get_test_results(self, test_id: Optional[str] = None) -> Dict[str, ContractTestResult]:
        """Get contract test results"""
        if test_id:
            return {test_id: self.test_results.get(test_id)}
        return self.test_results
    
    async def add_service_contract(self, contract: ServiceContract):
        """Add new service contract"""
        self.contracts[contract.service_name] = contract
        self.logger.info(f"Added contract for service: {contract.service_name}")
    
    async def update_service_contract(self, service: str, contract: ServiceContract):
        """Update existing service contract"""
        if service in self.contracts:
            # Check compatibility before update
            compatibility = await self.validate_contract_compatibility(service, contract.version)
            
            if compatibility["compatible"]:
                self.contracts[service] = contract
                self.logger.info(f"Updated contract for service: {service}")
            else:
                self.logger.warning(f"Contract update rejected due to breaking changes: {service}")
                raise ValueError(f"Breaking changes detected: {compatibility['breaking_changes']}")
        else:
            raise ValueError(f"Service contract not found: {service}")

# Service instance
contract_testing_service = ContractTestingService()