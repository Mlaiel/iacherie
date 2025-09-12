"""
Enterprise Health Check Manager for ML Services
DevOps + Backend Senior implementation with comprehensive health monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import time
import aiohttp
import socket
from abc import ABC, abstractmethod
import uuid
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class HealthCheckType(Enum):
    """Types of health checks"""
    HTTP = "http"
    TCP = "tcp"
    DATABASE = "database"
    QUEUE = "queue"
    CUSTOM = "custom"
    ML_MODEL = "ml_model"
    DEPENDENCY = "dependency"


class ServiceType(Enum):
    """Types of services"""
    API_GATEWAY = "api_gateway"
    MODEL_SERVING = "model_serving"
    DATA_PIPELINE = "data_pipeline"
    STORAGE = "storage"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    MONITORING = "monitoring"
    SECURITY = "security"


@dataclass
class HealthCheck:
    """Health check configuration"""
    check_id: str
    name: str
    service_name: str
    service_type: ServiceType
    check_type: HealthCheckType
    endpoint: Optional[str] = None
    interval: timedelta = field(default_factory=lambda: timedelta(seconds=30))
    timeout: timedelta = field(default_factory=lambda: timedelta(seconds=10))
    retry_count: int = 3
    retry_delay: timedelta = field(default_factory=lambda: timedelta(seconds=1))
    expected_status_codes: List[int] = field(default_factory=lambda: [200])
    custom_check_function: Optional[Callable] = None
    creator_impact: str = "medium"  # low, medium, high, critical
    
    
@dataclass
class HealthCheckResult:
    """Health check result"""
    check_id: str
    status: HealthStatus
    response_time: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None


@dataclass
class ServiceHealth:
    """Overall service health"""
    service_name: str
    service_type: ServiceType
    status: HealthStatus
    uptime_percentage: float
    avg_response_time: float
    last_check: datetime
    check_results: List[HealthCheckResult] = field(default_factory=list)
    creator_impact_assessment: str = "medium"


class HealthCheckManager:
    """Enterprise health check manager for ML services"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_results: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.service_health: Dict[str, ServiceHealth] = {}
        self.alert_handlers: List[Callable] = []
        self.running_checks: Dict[str, asyncio.Task] = {}
        
        # Creator-specific health priorities
        self.creator_service_priorities = {
            'musicians': {
                'audio_processing': 'critical',
                'model_serving': 'high',
                'collaboration_api': 'high',
                'streaming_service': 'critical'
            },
            'photographers': {
                'image_processing': 'critical',
                'storage_service': 'critical',
                'portfolio_api': 'high',
                'cdn_service': 'high'
            },
            'bloggers': {
                'content_generation': 'high',
                'seo_service': 'high',
                'publishing_api': 'medium',
                'analytics_service': 'medium'
            },
            'influencers': {
                'multi_platform_sync': 'critical',
                'analytics_service': 'critical',
                'scheduling_service': 'high',
                'engagement_tracker': 'high'
            },
            'comedians': {
                'video_processing': 'critical',
                'timing_analysis': 'high',
                'performance_api': 'medium',
                'venue_matching': 'medium'
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize health check manager"""
        try:
            logger.info("Initializing Health Check Manager...")
            
            # Setup default health checks
            await self._setup_default_health_checks()
            
            # Start health check monitoring
            await self._start_monitoring()
            
            # Setup alert system
            await self._setup_alert_system()
            
            logger.info("Health Check Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Health Check Manager: {e}")
            return False
    
    async def add_health_check(self, health_check: HealthCheck) -> bool:
        """Add new health check"""
        try:
            self.health_checks[health_check.check_id] = health_check
            
            # Start monitoring for this check
            task = asyncio.create_task(self._monitor_health_check(health_check))
            self.running_checks[health_check.check_id] = task
            
            logger.info(f"Added health check: {health_check.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add health check: {e}")
            return False
    
    async def remove_health_check(self, check_id: str) -> bool:
        """Remove health check"""
        try:
            if check_id in self.health_checks:
                # Stop monitoring task
                if check_id in self.running_checks:
                    self.running_checks[check_id].cancel()
                    del self.running_checks[check_id]
                
                # Remove from tracking
                del self.health_checks[check_id]
                if check_id in self.check_results:
                    del self.check_results[check_id]
                
                logger.info(f"Removed health check: {check_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove health check: {e}")
            return False
    
    async def get_service_health(self, service_name: Optional[str] = None) -> Dict[str, ServiceHealth]:
        """Get health status for services"""
        try:
            if service_name:
                return {service_name: self.service_health.get(service_name)}
            
            return self.service_health.copy()
            
        except Exception as e:
            logger.error(f"Failed to get service health: {e}")
            return {}
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        try:
            healthy_services = 0
            total_services = len(self.service_health)
            critical_issues = 0
            degraded_services = 0
            
            creator_impact = {
                'musicians': {'status': 'healthy', 'affected_services': []},
                'photographers': {'status': 'healthy', 'affected_services': []},
                'bloggers': {'status': 'healthy', 'affected_services': []},
                'influencers': {'status': 'healthy', 'affected_services': []},
                'comedians': {'status': 'healthy', 'affected_services': []}
            }
            
            for service_name, service_health in self.service_health.items():
                if service_health.status == HealthStatus.HEALTHY:
                    healthy_services += 1
                elif service_health.status == HealthStatus.UNHEALTHY:
                    critical_issues += 1
                    # Check creator impact
                    await self._assess_creator_impact(service_name, creator_impact)
                elif service_health.status == HealthStatus.DEGRADED:
                    degraded_services += 1
            
            overall_status = HealthStatus.HEALTHY
            if critical_issues > 0:
                overall_status = HealthStatus.UNHEALTHY
            elif degraded_services > 0:
                overall_status = HealthStatus.DEGRADED
            
            uptime_percentage = (healthy_services / total_services * 100) if total_services > 0 else 100
            
            return {
                'overall_status': overall_status.value,
                'uptime_percentage': uptime_percentage,
                'total_services': total_services,
                'healthy_services': healthy_services,
                'critical_issues': critical_issues,
                'degraded_services': degraded_services,
                'creator_impact': creator_impact,
                'last_updated': datetime.utcnow(),
                'response_time_avg': await self._calculate_avg_response_time()
            }
            
        except Exception as e:
            logger.error(f"Failed to get overall health: {e}")
            return {'overall_status': 'unknown', 'error': str(e)}
    
    async def force_health_check(self, check_id: str) -> HealthCheckResult:
        """Force immediate health check"""
        try:
            if check_id not in self.health_checks:
                raise ValueError(f"Health check {check_id} not found")
            
            health_check = self.health_checks[check_id]
            result = await self._perform_health_check(health_check)
            
            # Store result
            self.check_results[check_id].append(result)
            
            # Update service health
            await self._update_service_health(health_check.service_name)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to force health check: {e}")
            return HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNKNOWN,
                response_time=0.0,
                message="Check failed",
                error=str(e)
            )
    
    async def get_health_history(self, 
                               check_id: str,
                               time_period: Optional[timedelta] = None) -> List[HealthCheckResult]:
        """Get health check history"""
        try:
            if check_id not in self.check_results:
                return []
            
            results = list(self.check_results[check_id])
            
            if time_period:
                cutoff_time = datetime.utcnow() - time_period
                results = [r for r in results if r.timestamp >= cutoff_time]
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get health history: {e}")
            return []
    
    async def add_alert_handler(self, handler: Callable) -> bool:
        """Add alert handler for health status changes"""
        try:
            self.alert_handlers.append(handler)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert handler: {e}")
            return False
    
    async def _setup_default_health_checks(self):
        """Setup default health checks for core services"""
        
        # API Gateway health check
        api_check = HealthCheck(
            check_id="api_gateway_health",
            name="API Gateway Health",
            service_name="api_gateway",
            service_type=ServiceType.API_GATEWAY,
            check_type=HealthCheckType.HTTP,
            endpoint="/health",
            interval=timedelta(seconds=15),
            creator_impact="critical"
        )
        await self.add_health_check(api_check)
        
        # Model serving health check
        model_check = HealthCheck(
            check_id="model_serving_health",
            name="Model Serving Health",
            service_name="model_serving",
            service_type=ServiceType.MODEL_SERVING,
            check_type=HealthCheckType.ML_MODEL,
            interval=timedelta(seconds=30),
            creator_impact="critical"
        )
        await self.add_health_check(model_check)
        
        # Database health check
        db_check = HealthCheck(
            check_id="database_health",
            name="Database Health",
            service_name="database",
            service_type=ServiceType.STORAGE,
            check_type=HealthCheckType.DATABASE,
            interval=timedelta(seconds=20),
            creator_impact="critical"
        )
        await self.add_health_check(db_check)
        
        # Message queue health check
        queue_check = HealthCheck(
            check_id="message_queue_health",
            name="Message Queue Health",
            service_name="message_queue",
            service_type=ServiceType.MESSAGE_QUEUE,
            check_type=HealthCheckType.QUEUE,
            interval=timedelta(seconds=30),
            creator_impact="high"
        )
        await self.add_health_check(queue_check)
    
    async def _start_monitoring(self):
        """Start health check monitoring tasks"""
        for check_id, health_check in self.health_checks.items():
            if check_id not in self.running_checks:
                task = asyncio.create_task(self._monitor_health_check(health_check))
                self.running_checks[check_id] = task
    
    async def _setup_alert_system(self):
        """Setup alert system"""
        # Default alert handler
        async def default_alert_handler(service_name: str, 
                                      old_status: HealthStatus, 
                                      new_status: HealthStatus):
            logger.warning(f"Service {service_name} status changed: {old_status.value} -> {new_status.value}")
        
        await self.add_alert_handler(default_alert_handler)
    
    async def _monitor_health_check(self, health_check: HealthCheck):
        """Monitor specific health check continuously"""
        while True:
            try:
                # Perform health check
                result = await self._perform_health_check(health_check)
                
                # Store result
                self.check_results[health_check.check_id].append(result)
                
                # Update service health
                await self._update_service_health(health_check.service_name)
                
                # Wait for next check
                await asyncio.sleep(health_check.interval.total_seconds())
                
            except asyncio.CancelledError:
                logger.info(f"Health check monitoring cancelled: {health_check.name}")
                break
            except Exception as e:
                logger.error(f"Health check monitoring error: {e}")
                await asyncio.sleep(health_check.interval.total_seconds())
    
    async def _perform_health_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform individual health check"""
        start_time = time.time()
        
        try:
            if health_check.check_type == HealthCheckType.HTTP:
                result = await self._perform_http_check(health_check)
            elif health_check.check_type == HealthCheckType.TCP:
                result = await self._perform_tcp_check(health_check)
            elif health_check.check_type == HealthCheckType.DATABASE:
                result = await self._perform_database_check(health_check)
            elif health_check.check_type == HealthCheckType.QUEUE:
                result = await self._perform_queue_check(health_check)
            elif health_check.check_type == HealthCheckType.ML_MODEL:
                result = await self._perform_ml_model_check(health_check)
            elif health_check.check_type == HealthCheckType.CUSTOM:
                result = await self._perform_custom_check(health_check)
            else:
                result = HealthCheckResult(
                    check_id=health_check.check_id,
                    status=HealthStatus.UNKNOWN,
                    response_time=0.0,
                    message="Unknown check type"
                )
            
        except Exception as e:
            result = HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message=f"Health check failed: {str(e)}",
                error=str(e)
            )
        
        return result
    
    async def _perform_http_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform HTTP health check"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    health_check.endpoint,
                    timeout=aiohttp.ClientTimeout(total=health_check.timeout.total_seconds())
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status in health_check.expected_status_codes:
                        status = HealthStatus.HEALTHY
                        message = f"HTTP check successful (status: {response.status})"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"Unexpected status code: {response.status}"
                    
                    return HealthCheckResult(
                        check_id=health_check.check_id,
                        status=status,
                        response_time=response_time,
                        message=message,
                        details={'status_code': response.status}
                    )
                    
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message="HTTP check timeout",
                error="timeout"
            )
    
    async def _perform_tcp_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform TCP health check"""
        start_time = time.time()
        
        try:
            # Parse endpoint for host and port
            host, port = health_check.endpoint.split(':')
            port = int(port)
            
            # Attempt TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=health_check.timeout.total_seconds()
            )
            
            writer.close()
            await writer.wait_closed()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="TCP connection successful"
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message="TCP connection failed",
                error=str(e)
            )
    
    async def _perform_database_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform database health check"""
        start_time = time.time()
        
        try:
            # Simulate database check
            # In real implementation, this would test actual database connection
            await asyncio.sleep(0.1)  # Simulate query time
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="Database connection successful",
                details={'connection_pool_size': 10, 'active_connections': 5}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message="Database check failed",
                error=str(e)
            )
    
    async def _perform_queue_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform message queue health check"""
        start_time = time.time()
        
        try:
            # Simulate queue check
            await asyncio.sleep(0.05)  # Simulate queue status check
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="Message queue healthy",
                details={'queue_depth': 25, 'consumers': 3}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message="Queue check failed",
                error=str(e)
            )
    
    async def _perform_ml_model_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform ML model health check"""
        start_time = time.time()
        
        try:
            # Simulate model health check (inference test)
            await asyncio.sleep(0.2)  # Simulate inference time
            
            response_time = time.time() - start_time
            
            # Check if response time is acceptable
            if response_time > 1.0:  # 1 second threshold
                status = HealthStatus.DEGRADED
                message = f"Model response time degraded: {response_time:.2f}s"
            else:
                status = HealthStatus.HEALTHY
                message = f"Model inference successful: {response_time:.2f}s"
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=status,
                response_time=response_time,
                message=message,
                details={'model_version': '1.2.0', 'memory_usage': '2.5GB'}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message="Model health check failed",
                error=str(e)
            )
    
    async def _perform_custom_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Perform custom health check"""
        start_time = time.time()
        
        try:
            if health_check.custom_check_function:
                result = await health_check.custom_check_function()
                response_time = time.time() - start_time
                
                return HealthCheckResult(
                    check_id=health_check.check_id,
                    status=result.get('status', HealthStatus.UNKNOWN),
                    response_time=response_time,
                    message=result.get('message', 'Custom check completed'),
                    details=result.get('details', {})
                )
            else:
                return HealthCheckResult(
                    check_id=health_check.check_id,
                    status=HealthStatus.UNKNOWN,
                    response_time=0.0,
                    message="No custom check function defined"
                )
                
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                message="Custom check failed",
                error=str(e)
            )
    
    async def _update_service_health(self, service_name: str):
        """Update overall service health based on checks"""
        try:
            service_checks = [
                check for check in self.health_checks.values()
                if check.service_name == service_name
            ]
            
            if not service_checks:
                return
            
            # Get recent results for all checks
            all_results = []
            for check in service_checks:
                if check.check_id in self.check_results:
                    recent_results = list(self.check_results[check.check_id])[-10:]  # Last 10 results
                    all_results.extend(recent_results)
            
            if not all_results:
                return
            
            # Calculate overall status
            healthy_count = sum(1 for r in all_results if r.status == HealthStatus.HEALTHY)
            total_count = len(all_results)
            uptime_percentage = (healthy_count / total_count) * 100
            
            # Determine overall status
            if uptime_percentage >= 95:
                overall_status = HealthStatus.HEALTHY
            elif uptime_percentage >= 80:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.UNHEALTHY
            
            # Calculate average response time
            avg_response_time = statistics.mean([r.response_time for r in all_results])
            
            # Update service health
            old_status = None
            if service_name in self.service_health:
                old_status = self.service_health[service_name].status
            
            service_type = service_checks[0].service_type
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                service_type=service_type,
                status=overall_status,
                uptime_percentage=uptime_percentage,
                avg_response_time=avg_response_time,
                last_check=datetime.utcnow(),
                check_results=all_results[-5:],  # Keep last 5 results
                creator_impact_assessment=await self._get_creator_impact_assessment(service_name)
            )
            
            # Trigger alerts if status changed
            if old_status and old_status != overall_status:
                await self._trigger_alerts(service_name, old_status, overall_status)
                
        except Exception as e:
            logger.error(f"Failed to update service health: {e}")
    
    async def _get_creator_impact_assessment(self, service_name: str) -> str:
        """Assess impact of service health on creators"""
        impact_levels = []
        
        for creator_type, services in self.creator_service_priorities.items():
            if service_name in services:
                impact_levels.append(services[service_name])
        
        if 'critical' in impact_levels:
            return 'critical'
        elif 'high' in impact_levels:
            return 'high'
        elif 'medium' in impact_levels:
            return 'medium'
        else:
            return 'low'
    
    async def _assess_creator_impact(self, service_name: str, creator_impact: Dict[str, Any]):
        """Assess impact on specific creator types"""
        for creator_type, services in self.creator_service_priorities.items():
            if service_name in services:
                priority = services[service_name]
                if priority in ['critical', 'high']:
                    creator_impact[creator_type]['status'] = 'affected'
                    creator_impact[creator_type]['affected_services'].append(service_name)
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time across all services"""
        try:
            all_times = []
            for results in self.check_results.values():
                recent_results = list(results)[-10:]  # Last 10 results
                all_times.extend([r.response_time for r in recent_results])
            
            return statistics.mean(all_times) if all_times else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate average response time: {e}")
            return 0.0
    
    async def _trigger_alerts(self, 
                            service_name: str,
                            old_status: HealthStatus,
                            new_status: HealthStatus):
        """Trigger alerts for status changes"""
        try:
            for handler in self.alert_handlers:
                asyncio.create_task(handler(service_name, old_status, new_status))
                
        except Exception as e:
            logger.error(f"Failed to trigger alerts: {e}")


