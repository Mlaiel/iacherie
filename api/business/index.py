"""Business services index for IA Influencer Agent platform.

This module provides a centralized access point for all business services,
facilitating service discovery, dependency injection, and service orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.

WARNING: This code is proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution is strictly
prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from typing import Dict, Type, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from .user_service import UserService
from .content_service import ContentService
from .ai_processing_service import AIProcessingService
from .protection_service import ProtectionService
from .collaboration_service import CollaborationService
from .matching_service import MatchingService
from .notification_service import NotificationService
from .monetization_service import MonetizationService
from .analytics_service import AnalyticsService
from .seo_service import SEOService
from .distribution_service import DistributionService

from ..core.config import get_settings
from ..core.database import get_db
from ..utils.monitoring import ServiceMonitor
from ..utils.health_check import ServiceHealthChecker

logger = logging.getLogger(__name__)
settings = get_settings()

class BusinessServiceRegistry:
    """
    Advanced registry for all business services with comprehensive dependency injection,
    health monitoring, and service orchestration capabilities.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._service_types: Dict[str, Type] = {
            'user': UserService,
            'content': ContentService,
            'ai_processing': AIProcessingService,
            'protection': ProtectionService,
            'collaboration': CollaborationService,
            'matching': MatchingService,
            'notification': NotificationService,
            'monetization': MonetizationService,
            'analytics': AnalyticsService,
            'seo': SEOService,
            'distribution': DistributionService
        }
        self._service_dependencies: Dict[str, List[str]] = {
            'content': ['user', 'ai_processing'],
            'protection': ['content', 'ai_processing'],
            'collaboration': ['user', 'content'],
            'matching': ['user', 'content', 'analytics'],
            'monetization': ['user', 'content', 'analytics'],
            'analytics': ['user', 'content'],
            'seo': ['content', 'analytics'],
            'distribution': ['content', 'seo', 'analytics']
        }
        self._service_monitor = ServiceMonitor()
        self._health_checker = ServiceHealthChecker()
        self._initialization_order: List[str] = []
        self._is_initialized = False
    
    async def initialize_services(self) -> None:
        """
Initialize all services in dependency order."""
        try:
            logger.info("Starting business services initialization...")
            
            # Calculate initialization order based on dependencies
            self._initialization_order = self._calculate_initialization_order()
            
            # Initialize services in order
            for service_name in self._initialization_order:
                await self._initialize_service(service_name)
                logger.info(f"Service '{service_name}' initialized successfully")
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            self._is_initialized = True
            logger.info("All business services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize business services: {str(e)}")
            raise
    
    async def shutdown_services(self) -> None:
        """Gracefully shutdown all services."""
        try:
            logger.info("Starting graceful shutdown of business services...")
            
            # Shutdown services in reverse order
            for service_name in reversed(self._initialization_order):
                await self._shutdown_service(service_name)
                logger.info(f"Service '{service_name}' shut down successfully")
            
            # Stop health monitoring
            await self._stop_health_monitoring()
            
            self._is_initialized = False
            logger.info("All business services shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during services shutdown: {str(e)}")
            raise
    
    def get_service(self, service_name: str) -> Any:
        """
        Get service instance by name with dependency resolution.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is unknown or not initialized
        """
        if not self._is_initialized:
            raise RuntimeError("Services not initialized. Call initialize_services() first.")
        
        if service_name not in self._services:
            if service_name in self._service_types:
                # Initialize service with dependencies
                dependencies = self._resolve_dependencies(service_name)
                self._services[service_name] = self._service_types[service_name](**dependencies)
                
                # Register with monitoring
                self._service_monitor.register_service(service_name, self._services[service_name])
            else:
                raise ValueError(f"Unknown service: {service_name}")
        
        return self._services[service_name]
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """
        Register a service instance manually.
        
        Args:
            service_name: Name of the service
            service_instance: Service instance to register
        """
        self._services[service_name] = service_instance
        self._service_monitor.register_service(service_name, service_instance)
        logger.info(f"Service '{service_name}' registered manually")
    
    def get_service_health(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health status of service(s).
        
        Args:
            service_name: Specific service name (optional, returns all if None)
            
        Returns:
            Health status information
        """
        if service_name:
            return self._health_checker.check_service_health(service_name)
        else:
            return self._health_checker.check_all_services_health()
    
    def get_service_metrics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for service(s).
        
        Args:
            service_name: Specific service name (optional, returns all if None)
            
        Returns:
            Service metrics and performance data
        """
        if service_name:
            return self._service_monitor.get_service_metrics(service_name)
        else:
            return self._service_monitor.get_all_service_metrics()
    
    def list_services(self) -> List[str]:
        """
List all available services."""
        return list(self._service_types.keys())
    
    def get_service_dependencies(self, service_name: str) -> List[str]:
        """
Get dependencies for a specific service."""
        return self._service_dependencies.get(service_name, [])
    
    @asynccontextmanager
    async def service_context(self, service_names: List[str]):
        """
        Async context manager for service lifecycle management.
        
        Args:
            service_names: List of service names to manage
        """
        services = {}
        try:
            # Initialize requested services
            for service_name in service_names:
                services[service_name] = self.get_service(service_name)
            
            yield services
            
        except Exception as e:
            logger.error(f"Error in service context: {str(e)}")
            raise
        finally:
            # Cleanup if needed
            for service_name, service in services.items():
                if hasattr(service, 'cleanup'):
                    try:
                        await service.cleanup()
                    except Exception as e:
                        logger.warning(f"Error cleaning up service '{service_name}': {str(e)}")
    
    # Private helper methods
    def _calculate_initialization_order(self) -> List[str]:
        """Calculate the order to initialize services based on dependencies."""
        order = []
        visited = set()
        visiting = set()
        
        def visit(service_name: str):
            if service_name in visiting:
                raise ValueError(f"Circular dependency detected involving {service_name}")
            if service_name in visited:
                return
            
            visiting.add(service_name)
            
            # Visit dependencies first
            for dependency in self._service_dependencies.get(service_name, []):
                visit(dependency)
            
            visiting.remove(service_name)
            visited.add(service_name)
            order.append(service_name)
        
        # Visit all services
        for service_name in self._service_types.keys():
            visit(service_name)
        
        return order
    
    async def _initialize_service(self, service_name: str) -> None:
        """Initialize a single service."""
        try:
            if service_name in self._services:
                return  # Already initialized
            
            # Resolve dependencies
            dependencies = self._resolve_dependencies(service_name)
            
            # Create service instance
            service_instance = self._service_types[service_name](**dependencies)
            
            # Initialize service if it has an initialize method
            if hasattr(service_instance, 'initialize'):
                await service_instance.initialize()
            
            # Store service
            self._services[service_name] = service_instance
            
            # Register with monitoring
            self._service_monitor.register_service(service_name, service_instance)
            
        except Exception as e:
            logger.error(f"Failed to initialize service '{service_name}': {str(e)}")
            raise
    
    async def _shutdown_service(self, service_name: str) -> None:
        """Shutdown a single service."""
        try:
            if service_name not in self._services:
                return  # Not initialized
            
            service = self._services[service_name]
            
            # Call shutdown method if available
            if hasattr(service, 'shutdown'):
                await service.shutdown()
            
            # Unregister from monitoring
            self._service_monitor.unregister_service(service_name)
            
            # Remove from registry
            del self._services[service_name]
            
        except Exception as e:
            logger.error(f"Failed to shutdown service '{service_name}': {str(e)}")
            raise
    
    def _resolve_dependencies(self, service_name: str) -> Dict[str, Any]:
        """Resolve dependencies for a service."""
        dependencies = {}
        
        for dep_name in self._service_dependencies.get(service_name, []):
            if dep_name not in self._services:
                # Initialize dependency if not already done
                dep_dependencies = self._resolve_dependencies(dep_name)
                self._services[dep_name] = self._service_types[dep_name](**dep_dependencies)
            
            dependencies[dep_name] = self._services[dep_name]
        
        return dependencies
    
    async def _start_health_monitoring(self) -> None:
        """
Start health monitoring for all services."""
        try:
            await self._health_checker.start_monitoring()
            logger.info("Health monitoring started for all services")
        except Exception as e:
            logger.warning(f"Failed to start health monitoring: {str(e)}")
    
    async def _stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        try:
            await self._health_checker.stop_monitoring()
            logger.info("Health monitoring stopped")
        except Exception as e:
            logger.warning(f"Error stopping health monitoring: {str(e)}")

class BusinessServiceOrchestrator:
    """
    High-level orchestrator for complex business operations involving multiple services.
    """
    
    def __init__(self, service_registry: BusinessServiceRegistry):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def execute_content_workflow(
        self,
        user_id: str,
        content_data: Dict[str, Any],
        workflow_options: Dict[str, Any],
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Execute complete content creation and distribution workflow.
        
        Args:
            user_id: User identifier
            content_data: Content creation data
            workflow_options: Workflow configuration options
            db: Database session
            
        Returns:
            Workflow execution results
        """
        workflow_results = {
            "workflow_id": f"wf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "started_at": datetime.utcnow(),
            "steps": [],
            "status": "in_progress"
        }
        
        try:
            # Step 1: Create content
            content_service = self.registry.get_service('content')
            content_result = await content_service.create_content(
                user_id, content_data, db
            )
            workflow_results["steps"].append({
                "step": "content_creation",
                "status": "completed",
                "result": content_result
            })
            
            # Step 2: AI processing and enhancement
            if workflow_options.get("ai_processing", True):
                ai_service = self.registry.get_service('ai_processing')
                ai_result = await ai_service.process_content(
                    content_result["content_id"], db
                )
                workflow_results["steps"].append({
                    "step": "ai_processing",
                    "status": "completed",
                    "result": ai_result
                })
            
            # Step 3: Content protection
            if workflow_options.get("enable_protection", True):
                protection_service = self.registry.get_service('protection')
                protection_result = await protection_service.protect_content(
                    content_result["content_id"], db
                )
                workflow_results["steps"].append({
                    "step": "content_protection",
                    "status": "completed",
                    "result": protection_result
                })
            
            # Step 4: SEO optimization
            if workflow_options.get("seo_optimization", True):
                seo_service = self.registry.get_service('seo')
                seo_result = await seo_service.optimize_content_metadata(
                    content_result["content_id"],
                    workflow_options.get("target_platforms", []),
                    db=db
                )
                workflow_results["steps"].append({
                    "step": "seo_optimization",
                    "status": "completed",
                    "result": seo_result
                })
            
            # Step 5: Distribution planning
            if workflow_options.get("auto_distribution", False):
                distribution_service = self.registry.get_service('distribution')
                distribution_result = await distribution_service.create_distribution_plan(
                    content_result["content_id"],
                    workflow_options.get("distribution_targets", []),
                    db=db
                )
                workflow_results["steps"].append({
                    "step": "distribution_planning",
                    "status": "completed",
                    "result": distribution_result
                })
            
            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.utcnow()
            
            return workflow_results
            
        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            workflow_results["failed_at"] = datetime.utcnow()
            logger.error(f"Content workflow failed: {str(e)}")
            raise

# Global instances
service_registry = BusinessServiceRegistry()
service_orchestrator = BusinessServiceOrchestrator(service_registry)

# Service factory functions for dependency injection
def get_user_service() -> UserService:
    """Get UserService instance."""
    return service_registry.get_service('user')

def get_content_service() -> ContentService:
    """
Get ContentService instance."""
    return service_registry.get_service('content')

def get_ai_processing_service() -> AIProcessingService:
    """
Get AIProcessingService instance."""
    return service_registry.get_service('ai_processing')

def get_protection_service() -> ProtectionService:
    """
Get ProtectionService instance."""
    return service_registry.get_service('protection')

def get_collaboration_service() -> CollaborationService:
    """
Get CollaborationService instance."""
    return service_registry.get_service('collaboration')

def get_matching_service() -> MatchingService:
    """
Get MatchingService instance."""
    return service_registry.get_service('matching')

def get_notification_service() -> NotificationService:
    """
Get NotificationService instance."""
    return service_registry.get_service('notification')

def get_monetization_service() -> MonetizationService:
    """
Get MonetizationService instance."""
    return service_registry.get_service('monetization')

def get_analytics_service() -> AnalyticsService:
    """
Get AnalyticsService instance."""
    return service_registry.get_service('analytics')

def get_seo_service() -> SEOService:
    """
Get SEOService instance."""
    return service_registry.get_service('seo')

def get_distribution_service() -> DistributionService:
    """
Get DistributionService instance."""
    return service_registry.get_service('distribution')

def get_service_orchestrator() -> BusinessServiceOrchestrator:
    """
Get BusinessServiceOrchestrator instance."""
    return service_orchestrator

# Core business services
from .user_service import UserService, UserManager, ProfileManager
from .content_service import ContentService, ContentManager, MediaProcessor
from .ai_processing_service import AIProcessingService, ContentAnalyzer, QualityAssessment
from .protection_service import ProtectionService, CopyrightManager, SecurityValidator

# Collaboration and matching services
from .collaboration_service import CollaborationService, PartnershipManager, ProjectCoordinator
from .matching_service import MatchingService, RecommendationEngine, CompatibilityAnalyzer

# Monetization and business logic
from .monetization_service import MonetizationService, RevenueManager, PaymentProcessor
from .notification_service import NotificationService, AlertManager, CommunicationHub

# Service orchestration
from .orchestrator import BusinessOrchestrator, ServiceCoordinator, WorkflowManager


def initialize_business_services(core_services):
    """
    Initialize all business services with core dependencies
    
    Args:
        core_services: Core platform services (database, security, etc.)
        
    Returns:
        dict: Initialized business services
    """
    services = {
        'user_service': UserService(core_services),
        'content_service': ContentService(core_services),
        'ai_processing_service': AIProcessingService(core_services),
        'protection_service': ProtectionService(core_services),
        'collaboration_service': CollaborationService(core_services),
        'matching_service': MatchingService(core_services),
        'monetization_service': MonetizationService(core_services),
        'notification_service': NotificationService(core_services)
    }
    
    # Initialize orchestrator with all services
    services['orchestrator'] = BusinessOrchestrator(services, core_services)
    
    return services


def get_business_orchestrator(core_services):
    """
Get business orchestrator with all services initialized"""
    services = initialize_business_services(core_services)
    return services['orchestrator']


def get_user_service(core_services):
    """
Get standalone user service"""
    return UserService(core_services)


def get_content_service(core_services):
    """
Get standalone content service"""
    return ContentService(core_services)


def get_ai_processing_service(core_services):
    """
Get standalone AI processing service"""
    return AIProcessingService(core_services)


def get_protection_service(core_services):
    """
Get standalone protection service"""
    return ProtectionService(core_services)


def get_collaboration_service(core_services):
    """
Get standalone collaboration service"""
    return CollaborationService(core_services)


def get_matching_service(core_services):
    """
Get standalone matching service"""
    return MatchingService(core_services)


def get_monetization_service(core_services):
    """
Get standalone monetization service"""
    return MonetizationService(core_services)


def get_notification_service(core_services):
    """
Get standalone notification service"""
    return NotificationService(core_services)


# Service factory aliases
create_user_service = get_user_service
create_content_service = get_content_service
create_ai_service = get_ai_processing_service
create_protection_service = get_protection_service
create_collaboration_service = get_collaboration_service
create_matching_service = get_matching_service
create_monetization_service = get_monetization_service
create_notification_service = get_notification_service
create_business_orchestrator = get_business_orchestrator


__all__ = [
    # Core Services
    'UserService',
    'ContentService', 
    'AIProcessingService',
    'ProtectionService',
    'CollaborationService',
    'MatchingService',
    'MonetizationService',
    'NotificationService',
    
    # Specialized Managers
    'UserManager',
    'ContentManager',
    'CopyrightManager',
    'PartnershipManager',
    'RecommendationEngine',
    'RevenueManager',
    'PaymentProcessor',
    'AlertManager',
    
    # Orchestration
    'BusinessOrchestrator',
    'ServiceCoordinator',
    'WorkflowManager',
    
    # Factory Functions
    'initialize_business_services',
    'get_business_orchestrator',
    'get_user_service',
    'get_content_service',
    'get_ai_processing_service',
    'get_protection_service',
    'get_collaboration_service',
    'get_matching_service',
    'get_monetization_service',
    'get_notification_service',
    
    # Service Aliases
    'create_user_service',
    'create_content_service',
    'create_ai_service',
    'create_protection_service',
    'create_collaboration_service',
    'create_matching_service',
    'create_monetization_service',
    'create_notification_service',
    'create_business_orchestrator'
]
