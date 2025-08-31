"""MongoDB Replication Handler - IA Influencer Agent Platform

Comprehensive MongoDB replication management with replica sets, sharding,
and cross-cluster replication for content creator platform data.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure, ConfigurationError
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import gridfs
from .config import ReplicationConfig


class MongoDBReplicationHandler:
    """
    MongoDB replication handler for comprehensive replica set and sharding management.
    
    Provides robust MongoDB replication capabilities including:
    - Replica set configuration and management
    - Sharded cluster replication
    - Cross-cluster synchronization
    - Oplog tailing and processing
    - Conflict resolution
    - Performance monitoring
    """
    
    def __init__(self, config: Dict[str, Any], replication_config: ReplicationConfig):
        """
        Initialize MongoDB replication handler.
        
        Args:
            config: MongoDB-specific configuration
            replication_config: Global replication configuration
        """
        self.config = config
        self.replication_config = replication_config
        self.logger = logging.getLogger(f"{__name__}.MongoDBReplicationHandler")
        
        # Connection management
        self.primary_client: Optional[AsyncIOMotorClient] = None
        self.secondary_clients: Dict[str, AsyncIOMotorClient] = {}
        self.sync_client: Optional[MongoClient] = None  # For sync operations
        
        # Replication state
        self.replica_set_name = config.get("replica_set_name", "rs0")
        self.shard_key = config.get("shard_key", "_id")
        self.read_preference = config.get("read_preference", "secondaryPreferred")
        self.write_concern = config.get("write_concern", "majority")
        
        # Monitoring
        self.is_monitoring = False
        self.last_oplog_timestamp: Optional[datetime] = None
        self.replication_lag = 0
        self.oplog_processor_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.metrics = {
            "operations_replicated": 0,
            "bytes_transferred": 0,
            "replication_lag_ms": 0,
            "last_sync_time": None,
            "error_count": 0,
            "conflicts_resolved": 0
        }
        
        self.logger.info("MongoDBReplicationHandler initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize MongoDB replication connections and configuration.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing MongoDB replication handler...")
            
            # Initialize primary connection
            await self._initialize_primary_connection()
            
            # Initialize secondary connections
            await self._initialize_secondary_connections()
            
            # Verify replica set configuration
            await self._verify_replica_set_config()
            
            # Setup initial monitoring
            await self._setup_monitoring()
            
            self.logger.info("MongoDB replication handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MongoDB replication handler: {e}")
            return False
    
    async def _initialize_primary_connection(self) -> None:
        """Initialize connection to primary MongoDB instance"""
        try:
            connection_string = self._build_connection_string(self.config)
            
            self.primary_client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=self.config.get("pool_size", 50),
                minPoolSize=10,
                serverSelectionTimeoutMS=self.config.get("timeout", 30000),
                connectTimeoutMS=self.config.get("timeout", 30000),
                readPreference=self.read_preference,
                w=self.write_concern,
                replicaSet=self.replica_set_name
            )
            
            # Test connection
            await self.primary_client.admin.command("ping")
            
            # Create sync client for operations that require synchronous access
            self.sync_client = MongoClient(
                connection_string,
                maxPoolSize=10,
                replicaSet=self.replica_set_name
            )
            
            self.logger.info("Primary MongoDB connection established")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize primary MongoDB connection: {e}")
            raise
    
    async def _initialize_secondary_connections(self) -> None:
        """Initialize connections to secondary MongoDB instances"""
        secondary_configs = self.config.get("secondaries", [])
        
        for idx, secondary_config in enumerate(secondary_configs):
            try:
                connection_string = self._build_connection_string(secondary_config)
                
                client = AsyncIOMotorClient(
                    connection_string,
                    maxPoolSize=20,
                    readPreference="secondary",
                    serverSelectionTimeoutMS=30000
                )
                
                # Test connection
                await client.admin.command("ping")
                
                secondary_name = f"secondary_{idx}"
                self.secondary_clients[secondary_name] = client
                
                self.logger.info(f"Secondary MongoDB connection established: {secondary_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to connect to secondary {idx}: {e}")
    
    def _build_connection_string(self, config: Dict[str, Any]) -> str:
        """Build MongoDB connection string from configuration"""
        host = config.get("host", "localhost")
        port = config.get("port", 27017)
        username = config.get("username")
        password = config.get("password")
        database = config.get("database", "admin")
        
        if username and password:
            auth_string = f"{username}:{password}@"
        else:
            auth_string = ""
        
        # Additional connection parameters
        params = []
        if config.get("ssl_enabled", False):
            params.append("ssl=true")
        if config.get("auth_source"):
            params.append(f"authSource={config['auth_source']}")
        
        param_string = "&".join(params)
        if param_string:
            param_string = "?" + param_string
        
        return f"mongodb://{auth_string}{host}:{port}/{database}{param_string}"
    
    async def _verify_replica_set_config(self) -> None:
        """Verify and configure replica set if needed"""
        try:
            # Check replica set status
            rs_status = await self.primary_client.admin.command("replSetGetStatus")
            
            if rs_status.get("ok") != 1:
                self.logger.warning("Replica set not properly configured")
                await self._configure_replica_set()
            else:
                self.logger.info(f"Replica set '{self.replica_set_name}' is configured")
                
        except Exception as e:
            if "not running with --replSet" in str(e):
                self.logger.warning("MongoDB not running in replica set mode")
            else:
                self.logger.error(f"Error verifying replica set config: {e}")
    
    async def _configure_replica_set(self) -> None:
        """Configure MongoDB replica set"""
        try:
            self.logger.info("Configuring MongoDB replica set...")
            
            # Basic replica set configuration
            config = {
                "_id": self.replica_set_name,
                "members": [
                    {
                        "_id": 0,
                        "host": f"{self.config['host']}:{self.config['port']}",
                        "priority": 1
                    }
                ]
            }
            
            # Add secondary members
            for idx, secondary in enumerate(self.config.get("secondaries", [])):
                config["members"].append({
                    "_id": idx + 1,
                    "host": f"{secondary['host']}:{secondary['port']}",
                    "priority": 0.5
                })
            
            # Initialize replica set
            await self.primary_client.admin.command("replSetInitiate", config)
            
            # Wait for replica set to stabilize
            await asyncio.sleep(10)
            
            self.logger.info("Replica set configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to configure replica set: {e}")
            raise
    
    async def _setup_monitoring(self) -> None:
        """Setup MongoDB replication monitoring"""
        self.is_monitoring = True
        
        # Start oplog monitoring
        self.oplog_processor_task = asyncio.create_task(self._monitor_oplog())
        
        self.logger.info("MongoDB replication monitoring started")
    
    async def start_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any], 
        mode: str = "replica_set"
    ) -> bool:
        """
        Start MongoDB replication process.
        
        Args:
            source_config: Source database configuration
            target_config: Target database configuration
            mode: Replication mode (replica_set, sharded, cross_cluster)
            
        Returns:
            bool: True if replication started successfully
        """
        try:
            self.logger.info(f"Starting MongoDB replication in {mode} mode")
            
            if mode == "replica_set":
                return await self._start_replica_set_replication(source_config, target_config)
            elif mode == "sharded":
                return await self._start_sharded_replication(source_config, target_config)
            elif mode == "cross_cluster":
                return await self._start_cross_cluster_replication(source_config, target_config)
            else:
                self.logger.error(f"Unsupported replication mode: {mode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start MongoDB replication: {e}")
            return False
    
    async def _start_replica_set_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start replica set replication"""
        try:
            # Replica set replication is automatic in MongoDB
            # We just need to ensure proper configuration
            
            # Verify replica set is healthy
            rs_status = await self.primary_client.admin.command("replSetGetStatus")
            
            if rs_status.get("ok") != 1:
                self.logger.error("Replica set not healthy")
                return False
            
            # Check all members are reachable
            for member in rs_status.get("members", []):
                if member.get("health") != 1:
                    self.logger.warning(f"Member {member.get('name')} is not healthy")
            
            self.logger.info("Replica set replication is active")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start replica set replication: {e}")
            return False
    
    async def _start_sharded_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start sharded cluster replication"""
        try:
            # Configure sharding if not already done
            databases_to_shard = source_config.get("databases", [])
            
            for db_config in databases_to_shard:
                db_name = db_config["name"]
                collections = db_config.get("collections", [])
                
                # Enable sharding for database
                await self.primary_client.admin.command("enableSharding", db_name)
                
                # Shard collections
                for collection_config in collections:
                    collection_name = collection_config["name"]
                    shard_key = collection_config.get("shard_key", {"_id": 1})
                    
                    await self.primary_client.admin.command(
                        "shardCollection",
                        f"{db_name}.{collection_name}",
                        key=shard_key
                    )
            
            self.logger.info("Sharded cluster replication configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start sharded replication: {e}")
            return False
    
    async def _start_cross_cluster_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start cross-cluster replication using Change Streams"""
        try:
            databases = source_config.get("databases", [])
            
            for db_name in databases:
                # Start change stream for database
                asyncio.create_task(
                    self._process_change_stream(db_name, target_config)
                )
            
            self.logger.info("Cross-cluster replication started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start cross-cluster replication: {e}")
            return False
    
    async def _process_change_stream(self, database_name: str, target_config: Dict[str, Any]) -> None:
        """Process change stream for cross-cluster replication"""
        try:
            # Connect to target cluster
            target_client = AsyncIOMotorClient(
                self._build_connection_string(target_config)
            )
            
            # Watch changes in source database
            async with self.primary_client[database_name].watch() as stream:
                async for change in stream:
                    await self._replicate_change(change, target_client, database_name)
                    
        except Exception as e:
            self.logger.error(f"Error processing change stream for {database_name}: {e}")
    
    async def _replicate_change(
        self, 
        change: Dict[str, Any], 
        target_client: AsyncIOMotorClient, 
        database_name: str
    ) -> None:
        """Replicate a single change to target cluster"""
        try:
            operation_type = change.get("operationType")
            ns = change.get("ns", {})
            collection_name = ns.get("coll")
            
            if not collection_name:
                return
            
            target_collection = target_client[database_name][collection_name]
            
            if operation_type == "insert":
                document = change.get("fullDocument")
                if document:
                    await target_collection.insert_one(document)
                    
            elif operation_type == "update":
                document_key = change.get("documentKey")
                update_description = change.get("updateDescription", {})
                
                if document_key and update_description:
                    await target_collection.update_one(
                        document_key,
                        {
                            "$set": update_description.get("updatedFields", {}),
                            "$unset": {
                                field: "" for field in update_description.get("removedFields", [])
                            }
                        }
                    )
                    
            elif operation_type == "delete":
                document_key = change.get("documentKey")
                if document_key:
                    await target_collection.delete_one(document_key)
            
            # Update metrics
            self.metrics["operations_replicated"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to replicate change: {e}")
            self.metrics["error_count"] += 1
    
    async def _monitor_oplog(self) -> None:
        """Monitor MongoDB oplog for replication lag and health"""
        while self.is_monitoring:
            try:
                # Get oplog statistics
                oplog_stats = await self.primary_client.local.oplog.rs.find().sort([("$natural", -1)]).limit(1).to_list(1)
                
                if oplog_stats:
                    latest_op = oplog_stats[0]
                    current_timestamp = latest_op.get("ts")
                    
                    if self.last_oplog_timestamp:
                        # Calculate replication lag
                        lag_seconds = current_timestamp.time - self.last_oplog_timestamp.time
                        self.replication_lag = lag_seconds
                        self.metrics["replication_lag_ms"] = lag_seconds * 1000
                    
                    self.last_oplog_timestamp = current_timestamp
                
                # Check replica set status
                rs_status = await self.primary_client.admin.command("replSetGetStatus")
                
                # Update metrics from replica set status
                for member in rs_status.get("members", []):
                    if member.get("stateStr") == "SECONDARY":
                        member_lag = member.get("optimeDate")
                        if member_lag:
                            primary_optime = rs_status.get("optimeDate")
                            if primary_optime:
                                lag_ms = (primary_optime - member_lag).total_seconds() * 1000
                                self.metrics["replication_lag_ms"] = max(
                                    self.metrics["replication_lag_ms"], 
                                    lag_ms
                                )
                
                await asyncio.sleep(self.replication_config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoring oplog: {e}")
                await asyncio.sleep(30)
    
    async def stop_replication(self, graceful: bool = True) -> bool:
        """
        Stop MongoDB replication.
        
        Args:
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if stopped successfully
        """
        try:
            self.logger.info(f"Stopping MongoDB replication (graceful={graceful})")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.oplog_processor_task:
                self.oplog_processor_task.cancel()
                try:
                    await self.oplog_processor_task
                except asyncio.CancelledError:
                    pass
            
            if graceful:
                # Wait for pending operations to complete
                await asyncio.sleep(5)
            
            self.logger.info("MongoDB replication stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop MongoDB replication: {e}")
            return False
    
    async def pause_replication(self) -> bool:
        """
        Pause MongoDB replication.
        
        Returns:
            bool: True if paused successfully
        """
        try:
            self.logger.info("Pausing MongoDB replication")
            
            # For MongoDB, we can step down the primary to pause writes
            await self.primary_client.admin.command("replSetStepDown", 60)
            
            self.logger.info("MongoDB replication paused")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause MongoDB replication: {e}")
            return False
    
    async def resume_replication(self) -> bool:
        """
        Resume MongoDB replication.
        
        Returns:
            bool: True if resumed successfully
        """
        try:
            self.logger.info("Resuming MongoDB replication")
            
            # MongoDB will automatically elect a new primary
            # We just need to wait for the election to complete
            await asyncio.sleep(10)
            
            # Verify primary is available
            is_master = await self.primary_client.admin.command("isMaster")
            
            if is_master.get("ismaster"):
                self.logger.info("MongoDB replication resumed")
                return True
            else:
                self.logger.warning("Primary not yet available after resume")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to resume MongoDB replication: {e}")
            return False
    
    async def trigger_sync(self, force: bool = False) -> bool:
        """
        Trigger manual synchronization.
        
        Args:
            force: Whether to force synchronization
            
        Returns:
            bool: True if sync triggered successfully
        """
        try:
            self.logger.info(f"Triggering MongoDB sync (force={force})")
            
            # Force replica set to sync by stepping down and back up
            if force:
                await self.primary_client.admin.command("replSetStepDown", 1)
                await asyncio.sleep(5)
            
            # Ensure all secondaries are caught up
            await self.primary_client.admin.command("replSetSyncFrom", "")
            
            self.logger.info("MongoDB sync completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger MongoDB sync: {e}")
            return False
    
    async def prepare_maintenance(self, duration: timedelta) -> bool:
        """
        Prepare for maintenance mode.
        
        Args:
            duration: Expected maintenance duration
            
        Returns:
            bool: True if preparation successful
        """
        try:
            self.logger.info(f"Preparing MongoDB for maintenance (duration: {duration})")
            
            # Set replica set to maintenance mode
            # Step down primary to prevent writes
            await self.primary_client.admin.command("replSetStepDown", int(duration.total_seconds()))
            
            # Ensure all data is synced before maintenance
            await self._wait_for_replication_sync()
            
            self.logger.info("MongoDB prepared for maintenance")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare MongoDB for maintenance: {e}")
            return False
    
    async def exit_maintenance(self) -> bool:
        """
        Exit maintenance mode.
        
        Returns:
            bool: True if exit successful
        """
        try:
            self.logger.info("Exiting MongoDB maintenance mode")
            
            # MongoDB will automatically elect a new primary
            # Wait for election to complete
            await asyncio.sleep(10)
            
            # Verify cluster is healthy
            rs_status = await self.primary_client.admin.command("replSetGetStatus")
            
            if rs_status.get("ok") == 1:
                self.logger.info("MongoDB maintenance mode exited successfully")
                return True
            else:
                self.logger.error("MongoDB cluster not healthy after maintenance")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to exit MongoDB maintenance mode: {e}")
            return False
    
    async def _wait_for_replication_sync(self, timeout: int = 300) -> bool:
        """Wait for all replicas to sync"""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            try:
                rs_status = await self.primary_client.admin.command("replSetGetStatus")
                
                all_synced = True
                for member in rs_status.get("members", []):
                    if member.get("stateStr") not in ["PRIMARY", "SECONDARY"]:
                        all_synced = False
                        break
                
                if all_synced:
                    return True
                
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.warning(f"Error checking sync status: {e}")
                await asyncio.sleep(10)
        
        return False
    
    async def get_replication_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive replication metrics.
        
        Returns:
            Dict containing replication metrics
        """
        try:
            # Get replica set status
            rs_status = await self.primary_client.admin.command("replSetGetStatus")
            
            # Get database statistics
            db_stats = await self.primary_client.admin.command("dbStats")
            
            # Calculate additional metrics
            current_time = datetime.utcnow()
            self.metrics.update({
                "last_sync_time": current_time.isoformat(),
                "replica_set_health": rs_status.get("ok", 0),
                "member_count": len(rs_status.get("members", [])),
                "data_size_bytes": db_stats.get("dataSize", 0),
                "storage_size_bytes": db_stats.get("storageSize", 0),
                "index_size_bytes": db_stats.get("indexSize", 0),
                "collections_count": db_stats.get("collections", 0)
            })
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get MongoDB replication metrics: {e}")
            return self.metrics
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check MongoDB replication health.
        
        Returns:
            Dict containing health status
        """
        health = {
            "healthy": False,
            "primary_available": False,
            "secondaries_healthy": 0,
            "replication_lag_ok": False,
            "issues": []
        }
        
        try:
            # Check primary connection
            await self.primary_client.admin.command("ping")
            health["primary_available"] = True
            
            # Check replica set status
            rs_status = await self.primary_client.admin.command("replSetGetStatus")
            
            if rs_status.get("ok") == 1:
                members = rs_status.get("members", [])
                healthy_secondaries = 0
                
                for member in members:
                    if member.get("stateStr") == "SECONDARY" and member.get("health") == 1:
                        healthy_secondaries += 1
                    elif member.get("health") != 1:
                        health["issues"].append(f"Member {member.get('name')} is unhealthy")
                
                health["secondaries_healthy"] = healthy_secondaries
                
                # Check replication lag
                if self.metrics["replication_lag_ms"] < self.replication_config.lag_threshold:
                    health["replication_lag_ok"] = True
                else:
                    health["issues"].append(f"High replication lag: {self.metrics['replication_lag_ms']}ms")
                
                # Overall health
                health["healthy"] = (
                    health["primary_available"] and 
                    health["secondaries_healthy"] > 0 and 
                    health["replication_lag_ok"]
                )
            else:
                health["issues"].append("Replica set status check failed")
                
        except Exception as e:
            health["issues"].append(f"Health check error: {str(e)}")
        
        return health
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed MongoDB replication status.
        
        Returns:
            Dict containing detailed status information
        """
        try:
            rs_status = await self.primary_client.admin.command("replSetGetStatus")
            
            status = {
                "handler_type": "mongodb",
                "replica_set_name": self.replica_set_name,
                "primary_host": f"{self.config['host']}:{self.config['port']}",
                "read_preference": self.read_preference,
                "write_concern": self.write_concern,
                "monitoring_active": self.is_monitoring,
                "last_oplog_timestamp": self.last_oplog_timestamp.isoformat() if self.last_oplog_timestamp else None,
                "replica_set_status": rs_status,
                "metrics": self.metrics,
                "secondary_connections": len(self.secondary_clients)
            }
            
            return status
            
        except Exception as e:
            return {
                "handler_type": "mongodb",
                "error": str(e),
                "metrics": self.metrics
            }
    
    async def shutdown(self) -> None:
        """Shutdown MongoDB replication handler"""
        try:
            self.logger.info("Shutting down MongoDB replication handler...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.oplog_processor_task:
                self.oplog_processor_task.cancel()
                try:
                    await self.oplog_processor_task
                except asyncio.CancelledError:
                    pass
            
            # Close connections
            if self.primary_client:
                self.primary_client.close()
            
            if self.sync_client:
                self.sync_client.close()
            
            for client in self.secondary_clients.values():
                client.close()
            
            self.logger.info("MongoDB replication handler shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during MongoDB handler shutdown: {e}")
