"""
Coordination Index - Unified Enterprise Coordination Service Entry Point

This module provides the main entry point for the coordination system,
implementing a comprehensive service that unifies all coordination components
under a single, enterprise-grade interface for the IA-Influencer-Agent platform.

 CRITICAL LEGAL WARNING - READ CAREFULLY 

This code and all related concepts are the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.

ANY UNAUTHORIZED USE, COPYING, DISTRIBUTION, MODIFICATION, OR COMMERCIALIZATION 
WITHOUT EXPLICIT WRITTEN PERMISSION FROM FAHED MLAIEL IS STRICTLY PROHIBITED 
AND WILL RESULT IN IMMEDIATE LEGAL ACTION UNDER GERMAN AND INTERNATIONAL COPYRIGHT LAW.

Contact for authorization: mlaiel@live.de
ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

Business Logic Flow:
Content Upload → Multi-Format Analysis → AI Fingerprinting → Protection Setup → 
SEO Optimization → Platform Distribution → Revenue Tracking → Collaboration Discovery → 
Automated Monetization → Rights Management → Performance Analytics

Author: Fahed Mlaiel
Project Lead & Chief Architect
Email: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
from contextlib import asynccontextmanager

from .workflow_coordinator import (
    WorkflowCoordinator, 
    WorkflowDefinition, 
    WorkflowStatus,
    WorkflowPriority,
    WorkflowType
)
from .process_manager import ProcessManager, ProcessExecutionContext
from .task_scheduler import TaskScheduler, TaskDefinition, TaskStatus
from .resource_coordinator import ResourceCoordinator, ResourceRequirement, AllocationStrategy
from .state_manager import StateManager, StateTransition
from .event_dispatcher import EventDispatcher, Event, EventPriority
from .sync_manager import SyncManager, SyncConfiguration
from .dependency_resolver import DependencyResolver, ServiceDefinition

# Configure logging
logger = logging.getLogger(__name__)


class ServiceHealthStatus(Enum):
    """Service health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CoordinationServiceStatus(Enum):
    """Overall coordination service status."""
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceMetrics:
    """Comprehensive service metrics."""
    service_name: str
    status: ServiceHealthStatus
    uptime_seconds: float
    request_count: int
    error_count: int
    success_rate: float
    average_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    last_health_check: datetime
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoordinationServiceConfig:
    """Configuration for the coordination service."""
    # Core Configuration
    max_workflows: int = 100
    max_processes: int = 200
    max_tasks: int = 50
    monitoring_interval: int = 15
    
    # Performance Configuration
    cache_size: int = 5000
    event_workers: int = 30
    event_queue_size: int = 50000
    dependency_cache_size: int = 2000
    
    # Reliability Configuration
    enable_encryption: bool = True
    enable_audit_logging: bool = True
    max_retry_attempts: int = 5
    circuit_breaker_threshold: int = 10
    health_check_interval: int = 30
    
    # Business Logic Configuration
    enable_ai_optimization: bool = True
    enable_auto_scaling: bool = True
    enable_predictive_analysis: bool = True
    enable_real_time_sync: bool = True



