"""Elasticsearch Replication Handler - IA Influencer Agent Platform

Advanced Elasticsearch cluster replication and cross-cluster search for content
protection, fingerprinting data, and analytics across multiple regions.

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
from elasticsearch import AsyncElasticsearch, Elasticsearch
from elasticsearch.exceptions import (
    ConnectionError, TransportError, NotFoundError, 
    ConflictError, RequestError
)
import json
import aiohttp
from .config import ReplicationConfig


class ElasticsearchReplicationHandler:
    """    Elasticsearch replication handler for cross-cluster search and replication.
    
    Provides comprehensive Elasticsearch replication capabilities including:
    - Cross-cluster replication (CCR)
    - Cross-cluster search (CCS)
    - Index lifecycle management
    - Snapshot and restore
    - Shard allocation control
    - Real-time monitoring and alerting
    """    
    def __init__(self, config: Dict[str, Any], replication_config: ReplicationConfig):
        """        Initialize Elasticsearch replication handler.
        
        Args:
            config: Elasticsearch-specific configuration
            replication_config: Global replication configuration
        """        self.config = config
        self.replication_config = replication_config
        self.logger = logging.getLogger(f"{__name__}.ElasticsearchReplicationHandler")
        
        # Connection management
        self.primary_client: Optional[AsyncElasticsearch] = None
        self.secondary_clients: Dict[str, AsyncElasticsearch] = {}
        self.sync_client: Optional[Elasticsearch] = None
        
        # Replication configuration
        self.cluster_name = config.get("cluster_name", "ia-influencer-cluster")
        self.replica_count = config.get("replica_count", 1)
        self.shard_count = config.get("shard_count", 5)
        self.refresh_interval = config.get("refresh_interval", "1s")
        
        # Cross-cluster replication settings
        self.remote_clusters = config.get("remote_clusters", {})
        self.replication_patterns = config.get("replication_patterns", [])
        
        # Monitoring
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.metrics = {
            "documents_indexed": 0,
            "documents_replicated": 0,
            "bytes_transferred": 0,
            "replication_lag_ms": 0,
            "last_sync_time": None,
            "error_count": 0,
            "active_shards": 0,
            "unassigned_shards": 0,
            "cluster_health": "unknown"
        }
        
        self.logger.info("ElasticsearchReplicationHandler initialized")
    
    async def initialize(self) -> bool:
        """        Initialize Elasticsearch replication connections and configuration.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info("Initializing Elasticsearch replication handler...")
            
            # Initialize primary connection
            await self._initialize_primary_connection()
            
            # Initialize secondary connections
            await self._initialize_secondary_connections()
            
            # Setup cluster configuration
            await self._setup_cluster_configuration()
            
            # Configure cross-cluster replication
            await self._configure_cross_cluster_replication()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            self.logger.info("Elasticsearch replication handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch replication handler: {e}")
            return False
    
    async def _initialize_primary_connection(self) -> None:
        """Initialize connection to primary Elasticsearch cluster"""        try:
            # Build connection configuration
            hosts = self._build_hosts_config(self.config)
            
            # SSL/TLS configuration
            ssl_config = {}
            if self.config.get("ssl_enabled", True):
                ssl_config = {
                    "use_ssl": True,
                    "verify_certs": self.config.get("verify_certs", True),
                    "ssl_show_warn": False
                }
                
                if self.config.get("ca_certs"):
                    ssl_config["ca_certs"] = self.config["ca_certs"]
                if self.config.get("client_cert"):
                    ssl_config["client_cert"] = self.config["client_cert"]
                if self.config.get("client_key"):
                    ssl_config["client_key"] = self.config["client_key"]
            
            # Authentication
            auth_config = {}
            if self.config.get("username") and self.config.get("password"):
                auth_config = {
                    "http_auth": (self.config["username"], self.config["password"])
                }
            elif self.config.get("api_key"):
                auth_config = {
                    "api_key": self.config["api_key"]
                }
            
            # Create async client
            self.primary_client = AsyncElasticsearch(
                hosts=hosts,
                timeout=self.config.get("timeout", 30),
                max_retries=self.config.get("max_retries", 3),
                retry_on_timeout=True,
                **ssl_config,
                **auth_config
            )
            
            # Create sync client for operations that require synchronous access
            self.sync_client = Elasticsearch(
                hosts=hosts,
                timeout=self.config.get("timeout", 30),
                **ssl_config,
                **auth_config
            )
            
            # Test connection
            cluster_health = await self.primary_client.cluster.health()
            self.logger.info(f"Primary Elasticsearch connection established. "
                           f"Cluster: {cluster_health['cluster_name']}, "
                           f"Status: {cluster_health['status']}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize primary Elasticsearch connection: {e}")
            raise
    
    async def _initialize_secondary_connections(self) -> None:
        """Initialize connections to secondary Elasticsearch clusters"""        for cluster_name, cluster_config in self.remote_clusters.items():
            try:
                hosts = self._build_hosts_config(cluster_config)
                
                # SSL/TLS configuration
                ssl_config = {}
                if cluster_config.get("ssl_enabled", True):
                    ssl_config = {
                        "use_ssl": True,
                        "verify_certs": cluster_config.get("verify_certs", True),
                        "ssl_show_warn": False
                    }
                
                # Authentication
                auth_config = {}
                if cluster_config.get("username") and cluster_config.get("password"):
                    auth_config = {
                        "http_auth": (cluster_config["username"], cluster_config["password"])
                    }
                
                client = AsyncElasticsearch(
                    hosts=hosts,
                    timeout=30,
                    **ssl_config,
                    **auth_config
                )
                
                # Test connection
                await client.cluster.health()
                
                self.secondary_clients[cluster_name] = client
                self.logger.info(f"Secondary Elasticsearch connection established: {cluster_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to connect to secondary cluster {cluster_name}: {e}")
    
    def _build_hosts_config(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build Elasticsearch hosts configuration"""        hosts = []
        
        # Single host configuration
        if "host" in config and "port" in config:
            hosts.append({
                "host": config["host"],
                "port": config["port"]
            })
        
        # Multiple hosts configuration
        elif "hosts" in config:
            for host_config in config["hosts"]:
                if isinstance(host_config, str):
                    # Parse host:port string
                    if ":" in host_config:
                        host, port = host_config.split(":", 1)
                        hosts.append({"host": host, "port": int(port)})
                    else:
                        hosts.append({"host": host_config, "port": 9200})
                elif isinstance(host_config, dict):
                    hosts.append(host_config)
        
        return hosts or [{"host": "localhost", "port": 9200}]
    
    async def _setup_cluster_configuration(self) -> None:
        """Setup cluster-level configuration"""        try:
            # Set cluster-level settings
            cluster_settings = {
                "persistent": {
                    "cluster.routing.allocation.disk.threshold.enabled": True,
                    "cluster.routing.allocation.disk.watermark.low": "85%",
                    "cluster.routing.allocation.disk.watermark.high": "90%",
                    "cluster.routing.allocation.disk.watermark.flood_stage": "95%",
                    "indices.recovery.max_bytes_per_sec": "100mb",
                    "cluster.routing.allocation.cluster_concurrent_rebalance": 2
                }
            }
            
            await self.primary_client.cluster.put_settings(body=cluster_settings)
            
            # Setup index templates for content protection data
            await self._setup_index_templates()
            
            self.logger.info("Cluster configuration completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup cluster configuration: {e}")
    
    async def _setup_index_templates(self) -> None:
        """Setup index templates for the platform"""        templates = [
            {
                "name": "fingerprints-template",
                "index_patterns": ["fingerprints-*"],
                "template": {
                    "settings": {
                        "number_of_shards": self.shard_count,
                        "number_of_replicas": self.replica_count,
                        "refresh_interval": self.refresh_interval,
                        "analysis": {
                            "analyzer": {
                                "content_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "asciifolding", "stop"]
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "content_hash": {"type": "keyword"},
                            "fingerprint_vector": {"type": "dense_vector", "dims": 512},
                            "content_type": {"type": "keyword"},
                            "creator_id": {"type": "keyword"},
                            "platform": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "metadata": {"type": "object", "dynamic": True}
                        }
                    }
                }
            },
            {
                "name": "analytics-template",
                "index_patterns": ["analytics-*"],
                "template": {
                    "settings": {
                        "number_of_shards": self.shard_count,
                        "number_of_replicas": self.replica_count,
                        "refresh_interval": "30s"
                    },
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "event_type": {"type": "keyword"},
                            "platform": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "metrics": {"type": "object", "dynamic": True},
                            "location": {"type": "geo_point"}
                        }
                    }
                }
            },
            {
                "name": "monitoring-template",
                "index_patterns": ["monitoring-*"],
                "template": {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "refresh_interval": "5s"
                    },
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "service": {"type": "keyword"},
                            "level": {"type": "keyword"},
                            "message": {"type": "text"},
                            "metrics": {"type": "object", "dynamic": True}
                        }
                    }
                }
            }
        ]
        
        for template in templates:
            try:
                await self.primary_client.indices.put_index_template(
                    name=template["name"],
                    body=template
                )
                self.logger.debug(f"Created index template: {template['name']}")
            except Exception as e:
                self.logger.error(f"Failed to create template {template['name']}: {e}")
    
    async def _configure_cross_cluster_replication(self) -> None:
        """Configure cross-cluster replication"""        try:
            # Configure remote clusters
            for cluster_name, cluster_config in self.remote_clusters.items():
                remote_settings = {
                    "persistent": {
                        f"cluster.remote.{cluster_name}.seeds": cluster_config.get("seeds", []),
                        f"cluster.remote.{cluster_name}.skip_unavailable": True
                    }
                }
                
                await self.primary_client.cluster.put_settings(body=remote_settings)
                self.logger.info(f"Configured remote cluster: {cluster_name}")
            
            # Setup follower indices for configured patterns
            for pattern in self.replication_patterns:
                await self._setup_follower_index(pattern)
            
        except Exception as e:
            self.logger.error(f"Failed to configure cross-cluster replication: {e}")
    
    async def _setup_follower_index(self, pattern: Dict[str, Any]) -> None:
        """Setup a follower index for cross-cluster replication"""        try:
            leader_index = pattern["leader_index"]
            follower_index = pattern["follower_index"]
            remote_cluster = pattern["remote_cluster"]
            
            follower_config = {
                "remote_cluster": remote_cluster,
                "leader_index": leader_index,
                "max_read_request_operation_count": 5120,
                "max_outstanding_read_requests": 12,
                "max_read_request_size": "32mb",
                "max_write_request_operation_count": 5120,
                "max_outstanding_write_requests": 9,
                "max_write_request_size": "9mb",
                "max_write_buffer_count": 512,
                "max_write_buffer_size": "512mb",
                "max_retry_delay": "500ms",
                "read_poll_timeout": "1m"
            }
            
            await self.primary_client.ccr.put_follow(
                index=follower_index,
                body=follower_config
            )
            
            self.logger.info(f"Setup follower index: {follower_index} -> {remote_cluster}:{leader_index}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup follower index {pattern}: {e}")
    
    async def _setup_monitoring(self) -> None:
        """Setup Elasticsearch replication monitoring"""        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_replication())
        self.logger.info("Elasticsearch replication monitoring started")
    
    async def start_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any], 
        mode: str = "cross_cluster"
    ) -> bool:
        """        Start Elasticsearch replication process.
        
        Args:
            source_config: Source cluster configuration
            target_config: Target cluster configuration
            mode: Replication mode (cross_cluster, snapshot_restore, index_copy)
            
        Returns:
            bool: True if replication started successfully
        """        try:
            self.logger.info(f"Starting Elasticsearch replication in {mode} mode")
            
            if mode == "cross_cluster":
                return await self._start_cross_cluster_replication(source_config, target_config)
            elif mode == "snapshot_restore":
                return await self._start_snapshot_replication(source_config, target_config)
            elif mode == "index_copy":
                return await self._start_index_copy_replication(source_config, target_config)
            else:
                self.logger.error(f"Unsupported replication mode: {mode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start Elasticsearch replication: {e}")
            return False
    
    async def _start_cross_cluster_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start cross-cluster replication"""        try:
            indices_to_replicate = source_config.get("indices", [])
            
            for index_config in indices_to_replicate:
                source_index = index_config["name"]
                target_index = index_config.get("target_name", source_index)
                remote_cluster = target_config.get("cluster_name")
                
                # Create follower index
                follower_config = {
                    "remote_cluster": remote_cluster,
                    "leader_index": source_index,
                    **index_config.get("ccr_settings", {})
                }
                
                await self.primary_client.ccr.put_follow(
                    index=target_index,
                    body=follower_config
                )
                
                self.logger.info(f"Started CCR for {source_index} -> {target_index}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start cross-cluster replication: {e}")
            return False
    
    async def _start_snapshot_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start snapshot-based replication"""        try:
            repository_name = source_config.get("repository", "backup-repo")
            indices = source_config.get("indices", ["*"])
            
            # Create snapshot
            snapshot_name = f"replication-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            
            snapshot_config = {
                "indices": ",".join(indices),
                "ignore_unavailable": True,
                "include_global_state": False,
                "metadata": {
                    "purpose": "replication",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self.primary_client.snapshot.create(
                repository=repository_name,
                snapshot=snapshot_name,
                body=snapshot_config
            )
            
            # Schedule restore on target cluster
            asyncio.create_task(
                self._restore_snapshot_on_target(snapshot_name, repository_name, target_config)
            )
            
            self.logger.info(f"Started snapshot replication: {snapshot_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start snapshot replication: {e}")
            return False
    
    async def _start_index_copy_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start index copy replication using reindex API"""        try:
            target_cluster = target_config.get("cluster_name")
            target_client = self.secondary_clients.get(target_cluster)
            
            if not target_client:
                self.logger.error(f"Target cluster not configured: {target_cluster}")
                return False
            
            indices = source_config.get("indices", [])
            
            for index_name in indices:
                # Use reindex API to copy data
                reindex_config = {
                    "source": {
                        "index": index_name,
                        "remote": {
                            "host": f"http://{self.config['host']}:{self.config['port']}"
                        }
                    },
                    "dest": {
                        "index": f"{index_name}-replica"
                    }
                }
                
                # Start reindex operation on target cluster
                response = await target_client.reindex(body=reindex_config, wait_for_completion=False)
                task_id = response.get("task")
                
                if task_id:
                    self.logger.info(f"Started index copy for {index_name}, task: {task_id}")
                    # Monitor reindex task
                    asyncio.create_task(self._monitor_reindex_task(target_client, task_id))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start index copy replication: {e}")
            return False
    
    async def _restore_snapshot_on_target(
        self, 
        snapshot_name: str, 
        repository_name: str, 
        target_config: Dict[str, Any]
    ) -> None:
        """Restore snapshot on target cluster"""        try:
            # Wait for snapshot to complete
            await self._wait_for_snapshot_completion(snapshot_name, repository_name)
            
            target_cluster = target_config.get("cluster_name")
            target_client = self.secondary_clients.get(target_cluster)
            
            if not target_client:
                self.logger.error(f"Target cluster not available: {target_cluster}")
                return
            
            # Restore snapshot
            restore_config = {
                "ignore_unavailable": True,
                "include_global_state": False,
                "rename_pattern": "(.+)",
                "rename_replacement": "$1-replica"
            }
            
            await target_client.snapshot.restore(
                repository=repository_name,
                snapshot=snapshot_name,
                body=restore_config
            )
            
            self.logger.info(f"Restored snapshot {snapshot_name} on {target_cluster}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore snapshot on target: {e}")
    
    async def _wait_for_snapshot_completion(self, snapshot_name: str, repository_name: str) -> None:
        """Wait for snapshot to complete"""        while True:
            try:
                response = await self.primary_client.snapshot.get(
                    repository=repository_name,
                    snapshot=snapshot_name
                )
                
                snapshot = response["snapshots"][0]
                state = snapshot.get("state")
                
                if state == "SUCCESS":
                    break
                elif state == "FAILED":
                    raise Exception(f"Snapshot failed: {snapshot.get('failures', [])}")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error checking snapshot status: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_reindex_task(self, client: AsyncElasticsearch, task_id: str) -> None:
        """Monitor reindex task progress"""        while True:
            try:
                response = await client.tasks.get(task_id=task_id)
                
                if response.get("completed"):
                    if response.get("response", {}).get("failures"):
                        self.logger.error(f"Reindex task {task_id} failed: {response['response']['failures']}")
                    else:
                        self.logger.info(f"Reindex task {task_id} completed successfully")
                    break
                
                # Log progress
                progress = response.get("task", {}).get("status", {})
                total = progress.get("total", 0)
                created = progress.get("created", 0)
                
                if total > 0:
                    percentage = (created / total) * 100
                    self.logger.info(f"Reindex progress: {percentage:.1f}% ({created}/{total})")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error monitoring reindex task {task_id}: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_replication(self) -> None:
        """Monitor Elasticsearch replication health and metrics"""        while self.is_monitoring:
            try:
                # Get cluster health
                health = await self.primary_client.cluster.health()
                self.metrics["cluster_health"] = health["status"]
                self.metrics["active_shards"] = health["active_shards"]
                self.metrics["unassigned_shards"] = health["unassigned_shards"]
                
                # Get cluster stats
                stats = await self.primary_client.cluster.stats()
                indices_stats = stats.get("indices", {})
                
                self.metrics["documents_indexed"] = indices_stats.get("count", 0)
                self.metrics["bytes_transferred"] = indices_stats.get("store", {}).get("size_in_bytes", 0)
                
                # Monitor CCR if enabled
                if self.replication_patterns:
                    await self._monitor_ccr_stats()
                
                # Update last sync time
                self.metrics["last_sync_time"] = datetime.utcnow().isoformat()
                
                await asyncio.sleep(self.replication_config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in replication monitoring: {e}")
                self.metrics["error_count"] += 1
                await asyncio.sleep(60)
    
    async def _monitor_ccr_stats(self) -> None:
        """Monitor Cross-Cluster Replication statistics"""        try:
            # Get CCR stats
            ccr_stats = await self.primary_client.ccr.stats()
            
            total_operations = 0
            max_lag = 0
            
            for follower_index in ccr_stats.get("follow_stats", {}).get("indices", []):
                for shard in follower_index.get("shards", []):
                    operations_read = shard.get("operations_read", 0)
                    operations_written = shard.get("operations_written", 0)
                    
                    total_operations += operations_read
                    
                    # Calculate lag
                    leader_global_checkpoint = shard.get("leader_global_checkpoint", 0)
                    follower_global_checkpoint = shard.get("follower_global_checkpoint", 0)
                    lag = leader_global_checkpoint - follower_global_checkpoint
                    
                    max_lag = max(max_lag, lag)
            
            self.metrics["documents_replicated"] = total_operations
            self.metrics["replication_lag_ms"] = max_lag  # Approximate lag in operations
            
        except Exception as e:
            self.logger.error(f"Error monitoring CCR stats: {e}")
    
    async def stop_replication(self, graceful: bool = True) -> bool:
        """        Stop Elasticsearch replication.
        
        Args:
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if stopped successfully
        """        try:
            self.logger.info(f"Stopping Elasticsearch replication (graceful={graceful})")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Stop CCR followers
            for pattern in self.replication_patterns:
                try:
                    follower_index = pattern["follower_index"]
                    await self.primary_client.ccr.pause_follow(index=follower_index)
                    
                    if not graceful:
                        await self.primary_client.ccr.unfollow(index=follower_index)
                    
                    self.logger.info(f"Stopped CCR for {follower_index}")
                    
                except Exception as e:
                    self.logger.error(f"Error stopping CCR for {follower_index}: {e}")
            
            self.logger.info("Elasticsearch replication stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Elasticsearch replication: {e}")
            return False
    
    async def pause_replication(self) -> bool:
        """        Pause Elasticsearch replication.
        
        Returns:
            bool: True if paused successfully
        """        try:
            self.logger.info("Pausing Elasticsearch replication")
            
            # Pause CCR followers
            for pattern in self.replication_patterns:
                follower_index = pattern["follower_index"]
                await self.primary_client.ccr.pause_follow(index=follower_index)
                self.logger.info(f"Paused CCR for {follower_index}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause Elasticsearch replication: {e}")
            return False
    
    async def resume_replication(self) -> bool:
        """        Resume Elasticsearch replication.
        
        Returns:
            bool: True if resumed successfully
        """        try:
            self.logger.info("Resuming Elasticsearch replication")
            
            # Resume CCR followers
            for pattern in self.replication_patterns:
                follower_index = pattern["follower_index"]
                await self.primary_client.ccr.resume_follow(index=follower_index)
                self.logger.info(f"Resumed CCR for {follower_index}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume Elasticsearch replication: {e}")
            return False
    
    async def trigger_sync(self, force: bool = False) -> bool:
        """        Trigger manual synchronization.
        
        Args:
            force: Whether to force synchronization
            
        Returns:
            bool: True if sync triggered successfully
        """        try:
            self.logger.info(f"Triggering Elasticsearch sync (force={force})")
            
            if force:
                # Force refresh all indices
                await self.primary_client.indices.refresh(index="_all")
                
                # Force sync all CCR followers
                for pattern in self.replication_patterns:
                    follower_index = pattern["follower_index"]
                    
                    # Pause and resume to force sync
                    await self.primary_client.ccr.pause_follow(index=follower_index)
                    await asyncio.sleep(1)
                    await self.primary_client.ccr.resume_follow(index=follower_index)
            
            self.logger.info("Elasticsearch sync completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger Elasticsearch sync: {e}")
            return False
    
    async def prepare_maintenance(self, duration: timedelta) -> bool:
        """        Prepare for maintenance mode.
        
        Args:
            duration: Expected maintenance duration
            
        Returns:
            bool: True if preparation successful
        """        try:
            self.logger.info(f"Preparing Elasticsearch for maintenance (duration: {duration})")
            
            # Disable shard allocation
            allocation_settings = {
                "persistent": {
                    "cluster.routing.allocation.enable": "none"
                }
            }
            
            await self.primary_client.cluster.put_settings(body=allocation_settings)
            
            # Sync flush all indices
            await self.primary_client.indices.flush(index="_all", force=True)
            
            self.logger.info("Elasticsearch prepared for maintenance")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare Elasticsearch for maintenance: {e}")
            return False
    
    async def exit_maintenance(self) -> bool:
        """        Exit maintenance mode.
        
        Returns:
            bool: True if exit successful
        """        try:
            self.logger.info("Exiting Elasticsearch maintenance mode")
            
            # Re-enable shard allocation
            allocation_settings = {
                "persistent": {
                    "cluster.routing.allocation.enable": "all"
                }
            }
            
            await self.primary_client.cluster.put_settings(body=allocation_settings)
            
            # Wait for cluster to stabilize
            await asyncio.sleep(10)
            
            # Check cluster health
            health = await self.primary_client.cluster.health(wait_for_status="yellow", timeout="30s")
            
            if health["status"] in ["green", "yellow"]:
                self.logger.info("Elasticsearch maintenance mode exited successfully")
                return True
            else:
                self.logger.warning(f"Cluster health after maintenance: {health['status']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to exit Elasticsearch maintenance mode: {e}")
            return False
    
    async def get_replication_metrics(self) -> Dict[str, Any]:
        """        Get comprehensive replication metrics.
        
        Returns:
            Dict containing replication metrics
        """        try:
            # Get cluster stats
            cluster_stats = await self.primary_client.cluster.stats()
            nodes_stats = await self.primary_client.nodes.stats()
            
            # Update metrics with fresh data
            self.metrics.update({
                "cluster_name": cluster_stats.get("cluster_name"),
                "nodes_count": cluster_stats.get("nodes", {}).get("count", {}).get("total", 0),
                "indices_count": cluster_stats.get("indices", {}).get("count", 0),
                "shards_total": cluster_stats.get("indices", {}).get("shards", {}).get("total", 0),
                "docs_count": cluster_stats.get("indices", {}).get("docs", {}).get("count", 0),
                "store_size_bytes": cluster_stats.get("indices", {}).get("store", {}).get("size_in_bytes", 0),
                "last_sync_time": datetime.utcnow().isoformat()
            })
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get Elasticsearch replication metrics: {e}")
            return self.metrics
    
    async def check_health(self) -> Dict[str, Any]:
        """        Check Elasticsearch replication health.
        
        Returns:
            Dict containing health status
        """        health = {
            "healthy": False,
            "cluster_available": False,
            "replication_active": False,
            "issues": []
        }
        
        try:
            # Check cluster health
            cluster_health = await self.primary_client.cluster.health()
            
            health["cluster_available"] = True
            health["cluster_status"] = cluster_health["status"]
            
            if cluster_health["status"] == "red":
                health["issues"].append("Cluster status is RED")
            elif cluster_health["unassigned_shards"] > 0:
                health["issues"].append(f"Unassigned shards: {cluster_health['unassigned_shards']}")
            
            # Check CCR health
            if self.replication_patterns:
                try:
                    ccr_stats = await self.primary_client.ccr.stats()
                    
                    active_followers = 0
                    for follower_index in ccr_stats.get("follow_stats", {}).get("indices", []):
                        for shard in follower_index.get("shards", []):
                            if shard.get("fatal_exception") is None:
                                active_followers += 1
                            else:
                                health["issues"].append(f"CCR shard error: {shard.get('fatal_exception')}")
                    
                    health["replication_active"] = active_followers > 0
                    health["active_followers"] = active_followers
                    
                except Exception as e:
                    health["issues"].append(f"CCR health check failed: {str(e)}")
            
            # Overall health
            health["healthy"] = (
                health["cluster_available"] and
                cluster_health["status"] in ["green", "yellow"] and
                len(health["issues"]) == 0
            )
            
        except Exception as e:
            health["issues"].append(f"Health check error: {str(e)}")
        
        return health
    
    async def get_status(self) -> Dict[str, Any]:
        """        Get detailed Elasticsearch replication status.
        
        Returns:
            Dict containing detailed status information
        """        try:
            cluster_health = await self.primary_client.cluster.health()
            
            status = {
                "handler_type": "elasticsearch",
                "cluster_name": self.cluster_name,
                "primary_host": f"{self.config['host']}:{self.config['port']}",
                "replica_count": self.replica_count,
                "shard_count": self.shard_count,
                "monitoring_active": self.is_monitoring,
                "cluster_health": cluster_health,
                "remote_clusters": list(self.remote_clusters.keys()),
                "replication_patterns": len(self.replication_patterns),
                "metrics": self.metrics,
                "secondary_connections": len(self.secondary_clients)
            }
            
            return status
            
        except Exception as e:
            return {
                "handler_type": "elasticsearch",
                "error": str(e),
                "metrics": self.metrics
            }
    
    async def shutdown(self) -> None:
        """Shutdown Elasticsearch replication handler"""        try:
            self.logger.info("Shutting down Elasticsearch replication handler...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Close connections
            if self.primary_client:
                await self.primary_client.close()
            
            for client in self.secondary_clients.values():
                await client.close()
            
            if self.sync_client:
                self.sync_client.close()
            
            self.logger.info("Elasticsearch replication handler shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during Elasticsearch handler shutdown: {e}")
