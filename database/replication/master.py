"""
Replication Master Orchestrator - IA Influencer Agent Platform

Central orchestrator for all database replication activities across the content creator ecosystem.
Manages PostgreSQL, Redis, MongoDB, Elasticsearch, and Vector store replication with automated
failover, conflict resolution, and cross-region synchronization.

This module coordinates:
- Multi-database replication topology
- Automated failover and disaster recovery
- Cross-region data synchronization
- Performance monitoring and alerting
- Conflict detection and resolution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from .manager import ReplicationManager
from .coordinator import ReplicationCoordinator
from .topology import TopologyManager
from .health_monitor import ReplicationHealthMonitor
from .failover import FailoverManager
from .config import ReplicationConfig
from .metrics import ReplicationMetrics
from .utils import ReplicationUtils


class ReplicationMode(Enum):
    """Replication operational modes"""
    MASTER_SLAVE = "master_slave"
    MASTER_MASTER = "master_master"
    CLUSTER = "cluster"
    HYBRID = "hybrid"


class ReplicationStatus(Enum):
    """Replication system status"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    MAINTENANCE = "maintenance"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class ReplicationTopology:
    """Replication topology configuration"""
    primary_region: str
    secondary_regions: List[str]
    database_configs: Dict[str, Any]
    failover_policies: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


