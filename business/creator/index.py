"""Creator Management System - Central Orchestration Hub

Ultra-sophisticated central orchestration system for the complete creator management
ecosystem. This module serves as the main entry point and coordinator for all
creator-related operations, integrating profile management, registration, authentication,
analytics, monetization, and collaboration features.

Business Logic Flow:
System Initialization → Service Registration → Creator Lifecycle Management →
Real-Time Monitoring → Performance Optimization → Graceful Shutdown

Project: IA Influencer Agent + Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from contextlib import asynccontextmanager

# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from fastapi import HTTPException, status
import aiohttp

# Internal imports
from ...core.database import get_async_session, get_db_engine
from ...core.config import get_settings, Settings
from ...core.cache import CacheManager
from ...core.security import SecurityManager
from ...core.logging import get_logger
from ...core.monitoring import MetricsCollector
from ...core.email import EmailService
from ...core.sms import SMSService

# Creator module imports
from .profile_manager import (
    CreatorProfileManager, CreatorProfile, CreatorType,
    VerificationLevel, ProfessionalTier
)
from .registration_handler import (
    CreatorRegistrationHandler, RegistrationWorkflow,
    OnboardingPipeline, KYCProcessor
)
from .authentication_system import (
    CreatorAuthenticationSystem, MultiFactorAuth,
    SessionManager, SecurityController
)
from .dashboard_controller import (
    CreatorDashboardController, RealTimeAnalytics,
    PerformanceMetrics, InsightEngine
)
from .monetization_engine import (
    CreatorMonetizationEngine, RevenueTracker,
    PaymentProcessor, TaxComplianceManager
)
from .collaboration_hub import (
    CreatorCollaborationHub, MatchingEngine,
    PartnershipManager, ProjectCoordinator
)
from .content_portfolio import (
    CreatorContentPortfolio, ShowcaseManager,
    AchievementTracker, QualityAssessment
)
from .verification_system import (
    CreatorVerificationSystem, IdentityVerification,
    ProfessionalVerification, BadgeManager
)
from .analytics_aggregator import (
    CreatorAnalyticsAggregator, MultiPlatformDataCollector,
    MetricsProcessor, ReportGenerator
)
from .notification_manager import (
    CreatorNotificationManager, RealTimeNotifications,
    AlertSystem, CommunicationHub
)

# Configure logging
logger = get_logger(__name__)


class SystemStatus(Enum):
    """
Creator management system status"""

    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class ServiceHealth(Enum):
    """Individual service health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_creators: int = 0
    active_creators: int = 0
    registrations_today: int = 0
    verifications_pending: int = 0
    collaborations_active: int = 0
    revenue_today: float = 0.0
    
    # Performance metrics
    avg_response_time: float = 0.0
    success_rate: float = 100.0
    error_rate: float = 0.0
    
    # Resource utilization
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    database_connections: int = 0
    cache_hit_rate: float = 0.0


@dataclass
class ServiceRegistry:
    """
Registry of all creator management services"""
    profile_manager: Optional[CreatorProfileManager] = None
    registration_handler: Optional[CreatorRegistrationHandler] = None
    authentication_system: Optional[CreatorAuthenticationSystem] = None
    dashboard_controller: Optional[CreatorDashboardController] = None
    monetization_engine: Optional[CreatorMonetizationEngine] = None
    collaboration_hub: Optional[CreatorCollaborationHub] = None
    content_portfolio: Optional[CreatorContentPortfolio] = None
    verification_system: Optional[CreatorVerificationSystem] = None
    analytics_aggregator: Optional[CreatorAnalyticsAggregator] = None
    notification_manager: Optional[CreatorNotificationManager] = None
    
    # Core services
    cache_manager: Optional[CacheManager] = None
    security_manager: Optional[SecurityManager] = None
    email_service: Optional[EmailService] = None
    sms_service: Optional[SMSService] = None
    metrics_collector: Optional[MetricsCollector] = None


