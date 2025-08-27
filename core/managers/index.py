"""
Core Managers Index - IA-Influencer-Agent
================================================================================
Module: backend/core/managers/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Manager Index - Central Manager Registry & Factory
Responsibility: Centralized access point for all enterprise managers
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Application startup → Manager initialization → Service registration → 
Health monitoring → Lifecycle management → Graceful shutdown
"""

from typing import Any, Dict, List, Optional, Union, Type, TypeVar
import logging
import asyncio
from datetime import datetime
import inspect

# Import all managers
from .analytics_manager import AnalyticsManager, get_analytics_manager
from .backup_manager import EnterpriseBackupManager, get_backup_manager
from .cache_manager import IntelligentCacheManager, get_cache_manager
from .collaboration_manager import CollaborationManager, get_collaboration_manager
from .database_manager import EnterpriseDatabaseManager, get_database_manager
from .license_manager import LicenseManager, get_license_manager
from .migration_manager import MigrationManager, get_migration_manager
from .notification_manager import NotificationManager, get_notification_manager
from .queue_manager import IntelligentQueueManager, get_queue_manager
from .resource_manager import ResourceManager, get_resource_manager
from .security_manager import SecurityManager, get_security_manager
from .session_manager import SessionManager, get_session_manager
from .storage_manager import CloudStorageManager, get_storage_manager
from .tenant_manager import TenantManager, get_tenant_manager
from .workflow_manager import WorkflowManager, get_workflow_manager

# New industrial managers
from .protection_manager import ProtectionManager, get_protection_manager
from .fingerprinting_manager import FingerprintingManager, get_fingerprinting_manager
from .revenue_manager import RevenueManager, get_revenue_manager
from .monetization_manager import MonetizationManager, get_monetization_manager
from .content_manager import ContentManager, get_content_manager
from .ai_agent_manager import AiAgentManager, get_ai_agent_manager
from .multilingual_manager import MultilingualManager, get_multilingual_manager
from .distribution_manager import DistributionManager, get_distribution_manager
from .compliance_manager import ComplianceManager, get_compliance_manager
from .performance_manager import PerformanceManager, get_performance_manager

logger = logging.getLogger(__name__)

# Type variable for manager types
ManagerType = TypeVar('ManagerType')

# Global manager registry
_MANAGER_REGISTRY: Dict[str, Any] = {}
_MANAGER_FACTORIES: Dict[str, callable] = {}
_MANAGER_HEALTH_STATUS: Dict[str, Dict[str, Any]] = {}