class ReplicationMaster:
    """
    Master orchestrator for enterprise database replication.
    
    Coordinates all replication activities across multiple database systems,
    providing high availability, disaster recovery, and performance optimization
    for the IA Influencer Agent platform serving content creators globally.
    """
    
    def __init__(self, config: ReplicationConfig):
        """Initialize replication master with comprehensive configuration"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReplicationMaster")
        
        # Core components
        self.manager = ReplicationManager(config)
        self.coordinator = ReplicationCoordinator(config)
        self.topology_manager = TopologyManager(config)
        self.health_monitor = ReplicationHealthMonitor(config)
        self.failover_manager = FailoverManager(config)
        self.metrics = ReplicationMetrics(config)
        self.utils = ReplicationUtils(config)
        
        # State management
        self.status = ReplicationStatus.INITIALIZING
        self.topology: Optional[ReplicationTopology] = None
        self.active_replications: Set[str] = set()
        self.failed_replications: Set[str] = set()
        self.maintenance_windows: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        self.replication_metrics: Dict[str, Any] = {}
        
        self.logger.info("ReplicationMaster initialized successfully")
    
    async def initialize(self) -> bool:
        """
        Initialize the complete replication infrastructure.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """



        try:
            self.logger.info("Initializing replication master infrastructure...")
            self.start_time = datetime.utcnow()
            
            # Initialize core components
            await self._initialize_components()
            
            # Setup replication topology
            await self._setup_topology()
            
            # Start health monitoring
            await self._start_monitoring()
            
            # Validate initial replication state
            if await self._validate_initial_state():
                self.status = ReplicationStatus.HEALTHY
                self.logger.info("Replication master initialization completed successfully")
                return True
            else:
                self.status = ReplicationStatus.DEGRADED
                self.logger.warning("Replication master initialized with degraded performance")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize replication master: {e}")
            self.status = ReplicationStatus.FAILING
            return False
    
    async def _initialize_components(self) -> None:
        """Initialize all replication components"""
        components = [
            ("Manager", self.manager.initialize()),
            ("Coordinator", self.coordinator.initialize()),
            ("Topology Manager", self.topology_manager.initialize()),
            ("Health Monitor", self.health_monitor.initialize()),
            ("Failover Manager", self.failover_manager.initialize()),
            ("Metrics", self.metrics.initialize())
        ]
        
        for name, coro in components:
            try:
                await coro
                self.logger.debug(f"{name} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name}: {e}")
                raise
    
    async def _setup_topology(self) -> None:
        """Setup replication topology based on configuration"""
        self.logger.info("Setting up replication topology...")
        
        # Extract topology configuration
        topology_config = self.config.get_topology_config()
        
        self.topology = ReplicationTopology(
            primary_region=topology_config.get("primary_region", "eu-west-1"),
            secondary_regions=topology_config.get("secondary_regions", ["us-east-1"]),
            database_configs=topology_config.get("databases", {}),
            failover_policies=topology_config.get("failover", {}),
            monitoring_config=topology_config.get("monitoring", {})
        )
        
        # Configure topology manager
        await self.topology_manager.setup_topology(self.topology)
        
        self.logger.info(f"Topology configured: Primary={self.topology.primary_region}, "
                        f"Secondaries={self.topology.secondary_regions}")
    
    async def _start_monitoring(self) -> None:
        """Start comprehensive health monitoring"""
        self.logger.info("Starting replication health monitoring...")
        
        # Start health monitoring for all components
        monitoring_tasks = [
            self.health_monitor.start_monitoring(),
            self.metrics.start_collection(),
            self._periodic_health_check()
        ]
        
        # Schedule monitoring tasks
        for task in monitoring_tasks:
            asyncio.create_task(task)
        
        self.logger.info("Health monitoring started successfully")
    
    async def _validate_initial_state(self) -> bool:
        """Validate initial replication state"""
        self.logger.info("Validating initial replication state...")
        
        try:
            # Check all database connections
            connection_health = await self.health_monitor.check_all_connections()
            
            # Validate replication channels
            replication_health = await self.coordinator.validate_all_replications()
            
            # Check failover readiness
            failover_ready = await self.failover_manager.validate_failover_readiness()
            
            overall_health = all([connection_health, replication_health, failover_ready])
            
            self.logger.info(f"Initial state validation: Connections={connection_health}, "
                           f"Replication={replication_health}, Failover={failover_ready}")
            
            return overall_health
            
        except Exception as e:
            self.logger.error(f"Failed to validate initial state: {e}")
            return False
    
    async def start_replication(self, database_type: str, mode: ReplicationMode = None) -> bool:
        """
        Start replication for specified database type.
        
        Args:
            database_type: Type of database (postgresql, redis, mongodb, etc.)
            mode: Replication mode override
            
        Returns:
            bool: True if replication started successfully
        """



        try:
            self.logger.info(f"Starting replication for {database_type}")
            
            # Get database-specific configuration
            db_config = self.config.get_database_config(database_type)
            if not db_config:
                self.logger.error(f"No configuration found for {database_type}")
                return False
            
            # Start replication through manager
            success = await self.manager.start_replication(database_type, db_config, mode)
            
            if success:
                self.active_replications.add(database_type)
                self.failed_replications.discard(database_type)
                self.logger.info(f"Replication started successfully for {database_type}")
            else:
                self.failed_replications.add(database_type)
                self.logger.error(f"Failed to start replication for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting replication for {database_type}: {e}")
            self.failed_replications.add(database_type)
            return False
    
    async def stop_replication(self, database_type: str, graceful: bool = True) -> bool:
        """
        Stop replication for specified database type.
        
        Args:
            database_type: Type of database to stop replication
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if replication stopped successfully
        """



        try:
            self.logger.info(f"Stopping replication for {database_type} (graceful={graceful})")
            
            # Stop replication through manager
            success = await self.manager.stop_replication(database_type, graceful)
            
            if success:
                self.active_replications.discard(database_type)
                self.logger.info(f"Replication stopped successfully for {database_type}")
            else:
                self.logger.error(f"Failed to stop replication for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error stopping replication for {database_type}: {e}")
            return False
    
    async def failover_database(self, database_type: str, target_region: str = None) -> bool:
        """
        Perform database failover to secondary region.
        
        Args:
            database_type: Database to failover
            target_region: Target region for failover (auto-select if None)
            
        Returns:
            bool: True if failover successful
        """



        try:
            self.logger.warning(f"Initiating failover for {database_type} to {target_region}")
            self.status = ReplicationStatus.DISASTER_RECOVERY
            
            # Execute failover through failover manager
            success = await self.failover_manager.execute_failover(
                database_type, 
                target_region or self.topology.secondary_regions[0]
            )
            
            if success:
                self.logger.info(f"Failover completed successfully for {database_type}")
                await self._update_topology_after_failover(database_type, target_region)
                self.status = ReplicationStatus.HEALTHY
            else:
                self.logger.error(f"Failover failed for {database_type}")
                self.status = ReplicationStatus.FAILING
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during failover for {database_type}: {e}")
            self.status = ReplicationStatus.FAILING
            return False
    
    async def _update_topology_after_failover(self, database_type: str, new_primary_region: str) -> None:
        """Update topology configuration after successful failover"""
        if self.topology and new_primary_region:
            # Update topology to reflect new primary
            await self.topology_manager.update_primary_region(database_type, new_primary_region)
            
            # Reconfigure replication to new topology
            await self.coordinator.reconfigure_after_failover(database_type, new_primary_region)
            
            self.logger.info(f"Topology updated after failover: {database_type} -> {new_primary_region}")
    
    async def _periodic_health_check(self) -> None:
        """Periodic health check routine"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                self.last_health_check = datetime.utcnow()
                
                # Perform comprehensive health check
                health_status = await self.health_monitor.comprehensive_health_check()
                
                # Update metrics
                await self.metrics.update_health_metrics(health_status)
                
                # Check for automatic failover conditions
                if self.config.automatic_failover_enabled:
                    await self._check_failover_conditions(health_status)
                
                # Log health status
                self.logger.debug(f"Health check completed: {health_status}")
                
            except Exception as e:
                self.logger.error(f"Error in periodic health check: {e}")
    
    async def _check_failover_conditions(self, health_status: Dict[str, Any]) -> None:
        """Check if automatic failover conditions are met"""
        for db_type, status in health_status.items():
            if status.get("requires_failover", False):
                self.logger.warning(f"Automatic failover triggered for {db_type}")
                await self.failover_database(db_type)
    
    async def get_replication_status(self) -> Dict[str, Any]:
        """
        Get comprehensive replication status.
        
        Returns:
            Dict containing detailed status information
        """



        return {
            "master_status": self.status.value,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
            "active_replications": list(self.active_replications),
            "failed_replications": list(self.failed_replications),
            "topology": {
                "primary_region": self.topology.primary_region if self.topology else None,
                "secondary_regions": self.topology.secondary_regions if self.topology else [],
            },
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "metrics": await self.metrics.get_current_metrics(),
            "health": await self.health_monitor.get_overall_health()
        }
    
    async def enter_maintenance_mode(self, database_type: str, duration: timedelta) -> bool:
        """
        Enter maintenance mode for specified database.
        
        Args:
            database_type: Database to put in maintenance mode
            duration: Expected maintenance duration
            
        Returns:
            bool: True if maintenance mode entered successfully
        """



        try:
            self.logger.info(f"Entering maintenance mode for {database_type} (duration: {duration})")
            self.status = ReplicationStatus.MAINTENANCE
            
            # Schedule maintenance window
            maintenance_window = {
                "database_type": database_type,
                "start_time": datetime.utcnow(),
                "duration": duration,
                "end_time": datetime.utcnow() + duration
            }
            
            self.maintenance_windows.append(maintenance_window)
            
            # Prepare for maintenance
            success = await self.manager.prepare_maintenance(database_type, duration)
            
            if success:
                self.logger.info(f"Maintenance mode activated for {database_type}")
            else:
                self.logger.error(f"Failed to enter maintenance mode for {database_type}")
                self.status = ReplicationStatus.HEALTHY
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error entering maintenance mode for {database_type}: {e}")
            return False
    
    async def exit_maintenance_mode(self, database_type: str) -> bool:
        """
        Exit maintenance mode for specified database.
        
        Args:
            database_type: Database to exit maintenance mode
            
        Returns:
            bool: True if maintenance mode exited successfully
        """



        try:
            self.logger.info(f"Exiting maintenance mode for {database_type}")
            
            # Exit maintenance through manager
            success = await self.manager.exit_maintenance(database_type)
            
            if success:
                # Remove from maintenance windows
                self.maintenance_windows = [
                    w for w in self.maintenance_windows 
                    if w["database_type"] != database_type
                ]
                
                # Update status if no other maintenance windows
                if not self.maintenance_windows:
                    self.status = ReplicationStatus.HEALTHY
                
                self.logger.info(f"Maintenance mode exited for {database_type}")
            else:
                self.logger.error(f"Failed to exit maintenance mode for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error exiting maintenance mode for {database_type}: {e}")
            return False
    
    @asynccontextmanager
    async def maintenance_context(self, database_type: str, duration: timedelta):
        """
        Context manager for maintenance operations.
        
        Args:
            database_type: Database to maintain
            duration: Expected maintenance duration
        """



        try:
            await self.enter_maintenance_mode(database_type, duration)
            yield
        finally:
            await self.exit_maintenance_mode(database_type)
    
    async def shutdown(self, graceful: bool = True) -> None:
        """
        Shutdown replication master and all components.
        
        Args:
            graceful: Whether to perform graceful shutdown
        """



        try:
            self.logger.info(f"Shutting down replication master (graceful={graceful})")
            
            # Stop all active replications
            shutdown_tasks = []
            for db_type in list(self.active_replications):
                shutdown_tasks.append(self.stop_replication(db_type, graceful))
            
            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
            # Shutdown components
            component_shutdown = [
                self.health_monitor.shutdown(),
                self.metrics.shutdown(),
                self.failover_manager.shutdown(),
                self.coordinator.shutdown(),
                self.manager.shutdown()
            ]
            
            await asyncio.gather(*component_shutdown, return_exceptions=True)
            
            self.logger.info("Replication master shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise
