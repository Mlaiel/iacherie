"""Health Validator - Deployment Automation

Comprehensive health validation system for the IA Influencer Agent platform,
providing real-time health monitoring, validation, and diagnostics across
all system components during deployment and runtime.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import aiohttp
import psutil
from concurrent.futures import ThreadPoolExecutor
import time

from ..core.base import BaseComponent
from ..monitoring.metrics_collector import MetricsCollector
from ..kubernetes.pod_manager import PodManager
from ..database.connection_manager import ConnectionManager
from ..cache.redis_manager import RedisManager
from ..queue.message_queue_manager import MessageQueueManager


class HealthStatus(Enum):
    """Health status types"""    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    CRITICAL = "critical"


class ComponentType(Enum):
    """Component types for health checking"""    POD = "pod"
    SERVICE = "service"
    ENDPOINT = "endpoint"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"
    AI_MODEL = "ai_model"
    EXTERNAL_API = "external_api"
    NETWORK = "network"


@dataclass
class HealthCheck:
    """Health check definition"""    name: str
    component_type: ComponentType
    check_function: Callable
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    critical: bool = False
    expected_response_time: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthResult:
    """Health check result"""    name: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None


class HealthValidator(BaseComponent):
    """    Enterprise-grade health validation system.
    
    Provides comprehensive health monitoring and validation for all components
    of the IA Influencer Agent platform including pods, services, databases,
    AI models, and external dependencies.
    """    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core managers
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        self.pod_manager = PodManager(config.get('kubernetes', {}))
        self.db_manager = ConnectionManager(config.get('database', {}))
        self.redis_manager = RedisManager(config.get('redis', {}))
        self.queue_manager = MessageQueueManager(config.get('message_queue', {}))
        
        # HTTP client for endpoint checks
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.get('http_timeout', 30))
        )
        
        # Thread pool for CPU-intensive checks
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))
        
        # Health check registry
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_history: Dict[str, List[HealthResult]] = {}
        
        # Validation thresholds
        self.thresholds = config.get('thresholds', {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2.0,
            'error_rate': 5.0,
            'availability': 99.0
        })
        
        # Initialize health checks
        self._initialize_health_checks()

    def _initialize_health_checks(self):
        """Initialize built-in health checks"""        
        # Pod health checks
        self.register_health_check(HealthCheck(
            name="ai_agent_pods",
            component_type=ComponentType.POD,
            check_function=self._check_ai_agent_pods,
            critical=True,
            tags={"service": "ai_agent", "tier": "core"}
        ))
        
        self.register_health_check(HealthCheck(
            name="content_protection_pods",
            component_type=ComponentType.POD,
            check_function=self._check_content_protection_pods,
            critical=True,
            tags={"service": "content_protection", "tier": "core"}
        ))
        
        self.register_health_check(HealthCheck(
            name="fingerprinting_pods",
            component_type=ComponentType.POD,
            check_function=self._check_fingerprinting_pods,
            critical=True,
            tags={"service": "fingerprinting", "tier": "processing"}
        ))
        
        self.register_health_check(HealthCheck(
            name="monetization_pods",
            component_type=ComponentType.POD,
            check_function=self._check_monetization_pods,
            critical=False,
            tags={"service": "monetization", "tier": "business"}
        ))
        
        self.register_health_check(HealthCheck(
            name="crawler_pods",
            component_type=ComponentType.POD,
            check_function=self._check_crawler_pods,
            critical=False,
            tags={"service": "crawler", "tier": "processing"}
        ))
        
        self.register_health_check(HealthCheck(
            name="api_gateway_pods",
            component_type=ComponentType.POD,
            check_function=self._check_api_gateway_pods,
            critical=True,
            tags={"service": "api_gateway", "tier": "frontend"}
        ))
        
        # Service endpoint checks
        self.register_health_check(HealthCheck(
            name="ai_agent_endpoint",
            component_type=ComponentType.ENDPOINT,
            check_function=self._check_ai_agent_endpoint,
            critical=True,
            expected_response_time=0.5,
            dependencies=["ai_agent_pods"]
        ))
        
        self.register_health_check(HealthCheck(
            name="content_protection_endpoint",
            component_type=ComponentType.ENDPOINT,
            check_function=self._check_content_protection_endpoint,
            critical=True,
            expected_response_time=1.0,
            dependencies=["content_protection_pods"]
        ))
        
        self.register_health_check(HealthCheck(
            name="api_gateway_endpoint",
            component_type=ComponentType.ENDPOINT,
            check_function=self._check_api_gateway_endpoint,
            critical=True,
            expected_response_time=0.3,
            dependencies=["api_gateway_pods"]
        ))
        
        # Database health checks
        self.register_health_check(HealthCheck(
            name="postgresql_primary",
            component_type=ComponentType.DATABASE,
            check_function=self._check_postgresql_primary,
            critical=True,
            expected_response_time=0.1
        ))
        
        self.register_health_check(HealthCheck(
            name="postgresql_replicas",
            component_type=ComponentType.DATABASE,
            check_function=self._check_postgresql_replicas,
            critical=False,
            dependencies=["postgresql_primary"]
        ))
        
        # Cache health checks
        self.register_health_check(HealthCheck(
            name="redis_primary",
            component_type=ComponentType.CACHE,
            check_function=self._check_redis_primary,
            critical=True,
            expected_response_time=0.05
        ))
        
        self.register_health_check(HealthCheck(
            name="redis_cluster",
            component_type=ComponentType.CACHE,
            check_function=self._check_redis_cluster,
            critical=False,
            dependencies=["redis_primary"]
        ))
        
        # Message queue health checks
        self.register_health_check(HealthCheck(
            name="celery_broker",
            component_type=ComponentType.MESSAGE_QUEUE,
            check_function=self._check_celery_broker,
            critical=True
        ))
        
        # Content Protection specialized checks
        self.register_health_check(HealthCheck(
            name="fingerprinting_accuracy",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_fingerprinting_accuracy,
            critical=True,
            timeout=120,
            expected_response_time=5.0,
            dependencies=["fingerprinting_pods"]
        ))
        
        self.register_health_check(HealthCheck(
            name="vector_database_performance",
            component_type=ComponentType.DATABASE,
            check_function=self._check_vector_database_performance,
            critical=True,
            timeout=30,
            expected_response_time=1.0
        ))
        
        self.register_health_check(HealthCheck(
            name="crawling_infrastructure",
            component_type=ComponentType.SERVICE,
            check_function=self._check_crawling_infrastructure,
            critical=False,
            timeout=60,
            dependencies=["crawler_pods"]
        ))
        
        # Monetization system checks
        self.register_health_check(HealthCheck(
            name="payment_processing_flow",
            component_type=ComponentType.SERVICE,
            check_function=self._check_payment_processing_flow,
            critical=True,
            timeout=45,
            expected_response_time=2.0,
            dependencies=["monetization_pods"]
        ))
        
        self.register_health_check(HealthCheck(
            name="revenue_tracking_accuracy",
            component_type=ComponentType.SERVICE,
            check_function=self._check_revenue_tracking_accuracy,
            critical=True,
            timeout=60,
            dependencies=["revenue_analytics_pods"]
        ))
        
        self.register_health_check(HealthCheck(
            name="collaboration_matching_engine",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_collaboration_matching_engine,
            critical=False,
            timeout=90,
            expected_response_time=3.0
        ))
        
        # Audio processing specialized checks
        self.register_health_check(HealthCheck(
            name="audio_processing_pipeline",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_audio_processing_pipeline,
            critical=True,
            timeout=120,
            expected_response_time=10.0
        ))
        
        self.register_health_check(HealthCheck(
            name="music_generation_quality",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_music_generation_quality,
            critical=False,
            timeout=180,
            expected_response_time=30.0
        ))
        
        self.register_health_check(HealthCheck(
            name="audio_fingerprinting_speed",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_audio_fingerprinting_speed,
            critical=True,
            timeout=60,
            expected_response_time=5.0
        ))
        
        # Platform integration checks
        self.register_health_check(HealthCheck(
            name="spotify_api_integration",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_spotify_api_integration,
            critical=False,
            timeout=15
        ))
        
        self.register_health_check(HealthCheck(
            name="youtube_api_integration",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_youtube_api_integration,
            critical=False,
            timeout=15
        ))
        
        self.register_health_check(HealthCheck(
            name="instagram_api_integration",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_instagram_api_integration,
            critical=False,
            timeout=15
        ))
        
        self.register_health_check(HealthCheck(
            name="tiktok_api_integration",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_tiktok_api_integration,
            critical=False,
            timeout=15
        ))
        
        self.register_health_check(HealthCheck(
            name="celery_workers",
            component_type=ComponentType.MESSAGE_QUEUE,
            check_function=self._check_celery_workers,
            critical=False,
            dependencies=["celery_broker"]
        ))
        
        # AI model health checks
        self.register_health_check(HealthCheck(
            name="text_generation_model",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_text_generation_model,
            critical=True,
            timeout=60,
            expected_response_time=2.0
        ))
        
        self.register_health_check(HealthCheck(
            name="audio_analysis_model",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_audio_analysis_model,
            critical=True,
            timeout=60,
            expected_response_time=5.0
        ))
        
        self.register_health_check(HealthCheck(
            name="image_analysis_model",
            component_type=ComponentType.AI_MODEL,
            check_function=self._check_image_analysis_model,
            critical=True,
            timeout=60,
            expected_response_time=3.0
        ))
        
        # External API health checks
        self.register_health_check(HealthCheck(
            name="openai_api",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_openai_api,
            critical=False,
            timeout=10
        ))
        
        self.register_health_check(HealthCheck(
            name="stripe_api",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_stripe_api,
            critical=False,
            timeout=10
        ))
        
        self.register_health_check(HealthCheck(
            name="youtube_api",
            component_type=ComponentType.EXTERNAL_API,
            check_function=self._check_youtube_api,
            critical=False,
            timeout=10
        ))

    def register_health_check(self, health_check: HealthCheck):
        """Register a new health check"""        self.health_checks[health_check.name] = health_check
        self.health_history[health_check.name] = []

    async def validate_environment_readiness(
        self,
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate that the environment is ready for deployment.
        
        Args:
            environment: Environment to validate
            context: Validation context
            
        Returns:
            Validation results
        """        self.logger.info(f"Validating environment readiness: {environment}")
        
        validation_results = {
            'environment': environment,
            'ready': True,
            'timestamp': datetime.utcnow(),
            'checks': {},
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        # Define environment readiness checks
        readiness_checks = [
            'postgresql_primary',
            'redis_primary',
            'celery_broker'
        ]
        
        # Execute readiness checks
        for check_name in readiness_checks:
            if check_name in self.health_checks:
                try:
                    result = await self._execute_health_check(check_name)
                    validation_results['checks'][check_name] = result
                    
                    if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                        validation_results['ready'] = False
                        validation_results['errors'].append(
                            f"{check_name}: {result.message}"
                        )
                    elif result.status == HealthStatus.DEGRADED:
                        validation_results['warnings'].append(
                            f"{check_name}: {result.message}"
                        )
                        
                except Exception as e:
                    validation_results['ready'] = False
                    validation_results['errors'].append(
                        f"{check_name}: Health check failed - {str(e)}"
                    )
        
        # Generate summary
        validation_results['summary'] = {
            'total_checks': len(readiness_checks),
            'passed': sum(1 for r in validation_results['checks'].values() 
                         if r.status == HealthStatus.HEALTHY),
            'failed': sum(1 for r in validation_results['checks'].values() 
                         if r.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]),
            'degraded': sum(1 for r in validation_results['checks'].values() 
                           if r.status == HealthStatus.DEGRADED)
        }
        
        return validation_results

    async def validate_services(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate health of deployed services.
        
        Args:
            services: List of services to validate
            environment: Environment to validate
            context: Validation context
            
        Returns:
            Service validation results
        """        self.logger.info(f"Validating {len(services)} services in {environment}")
        
        validation_results = {
            'services': services,
            'environment': environment,
            'healthy': True,
            'timestamp': datetime.utcnow(),
            'service_results': {},
            'overall_health': {},
            'errors': []
        }
        
        # Map services to health checks
        service_check_mapping = {
            'ai_agent': ['ai_agent_pods', 'ai_agent_endpoint'],
            'content_protection': ['content_protection_pods', 'content_protection_endpoint'],
            'fingerprinting': ['fingerprinting_pods'],
            'monetization': ['monetization_pods'],
            'crawler': ['crawler_pods'],
            'api_gateway': ['api_gateway_pods', 'api_gateway_endpoint']
        }
        
        # Execute health checks for each service
        for service in services:
            service_checks = service_check_mapping.get(service, [])
            service_result = {
                'healthy': True,
                'checks': {},
                'errors': []
            }
            
            for check_name in service_checks:
                if check_name in self.health_checks:
                    try:
                        result = await self._execute_health_check(check_name)
                        service_result['checks'][check_name] = result
                        
                        if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                            service_result['healthy'] = False
                            validation_results['healthy'] = False
                            service_result['errors'].append(result.message)
                            
                    except Exception as e:
                        service_result['healthy'] = False
                        validation_results['healthy'] = False
                        service_result['errors'].append(f"{check_name}: {str(e)}")
            
            validation_results['service_results'][service] = service_result
        
        # Calculate overall health metrics
        validation_results['overall_health'] = await self._calculate_overall_health(
            validation_results['service_results']
        )
        
        return validation_results

    async def validate_performance(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate performance metrics of services.
        
        Args:
            services: List of services to validate
            environment: Environment to validate
            context: Validation context
            
        Returns:
            Performance validation results
        """        self.logger.info(f"Validating performance for {len(services)} services")
        
        performance_results = {
            'services': services,
            'environment': environment,
            'acceptable': True,
            'timestamp': datetime.utcnow(),
            'metrics': {},
            'thresholds': self.thresholds,
            'violations': []
        }
        
        # Collect performance metrics for each service
        for service in services:
            try:
                service_metrics = await self._collect_service_performance_metrics(
                    service, environment
                )
                performance_results['metrics'][service] = service_metrics
                
                # Check against thresholds
                violations = self._check_performance_thresholds(service, service_metrics)
                if violations:
                    performance_results['acceptable'] = False
                    performance_results['violations'].extend(violations)
                    
            except Exception as e:
                self.logger.error(f"Failed to collect metrics for {service}: {str(e)}")
                performance_results['acceptable'] = False
                performance_results['violations'].append(
                    f"{service}: Metrics collection failed - {str(e)}"
                )
        
        return performance_results

    async def validate_security(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate security configuration of services.
        
        Args:
            services: List of services to validate
            environment: Environment to validate
            context: Validation context
            
        Returns:
            Security validation results
        """        self.logger.info(f"Validating security for {len(services)} services")
        
        security_results = {
            'services': services,
            'environment': environment,
            'secure': True,
            'timestamp': datetime.utcnow(),
            'security_checks': {},
            'vulnerabilities': [],
            'recommendations': []
        }
        
        # Security checks for each service
        for service in services:
            try:
                service_security = await self._validate_service_security(service, environment)
                security_results['security_checks'][service] = service_security
                
                if not service_security['secure']:
                    security_results['secure'] = False
                    security_results['vulnerabilities'].extend(
                        service_security.get('vulnerabilities', [])
                    )
                    
                security_results['recommendations'].extend(
                    service_security.get('recommendations', [])
                )
                
            except Exception as e:
                self.logger.error(f"Security validation failed for {service}: {str(e)}")
                security_results['secure'] = False
                security_results['vulnerabilities'].append(
                    f"{service}: Security validation failed - {str(e)}"
                )
        
        return security_results

    async def _execute_health_check(self, check_name: str) -> HealthResult:
        """Execute a single health check"""        health_check = self.health_checks[check_name]
        start_time = time.time()
        
        for attempt in range(health_check.retry_attempts):
            try:
                # Execute the health check function
                result = await asyncio.wait_for(
                    health_check.check_function(),
                    timeout=health_check.timeout
                )
                
                response_time = time.time() - start_time
                
                # Determine health status based on response time and result
                if isinstance(result, bool):
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "Check passed" if result else "Check failed"
                    details = {}
                elif isinstance(result, dict):
                    status = result.get('status', HealthStatus.UNKNOWN)
                    message = result.get('message', 'No message')
                    details = result.get('details', {})
                else:
                    status = HealthStatus.HEALTHY
                    message = str(result)
                    details = {}
                
                # Check response time threshold
                if response_time > health_check.expected_response_time:
                    if status == HealthStatus.HEALTHY:
                        status = HealthStatus.DEGRADED
                        message += f" (slow response: {response_time:.2f}s)"
                
                health_result = HealthResult(
                    name=check_name,
                    status=status,
                    message=message,
                    response_time=response_time,
                    timestamp=datetime.utcnow(),
                    details=details
                )
                
                # Store in history
                self.health_history[check_name].append(health_result)
                if len(self.health_history[check_name]) > 100:  # Keep last 100 results
                    self.health_history[check_name].pop(0)
                
                return health_result
                
            except asyncio.TimeoutError:
                if attempt < health_check.retry_attempts - 1:
                    await asyncio.sleep(health_check.retry_delay)
                    continue
                
                return HealthResult(
                    name=check_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Timeout after {health_check.timeout}s",
                    response_time=time.time() - start_time,
                    timestamp=datetime.utcnow(),
                    error="Timeout"
                )
                
            except Exception as e:
                if attempt < health_check.retry_attempts - 1:
                    await asyncio.sleep(health_check.retry_delay)
                    continue
                
                return HealthResult(
                    name=check_name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    response_time=time.time() - start_time,
                    timestamp=datetime.utcnow(),
                    error=str(e)
                )

    # Health check implementations
    async def _check_ai_agent_pods(self) -> Dict[str, Any]:
        """Check AI agent pod health"""        pods = await self.pod_manager.get_pods_by_label("app=ia-influencer-ai-agent")
        
        if not pods:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No AI agent pods found',
                'details': {'pod_count': 0}
            }
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        if len(healthy_pods) == 0:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No healthy AI agent pods',
                'details': {'pod_count': len(pods), 'healthy_count': 0}
            }
        elif len(healthy_pods) < len(pods):
            return {
                'status': HealthStatus.DEGRADED,
                'message': f'{len(healthy_pods)}/{len(pods)} AI agent pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }
        else:
            return {
                'status': HealthStatus.HEALTHY,
                'message': f'All {len(pods)} AI agent pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }

    async def _check_content_protection_pods(self) -> Dict[str, Any]:
        """Check content protection pod health"""        pods = await self.pod_manager.get_pods_by_label("app=ia-influencer-content-protection")
        
        if not pods:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No content protection pods found',
                'details': {'pod_count': 0}
            }
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        if len(healthy_pods) == 0:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No healthy content protection pods',
                'details': {'pod_count': len(pods), 'healthy_count': 0}
            }
        elif len(healthy_pods) < len(pods):
            return {
                'status': HealthStatus.DEGRADED,
                'message': f'{len(healthy_pods)}/{len(pods)} content protection pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }
        else:
            return {
                'status': HealthStatus.HEALTHY,
                'message': f'All {len(pods)} content protection pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }

    async def _check_fingerprinting_pods(self) -> Dict[str, Any]:
        """Check fingerprinting pod health"""        pods = await self.pod_manager.get_pods_by_label("app=ia-influencer-fingerprinting")
        
        if not pods:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No fingerprinting pods found',
                'details': {'pod_count': 0}
            }
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        if len(healthy_pods) == 0:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No healthy fingerprinting pods',
                'details': {'pod_count': len(pods), 'healthy_count': 0}
            }
        elif len(healthy_pods) < len(pods):
            return {
                'status': HealthStatus.DEGRADED,
                'message': f'{len(healthy_pods)}/{len(pods)} fingerprinting pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }
        else:
            return {
                'status': HealthStatus.HEALTHY,
                'message': f'All {len(pods)} fingerprinting pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }

    async def _check_monetization_pods(self) -> Dict[str, Any]:
        """Check monetization pod health"""        pods = await self.pod_manager.get_pods_by_label("app=ia-influencer-monetization")
        
        if not pods:
            return {
                'status': HealthStatus.DEGRADED,
                'message': 'No monetization pods found',
                'details': {'pod_count': 0}
            }
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        if len(healthy_pods) == 0:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': 'No healthy monetization pods',
                'details': {'pod_count': len(pods), 'healthy_count': 0}
            }
        elif len(healthy_pods) < len(pods):
            return {
                'status': HealthStatus.DEGRADED,
                'message': f'{len(healthy_pods)}/{len(pods)} monetization pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }
        else:
            return {
                'status': HealthStatus.HEALTHY,
                'message': f'All {len(pods)} monetization pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }

    async def _check_crawler_pods(self) -> Dict[str, Any]:
        """Check crawler pod health"""        pods = await self.pod_manager.get_pods_by_label("app=ia-influencer-crawler")
        
        if not pods:
            return {
                'status': HealthStatus.DEGRADED,
                'message': 'No crawler pods found',
                'details': {'pod_count': 0}
            }
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        if len(healthy_pods) == 0:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': 'No healthy crawler pods',
                'details': {'pod_count': len(pods), 'healthy_count': 0}
            }
        elif len(healthy_pods) < len(pods):
            return {
                'status': HealthStatus.DEGRADED,
                'message': f'{len(healthy_pods)}/{len(pods)} crawler pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }
        else:
            return {
                'status': HealthStatus.HEALTHY,
                'message': f'All {len(pods)} crawler pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }

    async def _check_api_gateway_pods(self) -> Dict[str, Any]:
        """Check API gateway pod health"""        pods = await self.pod_manager.get_pods_by_label("app=ia-influencer-api-gateway")
        
        if not pods:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No API gateway pods found',
                'details': {'pod_count': 0}
            }
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        if len(healthy_pods) == 0:
            return {
                'status': HealthStatus.CRITICAL,
                'message': 'No healthy API gateway pods',
                'details': {'pod_count': len(pods), 'healthy_count': 0}
            }
        elif len(healthy_pods) < len(pods):
            return {
                'status': HealthStatus.DEGRADED,
                'message': f'{len(healthy_pods)}/{len(pods)} API gateway pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }
        else:
            return {
                'status': HealthStatus.HEALTHY,
                'message': f'All {len(pods)} API gateway pods healthy',
                'details': {'pod_count': len(pods), 'healthy_count': len(healthy_pods)}
            }

    async def _check_ai_agent_endpoint(self) -> Dict[str, Any]:
        """Check AI agent endpoint health"""        try:
            async with self.http_session.get("http://ia-influencer-ai-agent:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'AI agent endpoint responding',
                        'details': {'response_status': response.status, 'data': data}
                    }
                else:
                    return {
                        'status': HealthStatus.UNHEALTHY,
                        'message': f'AI agent endpoint returned {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'AI agent endpoint unreachable: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_content_protection_endpoint(self) -> Dict[str, Any]:
        """Check content protection endpoint health"""        try:
            async with self.http_session.get("http://ia-influencer-content-protection:8001/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'Content protection endpoint responding',
                        'details': {'response_status': response.status, 'data': data}
                    }
                else:
                    return {
                        'status': HealthStatus.UNHEALTHY,
                        'message': f'Content protection endpoint returned {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Content protection endpoint unreachable: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_api_gateway_endpoint(self) -> Dict[str, Any]:
        """Check API gateway endpoint health"""        try:
            async with self.http_session.get("http://ia-influencer-api-gateway:8080/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'API gateway endpoint responding',
                        'details': {'response_status': response.status, 'data': data}
                    }
                else:
                    return {
                        'status': HealthStatus.UNHEALTHY,
                        'message': f'API gateway endpoint returned {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'API gateway endpoint unreachable: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_postgresql_primary(self) -> Dict[str, Any]:
        """Check PostgreSQL primary database health"""        try:
            connection_info = await self.db_manager.check_primary_connection()
            if connection_info['connected']:
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': 'PostgreSQL primary healthy',
                    'details': connection_info
                }
            else:
                return {
                    'status': HealthStatus.CRITICAL,
                    'message': 'PostgreSQL primary connection failed',
                    'details': connection_info
                }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'PostgreSQL primary check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_postgresql_replicas(self) -> Dict[str, Any]:
        """Check PostgreSQL replica health"""        try:
            replica_info = await self.db_manager.check_replica_connections()
            healthy_replicas = [r for r in replica_info if r['connected']]
            
            if len(healthy_replicas) == len(replica_info):
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': f'All {len(replica_info)} PostgreSQL replicas healthy',
                    'details': {'replicas': replica_info}
                }
            elif len(healthy_replicas) > 0:
                return {
                    'status': HealthStatus.DEGRADED,
                    'message': f'{len(healthy_replicas)}/{len(replica_info)} PostgreSQL replicas healthy',
                    'details': {'replicas': replica_info}
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'message': 'No healthy PostgreSQL replicas',
                    'details': {'replicas': replica_info}
                }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'PostgreSQL replica check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_redis_primary(self) -> Dict[str, Any]:
        """Check Redis primary health"""        try:
            redis_info = await self.redis_manager.check_primary_health()
            if redis_info['healthy']:
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': 'Redis primary healthy',
                    'details': redis_info
                }
            else:
                return {
                    'status': HealthStatus.CRITICAL,
                    'message': 'Redis primary unhealthy',
                    'details': redis_info
                }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Redis primary check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_redis_cluster(self) -> Dict[str, Any]:
        """Check Redis cluster health"""        try:
            cluster_info = await self.redis_manager.check_cluster_health()
            healthy_nodes = cluster_info.get('healthy_nodes', 0)
            total_nodes = cluster_info.get('total_nodes', 0)
            
            if healthy_nodes == total_nodes and total_nodes > 0:
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': f'All {total_nodes} Redis cluster nodes healthy',
                    'details': cluster_info
                }
            elif healthy_nodes > total_nodes // 2:
                return {
                    'status': HealthStatus.DEGRADED,
                    'message': f'{healthy_nodes}/{total_nodes} Redis cluster nodes healthy',
                    'details': cluster_info
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'message': f'Only {healthy_nodes}/{total_nodes} Redis cluster nodes healthy',
                    'details': cluster_info
                }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'Redis cluster check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_celery_broker(self) -> Dict[str, Any]:
        """Check Celery broker health"""        try:
            broker_info = await self.queue_manager.check_broker_health()
            if broker_info['healthy']:
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': 'Celery broker healthy',
                    'details': broker_info
                }
            else:
                return {
                    'status': HealthStatus.CRITICAL,
                    'message': 'Celery broker unhealthy',
                    'details': broker_info
                }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Celery broker check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_celery_workers(self) -> Dict[str, Any]:
        """Check Celery workers health"""        try:
            worker_info = await self.queue_manager.check_workers_health()
            active_workers = worker_info.get('active_workers', 0)
            total_workers = worker_info.get('total_workers', 0)
            
            if active_workers == total_workers and total_workers > 0:
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': f'All {total_workers} Celery workers active',
                    'details': worker_info
                }
            elif active_workers > 0:
                return {
                    'status': HealthStatus.DEGRADED,
                    'message': f'{active_workers}/{total_workers} Celery workers active',
                    'details': worker_info
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'message': 'No active Celery workers',
                    'details': worker_info
                }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'Celery workers check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_text_generation_model(self) -> Dict[str, Any]:
        """Check text generation AI model health"""        try:
            # Test model with a simple prompt
            test_prompt = "Generate a brief test response:"
            async with self.http_session.post(
                "http://ia-influencer-ai-agent:8000/api/v1/generate/text",
                json={"prompt": test_prompt, "max_tokens": 10}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'Text generation model responding',
                        'details': {'response_status': response.status, 'data': data}
                    }
                else:
                    return {
                        'status': HealthStatus.UNHEALTHY,
                        'message': f'Text generation model returned {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Text generation model check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_audio_analysis_model(self) -> Dict[str, Any]:
        """Check audio analysis AI model health"""        try:
            # Test model health endpoint
            async with self.http_session.get(
                "http://ia-influencer-ai-agent:8000/api/v1/models/audio/health"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'Audio analysis model healthy',
                        'details': {'response_status': response.status, 'data': data}
                    }
                else:
                    return {
                        'status': HealthStatus.UNHEALTHY,
                        'message': f'Audio analysis model returned {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Audio analysis model check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_image_analysis_model(self) -> Dict[str, Any]:
        """Check image analysis AI model health"""        try:
            # Test model health endpoint
            async with self.http_session.get(
                "http://ia-influencer-ai-agent:8000/api/v1/models/image/health"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'Image analysis model healthy',
                        'details': {'response_status': response.status, 'data': data}
                    }
                else:
                    return {
                        'status': HealthStatus.UNHEALTHY,
                        'message': f'Image analysis model returned {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f'Image analysis model check failed: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API health"""        try:
            async with self.http_session.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": "Bearer test"}  # This will fail auth but test connectivity
            ) as response:
                if response.status == 401:  # Expected auth failure
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'OpenAI API reachable',
                        'details': {'response_status': response.status}
                    }
                else:
                    return {
                        'status': HealthStatus.DEGRADED,
                        'message': f'OpenAI API unexpected response {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'OpenAI API unreachable: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_stripe_api(self) -> Dict[str, Any]:
        """Check Stripe API health"""        try:
            async with self.http_session.get("https://api.stripe.com/v1/charges") as response:
                if response.status == 401:  # Expected auth failure
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'Stripe API reachable',
                        'details': {'response_status': response.status}
                    }
                else:
                    return {
                        'status': HealthStatus.DEGRADED,
                        'message': f'Stripe API unexpected response {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'Stripe API unreachable: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _check_youtube_api(self) -> Dict[str, Any]:
        """Check YouTube API health"""        try:
            async with self.http_session.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={"part": "snippet", "key": "test"}  # This will fail but test connectivity
            ) as response:
                if response.status in [400, 403]:  # Expected API key failure
                    return {
                        'status': HealthStatus.HEALTHY,
                        'message': 'YouTube API reachable',
                        'details': {'response_status': response.status}
                    }
                else:
                    return {
                        'status': HealthStatus.DEGRADED,
                        'message': f'YouTube API unexpected response {response.status}',
                        'details': {'response_status': response.status}
                    }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'YouTube API unreachable: {str(e)}',
                'details': {'error': str(e)}
            }

    async def _collect_service_performance_metrics(
        self, 
        service: str, 
        environment: str
    ) -> Dict[str, float]:
        """Collect performance metrics for a service"""        
        metrics = await self.metrics_collector.collect_service_metrics(service, environment)
        
        return {
            'cpu_usage': metrics.get('cpu_usage_percentage', 0.0),
            'memory_usage': metrics.get('memory_usage_percentage', 0.0),
            'disk_usage': metrics.get('disk_usage_percentage', 0.0),
            'response_time': metrics.get('avg_response_time_ms', 0.0),
            'error_rate': metrics.get('error_rate_percentage', 0.0),
            'request_rate': metrics.get('requests_per_second', 0.0),
            'availability': metrics.get('availability_percentage', 100.0)
        }

    def _check_performance_thresholds(
        self, 
        service: str, 
        metrics: Dict[str, float]
    ) -> List[str]:
        """Check performance metrics against thresholds"""        
        violations = []
        
        for metric_name, value in metrics.items():
            if metric_name in self.thresholds:
                threshold = self.thresholds[metric_name]
                
                if metric_name == 'availability':
                    if value < threshold:
                        violations.append(
                            f"{service}: {metric_name} {value:.1f}% below threshold {threshold}%"
                        )
                else:
                    if value > threshold:
                        violations.append(
                            f"{service}: {metric_name} {value:.1f}% above threshold {threshold}%"
                        )
        
        return violations

    async def _validate_service_security(
        self, 
        service: str, 
        environment: str
    ) -> Dict[str, Any]:
        """Validate security configuration for a service"""        
        security_result = {
            'secure': True,
            'vulnerabilities': [],
            'recommendations': []
        }
        
        # This would implement actual security checks
        # For now, return a mock result
        security_result['recommendations'].append(
            f"Review {service} security configuration for {environment}"
        )
        
        return security_result

    async def _calculate_overall_health(
        self, 
        service_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall health metrics"""        
        total_services = len(service_results)
        healthy_services = sum(1 for result in service_results.values() if result['healthy'])
        
        overall_health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        if overall_health_percentage >= 90:
            overall_status = HealthStatus.HEALTHY
        elif overall_health_percentage >= 70:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        return {
            'status': overall_status,
            'health_percentage': overall_health_percentage,
            'healthy_services': healthy_services,
            'total_services': total_services,
            'unhealthy_services': total_services - healthy_services
        }

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""        summary = {
            'timestamp': datetime.utcnow(),
            'total_checks': len(self.health_checks),
            'check_status': {},
            'critical_issues': [],
            'degraded_services': []
        }
        
        # Get latest results for each check
        for check_name in self.health_checks:
            if check_name in self.health_history and self.health_history[check_name]:
                latest_result = self.health_history[check_name][-1]
                summary['check_status'][check_name] = {
                    'status': latest_result.status.value,
                    'message': latest_result.message,
                    'timestamp': latest_result.timestamp
                }
                
                if latest_result.status == HealthStatus.CRITICAL:
                    summary['critical_issues'].append(check_name)
                elif latest_result.status == HealthStatus.DEGRADED:
                    summary['degraded_services'].append(check_name)
        
        return summary

    async def cleanup(self):
        """Cleanup resources"""        await self.http_session.close()
        self.executor.shutdown(wait=True)