# Creator-specific health monitoring
class CreatorHealthMonitor:
    """Creator-specific health monitoring"""
    
    @staticmethod
    async def setup_musician_monitoring(health_manager: HealthCheckManager) -> bool:
        """Setup health monitoring optimized for musicians"""
        
        # Audio processing service check
        audio_check = HealthCheck(
            check_id="audio_processing_health",
            name="Audio Processing Health",
            service_name="audio_processing",
            service_type=ServiceType.MODEL_SERVING,
            check_type=HealthCheckType.ML_MODEL,
            interval=timedelta(seconds=15),
            creator_impact="critical"
        )
        
        return await health_manager.add_health_check(audio_check)
    
    @staticmethod
    async def setup_photographer_monitoring(health_manager: HealthCheckManager) -> bool:
        """Setup health monitoring optimized for photographers"""
        
        # Image processing service check
        image_check = HealthCheck(
            check_id="image_processing_health",
            name="Image Processing Health",
            service_name="image_processing",
            service_type=ServiceType.MODEL_SERVING,
            check_type=HealthCheckType.ML_MODEL,
            interval=timedelta(seconds=20),
            creator_impact="critical"
        )
        
        return await health_manager.add_health_check(image_check)


# Example usage and testing
async def main():
    """Example usage of Health Check Manager"""
    manager = HealthCheckManager()
    
    # Initialize
    await manager.initialize()
    
    # Wait a bit for some checks to run
    await asyncio.sleep(5)
    
    # Get overall health
    overall = await manager.get_overall_health()
    print(f"Overall Health: {json.dumps(overall, indent=2, default=str)}")
    
    # Get service health
    services = await manager.get_service_health()
    print(f"Service Health: {json.dumps(services, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())