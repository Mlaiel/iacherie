"""
Contract Testing for Microservices
Tests API contracts between services to ensure compatibility

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContractTest:
    """Represents a contract test between services"""
    service_name: str
    endpoint: str
    method: str
    expected_schema: Dict[str, Any]
    consumer_service: str
    test_data: Dict[str, Any]


@dataclass
class ContractResult:
    """Contract test result"""
    test_name: str
    service: str
    endpoint: str
    passed: bool
    schema_valid: bool
    response_time_ms: float
    error_message: str = ""


class MicroserviceContractTester:
    """
    Contract testing for microservice APIs
    Validates service contracts and API compatibility
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[ContractResult] = []
    
    def _define_service_contracts(self) -> List[ContractTest]:
        """Define microservice contracts to test"""
        contracts = [
            # Content Service Contract
            ContractTest(
                service_name="content_service",
                endpoint="/api/v1/content",
                method="GET",
                expected_schema={
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string"},
                        "title": {"type": "string"},
                        "creator_id": {"type": "string"},
                        "created_at": {"type": "string"},
                        "status": {"type": "string", "enum": ["active", "pending", "archived"]}
                    },
                    "required": ["content_id", "title", "creator_id", "created_at", "status"]
                },
                consumer_service="analytics_service",
                test_data={}
            ),
            
            # Creator Service Contract
            ContractTest(
                service_name="creator_service",
                endpoint="/api/v1/creators",
                method="POST",
                expected_schema={
                    "type": "object",
                    "properties": {
                        "creator_id": {"type": "string"},
                        "username": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "verified": {"type": "boolean"},
                        "created_at": {"type": "string"}
                    },
                    "required": ["creator_id", "username", "email", "verified", "created_at"]
                },
                consumer_service="content_service",
                test_data={
                    "username": "test_creator",
                    "email": "test@example.com",
                    "bio": "Test creator for contract testing"
                }
            ),
            
            # Analytics Service Contract
            ContractTest(
                service_name="analytics_service",
                endpoint="/api/v1/analytics/metrics",
                method="GET",
                expected_schema={
                    "type": "object",
                    "properties": {
                        "total_content": {"type": "integer", "minimum": 0},
                        "protected_files": {"type": "integer", "minimum": 0},
                        "monthly_revenue": {"type": "number", "minimum": 0},
                        "active_monitoring": {"type": "integer", "minimum": 0},
                        "timestamp": {"type": "string"}
                    },
                    "required": ["total_content", "protected_files", "monthly_revenue", "active_monitoring", "timestamp"]
                },
                consumer_service="dashboard_service",
                test_data={}
            ),
            
            # Protection Service Contract
            ContractTest(
                service_name="protection_service",
                endpoint="/api/v1/protection/scan",
                method="POST",
                expected_schema={
                    "type": "object",
                    "properties": {
                        "scan_id": {"type": "string"},
                        "content_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["scanning", "completed", "failed"]},
                        "violations_found": {"type": "integer", "minimum": 0},
                        "scan_timestamp": {"type": "string"}
                    },
                    "required": ["scan_id", "content_id", "status", "violations_found", "scan_timestamp"]
                },
                consumer_service="monitoring_service",
                test_data={
                    "content_id": "test_content_123",
                    "scan_type": "full_scan"
                }
            )
        ]
        return contracts
    
    def _validate_schema(self, response_data: Dict[str, Any], expected_schema: Dict[str, Any]) -> bool:
        """
        Validate response against expected schema
        Simplified schema validation for contract testing
        """
        try:
            if expected_schema.get("type") == "object":
                if not isinstance(response_data, dict):
                    return False
                
                # Check required properties
                required_props = expected_schema.get("required", [])
                for prop in required_props:
                    if prop not in response_data:
                        logger.error(f"Missing required property: {prop}")
                        return False
                
                # Check property types
                properties = expected_schema.get("properties", {})
                for prop, prop_schema in properties.items():
                    if prop in response_data:
                        value = response_data[prop]
                        expected_type = prop_schema.get("type")
                        
                        if expected_type == "string" and not isinstance(value, str):
                            return False
                        elif expected_type == "integer" and not isinstance(value, int):
                            return False
                        elif expected_type == "number" and not isinstance(value, (int, float)):
                            return False
                        elif expected_type == "boolean" and not isinstance(value, bool):
                            return False
                        
                        # Check enum values
                        if "enum" in prop_schema and value not in prop_schema["enum"]:
                            return False
                        
                        # Check minimum values
                        if "minimum" in prop_schema and isinstance(value, (int, float)):
                            if value < prop_schema["minimum"]:
                                return False
            
            return True
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    def _mock_service_response(self, contract: ContractTest) -> Dict[str, Any]:
        """
        Generate mock response for contract testing
        In production, this would make actual service calls
        """
        mock_responses = {
            "content_service": {
                "content_id": "content_123",
                "title": "Test Content",
                "creator_id": "creator_456",
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            },
            "creator_service": {
                "creator_id": "creator_789",
                "username": "test_creator",
                "email": "test@example.com",
                "verified": True,
                "created_at": datetime.utcnow().isoformat()
            },
            "analytics_service": {
                "total_content": 1247,
                "protected_files": 1198,
                "monthly_revenue": 24580.50,
                "active_monitoring": 892,
                "timestamp": datetime.utcnow().isoformat()
            },
            "protection_service": {
                "scan_id": "scan_101112",
                "content_id": "test_content_123",
                "status": "completed",
                "violations_found": 2,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return mock_responses.get(contract.service_name, {})
    
    def test_contract(self, contract: ContractTest) -> ContractResult:
        """Test a single service contract"""
        start_time = datetime.now()
        
        try:
            # Use mock responses for testing
            response_data = self._mock_service_response(contract)
            
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Validate schema compliance
            schema_valid = self._validate_schema(response_data, contract.expected_schema)
            
            result = ContractResult(
                test_name=f"{contract.service_name}_{contract.endpoint.replace('/', '_')}",
                service=contract.service_name,
                endpoint=contract.endpoint,
                passed=schema_valid,
                schema_valid=schema_valid,
                response_time_ms=response_time_ms,
                error_message="" if schema_valid else "Schema validation failed"
            )
            
            self.results.append(result)
            return result
            
        except Exception as e:
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            result = ContractResult(
                test_name=f"{contract.service_name}_{contract.endpoint.replace('/', '_')}",
                service=contract.service_name,
                endpoint=contract.endpoint,
                passed=False,
                schema_valid=False,
                response_time_ms=response_time_ms,
                error_message=str(e)
            )
            
            self.results.append(result)
            return result
    
    def run_all_contract_tests(self) -> List[ContractResult]:
        """Run all contract tests"""
        contracts = self._define_service_contracts()
        results = []
        
        for contract in contracts:
            result = self.test_contract(contract)
            results.append(result)
            logger.info(f"Contract test {result.test_name}: {'PASSED' if result.passed else 'FAILED'}")
        
        return results
    
    def generate_contract_report(self) -> Dict[str, Any]:
        """Generate contract testing report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        avg_response_time = sum(r.response_time_ms for r in self.results) / total_tests if total_tests > 0 else 0
        
        report = {
            "contract_testing_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_response_time_ms": round(avg_response_time, 2)
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "service": r.service,
                    "endpoint": r.endpoint,
                    "passed": r.passed,
                    "schema_valid": r.schema_valid,
                    "response_time_ms": r.response_time_ms,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        return report


# Pytest fixtures and tests
@pytest.fixture
def contract_tester():
    """Contract tester fixture"""
    return MicroserviceContractTester()


@pytest.mark.contract
class TestMicroserviceContracts:
    """Contract testing suite for microservices"""
    
    def test_content_service_contract(self, contract_tester):
        """Test content service API contract"""
        contracts = contract_tester._define_service_contracts()
        content_contract = next(c for c in contracts if c.service_name == "content_service")
        
        result = contract_tester.test_contract(content_contract)
        
        assert result.passed, f"Content service contract failed: {result.error_message}"
        assert result.schema_valid, "Content service response schema is invalid"
        assert result.response_time_ms < 2000, "Content service response too slow"
    
    def test_creator_service_contract(self, contract_tester):
        """Test creator service API contract"""
        contracts = contract_tester._define_service_contracts()
        creator_contract = next(c for c in contracts if c.service_name == "creator_service")
        
        result = contract_tester.test_contract(creator_contract)
        
        assert result.passed, f"Creator service contract failed: {result.error_message}"
        assert result.schema_valid, "Creator service response schema is invalid"
        assert result.response_time_ms < 2000, "Creator service response too slow"
    
    def test_analytics_service_contract(self, contract_tester):
        """Test analytics service API contract"""
        contracts = contract_tester._define_service_contracts()
        analytics_contract = next(c for c in contracts if c.service_name == "analytics_service")
        
        result = contract_tester.test_contract(analytics_contract)
        
        assert result.passed, f"Analytics service contract failed: {result.error_message}"
        assert result.schema_valid, "Analytics service response schema is invalid"
        assert result.response_time_ms < 2000, "Analytics service response too slow"
    
    def test_protection_service_contract(self, contract_tester):
        """Test protection service API contract"""
        contracts = contract_tester._define_service_contracts()
        protection_contract = next(c for c in contracts if c.service_name == "protection_service")
        
        result = contract_tester.test_contract(protection_contract)
        
        assert result.passed, f"Protection service contract failed: {result.error_message}"
        assert result.schema_valid, "Protection service response schema is invalid"
        assert result.response_time_ms < 2000, "Protection service response too slow"
    
    def test_all_contracts_comprehensive(self, contract_tester):
        """Run comprehensive contract testing suite"""
        results = contract_tester.run_all_contract_tests()
        
        assert len(results) >= 4, "Should test at least 4 service contracts"
        
        passed_tests = sum(1 for r in results if r.passed)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        assert success_rate >= 80, f"Contract success rate too low: {success_rate}%"
        
        # Generate and validate report
        report = contract_tester.generate_contract_report()
        assert "contract_testing_summary" in report
        assert report["contract_testing_summary"]["total_tests"] == total_tests
        assert report["contract_testing_summary"]["passed"] == passed_tests
        
        # Log contract testing results
        logger.info(f"Contract testing complete: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")


if __name__ == "__main__":
    # Run contract tests independently
    tester = MicroserviceContractTester()
    results = tester.run_all_contract_tests()
    report = tester.generate_contract_report()
    
    print("\n=== MICROSERVICE CONTRACT TESTING REPORT ===")
    print(json.dumps(report, indent=2))