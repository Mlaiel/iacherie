"""Replication Manager - IA Influencer Agent Platform

Comprehensive replication lifecycle management for all database systems.
Handles database-specific replication setup, monitoring, and maintenance
for PostgreSQL, Redis, MongoDB, Elasticsearch, and Vector stores.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from .postgresql import PostgreSQLReplicationHandler
from .redis import RedisReplicationHandler
from .mongodb import MongoDBReplicationHandler
from .elasticsearch import ElasticsearchReplicationHandler
from .vector_stores import VectorStoreReplicationHandler
from .config import ReplicationConfig
from .utils import ReplicationUtils


class ReplicationHandlerType(Enum):
    """
Supported replication handler types"""

    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"


@dataclass
class ReplicationJob:
    """Replication job configuration"""
    database_type: str
    source_config: Dict[str, Any]
    target_config: Dict[str, Any]
    replication_mode: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    last_sync: Optional[datetime] = None
    error_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)


class ReplicationManager:
    """
    Central manager for database replication lifecycle operations.
    
    Coordinates replication setup, monitoring, and maintenance across
    multiple database systems supporting the content creator platform.
    """
    
    def __init__(self, config: ReplicationConfig):
        """
Initialize replication manager with configuration"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReplicationManager")
        self.utils = ReplicationUtils(config)
        
        # Database handlers
        self.handlers: Dict[str, Any] = {}
        self.active_jobs: Dict[str, ReplicationJob] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # State tracking
        self.initialized = False
        self.manager_status = "initializing"
        
        self.logger.info("ReplicationManager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize replication manager and all database handlers.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing replication manager...")
            
            # Initialize database handlers
            await self._initialize_handlers()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            self.initialized = True
            self.manager_status = "ready"
            
            self.logger.info("Replication manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize replication manager: {e}")
            self.manager_status = "failed"
            return False
    
    async def _initialize_handlers(self) -> None:
        """Initialize all database replication handlers"""
        handler_configs = {
            ReplicationHandlerType.POSTGRESQL: PostgreSQLReplicationHandler,
            ReplicationHandlerType.REDIS: RedisReplicationHandler,
            ReplicationHandlerType.MONGODB: MongoDBReplicationHandler,
            ReplicationHandlerType.ELASTICSEARCH: ElasticsearchReplicationHandler,
            ReplicationHandlerType.VECTOR_STORE: VectorStoreReplicationHandler
        }
        
        for handler_type, handler_class in handler_configs.items():
            try:
                handler_config = self.config.get_database_config(handler_type.value)
                if handler_config and handler_config.get("enabled", False):
                    handler = handler_class(handler_config, self.config)
                    await handler.initialize()
                    self.handlers[handler_type.value] = handler
                    self.logger.debug(f"Initialized {handler_type.value} replication handler")
                else:
                    self.logger.debug(f"Skipping {handler_type.value} handler (disabled)")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize {handler_type.value} handler: {e}")
                # Continue with other handlers
    
    async def _setup_monitoring(self) -> None:
        """Setup replication monitoring"""
        self.logger.info("Setting up replication monitoring...")
        
        # Start periodic monitoring task
        asyncio.create_task(self._periodic_monitoring())
        
        self.logger.info("Replication monitoring setup completed")
    
    async def start_replication(
        self, 
        database_type: str, 
        config: Dict[str, Any], 
        mode: str = "master_slave"
    ) -> bool:
        """
        Start replication for specified database type.
        
        Args:
            database_type: Type of database to replicate
            config: Database-specific configuration
            mode: Replication mode
            
        Returns:
            bool: True if replication started successfully
        """
        try:
            if not self.initialized:
                self.logger.error("Replication manager not initialized")
                return False
            
            self.logger.info(f"Starting replication for {database_type} in {mode} mode")
            
            # Get appropriate handler
            handler = self.handlers.get(database_type)
            if not handler:
                self.logger.error(f"No handler available for {database_type}")
                return False
            
            # Create replication job
            job = ReplicationJob(
                database_type=database_type,
                source_config=config.get("source", {}),
                target_config=config.get("target", {}),
                replication_mode=mode
            )
            
            # Start replication through handler
            success = await handler.start_replication(
                source_config=job.source_config,
                target_config=job.target_config,
                mode=mode
            )
            
            if success:
                job.status = "active"
                job.last_sync = datetime.utcnow()
                self.active_jobs[database_type] = job
                
                self.logger.info(f"Replication started successfully for {database_type}")
                
                # Start job monitoring
                asyncio.create_task(self._monitor_job(database_type))
            else:
                job.status = "failed"
                self.logger.error(f"Failed to start replication for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting replication for {database_type}: {e}")
            return False
    
    async def stop_replication(self, database_type: str, graceful: bool = True) -> bool:
        """
        Stop replication for specified database type.
        
        Args:
            database_type: Database type to stop replication
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if replication stopped successfully
        """
        try:
            self.logger.info(f"Stopping replication for {database_type} (graceful={graceful})")
            
            # Get handler and job
            handler = self.handlers.get(database_type)
            job = self.active_jobs.get(database_type)
            
            if not handler:
                self.logger.warning(f"No handler found for {database_type}")
                return True  # Consider success if no handler
            
            if not job:
                self.logger.warning(f"No active job found for {database_type}")
                return True  # Consider success if no job
            
            # Stop replication through handler
            success = await handler.stop_replication(graceful)
            
            if success:
                job.status = "stopped"
                self.active_jobs.pop(database_type, None)
                self.logger.info(f"Replication stopped successfully for {database_type}")
            else:
                job.status = "stop_failed"
                self.logger.error(f"Failed to stop replication for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error stopping replication for {database_type}: {e}")
            return False
    
    async def pause_replication(self, database_type: str) -> bool:
        """
        Pause replication for specified database type.
        
        Args:
            database_type: Database type to pause
            
        Returns:
            bool: True if replication paused successfully
        """
        try:
            self.logger.info(f"Pausing replication for {database_type}")
            
            handler = self.handlers.get(database_type)
            job = self.active_jobs.get(database_type)
            
            if not handler or not job:
                self.logger.error(f"Handler or job not found for {database_type}")
                return False
            
            # Pause replication through handler
            success = await handler.pause_replication()
            
            if success:
                job.status = "paused"
                self.logger.info(f"Replication paused successfully for {database_type}")
            else:
                self.logger.error(f"Failed to pause replication for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error pausing replication for {database_type}: {e}")
            return False
    
    async def resume_replication(self, database_type: str) -> bool:
        """
        Resume paused replication for specified database type.
        
        Args:
            database_type: Database type to resume
            
        Returns:
            bool: True if replication resumed successfully
        """
        try:
            self.logger.info(f"Resuming replication for {database_type}")
            
            handler = self.handlers.get(database_type)
            job = self.active_jobs.get(database_type)
            
            if not handler or not job:
                self.logger.error(f"Handler or job not found for {database_type}")
                return False
            
            # Resume replication through handler
            success = await handler.resume_replication()
            
            if success:
                job.status = "active"
                job.last_sync = datetime.utcnow()
                self.logger.info(f"Replication resumed successfully for {database_type}")
            else:
                self.logger.error(f"Failed to resume replication for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error resuming replication for {database_type}: {e}")
            return False
    
    async def sync_replication(self, database_type: str, force: bool = False) -> bool:
        """
        Trigger manual synchronization for specified database type.
        
        Args:
            database_type: Database type to synchronize
            force: Whether to force synchronization
            
        Returns:
            bool: True if synchronization successful
        """
        try:
            self.logger.info(f"Triggering manual sync for {database_type} (force={force})")
            
            handler = self.handlers.get(database_type)
            job = self.active_jobs.get(database_type)
            
            if not handler:
                self.logger.error(f"No handler found for {database_type}")
                return False
            
            # Trigger synchronization through handler
            success = await handler.trigger_sync(force)
            
            if success and job:
                job.last_sync = datetime.utcnow()
                job.metrics["manual_syncs"] = job.metrics.get("manual_syncs", 0) + 1
                self.logger.info(f"Manual sync completed for {database_type}")
            else:
                self.logger.error(f"Manual sync failed for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during manual sync for {database_type}: {e}")
            return False
    
    async def prepare_maintenance(self, database_type: str, duration: timedelta) -> bool:
        """
        Prepare database for maintenance mode.
        
        Args:
            database_type: Database to prepare for maintenance
            duration: Expected maintenance duration
            
        Returns:
            bool: True if preparation successful
        """
        try:
            self.logger.info(f"Preparing {database_type} for maintenance (duration: {duration})")
            
            handler = self.handlers.get(database_type)
            if not handler:
                self.logger.error(f"No handler found for {database_type}")
                return False
            
            # Prepare for maintenance through handler
            success = await handler.prepare_maintenance(duration)
            
            if success:
                job = self.active_jobs.get(database_type)
                if job:
                    job.status = "maintenance_prep"
                self.logger.info(f"Maintenance preparation completed for {database_type}")
            else:
                self.logger.error(f"Maintenance preparation failed for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error preparing maintenance for {database_type}: {e}")
            return False
    
    async def exit_maintenance(self, database_type: str) -> bool:
        """
        Exit maintenance mode for database.
        
        Args:
            database_type: Database to exit maintenance
            
        Returns:
            bool: True if exit successful
        """
        try:
            self.logger.info(f"Exiting maintenance mode for {database_type}")
            
            handler = self.handlers.get(database_type)
            if not handler:
                self.logger.error(f"No handler found for {database_type}")
                return False
            
            # Exit maintenance through handler
            success = await handler.exit_maintenance()
            
            if success:
                job = self.active_jobs.get(database_type)
                if job:
                    job.status = "active"
                    job.last_sync = datetime.utcnow()
                self.logger.info(f"Maintenance mode exited for {database_type}")
            else:
                self.logger.error(f"Failed to exit maintenance mode for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error exiting maintenance for {database_type}: {e}")
            return False
    
    async def _monitor_job(self, database_type: str) -> None:
        """Monitor specific replication job"""
        while database_type in self.active_jobs:
            try:
                job = self.active_jobs[database_type]
                handler = self.handlers.get(database_type)
                
                if not handler or job.status not in ["active", "paused"]:
                    break
                
                # Get replication metrics from handler
                metrics = await handler.get_replication_metrics()
                
                # Update job metrics
                job.metrics.update(metrics)
                
                # Check for issues
                if metrics.get("lag_seconds", 0) > self.config.lag_threshold:
                    self.logger.warning(f"High replication lag for {database_type}: "
                                      f"{metrics['lag_seconds']}s")
                    job.error_count += 1
                
                if metrics.get("errors", 0) > 0:
                    self.logger.warning(f"Replication errors for {database_type}: "
                                      f"{metrics['errors']}")
                    job.error_count += 1
                
                # Sleep before next check
                await asyncio.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoring job {database_type}: {e}")
                await asyncio.sleep(30)  # Longer delay on error
    
    async def _periodic_monitoring(self) -> None:
        """Periodic monitoring of all replication jobs"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                # Check all active jobs
                for database_type, job in list(self.active_jobs.items()):
                    handler = self.handlers.get(database_type)
                    
                    if not handler:
                        continue
                    
                    # Check handler health
                    health = await handler.check_health()
                    
                    if not health.get("healthy", False):
                        self.logger.warning(f"Health check failed for {database_type}: "
                                          f"{health}")
                        job.error_count += 1
                    
                    # Auto-recovery for failed jobs
                    if job.error_count > self.config.max_error_count:
                        self.logger.warning(f"Auto-recovery triggered for {database_type}")
                        await self._attempt_recovery(database_type)
                
            except Exception as e:
                self.logger.error(f"Error in periodic monitoring: {e}")
    
    async def _attempt_recovery(self, database_type: str) -> bool:
        """Attempt automatic recovery for failed replication"""
        try:
            self.logger.info(f"Attempting recovery for {database_type}")
            
            job = self.active_jobs.get(database_type)
            if not job:
                return False
            
            # Stop current replication
            await self.stop_replication(database_type, graceful=False)
            
            # Wait before restart
            await asyncio.sleep(5)
            
            # Restart replication
            config = {
                "source": job.source_config,
                "target": job.target_config
            }
            
            success = await self.start_replication(
                database_type, 
                config, 
                job.replication_mode
            )
            
            if success:
                self.logger.info(f"Recovery successful for {database_type}")
                # Reset error count
                if database_type in self.active_jobs:
                    self.active_jobs[database_type].error_count = 0
            else:
                self.logger.error(f"Recovery failed for {database_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during recovery for {database_type}: {e}")
            return False
    
    async def get_replication_status(self) -> Dict[str, Any]:
        """
        Get comprehensive replication status for all jobs.
        
        Returns:
            Dict containing status information for all replication jobs
        """
        status = {
            "manager_status": self.manager_status,
            "initialized": self.initialized,
            "total_jobs": len(self.active_jobs),
            "handlers": list(self.handlers.keys()),
            "jobs": {}
        }
        
        for database_type, job in self.active_jobs.items():
            handler = self.handlers.get(database_type)
            
            job_status = {
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "last_sync": job.last_sync.isoformat() if job.last_sync else None,
                "error_count": job.error_count,
                "replication_mode": job.replication_mode,
                "metrics": job.metrics
            }
            
            # Add handler-specific status
            if handler:
                try:
                    handler_status = await handler.get_status()
                    job_status["handler_status"] = handler_status
                except Exception as e:
                    job_status["handler_error"] = str(e)
            
            status["jobs"][database_type] = job_status
        
        return status
    
    async def shutdown(self) -> None:
        """Shutdown replication manager and all handlers"""
        try:
            self.logger.info("Shutting down replication manager...")
            
            # Stop all active jobs
            stop_tasks = []
            for database_type in list(self.active_jobs.keys()):
                stop_tasks.append(self.stop_replication(database_type, graceful=True))
            
            if stop_tasks:
                await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            # Shutdown handlers
            for handler in self.handlers.values():
                try:
                    await handler.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down handler: {e}")
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.manager_status = "shutdown"
            self.logger.info("Replication manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during manager shutdown: {e}")
            raise
