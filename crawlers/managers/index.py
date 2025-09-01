"""Crawler Managers Index
=====================

Central index and factory for all crawler management systems in the IA Influencer Agent platform.
Provides convenient access to all manager classes and factory functions.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  CRITICAL LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel. Any unauthorized use,
reproduction, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in legal action.
"""

from typing import Dict, Any, Optional
import asyncio
import logging

# Import all managers
from .content_discovery_manager import ContentDiscoveryManager, create_content_discovery_manager
from .resource_allocation_manager import ResourceAllocationManager, create_resource_allocation_manager
from .session_manager import SessionManager, create_session_manager
from .queue_manager import QueueManager, create_queue_manager
from .data_pipeline_manager import DataPipelineManager, create_data_pipeline_manager
from .error_recovery_manager import ErrorRecoveryManager, create_error_recovery_manager
from .platform_integration_manager import PlatformIntegrationManager, create_platform_integration_manager
from .content_protection_manager import ContentProtectionManager, create_content_protection_manager
from .monetization_manager import MonetizationManager, create_monetization_manager
from .collaboration_manager import CollaborationManager, create_collaboration_manager

from ...core.logging import get_logger


class ManagerRegistry:
    """
    Central registry for all crawler managers with lifecycle management.
    
    Features:
    - Centralized manager creation and initialization
    - Dependency injection and configuration management
    - Health monitoring and status reporting
    - Graceful shutdown and resource cleanup
    """
    
    def __init__(self):
        """
Initialize manager registry."""
        self.logger = get_logger(__name__)
        self.managers: Dict[str, Any] = {}
        self.configurations: Dict[str, Any] = {}
        self.health_status: Dict[str, bool] = {}
        self._initialized = False
    
    async def initialize_all_managers(self, configurations: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize all managers with their configurations.
        
        Args:
            configurations: Manager-specific configurations
            
        Returns:
            bool: True if all managers initialized successfully
        """
        try:
            if self._initialized:
                self.logger.warning("Managers already initialized")
                return True
            
            configs = configurations or {}
            
            # Initialize managers in dependency order
            initialization_order = [
                ("error_recovery", ErrorRecoveryManager, create_error_recovery_manager),
                ("resource_allocation", ResourceAllocationManager, create_resource_allocation_manager),
                ("session", SessionManager, create_session_manager),
                ("queue", QueueManager, create_queue_manager),
                ("data_pipeline", DataPipelineManager, create_data_pipeline_manager),
                ("content_discovery", ContentDiscoveryManager, create_content_discovery_manager),
                ("platform_integration", PlatformIntegrationManager, create_platform_integration_manager),
                ("content_protection", ContentProtectionManager, create_content_protection_manager),
                ("monetization", MonetizationManager, create_monetization_manager),
                ("collaboration", CollaborationManager, create_collaboration_manager)
            ]
            
            for manager_name, manager_class, factory_func in initialization_order:
                try:
                    config = configs.get(manager_name)
                    manager = await factory_func(config)
                    
                    self.managers[manager_name] = manager
                    self.configurations[manager_name] = config
                    self.health_status[manager_name] = True
                    
                    self.logger.info(f"Manager '{manager_name}' initialized successfully")
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize manager '{manager_name}': {str(e)}")
                    self.health_status[manager_name] = False
                    # Continue with other managers
            
            self._initialized = True
            
            # Perform health check
            healthy_managers = sum(1 for status in self.health_status.values() if status)
            total_managers = len(self.health_status)
            
            self.logger.info(
                f"Manager registry initialized: {healthy_managers}/{total_managers} managers healthy"
            )
            
            return healthy_managers == total_managers
            
        except Exception as e:
            self.logger.error(f"Failed to initialize manager registry: {str(e)}")
            return False
    
    def get_manager(self, manager_name: str) -> Optional[Any]:
        """
        Get a specific manager instance.
        
        Args:
            manager_name: Name of the manager
            
        Returns:
            Manager instance or None if not found
        """
        return self.managers.get(manager_name)
    
    def get_content_discovery_manager(self) -> Optional[ContentDiscoveryManager]:
        """
Get content discovery manager."""
        return self.get_manager("content_discovery")
    
    def get_resource_allocation_manager(self) -> Optional[ResourceAllocationManager]:
        """Get resource allocation manager."""
        return self.get_manager("resource_allocation")
    
    def get_session_manager(self) -> Optional[SessionManager]:
        """Get session manager."""
        return self.get_manager("session")
    
    def get_queue_manager(self) -> Optional[QueueManager]:
        """Get queue manager."""
        return self.get_manager("queue")
    
    def get_data_pipeline_manager(self) -> Optional[DataPipelineManager]:
        """Get data pipeline manager."""
        return self.get_manager("data_pipeline")
    
    def get_error_recovery_manager(self) -> Optional[ErrorRecoveryManager]:
        """Get error recovery manager."""
        return self.get_manager("error_recovery")
    
    def get_platform_integration_manager(self) -> Optional[PlatformIntegrationManager]:
        """Get platform integration manager."""
        return self.get_manager("platform_integration")
    
    def get_content_protection_manager(self) -> Optional[ContentProtectionManager]:
        """Get content protection manager."""
        return self.get_manager("content_protection")
    
    def get_monetization_manager(self) -> Optional[MonetizationManager]:
        """Get monetization manager."""
        return self.get_manager("monetization")
    
    def get_collaboration_manager(self) -> Optional[CollaborationManager]:
        """Get collaboration manager."""
        return self.get_manager("collaboration")
    
    async def check_health(self) -> Dict[str, bool]:
        """
        Check health status of all managers.
        
        Returns:
            Dict[str, bool]: Health status of each manager
        """
        health_results = {}
        
        for manager_name, manager in self.managers.items():
            try:
                # Try to call a health check method if available
                if hasattr(manager, 'check_health'):
                    health_results[manager_name] = await manager.check_health()
                elif hasattr(manager, 'health_check'):
                    health_results[manager_name] = await manager.health_check()
                else:
                    # Assume healthy if manager exists
                    health_results[manager_name] = manager is not None
                    
            except Exception as e:
                self.logger.error(f"Health check failed for {manager_name}: {str(e)}")
                health_results[manager_name] = False
        
        # Update internal health status
        self.health_status.update(health_results)
        
        return health_results
    
    async def get_manager_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics from all managers.
        
        Returns:
            Dict[str, Dict[str, Any]]: Statistics from each manager
        """
        statistics = {}
        
        for manager_name, manager in self.managers.items():
            try:
                # Try to get statistics if available
                if hasattr(manager, 'get_statistics'):
                    statistics[manager_name] = await manager.get_statistics()
                elif hasattr(manager, 'get_metrics'):
                    statistics[manager_name] = await manager.get_metrics()
                else:
                    statistics[manager_name] = {"status": "active", "type": type(manager).__name__}
                    
            except Exception as e:
                self.logger.error(f"Failed to get statistics for {manager_name}: {str(e)}")
                statistics[manager_name] = {"error": str(e)}
        
        return statistics
    
    async def restart_manager(self, manager_name: str) -> bool:
        """
        Restart a specific manager.
        
        Args:
            manager_name: Name of the manager to restart
            
        Returns:
            bool: True if restart successful
        """
        try:
            if manager_name not in self.managers:
                self.logger.error(f"Manager '{manager_name}' not found")
                return False
            
            # Close existing manager
            old_manager = self.managers[manager_name]
            if hasattr(old_manager, 'close'):
                await old_manager.close()
            
            # Recreate manager
            config = self.configurations.get(manager_name)
            
            # Get factory function based on manager name
            factory_functions = {
                "content_discovery": create_content_discovery_manager,
                "resource_allocation": create_resource_allocation_manager,
                "session": create_session_manager,
                "queue": create_queue_manager,
                "data_pipeline": create_data_pipeline_manager,
                "error_recovery": create_error_recovery_manager,
                "platform_integration": create_platform_integration_manager,
                "content_protection": create_content_protection_manager,
                "monetization": create_monetization_manager,
                "collaboration": create_collaboration_manager
            }
            
            factory_func = factory_functions.get(manager_name)
            if not factory_func:
                self.logger.error(f"No factory function for manager '{manager_name}'")
                return False
            
            new_manager = await factory_func(config)
            self.managers[manager_name] = new_manager
            self.health_status[manager_name] = True
            
            self.logger.info(f"Manager '{manager_name}' restarted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart manager '{manager_name}': {str(e)}")
            self.health_status[manager_name] = False
            return False
    
    async def close_all(self):
        """Close all managers and cleanup resources."""
        try:
            for manager_name, manager in self.managers.items():
                try:
                    if hasattr(manager, 'close'):
                        await manager.close()
                    self.health_status[manager_name] = False
                except Exception as e:
                    self.logger.error(f"Error closing manager '{manager_name}': {str(e)}")
            
            self.managers.clear()
            self.configurations.clear()
            self.health_status.clear()
            self._initialized = False
            
            self.logger.info("All managers closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing managers: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        await self.close_all()


# Global registry instance
_manager_registry: Optional[ManagerRegistry] = None


async def get_manager_registry(configurations: Optional[Dict[str, Any]] = None) -> ManagerRegistry:
    """
    Get or create the global manager registry.
    
    Args:
        configurations: Manager configurations for initialization
        
    Returns:
        ManagerRegistry: Global manager registry instance
    """
    global _manager_registry
    
    if _manager_registry is None:
        _manager_registry = ManagerRegistry()
        await _manager_registry.initialize_all_managers(configurations)
    
    return _manager_registry


async def shutdown_manager_registry():
    """
Shutdown the global manager registry."""
    global _manager_registry
    
    if _manager_registry:
        await _manager_registry.close_all()
        _manager_registry = None


# Convenience functions for common operations
async def create_complete_manager_suite(configurations: Optional[Dict[str, Any]] = None) -> ManagerRegistry:
    """
    Create a complete suite of all managers.
    
    Args:
        configurations: Manager-specific configurations
        
    Returns:
        ManagerRegistry: Initialized manager registry
    """
    registry = ManagerRegistry()
    await registry.initialize_all_managers(configurations)
    return registry


async def get_content_discovery_manager(config: Optional[Any] = None) -> ContentDiscoveryManager:
    """
Quick access to content discovery manager."""
    if config:
        return await create_content_discovery_manager(config)
    else:
        registry = await get_manager_registry()
        return registry.get_content_discovery_manager()


async def get_platform_integration_manager(config: Optional[Any] = None) -> PlatformIntegrationManager:
    """
Quick access to platform integration manager."""
    if config:
        return await create_platform_integration_manager(config)
    else:
        registry = await get_manager_registry()
        return registry.get_platform_integration_manager()


async def get_content_protection_manager(config: Optional[Any] = None) -> ContentProtectionManager:
    """
Quick access to content protection manager."""
    if config:
        return await create_content_protection_manager(config)
    else:
        registry = await get_manager_registry()
        return registry.get_content_protection_manager()


async def get_monetization_manager(config: Optional[Any] = None) -> MonetizationManager:
    """
Quick access to monetization manager."""
    if config:
        return await create_monetization_manager(config)
    else:
        registry = await get_manager_registry()
        return registry.get_monetization_manager()


async def get_collaboration_manager(config: Optional[Any] = None) -> CollaborationManager:
    """
Quick access to collaboration manager."""
    if config:
        return await create_collaboration_manager(config)
    else:
        registry = await get_manager_registry()
        return registry.get_collaboration_manager()


# Export all components
__all__ = [
    "ManagerRegistry",
    "get_manager_registry",
    "shutdown_manager_registry",
    "create_complete_manager_suite",
    "get_content_discovery_manager",
    "get_platform_integration_manager",
    "get_content_protection_manager",
    "get_monetization_manager",
    "get_collaboration_manager"
]
