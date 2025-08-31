"""🚀 Surveillance Module Index - IA Influencer Agent Business Layer
==============================================================

Central index and orchestration file for the surveillance business module,
providing unified access to all surveillance components and services.

Architecture: Enterprise 3-Tier Professional (Backend Level 2)
Module: backend/business/surveillance/index.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Flow:
Module Initialization → Component Registration → Service Discovery → 
Configuration Management → Health Checks → Monitoring Activation → 
Orchestration Layer → API Endpoints → Error Handling → Metrics Collection
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import redis
from sqlalchemy import create_engine
import importlib
import inspect

# Core surveillance components
from .web_crawler import WebCrawlerEngine, CrawlerConfig, CrawlerResult
from .platform_monitor import PlatformMonitoringService, MonitoringAlert
from .infringement_detector import InfringementDetectionEngine, InfringementReport
from .takedown_manager import TakedownManager, TakedownRequest
from .analytics_tracker import SurveillanceAnalytics, SurveillanceMetrics
from .alert_system import AlertSystem, AlertConfig
from .reporting_engine import ReportingEngine, SurveillanceReport
from .api_integrator import APIIntegrator, PlatformAPI
from .content_scanner import ContentScanner, ScanResult
from .protection_enforcer import ProtectionEnforcer, EnforcementAction
from .fingerprinting_engine import FingerprintingEngine, ContentFingerprint

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"
    ERROR = "error"


class ComponentType(Enum):
    """Surveillance component types"""    CRAWLER = "crawler"
    MONITOR = "monitor"
    DETECTOR = "detector"
    MANAGER = "manager"
    ANALYTICS = "analytics"
    ALERT = "alert"
    REPORTING = "reporting"
    INTEGRATOR = "integrator"
    SCANNER = "scanner"
    ENFORCER = "enforcer"
    FINGERPRINTING = "fingerprinting"


@dataclass
class ServiceHealth:
    """Service health information"""    service_name: str
    component_type: ComponentType
    status: ServiceStatus
    uptime: float
    last_check: datetime
    error_count: int = 0
    warning_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)


@dataclass
class SurveillanceConfig:
    """Global surveillance configuration"""    # Database configuration
    database_url: Optional[str] = None
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Storage configuration
    storage_path: Optional[Path] = None
    temp_path: Optional[Path] = None
    
    # Service configuration
    max_concurrent_tasks: int = 100
    task_timeout: int = 300
    batch_size: int = 50
    
    # Monitoring configuration
    health_check_interval: int = 60
    metrics_collection_interval: int = 30
    alert_threshold: float = 0.8
    
    # Security configuration
    api_key: Optional[str] = None
    encryption_key: Optional[str] = None
    rate_limit: int = 1000
    
    # Feature flags
    enable_real_time_monitoring: bool = True
    enable_ml_detection: bool = True
    enable_auto_takedown: bool = False
    enable_advanced_analytics: bool = True
    
    # Platform configuration
    enabled_platforms: List[str] = field(default_factory=lambda: [
        'youtube', 'tiktok', 'instagram', 'twitter', 'facebook'
    ])


class SurveillanceOrchestrator:
    """    Central Surveillance Orchestrator
    
    Manages and coordinates all surveillance components, providing
    a unified interface for surveillance operations and monitoring.
    """    
    def __init__(self, config: Optional[SurveillanceConfig] = None):
        """Initialize surveillance orchestrator"""        self.config = config or SurveillanceConfig()
        self.services: Dict[str, Any] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.is_running = False
        self.startup_time = datetime.now(timezone.utc)
        
        # Initialize connections
        self.redis_client: Optional[redis.Redis] = None
        self.database_engine = None
        
        # Internal state
        self.task_queue = asyncio.Queue(maxsize=self.config.max_concurrent_tasks)
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.metrics_collector = None
        
        logger.info("SurveillanceOrchestrator initialized")
    
    async def initialize(self) -> bool:
        """Initialize all surveillance services"""        try:
            logger.info("Starting surveillance orchestrator initialization...")
            
            # Initialize connections
            await self._initialize_connections()
            
            # Initialize core services
            await self._initialize_services()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            # Start metrics collection
            await self._start_metrics_collection()
            
            # Verify all services
            if await self._verify_services():
                self.is_running = True
                logger.info("Surveillance orchestrator initialized successfully")
                return True
            else:
                logger.error("Service verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Orchestrator initialization failed: {e}")
            return False
    
    async def _initialize_connections(self):
        """Initialize database and Redis connections"""        try:
            # Initialize Redis
            if self.config.redis_url:
                self.redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True
                )
                # Test connection
                await asyncio.to_thread(self.redis_client.ping)
                logger.info("Redis connection established")
            
            # Initialize database
            if self.config.database_url:
                self.database_engine = create_engine(self.config.database_url)
                # Test connection
                with self.database_engine.begin() as conn:
                    conn.execute("SELECT 1")
                logger.info("Database connection established")
                
        except Exception as e:
            logger.error(f"Connection initialization failed: {e}")
            raise
    
    async def _initialize_services(self):
        """Initialize all surveillance services"""        try:
            # Storage paths
            storage_path = self.config.storage_path or Path("surveillance_data")
            storage_path.mkdir(exist_ok=True)
            
            temp_path = self.config.temp_path or Path("temp")
            temp_path.mkdir(exist_ok=True)
            
            # Initialize Web Crawler
            self.services['web_crawler'] = WebCrawlerEngine(
                redis_client=self.redis_client,
                database_url=self.config.database_url
            )
            
            # Initialize Platform Monitor
            self.services['platform_monitor'] = PlatformMonitoringService(
                redis_client=self.redis_client,
                database_url=self.config.database_url
            )
            
            # Initialize Infringement Detector
            self.services['infringement_detector'] = InfringementDetectionEngine(
                redis_client=self.redis_client,
                database_url=self.config.database_url
            )
            
            # Initialize Takedown Manager
            self.services['takedown_manager'] = TakedownManager(
                redis_client=self.redis_client,
                database_url=self.config.database_url
            )
            
            # Initialize Analytics Tracker
            self.services['analytics_tracker'] = SurveillanceAnalytics(
                redis_client=self.redis_client,
                database_url=self.config.database_url,
                storage_path=storage_path
            )
            
            # Initialize Alert System
            self.services['alert_system'] = AlertSystem(
                redis_client=self.redis_client
            )
            
            # Initialize Reporting Engine
            self.services['reporting_engine'] = ReportingEngine(
                redis_client=self.redis_client,
                database_url=self.config.database_url,
                storage_path=storage_path
            )
            
            # Initialize API Integrator
            self.services['api_integrator'] = APIIntegrator(
                redis_client=self.redis_client
            )
            
            # Initialize Content Scanner
            self.services['content_scanner'] = ContentScanner(
                redis_client=self.redis_client,
                temp_path=temp_path
            )
            
            # Initialize Protection Enforcer
            self.services['protection_enforcer'] = ProtectionEnforcer(
                redis_client=self.redis_client,
                database_url=self.config.database_url
            )
            
            # Initialize Fingerprinting Engine
            self.services['fingerprinting_engine'] = FingerprintingEngine(
                redis_client=self.redis_client,
                database_url=self.config.database_url,
                storage_path=storage_path
            )
            
            # Initialize service health tracking
            for service_name, service in self.services.items():
                component_type = self._get_component_type(service_name)
                self.service_health[service_name] = ServiceHealth(
                    service_name=service_name,
                    component_type=component_type,
                    status=ServiceStatus.INITIALIZING,
                    uptime=0.0,
                    last_check=datetime.now(timezone.utc),
                    dependencies=self._get_service_dependencies(service_name)
                )
            
            logger.info(f"Initialized {len(self.services)} surveillance services")
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise
    
    def _get_component_type(self, service_name: str) -> ComponentType:
        """Get component type for service"""        mapping = {
            'web_crawler': ComponentType.CRAWLER,
            'platform_monitor': ComponentType.MONITOR,
            'infringement_detector': ComponentType.DETECTOR,
            'takedown_manager': ComponentType.MANAGER,
            'analytics_tracker': ComponentType.ANALYTICS,
            'alert_system': ComponentType.ALERT,
            'reporting_engine': ComponentType.REPORTING,
            'api_integrator': ComponentType.INTEGRATOR,
            'content_scanner': ComponentType.SCANNER,
            'protection_enforcer': ComponentType.ENFORCER,
            'fingerprinting_engine': ComponentType.FINGERPRINTING
        }
        return mapping.get(service_name, ComponentType.MANAGER)
    
    def _get_service_dependencies(self, service_name: str) -> List[str]:
        """Get service dependencies"""        dependencies = {
            'web_crawler': ['redis', 'database'],
            'platform_monitor': ['redis', 'database', 'alert_system'],
            'infringement_detector': ['redis', 'database', 'fingerprinting_engine'],
            'takedown_manager': ['redis', 'database', 'api_integrator'],
            'analytics_tracker': ['redis', 'database'],
            'alert_system': ['redis'],
            'reporting_engine': ['redis', 'database', 'analytics_tracker'],
            'api_integrator': ['redis'],
            'content_scanner': [],
            'protection_enforcer': ['redis', 'database', 'takedown_manager'],
            'fingerprinting_engine': ['redis', 'database']
        }
        return dependencies.get(service_name, [])
    
    async def _start_health_monitoring(self):
        """Start health monitoring task"""        async def health_monitor():
            while self.is_running:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(5)
        
        self.active_tasks['health_monitor'] = asyncio.create_task(health_monitor())
        logger.info("Health monitoring started")
    
    async def _start_metrics_collection(self):
        """Start metrics collection task"""        async def metrics_collector():
            while self.is_running:
                try:
                    await self._collect_metrics()
                    await asyncio.sleep(self.config.metrics_collection_interval)
                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
                    await asyncio.sleep(5)
        
        self.active_tasks['metrics_collector'] = asyncio.create_task(metrics_collector())
        logger.info("Metrics collection started")
    
    async def _perform_health_checks(self):
        """Perform health checks on all services"""        try:
            for service_name, service in self.services.items():
                health = self.service_health[service_name]
                
                try:
                    # Basic service check
                    if hasattr(service, 'health_check'):
                        is_healthy = await service.health_check()
                    else:
                        is_healthy = service is not None
                    
                    # Update health status
                    if is_healthy:
                        if health.status == ServiceStatus.INITIALIZING:
                            health.status = ServiceStatus.HEALTHY
                        health.error_count = max(0, health.error_count - 1)
                    else:
                        health.error_count += 1
                        if health.error_count > 3:
                            health.status = ServiceStatus.UNHEALTHY
                        else:
                            health.status = ServiceStatus.DEGRADED
                    
                    # Update uptime
                    health.uptime = (datetime.now(timezone.utc) - self.startup_time).total_seconds()
                    health.last_check = datetime.now(timezone.utc)
                    
                except Exception as e:
                    logger.error(f"Health check failed for {service_name}: {e}")
                    health.status = ServiceStatus.ERROR
                    health.error_count += 1
                    
        except Exception as e:
            logger.error(f"Health check process failed: {e}")
    
    async def _collect_metrics(self):
        """Collect metrics from all services"""        try:
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, 'get_metrics'):
                        metrics = await service.get_metrics()
                        self.service_health[service_name].metrics = metrics
                        
                        # Store metrics in analytics tracker if available
                        if 'analytics_tracker' in self.services:
                            await self.services['analytics_tracker'].record_service_metrics(
                                service_name, metrics
                            )
                            
                except Exception as e:
                    logger.error(f"Metrics collection failed for {service_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Metrics collection process failed: {e}")
    
    async def _verify_services(self) -> bool:
        """Verify all services are properly initialized"""        try:
            verification_results = {}
            
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, 'verify_initialization'):
                        is_verified = await service.verify_initialization()
                    else:
                        is_verified = service is not None
                    
                    verification_results[service_name] = is_verified
                    
                    if is_verified:
                        self.service_health[service_name].status = ServiceStatus.HEALTHY
                    else:
                        self.service_health[service_name].status = ServiceStatus.ERROR
                        
                except Exception as e:
                    logger.error(f"Service verification failed for {service_name}: {e}")
                    verification_results[service_name] = False
                    self.service_health[service_name].status = ServiceStatus.ERROR
            
            # Check if all services are verified
            all_verified = all(verification_results.values())
            
            logger.info(f"Service verification: {sum(verification_results.values())}/{len(verification_results)} services verified")
            
            return all_verified
            
        except Exception as e:
            logger.error(f"Service verification process failed: {e}")
            return False
    
    async def get_service_health(self) -> Dict[str, ServiceHealth]:
        """Get health status of all services"""        return self.service_health.copy()
    
    async def get_service(self, service_name: str) -> Optional[Any]:
        """Get specific service instance"""        return self.services.get(service_name)
    
    async def execute_surveillance_task(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        priority: int = 5
    ) -> str:
        """Execute a surveillance task"""        try:
            task_id = f"task_{int(datetime.now().timestamp())}_{task_type}"
            
            # Create task coroutine based on type
            if task_type == 'web_crawl':
                task_coro = self._execute_web_crawl(task_data)
            elif task_type == 'content_scan':
                task_coro = self._execute_content_scan(task_data)
            elif task_type == 'infringement_detection':
                task_coro = self._execute_infringement_detection(task_data)
            elif task_type == 'takedown_request':
                task_coro = self._execute_takedown_request(task_data)
            elif task_type == 'analytics_report':
                task_coro = self._execute_analytics_report(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Execute task with timeout
            task = asyncio.create_task(
                asyncio.wait_for(task_coro, timeout=self.config.task_timeout)
            )
            
            self.active_tasks[task_id] = task
            
            logger.info(f"Surveillance task {task_id} started")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to execute surveillance task: {e}")
            raise
    
    async def _execute_web_crawl(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web crawling task"""        crawler = self.services['web_crawler']
        
        config = CrawlerConfig(**task_data.get('config', {}))
        result = await crawler.crawl_platform(
            platform=task_data['platform'],
            search_terms=task_data['search_terms'],
            config=config
        )
        
        return {'type': 'web_crawl', 'result': result}
    
    async def _execute_content_scan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content scanning task"""        scanner = self.services['content_scanner']
        
        result = await scanner.scan_content(
            content_path=task_data['content_path'],
            scan_types=task_data.get('scan_types', [])
        )
        
        return {'type': 'content_scan', 'result': result}
    
    async def _execute_infringement_detection(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute infringement detection task"""        detector = self.services['infringement_detector']
        
        result = await detector.detect_infringement(
            content_fingerprint=task_data['content_fingerprint'],
            search_platforms=task_data.get('search_platforms', [])
        )
        
        return {'type': 'infringement_detection', 'result': result}
    
    async def _execute_takedown_request(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute takedown request task"""        manager = self.services['takedown_manager']
        
        result = await manager.submit_takedown_request(
            infringement_report=task_data['infringement_report'],
            request_type=task_data.get('request_type', 'dmca')
        )
        
        return {'type': 'takedown_request', 'result': result}
    
    async def _execute_analytics_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics report generation task"""        analytics = self.services['analytics_tracker']
        
        result = await analytics.generate_analytics_report(
            time_range=task_data['time_range'],
            user_id=task_data.get('user_id'),
            platforms=task_data.get('platforms'),
            include_visualizations=task_data.get('include_visualizations', True)
        )
        
        return {'type': 'analytics_report', 'result': result}
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of specific task"""        if task_id not in self.active_tasks:
            return {'status': 'not_found'}
        
        task = self.active_tasks[task_id]
        
        if task.done():
            try:
                result = await task
                return {
                    'status': 'completed',
                    'result': result
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'error': str(e)
                }
        else:
            return {'status': 'running'}
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel specific task"""        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.active_tasks[task_id]
        return True
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""        try:
            # Calculate overall health
            healthy_services = sum(
                1 for health in self.service_health.values() 
                if health.status == ServiceStatus.HEALTHY
            )
            total_services = len(self.service_health)
            health_percentage = (healthy_services / total_services) * 100 if total_services > 0 else 0
            
            # Get active tasks count
            active_tasks_count = len([task for task in self.active_tasks.values() if not task.done()])
            
            # System uptime
            uptime = (datetime.now(timezone.utc) - self.startup_time).total_seconds()
            
            # Get memory usage (simplified)
            import psutil
            memory_info = psutil.virtual_memory()
            
            return {
                'orchestrator_status': 'running' if self.is_running else 'stopped',
                'health_percentage': health_percentage,
                'services': {
                    'total': total_services,
                    'healthy': healthy_services,
                    'degraded': sum(1 for h in self.service_health.values() if h.status == ServiceStatus.DEGRADED),
                    'unhealthy': sum(1 for h in self.service_health.values() if h.status == ServiceStatus.UNHEALTHY),
                    'error': sum(1 for h in self.service_health.values() if h.status == ServiceStatus.ERROR)
                },
                'tasks': {
                    'active': active_tasks_count,
                    'total': len(self.active_tasks)
                },
                'system': {
                    'uptime': uptime,
                    'memory_usage': memory_info.percent,
                    'memory_available': memory_info.available
                },
                'configuration': {
                    'max_concurrent_tasks': self.config.max_concurrent_tasks,
                    'enabled_platforms': self.config.enabled_platforms,
                    'features': {
                        'real_time_monitoring': self.config.enable_real_time_monitoring,
                        'ml_detection': self.config.enable_ml_detection,
                        'auto_takedown': self.config.enable_auto_takedown,
                        'advanced_analytics': self.config.enable_advanced_analytics
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def shutdown(self):
        """Graceful shutdown of orchestrator"""        try:
            logger.info("Starting surveillance orchestrator shutdown...")
            
            self.is_running = False
            
            # Cancel all active tasks
            for task_id, task in list(self.active_tasks.items()):
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.active_tasks.clear()
            
            # Shutdown services
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, 'shutdown'):
                        await service.shutdown()
                    self.service_health[service_name].status = ServiceStatus.STOPPED
                except Exception as e:
                    logger.error(f"Error shutting down {service_name}: {e}")
            
            # Close connections
            if self.redis_client:
                await asyncio.to_thread(self.redis_client.close)
            
            if self.database_engine:
                self.database_engine.dispose()
            
            logger.info("Surveillance orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global orchestrator instance
_orchestrator: Optional[SurveillanceOrchestrator] = None


def get_orchestrator(config: Optional[SurveillanceConfig] = None) -> SurveillanceOrchestrator:
    """Get global orchestrator instance"""    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = SurveillanceOrchestrator(config)
    
    return _orchestrator


async def initialize_surveillance_module(config: Optional[SurveillanceConfig] = None) -> bool:
    """Initialize the entire surveillance module"""    try:
        orchestrator = get_orchestrator(config)
        return await orchestrator.initialize()
    except Exception as e:
        logger.error(f"Surveillance module initialization failed: {e}")
        return False


async def shutdown_surveillance_module():
    """Shutdown the surveillance module"""    global _orchestrator
    
    if _orchestrator:
        await _orchestrator.shutdown()
        _orchestrator = None


# Convenience functions for direct service access
async def get_web_crawler() -> Optional[WebCrawlerEngine]:
    """Get web crawler service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('web_crawler')


async def get_platform_monitor() -> Optional[PlatformMonitoringService]:
    """Get platform monitoring service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('platform_monitor')


async def get_infringement_detector() -> Optional[InfringementDetectionEngine]:
    """Get infringement detection service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('infringement_detector')


async def get_takedown_manager() -> Optional[TakedownManager]:
    """Get takedown manager service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('takedown_manager')


async def get_analytics_tracker() -> Optional[SurveillanceAnalytics]:
    """Get analytics tracker service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('analytics_tracker')


async def get_alert_system() -> Optional[AlertSystem]:
    """Get alert system service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('alert_system')


async def get_reporting_engine() -> Optional[ReportingEngine]:
    """Get reporting engine service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('reporting_engine')


async def get_content_scanner() -> Optional[ContentScanner]:
    """Get content scanner service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('content_scanner')


async def get_fingerprinting_engine() -> Optional[FingerprintingEngine]:
    """Get fingerprinting engine service"""    orchestrator = get_orchestrator()
    return await orchestrator.get_service('fingerprinting_engine')


# Export all classes and functions
__all__ = [
    # Core classes
    'SurveillanceOrchestrator',
    'SurveillanceConfig', 
    'ServiceHealth',
    'ServiceStatus',
    'ComponentType',
    
    # Global functions
    'get_orchestrator',
    'initialize_surveillance_module',
    'shutdown_surveillance_module',
    
    # Service access functions
    'get_web_crawler',
    'get_platform_monitor', 
    'get_infringement_detector',
    'get_takedown_manager',
    'get_analytics_tracker',
    'get_alert_system',
    'get_reporting_engine',
    'get_content_scanner',
    'get_fingerprinting_engine',
    
    # Service classes (re-exported)
    'WebCrawlerEngine',
    'PlatformMonitoringService',
    'InfringementDetectionEngine', 
    'TakedownManager',
    'SurveillanceAnalytics',
    'AlertSystem',
    'ReportingEngine',
    'APIIntegrator',
    'ContentScanner',
    'ProtectionEnforcer',
    'FingerprintingEngine',
    
    # Data classes (re-exported)
    'CrawlerConfig',
    'CrawlerResult',
    'MonitoringAlert',
    'InfringementReport',
    'TakedownRequest',
    'SurveillanceMetrics',
    'AlertConfig',
    'SurveillanceReport',
    'PlatformAPI',
    'ScanResult',
    'EnforcementAction',
    'ContentFingerprint'
]
