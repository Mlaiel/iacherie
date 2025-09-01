"""Database Connection Factory - IA Influencer Agent Platform

Centralized factory for creating and configuring database connections:
- Database connection instantiation
- Configuration injection
- Dependency resolution
- Connection validation
- Pool management
- Multi-tenant setup

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Type, Union, List
from dataclasses import dataclass
from datetime import datetime

# Import connection handlers
from .postgresql import PostgreSQLConnectionHandler
from .redis import RedisConnectionHandler
from .mongodb import MongoDBConnectionHandler
from .elasticsearch import ElasticsearchConnectionHandler
from .vector_stores import VectorStoreConnectionHandler
from .object_storage import ObjectStorageConnectionHandler

# Import infrastructure components
from .health_monitor import DatabaseHealthMonitor
from .pool_manager import ConnectionPoolManager
from .transaction_manager import TransactionManager
from .session_manager import SessionManager
from .failover import FailoverManager
from .load_balancer import DatabaseLoadBalancer
from .config_manager import DatabaseConfigurationManager, Environment

# Import configuration classes
from .config_manager import (
    DatabaseConfig, RedisConfig, MongoConfig, ElasticsearchConfig,
    VectorStoreConfig, ObjectStorageConfig, TenantConfig
)


@dataclass
class ConnectionSpec:
    """Connection specification for factory"""
    handler_type: str
    config: Dict[str, Any]
    tenant_id: Optional[str] = None
    pool_size: int = 10
    health_check: bool = True
    failover_enabled: bool = True
    load_balancing: bool = True


class DatabaseConnectionFactory:
    """
    Factory for creating and managing database connections.
    
    Provides:
    - Centralized connection creation
    - Configuration management
    - Dependency injection
    - Connection validation
    - Infrastructure setup
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.logger = logging.getLogger(__name__)
        self.environment = environment
        
        # Configuration manager
        self.config_manager: Optional[DatabaseConfigurationManager] = None
        
        # Infrastructure components
        self.health_monitor: Optional[DatabaseHealthMonitor] = None
        self.pool_manager: Optional[ConnectionPoolManager] = None
        self.transaction_manager: Optional[TransactionManager] = None
        self.session_manager: Optional[SessionManager] = None
        self.failover_manager: Optional[FailoverManager] = None
        self.load_balancer: Optional[DatabaseLoadBalancer] = None
        
        # Connection handlers registry
        self.handlers: Dict[str, Any] = {}
        
        # Handler type mapping
        self.handler_classes = {
            "postgresql": PostgreSQLConnectionHandler,
            "redis": RedisConnectionHandler,
            "mongodb": MongoDBConnectionHandler,
            "elasticsearch": ElasticsearchConnectionHandler,
            "vector_store": VectorStoreConnectionHandler,
            "object_storage": ObjectStorageConnectionHandler
        }
        
        # Factory statistics
        self.stats = {
            "connections_created": 0,
            "connections_failed": 0,
            "handlers_initialized": 0,
            "infrastructure_setup": False
        }
    
    async def initialize(self, config_dir: Optional[str] = None) -> None:
        """Initialize the connection factory"""
        
        self.logger.info("Initializing database connection factory...")
        
        # Initialize configuration manager
        self.config_manager = DatabaseConfigurationManager(self.environment)
        await self.config_manager.initialize(config_dir)
        
        # Setup infrastructure components
        await self._setup_infrastructure()
        
        self.stats["infrastructure_setup"] = True
        self.logger.info("Database connection factory initialized successfully")
    
    async def _setup_infrastructure(self) -> None:
        """Setup infrastructure components"""
        
        # Health monitor
        self.health_monitor = DatabaseHealthMonitor()
        await self.health_monitor.initialize()
        
        # Pool manager
        self.pool_manager = ConnectionPoolManager()
        await self.pool_manager.initialize()
        
        # Transaction manager
        self.transaction_manager = TransactionManager()
        await self.transaction_manager.initialize()
        
        # Session manager
        self.session_manager = SessionManager()
        await self.session_manager.initialize()
        
        # Failover manager
        self.failover_manager = FailoverManager()
        
        # Load balancer
        self.load_balancer = DatabaseLoadBalancer()
        
        self.logger.info("Infrastructure components initialized")
    
    async def create_connection(self, 
                              handler_type: str, 
                              tenant_id: Optional[str] = None,
                              custom_config: Optional[Dict[str, Any]] = None) -> Any:
        """Create a database connection handler"""
        
        try:
            # Validate handler type
            if handler_type not in self.handler_classes:
                raise ValueError(f"Unknown handler type: {handler_type}")
            
            # Get configuration
            config = await self._get_connection_config(handler_type, tenant_id, custom_config)
            
            # Create handler instance
            handler_class = self.handler_classes[handler_type]
            handler = handler_class()
            
            # Initialize handler
            await handler.initialize(config, tenant_id)
            
            # Setup infrastructure integration
            await self._integrate_handler(handler, handler_type, tenant_id)
            
            # Register handler
            handler_key = f"{handler_type}:{tenant_id or 'global'}"
            self.handlers[handler_key] = handler
            
            self.stats["connections_created"] += 1
            self.stats["handlers_initialized"] += 1
            
            self.logger.info(f"Created {handler_type} connection handler for tenant {tenant_id or 'global'}")
            return handler
            
        except Exception as e:
            self.stats["connections_failed"] += 1
            self.logger.error(f"Failed to create {handler_type} connection: {e}")
            raise
    
    async def _get_connection_config(self, 
                                   handler_type: str, 
                                   tenant_id: Optional[str],
                                   custom_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get connection configuration"""
        
        # Start with configuration from config manager
        config = self.config_manager.get_database_config(handler_type, tenant_id)
        
        if not config:
            raise ValueError(f"No configuration found for {handler_type}")
        
        # Convert configuration object to dictionary
        if hasattr(config, '__dict__'):
            config_dict = config.__dict__.copy()
        else:
            config_dict = dict(config)
        
        # Apply custom configuration overrides
        if custom_config:
            config_dict.update(custom_config)
        
        return config_dict
    
    async def _integrate_handler(self, handler: Any, handler_type: str, tenant_id: Optional[str]) -> None:
        """Integrate handler with infrastructure components"""
        
        # Set up health monitoring
        if self.health_monitor and hasattr(handler, 'set_health_monitor'):
            handler.set_health_monitor(self.health_monitor)
        
        # Set up pool management
        if self.pool_manager and hasattr(handler, 'set_pool_manager'):
            handler.set_pool_manager(self.pool_manager)
        
        # Set up transaction management
        if self.transaction_manager and hasattr(handler, 'set_transaction_manager'):
            handler.set_transaction_manager(self.transaction_manager)
        
        # Set up session management
        if self.session_manager and hasattr(handler, 'set_session_manager'):
            handler.set_session_manager(self.session_manager)
        
        # Register with failover manager
        if self.failover_manager:
            # This would register the handler for failover scenarios
            pass
        
        # Register with load balancer
        if self.load_balancer:
            # This would register the handler for load balancing
            pass
    
    async def create_tenant_connections(self, tenant_id: str) -> Dict[str, Any]:
        """Create all connections for a specific tenant"""
        
        if not self.config_manager:
            raise RuntimeError("Factory not initialized")
        
        tenant_config = self.config_manager.get_tenant_config(tenant_id)
        if not tenant_config:
            raise ValueError(f"No configuration found for tenant {tenant_id}")
        
        connections = {}
        
        # Create connections based on tenant configuration
        for handler_type in self.handler_classes.keys():
            try:
                connection = await self.create_connection(handler_type, tenant_id)
                connections[handler_type] = connection
            except Exception as e:
                self.logger.warning(f"Failed to create {handler_type} for tenant {tenant_id}: {e}")
        
        self.logger.info(f"Created {len(connections)} connections for tenant {tenant_id}")
        return connections
    
    async def create_global_connections(self) -> Dict[str, Any]:
        """Create global (shared) connections"""
        
        connections = {}
        
        for handler_type in self.handler_classes.keys():
            try:
                connection = await self.create_connection(handler_type)
                connections[handler_type] = connection
            except Exception as e:
                self.logger.warning(f"Failed to create global {handler_type}: {e}")
        
        self.logger.info(f"Created {len(connections)} global connections")
        return connections
    
    def get_connection(self, handler_type: str, tenant_id: Optional[str] = None) -> Optional[Any]:
        """Get existing connection handler"""
        handler_key = f"{handler_type}:{tenant_id or 'global'}"
        return self.handlers.get(handler_key)
    
    def list_connections(self) -> List[str]:
        """List all active connections"""
        return list(self.handlers.keys())
    
    async def validate_connection(self, handler_type: str, tenant_id: Optional[str] = None) -> bool:
        """Validate a connection"""
        
        handler = self.get_connection(handler_type, tenant_id)
        if not handler:
            return False
        
        try:
            # Perform health check
            if hasattr(handler, 'health_check'):
                return await handler.health_check()
            return True
        except Exception as e:
            self.logger.error(f"Connection validation failed for {handler_type}: {e}")
            return False
    
    async def close_connection(self, handler_type: str, tenant_id: Optional[str] = None) -> bool:
        """Close a specific connection"""
        
        handler_key = f"{handler_type}:{tenant_id or 'global'}"
        handler = self.handlers.get(handler_key)
        
        if not handler:
            return False
        
        try:
            if hasattr(handler, 'shutdown'):
                await handler.shutdown()
            
            del self.handlers[handler_key]
            self.logger.info(f"Closed connection {handler_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close connection {handler_key}: {e}")
            return False
    
    async def close_tenant_connections(self, tenant_id: str) -> int:
        """Close all connections for a tenant"""
        
        closed_count = 0
        handler_keys = [key for key in self.handlers.keys() if key.endswith(f":{tenant_id}")]
        
        for handler_key in handler_keys:
            handler_type = handler_key.split(':')[0]
            if await self.close_connection(handler_type, tenant_id):
                closed_count += 1
        
        self.logger.info(f"Closed {closed_count} connections for tenant {tenant_id}")
        return closed_count
    
    async def refresh_connection(self, handler_type: str, tenant_id: Optional[str] = None) -> bool:
        """Refresh a connection (close and recreate)"""
        
        try:
            # Close existing connection
            await self.close_connection(handler_type, tenant_id)
            
            # Create new connection
            await self.create_connection(handler_type, tenant_id)
            
            self.logger.info(f"Refreshed connection {handler_type} for tenant {tenant_id or 'global'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh connection {handler_type}: {e}")
            return False
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all active connections"""
        
        results = {}
        
        for handler_key in self.handlers.keys():
            handler_type, tenant_id = handler_key.split(':')
            tenant_id = tenant_id if tenant_id != 'global' else None
            
            results[handler_key] = await self.validate_connection(handler_type, tenant_id)
        
        successful = sum(1 for result in results.values() if result)
        total = len(results)
        
        self.logger.info(f"Connection test results: {successful}/{total} successful")
        return results
    
    async def add_tenant(self, tenant_config: TenantConfig) -> bool:
        """Add a new tenant and create its connections"""
        
        try:
            # Add tenant to configuration manager
            success = await self.config_manager.add_tenant(tenant_config)
            if not success:
                return False
            
            # Create tenant connections
            connections = await self.create_tenant_connections(tenant_config.tenant_id)
            
            self.logger.info(f"Added tenant {tenant_config.tenant_id} with {len(connections)} connections")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add tenant {tenant_config.tenant_id}: {e}")
            return False
    
    async def remove_tenant(self, tenant_id: str) -> bool:
        """Remove a tenant and close its connections"""
        
        try:
            # Close tenant connections
            closed_count = await self.close_tenant_connections(tenant_id)
            
            # Remove tenant from configuration manager
            success = await self.config_manager.remove_tenant(tenant_id)
            
            self.logger.info(f"Removed tenant {tenant_id} (closed {closed_count} connections)")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to remove tenant {tenant_id}: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get factory metrics"""
        
        # Connection status
        connection_status = {}
        for handler_key, handler in self.handlers.items():
            try:
                if hasattr(handler, 'get_metrics'):
                    metrics = await handler.get_metrics()
                    connection_status[handler_key] = {
                        "status": "healthy",
                        "metrics": metrics
                    }
                else:
                    connection_status[handler_key] = {"status": "unknown"}
            except Exception as e:
                connection_status[handler_key] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Infrastructure metrics
        infrastructure_metrics = {}
        
        if self.health_monitor:
            infrastructure_metrics["health_monitor"] = await self.health_monitor.get_metrics()
        
        if self.pool_manager:
            infrastructure_metrics["pool_manager"] = await self.pool_manager.get_metrics()
        
        if self.transaction_manager:
            infrastructure_metrics["transaction_manager"] = await self.transaction_manager.get_metrics()
        
        if self.session_manager:
            infrastructure_metrics["session_manager"] = await self.session_manager.get_metrics()
        
        if self.config_manager:
            infrastructure_metrics["config_manager"] = await self.config_manager.get_metrics()
        
        return {
            "factory_statistics": self.stats,
            "active_connections": len(self.handlers),
            "connection_status": connection_status,
            "infrastructure_metrics": infrastructure_metrics,
            "environment": self.environment.value,
            "initialized": self.stats["infrastructure_setup"]
        }
    
    async def shutdown(self) -> None:
        """Shutdown the connection factory"""
        
        self.logger.info("Shutting down database connection factory...")
        
        # Close all connections
        for handler_key in list(self.handlers.keys()):
            handler_type, tenant_id = handler_key.split(':')
            tenant_id = tenant_id if tenant_id != 'global' else None
            await self.close_connection(handler_type, tenant_id)
        
        # Shutdown infrastructure components
        if self.session_manager:
            await self.session_manager.shutdown()
        
        if self.transaction_manager:
            await self.transaction_manager.shutdown()
        
        if self.pool_manager:
            await self.pool_manager.shutdown()
        
        if self.health_monitor:
            await self.health_monitor.shutdown()
        
        if self.failover_manager:
            await self.failover_manager.shutdown()
        
        if self.load_balancer:
            await self.load_balancer.shutdown()
        
        if self.config_manager:
            await self.config_manager.shutdown()
        
        # Clear references
        self.handlers.clear()
        self.config_manager = None
        self.health_monitor = None
        self.pool_manager = None
        self.transaction_manager = None
        self.session_manager = None
        self.failover_manager = None
        self.load_balancer = None
        
        self.logger.info("Database connection factory shutdown completed")


# Global factory instance
_factory_instance: Optional[DatabaseConnectionFactory] = None


async def get_factory(environment: Environment = Environment.DEVELOPMENT) -> DatabaseConnectionFactory:
    """Get global factory instance"""
    global _factory_instance
    
    if _factory_instance is None:
        _factory_instance = DatabaseConnectionFactory(environment)
        await _factory_instance.initialize()
    
    return _factory_instance


async def shutdown_factory() -> None:
    """Shutdown global factory instance"""
    global _factory_instance
    
    if _factory_instance:
        await _factory_instance.shutdown()
        _factory_instance = None
