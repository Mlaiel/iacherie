"""Database Replication Index - IA Influencer Agent Platform

Main entry point and orchestrator for the enterprise database replication system.
Provides unified interface for initializing, managing, and monitoring all
replication components across multiple database types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import signal
import sys

from .config import ReplicationConfig
from .manager import ReplicationManager
from .master import ReplicationMaster
from .coordinator import ReplicationCoordinator
from .postgresql import PostgreSQLReplicationHandler
from .redis import RedisReplicationHandler
from .mongodb import MongoDBReplicationHandler
from .elasticsearch import ElasticsearchReplicationHandler
from .vector_stores import VectorStoreReplicationHandler
from .topology import TopologyManager
from .health_monitor import ReplicationHealthMonitor
from .conflict_resolver import ConflictResolver
from .failover import FailoverManager
from .metrics import ReplicationMetrics
from .utils import ReplicationUtils


class ReplicationOrchestrator:
    """
    Main orchestrator for the database replication system.
    
    Coordinates all replication components, provides unified API,
    and manages the complete lifecycle of the replication infrastructure
    for the IA Influencer Agent platform.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the replication orchestrator.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.ReplicationOrchestrator")
        
        # Core configuration
        self.config = ReplicationConfig.from_file(config_path) if config_path else ReplicationConfig()
        self.is_initialized = False
        self.is_running = False
        
        # Core components
        self.master: Optional[ReplicationMaster] = None
        self.manager: Optional[ReplicationManager] = None
        self.coordinator: Optional[ReplicationCoordinator] = None
        self.topology_manager: Optional[TopologyManager] = None
        self.health_monitor: Optional[ReplicationHealthMonitor] = None
        self.conflict_resolver: Optional[ConflictResolver] = None
        self.failover_manager: Optional[FailoverManager] = None
        self.metrics: Optional[ReplicationMetrics] = None
        
        # Database handlers
        self.database_handlers: Dict[str, Any] = {}
        
        # Runtime state
        self.start_time: Optional[datetime] = None
        self.shutdown_event = asyncio.Event()
        
        # Signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        self.logger.info("ReplicationOrchestrator initialized")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self) -> bool:
        """
        Initialize all replication components.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing replication orchestrator...")
            
            # Initialize metrics first
            await self._initialize_metrics()
            
            # Initialize core infrastructure
            await self._initialize_topology_manager()
            await self._initialize_conflict_resolver()
            await self._initialize_health_monitor()
            await self._initialize_failover_manager()
            
            # Initialize database handlers
            await self._initialize_database_handlers()
            
            # Initialize coordination layer
            await self._initialize_coordinator()
            await self._initialize_manager()
            await self._initialize_master()
            
            # Validate initialization
            await self._validate_initialization()
            
            self.is_initialized = True
            self.logger.info("Replication orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize replication orchestrator: {e}")
            await self._cleanup_failed_initialization()
            return False
    
    async def _initialize_metrics(self) -> None:
        """Initialize metrics collection system"""
        try:
            self.metrics = ReplicationMetrics(self.config)
            await self.metrics.initialize()
            self.logger.info("Metrics system initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics: {e}")
            raise
    
    async def _initialize_topology_manager(self) -> None:
        """Initialize topology manager"""
        try:
            self.topology_manager = TopologyManager(self.config)
            await self.topology_manager.initialize()
            self.logger.info("Topology manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize topology manager: {e}")
            raise
    
    async def _initialize_conflict_resolver(self) -> None:
        """Initialize conflict resolver"""
        try:
            self.conflict_resolver = ConflictResolver(self.config)
            await self.conflict_resolver.initialize()
            self.logger.info("Conflict resolver initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize conflict resolver: {e}")
            raise
    
    async def _initialize_health_monitor(self) -> None:
        """Initialize health monitoring system"""
        try:
            self.health_monitor = ReplicationHealthMonitor(
                self.config, 
                topology_manager=self.topology_manager
            )
            await self.health_monitor.initialize()
            self.logger.info("Health monitor initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize health monitor: {e}")
            raise
    
    async def _initialize_failover_manager(self) -> None:
        """Initialize failover management system"""
        try:
            self.failover_manager = FailoverManager(
                self.config, 
                topology_manager=self.topology_manager
            )
            await self.failover_manager.initialize()
            self.logger.info("Failover manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize failover manager: {e}")
            raise
    
    async def _initialize_database_handlers(self) -> None:
        """Initialize database-specific replication handlers"""
        try:
            enabled_databases = self.config.get_enabled_databases()
            
            for db_type in enabled_databases:
                handler = await self._create_database_handler(db_type)
                if handler:
                    self.database_handlers[db_type] = handler
                    self.logger.info(f"{db_type} handler initialized")
            
            self.logger.info(f"Database handlers initialized: {list(self.database_handlers.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database handlers: {e}")
            raise
    
    async def _create_database_handler(self, db_type: str) -> Optional[Any]:
        """Create handler for specific database type"""
        try:
            if db_type == "postgresql":
                handler = PostgreSQLReplicationHandler(
                    self.config, 
                    topology_manager=self.topology_manager,
                    conflict_resolver=self.conflict_resolver
                )
            elif db_type == "redis":
                handler = RedisReplicationHandler(
                    self.config,
                    topology_manager=self.topology_manager,
                    conflict_resolver=self.conflict_resolver
                )
            elif db_type == "mongodb":
                handler = MongoDBReplicationHandler(
                    self.config,
                    topology_manager=self.topology_manager,
                    conflict_resolver=self.conflict_resolver
                )
            elif db_type == "elasticsearch":
                handler = ElasticsearchReplicationHandler(
                    self.config,
                    topology_manager=self.topology_manager,
                    conflict_resolver=self.conflict_resolver
                )
            elif db_type == "vector_stores":
                handler = VectorStoreReplicationHandler(
                    self.config,
                    topology_manager=self.topology_manager,
                    conflict_resolver=self.conflict_resolver
                )
            else:
                self.logger.warning(f"Unknown database type: {db_type}")
                return None
            
            # Initialize the handler
            await handler.initialize()
            return handler
            
        except Exception as e:
            self.logger.error(f"Failed to create {db_type} handler: {e}")
            return None
    
    async def _initialize_coordinator(self) -> None:
        """Initialize replication coordinator"""
        try:
            self.coordinator = ReplicationCoordinator(
                self.config,
                database_handlers=self.database_handlers,
                topology_manager=self.topology_manager,
                conflict_resolver=self.conflict_resolver,
                metrics=self.metrics
            )
            await self.coordinator.initialize()
            self.logger.info("Replication coordinator initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize coordinator: {e}")
            raise
    
    async def _initialize_manager(self) -> None:
        """Initialize replication manager"""
        try:
            self.manager = ReplicationManager(
                self.config,
                coordinator=self.coordinator,
                health_monitor=self.health_monitor,
                failover_manager=self.failover_manager,
                metrics=self.metrics
            )
            await self.manager.initialize()
            self.logger.info("Replication manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize manager: {e}")
            raise
    
    async def _initialize_master(self) -> None:
        """Initialize replication master"""
        try:
            self.master = ReplicationMaster(
                self.config,
                manager=self.manager,
                topology_manager=self.topology_manager,
                health_monitor=self.health_monitor,
                failover_manager=self.failover_manager
            )
            await self.master.initialize()
            self.logger.info("Replication master initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize master: {e}")
            raise
    
    async def _validate_initialization(self) -> None:
        """Validate that all components are properly initialized"""
        try:
            components = {
                "master": self.master,
                "manager": self.manager,
                "coordinator": self.coordinator,
                "topology_manager": self.topology_manager,
                "health_monitor": self.health_monitor,
                "conflict_resolver": self.conflict_resolver,
                "failover_manager": self.failover_manager,
                "metrics": self.metrics
            }
            
            for name, component in components.items():
                if not component:
                    raise ValueError(f"Component {name} not initialized")
            
            # Validate database handlers
            if not self.database_handlers:
                raise ValueError("No database handlers initialized")
            
            # Perform connectivity tests
            await self._test_component_connectivity()
            
            self.logger.info("Component validation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Component validation failed: {e}")
            raise
    
    async def _test_component_connectivity(self) -> None:
        """Test connectivity between components"""
        try:
            # Test topology manager
            topology_status = await self.topology_manager.get_topology_status()
            if not topology_status.get("healthy", False):
                raise ValueError("Topology manager not healthy")
            
            # Test database connections
            for db_type, handler in self.database_handlers.items():
                connection_status = await handler.test_connection()
                if not connection_status:
                    raise ValueError(f"{db_type} handler connection failed")
            
            self.logger.info("Component connectivity tests passed")
            
        except Exception as e:
            self.logger.error(f"Component connectivity test failed: {e}")
            raise
    
    async def _cleanup_failed_initialization(self) -> None:
        """Cleanup after failed initialization"""
        try:
            self.logger.info("Cleaning up after failed initialization...")
            
            # Shutdown components in reverse order
            components = [
                self.master,
                self.manager,
                self.coordinator,
                self.failover_manager,
                self.health_monitor,
                self.conflict_resolver,
                self.topology_manager,
                self.metrics
            ]
            
            for component in components:
                if component:
                    try:
                        await component.shutdown()
                    except Exception as e:
                        self.logger.error(f"Error shutting down component: {e}")
            
            # Shutdown database handlers
            for handler in self.database_handlers.values():
                try:
                    await handler.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down database handler: {e}")
            
            self.database_handlers.clear()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def start(self) -> bool:
        """
        Start the replication system.
        
        Returns:
            bool: True if started successfully
        """
        try:
            if not self.is_initialized:
                self.logger.error("Cannot start: system not initialized")
                return False
            
            if self.is_running:
                self.logger.warning("Replication system already running")
                return True
            
            self.logger.info("Starting replication system...")
            self.start_time = datetime.utcnow()
            
            # Start components in order
            await self.health_monitor.start()
            await self.failover_manager.start()
            
            # Start database handlers
            for db_type, handler in self.database_handlers.items():
                await handler.start_replication()
                self.logger.info(f"{db_type} replication started")
            
            # Start coordination layer
            await self.coordinator.start()
            await self.manager.start()
            await self.master.start()
            
            self.is_running = True
            
            # Log startup metrics
            startup_metrics = {
                "start_time": self.start_time.isoformat(),
                "enabled_databases": list(self.database_handlers.keys()),
                "component_count": len([c for c in [
                    self.master, self.manager, self.coordinator,
                    self.topology_manager, self.health_monitor,
                    self.conflict_resolver, self.failover_manager
                ] if c])
            }
            
            self.logger.info(f"Replication system started successfully: {startup_metrics}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start replication system: {e}")
            await self._emergency_shutdown()
            return False
    
    async def stop(self) -> bool:
        """
        Stop the replication system gracefully.
        
        Returns:
            bool: True if stopped successfully
        """
        try:
            if not self.is_running:
                self.logger.warning("Replication system not running")
                return True
            
            self.logger.info("Stopping replication system...")
            
            # Stop components in reverse order
            await self.master.stop()
            await self.manager.stop()
            await self.coordinator.stop()
            
            # Stop database handlers
            for db_type, handler in self.database_handlers.items():
                await handler.stop_replication()
                self.logger.info(f"{db_type} replication stopped")
            
            await self.failover_manager.stop()
            await self.health_monitor.stop()
            
            self.is_running = False
            
            # Calculate uptime
            if self.start_time:
                uptime = datetime.utcnow() - self.start_time
                self.logger.info(f"Replication system stopped after {uptime}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping replication system: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the replication system completely"""
        try:
            self.logger.info("Shutting down replication system...")
            
            # Stop if running
            if self.is_running:
                await self.stop()
            
            # Shutdown all components
            await self._cleanup_failed_initialization()
            
            # Set shutdown event
            self.shutdown_event.set()
            
            self.logger.info("Replication system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def _emergency_shutdown(self) -> None:
        """Emergency shutdown in case of critical errors"""
        try:
            self.logger.critical("Performing emergency shutdown...")
            
            self.is_running = False
            
            # Force shutdown all components
            tasks = []
            
            if self.master:
                tasks.append(self.master.shutdown())
            if self.manager:
                tasks.append(self.manager.shutdown())
            if self.coordinator:
                tasks.append(self.coordinator.shutdown())
            
            for handler in self.database_handlers.values():
                tasks.append(handler.shutdown())
            
            if self.failover_manager:
                tasks.append(self.failover_manager.shutdown())
            if self.health_monitor:
                tasks.append(self.health_monitor.shutdown())
            
            # Execute with timeout
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30
            )
            
            self.shutdown_event.set()
            
        except Exception as e:
            self.logger.critical(f"Emergency shutdown failed: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dict containing system status information
        """
        try:
            status = {
                "orchestrator": {
                    "initialized": self.is_initialized,
                    "running": self.is_running,
                    "start_time": self.start_time.isoformat() if self.start_time else None,
                    "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
                },
                "components": {},
                "databases": {},
                "overall_health": "unknown"
            }
            
            # Get component status
            if self.master:
                status["components"]["master"] = await self.master.get_status()
            if self.manager:
                status["components"]["manager"] = await self.manager.get_status()
            if self.coordinator:
                status["components"]["coordinator"] = await self.coordinator.get_status()
            if self.topology_manager:
                status["components"]["topology"] = await self.topology_manager.get_topology_status()
            if self.health_monitor:
                status["components"]["health_monitor"] = await self.health_monitor.get_health_status()
            if self.failover_manager:
                status["components"]["failover"] = self.failover_manager.get_failover_status()
            
            # Get database status
            for db_type, handler in self.database_handlers.items():
                status["databases"][db_type] = await handler.get_replication_status()
            
            # Calculate overall health
            status["overall_health"] = self._calculate_overall_health(status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_health(self, status: Dict[str, Any]) -> str:
        """Calculate overall system health"""
        try:
            if not self.is_running:
                return "stopped"
            
            # Check component health
            component_health = []
            for component_status in status.get("components", {}).values():
                if isinstance(component_status, dict):
                    health = component_status.get("healthy", False)
                    component_health.append(health)
            
            # Check database health
            database_health = []
            for db_status in status.get("databases", {}).values():
                if isinstance(db_status, dict):
                    health = db_status.get("healthy", False)
                    database_health.append(health)
            
            all_health = component_health + database_health
            
            if not all_health:
                return "unknown"
            
            healthy_count = sum(all_health)
            total_count = len(all_health)
            
            health_percentage = (healthy_count / total_count) * 100
            
            if health_percentage >= 90:
                return "healthy"
            elif health_percentage >= 70:
                return "degraded"
            else:
                return "unhealthy"
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall health: {e}")
            return "error"
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics.
        
        Returns:
            Dict containing system metrics
        """
        try:
            if not self.metrics:
                return {}
            
            return await self.metrics.get_comprehensive_metrics()
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
    
    async def trigger_manual_failover(self, node_id: str) -> bool:
        """
        Trigger manual failover for a specific node.
        
        Args:
            node_id: ID of the node to failover
            
        Returns:
            bool: True if failover initiated successfully
        """
        try:
            if not self.failover_manager:
                self.logger.error("Failover manager not available")
                return False
            
            return await self.failover_manager.trigger_manual_failover(node_id)
            
        except Exception as e:
            self.logger.error(f"Failed to trigger manual failover: {e}")
            return False
    
    async def run(self) -> None:
        """
        Run the replication system (main entry point).
        
        This method will run until shutdown is requested.
        """
        try:
            # Initialize system
            if not await self.initialize():
                self.logger.error("Failed to initialize replication system")
                return
            
            # Start system
            if not await self.start():
                self.logger.error("Failed to start replication system")
                return
            
            self.logger.info("Replication system is now running. Press Ctrl+C to stop.")
            
            # Wait for shutdown event
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in main run loop: {e}")
        finally:
            await self.shutdown()


# Factory functions for easy instantiation
def create_replication_orchestrator(config_path: Optional[str] = None) -> ReplicationOrchestrator:
    """
    Factory function to create a replication orchestrator.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ReplicationOrchestrator instance
    """
    return ReplicationOrchestrator(config_path)


async def run_replication_system(config_path: Optional[str] = None) -> None:
    """
    Convenience function to run the complete replication system.
    
    Args:
        config_path: Path to configuration file
    """
    orchestrator = create_replication_orchestrator(config_path)
    await orchestrator.run()


# CLI entry point
async def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="IA Influencer Agent Database Replication System")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run replication system
    await run_replication_system(args.config)


if __name__ == "__main__":
    # Ensure we're using the correct event loop policy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the main function
    asyncio.run(main())