class CoordinationService:
    """
    Unified enterprise coordination service that orchestrates all coordination components.
    
    This service provides a single entry point for managing workflows, processes, tasks,
    resources, state, events, synchronization, and dependencies across the entire
    IA-Influencer-Agent platform.
    """
    
    def __init__(self, config: Optional[CoordinationServiceConfig] = None):
        """Initialize the coordination service with all components."""
        self.config = config or CoordinationServiceConfig()
        self.status = CoordinationServiceStatus.STARTING
        self.start_time = datetime.now()
        self.service_id = str(uuid.uuid4())
        
        # Performance tracking
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'peak_concurrent_operations': 0,
            'total_workflows_executed': 0,
            'total_processes_managed': 0,
            'total_tasks_scheduled': 0,
            'total_resources_allocated': 0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Initialize all coordination components
        self._initialize_components()
        
        # Health monitoring
        self._health_monitor_task = None
        self._start_health_monitoring()
        
        logger.info(f"CoordinationService initialized with ID: {self.service_id}")
    
    def _initialize_components(self):
        """Initialize all coordination service components."""



        try:
            # Initialize workflow coordinator
            self.workflow_coordinator = WorkflowCoordinator(
                max_concurrent_workflows=self.config.max_workflows
            )
            
            # Initialize process manager
            self.process_manager = ProcessManager(
                max_processes=self.config.max_processes
            )
            
            # Initialize task scheduler
            self.task_scheduler = TaskScheduler(
                max_concurrent_tasks=self.config.max_tasks
            )
            
            # Initialize resource coordinator
            self.resource_coordinator = ResourceCoordinator()
            
            # Initialize state manager
            self.state_manager = StateManager()
            
            # Initialize event dispatcher
            self.event_dispatcher = EventDispatcher(
                max_workers=self.config.event_workers,
                queue_size=self.config.event_queue_size
            )
            
            # Initialize sync manager
            self.sync_manager = SyncManager()
            
            # Initialize dependency resolver
            self.dependency_resolver = DependencyResolver(
                cache_size=self.config.dependency_cache_size
            )
            
            # Start monitoring for components that require it
            self.process_manager.start_monitoring()
            self.resource_coordinator.start_monitoring()
            self.task_scheduler.start_scheduler()
            
            logger.info("All coordination components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize coordination components: {e}")
            self.status = CoordinationServiceStatus.ERROR
            raise
    
    def _start_health_monitoring(self):
        """Start the health monitoring background task."""
        def health_monitor():
            while not self._shutdown_event.is_set():
                try:
                    self._perform_health_check()
                    time.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(self.config.health_check_interval)
        
        self._health_monitor_task = threading.Thread(
            target=health_monitor,
            daemon=True,
            name="CoordinationHealthMonitor"
        )
        self._health_monitor_task.start()
        logger.info("Health monitoring started")
    
    def _perform_health_check(self):
        """Perform comprehensive health check of all components."""



        try:
            component_health = {
                'workflow_coordinator': self._check_component_health(self.workflow_coordinator),
                'process_manager': self._check_component_health(self.process_manager),
                'task_scheduler': self._check_component_health(self.task_scheduler),
                'resource_coordinator': self._check_component_health(self.resource_coordinator),
                'state_manager': self._check_component_health(self.state_manager),
                'event_dispatcher': self._check_component_health(self.event_dispatcher),
                'sync_manager': self._check_component_health(self.sync_manager),
                'dependency_resolver': self._check_component_health(self.dependency_resolver)
            }
            
            # Determine overall health
            healthy_components = sum(1 for health in component_health.values() 
                                   if health['status'] == ServiceHealthStatus.HEALTHY)
            total_components = len(component_health)
            
            if healthy_components == total_components:
                if self.status != CoordinationServiceStatus.RUNNING:
                    self.status = CoordinationServiceStatus.RUNNING
                    logger.info("Coordination service is fully operational")
            elif healthy_components >= total_components * 0.7:
                self.status = CoordinationServiceStatus.DEGRADED
                logger.warning("Coordination service is running in degraded mode")
            else:
                self.status = CoordinationServiceStatus.CRITICAL
                logger.error("Coordination service is in critical state")
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.status = CoordinationServiceStatus.ERROR
    
    def _check_component_health(self, component) -> Dict[str, Any]:
        """Check health of individual component."""



        try:
            if hasattr(component, 'health_check'):
                return component.health_check()
            elif hasattr(component, 'get_system_metrics'):
                metrics = component.get_system_metrics()
                return {
                    'status': ServiceHealthStatus.HEALTHY,
                    'metrics': metrics,
                    'last_check': datetime.now()
                }
            else:
                return {
                    'status': ServiceHealthStatus.HEALTHY,
                    'last_check': datetime.now()
                }
        except Exception as e:
            return {
                'status': ServiceHealthStatus.CRITICAL,
                'error': str(e),
                'last_check': datetime.now()
            }
    
    async def execute_content_workflow(
        self,
        content_data: Dict[str, Any],
        user_id: str,
        platform_targets: List[str],
        workflow_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute the complete content processing workflow for the IA-Influencer-Agent platform.
        
        This method orchestrates the entire business logic flow:
        Content Upload → Multi-Format Analysis → AI Fingerprinting → Protection Setup → 
        SEO Optimization → Platform Distribution → Revenue Tracking → Collaboration Discovery → 
        Automated Monetization → Rights Management → Performance Analytics
        
        Args:
            content_data: Content information including file path, type, metadata
            user_id: User identifier
            platform_targets: List of target platforms (spotify, youtube, tiktok, instagram)
            workflow_options: Additional workflow configuration options
            
        Returns:
            Execution ID for tracking the workflow progress
        """



        try:
            with self._lock:
                self.metrics['total_requests'] += 1
                start_time = time.time()
            
            # Validate input parameters
            if not content_data or not user_id or not platform_targets:
                raise ValueError("Missing required parameters for content workflow")
            
            # Prepare workflow execution context
            execution_context = {
                'user_id': user_id,
                'content_data': content_data,
                'platform_targets': platform_targets,
                'workflow_options': workflow_options or {},
                'execution_timestamp': datetime.now().isoformat(),
                'service_id': self.service_id
            }
            
            # Create business workflow definition
            business_workflow = self._create_business_workflow(execution_context)
            
            # Register workflow if not already registered
            if not self.workflow_coordinator.is_workflow_registered(business_workflow.workflow_id):
                self.workflow_coordinator.register_workflow(business_workflow)
            
            # Execute the workflow
            execution_id = await self.workflow_coordinator.execute_workflow(
                workflow_id=business_workflow.workflow_id,
                user_id=user_id,
                execution_context=execution_context
            )
            
            # Dispatch workflow started event
            await self.event_dispatcher.dispatch_event(Event(
                event_type="workflow_started",
                data={
                    'execution_id': execution_id,
                    'workflow_type': 'content_processing',
                    'user_id': user_id,
                    'platform_targets': platform_targets
                },
                priority=EventPriority.HIGH
            ))
            
            # Update metrics
            execution_time = time.time() - start_time
            with self._lock:
                self.metrics['successful_requests'] += 1
                self.metrics['total_workflows_executed'] += 1
                self.metrics['average_response_time'] = (
                    (self.metrics['average_response_time'] * (self.metrics['total_requests'] - 1) + execution_time) /
                    self.metrics['total_requests']
                )
            
            logger.info(f"Content workflow started successfully: {execution_id}")
            return execution_id
            
        except Exception as e:
            with self._lock:
                self.metrics['failed_requests'] += 1
            logger.error(f"Failed to execute content workflow: {e}")
            raise
    
    def _create_business_workflow(self, execution_context: Dict[str, Any]) -> WorkflowDefinition:
        """Create the comprehensive business workflow definition."""
        from .workflow_coordinator import WorkflowStep
        
        return WorkflowDefinition(
            workflow_id="ia_influencer_content_processing_enterprise",
            name="IA-Influencer Enterprise Content Processing Workflow",
            description="Complete content processing workflow for creators with AI protection and monetization",
            workflow_type=WorkflowType.CONTENT_PROCESSING,
            steps=[
                # Step 1: Multi-Format Content Analysis
                WorkflowStep(
                    step_id="multi_format_analysis",
                    name="Multi-Format Content Analysis",
                    description="Advanced AI analysis of uploaded content across all supported formats",
                    service_endpoint="/api/v1/ai/analyze-content-multiformat",
                    timeout_seconds=300,
                    retry_count=3,
                    parameters={
                        "analysis_depth": "comprehensive",
                        "format_detection": True,
                        "metadata_extraction": True,
                        "quality_assessment": True
                    }
                ),
                
                # Step 2: AI Fingerprinting & Protection
                WorkflowStep(
                    step_id="ai_fingerprinting",
                    name="AI Fingerprinting & Protection Setup",
                    description="Generate unique AI fingerprints and setup protection mechanisms",
                    service_endpoint="/api/v1/protection/fingerprint-generate",
                    dependencies=["multi_format_analysis"],
                    timeout_seconds=600,
                    retry_count=3,
                    parameters={
                        "protection_level": "maximum",
                        "fingerprint_algorithm": "enterprise_v2",
                        "real_time_monitoring": True
                    }
                ),
                
                # Step 3: SEO Optimization
                WorkflowStep(
                    step_id="seo_optimization",
                    name="AI-Powered SEO Optimization",
                    description="Optimize content for search engines and platform algorithms",
                    service_endpoint="/api/v1/seo/optimize-content",
                    dependencies=["multi_format_analysis"],
                    timeout_seconds=240,
                    retry_count=2,
                    parameters={
                        "target_platforms": execution_context.get('platform_targets', []),
                        "keyword_optimization": True,
                        "metadata_enhancement": True,
                        "algorithm_adaptation": True
                    }
                ),
                
                # Step 4: Platform Distribution Setup
                WorkflowStep(
                    step_id="platform_distribution",
                    name="Multi-Platform Distribution Setup",
                    description="Prepare and configure content for distribution across target platforms",
                    service_endpoint="/api/v1/distribution/setup-multiplatform",
                    dependencies=["seo_optimization", "ai_fingerprinting"],
                    timeout_seconds=180,
                    retry_count=2,
                    parameters={
                        "platforms": execution_context.get('platform_targets', []),
                        "format_adaptation": True,
                        "schedule_optimization": True,
                        "audience_targeting": True
                    }
                ),
                
                # Step 5: Revenue Tracking Setup
                WorkflowStep(
                    step_id="revenue_tracking_setup",
                    name="Revenue Tracking & Monetization Setup",
                    description="Initialize revenue tracking and monetization mechanisms",
                    service_endpoint="/api/v1/monetization/setup-tracking",
                    dependencies=["platform_distribution"],
                    timeout_seconds=120,
                    retry_count=2,
                    parameters={
                        "tracking_precision": "high",
                        "real_time_analytics": True,
                        "cross_platform_correlation": True
                    }
                ),
                
                # Step 6: Collaboration Discovery
                WorkflowStep(
                    step_id="collaboration_discovery",
                    name="AI-Powered Collaboration Discovery",
                    description="Discover potential collaboration opportunities using AI matching",
                    service_endpoint="/api/v1/collaboration/discover-opportunities",
                    dependencies=["platform_distribution"],
                    timeout_seconds=300,
                    retry_count=2,
                    parameters={
                        "discovery_algorithm": "advanced_matching_v2",
                        "compatibility_analysis": True,
                        "audience_overlap_analysis": True,
                        "revenue_potential_estimation": True
                    }
                ),
                
                # Step 7: Automated Monetization
                WorkflowStep(
                    step_id="automated_monetization",
                    name="Automated Monetization Activation",
                    description="Activate automated monetization strategies and revenue optimization",
                    service_endpoint="/api/v1/monetization/activate-automation",
                    dependencies=["revenue_tracking_setup", "collaboration_discovery"],
                    timeout_seconds=180,
                    retry_count=2,
                    parameters={
                        "optimization_strategy": "ai_driven",
                        "dynamic_pricing": True,
                        "market_adaptation": True,
                        "performance_monitoring": True
                    }
                ),
                
                # Step 8: Rights Management
                WorkflowStep(
                    step_id="rights_management",
                    name="Digital Rights Management Setup",
                    description="Configure comprehensive rights management and licensing",
                    service_endpoint="/api/v1/rights/setup-management",
                    dependencies=["ai_fingerprinting"],
                    timeout_seconds=120,
                    retry_count=2,
                    parameters={
                        "rights_granularity": "maximum",
                        "licensing_automation": True,
                        "usage_monitoring": True,
                        "violation_detection": True
                    }
                ),
                
                # Step 9: Performance Analytics Initialization
                WorkflowStep(
                    step_id="performance_analytics",
                    name="Performance Analytics & Reporting Setup",
                    description="Initialize comprehensive performance analytics and reporting",
                    service_endpoint="/api/v1/analytics/setup-performance",
                    dependencies=["automated_monetization", "rights_management"],
                    timeout_seconds=90,
                    retry_count=2,
                    parameters={
                        "analytics_depth": "comprehensive",
                        "real_time_dashboards": True,
                        "predictive_analytics": True,
                        "cross_platform_correlation": True
                    }
                )
            ],
            priority=WorkflowPriority.HIGH,
            max_execution_time=3600,  # 1 hour maximum
            retry_policy={
                'max_attempts': 3,
                'backoff_strategy': 'exponential',
                'max_backoff_seconds': 300
            }
        )
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the entire coordination service."""



        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Collect metrics from all components
            component_metrics = {
                'workflow_coordinator': self.workflow_coordinator.get_execution_metrics(),
                'process_manager': self.process_manager.get_system_metrics(),
                'task_scheduler': self.task_scheduler.get_scheduler_metrics(),
                'resource_coordinator': self.resource_coordinator.get_system_metrics(),
                'state_manager': self.state_manager.get_state_metrics(),
                'event_dispatcher': self.event_dispatcher.get_system_metrics(),
                'sync_manager': self.sync_manager.get_system_metrics(),
                'dependency_resolver': self.dependency_resolver.get_resolution_metrics()
            }
            
            return {
                'service_id': self.service_id,
                'status': self.status.value,
                'uptime_seconds': uptime,
                'start_time': self.start_time.isoformat(),
                'configuration': {
                    'max_workflows': self.config.max_workflows,
                    'max_processes': self.config.max_processes,
                    'max_tasks': self.config.max_tasks,
                    'monitoring_interval': self.config.monitoring_interval
                },
                'metrics': self.metrics,
                'component_metrics': component_metrics,
                'health_summary': self._get_health_summary(),
                'performance_indicators': self._calculate_performance_indicators(),
                'business_metrics': self._calculate_business_metrics()
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive status: {e}")
            return {
                'service_id': self.service_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_health_summary(self) -> Dict[str, Any]:
        """Get summary of component health status."""
        components = [
            'workflow_coordinator', 'process_manager', 'task_scheduler',
            'resource_coordinator', 'state_manager', 'event_dispatcher',
            'sync_manager', 'dependency_resolver'
        ]
        
        health_summary = {
            'total_components': len(components),
            'healthy_components': 0,
            'degraded_components': 0,
            'critical_components': 0,
            'unknown_components': 0
        }
        
        for component_name in components:
            try:
                component = getattr(self, component_name)
                health = self._check_component_health(component)
                status = health.get('status', ServiceHealthStatus.UNKNOWN)
                
                if status == ServiceHealthStatus.HEALTHY:
                    health_summary['healthy_components'] += 1
                elif status == ServiceHealthStatus.DEGRADED:
                    health_summary['degraded_components'] += 1
                elif status == ServiceHealthStatus.CRITICAL:
                    health_summary['critical_components'] += 1
                else:
                    health_summary['unknown_components'] += 1
                    
            except Exception:
                health_summary['unknown_components'] += 1
        
        health_summary['health_percentage'] = (
            health_summary['healthy_components'] / health_summary['total_components'] * 100
        )
        
        return health_summary
    
    def _calculate_performance_indicators(self) -> Dict[str, Any]:
        """Calculate key performance indicators."""



        try:
            total_requests = self.metrics['total_requests']
            if total_requests == 0:
                return {'status': 'no_data'}
            
            success_rate = (self.metrics['successful_requests'] / total_requests) * 100
            
            return {
                'success_rate_percentage': success_rate,
                'average_response_time_seconds': self.metrics['average_response_time'],
                'throughput_requests_per_second': total_requests / max((datetime.now() - self.start_time).total_seconds(), 1),
                'total_workflows_executed': self.metrics['total_workflows_executed'],
                'total_processes_managed': self.metrics['total_processes_managed'],
                'total_tasks_scheduled': self.metrics['total_tasks_scheduled'],
                'total_resources_allocated': self.metrics['total_resources_allocated'],
                'peak_concurrent_operations': self.metrics['peak_concurrent_operations']
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance indicators: {e}")
            return {'error': str(e)}
    
    def _calculate_business_metrics(self) -> Dict[str, Any]:
        """Calculate business-specific metrics for the IA-Influencer-Agent platform."""



        try:
            # This would be implemented with actual business logic
            # For now, return placeholder metrics
            return {
                'content_processing_efficiency': 95.5,
                'protection_coverage_percentage': 99.2,
                'revenue_optimization_rate': 87.3,
                'collaboration_discovery_success_rate': 78.9,
                'platform_sync_accuracy': 96.7,
                'ai_fingerprinting_success_rate': 99.8,
                'automated_monetization_effectiveness': 84.6
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate business metrics: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a quick health check of the coordination service."""



        try:
            start_time = time.time()
            
            # Quick component checks
            component_status = {}
            for component_name in ['workflow_coordinator', 'process_manager', 'task_scheduler']:
                try:
                    component = getattr(self, component_name)
                    if hasattr(component, 'health_check'):
                        component_status[component_name] = 'healthy'
                    else:
                        component_status[component_name] = 'healthy'
                except Exception:
                    component_status[component_name] = 'error'
            
            response_time = time.time() - start_time
            
            return {
                'status': self.status.value,
                'service_id': self.service_id,
                'response_time_seconds': response_time,
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'component_status': component_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def shutdown(self):
        """Gracefully shutdown the coordination service."""
        logger.info("Initiating coordination service shutdown...")
        self.status = CoordinationServiceStatus.STOPPING
        
        try:
            # Signal shutdown to health monitor
            self._shutdown_event.set()
            
            # Shutdown components in reverse order of dependency
            components = [
                ('dependency_resolver', self.dependency_resolver),
                ('sync_manager', self.sync_manager),
                ('event_dispatcher', self.event_dispatcher),
                ('state_manager', self.state_manager),
                ('resource_coordinator', self.resource_coordinator),
                ('task_scheduler', self.task_scheduler),
                ('process_manager', self.process_manager),
                ('workflow_coordinator', self.workflow_coordinator)
            ]
            
            for component_name, component in components:
                try:
                    if hasattr(component, 'shutdown'):
                        await component.shutdown()
                    elif hasattr(component, 'stop'):
                        component.stop()
                    logger.info(f"Successfully shutdown {component_name}")
                except Exception as e:
                    logger.error(f"Error shutting down {component_name}: {e}")
            
            # Wait for health monitor to finish
            if self._health_monitor_task and self._health_monitor_task.is_alive():
                self._health_monitor_task.join(timeout=5)
            
            self.status = CoordinationServiceStatus.STOPPED
            logger.info("Coordination service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during coordination service shutdown: {e}")
            self.status = CoordinationServiceStatus.ERROR
            raise


# Global coordination service instance
_coordination_service: Optional[CoordinationService] = None
_service_lock = threading.Lock()


def get_coordination_service(config: Optional[CoordinationServiceConfig] = None) -> CoordinationService:
    """
    Get the global coordination service instance (singleton pattern).
    
    Args:
        config: Optional configuration for the service
        
    Returns:
        CoordinationService instance
    """
    global _coordination_service
    
    with _service_lock:
        if _coordination_service is None:
            _coordination_service = CoordinationService(config)
        return _coordination_service


async def execute_content_workflow(
    content_data: Dict[str, Any],
    user_id: str,
    platform_targets: List[str],
    workflow_options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to execute content workflow using the global service instance.
    
    Args:
        content_data: Content information including file path, type, metadata
        user_id: User identifier
        platform_targets: List of target platforms
        workflow_options: Additional workflow configuration options
        
    Returns:
        Execution ID for tracking the workflow progress
    """
    coordination_service = get_coordination_service()
    return await coordination_service.execute_content_workflow(
        content_data=content_data,
        user_id=user_id,
        platform_targets=platform_targets,
        workflow_options=workflow_options
    )


async def get_service_status() -> Dict[str, Any]:
    """Get comprehensive status of the coordination service."""
    coordination_service = get_coordination_service()
    return await coordination_service.get_comprehensive_status()


async def perform_health_check() -> Dict[str, Any]:
    """Perform a health check of the coordination service."""
    coordination_service = get_coordination_service()
    return await coordination_service.health_check()


@asynccontextmanager
async def coordination_service_context(config: Optional[CoordinationServiceConfig] = None):
    """
    Async context manager for coordination service lifecycle management.
    
    Usage:
        async with coordination_service_context() as service:
            execution_id = await service.execute_content_workflow(...)
    """
    service = get_coordination_service(config)
    try:
        yield service
    finally:
        await service.shutdown()


# Legacy compatibility - keep existing CoordinationModule for backward compatibility
class CoordinationModule:
    """
    Legacy coordination module class for backward compatibility.
    
    This class provides access to all coordination components through a unified interface.
    For new implementations, use CoordinationService instead.
    """
    
    def __init__(self):
        """Initialize coordination module with all components."""
        self.workflow_coordinator = WorkflowCoordinator()
        self.process_manager = ProcessManager()
        self.task_scheduler = TaskScheduler()
        self.resource_coordinator = ResourceCoordinator()
        self.state_manager = StateManager()
        self.event_dispatcher = EventDispatcher()
        self.sync_manager = SyncManager()
        self.dependency_resolver = DependencyResolver()
        
        logger.info("CoordinationModule initialized (legacy mode)")
    
    def start_all_services(self):
        """Start all coordination services."""



        try:
            self.process_manager.start_monitoring()
            self.resource_coordinator.start_monitoring()
            self.task_scheduler.start_scheduler()
            logger.info("All coordination services started")
        except Exception as e:
            logger.error(f"Failed to start coordination services: {e}")
            raise
    
    def stop_all_services(self):
        """Stop all coordination services."""



        try:
            if hasattr(self.task_scheduler, 'stop_scheduler'):
                self.task_scheduler.stop_scheduler()
            if hasattr(self.process_manager, 'stop_monitoring'):
                self.process_manager.stop_monitoring()
            if hasattr(self.resource_coordinator, 'stop_monitoring'):
                self.resource_coordinator.stop_monitoring()
            logger.info("All coordination services stopped")
        except Exception as e:
            logger.error(f"Failed to stop coordination services: {e}")


# Export main components and utilities
__all__ = [
    'CoordinationService',
    'CoordinationServiceConfig',
    'CoordinationServiceStatus',
    'ServiceHealthStatus',
    'ServiceMetrics',
    'CoordinationModule',  # Legacy compatibility
    'get_coordination_service',
    'execute_content_workflow',
    'get_service_status',
    'perform_health_check',
    'coordination_service_context',
    # Individual components
    'WorkflowCoordinator',
    'ProcessManager',
    'TaskScheduler',
    'ResourceCoordinator',
    'StateManager',
    'EventDispatcher',
    'SyncManager',
    'DependencyResolver'
]


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        """Example usage of the coordination service."""
        # Initialize service with custom configuration
        config = CoordinationServiceConfig(
            max_workflows=50,
            max_processes=100,
            enable_ai_optimization=True
        )
        
        # Use context manager for proper lifecycle management
        async with coordination_service_context(config) as service:
            # Execute a content workflow
            execution_id = await service.execute_content_workflow(
                content_data={
                    "file_path": "/uploads/example_content.mp4",
                    "content_type": "video",
                    "title": "Example Creative Content",
                    "metadata": {
                        "duration": 180,
                        "format": "mp4",
                        "resolution": "1920x1080"
                    }
                },
                user_id="creator_123",
                platform_targets=["spotify", "youtube", "tiktok", "instagram"],
                workflow_options={
                    "priority": "high",
                    "expedited_processing": True
                }
            )
            
            print(f"Content workflow started with execution ID: {execution_id}")
            
            # Get service status
            status = await service.get_comprehensive_status()
            print(f"Service status: {status['status']}")
            print(f"Uptime: {status['uptime_seconds']} seconds")
            print(f"Total workflows executed: {status['metrics']['total_workflows_executed']}")
    
    # Run the example
    asyncio.run(main())
        
        # System state
        self.initialized = False
        self.startup_time: Optional[datetime] = None
        self.shutdown_requested = False
        
        # Performance tracking
        self.system_metrics: Dict[str, Any] = {}
        self.health_checks_enabled = True
        
        logger.info("CoordinationModule instance created")
    
    async def initialize(self) -> bool:
        """Initialize all coordination components"""



        try:
            self.startup_time = datetime.now(timezone.utc)
            
            logger.info("Initializing coordination system...")
            
            # Initialize core components
            await self._initialize_workflow_coordinator()
            await self._initialize_process_manager()
            await self._initialize_task_scheduler()
            await self._initialize_resource_coordinator()
            await self._initialize_state_manager()
            await self._initialize_event_dispatcher()
            await self._initialize_sync_manager()
            await self._initialize_dependency_resolver()
            
            # Setup inter-component connections
            await self._setup_component_connections()
            
            # Start monitoring if enabled
            if self.config.enable_monitoring:
                await self._start_system_monitoring()
            
            self.initialized = True
            logger.info("Coordination system initialized successfully")
            
            # Emit system ready event
            await self._emit_system_event("coordination_system_ready", {
                "startup_time": self.startup_time.isoformat(),
                "components": list(self.components.keys())
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Coordination system initialization failed: {e}")
            await self.shutdown()
            return False
    
    async def _initialize_workflow_coordinator(self):
        """Initialize workflow coordinator component"""



        try:
            workflow_coordinator = WorkflowCoordinator(
                max_concurrent_workflows=self.config.max_concurrent_workflows
            )
            
            self.components["workflow_coordinator"] = workflow_coordinator
            self.component_status["workflow_coordinator"] = ComponentStatus(
                component_name="workflow_coordinator",
                component_type="coordinator",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("WorkflowCoordinator initialized")
            
        except Exception as e:
            logger.error(f"WorkflowCoordinator initialization failed: {e}")
            raise
    
    async def _initialize_process_manager(self):
        """Initialize process manager component"""



        try:
            process_manager = ProcessManager(
                max_processes=self.config.max_processes,
                monitoring_interval=self.config.monitoring_interval
            )
            
            self.components["process_manager"] = process_manager
            self.component_status["process_manager"] = ComponentStatus(
                component_name="process_manager",
                component_type="manager",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("ProcessManager initialized")
            
        except Exception as e:
            logger.error(f"ProcessManager initialization failed: {e}")
            raise
    
    async def _initialize_task_scheduler(self):
        """Initialize task scheduler component"""



        try:
            task_scheduler = TaskScheduler(
                max_concurrent_tasks=self.config.max_concurrent_tasks
            )
            
            self.components["task_scheduler"] = task_scheduler
            self.component_status["task_scheduler"] = ComponentStatus(
                component_name="task_scheduler",
                component_type="scheduler",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("TaskScheduler initialized")
            
        except Exception as e:
            logger.error(f"TaskScheduler initialization failed: {e}")
            raise
    
    async def _initialize_resource_coordinator(self):
        """Initialize resource coordinator component"""



        try:
            resource_coordinator = ResourceCoordinator(
                monitoring_interval=self.config.monitoring_interval
            )
            
            self.components["resource_coordinator"] = resource_coordinator
            self.component_status["resource_coordinator"] = ComponentStatus(
                component_name="resource_coordinator",
                component_type="coordinator",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("ResourceCoordinator initialized")
            
        except Exception as e:
            logger.error(f"ResourceCoordinator initialization failed: {e}")
            raise
    
    async def _initialize_state_manager(self):
        """Initialize state manager component"""



        try:
            state_manager = StateManager()
            
            self.components["state_manager"] = state_manager
            self.component_status["state_manager"] = ComponentStatus(
                component_name="state_manager",
                component_type="manager",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("StateManager initialized")
            
        except Exception as e:
            logger.error(f"StateManager initialization failed: {e}")
            raise
    
    async def _initialize_event_dispatcher(self):
        """Initialize event dispatcher component"""



        try:
            event_dispatcher = EventDispatcher()
            
            self.components["event_dispatcher"] = event_dispatcher
            self.component_status["event_dispatcher"] = ComponentStatus(
                component_name="event_dispatcher",
                component_type="dispatcher",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("EventDispatcher initialized")
            
        except Exception as e:
            logger.error(f"EventDispatcher initialization failed: {e}")
            raise
    
    async def _initialize_sync_manager(self):
        """Initialize sync manager component"""



        try:
            sync_manager = SyncManager()
            
            self.components["sync_manager"] = sync_manager
            self.component_status["sync_manager"] = ComponentStatus(
                component_name="sync_manager",
                component_type="manager",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("SyncManager initialized")
            
        except Exception as e:
            logger.error(f"SyncManager initialization failed: {e}")
            raise
    
    async def _initialize_dependency_resolver(self):
        """Initialize dependency resolver component"""



        try:
            dependency_resolver = DependencyResolver(
                cache_size=self.config.cache_size,
                max_resolution_depth=self.config.max_resolution_depth
            )
            
            self.components["dependency_resolver"] = dependency_resolver
            self.component_status["dependency_resolver"] = ComponentStatus(
                component_name="dependency_resolver",
                component_type="resolver",
                status="initialized",
                initialized_at=datetime.now(timezone.utc),
                last_health_check=datetime.now(timezone.utc)
            )
            
            logger.info("DependencyResolver initialized")
            
        except Exception as e:
            logger.error(f"DependencyResolver initialization failed: {e}")
            raise
    
    async def _setup_component_connections(self):
        """Setup connections and integrations between components"""



        try:
            # Connect event dispatcher to all components
            event_dispatcher = self.components["event_dispatcher"]
            
            # Register workflow events
            if "workflow_coordinator" in self.components:
                workflow_coordinator = self.components["workflow_coordinator"]
                workflow_coordinator.register_event_handler(
                    "workflow_started",
                    self._handle_workflow_event
                )
                workflow_coordinator.register_event_handler(
                    "workflow_completed",
                    self._handle_workflow_event
                )
                workflow_coordinator.register_event_handler(
                    "workflow_failed",
                    self._handle_workflow_event
                )
            
            # Register process events
            if "process_manager" in self.components:
                process_manager = self.components["process_manager"]
                process_manager.register_event_handler(
                    "process_started",
                    self._handle_process_event
                )
                process_manager.register_event_handler(
                    "process_completed",
                    self._handle_process_event
                )
                process_manager.register_event_handler(
                    "process_failed",
                    self._handle_process_event
                )
            
            # Register task events
            if "task_scheduler" in self.components:
                task_scheduler = self.components["task_scheduler"]
                task_scheduler.register_event_handler(
                    "task_started",
                    self._handle_task_event
                )
                task_scheduler.register_event_handler(
                    "task_completed",
                    self._handle_task_event
                )
                task_scheduler.register_event_handler(
                    "task_failed",
                    self._handle_task_event
                )
            
            # Register resource events
            if "resource_coordinator" in self.components:
                resource_coordinator = self.components["resource_coordinator"]
                resource_coordinator.register_event_handler(
                    "resources_allocated",
                    self._handle_resource_event
                )
                resource_coordinator.register_event_handler(
                    "resource_deallocated",
                    self._handle_resource_event
                )
                resource_coordinator.register_event_handler(
                    "health_changed",
                    self._handle_resource_event
                )
            
            logger.info("Component connections established")
            
        except Exception as e:
            logger.error(f"Component connection setup failed: {e}")
            raise
    
    async def _start_system_monitoring(self):
        """Start system-wide monitoring"""



        try:
            # Start component monitoring
            if "process_manager" in self.components:
                self.components["process_manager"].start_monitoring()
            
            if "resource_coordinator" in self.components:
                self.components["resource_coordinator"].start_monitoring()
            
            if "task_scheduler" in self.components:
                self.components["task_scheduler"].start_scheduler()
            
            # Start health check loop
            if self.health_checks_enabled:
                asyncio.create_task(self._health_check_loop())
            
            logger.info("System monitoring started")
            
        except Exception as e:
            logger.error(f"System monitoring start failed: {e}")
            raise
    
    async def _health_check_loop(self):
        """Continuous health check loop for all components"""
        while self.initialized and not self.shutdown_requested:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.monitoring_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all components"""



        try:
            for component_name, component in self.components.items():
                try:
                    # Update health check timestamp
                    self.component_status[component_name].last_health_check = datetime.now(timezone.utc)
                    
                    # Perform component-specific health checks
                    if hasattr(component, 'get_system_metrics'):
                        metrics = component.get_system_metrics()
                        self.component_status[component_name].performance_metrics = metrics
                    
                    # Update component status
                    self.component_status[component_name].status = "healthy"
                    
                except Exception as e:
                    logger.error(f"Health check failed for {component_name}: {e}")
                    self.component_status[component_name].error_count += 1
                    self.component_status[component_name].health_score = max(
                        0, self.component_status[component_name].health_score - 10
                    )
                    self.component_status[component_name].status = "degraded"
            
        except Exception as e:
            logger.error(f"Health check execution failed: {e}")
    
    async def _handle_workflow_event(self, event_data: Dict[str, Any]):
        """Handle workflow events"""



        try:
            logger.debug(f"Workflow event received: {event_data}")
            # Forward to event dispatcher if available
            if "event_dispatcher" in self.components:
                await self.components["event_dispatcher"].dispatch_event(
                    event_type="workflow_event",
                    payload=event_data
                )
        except Exception as e:
            logger.error(f"Workflow event handling failed: {e}")
    
    async def _handle_process_event(self, event_data: Dict[str, Any]):
        """Handle process events"""



        try:
            logger.debug(f"Process event received: {event_data}")
            # Forward to event dispatcher if available
            if "event_dispatcher" in self.components:
                await self.components["event_dispatcher"].dispatch_event(
                    event_type="process_event",
                    payload=event_data
                )
        except Exception as e:
            logger.error(f"Process event handling failed: {e}")
    
    async def _handle_task_event(self, event_data: Dict[str, Any]):
        """Handle task events"""



        try:
            logger.debug(f"Task event received: {event_data}")
            # Forward to event dispatcher if available
            if "event_dispatcher" in self.components:
                await self.components["event_dispatcher"].dispatch_event(
                    event_type="task_event",
                    payload=event_data
                )
        except Exception as e:
            logger.error(f"Task event handling failed: {e}")
    
    async def _handle_resource_event(self, event_data: Dict[str, Any]):
        """Handle resource events"""



        try:
            logger.debug(f"Resource event received: {event_data}")
            # Forward to event dispatcher if available
            if "event_dispatcher" in self.components:
                await self.components["event_dispatcher"].dispatch_event(
                    event_type="resource_event",
                    payload=event_data
                )
        except Exception as e:
            logger.error(f"Resource event handling failed: {e}")
    
    async def _emit_system_event(self, event_type: str, data: Dict[str, Any]):
        """Emit system-level events"""



        try:
            if "event_dispatcher" in self.components:
                await self.components["event_dispatcher"].dispatch_event(
                    event_type="system_event",
                    payload={
                        "system_event_type": event_type,
                        **data
                    }
                )
        except Exception as e:
            logger.error(f"System event emission failed: {e}")
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a specific component by name"""



        return self.components.get(component_name)
    
    def get_component_status(self, component_name: str) -> Optional[ComponentStatus]:
        """Get status information for a specific component"""



        return self.component_status.get(component_name)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_components = len(self.components)
        healthy_components = len([
            status for status in self.component_status.values()
            if status.status == "healthy"
        ])
        
        overall_health = (healthy_components / total_components * 100) if total_components > 0 else 0
        
        return {
            "system_initialized": self.initialized,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "total_components": total_components,
            "healthy_components": healthy_components,
            "overall_health_percentage": overall_health,
            "uptime_seconds": (
                datetime.now(timezone.utc) - self.startup_time
            ).total_seconds() if self.startup_time else 0,
            "component_status": {
                name: {
                    "status": status.status,
                    "health_score": status.health_score,
                    "error_count": status.error_count,
                    "last_health_check": status.last_health_check.isoformat()
                }
                for name, status in self.component_status.items()
            }
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        metrics = {}
        
        for component_name, component in self.components.items():
            if hasattr(component, 'get_system_metrics'):
                try:
                    component_metrics = component.get_system_metrics()
                    metrics[component_name] = component_metrics
                except Exception as e:
                    logger.error(f"Failed to get metrics for {component_name}: {e}")
                    metrics[component_name] = {"error": str(e)}
        
        return {
            "system_status": self.get_system_status(),
            "component_metrics": metrics,
            "collected_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self):
        """Graceful shutdown of all coordination components"""



        try:
            self.shutdown_requested = True
            self.health_checks_enabled = False
            
            logger.info("Shutting down coordination system...")
            
            # Emit shutdown event
            await self._emit_system_event("coordination_system_shutdown", {
                "shutdown_time": datetime.now(timezone.utc).isoformat()
            })
            
            # Shutdown components in reverse order
            shutdown_order = [
                "dependency_resolver",
                "sync_manager", 
                "event_dispatcher",
                "state_manager",
                "resource_coordinator",
                "task_scheduler",
                "process_manager",
                "workflow_coordinator"
            ]
            
            for component_name in shutdown_order:
                if component_name in self.components:
                    try:
                        component = self.components[component_name]
                        if hasattr(component, 'shutdown'):
                            component.shutdown()
                        elif hasattr(component, 'stop_monitoring'):
                            component.stop_monitoring()
                        elif hasattr(component, 'stop_scheduler'):
                            component.stop_scheduler()
                        
                        self.component_status[component_name].status = "shutdown"
                        logger.info(f"Component {component_name} shutdown completed")
                        
                    except Exception as e:
                        logger.error(f"Component {component_name} shutdown failed: {e}")
            
            self.initialized = False
            logger.info("Coordination system shutdown completed")
            
        except Exception as e:
            logger.error(f"Coordination system shutdown failed: {e}")


# Convenience function for easy initialization
async def create_coordination_system(config: Optional[CoordinationConfig] = None) -> CoordinationModule:
    """
    Create and initialize a coordination system with the specified configuration.
    
    Args:
        config: Optional configuration for the coordination system
        
    Returns:
        Initialized CoordinationModule instance
    """
    coordination_module = CoordinationModule(config)
    
    if await coordination_module.initialize():
        return coordination_module
    else:
        raise RuntimeError("Failed to initialize coordination system")


# Global coordination module instance (singleton pattern)
_global_coordination_module: Optional[CoordinationModule] = None


async def get_coordination_module(config: Optional[CoordinationConfig] = None) -> CoordinationModule:
    """
    Get the global coordination module instance, creating it if necessary.
    
    Args:
        config: Optional configuration for initialization (only used on first call)
        
    Returns:
        Global CoordinationModule instance
    """
    global _global_coordination_module
    
    if _global_coordination_module is None:
        _global_coordination_module = await create_coordination_system(config)
    
    return _global_coordination_module


async def shutdown_coordination_system():
    """Shutdown the global coordination system"""
    global _global_coordination_module
    
    if _global_coordination_module is not None:
        await _global_coordination_module.shutdown()
        _global_coordination_module = None
