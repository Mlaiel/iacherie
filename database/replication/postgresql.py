"""PostgreSQL Replication Handler - IA Influencer Agent Platform

Advanced PostgreSQL streaming and logical replication management for content creator data.
Supports master-slave, master-master, and cluster replication modes with automated
failover, conflict resolution, and performance optimization.

Handles:
- User profiles and content metadata replication
- Revenue tracking data synchronization
- AI fingerprint data replication
- Real-time analytics data streaming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import asyncpg
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class PostgreSQLReplicationMode(Enum):
    """PostgreSQL replication modes"""    STREAMING = "streaming"
    LOGICAL = "logical"
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"


class ReplicationSlotStatus(Enum):
    """Replication slot status"""    ACTIVE = "active"
    INACTIVE = "inactive"
    TEMPORARY = "temporary"
    DROPPED = "dropped"


@dataclass
class ReplicationSlot:
    """PostgreSQL replication slot configuration"""    slot_name: str
    plugin: str = "pgoutput"
    slot_type: str = "logical"
    database: str = "postgres"
    active: bool = False
    restart_lsn: Optional[str] = None
    confirmed_flush_lsn: Optional[str] = None


@dataclass
class PostgreSQLReplicationMetrics:
    """PostgreSQL replication metrics"""    lag_bytes: int = 0
    lag_seconds: float = 0.0
    sent_lsn: Optional[str] = None
    write_lsn: Optional[str] = None
    flush_lsn: Optional[str] = None
    replay_lsn: Optional[str] = None
    sync_state: str = "unknown"
    pid: Optional[int] = None
    usename: Optional[str] = None
    application_name: Optional[str] = None
    client_addr: Optional[str] = None
    backend_start: Optional[datetime] = None


class PostgreSQLReplicationHandler:
    """    Advanced PostgreSQL replication handler for the IA Influencer Agent platform.
    
    Manages streaming and logical replication for content creator data,
    AI fingerprints, revenue tracking, and analytics with high availability
    and disaster recovery capabilities.
    """    
    def __init__(self, config: Dict[str, Any], global_config: Any):
        """Initialize PostgreSQL replication handler"""        self.config = config
        self.global_config = global_config
        self.logger = logging.getLogger(f"{__name__}.PostgreSQLReplicationHandler")
        
        # Connection configuration
        self.master_config = config.get("master", {})
        self.slave_configs = config.get("slaves", [])
        self.replication_config = config.get("replication", {})
        
        # Connection pools
        self.master_pool: Optional[asyncpg.Pool] = None
        self.slave_pools: Dict[str, asyncpg.Pool] = {}
        self.replication_connections: Dict[str, asyncpg.Connection] = {}
        
        # Replication state
        self.replication_slots: Dict[str, ReplicationSlot] = {}
        self.publications: List[str] = []
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring
        self.is_monitoring = False
        self.last_metrics: Dict[str, PostgreSQLReplicationMetrics] = {}
        
        self.logger.info("PostgreSQL replication handler initialized")
    
    async def initialize(self) -> bool:
        """        Initialize PostgreSQL replication infrastructure.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info("Initializing PostgreSQL replication handler...")
            
            # Initialize connection pools
            await self._initialize_connection_pools()
            
            # Setup replication infrastructure
            await self._setup_replication_infrastructure()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.logger.info("PostgreSQL replication handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL replication handler: {e}")
            return False
    
    async def _initialize_connection_pools(self) -> None:
        """Initialize connection pools for master and slaves"""        # Master connection pool
        if self.master_config:
            self.master_pool = await asyncpg.create_pool(
                host=self.master_config["host"],
                port=self.master_config["port"],
                database=self.master_config["database"],
                user=self.master_config["username"],
                password=self.master_config["password"],
                ssl=self.master_config.get("ssl_enabled", True),
                min_size=5,
                max_size=self.master_config.get("pool_size", 20),
                command_timeout=self.master_config.get("timeout", 30)
            )
            self.logger.debug("Master connection pool initialized")
        
        # Slave connection pools
        for i, slave_config in enumerate(self.slave_configs):
            slave_name = slave_config.get("name", f"slave_{i}")
            pool = await asyncpg.create_pool(
                host=slave_config["host"],
                port=slave_config["port"],
                database=slave_config["database"],
                user=slave_config["username"],
                password=slave_config["password"],
                ssl=slave_config.get("ssl_enabled", True),
                min_size=3,
                max_size=slave_config.get("pool_size", 10),
                command_timeout=slave_config.get("timeout", 30)
            )
            self.slave_pools[slave_name] = pool
            self.logger.debug(f"Slave connection pool initialized: {slave_name}")
    
    async def _setup_replication_infrastructure(self) -> None:
        """Setup PostgreSQL replication infrastructure"""        replication_mode = self.replication_config.get("mode", "streaming")
        
        if replication_mode == "streaming":
            await self._setup_streaming_replication()
        elif replication_mode == "logical":
            await self._setup_logical_replication()
        else:
            raise ValueError(f"Unsupported replication mode: {replication_mode}")
    
    async def _setup_streaming_replication(self) -> None:
        """Setup PostgreSQL streaming replication"""        self.logger.info("Setting up streaming replication...")
        
        if not self.master_pool:
            raise ValueError("Master connection pool not initialized")
        
        async with self.master_pool.acquire() as conn:
            # Create replication user if not exists
            await self._create_replication_user(conn)
            
            # Configure streaming replication settings
            await self._configure_streaming_replication(conn)
            
            # Create replication slots for each slave
            for slave_name in self.slave_pools.keys():
                slot_name = f"slot_{slave_name}"
                await self._create_replication_slot(conn, slot_name, "physical")
        
        self.logger.info("Streaming replication setup completed")
    
    async def _setup_logical_replication(self) -> None:
        """Setup PostgreSQL logical replication"""        self.logger.info("Setting up logical replication...")
        
        if not self.master_pool:
            raise ValueError("Master connection pool not initialized")
        
        async with self.master_pool.acquire() as conn:
            # Create replication user if not exists
            await self._create_replication_user(conn)
            
            # Create logical replication slots
            for slave_name in self.slave_pools.keys():
                slot_name = f"logical_slot_{slave_name}"
                await self._create_replication_slot(conn, slot_name, "logical", "pgoutput")
            
            # Create publications for content creator tables
            await self._create_publications(conn)
        
        # Create subscriptions on slaves
        await self._create_subscriptions()
        
        self.logger.info("Logical replication setup completed")
    
    async def _create_replication_user(self, conn: asyncpg.Connection) -> None:
        """Create replication user with appropriate privileges"""        replication_user = self.replication_config.get("user", "replication_user")
        replication_password = self.replication_config.get("password", "secure_password")
        
        try:
            # Create user if not exists
            await conn.execute(f"""                DO $$
                BEGIN
                   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{replication_user}') THEN
                      CREATE ROLE {replication_user} WITH REPLICATION LOGIN PASSWORD '{replication_password}';
                   END IF;
                END
                $$;
            """)
            
            # Grant necessary privileges
            await conn.execute(f"GRANT USAGE ON SCHEMA public TO {replication_user}")
            await conn.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {replication_user}")
            await conn.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {replication_user}")
            
            self.logger.debug(f"Replication user '{replication_user}' created/updated")
            
        except Exception as e:
            self.logger.error(f"Failed to create replication user: {e}")
            raise
    
    async def _create_replication_slot(
        self, 
        conn: asyncpg.Connection, 
        slot_name: str, 
        slot_type: str,
        plugin: str = None
    ) -> None:
        """Create replication slot"""        try:
            # Check if slot already exists
            result = await conn.fetchval(
                "SELECT slot_name FROM pg_replication_slots WHERE slot_name = $1",
                slot_name
            )
            
            if result:
                self.logger.debug(f"Replication slot '{slot_name}' already exists")
                return
            
            # Create slot based on type
            if slot_type == "physical":
                await conn.execute(f"SELECT pg_create_physical_replication_slot('{slot_name}')")
            elif slot_type == "logical":
                plugin = plugin or "pgoutput"
                await conn.execute(f"SELECT pg_create_logical_replication_slot('{slot_name}', '{plugin}')")
            
            # Store slot configuration
            self.replication_slots[slot_name] = ReplicationSlot(
                slot_name=slot_name,
                plugin=plugin or "",
                slot_type=slot_type,
                active=False
            )
            
            self.logger.info(f"Replication slot '{slot_name}' created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create replication slot '{slot_name}': {e}")
            raise
    
    async def _configure_streaming_replication(self, conn: asyncpg.Connection) -> None:
        """Configure streaming replication settings"""        settings = {
            "wal_level": "replica",
            "max_wal_senders": max(10, len(self.slave_pools) + 2),
            "max_replication_slots": max(10, len(self.slave_pools) + 2),
            "synchronous_commit": self.replication_config.get("synchronous_commit", "off"),
            "hot_standby": "on",
            "archive_mode": "on",
            "archive_command": "test ! -f /var/lib/postgresql/archive/%f && cp %p /var/lib/postgresql/archive/%f"
        }
        
        for setting, value in settings.items():
            try:
                current_value = await conn.fetchval(f"SHOW {setting}")
                if str(current_value) != str(value):
                    self.logger.warning(f"PostgreSQL setting '{setting}' should be '{value}' but is '{current_value}'")
            except Exception as e:
                self.logger.debug(f"Could not check setting '{setting}': {e}")
    
    async def _create_publications(self, conn: asyncpg.Connection) -> None:
        """Create publications for logical replication"""        # Define table groups for content creator platform
        table_groups = {
            "users_publication": [
                "users", "user_profiles", "user_settings", "user_subscriptions"
            ],
            "content_publication": [
                "content_fingerprints", "content_metadata", "content_tags",
                "content_protection_alerts", "content_violations"
            ],
            "monetization_publication": [
                "revenue_tracking", "payment_transactions", "licensing_agreements",
                "royalty_distributions", "platform_earnings"
            ],
            "analytics_publication": [
                "user_analytics", "content_analytics", "performance_metrics",
                "engagement_data", "recommendation_logs"
            ]
        }
        
        for publication_name, tables in table_groups.items():
            try:
                # Check if publication exists
                exists = await conn.fetchval(
                    "SELECT pubname FROM pg_publication WHERE pubname = $1",
                    publication_name
                )
                
                if not exists:
                    # Create publication
                    table_list = ", ".join(tables)
                    await conn.execute(f"CREATE PUBLICATION {publication_name} FOR TABLE {table_list}")
                    self.publications.append(publication_name)
                    self.logger.info(f"Publication '{publication_name}' created")
                else:
                    self.publications.append(publication_name)
                    self.logger.debug(f"Publication '{publication_name}' already exists")
                    
            except Exception as e:
                self.logger.error(f"Failed to create publication '{publication_name}': {e}")
    
    async def _create_subscriptions(self) -> None:
        """Create subscriptions on slave databases"""        for slave_name, slave_pool in self.slave_pools.items():
            async with slave_pool.acquire() as conn:
                for publication in self.publications:
                    subscription_name = f"{publication}_{slave_name}"
                    
                    try:
                        # Check if subscription exists
                        exists = await conn.fetchval(
                            "SELECT subname FROM pg_subscription WHERE subname = $1",
                            subscription_name
                        )
                        
                        if not exists:
                            # Build connection string for master
                            master_conn_str = (
                                f"host={self.master_config['host']} "
                                f"port={self.master_config['port']} "
                                f"dbname={self.master_config['database']} "
                                f"user={self.replication_config.get('user', 'replication_user')} "
                                f"password={self.replication_config.get('password', 'secure_password')}"
                            )
                            
                            # Create subscription
                            await conn.execute(f"""                                CREATE SUBSCRIPTION {subscription_name} 
                                CONNECTION '{master_conn_str}' 
                                PUBLICATION {publication}
                            """)
                            
                            self.subscriptions[subscription_name] = {
                                "slave_name": slave_name,
                                "publication": publication,
                                "created_at": datetime.utcnow()
                            }
                            
                            self.logger.info(f"Subscription '{subscription_name}' created")
                        else:
                            self.subscriptions[subscription_name] = {
                                "slave_name": slave_name,
                                "publication": publication,
                                "created_at": datetime.utcnow()
                            }
                            self.logger.debug(f"Subscription '{subscription_name}' already exists")
                            
                    except Exception as e:
                        self.logger.error(f"Failed to create subscription '{subscription_name}': {e}")
    
    async def _start_monitoring(self) -> None:
        """Start replication monitoring"""        self.is_monitoring = True
        asyncio.create_task(self._monitoring_loop())
        self.logger.info("PostgreSQL replication monitoring started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                await self._collect_replication_metrics()
                await asyncio.sleep(self.global_config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Longer delay on error
    
    async def _collect_replication_metrics(self) -> None:
        """Collect replication metrics from master and slaves"""        if not self.master_pool:
            return
        
        async with self.master_pool.acquire() as conn:
            # Get replication stats from master
            try:
                replication_stats = await conn.fetch("""                    SELECT 
                        pid,
                        usename,
                        application_name,
                        client_addr,
                        backend_start,
                        state,
                        sent_lsn,
                        write_lsn,
                        flush_lsn,
                        replay_lsn,
                        write_lag,
                        flush_lag,
                        replay_lag,
                        sync_state
                    FROM pg_stat_replication
                """)
                
                for stat in replication_stats:
                    app_name = stat["application_name"] or "unknown"
                    
                    # Calculate lag in seconds
                    lag_seconds = 0.0
                    if stat["replay_lag"]:
                        lag_seconds = stat["replay_lag"].total_seconds()
                    
                    metrics = PostgreSQLReplicationMetrics(
                        lag_seconds=lag_seconds,
                        sent_lsn=stat["sent_lsn"],
                        write_lsn=stat["write_lsn"],
                        flush_lsn=stat["flush_lsn"],
                        replay_lsn=stat["replay_lsn"],
                        sync_state=stat["sync_state"],
                        pid=stat["pid"],
                        usename=stat["usename"],
                        application_name=app_name,
                        client_addr=str(stat["client_addr"]) if stat["client_addr"] else None,
                        backend_start=stat["backend_start"]
                    )
                    
                    self.last_metrics[app_name] = metrics
                
                # Log warnings for high lag
                for app_name, metrics in self.last_metrics.items():
                    if metrics.lag_seconds > self.global_config.lag_threshold / 1000:
                        self.logger.warning(f"High replication lag for {app_name}: {metrics.lag_seconds}s")
                
            except Exception as e:
                self.logger.error(f"Failed to collect replication metrics: {e}")
    
    async def start_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any], 
        mode: str
    ) -> bool:
        """        Start PostgreSQL replication.
        
        Args:
            source_config: Source database configuration
            target_config: Target database configuration  
            mode: Replication mode
            
        Returns:
            bool: True if replication started successfully
        """        try:
            self.logger.info(f"Starting PostgreSQL replication in {mode} mode")
            
            # Update configurations
            self.master_config.update(source_config)
            if target_config not in self.slave_configs:
                self.slave_configs.append(target_config)
            
            # Reinitialize if needed
            if not self.master_pool:
                await self._initialize_connection_pools()
                await self._setup_replication_infrastructure()
            
            self.logger.info("PostgreSQL replication started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start PostgreSQL replication: {e}")
            return False
    
    async def stop_replication(self, graceful: bool = True) -> bool:
        """        Stop PostgreSQL replication.
        
        Args:
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if replication stopped successfully
        """        try:
            self.logger.info(f"Stopping PostgreSQL replication (graceful={graceful})")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if graceful:
                # Drop subscriptions
                for subscription_name, sub_info in self.subscriptions.items():
                    slave_name = sub_info["slave_name"]
                    if slave_name in self.slave_pools:
                        async with self.slave_pools[slave_name].acquire() as conn:
                            try:
                                await conn.execute(f"DROP SUBSCRIPTION IF EXISTS {subscription_name}")
                                self.logger.debug(f"Subscription '{subscription_name}' dropped")
                            except Exception as e:
                                self.logger.error(f"Failed to drop subscription '{subscription_name}': {e}")
                
                # Drop replication slots
                if self.master_pool:
                    async with self.master_pool.acquire() as conn:
                        for slot_name in self.replication_slots:
                            try:
                                await conn.execute(f"SELECT pg_drop_replication_slot('{slot_name}')")
                                self.logger.debug(f"Replication slot '{slot_name}' dropped")
                            except Exception as e:
                                self.logger.error(f"Failed to drop replication slot '{slot_name}': {e}")
            
            # Close connection pools
            if self.master_pool:
                await self.master_pool.close()
                self.master_pool = None
            
            for slave_name, pool in self.slave_pools.items():
                await pool.close()
            self.slave_pools.clear()
            
            # Clear state
            self.replication_slots.clear()
            self.subscriptions.clear()
            self.publications.clear()
            
            self.logger.info("PostgreSQL replication stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop PostgreSQL replication: {e}")
            return False
    
    async def pause_replication(self) -> bool:
        """Pause PostgreSQL replication"""        try:
            self.logger.info("Pausing PostgreSQL replication")
            
            # Disable subscriptions
            for subscription_name, sub_info in self.subscriptions.items():
                slave_name = sub_info["slave_name"]
                if slave_name in self.slave_pools:
                    async with self.slave_pools[slave_name].acquire() as conn:
                        await conn.execute(f"ALTER SUBSCRIPTION {subscription_name} DISABLE")
            
            self.logger.info("PostgreSQL replication paused")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause PostgreSQL replication: {e}")
            return False
    
    async def resume_replication(self) -> bool:
        """Resume paused PostgreSQL replication"""        try:
            self.logger.info("Resuming PostgreSQL replication")
            
            # Enable subscriptions
            for subscription_name, sub_info in self.subscriptions.items():
                slave_name = sub_info["slave_name"]
                if slave_name in self.slave_pools:
                    async with self.slave_pools[slave_name].acquire() as conn:
                        await conn.execute(f"ALTER SUBSCRIPTION {subscription_name} ENABLE")
            
            self.logger.info("PostgreSQL replication resumed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume PostgreSQL replication: {e}")
            return False
    
    async def trigger_sync(self, force: bool = False) -> bool:
        """Trigger manual synchronization"""        try:
            self.logger.info(f"Triggering PostgreSQL sync (force={force})")
            
            if not self.master_pool:
                return False
            
            # Force WAL switch to ensure latest changes are available
            async with self.master_pool.acquire() as conn:
                await conn.execute("SELECT pg_switch_wal()")
            
            # Refresh subscriptions
            for subscription_name, sub_info in self.subscriptions.items():
                slave_name = sub_info["slave_name"]
                if slave_name in self.slave_pools:
                    async with self.slave_pools[slave_name].acquire() as conn:
                        await conn.execute(f"ALTER SUBSCRIPTION {subscription_name} REFRESH PUBLICATION")
            
            self.logger.info("PostgreSQL sync triggered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger PostgreSQL sync: {e}")
            return False
    
    async def prepare_maintenance(self, duration: timedelta) -> bool:
        """Prepare for maintenance mode"""        try:
            self.logger.info(f"Preparing PostgreSQL for maintenance (duration: {duration})")
            
            # Pause replication to avoid conflicts during maintenance
            await self.pause_replication()
            
            # Create backup before maintenance
            if self.master_pool:
                async with self.master_pool.acquire() as conn:
                    await conn.execute("SELECT pg_start_backup('maintenance_backup')")
            
            self.logger.info("PostgreSQL maintenance preparation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare PostgreSQL for maintenance: {e}")
            return False
    
    async def exit_maintenance(self) -> bool:
        """Exit maintenance mode"""        try:
            self.logger.info("Exiting PostgreSQL maintenance mode")
            
            # Stop backup if running
            if self.master_pool:
                async with self.master_pool.acquire() as conn:
                    try:
                        await conn.execute("SELECT pg_stop_backup()")
                    except Exception:
                        pass  # Backup might not be running
            
            # Resume replication
            await self.resume_replication()
            
            self.logger.info("PostgreSQL maintenance mode exited")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to exit PostgreSQL maintenance mode: {e}")
            return False
    
    async def check_health(self) -> Dict[str, Any]:
        """Check PostgreSQL replication health"""        health = {
            "healthy": True,
            "issues": [],
            "metrics": {},
            "connections": {}
        }
        
        try:
            # Check master connection
            if self.master_pool:
                async with self.master_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                    health["connections"]["master"] = "healthy"
            else:
                health["healthy"] = False
                health["issues"].append("Master connection pool not available")
            
            # Check slave connections
            for slave_name, pool in self.slave_pools.items():
                try:
                    async with pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                        health["connections"][slave_name] = "healthy"
                except Exception as e:
                    health["healthy"] = False
                    health["issues"].append(f"Slave {slave_name} connection failed: {e}")
                    health["connections"][slave_name] = "failed"
            
            # Check replication lag
            for app_name, metrics in self.last_metrics.items():
                if metrics.lag_seconds > self.global_config.lag_threshold / 1000:
                    health["healthy"] = False
                    health["issues"].append(f"High lag for {app_name}: {metrics.lag_seconds}s")
            
            health["metrics"] = {
                name: {
                    "lag_seconds": metrics.lag_seconds,
                    "sync_state": metrics.sync_state
                }
                for name, metrics in self.last_metrics.items()
            }
            
        except Exception as e:
            health["healthy"] = False
            health["issues"].append(f"Health check failed: {e}")
        
        return health
    
    async def get_replication_metrics(self) -> Dict[str, Any]:
        """Get current replication metrics"""        metrics = {
            "total_slaves": len(self.slave_pools),
            "active_slots": len([s for s in self.replication_slots.values() if s.active]),
            "publications": len(self.publications),
            "subscriptions": len(self.subscriptions),
            "lag_metrics": {},
            "errors": 0
        }
        
        # Add detailed lag metrics
        for app_name, repl_metrics in self.last_metrics.items():
            metrics["lag_metrics"][app_name] = {
                "lag_seconds": repl_metrics.lag_seconds,
                "sync_state": repl_metrics.sync_state,
                "client_addr": repl_metrics.client_addr
            }
        
        return metrics
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""        return {
            "handler_type": "postgresql",
            "initialized": self.master_pool is not None,
            "monitoring": self.is_monitoring,
            "replication_mode": self.replication_config.get("mode", "streaming"),
            "master_configured": bool(self.master_config),
            "slaves_count": len(self.slave_pools),
            "replication_slots": len(self.replication_slots),
            "publications": self.publications,
            "subscriptions": list(self.subscriptions.keys()),
            "last_metrics_count": len(self.last_metrics)
        }
    
    async def shutdown(self) -> None:
        """Shutdown PostgreSQL replication handler"""        try:
            self.logger.info("Shutting down PostgreSQL replication handler")
            await self.stop_replication(graceful=True)
            self.logger.info("PostgreSQL replication handler shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during PostgreSQL handler shutdown: {e}")
            raise
