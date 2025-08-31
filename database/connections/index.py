"""Database Connections Index - IA Influencer Agent Platform

Main entry point for database connections management.
Provides centralized access to all connection types and management functions.

Business Logic Flow:
Content Creator → Multi-Database Operations → AI Processing → 
Protection Monitoring → Revenue Tracking → Collaboration Distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from contextlib import asynccontextmanager

# Import all connection management components
from .manager import DatabaseConnectionManager, get_connection_manager
from .factory import DatabaseConnectionFactory, ConnectionSpec
from .config_manager import DatabaseConfigurationManager, Environment
from .tenant_manager import TenantConnectionManager, TenantType, TenantConfig

# Import specific database handlers
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


logger = logging.getLogger(__name__)


class DatabaseConnectionsIndex:
    """
    Central index for all database connections and operations.
    
    Features:
    - Unified access to all database types
    - Multi-tenant connection management
    - Health monitoring and failover
    - Transaction coordination
    - Performance optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection_manager: Optional[DatabaseConnectionManager] = None
        self.tenant_manager: Optional[TenantConnectionManager] = None
        self.factory: Optional[DatabaseConnectionFactory] = None
        self.config_manager: Optional[DatabaseConfigurationManager] = None
        
        # Component registries
        self.handlers: Dict[str, Any] = {}
        self.active_connections: Dict[str, List[Any]] = {}
        self.connection_stats: Dict[str, Dict[str, int]] = {}
        
        self._initialized = False
    
    async def initialize(
        self,
        config: Optional[Dict[str, Any]] = None,
        environment: Environment = Environment.DEVELOPMENT
    ) -> None:
        """
        Initialize all database connections and components.
        
        Args:
            config: Configuration dictionary for all databases
            environment: Deployment environment
        """
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing Database Connections Index...")
            
            # Initialize configuration manager
            self.config_manager = DatabaseConfigurationManager(environment)
            if config:
                await self.config_manager.load_configuration(config)
            
            # Initialize connection factory
            self.factory = DatabaseConnectionFactory(environment)
            await self.factory.initialize(self.config_manager)
            
            # Initialize main connection manager
            self.connection_manager = DatabaseConnectionManager(
                self.config_manager.get_all_configs()
            )
            await self.connection_manager.initialize()
            
            # Initialize tenant manager
            self.tenant_manager = TenantConnectionManager(
                self.config_manager.get_tenant_configs()
            )
            
            # Register all handlers
            await self._register_handlers()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            self._initialized = True
            self.logger.info("Database Connections Index initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Database Connections Index: {e}")
            raise
    
    async def get_connection(
        self,
        database_type: str,
        tenant_id: Optional[str] = None,
        readonly: bool = False
    ) -> Any:
        """
        Get database connection with optional tenant isolation.
        
        Args:
            database_type: Type of database (postgresql, redis, mongodb, etc.)
            tenant_id: Optional tenant ID for multi-tenant isolation
            readonly: Whether connection is for read-only operations
            
        Returns:
            Database connection object
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            if tenant_id:
                # Get tenant-isolated connection
                return await self.tenant_manager.get_tenant_connection(
                    tenant_id, database_type, readonly
                )
            else:
                # Get standard connection
                return await self.connection_manager.get_connection(
                    database_type, readonly
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get {database_type} connection: {e}")
            raise
    
    @asynccontextmanager
    async def session(
        self,
        database_type: str = "postgresql",
        tenant_id: Optional[str] = None,
        readonly: bool = False
    ):
        """
        Context manager for database sessions.
        
        Usage:
            async with db_index.session("postgresql", "artist_123") as session:
                result = await session.execute(query)
        """
        connection = None
        try:
            connection = await self.get_connection(database_type, tenant_id, readonly)
            yield connection
        finally:
            if connection:
                await self._release_connection(connection, database_type, tenant_id)
    
    @asynccontextmanager
    async def distributed_transaction(
        self,
        tenant_id: Optional[str] = None,
        databases: Optional[List[str]] = None
    ):
        """
        Context manager for distributed transactions across multiple databases.
        
        Args:
            tenant_id: Optional tenant ID for isolation
            databases: List of databases to include in transaction
            
        Usage:
            async with db_index.distributed_transaction("artist_123") as tx:
                await tx.postgresql.execute(sql)
                await tx.mongodb.insert_one(document)
                await tx.commit()
        """
        if not self._initialized:
            await self.initialize()
        
        transaction = await self.connection_manager.begin_distributed_transaction(
            tenant_id, databases or ["postgresql", "mongodb", "redis"]
        )
        
        try:
            yield transaction
        except Exception:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()
    
    async def register_tenant(
        self,
        tenant_id: str,
        tenant_type: TenantType,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> TenantConfig:
        """
        Register new content creator tenant.
        
        Args:
            tenant_id: Unique tenant identifier
            tenant_type: Type of content creator
            config_overrides: Custom configuration settings
            
        Returns:
            TenantConfig object
        """
        if not self._initialized:
            await self.initialize()
        
        return await self.tenant_manager.register_tenant(
            tenant_id, tenant_type, config_overrides
        )
    
    async def create_collaboration(
        self,
        primary_tenant_id: str,
        collaborator_tenant_ids: List[str],
        collaboration_type: str,
        permissions: Dict[str, List[str]]
    ) -> str:
        """
        Create secure collaboration between content creators.
        
        Args:
            primary_tenant_id: Primary content creator
            collaborator_tenant_ids: Collaborating creators
            collaboration_type: Type of collaboration
            permissions: Granular permissions per collaborator
            
        Returns:
            Collaboration session ID
        """
        if not self._initialized:
            await self.initialize()
        
        return await self.tenant_manager.create_tenant_collaboration(
            primary_tenant_id, collaborator_tenant_ids, collaboration_type, permissions
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all database connections."""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "databases": {},
            "connections": {},
            "performance": {}
        }
        
        try:
            # Get health status from connection manager
            manager_health = await self.connection_manager.get_health_status()
            health_status["databases"] = manager_health
            
            # Get connection statistics
            health_status["connections"] = self.connection_stats
            
            # Get performance metrics
            health_status["performance"] = await self._get_performance_metrics()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health_status
    
    async def optimize_connections(self) -> Dict[str, Any]:
        """
        Perform connection optimization across all databases.
        
        Returns:
            Optimization results and recommendations
        """
        if not self._initialized:
            await self.initialize()
        
        optimization_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "optimizations": {},
            "recommendations": []
        }
        
        try:
            # Run optimization on connection manager
            manager_optimization = await self.connection_manager.optimize_connections()
            optimization_results["optimizations"]["manager"] = manager_optimization
            
            # Optimize tenant connections
            tenant_optimization = await self.tenant_manager.optimize_tenant_connections()
            optimization_results["optimizations"]["tenants"] = tenant_optimization
            
            # Generate recommendations
            optimization_results["recommendations"] = await self._generate_optimization_recommendations()
            
        except Exception as e:
            self.logger.error(f"Connection optimization failed: {e}")
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    async def get_connection_metrics(
        self,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed connection metrics.
        
        Args:
            tenant_id: Optional tenant ID for tenant-specific metrics
            
        Returns:
            Connection metrics and statistics
        """
        if not self._initialized:
            await self.initialize()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "global_metrics": {},
            "tenant_metrics": {},
            "performance_metrics": {}
        }
        
        try:
            # Global connection metrics
            metrics["global_metrics"] = await self.connection_manager.get_metrics()
            
            # Tenant-specific metrics
            if tenant_id:
                metrics["tenant_metrics"] = await self.tenant_manager.get_tenant_metrics(tenant_id)
            else:
                # All tenant metrics
                all_tenants = await self.tenant_manager.get_all_tenant_metrics()
                metrics["tenant_metrics"] = all_tenants
            
            # Performance metrics
            metrics["performance_metrics"] = await self._get_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Failed to get connection metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    async def _register_handlers(self):
        """Register all database handlers with the factory."""
        handler_types = [
            "postgresql", "redis", "mongodb", "elasticsearch", 
            "vector_store", "object_storage"
        ]
        
        for handler_type in handler_types:
            try:
                handler = await self.factory.create_handler(handler_type)
                self.handlers[handler_type] = handler
                self.connection_stats[handler_type] = {
                    "active_connections": 0,
                    "total_queries": 0,
                    "error_count": 0
                }
                self.logger.info(f"Registered {handler_type} handler")
            except Exception as e:
                self.logger.error(f"Failed to register {handler_type} handler: {e}")
    
    async def _setup_monitoring(self):
        """Setup monitoring for all database connections."""
        try:
            # Initialize health monitoring
            health_monitor = DatabaseHealthMonitor()
            await health_monitor.initialize(self.handlers)
            
            # Start periodic health checks
            asyncio.create_task(self._periodic_health_check())
            
            self.logger.info("Database monitoring setup completed")
        except Exception as e:
            self.logger.error(f"Failed to setup monitoring: {e}")
    
    async def _periodic_health_check(self):
        """Periodic health check for all connections."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                health_status = await self.get_health_status()
                
                # Log any unhealthy connections
                for db_type, status in health_status.get("databases", {}).items():
                    if status.get("status") != "healthy":
                        self.logger.warning(f"Database {db_type} is unhealthy: {status}")
                
            except Exception as e:
                self.logger.error(f"Periodic health check failed: {e}")
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all database connections."""
        metrics = {
            "query_latency": {},
            "connection_utilization": {},
            "throughput": {},
            "error_rates": {}
        }
        
        for db_type, handler in self.handlers.items():
            try:
                if hasattr(handler, 'get_performance_metrics'):
                    handler_metrics = await handler.get_performance_metrics()
                    metrics["query_latency"][db_type] = handler_metrics.get("latency", 0)
                    metrics["connection_utilization"][db_type] = handler_metrics.get("utilization", 0)
                    metrics["throughput"][db_type] = handler_metrics.get("throughput", 0)
                    metrics["error_rates"][db_type] = handler_metrics.get("error_rate", 0)
            except Exception as e:
                self.logger.error(f"Failed to get metrics for {db_type}: {e}")
        
        return metrics
    
    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        try:
            performance_metrics = await self._get_performance_metrics()
            
            # Check query latency
            for db_type, latency in performance_metrics["query_latency"].items():
                if latency > 2000:  # 2 seconds
                    recommendations.append(
                        f"Consider optimizing {db_type} queries - high latency: {latency}ms"
                    )
            
            # Check connection utilization
            for db_type, utilization in performance_metrics["connection_utilization"].items():
                if utilization > 0.8:  # 80%
                    recommendations.append(
                        f"Consider increasing {db_type} connection pool size - utilization: {utilization:.1%}"
                    )
            
            # Check error rates
            for db_type, error_rate in performance_metrics["error_rates"].items():
                if error_rate > 0.05:  # 5%
                    recommendations.append(
                        f"Investigate {db_type} connection errors - error rate: {error_rate:.1%}"
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    async def _release_connection(
        self,
        connection: Any,
        database_type: str,
        tenant_id: Optional[str] = None
    ):
        """Release database connection back to pool."""
        try:
            if tenant_id:
                await self.tenant_manager._release_tenant_connection(tenant_id, connection)
            else:
                await self.connection_manager.release_connection(connection, database_type)
        except Exception as e:
            self.logger.error(f"Failed to release {database_type} connection: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown all database connections."""
        if not self._initialized:
            return
        
        try:
            self.logger.info("Shutting down Database Connections Index...")
            
            # Shutdown connection manager
            if self.connection_manager:
                await self.connection_manager.shutdown()
            
            # Shutdown tenant manager
            if self.tenant_manager:
                await self.tenant_manager.shutdown()
            
            # Close all handlers
            for handler in self.handlers.values():
                if hasattr(handler, 'shutdown'):
                    await handler.shutdown()
            
            self._initialized = False
            self.logger.info("Database Connections Index shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Global instance for easy access
_db_index: Optional[DatabaseConnectionsIndex] = None


async def get_database_index() -> DatabaseConnectionsIndex:
    """Get or create global database connections index."""
    global _db_index
    
    if _db_index is None:
        _db_index = DatabaseConnectionsIndex()
    
    if not _db_index._initialized:
        await _db_index.initialize()
    
    return _db_index


# Convenience functions for common operations
async def get_connection(
    database_type: str,
    tenant_id: Optional[str] = None,
    readonly: bool = False
) -> Any:
    """Convenience function to get database connection."""
    db_index = await get_database_index()
    return await db_index.get_connection(database_type, tenant_id, readonly)


async def session(
    database_type: str = "postgresql",
    tenant_id: Optional[str] = None,
    readonly: bool = False
):
    """Convenience function for database session context manager."""
    db_index = await get_database_index()
    return db_index.session(database_type, tenant_id, readonly)


async def distributed_transaction(
    tenant_id: Optional[str] = None,
    databases: Optional[List[str]] = None
):
    """Convenience function for distributed transaction context manager."""
    db_index = await get_database_index()
    return db_index.distributed_transaction(tenant_id, databases)


# Export main components
__all__ = [
    "DatabaseConnectionsIndex",
    "get_database_index",
    "get_connection",
    "session",
    "distributed_transaction",
    "DatabaseConnectionManager",
    "TenantConnectionManager",
    "DatabaseConnectionFactory",
    "TenantType",
    "TenantConfig"
]
