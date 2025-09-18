#!/usr/bin/env python3
"""
📋 CONTRACT TEST TEMPLATE - API CONTRACT TESTING
================================================

Consumer-driven contract testing for microservices API compatibility
and backward compatibility verification.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import json
import jsonschema
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class APIContract:
    """API contract definition"""
    endpoint: str
    method: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    status_codes: List[int]

class ContractTestTemplate:
    """
    🚀 ENTERPRISE CONTRACT TEST TEMPLATE
    
    API contract validation and compatibility testing.
    """
    
    def __init__(self, service_name: str):
        """Initialize contract test template"""
        self.service_name = service_name
        self.contracts: List[APIContract] = []
    
    def add_contract(self, contract: APIContract):
        """Add API contract for testing"""
        self.contracts.append(contract)
    
    def validate_request(self, request_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate request against schema"""
        try:
            jsonschema.validate(request_data, schema)
            return True
        except jsonschema.ValidationError:
            return False
    
    def validate_response(self, response_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate response against schema"""
        try:
            jsonschema.validate(response_data, schema)
            return True
        except jsonschema.ValidationError:
            return False
    
    def generate_contract_tests(self) -> str:
        """Generate contract test code"""
        test_code = f'''
import pytest
import requests
import jsonschema

class TestAPI{self.service_name}Contracts:
    """Contract tests for {self.service_name} API"""
    
    BASE_URL = "http://localhost:8080"
'''
        
        for i, contract in enumerate(self.contracts):
            test_code += f'''
    def test_contract_{i}_{contract.method}_{contract.endpoint.replace("/", "_")}(self):
        """Test contract for {contract.method} {contract.endpoint}"""
        # Request validation
        sample_request = {{"example": "data"}}
        assert self.validate_request_schema(sample_request, {contract.request_schema})
        
        # Response validation
        response = requests.{contract.method.lower()}(
            f"{{self.BASE_URL}}{contract.endpoint}",
            json=sample_request
        )
        
        assert response.status_code in {contract.status_codes}
        assert self.validate_response_schema(response.json(), {contract.response_schema})
'''
        
        return test_code

# Factory function
def create_contract_test_template(service_name: str, **kwargs) -> ContractTestTemplate:
    """Create contract test template"""
    return ContractTestTemplate(service_name, **kwargs)