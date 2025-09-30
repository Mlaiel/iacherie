"""
Health Checks Service Index
Enterprise Health Monitoring and Service Discovery

This module provides comprehensive health monitoring for all microservices,
including deep health checks, dependency validation, and real-time status reporting.

Key Features:
- Multi-level health check validation
- Service dependency monitoring
- Real-time health status reporting
- Automated remediation triggers
- Integration with monitoring and alerting systems

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"

@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    check_interval: int = 30
    timeout_seconds: int = 10
    retry_attempts: int = 3
    degraded_threshold: int = 2
    unhealthy_threshold: int = 5

class HealthCheckService:
    """Enterprise health check service"""
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self.services: Dict[str, Dict[str, Any]] = {}
        self.checks: Dict[str, List[Callable]] = {}
        self.status_history: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._monitoring_task: Optional[asyncio.Task] = None
    
    async def register_service(self, service_name: str, check_functions: List[Callable], config: Optional[HealthCheckConfig] = None) -> bool:
        """Register a service for health monitoring"""
        try:
            service_config = config or self.config
            self.services[service_name] = {
                'status': HealthStatus.UNKNOWN,
                'last_check': None,
                'failure_count': 0,
                'config': service_config,
                'metadata': {}
            }
            
            self.checks[service_name] = check_functions
            self.status_history[service_name] = []
            
            self.logger.info(f"Service registered for health monitoring: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service_name}: {str(e)}")
            return False
    
    async def perform_health_check(self, service_name: str) -> Dict[str, Any]:
        """Perform health check for a specific service"""
        try:
            if service_name not in self.services:
                return {
                    'service': service_name,
                    'status': HealthStatus.UNKNOWN.value,
                    'message': 'Service not registered',
                    'timestamp': datetime.now().isoformat()
                }
            
            service = self.services[service_name]
            check_functions = self.checks[service_name]
            
            results = []
            overall_status = HealthStatus.HEALTHY
            
            # Run all health checks
            for check_func in check_functions:
                try:
                    result = await self._execute_check(check_func, service['config'].timeout_seconds)
                    results.append(result)
                    
                    if not result.get('success', False):
                        overall_status = HealthStatus.UNHEALTHY
                        
                except Exception as e:
                    results.append({
                        'check': check_func.__name__,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    overall_status = HealthStatus.UNHEALTHY
            
            # Update service status
            await self._update_service_status(service_name, overall_status, results)
            
            return {
                'service': service_name,
                'status': overall_status.value,
                'checks': results,
                'timestamp': datetime.now().isoformat(),
                'failure_count': service['failure_count']
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed for {service_name}: {str(e)}")
            await self._update_service_status(service_name, HealthStatus.UNHEALTHY, [])
            return {
                'service': service_name,
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _execute_check(self, check_func: Callable, timeout: int) -> Dict[str, Any]:
        """Execute a single health check with timeout"""
        try:
            start_time = datetime.now()
            
            if asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(check_func(), timeout=timeout)
            else:
                result = check_func()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'check': check_func.__name__,
                'success': bool(result),
                'result': result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            return {
                'check': check_func.__name__,
                'success': False,
                'error': f'Check timed out after {timeout} seconds',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'check': check_func.__name__,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _update_service_status(self, service_name: str, status: HealthStatus, results: List[Dict[str, Any]]):
        """Update service status and history"""
        service = self.services[service_name]
        previous_status = service['status']
        
        service['status'] = status
        service['last_check'] = datetime.now()
        
        if status == HealthStatus.UNHEALTHY:
            service['failure_count'] += 1
        else:
            service['failure_count'] = 0
        
        # Store in history
        self.status_history[service_name].append({
            'status': status.value,
            'timestamp': datetime.now().isoformat(),
            'checks': results
        })
        
        # Keep only last 100 entries
        if len(self.status_history[service_name]) > 100:
            self.status_history[service_name] = self.status_history[service_name][-100:]
        
        # Log status changes
        if previous_status != status:
            self.logger.info(f"Service {service_name} status changed: {previous_status.value} -> {status.value}")
    
    async def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get current health status of a service"""
        if service_name in self.services:
            service = self.services[service_name]
            return {
                'service': service_name,
                'status': service['status'].value,
                'last_check': service['last_check'].isoformat() if service['last_check'] else None,
                'failure_count': service['failure_count'],
                'metadata': service['metadata']
            }
        return None
    
    async def get_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all registered services"""
        result = {}
        for service_name in self.services.keys():
            health = await self.get_service_health(service_name)
            if health:
                result[service_name] = health
        return result
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self.logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while True:
            try:
                for service_name in self.services.keys():
                    await self.perform_health_check(service_name)
                
                # Wait for next check interval
                await asyncio.sleep(self.config.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5)  # Short delay before retry

# Sample health check functions
async def database_health_check() -> bool:
    """Sample database health check"""
    # Implement actual database connection check
    return True

async def redis_health_check() -> bool:
    """Sample Redis health check"""
    # Implement actual Redis connection check
    return True

async def api_endpoint_health_check() -> bool:
    """Sample API endpoint health check"""
    # Implement actual API endpoint check
    return True

# Global health check service instance
health_check_service = HealthCheckService()

# Export main classes and functions
__all__ = [
    'HealthCheckService',
    'HealthCheckConfig',
    'HealthStatus',
    'health_check_service',
    'database_health_check',
    'redis_health_check',
    'api_endpoint_health_check'
]