class ManagerRegistry:
    """
    Central registry for all enterprise managers with lifecycle management
    """
    
    def __init__(self):
        self._managers: Dict[str, Any] = {}
        self._initialization_order: List[str] = []
        self._health_checks: Dict[str, callable] = {}
        self._startup_callbacks: Dict[str, List[callable]] = {}
        self._shutdown_callbacks: Dict[str, List[callable]] = {}
        
        # Register all manager factories
        self._register_manager_factories()
    
    def _register_manager_factories(self):
        """Register all manager factory functions"""
        self._manager_factories = {
            # Core infrastructure managers
            "database": get_database_manager,
            "cache": get_cache_manager,
            "queue": get_queue_manager,
            "storage": get_storage_manager,
            "backup": get_backup_manager,
            
            # Security and compliance
            "security": get_security_manager,
            "compliance": get_compliance_manager,
            "license": get_license_manager,
            
            # Content and processing
            "content": get_content_manager,
            "protection": get_protection_manager,
            "fingerprinting": get_fingerprinting_manager,
            "ai_agent": get_ai_agent_manager,
            
            # Business logic
            "monetization": get_monetization_manager,
            "revenue": get_revenue_manager,
            "distribution": get_distribution_manager,
            "collaboration": get_collaboration_manager,
            
            # Operations and monitoring
            "analytics": get_analytics_manager,
            "performance": get_performance_manager,
            "notification": get_notification_manager,
            "workflow": get_workflow_manager,
            
            # System management
            "session": get_session_manager,
            "tenant": get_tenant_manager,
            "resource": get_resource_manager,
            "migration": get_migration_manager,
            "multilingual": get_multilingual_manager,
        }
        
        # Define initialization order (dependencies first)
        self._initialization_order = [
            "database", "cache", "queue", "storage",  # Core infrastructure
            "security", "session", "tenant",  # Identity and security
            "backup", "resource", "migration",  # System services
            "content", "fingerprinting", "protection",  # Content services
            "ai_agent", "analytics", "performance",  # AI and analytics
            "monetization", "revenue", "distribution",  # Business services
            "compliance", "license", "notification",  # Compliance and communication
            "collaboration", "workflow", "multilingual",  # User services
        ]
    
    async def initialize_all_managers(self) -> Dict[str, bool]:
        """
        Initialize all managers in dependency order
        
        Returns:
            Dict mapping manager names to initialization success
        """
        initialization_results = {}
        
        logger.info("🚀 Starting IA-Influencer-Agent managers initialization...")
        
        for manager_name in self._initialization_order:
            try:
                start_time = datetime.now()
                
                # Get manager instance
                manager_factory = self._manager_factories.get(manager_name)
                if not manager_factory:
                    logger.warning(f"⚠️ No factory found for manager: {manager_name}")
                    initialization_results[manager_name] = False
                    continue
                
                manager_instance = manager_factory()
                
                # Initialize manager if it has an initialization method
                if hasattr(manager_instance, 'initialize_pool'):
                    success = await manager_instance.initialize_pool()
                elif hasattr(manager_instance, 'initialize_cache_system'):
                    success = await manager_instance.initialize_cache_system()
                elif hasattr(manager_instance, 'initialize_databases'):
                    success = await manager_instance.initialize_databases()
                elif hasattr(manager_instance, 'initialize_queue_system'):
                    success = await manager_instance.initialize_queue_system()
                elif hasattr(manager_instance, 'initialize_storage_pools'):
                    success = await manager_instance.initialize_storage_pools()
                elif hasattr(manager_instance, 'initialize_backup_system'):
                    success = await manager_instance.initialize_backup_system()
                else:
                    # Assume initialization is successful if no specific method
                    success = True
                
                if success:
                    self._managers[manager_name] = manager_instance
                    
                    # Execute startup callbacks
                    for callback in self._startup_callbacks.get(manager_name, []):
                        try:
                            await callback(manager_instance)
                        except Exception as e:
                            logger.error(f"❌ Startup callback failed for {manager_name}: {e}")
                    
                    initialization_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ {manager_name} manager initialized in {initialization_time:.2f}s")
                else:
                    logger.error(f"❌ Failed to initialize {manager_name} manager")
                
                initialization_results[manager_name] = success
                
            except Exception as e:
                logger.error(f"❌ Exception during {manager_name} initialization: {e}")
                initialization_results[manager_name] = False
        
        successful_count = sum(initialization_results.values())
        total_count = len(initialization_results)
        
        logger.info(f"🎯 Manager initialization completed: {successful_count}/{total_count} successful")
        
        # Perform initial health checks
        await self.perform_health_checks()
        
        return initialization_results
    
    async def shutdown_all_managers(self) -> Dict[str, bool]:
        """
        Gracefully shutdown all managers in reverse order
        
        Returns:
            Dict mapping manager names to shutdown success
        """
        shutdown_results = {}
        
        logger.info("🛑 Starting IA-Influencer-Agent managers shutdown...")
        
        # Shutdown in reverse order
        for manager_name in reversed(self._initialization_order):
            try:
                manager_instance = self._managers.get(manager_name)
                if not manager_instance:
                    continue
                
                # Execute shutdown callbacks
                for callback in self._shutdown_callbacks.get(manager_name, []):
                    try:
                        await callback(manager_instance)
                    except Exception as e:
                        logger.error(f"❌ Shutdown callback failed for {manager_name}: {e}")
                
                # Shutdown manager if it has a cleanup method
                if hasattr(manager_instance, 'cleanup'):
                    success = await manager_instance.cleanup()
                elif hasattr(manager_instance, 'shutdown'):
                    success = await manager_instance.shutdown()
                else:
                    success = True
                
                if success:
                    logger.info(f"✅ {manager_name} manager shutdown successfully")
                else:
                    logger.error(f"❌ Failed to shutdown {manager_name} manager")
                
                shutdown_results[manager_name] = success
                
            except Exception as e:
                logger.error(f"❌ Exception during {manager_name} shutdown: {e}")
                shutdown_results[manager_name] = False
        
        self._managers.clear()
        
        successful_count = sum(shutdown_results.values())
        total_count = len(shutdown_results)
        
        logger.info(f"🎯 Manager shutdown completed: {successful_count}/{total_count} successful")
        
        return shutdown_results
    
    async def perform_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health checks on all managers
        
        Returns:
            Dict mapping manager names to health status
        """
        health_results = {}
        
        for manager_name, manager_instance in self._managers.items():
            try:
                health_info = {
                    "healthy": True,
                    "status": "operational",
                    "last_check": datetime.now().isoformat(),
                    "details": {}
                }
                
                # Perform custom health check if available
                if hasattr(manager_instance, 'perform_health_checks'):
                    custom_health = await manager_instance.perform_health_checks()
                    health_info.update(custom_health)
                elif hasattr(manager_instance, 'get_health_status'):
                    custom_health = await manager_instance.get_health_status()
                    health_info.update(custom_health)
                
                # Perform basic connectivity check
                if hasattr(manager_instance, '_connection_pools'):
                    connection_count = len(getattr(manager_instance, '_connection_pools', {}))
                    health_info["details"]["active_connections"] = connection_count
                
                health_results[manager_name] = health_info
                
            except Exception as e:
                health_results[manager_name] = {
                    "healthy": False,
                    "status": "error",
                    "last_check": datetime.now().isoformat(),
                    "error": str(e)
                }
                logger.error(f"❌ Health check failed for {manager_name}: {e}")
        
        # Update global health status
        global _MANAGER_HEALTH_STATUS
        _MANAGER_HEALTH_STATUS = health_results
        
        return health_results
    
    def get_manager(self, manager_name: str) -> Optional[Any]:
        """
        Get a manager instance by name
        
        Args:
            manager_name: Name of the manager
            
        Returns:
            Manager instance or None if not found
        """
        return self._managers.get(manager_name)
    
    def register_startup_callback(self, manager_name: str, callback: callable):
        """Register a callback to be executed when a manager starts"""
        if manager_name not in self._startup_callbacks:
            self._startup_callbacks[manager_name] = []
        self._startup_callbacks[manager_name].append(callback)
    
    def register_shutdown_callback(self, manager_name: str, callback: callable):
        """Register a callback to be executed when a manager shuts down"""
        if manager_name not in self._shutdown_callbacks:
            self._shutdown_callbacks[manager_name] = []
        self._shutdown_callbacks[manager_name].append(callback)
    
    def get_all_managers(self) -> Dict[str, Any]:
        """Get all registered managers"""
        return self._managers.copy()
    
    def get_manager_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all managers"""
        return _MANAGER_HEALTH_STATUS.copy()


