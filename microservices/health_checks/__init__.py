"""
Health Checks Module for Ainflue Microservices
Implements health monitoring and service availability checks.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import time
from typing import Dict, List, Any, Callable, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

__all__ = ['HealthStatus', 'HealthCheck', 'HealthChecker', 'ServiceHealthManager']

class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class HealthCheck:
    """Individual health check implementation"""
    
    def __init__(self, name: str, check_func: Callable, timeout: int = 30):
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.last_check_time = None
        self.last_status = HealthStatus.UNKNOWN
        
    async def perform_check(self) -> Dict[str, Any]:
        """Perform the health check"""
        start_time = time.time()
        
        try:
            # Execute health check with timeout
            result = await asyncio.wait_for(
                self._execute_check(),
                timeout=self.timeout
            )
            
            self.last_check_time = time.time()
            self.last_status = HealthStatus.HEALTHY
            
            return {
                'name': self.name,
                'status': self.last_status.value,
                'duration': time.time() - start_time,
                'result': result,
                'timestamp': self.last_check_time
            }
            
        except asyncio.TimeoutError:
            self.last_status = HealthStatus.UNHEALTHY
            return {
                'name': self.name,
                'status': self.last_status.value,
                'error': 'Timeout',
                'duration': time.time() - start_time,
                'timestamp': time.time()
            }
        except Exception as e:
            self.last_status = HealthStatus.UNHEALTHY
            return {
                'name': self.name,
                'status': self.last_status.value,
                'error': str(e),
                'duration': time.time() - start_time,
                'timestamp': time.time()
            }
    
    async def _execute_check(self):
        """Execute the check function"""
        if asyncio.iscoroutinefunction(self.check_func):
            return await self.check_func()
        else:
            return self.check_func()

class HealthChecker:
    """Health checker for multiple services"""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        
    def add_check(self, health_check: HealthCheck):
        """Add a health check"""
        self.checks[health_check.name] = health_check
        logger.info(f"Added health check: {health_check.name}")
        
    def remove_check(self, check_name: str):
        """Remove a health check"""
        if check_name in self.checks:
            del self.checks[check_name]
            logger.info(f"Removed health check: {check_name}")
            
    async def check_all(self) -> Dict[str, Any]:
        """Perform all health checks"""
        results = {}
        
        # Execute all checks concurrently
        tasks = [
            check.perform_check() 
            for check in self.checks.values()
        ]
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        overall_status = HealthStatus.HEALTHY
        for result in check_results:
            if isinstance(result, Exception):
                continue
                
            results[result['name']] = result
            
            if result['status'] == HealthStatus.UNHEALTHY.value:
                overall_status = HealthStatus.UNHEALTHY
            elif result['status'] == HealthStatus.DEGRADED.value and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'checks': results,
            'timestamp': time.time()
        }

class ServiceHealthManager:
    """Manages health for an entire service"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.health_checker = HealthChecker()
        self.startup_time = time.time()
        
    def add_database_check(self, db_connection_func: Callable):
        """Add database connectivity check"""
        check = HealthCheck("database", db_connection_func)
        self.health_checker.add_check(check)
        
    def add_external_service_check(self, service_name: str, check_func: Callable):
        """Add external service dependency check"""
        check = HealthCheck(f"external_service_{service_name}", check_func)
        self.health_checker.add_check(check)
        
    async def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        health_results = await self.health_checker.check_all()
        
        return {
            'service': self.service_name,
            'uptime': time.time() - self.startup_time,
            'health': health_results,
            'version': '1.0.0'  # This could be dynamic
        }