class CreatorManagementSystem:
    """
    Central Creator Management System
    
    Ultra-sophisticated orchestration hub managing the complete creator ecosystem.
    Provides unified interface for all creator-related operations, monitoring,
    and optimization across the platform.
    
    Key Responsibilities:
    - Service initialization and lifecycle management
    - Real-time monitoring and health checks
    - Performance optimization and scaling
    - Event coordination and messaging
    - Resource management and cleanup
    - Error handling and recovery
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.logger = get_logger(self.__class__.__name__)
        
        # System state
        self.status = SystemStatus.INITIALIZING
        self.initialized_at: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        
        # Service registry
        self.services = ServiceRegistry()
        
        # Database and external connections
        self.db_engine: Optional[AsyncEngine] = None
        self.redis_client: Optional[redis.Redis] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        
        # Metrics and monitoring
        self.metrics = SystemMetrics()
        self.service_health: Dict[str, ServiceHealth] = {}
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        self.logger.info("Creator Management System initialized")
    
    async def initialize(self) -> None:
        """
        Initialize the complete creator management system
        
        Performs comprehensive system initialization including:
        - Database connections
        - Cache setup
        - Service initialization
        - Background task startup
        - Health monitoring
        """
        try:
            self.logger.info("Starting Creator Management System initialization...")
            self.status = SystemStatus.INITIALIZING
            
            # Initialize database connection
            await self._initialize_database()
            
            # Initialize cache and external services
            await self._initialize_external_services()
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Initialize business services
            await self._initialize_business_services()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Perform initial health check
            await self._perform_health_check()
            
            # Set system as running
            self.status = SystemStatus.RUNNING
            self.initialized_at = datetime.utcnow()
            
            self.logger.info("Creator Management System initialization completed successfully")
            
            # Emit system ready event
            await self._emit_event("system_ready", {
                'initialized_at': self.initialized_at.isoformat(),
                'services_count': len([s for s in self.services.__dict__.values() if s is not None])
            })
            
        except Exception as e:
            self.status = SystemStatus.ERROR
            self.logger.error(f"System initialization failed: {e}")
            await self._cleanup()
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status information
        
        Returns:
            Complete system status including metrics, health, and service information
        """
        try:
            # Update metrics
            await self._update_system_metrics()
            
            return {
                'status': self.status.value,
                'initialized_at': self.initialized_at.isoformat() if self.initialized_at else None,
                'uptime_seconds': (datetime.utcnow() - self.initialized_at).total_seconds() if self.initialized_at else 0,
                'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
                
                # System metrics
                'metrics': {
                    'total_creators': self.metrics.total_creators,
                    'active_creators': self.metrics.active_creators,
                    'registrations_today': self.metrics.registrations_today,
                    'verifications_pending': self.metrics.verifications_pending,
                    'collaborations_active': self.metrics.collaborations_active,
                    'revenue_today': self.metrics.revenue_today,
                    'avg_response_time': self.metrics.avg_response_time,
                    'success_rate': self.metrics.success_rate,
                    'error_rate': self.metrics.error_rate,
                    'cpu_usage': self.metrics.cpu_usage,
                    'memory_usage': self.metrics.memory_usage,
                    'database_connections': self.metrics.database_connections,
                    'cache_hit_rate': self.metrics.cache_hit_rate
                },
                
                # Service health
                'service_health': {
                    service_name: health.value 
                    for service_name, health in self.service_health.items()
                },
                
                # Background tasks
                'background_tasks': {
                    'total': len(self._background_tasks),
                    'running': len([task for task in self._background_tasks if not task.done()]),
                    'completed': len([task for task in self._background_tasks if task.done() and not task.exception()]),
                    'failed': len([task for task in self._background_tasks if task.done() and task.exception()])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_creator_manager(self) -> CreatorProfileManager:
        """Get the creator profile manager instance"""
        if not self.services.profile_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Creator profile manager not available"
            )
        return self.services.profile_manager
    
    async def get_registration_handler(self) -> CreatorRegistrationHandler:
        """Get the registration handler instance"""
        if not self.services.registration_handler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registration handler not available"
            )
        return self.services.registration_handler
    
    async def get_dashboard_controller(self) -> CreatorDashboardController:
        """Get the dashboard controller instance"""
        if not self.services.dashboard_controller:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Dashboard controller not available"
            )
        return self.services.dashboard_controller
    
    async def get_monetization_engine(self) -> CreatorMonetizationEngine:
        """Get the monetization engine instance"""
        if not self.services.monetization_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Monetization engine not available"
            )
        return self.services.monetization_engine
    
    async def get_collaboration_hub(self) -> CreatorCollaborationHub:
        """Get the collaboration hub instance"""
        if not self.services.collaboration_hub:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Collaboration hub not available"
            )
        return self.services.collaboration_hub
    
    async def register_event_handler(self, event_name: str, handler: Callable) -> None:
        """Register an event handler"""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
        self.logger.debug(f"Registered handler for event: {event_name}")
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the creator management system
        
        Performs cleanup of all resources including:
        - Background task cancellation
        - Database connection cleanup
        - Cache cleanup
        - Service shutdown
        """
        try:
            self.logger.info("Initiating Creator Management System shutdown...")
            self.status = SystemStatus.SHUTDOWN
            
            # Signal shutdown to background tasks
            self._shutdown_event.set()
            
            # Cancel background tasks
            await self._cancel_background_tasks()
            
            # Shutdown services
            await self._shutdown_services()
            
            # Cleanup resources
            await self._cleanup()
            
            self.logger.info("Creator Management System shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during system shutdown: {e}")
            raise
    
    # Private initialization methods
    
    async def _initialize_database(self) -> None:
        """Initialize database connections"""
        try:
            self.logger.info("Initializing database connections...")
            
            # Create async database engine
            self.db_engine = get_db_engine()
            
            # Test connection
            async with self.db_engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            self.logger.info("Database connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _initialize_external_services(self) -> None:
        """Initialize external services (cache, redis, etc.)"""
        try:
            self.logger.info("Initializing external services...")
            
            # Initialize cache manager
            self.services.cache_manager = CacheManager()
            await self.services.cache_manager.initialize()
            
            # Initialize Redis client
            redis_url = self.settings.REDIS_URL
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Initialize HTTP session
            self.http_session = aiohttp.ClientSession()
            
            self.logger.info("External services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"External services initialization failed: {e}")
            raise
    
    async def _initialize_core_services(self) -> None:
        """Initialize core system services"""
        try:
            self.logger.info("Initializing core services...")
            
            # Initialize security manager
            self.services.security_manager = SecurityManager()
            
            # Initialize email service
            self.services.email_service = EmailService()
            
            # Initialize SMS service
            self.services.sms_service = SMSService()
            
            # Initialize metrics collector
            self.services.metrics_collector = MetricsCollector()
            
            self.logger.info("Core services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Core services initialization failed: {e}")
            raise
    
    async def _initialize_business_services(self) -> None:
        """Initialize business logic services"""
        try:
            self.logger.info("Initializing business services...")
            
            # Create database session for services
            async_session = sessionmaker(
                self.db_engine, class_=AsyncSession, expire_on_commit=False
            )()
            
            # Initialize profile manager
            self.services.profile_manager = CreatorProfileManager(
                async_session,
                self.services.cache_manager,
                self.services.security_manager
            )
            
            # Initialize registration handler
            self.services.registration_handler = CreatorRegistrationHandler(async_session)
            
            # Initialize authentication system
            self.services.authentication_system = CreatorAuthenticationSystem(
                async_session,
                self.services.cache_manager,
                self.services.security_manager
            )
            
            # Initialize dashboard controller
            self.services.dashboard_controller = CreatorDashboardController(
                self.services.profile_manager,
                self.services.cache_manager
            )
            
            # Initialize monetization engine
            self.services.monetization_engine = CreatorMonetizationEngine(
                async_session,
                self.services.profile_manager,
                self.services.cache_manager
            )
            
            # Initialize collaboration hub
            self.services.collaboration_hub = CreatorCollaborationHub(
                async_session,
                self.services.profile_manager,
                self.services.cache_manager
            )
            
            # Initialize content portfolio
            self.services.content_portfolio = CreatorContentPortfolio(
                async_session,
                self.services.profile_manager
            )
            
            # Initialize verification system
            self.services.verification_system = CreatorVerificationSystem(
                async_session,
                self.services.profile_manager,
                self.services.cache_manager
            )
            
            # Initialize analytics aggregator
            self.services.analytics_aggregator = CreatorAnalyticsAggregator(
                async_session,
                self.services.cache_manager
            )
            
            # Initialize notification manager
            self.services.notification_manager = CreatorNotificationManager(
                self.services.cache_manager,
                self.services.email_service,
                self.services.sms_service
            )
            
            self.logger.info("Business services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Business services initialization failed: {e}")
            raise
    
    async def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks"""
        try:
            self.logger.info("Starting background tasks...")
            
            # Health check task
            health_check_task = asyncio.create_task(self._health_check_loop())
            self._background_tasks.append(health_check_task)
            
            # Metrics collection task
            metrics_task = asyncio.create_task(self._metrics_collection_loop())
            self._background_tasks.append(metrics_task)
            
            # System maintenance task
            maintenance_task = asyncio.create_task(self._maintenance_loop())
            self._background_tasks.append(maintenance_task)
            
            self.logger.info(f"Started {len(self._background_tasks)} background tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to start background tasks: {e}")
            raise
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._update_system_metrics()
                await asyncio.sleep(60)  # Update every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)
    
    async def _maintenance_loop(self) -> None:
        """Background system maintenance loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._perform_maintenance()
                await asyncio.sleep(3600)  # Maintenance every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Maintenance error: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _perform_health_check(self) -> None:
        """Perform comprehensive system health check"""
        try:
            self.last_health_check = datetime.utcnow()
            
            # Check database
            if self.db_engine:
                try:
                    async with self.db_engine.begin() as conn:
                        await conn.execute("SELECT 1")
                    self.service_health['database'] = ServiceHealth.HEALTHY
                except Exception:
                    self.service_health['database'] = ServiceHealth.UNHEALTHY
            
            # Check cache
            if self.services.cache_manager:
                try:
                    await self.services.cache_manager.ping()
                    self.service_health['cache'] = ServiceHealth.HEALTHY
                except Exception:
                    self.service_health['cache'] = ServiceHealth.UNHEALTHY
            
            # Check Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    self.service_health['redis'] = ServiceHealth.HEALTHY
                except Exception:
                    self.service_health['redis'] = ServiceHealth.UNHEALTHY
            
            # Check business services
            services_to_check = [
                ('profile_manager', self.services.profile_manager),
                ('registration_handler', self.services.registration_handler),
                ('dashboard_controller', self.services.dashboard_controller),
                ('monetization_engine', self.services.monetization_engine),
                ('collaboration_hub', self.services.collaboration_hub)
            ]
            
            for service_name, service in services_to_check:
                if service:
                    self.service_health[service_name] = ServiceHealth.HEALTHY
                else:
                    self.service_health[service_name] = ServiceHealth.UNHEALTHY
            
            # Update overall system status based on health checks
            unhealthy_services = [
                name for name, health in self.service_health.items() 
                if health == ServiceHealth.UNHEALTHY
            ]
            
            if unhealthy_services:
                if len(unhealthy_services) > len(self.service_health) // 2:
                    self.status = SystemStatus.ERROR
                else:
                    self.status = SystemStatus.DEGRADED
            else:
                self.status = SystemStatus.RUNNING
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.status = SystemStatus.ERROR
    
    async def _update_system_metrics(self) -> None:
        """Update system-wide metrics"""
        try:
            # Get creator metrics from profile manager
            if self.services.profile_manager:
                # In a real implementation, these would be actual database queries
                self.metrics.total_creators = 1000  # Placeholder
                self.metrics.active_creators = 750   # Placeholder
                self.metrics.registrations_today = 50  # Placeholder
                
            # Get verification metrics
            if self.services.verification_system:
                self.metrics.verifications_pending = 25  # Placeholder
                
            # Get collaboration metrics
            if self.services.collaboration_hub:
                self.metrics.collaborations_active = 150  # Placeholder
                
            # Get monetization metrics
            if self.services.monetization_engine:
                self.metrics.revenue_today = 15000.50  # Placeholder
                
            # Update performance metrics
            self.metrics.avg_response_time = 0.150  # 150ms
            self.metrics.success_rate = 99.5
            self.metrics.error_rate = 0.5
            
            # Update resource metrics (would be from actual system monitoring)
            self.metrics.cpu_usage = 25.0
            self.metrics.memory_usage = 45.0
            self.metrics.database_connections = 15
            self.metrics.cache_hit_rate = 95.5
            
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")
    
    async def _perform_maintenance(self) -> None:
        """Perform system maintenance tasks"""
        try:
            self.logger.info("Performing system maintenance...")
            
            # Clean up expired cache entries
            if self.services.cache_manager:
                await self.services.cache_manager.cleanup_expired()
            
            # Clean up completed background tasks
            self._background_tasks = [
                task for task in self._background_tasks 
                if not task.done()
            ]
            
            # Emit maintenance completed event
            await self._emit_event("maintenance_completed", {
                'timestamp': datetime.utcnow().isoformat(),
                'active_tasks': len(self._background_tasks)
            })
            
        except Exception as e:
            self.logger.error(f"Maintenance failed: {e}")
    
    async def _emit_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Emit system event to registered handlers"""
        try:
            if event_name in self._event_handlers:
                for handler in self._event_handlers[event_name]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event_data)
                        else:
                            handler(event_data)
                    except Exception as e:
                        self.logger.error(f"Event handler error for {event_name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to emit event {event_name}: {e}")
    
    async def _cancel_background_tasks(self) -> None:
        """Cancel all background tasks"""
        try:
            self.logger.info("Cancelling background tasks...")
            
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            self._background_tasks.clear()
            
        except Exception as e:
            self.logger.error(f"Failed to cancel background tasks: {e}")
    
    async def _shutdown_services(self) -> None:
        """Shutdown all services"""
        try:
            self.logger.info("Shutting down services...")
            
            # Shutdown services with cleanup methods
            services_with_cleanup = [
                self.services.cache_manager,
                self.services.email_service,
                self.services.sms_service
            ]
            
            for service in services_with_cleanup:
                if service and hasattr(service, 'cleanup'):
                    try:
                        await service.cleanup()
                    except Exception as e:
                        self.logger.error(f"Service cleanup error: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to shutdown services: {e}")
    
    async def _cleanup(self) -> None:
        """Cleanup system resources"""
        try:
            self.logger.info("Cleaning up system resources...")
            
            # Close HTTP session
            if self.http_session:
                await self.http_session.close()
                self.http_session = None
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
            
            # Close database engine
            if self.db_engine:
                await self.db_engine.dispose()
                self.db_engine = None
            
            self.logger.info("System cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Global system instance
_creator_system: Optional[CreatorManagementSystem] = None


async def initialize_creator_system(settings: Optional[Settings] = None) -> CreatorManagementSystem:
    """
    Initialize the global creator management system
    
    Args:
        settings: Optional settings override
        
    Returns:
        Initialized CreatorManagementSystem instance
    """
    global _creator_system
    
    if _creator_system is None:
        _creator_system = CreatorManagementSystem(settings)
        await _creator_system.initialize()
    
    return _creator_system


async def get_creator_system() -> CreatorManagementSystem:
    """
    Get the global creator management system instance
    
    Returns:
        CreatorManagementSystem instance
        
    Raises:
        HTTPException: If system is not initialized
    """
    global _creator_system
    
    if _creator_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Creator management system not initialized"
        )
    
    return _creator_system


async def get_creator_manager() -> CreatorProfileManager:
    """
    Get the creator profile manager instance
    
    Returns:
        CreatorProfileManager instance
    """
    system = await get_creator_system()
    return await system.get_creator_manager()


async def shutdown_creator_system() -> None:
    """
    Shutdown the global creator management system
    """
    global _creator_system
    
    if _creator_system is not None:
        await _creator_system.shutdown()
        _creator_system = None


@asynccontextmanager
async def creator_system_context(settings: Optional[Settings] = None):
        try:
            logger.info(f"Executing creator_system_context")
            
            # Implementation for creator_system_context
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"creator_system_context completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"creator_system_context failed: {e}")
            raise
        yield system
    finally:
        await shutdown_creator_system()


# Export main classes and functions
__all__ = [
    'CreatorManagementSystem',
    'SystemStatus',
    'ServiceHealth',
    'SystemMetrics',
    'initialize_creator_system',
    'get_creator_system',
    'get_creator_manager',
    'shutdown_creator_system',
    'creator_system_context'
]