# Global manager registry instance
_manager_registry = ManagerRegistry()


# Public API functions
async def initialize_all_managers() -> Dict[str, bool]:
    """
    Initialize all IA-Influencer-Agent managers
    
    Returns:
        Dict mapping manager names to initialization success
    """
    return await _manager_registry.initialize_all_managers()


async def shutdown_all_managers() -> Dict[str, bool]:
    """
    Shutdown all IA-Influencer-Agent managers
    
    Returns:
        Dict mapping manager names to shutdown success
    """
    return await _manager_registry.shutdown_all_managers()


async def perform_health_checks() -> Dict[str, Dict[str, Any]]:
    """
    Perform health checks on all managers
    
    Returns:
        Dict mapping manager names to health status
    """
    return await _manager_registry.perform_health_checks()


def get_manager(manager_name: str) -> Optional[Any]:
    """
    Get a manager instance by name
    
    Args:
        manager_name: Name of the manager (e.g., 'database', 'cache', 'queue')
        
    Returns:
        Manager instance or None if not found
    """
    return _manager_registry.get_manager(manager_name)


def get_all_managers() -> Dict[str, Any]:
    """
    Get all registered managers
    
    Returns:
        Dict mapping manager names to instances
    """
    return _manager_registry.get_all_managers()


def get_manager_health_status() -> Dict[str, Dict[str, Any]]:
    """
    Get health status of all managers
    
    Returns:
        Dict mapping manager names to health status
    """
    return _manager_registry.get_manager_health_status()


def register_startup_callback(manager_name: str, callback: callable):
    """
    Register a callback to be executed when a manager starts
    
    Args:
        manager_name: Name of the manager
        callback: Callback function to execute
    """
    _manager_registry.register_startup_callback(manager_name, callback)


def register_shutdown_callback(manager_name: str, callback: callable):
    """
    Register a callback to be executed when a manager shuts down
    
    Args:
        manager_name: Name of the manager
        callback: Callback function to execute
    """
    _manager_registry.register_shutdown_callback(manager_name, callback)


# Convenience functions for direct manager access
def get_database_manager_instance():
    """Get database manager instance"""
    return get_manager("database") or get_database_manager()


def get_cache_manager_instance():
    """Get cache manager instance"""
    return get_manager("cache") or get_cache_manager()


def get_queue_manager_instance():
    """Get queue manager instance"""
    return get_manager("queue") or get_queue_manager()


def get_storage_manager_instance():
    """Get storage manager instance"""
    return get_manager("storage") or get_storage_manager()


def get_backup_manager_instance():
    """Get backup manager instance"""
    return get_manager("backup") or get_backup_manager()


def get_protection_manager_instance():
    """Get protection manager instance"""
    return get_manager("protection") or get_protection_manager()


def get_fingerprinting_manager_instance():
    """Get fingerprinting manager instance"""
    return get_manager("fingerprinting") or get_fingerprinting_manager()


def get_monetization_manager_instance():
    """Get monetization manager instance"""
    return get_manager("monetization") or get_monetization_manager()


def get_ai_agent_manager_instance():
    """Get AI agent manager instance"""
    return get_manager("ai_agent") or get_ai_agent_manager()


# Export all manager access functions
__all__ = [
    # Manager registry functions
    "initialize_all_managers",
    "shutdown_all_managers", 
    "perform_health_checks",
    "get_manager",
    "get_all_managers",
    "get_manager_health_status",
    "register_startup_callback",
    "register_shutdown_callback",
    
    # Direct manager access functions
    "get_database_manager_instance",
    "get_cache_manager_instance",
    "get_queue_manager_instance",
    "get_storage_manager_instance",
    "get_backup_manager_instance",
    "get_protection_manager_instance",
    "get_fingerprinting_manager_instance",
    "get_monetization_manager_instance",
    "get_ai_agent_manager_instance",
    
    # Manager classes for type hints
    "ManagerRegistry",
]
