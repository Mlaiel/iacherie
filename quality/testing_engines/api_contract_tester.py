"""
Api Contract Tester module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
API Contract Testing Module - Ainflue Quality Platform
=====================================================

Enterprise-grade API contract testing system for microservices validation.
Demonstrates Backend Senior + DBA + Microservices architect expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import aiohttp
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import jsonschema
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContractTestResult:
    """Contract test execution result."""
    contract_name: str
    endpoint: str
    method: str
    status: str  # 'passed', 'failed', 'error'
    execution_time_ms: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    response_data: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class APIContract:
    """API contract definition."""
    name: str
    version: str
    service: str
    endpoints: List[Dict[str, Any]]
    schemas: Dict[str, Any]
    security_requirements: List[str] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)


class ContractValidator:
    """Validates API responses against contract schemas."""
    
    def __init__(self) -> None:
        self.schema_cache = {}
    
    def validate_response_schema(self, response_data: Dict, schema: Dict) -> List[str]:
        """Validate response against JSON schema."""
        errors = []
        try:
            jsonschema.validate(instance=response_data, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        return errors
    
    def validate_headers(self, headers: Dict[str, str], required_headers: List[str]) -> List[str]:
        """Validate required headers are present."""
        errors = []
        for header in required_headers:
            if header.lower() not in [h.lower() for h in headers.keys()]:
                errors.append(f"Missing required header: {header}")
        return errors
    
    def validate_status_code(self, actual: int, expected: Union[int, List[int]]) -> List[str]:
        """Validate HTTP status code."""
        errors = []
        if isinstance(expected, int):
            expected = [expected]
        
        if actual not in expected:
            errors.append(f"Unexpected status code: {actual}, expected one of: {expected}")
        return errors


class APIContractTester:
    """
    Enterprise API Contract Testing Engine
    ====================================
    
    Comprehensive contract testing for microservices architecture.
    Demonstrates Backend Senior + Microservices + DBA expertise.
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config = self._load_config(config_path)
        self.validator = ContractValidator()
        self.test_results: List[ContractTestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Enterprise features
        self.rate_limiter = {}
        self.circuit_breaker = {}
        self.test_metrics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'average_response_time': 0.0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load testing configuration."""
        default_config = {
            'timeout': 30,
            'max_retries': 3,
            'parallel_tests': 10,
            'base_urls': {},
            'auth_tokens': {},
            'circuit_breaker': {
                'failure_threshold': 5,
                'reset_timeout': 60
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def load_contracts(self, contracts_dir: str) -> List[APIContract]:
        """Load API contracts from directory."""
        contracts = []
        contracts_path = Path(contracts_dir)
        
        if not contracts_path.exists():
            logger.warning(f"Contracts directory not found: {contracts_dir}")
            return contracts
        
        for contract_file in contracts_path.glob("*.yaml"):
            try:
                with open(contract_file, 'r') as f:
                    contract_data = yaml.safe_load(f)
                    
                contract = APIContract(
                    name=contract_data.get('name', contract_file.stem),
                    version=contract_data.get('version', '1.0'),
                    service=contract_data.get('service', 'unknown'),
                    endpoints=contract_data.get('endpoints', []),
                    schemas=contract_data.get('schemas', {}),
                    security_requirements=contract_data.get('security_requirements', []),
                    rate_limits=contract_data.get('rate_limits', {})
                )
                contracts.append(contract)
                logger.info(f"Loaded contract: {contract.name} v{contract.version}")
                
            except Exception as e:
                logger.error(f"Failed to load contract {contract_file}: {e}")
        
        return contracts
    
    async def test_endpoint(self, contract: APIContract, endpoint: Dict[str, Any]) -> ContractTestResult:
        """Test a single endpoint against its contract."""
        start_time = datetime.now()
        
        result = ContractTestResult(
            contract_name=contract.name,
            endpoint=endpoint.get('path', ''),
            method=endpoint.get('method', 'GET').upper(),
            status='error',
            execution_time_ms=0.0
        )
        
        try:
            # Build request URL
            base_url = self.config['base_urls'].get(contract.service, 'http://localhost:8000')
            url = f"{base_url.rstrip('/')}{endpoint['path']}"
            
            # Prepare request parameters
            method = endpoint.get('method', 'GET').upper()
            headers = endpoint.get('headers', {})
            params = endpoint.get('parameters', {})
            body = endpoint.get('body', None)
            
            # Add authentication if required
            if 'authorization' in contract.security_requirements:
                auth_token = self.config['auth_tokens'].get(contract.service)
                if auth_token:
                    headers['Authorization'] = f"Bearer {auth_token}"
            
            # Make request
            timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
            
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=body if body else None
            ) as response:
                response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                result.response_data = response_data if isinstance(response_data, dict) else {'body': response_data}
                
                # Validate contract compliance
                errors = []
                
                # Status code validation
                expected_status = endpoint.get('expected_status', [200])
                errors.extend(self.validator.validate_status_code(response.status, expected_status))
                
                # Header validation
                required_headers = endpoint.get('required_headers', [])
                errors.extend(self.validator.validate_headers(dict(response.headers), required_headers))
                
                # Schema validation
                response_schema = endpoint.get('response_schema')
                if response_schema and isinstance(response_data, dict):
                    schema = contract.schemas.get(response_schema, response_schema)
                    errors.extend(self.validator.validate_response_schema(response_data, schema))
                
                result.errors = errors
                result.status = 'passed' if not errors else 'failed'
                
        except aiohttp.ClientError as e:
            result.errors.append(f"HTTP client error: {str(e)}")
            result.status = 'error'
            
        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")
            result.status = 'error'
        
        # Calculate execution time
        end_time = datetime.now()
        result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    async def run_contract_tests(self, contracts: List[APIContract]) -> Dict[str, Any]:
        """Run all contract tests."""
        logger.info(f"Starting contract tests for {len(contracts)} contracts")
        
        all_results = []
        
        for contract in contracts:
            logger.info(f"Testing contract: {contract.name}")
            
            # Test each endpoint
            tasks = []
            for endpoint in contract.endpoints:
                task = self.test_endpoint(contract, endpoint)
                tasks.append(task)
            
            # Execute tests with concurrency control
            semaphore = asyncio.Semaphore(self.config['parallel_tests'])
            
            async def bounded_test(task) -> None:
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[bounded_test(task) for task in tasks])
            all_results.extend(results)
        
        self.test_results = all_results
        
        # Update metrics
        self._update_metrics()
        
        # Generate report
        return self._generate_report()
    
    def _update_metrics(self) -> None:
        """Update test execution metrics."""
        if not self.test_results:
            return
        
        self.test_metrics['total_tests'] = len(self.test_results)
        self.test_metrics['passed_tests'] = len([r for r in self.test_results if r.status == 'passed'])
        self.test_metrics['failed_tests'] = len([r for r in self.test_results if r.status == 'failed'])
        self.test_metrics['error_tests'] = len([r for r in self.test_results if r.status == 'error'])
        
        total_time = sum(r.execution_time_ms for r in self.test_results)
        self.test_metrics['average_response_time'] = total_time / len(self.test_results)
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_contracts': len(set(r.contract_name for r in self.test_results)),
                'total_endpoints': len(self.test_results),
                'success_rate': self.test_metrics['passed_tests'] / max(self.test_metrics['total_tests'], 1) * 100,
                'metrics': self.test_metrics
            },
            'contracts': {},
            'failures': [],
            'performance': {
                'fastest_endpoint': None,
                'slowest_endpoint': None,
                'average_response_time': self.test_metrics['average_response_time']
            }
        }
        
        # Group results by contract
        for result in self.test_results:
            if result.contract_name not in report['contracts']:
                report['contracts'][result.contract_name] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'errors': 0,
                    'endpoints': []
                }
            
            contract_report = report['contracts'][result.contract_name]
            contract_report['total'] += 1
            contract_report['endpoints'].append({
                'endpoint': result.endpoint,
                'method': result.method,
                'status': result.status,
                'execution_time_ms': result.execution_time_ms,
                'errors': result.errors
            })
            
            if result.status == 'passed':
                contract_report['passed'] += 1
            elif result.status == 'failed':
                contract_report['failed'] += 1
                report['failures'].append({
                    'contract': result.contract_name,
                    'endpoint': result.endpoint,
                    'method': result.method,
                    'errors': result.errors
                })
            else:
                contract_report['errors'] += 1
        
        # Performance analysis
        if self.test_results:
            fastest = min(self.test_results, key=lambda r: r.execution_time_ms)
            slowest = max(self.test_results, key=lambda r: r.execution_time_ms)
            
            report['performance']['fastest_endpoint'] = {
                'contract': fastest.contract_name,
                'endpoint': fastest.endpoint,
                'time_ms': fastest.execution_time_ms
            }
            
            report['performance']['slowest_endpoint'] = {
                'contract': slowest.contract_name,
                'endpoint': slowest.endpoint,
                'time_ms': slowest.execution_time_ms
            }
        
        return report
    
    async def save_report(self, report -> None: Dict[str, Any], output_path -> None: str = "contract_test_report.json") -> None:
        """Save test report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Contract test report saved to: {output_path}")
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.session:
            await self.session.close()


# CLI Interface
async def main() -> None:
    """Main CLI interface for contract testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Contract Testing Engine")
    parser.add_argument("--contracts-dir", required=True, help="Directory containing contract definitions")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", default="contract_test_report.json", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize tester
    tester = APIContractTester(args.config)
    
    try:
        # Load contracts
        contracts = await tester.load_contracts(args.contracts_dir)
        
        if not contracts:
            logger.error("No contracts found to test")
            return
        
        # Run tests
        report = await tester.run_contract_tests(contracts)
        
        # Save report
        await tester.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n🔍 API Contract Test Results")
        print(f"{'='*50}")
        print(f"Contracts Tested: {summary['total_contracts']}")
        print(f"Endpoints Tested: {summary['total_endpoints']}")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        print(f"Average Response Time: {summary['metrics']['average_response_time']:.2f}ms")
        
        if summary['success_rate'] < 100:
            print(f"\n❌ {len(report['failures'])} failures detected")
            for failure in report['failures'][:5]:  # Show first 5 failures
                print(f"  - {failure['contract']}: {failure['method']} {failure['endpoint']}")
        else:
            print(f"\n✅ All tests passed!")
    
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())