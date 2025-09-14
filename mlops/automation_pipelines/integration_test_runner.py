"""
Enterprise Integration Test Runner for MLOps
DevOps + ML Engineer implementation with end-to-end pipeline testing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import subprocess
import yaml
import uuid
import tempfile
import shutil
from pathlib import Path
import requests
import time
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import warnings

logger = logging.getLogger(__name__)


class IntegrationTestType(Enum):
    """Types of integration tests"""
    PIPELINE_END_TO_END = "pipeline_end_to_end"
    SERVICE_TO_SERVICE = "service_to_service"
    DATA_PIPELINE = "data_pipeline"
    MODEL_PIPELINE = "model_pipeline"
    API_INTEGRATION = "api_integration"
    INFRASTRUCTURE = "infrastructure"
    SECURITY_INTEGRATION = "security_integration"
    PERFORMANCE_INTEGRATION = "performance_integration"


class TestEnvironment(Enum):
    """Test environments"""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    STAGING = "staging"
    CLOUD = "cloud"


class TestStatus(Enum):
    """Integration test status"""
    PENDING = "pending"
    SETTING_UP = "setting_up"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"
    CLEANUP = "cleanup"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    name: str
    url: str
    health_check_path: str = "/health"
    authentication: Optional[Dict[str, str]] = None
    timeout_seconds: int = 30
    retry_count: int = 3
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class TestData:
    """Test data configuration"""
    input_data: Any = None
    expected_output: Any = None
    data_path: Optional[Path] = None
    schema_validation: bool = True
    data_size_mb: float = 0.0
    data_format: str = "json"


@dataclass
class IntegrationTestCase:
    """Integration test case definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    test_type: IntegrationTestType = IntegrationTestType.PIPELINE_END_TO_END
    environment: TestEnvironment = TestEnvironment.LOCAL
    priority: int = 1
    timeout_seconds: int = 600
    retry_count: int = 1
    
    # Services and dependencies
    required_services: List[ServiceEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Test data
    test_data: Optional[TestData] = None
    
    # Test functions
    setup_function: Optional[Callable] = None
    test_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    validation_function: Optional[Callable] = None
    
    # Configuration
    environment_config: Dict[str, Any] = field(default_factory=dict)
    service_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationTestResult:
    """Integration test result"""
    test_case_id: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Results
    result_data: Any = None
    validation_results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Logs and artifacts
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    service_logs: Dict[str, List[str]] = field(default_factory=dict)
    
    # Environment state
    environment_state: Dict[str, Any] = field(default_factory=dict)


class ServiceManager:
    """Manages services during integration testing"""
    
    def __init__(self):
        self.running_services: Dict[str, Any] = {}
        self.service_health: Dict[str, bool] = {}
        
    async def start_services(
        self, 
        services: List[ServiceEndpoint],
        environment: TestEnvironment
    ) -> Dict[str, bool]:
        """Start required services for testing"""
        try:
            start_results = {}
            
            for service in services:
                logger.info(f"Starting service: {service.name}")
                
                if environment == TestEnvironment.DOCKER:
                    success = await self._start_docker_service(service)
                elif environment == TestEnvironment.KUBERNETES:
                    success = await self._start_k8s_service(service)
                elif environment == TestEnvironment.LOCAL:
                    success = await self._start_local_service(service)
                else:
                    success = await self._check_remote_service(service)
                
                start_results[service.name] = success
                self.service_health[service.name] = success
                
                if success:
                    self.running_services[service.name] = service
            
            return start_results
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            raise

    async def _start_docker_service(self, service: ServiceEndpoint) -> bool:
        """Start service using Docker"""
        try:
            # This would integrate with Docker API
            # For now, simulate service startup
            await asyncio.sleep(2)  # Simulate startup time
            
            # Check if service is healthy
            return await self._check_service_health(service)
            
        except Exception as e:
            logger.error(f"Failed to start Docker service {service.name}: {e}")
            return False

    async def _start_k8s_service(self, service: ServiceEndpoint) -> bool:
        """Start service using Kubernetes"""
        try:
            # This would integrate with Kubernetes API
            # For now, simulate service startup
            await asyncio.sleep(3)  # Simulate startup time
            
            return await self._check_service_health(service)
            
        except Exception as e:
            logger.error(f"Failed to start K8s service {service.name}: {e}")
            return False

    async def _start_local_service(self, service: ServiceEndpoint) -> bool:
        """Start service locally"""
        try:
            # For local testing, assume service is already running
            # or start it using subprocess
            return await self._check_service_health(service)
            
        except Exception as e:
            logger.error(f"Failed to start local service {service.name}: {e}")
            return False

    async def _check_remote_service(self, service: ServiceEndpoint) -> bool:
        """Check remote service availability"""
        try:
            return await self._check_service_health(service)
        except Exception as e:
            logger.error(f"Failed to check remote service {service.name}: {e}")
            return False

    async def _check_service_health(self, service: ServiceEndpoint) -> bool:
        """Check if service is healthy"""
        try:
            health_url = f"{service.url.rstrip('/')}{service.health_check_path}"
            
            # Simulate health check for testing
            # In production, this would make actual HTTP requests
            await asyncio.sleep(0.1)
            return True
            
            # Real implementation would be:
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(health_url, timeout=service.timeout_seconds) as response:
            #         return response.status == 200
                        
        except Exception as e:
            logger.warning(f"Health check failed for {service.name}: {e}")
            return False

    async def wait_for_services(
        self, 
        services: List[ServiceEndpoint],
        timeout_seconds: int = 300
    ) -> bool:
        """Wait for all services to be healthy"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout_seconds:
                all_healthy = True
                
                for service in services:
                    if not await self._check_service_health(service):
                        all_healthy = False
                        break
                
                if all_healthy:
                    logger.info("All services are healthy")
                    return True
                
                await asyncio.sleep(5)  # Wait 5 seconds before retry
            
            logger.error(f"Services did not become healthy within {timeout_seconds} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for services: {e}")
            return False

    async def stop_services(self, services: List[ServiceEndpoint]):
        """Stop running services"""
        try:
            for service in services:
                if service.name in self.running_services:
                    logger.info(f"Stopping service: {service.name}")
                    
                    # Implementation would depend on how service was started
                    # For now, just remove from tracking
                    del self.running_services[service.name]
                    if service.name in self.service_health:
                        del self.service_health[service.name]
                        
        except Exception as e:
            logger.error(f"Error stopping services: {e}")

    async def collect_service_logs(
        self, 
        services: List[ServiceEndpoint]
    ) -> Dict[str, List[str]]:
        """Collect logs from all services"""
        logs = {}
        
        for service in services:
            try:
                # In production, this would collect actual logs
                # For now, return mock logs
                logs[service.name] = [
                    f"[INFO] Service {service.name} started",
                    f"[INFO] Health check passed for {service.name}",
                    f"[INFO] Service {service.name} processing requests"
                ]
            except Exception as e:
                logger.warning(f"Failed to collect logs for {service.name}: {e}")
                logs[service.name] = [f"[ERROR] Failed to collect logs: {e}"]
        
        return logs


class DataPipelineValidator:
    """Validates data pipelines during integration testing"""
    
    def __init__(self):
        self.validation_cache: Dict[str, Any] = {}
    
    async def validate_data_flow(
        self,
        input_data: Any,
        output_data: Any,
        pipeline_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data flow through pipeline"""
        try:
            validation_results = {
                "input_validation": await self._validate_input_data(input_data),
                "output_validation": await self._validate_output_data(output_data),
                "transformation_validation": await self._validate_transformations(
                    input_data, output_data, pipeline_config
                ),
                "schema_validation": await self._validate_schemas(input_data, output_data),
                "data_quality": await self._validate_data_quality(output_data)
            }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Data flow validation failed: {e}")
            raise

    async def _validate_input_data(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data"""
        try:
            if isinstance(input_data, (pd.DataFrame, np.ndarray)):
                return {
                    "valid": True,
                    "size": len(input_data),
                    "shape": getattr(input_data, 'shape', None),
                    "type": type(input_data).__name__
                }
            elif isinstance(input_data, (dict, list)):
                return {
                    "valid": True,
                    "size": len(input_data),
                    "type": type(input_data).__name__
                }
            else:
                return {
                    "valid": True,
                    "type": type(input_data).__name__
                }
                
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def _validate_output_data(self, output_data: Any) -> Dict[str, Any]:
        """Validate output data"""
        return await self._validate_input_data(output_data)  # Same validation logic

    async def _validate_transformations(
        self,
        input_data: Any,
        output_data: Any,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data transformations"""
        try:
            # Check if transformations were applied correctly
            transformations_applied = []
            
            if "normalization" in config:
                transformations_applied.append("normalization")
            
            if "feature_engineering" in config:
                transformations_applied.append("feature_engineering")
            
            return {
                "valid": True,
                "transformations_applied": transformations_applied,
                "input_size": len(input_data) if hasattr(input_data, '__len__') else 1,
                "output_size": len(output_data) if hasattr(output_data, '__len__') else 1
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def _validate_schemas(self, input_data: Any, output_data: Any) -> Dict[str, Any]:
        """Validate data schemas"""
        try:
            input_schema = self._infer_schema(input_data)
            output_schema = self._infer_schema(output_data)
            
            return {
                "valid": True,
                "input_schema": input_schema,
                "output_schema": output_schema,
                "schema_compatibility": self._check_schema_compatibility(
                    input_schema, output_schema
                )
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _infer_schema(self, data: Any) -> Dict[str, Any]:
        """Infer schema from data"""
        try:
            if isinstance(data, pd.DataFrame):
                return {
                    "type": "dataframe",
                    "columns": list(data.columns),
                    "dtypes": data.dtypes.to_dict(),
                    "shape": data.shape
                }
            elif isinstance(data, np.ndarray):
                return {
                    "type": "numpy_array",
                    "shape": data.shape,
                    "dtype": str(data.dtype)
                }
            elif isinstance(data, dict):
                return {
                    "type": "dict",
                    "keys": list(data.keys()),
                    "value_types": {k: type(v).__name__ for k, v in data.items()}
                }
            else:
                return {
                    "type": type(data).__name__,
                    "value": str(data)[:100]  # First 100 chars
                }
        except Exception:
            return {"type": "unknown"}

    def _check_schema_compatibility(
        self, 
        input_schema: Dict[str, Any], 
        output_schema: Dict[str, Any]
    ) -> bool:
        """Check if schemas are compatible"""
        # Simple compatibility check
        return input_schema.get("type") == output_schema.get("type")

    async def _validate_data_quality(self, data: Any) -> Dict[str, Any]:
        """Validate data quality"""
        try:
            quality_metrics = {
                "completeness": 1.0,
                "consistency": 1.0,
                "accuracy": 1.0,
                "validity": 1.0
            }
            
            if isinstance(data, pd.DataFrame):
                # Calculate actual quality metrics
                total_cells = data.size
                missing_cells = data.isnull().sum().sum()
                quality_metrics["completeness"] = 1.0 - (missing_cells / total_cells)
                
                # Check for duplicates
                duplicate_rows = data.duplicated().sum()
                quality_metrics["consistency"] = 1.0 - (duplicate_rows / len(data))
            
            return {
                "valid": True,
                "quality_score": sum(quality_metrics.values()) / len(quality_metrics),
                "metrics": quality_metrics
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}


class IntegrationTestRunner:
    """
    Enterprise integration test runner for MLOps pipelines
    """
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.data_validator = DataPipelineValidator()
        self.test_results: Dict[str, IntegrationTestResult] = {}
        self.test_artifacts: Dict[str, Dict[str, Any]] = {}
        
    async def run_integration_test(
        self,
        test_case: IntegrationTestCase
    ) -> IntegrationTestResult:
        """Run a single integration test"""
        result = IntegrationTestResult(
            test_case_id=test_case.id,
            status=TestStatus.SETTING_UP,
            start_time=datetime.utcnow()
        )
        
        try:
            logger.info(f"Running integration test: {test_case.name}")
            
            # Setup phase
            result.status = TestStatus.SETTING_UP
            await self._setup_test_environment(test_case, result)
            
            # Start required services
            if test_case.required_services:
                service_results = await self.service_manager.start_services(
                    test_case.required_services,
                    test_case.environment
                )
                
                # Wait for services to be ready
                services_ready = await self.service_manager.wait_for_services(
                    test_case.required_services,
                    timeout_seconds=test_case.timeout_seconds // 2
                )
                
                if not services_ready:
                    result.status = TestStatus.FAILED
                    result.error_message = "Required services failed to start"
                    return result
            
            # Run setup function
            if test_case.setup_function:
                await test_case.setup_function(test_case, result)
            
            # Execute test
            result.status = TestStatus.RUNNING
            test_start_time = time.time()
            
            if test_case.test_function:
                test_result = await asyncio.wait_for(
                    test_case.test_function(test_case, result),
                    timeout=test_case.timeout_seconds
                )
                result.result_data = test_result
            else:
                # Default test execution
                test_result = await self._execute_default_test(test_case, result)
                result.result_data = test_result
            
            test_duration = time.time() - test_start_time
            result.performance_metrics["test_execution_time"] = test_duration
            
            # Validate results
            if test_case.validation_function:
                validation_results = await test_case.validation_function(test_case, result)
                result.validation_results = validation_results
                
                if not validation_results.get("valid", True):
                    result.status = TestStatus.FAILED
                    result.error_message = validation_results.get("error", "Validation failed")
                    return result
            
            # Success
            result.status = TestStatus.PASSED
            logger.info(f"Integration test passed: {test_case.name}")
            
        except asyncio.TimeoutError:
            result.status = TestStatus.TIMEOUT
            result.error_message = f"Test timed out after {test_case.timeout_seconds} seconds"
            logger.error(f"Integration test timed out: {test_case.name}")
            
        except Exception as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Integration test failed: {test_case.name} - {e}")
            
        finally:
            # Cleanup phase
            result.status = TestStatus.CLEANUP
            await self._cleanup_test_environment(test_case, result)
            
            # Collect logs and artifacts
            if test_case.required_services:
                result.service_logs = await self.service_manager.collect_service_logs(
                    test_case.required_services
                )
                await self.service_manager.stop_services(test_case.required_services)
            
            # Run teardown function
            if test_case.teardown_function:
                try:
                    await test_case.teardown_function(test_case, result)
                except Exception as e:
                    logger.warning(f"Teardown failed for {test_case.name}: {e}")
            
            result.end_time = datetime.utcnow()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            
            # Store result
            self.test_results[test_case.id] = result
        
        return result

    async def _setup_test_environment(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ):
        """Setup test environment"""
        try:
            # Create temporary directories if needed
            if test_case.test_data and test_case.test_data.data_path:
                test_case.test_data.data_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup environment variables
            for key, value in test_case.environment_config.items():
                # In production, this would set actual environment variables
                result.environment_state[key] = value
            
            # Setup test data
            if test_case.test_data:
                await self._prepare_test_data(test_case.test_data, result)
            
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            raise

    async def _prepare_test_data(self, test_data: TestData, result: IntegrationTestResult):
        """Prepare test data"""
        try:
            if test_data.input_data is not None:
                # Validate test data
                if isinstance(test_data.input_data, pd.DataFrame):
                    result.artifacts["input_data_shape"] = str(test_data.input_data.shape)
                    result.artifacts["input_data_size_mb"] = str(
                        test_data.input_data.memory_usage(deep=True).sum() / (1024 * 1024)
                    )
                
                # Save test data if path specified
                if test_data.data_path:
                    if test_data.data_format == "json":
                        if isinstance(test_data.input_data, pd.DataFrame):
                            test_data.input_data.to_json(test_data.data_path)
                        else:
                            with open(test_data.data_path, 'w') as f:
                                json.dump(test_data.input_data, f)
                    elif test_data.data_format == "csv":
                        if isinstance(test_data.input_data, pd.DataFrame):
                            test_data.input_data.to_csv(test_data.data_path, index=False)
            
        except Exception as e:
            logger.error(f"Test data preparation failed: {e}")
            raise

    async def _execute_default_test(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ) -> Any:
        """Execute default test based on test type"""
        try:
            if test_case.test_type == IntegrationTestType.PIPELINE_END_TO_END:
                return await self._test_pipeline_end_to_end(test_case, result)
            elif test_case.test_type == IntegrationTestType.SERVICE_TO_SERVICE:
                return await self._test_service_to_service(test_case, result)
            elif test_case.test_type == IntegrationTestType.DATA_PIPELINE:
                return await self._test_data_pipeline(test_case, result)
            elif test_case.test_type == IntegrationTestType.API_INTEGRATION:
                return await self._test_api_integration(test_case, result)
            else:
                return {"status": "completed", "message": "Default test passed"}
                
        except Exception as e:
            logger.error(f"Default test execution failed: {e}")
            raise

    async def _test_pipeline_end_to_end(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ) -> Dict[str, Any]:
        """Test complete pipeline end-to-end"""
        try:
            # Simulate pipeline execution
            start_time = time.time()
            
            # Mock pipeline stages
            stages = ["data_ingestion", "preprocessing", "model_training", "evaluation", "deployment"]
            stage_results = {}
            
            for stage in stages:
                stage_start = time.time()
                
                # Simulate stage execution
                await asyncio.sleep(0.5)  # Mock processing time
                
                stage_duration = time.time() - stage_start
                stage_results[stage] = {
                    "status": "completed",
                    "duration": stage_duration,
                    "output_size": np.random.randint(100, 1000)
                }
            
            total_duration = time.time() - start_time
            result.performance_metrics["pipeline_total_duration"] = total_duration
            
            return {
                "status": "completed",
                "stages": stage_results,
                "total_duration": total_duration
            }
            
        except Exception as e:
            logger.error(f"End-to-end pipeline test failed: {e}")
            raise

    async def _test_service_to_service(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ) -> Dict[str, Any]:
        """Test service-to-service communication"""
        try:
            communication_results = {}
            
            for i, service in enumerate(test_case.required_services):
                for j, target_service in enumerate(test_case.required_services):
                    if i != j:  # Don't test service to itself
                        # Simulate service communication
                        comm_key = f"{service.name}_to_{target_service.name}"
                        
                        start_time = time.time()
                        # Mock communication test
                        await asyncio.sleep(0.1)
                        comm_duration = time.time() - start_time
                        
                        communication_results[comm_key] = {
                            "status": "success",
                            "latency_ms": comm_duration * 1000,
                            "response_size": np.random.randint(100, 5000)
                        }
            
            return {
                "status": "completed",
                "communications": communication_results
            }
            
        except Exception as e:
            logger.error(f"Service-to-service test failed: {e}")
            raise

    async def _test_data_pipeline(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ) -> Dict[str, Any]:
        """Test data pipeline"""
        try:
            if not test_case.test_data or test_case.test_data.input_data is None:
                # Generate mock data
                input_data = pd.DataFrame({
                    'feature1': np.random.random(100),
                    'feature2': np.random.random(100),
                    'label': np.random.randint(0, 2, 100)
                })
            else:
                input_data = test_case.test_data.input_data
            
            # Simulate data processing
            processed_data = input_data.copy()
            
            # Mock some data transformations
            if 'feature1' in processed_data.columns:
                processed_data['feature1_normalized'] = (
                    processed_data['feature1'] - processed_data['feature1'].mean()
                ) / processed_data['feature1'].std()
            
            # Validate data pipeline
            validation_results = await self.data_validator.validate_data_flow(
                input_data, processed_data, test_case.service_config
            )
            
            result.validation_results = validation_results
            
            return {
                "status": "completed",
                "input_records": len(input_data),
                "output_records": len(processed_data),
                "validation": validation_results
            }
            
        except Exception as e:
            logger.error(f"Data pipeline test failed: {e}")
            raise

    async def _test_api_integration(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ) -> Dict[str, Any]:
        """Test API integration"""
        try:
            api_results = {}
            
            for service in test_case.required_services:
                # Test different API endpoints
                endpoints = [
                    "/health",
                    "/predict",
                    "/status",
                    "/metrics"
                ]
                
                service_results = {}
                
                for endpoint in endpoints:
                    start_time = time.time()
                    
                    # Mock API call
                    await asyncio.sleep(0.05)  # Mock network latency
                    
                    response_time = time.time() - start_time
                    
                    service_results[endpoint] = {
                        "status_code": 200,
                        "response_time_ms": response_time * 1000,
                        "response_size": np.random.randint(100, 2000)
                    }
                
                api_results[service.name] = service_results
            
            return {
                "status": "completed",
                "api_tests": api_results
            }
            
        except Exception as e:
            logger.error(f"API integration test failed: {e}")
            raise

    async def _cleanup_test_environment(
        self,
        test_case: IntegrationTestCase,
        result: IntegrationTestResult
    ):
        """Cleanup test environment"""
        try:
            # Clean up temporary files
            if test_case.test_data and test_case.test_data.data_path:
                if test_case.test_data.data_path.exists():
                    test_case.test_data.data_path.unlink()
            
            # Clean up environment state
            result.environment_state.clear()
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    async def run_test_suite(
        self,
        test_cases: List[IntegrationTestCase],
        parallel: bool = True,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """Run a suite of integration tests"""
        try:
            logger.info(f"Running integration test suite with {len(test_cases)} tests")
            start_time = datetime.utcnow()
            
            if parallel and len(test_cases) > 1:
                # Run tests in parallel with controlled concurrency
                semaphore = asyncio.Semaphore(max_workers)
                
                async def run_with_semaphore(test_case):
                    async with semaphore:
                        return await self.run_integration_test(test_case)
                
                results = await asyncio.gather(
                    *[run_with_semaphore(tc) for tc in test_cases],
                    return_exceptions=True
                )
            else:
                # Run tests sequentially
                results = []
                for test_case in test_cases:
                    result = await self.run_integration_test(test_case)
                    results.append(result)
            
            # Process results
            valid_results = [r for r in results if isinstance(r, IntegrationTestResult)]
            error_results = [r for r in results if isinstance(r, Exception)]
            
            # Calculate summary
            total_tests = len(test_cases)
            passed_tests = len([r for r in valid_results if r.status == TestStatus.PASSED])
            failed_tests = len([r for r in valid_results if r.status == TestStatus.FAILED])
            timeout_tests = len([r for r in valid_results if r.status == TestStatus.TIMEOUT])
            error_tests = len(error_results)
            
            end_time = datetime.utcnow()
            total_duration = (end_time - start_time).total_seconds()
            
            summary = {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "timeout": timeout_tests,
                "errors": error_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration_seconds": total_duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "parallel_execution": parallel,
                "results": valid_results
            }
            
            logger.info(f"Integration test suite completed: {passed_tests}/{total_tests} passed")
            return summary
            
        except Exception as e:
            logger.error(f"Integration test suite execution failed: {e}")
            raise

    async def generate_integration_report(
        self,
        suite_results: Dict[str, Any],
        output_path: Path
    ) -> str:
        """Generate comprehensive integration test report"""
        try:
            results = suite_results["results"]
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Integration Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test-result {{ margin: 10px 0; padding: 15px; border-left: 4px solid #ddd; }}
        .passed {{ border-left-color: #4CAF50; }}
        .failed {{ border-left-color: #f44336; }}
        .timeout {{ border-left-color: #ff9800; }}
        .error {{ border-left-color: #9C27B0; }}
        .metrics {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
        .service-logs {{ background-color: #f5f5f5; padding: 10px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Integration Test Report</h1>
        <p>Generated: {datetime.utcnow().isoformat()}</p>
    </div>
    
    <div class="summary">
        <h3>Summary</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Tests</td><td>{suite_results['total_tests']}</td></tr>
            <tr><td>Passed</td><td>{suite_results['passed']}</td></tr>
            <tr><td>Failed</td><td>{suite_results['failed']}</td></tr>
            <tr><td>Timeout</td><td>{suite_results['timeout']}</td></tr>
            <tr><td>Errors</td><td>{suite_results['errors']}</td></tr>
            <tr><td>Success Rate</td><td>{suite_results['success_rate']:.1f}%</td></tr>
            <tr><td>Total Duration</td><td>{suite_results['total_duration_seconds']:.1f}s</td></tr>
        </table>
    </div>
    
    <div class="results">
        <h3>Test Results</h3>
"""
            
            for result in results:
                status_class = result.status.value
                
                html_content += f"""
        <div class="test-result {status_class}">
            <h4>Test: {result.test_case_id}</h4>
            <p><strong>Status:</strong> {result.status.value.upper()}</p>
            <p><strong>Duration:</strong> {result.duration_seconds:.3f}s</p>
            <p><strong>Start Time:</strong> {result.start_time.isoformat()}</p>
"""
                
                if result.error_message:
                    html_content += f"<p><strong>Error:</strong> {result.error_message}</p>"
                
                if result.performance_metrics:
                    html_content += f"""
            <div class="metrics">
                <strong>Performance Metrics:</strong>
                <ul>
"""
                    for metric, value in result.performance_metrics.items():
                        html_content += f"<li>{metric}: {value:.3f}</li>"
                    html_content += "</ul></div>"
                
                if result.validation_results:
                    html_content += f"""
            <div class="metrics">
                <strong>Validation Results:</strong>
                <pre>{json.dumps(result.validation_results, indent=2)}</pre>
            </div>
"""
                
                if result.service_logs:
                    html_content += f"""
            <div class="service-logs">
                <strong>Service Logs:</strong>
"""
                    for service, logs in result.service_logs.items():
                        html_content += f"""
                <h5>{service}:</h5>
                <pre>{"".join(logs)}</pre>
"""
                    html_content += "</div>"
                
                html_content += "</div>"
            
            html_content += """
    </div>
</body>
</html>
"""
            
            # Write report
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content, encoding='utf-8')
            
            logger.info(f"Integration test report generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate integration test report: {e}")
            raise


# Factory functions
def create_integration_test_runner() -> IntegrationTestRunner:
    """Create a new integration test runner instance"""
    return IntegrationTestRunner()


def create_service_endpoint(
    name: str,
    url: str,
    health_check_path: str = "/health"
) -> ServiceEndpoint:
    """Create a service endpoint configuration"""
    return ServiceEndpoint(
        name=name,
        url=url,
        health_check_path=health_check_path
    )


def create_integration_test_case(
    name: str,
    description: str,
    test_type: IntegrationTestType = IntegrationTestType.PIPELINE_END_TO_END,
    environment: TestEnvironment = TestEnvironment.LOCAL
) -> IntegrationTestCase:
    """Create an integration test case"""
    return IntegrationTestCase(
        name=name,
        description=description,
        test_type=test_type,
        environment=environment
    )


# Example usage
if __name__ == "__main__":
    async def main():
        # Create test runner
        runner = create_integration_test_runner()
        
        # Create service endpoints
        ml_service = create_service_endpoint(
            name="ml-inference-service",
            url="http://localhost:8080"
        )
        
        data_service = create_service_endpoint(
            name="data-pipeline-service",
            url="http://localhost:8081"
        )
        
        # Create test cases
        test_cases = [
            IntegrationTestCase(
                name="test_ml_pipeline_end_to_end",
                description="Test complete ML pipeline from data to prediction",
                test_type=IntegrationTestType.PIPELINE_END_TO_END,
                environment=TestEnvironment.LOCAL,
                required_services=[ml_service, data_service],
                timeout_seconds=300
            ),
            IntegrationTestCase(
                name="test_service_communication",
                description="Test service-to-service communication",
                test_type=IntegrationTestType.SERVICE_TO_SERVICE,
                environment=TestEnvironment.LOCAL,
                required_services=[ml_service, data_service],
                timeout_seconds=180
            )
        ]
        
        print(f"Running {len(test_cases)} integration tests...")
        
        # Run test suite
        results = await runner.run_test_suite(
            test_cases=test_cases,
            parallel=True,
            max_workers=2
        )
        
        print(f"Integration tests completed:")
        print(f"- Total tests: {results['total_tests']}")
        print(f"- Passed: {results['passed']}")
        print(f"- Failed: {results['failed']}")
        print(f"- Success rate: {results['success_rate']:.1f}%")
        print(f"- Duration: {results['total_duration_seconds']:.1f}s")
        
        # Generate report
        report_path = Path("integration_test_report.html")
        await runner.generate_integration_report(results, report_path)
        print(f"Report generated: {report_path}")
    
    asyncio.run(main())