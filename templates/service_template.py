"""{{service_name}} Service Template
{{service_description}}

Author: {{author_name}} ({{author_email}})
Copyright: (c) {{year}} {{author_name}}. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Service-specific imports
from core.base_service import BaseService
from core.exceptions import ServiceException
from monitoring.metrics import MetricsCollector
from utils.logger import get_logger

logger = get_logger(__name__)

class {{service_name}}Status(Enum):
    """Service status enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class {{service_name}}Config:
    """Configuration for {{service_name}} service."""
    # Configuration parameters
    enabled: bool = True
    max_concurrent_requests: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_ttl: int = 3600
    
    # Service-specific configuration
    # Add your configuration parameters here
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.max_concurrent_requests <= 0:
            raise ValueError("max_concurrent_requests must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        return True

class {{service_name}}Service(BaseService):
    """{{service_description}}
    
    This service provides the following capabilities:
    - Feature 1: Description
    - Feature 2: Description
    - Feature 3: Description
    """
    
    def __init__(self, config: {{service_name}}Config):
        """Initialize the {{service_name}} service.
        
        Args:
            config: Service configuration
        """
        super().__init__()
        self.config = config
        self.config.validate()
        
        self.status = {{service_name}}Status.INITIALIZING
        self.metrics = MetricsCollector(service_name="{{service_name_lower}}")
        self.session_pool = {}
        
        # Service-specific initialization
        self._initialize_service()
        
    def _initialize_service(self):
        """Initialize service-specific components."""
        try:
            # Initialize your service components here
            # Examples:
            # - Database connections
            # - External API clients
            # - Cache systems
            # - Background tasks
            
            logger.info("{{service_name}} service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {{service_name}} service: {e}")
            raise ServiceException(f"Initialization failed: {e}")
    
    async def start(self) -> bool:
        """Start the service and all its components.
        
        Returns:
            bool: True if service started successfully
        """
        try:
            logger.info("Starting {{service_name}} service...")
            
            # Start service components
            await self._start_components()
            
            self.status = {{service_name}}Status.RUNNING
            logger.info("{{service_name}} service started successfully")
            
            # Record metrics
            self.metrics.increment_counter("service_starts")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {{service_name}} service: {e}")
            self.status = {{service_name}}Status.ERROR
            raise ServiceException(f"Service start failed: {e}")
    
    async def stop(self) -> bool:
        """Stop the service gracefully.
        
        Returns:
            bool: True if service stopped successfully
        """
        try:
            logger.info("Stopping {{service_name}} service...")
            
            # Stop service components
            await self._stop_components()
            
            self.status = {{service_name}}Status.STOPPED
            logger.info("{{service_name}} service stopped successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {{service_name}} service: {e}")
            return False
    
    async def _start_components(self):
        """Start all service components."""
        # Start your service components here
        # Examples:
        # - Background task workers
        # - Connection pools
        # - Monitoring services
        pass
    
    async def _stop_components(self):
        """Stop all service components gracefully."""
        # Stop your service components here
        # Examples:
        # - Close database connections
        # - Stop background tasks
        # - Clear caches
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check.
        
        Returns:
            Dict containing health status and metrics
        """
        try:
            health_status = {
                "service": "{{service_name}}",
                "status": self.status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "components": {}
            }
            
            # Check component health
            health_status["components"]["database"] = await self._check_database_health()
            health_status["components"]["cache"] = await self._check_cache_health()
            health_status["components"]["external_apis"] = await self._check_external_apis_health()
            
            # Calculate overall health
            component_statuses = [comp.get("healthy", False) for comp in health_status["components"].values()]
            health_status["healthy"] = all(component_statuses) and self.status == {{service_name}}Status.RUNNING
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "{{service_name}}",
                "status": "error",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            # Implement database health check
            # Example: ping database, check connection pool
            return {
                "healthy": True,
                "response_time_ms": 5,
                "connections_active": 10,
                "connections_max": 100
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health."""
        try:
            # Implement cache health check
            # Example: ping Redis, check memory usage
            return {
                "healthy": True,
                "response_time_ms": 2,
                "memory_usage_mb": 50,
                "hit_rate": 0.95
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_external_apis_health(self) -> Dict[str, Any]:
        """Check external API dependencies."""
        try:
            # Implement external API health checks
            # Example: ping third-party services
            return {
                "healthy": True,
                "apis_checked": 3,
                "apis_healthy": 3,
                "average_response_time_ms": 150
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    # Core service methods - implement your business logic here
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request.
        
        Args:
            request_data: Input data for processing
            
        Returns:
            Dict containing processing results
        """
        try:
            # Record request metrics
            self.metrics.increment_counter("requests_received")
            start_time = datetime.utcnow()
            
            # Validate input
            self._validate_request(request_data)
            
            # Process the request
            result = await self._process_business_logic(request_data)
            
            # Record success metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.record_histogram("request_duration_seconds", processing_time)
            self.metrics.increment_counter("requests_successful")
            
            return {
                "success": True,
                "result": result,
                "processing_time_seconds": processing_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            self.metrics.increment_counter("requests_failed")
            raise ServiceException(f"Processing failed: {e}")
    
    def _validate_request(self, request_data: Dict[str, Any]):
        """Validate request data."""
        # Implement your validation logic here
        if not request_data:
            raise ValueError("Request data cannot be empty")
        
        # Add specific validation for your service
        required_fields = ["field1", "field2"]  # Define your required fields
        for field in required_fields:
            if field not in request_data:
                raise ValueError(f"Required field '{field}' missing")
    
    async def _process_business_logic(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement your core business logic here.
        
        Args:
            request_data: Validated input data
            
        Returns:
            Dict containing processing results
        """
        # IMPLEMENTATION NOTE: Replace this with your actual business logic
        
        # Example processing steps:
        # 1. Data preprocessing
        processed_data = await self._preprocess_data(request_data)
        
        # 2. Core processing
        core_result = await self._core_processing(processed_data)
        
        # 3. Post-processing
        final_result = await self._postprocess_result(core_result)
        
        return final_result
    
    async def _preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess input data."""
        # Implement data preprocessing
        return data
    
    async def _core_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform core business logic processing."""
        # Implement your core processing logic
        return {"processed": True, "data": data}
    
    async def _postprocess_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process the results."""
        # Implement result post-processing
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics and statistics.
        
        Returns:
            Dict containing service metrics
        """
        return {
            "service": "{{service_name}}",
            "status": self.status.value,
            "metrics": self.metrics.get_all_metrics(),
            "config": {
                "max_concurrent_requests": self.config.max_concurrent_requests,
                "timeout_seconds": self.config.timeout_seconds,
                "cache_ttl": self.config.cache_ttl
            },
            "timestamp": datetime.utcnow().isoformat()
        }

# Service factory function
def create_{{service_name_lower}}_service(config: Optional[Dict[str, Any]] = None) -> {{service_name}}Service:
    """Create and configure a {{service_name}} service instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured {{service_name}}Service instance
    """
    if config is None:
        config = {}
    
    service_config = {{service_name}}Config(**config)
    return {{service_name}}Service(service_config)

# Example usage
async def main():
    """Example usage of the {{service_name}} service."""
    try:
        # Create service
        service = create_{{service_name_lower}}_service({
            "max_concurrent_requests": 50,
            "timeout_seconds": 30
        })
        
        # Start service
        await service.start()
        
        # Process a request
        result = await service.process_request({
            "field1": "value1",
            "field2": "value2"
        })
        
        print(f"Processing result: {result}")
        
        # Get health status
        health = await service.health_check()
        print(f"Service health: {health}")
        
        # Stop service
        await service.stop()
        
    except Exception as e:
        logger.error(f"Service example failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())