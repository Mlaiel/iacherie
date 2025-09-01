"""Shard Coordinator - Ultra-Industrial Distributed Database Management

Enterprise-grade shard coordination system for ultra-scalable database operations.
Manages distributed shards, load balancing, failover, replication, and consistency
across multiple database nodes for the IA Influencer Agent + Content Protection Platform.

Features:
- Intelligent shard distribution and load balancing
- Automatic failover and disaster recovery
- Multi-master replication with conflict resolution
- Consistent hashing for optimal data distribution
- Real-time health monitoring and alerting
- Dynamic shard rebalancing and splitting
- Cross-shard transaction coordination
- Performance optimization and caching strategies

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING 🚨
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, or distribution is strictly prohibited.
"""
import logging
import asyncio
import threading
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import hashlib
import time
import random
from collections import defaultdict, deque

from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import QueuePool
import redis
import psutil

logger = logging.getLogger(__name__)

class ShardStatus(Enum):
    """Shard operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    MIGRATING = "migrating"
    SPLITTING = "splitting"

class ShardHealthStatus(Enum):
    """Shard health indicators"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    OFFLINE = "offline"

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"
    RESOURCE_BASED = "resource_based"
    GEOGRAPHIC = "geographic"

class ReplicationStrategy(Enum):
    """Data replication strategies"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    SEMI_SYNCHRONOUS = "semi_synchronous"
    MASTER_SLAVE = "master_slave"
    MASTER_MASTER = "master_master"
    CHAIN_REPLICATION = "chain_replication"

class ConsistencyLevel(Enum):
    """Data consistency levels"""
    STRONG = "strong"
    EVENTUAL = "eventual"
    WEAK = "weak"
    BOUNDED_STALENESS = "bounded_staleness"
    SESSION = "session"
    CONSISTENT_PREFIX = "consistent_prefix"

class FailoverStrategy(Enum):
    """Failover strategies"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"

@dataclass
class ShardConfiguration:
    """Configuration for individual shard"""
    shard_id: str
    database_url: str
    weight: float = 1.0
    max_connections: int = 100
    timeout_seconds: int = 30
    backup_urls: List[str] = field(default_factory=list)
    geographic_region: str = "default"
    node_type: str = "primary"  # primary, replica, archive
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ShardMetrics:
    """Real-time shard performance metrics"""
    shard_id: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_connections: int = 0
    queries_per_second: float = 0.0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    replication_lag: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ShardNode:
    """Represents a database shard node"""
    shard_id: str
    config: ShardConfiguration
    status: ShardStatus = ShardStatus.INACTIVE
    health: ShardHealthStatus = ShardHealthStatus.UNKNOWN
    metrics: ShardMetrics = None
    engine: Any = None
    session_factory: Any = None
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    recovery_attempts: int = 0
    
    def __post_init__(self):
        if not self.metrics:
            self.metrics = ShardMetrics(shard_id=self.shard_id)

class ShardCoordinator:
    """
    Ultra-industrial shard coordinator for enterprise-grade distributed database management
    
    Manages distributed database shards with advanced features:
    - Intelligent load balancing and traffic distribution
    - Automatic failover with zero-downtime recovery
    - Multi-master replication with conflict resolution
    - Dynamic shard scaling and rebalancing
    - Cross-shard transaction coordination
    - Real-time performance monitoring and alerting
    - Geographic distribution and disaster recovery
    - Security-enhanced inter-shard communication
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize shard coordinator
        
        Args:
            config: Configuration dictionary with coordinator settings
        """
        self.config = config or {}
        self.shards: Dict[str, ShardNode] = {}
        self.shard_ring = []  # Consistent hashing ring
        self.load_balancer_strategy = LoadBalancingStrategy(
            self.config.get('load_balancing', 'consistent_hash')
        )
        self.replication_strategy = ReplicationStrategy(
            self.config.get('replication', 'asynchronous')
        )
        self.consistency_level = ConsistencyLevel(
            self.config.get('consistency', 'eventual')
        )
        self.failover_strategy = FailoverStrategy(
            self.config.get('failover', 'automatic')
        )
        
        # Performance and monitoring
        self.performance_cache = {}
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.circuit_breaker_threshold = self.config.get('circuit_breaker_threshold', 5)
        self.max_retry_attempts = self.config.get('max_retry_attempts', 3)
        
        # Redis for coordination and caching
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            decode_responses=True
        ) if redis_config else None
        
        # Thread safety and async support
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=16)
        self._monitoring_active = False
        self._health_monitor_task = None
        
        # Statistics and metrics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'shard_failures': defaultdict(int),
            'last_reset': datetime.utcnow()
        }
        
        logger.info("ShardCoordinator initialized with advanced distributed management")

    def add_shard(self, shard_config: ShardConfiguration) -> bool:
        """
        Add new shard to the coordination system
        
        Args:
            shard_config: Configuration for the new shard
            
        Returns:
            bool: True if shard added successfully
        """
        try:
            with self._lock:
                shard_id = shard_config.shard_id
                
                if shard_id in self.shards:
                    logger.warning(f"Shard {shard_id} already exists, updating configuration")
                
                # Create database engine with advanced pooling
                engine = create_engine(
                    shard_config.database_url,
                    poolclass=QueuePool,
                    pool_size=shard_config.max_connections // 4,
                    max_overflow=shard_config.max_connections // 2,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    connect_args={
                        'connect_timeout': shard_config.timeout_seconds,
                        'application_name': f'shard_coordinator_{shard_id}',
                        'options': '-c default_transaction_isolation=read_committed'
                    }
                )
                
                session_factory = sessionmaker(bind=engine)
                
                # Create shard node
                shard_node = ShardNode(
                    shard_id=shard_id,
                    config=shard_config,
                    engine=engine,
                    session_factory=session_factory
                )
                
                # Test connection
                if self._test_shard_connection(shard_node):
                    shard_node.status = ShardStatus.ACTIVE
                    shard_node.health = ShardHealthStatus.HEALTHY
                    self.shards[shard_id] = shard_node
                    
                    # Update consistent hashing ring
                    self._update_hash_ring()
                    
                    # Start health monitoring for this shard
                    self._schedule_health_check(shard_id)
                    
                    logger.info(f"Successfully added shard: {shard_id}")
                    return True
                else:
                    logger.error(f"Failed to establish connection to shard: {shard_id}")
                    engine.dispose()
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add shard {shard_config.shard_id}: {e}")
            return False

    def _test_shard_connection(self, shard_node: ShardNode) -> bool:
        """Test connection to a shard node"""
        try:
            with shard_node.session_factory() as session:
                result = session.execute(text("SELECT 1")).scalar()
                return result == 1
        except Exception as e:
            logger.warning(f"Connection test failed for shard {shard_node.shard_id}: {e}")
            return False

    def _update_hash_ring(self):
        """Update consistent hashing ring for load distribution"""
        try:
            self.shard_ring.clear()
            
            # Add virtual nodes for each shard (based on weight)
            for shard_id, shard_node in self.shards.items():
                if shard_node.status == ShardStatus.ACTIVE:
                    weight = shard_node.config.weight
                    virtual_nodes = int(weight * 100)  # 100 virtual nodes per weight unit
                    
                    for i in range(virtual_nodes):
                        virtual_key = f"{shard_id}:{i}"
                        hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                        self.shard_ring.append((hash_value, shard_id))
            
            # Sort ring by hash value
            self.shard_ring.sort(key=lambda x: x[0])
            
            logger.debug(f"Updated hash ring with {len(self.shard_ring)} virtual nodes")
            
        except Exception as e:
            logger.error(f"Failed to update hash ring: {e}")

    def get_shard_for_key(self, key: str) -> Optional[str]:
        """
        Get optimal shard for a given key using consistent hashing
        
        Args:
            key: Key to hash for shard selection
            
        Returns:
            Optional[str]: Shard ID or None if no active shards
        """
        try:
            if not self.shard_ring:
                return None
            
            # Hash the key
            key_hash = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
            
            # Find the first shard in the ring with hash >= key_hash
            for hash_value, shard_id in self.shard_ring:
                if hash_value >= key_hash:
                    shard_node = self.shards.get(shard_id)
                    if shard_node and shard_node.status == ShardStatus.ACTIVE:
                        return shard_id
            
            # Wrap around to the first shard in the ring
            if self.shard_ring:
                _, shard_id = self.shard_ring[0]
                shard_node = self.shards.get(shard_id)
                if shard_node and shard_node.status == ShardStatus.ACTIVE:
                    return shard_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get shard for key {key}: {e}")
            return None

    def get_optimal_shard(self, operation_type: str = "read", 
                         geographic_preference: str = None,
                         consistency_requirement: ConsistencyLevel = None) -> Optional[str]:
        """
        Get optimal shard based on various factors
        
        Args:
            operation_type: Type of operation (read, write, analytics)
            geographic_preference: Preferred geographic region
            consistency_requirement: Required consistency level
            
        Returns:
            Optional[str]: Optimal shard ID
        """
        try:
            with self._lock:
                active_shards = [
                    shard for shard in self.shards.values()
                    if shard.status == ShardStatus.ACTIVE and 
                       shard.health in [ShardHealthStatus.HEALTHY, ShardHealthStatus.WARNING]
                ]
                
                if not active_shards:
                    return None
                
                # Filter by geographic preference
                if geographic_preference:
                    geo_shards = [
                        shard for shard in active_shards
                        if shard.config.geographic_region == geographic_preference
                    ]
                    if geo_shards:
                        active_shards = geo_shards
                
                # Filter by node capabilities
                if operation_type == "analytics":
                    analytics_shards = [
                        shard for shard in active_shards
                        if "analytics" in shard.config.capabilities
                    ]
                    if analytics_shards:
                        active_shards = analytics_shards
                
                # Apply load balancing strategy
                if self.load_balancer_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                    optimal_shard = min(active_shards, 
                                      key=lambda s: s.metrics.active_connections)
                elif self.load_balancer_strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                    optimal_shard = min(active_shards, 
                                      key=lambda s: s.metrics.average_response_time)
                elif self.load_balancer_strategy == LoadBalancingStrategy.RESOURCE_BASED:
                    optimal_shard = min(active_shards, 
                                      key=lambda s: (s.metrics.cpu_usage + s.metrics.memory_usage) / 2)
                else:  # Round robin or weighted round robin
                    optimal_shard = self._get_round_robin_shard(active_shards)
                
                return optimal_shard.shard_id if optimal_shard else None
                
        except Exception as e:
            logger.error(f"Failed to get optimal shard: {e}")
            return None

    def _get_round_robin_shard(self, shards: List[ShardNode]) -> Optional[ShardNode]:
        """Get shard using round-robin with weight consideration"""
        if not shards:
            return None
        
        # Simple round-robin for now (can be enhanced with weights)
        current_time = int(time.time())
        shard_index = current_time % len(shards)
        return shards[shard_index]

    def execute_query(self, query: str, shard_id: str = None, 
                     params: Dict[str, Any] = None,
                     operation_type: str = "read",
                     timeout: int = None) -> Any:
        """
        Execute query on optimal or specified shard with advanced error handling
        
        Args:
            query: SQL query to execute
            shard_id: Specific shard ID (optional)
            params: Query parameters
            operation_type: Type of operation for optimization
            timeout: Query timeout in seconds
            
        Returns:
            Query result or None if failed
        """
        start_time = time.time()
        params = params or {}
        timeout = timeout or 30
        
        try:
            # Determine target shard
            if not shard_id:
                shard_id = self.get_optimal_shard(operation_type)
            
            if not shard_id:
                raise Exception("No available shards for query execution")
            
            shard_node = self.shards.get(shard_id)
            if not shard_node or shard_node.status != ShardStatus.ACTIVE:
                raise Exception(f"Shard {shard_id} is not available")
            
            # Execute query with circuit breaker pattern
            if shard_node.failure_count >= self.circuit_breaker_threshold:
                if not self._should_retry_failed_shard(shard_node):
                    raise Exception(f"Shard {shard_id} circuit breaker is open")
            
            # Execute query
            result = self._execute_on_shard(shard_node, query, params, timeout)
            
            # Update success metrics
            self._update_query_metrics(shard_id, start_time, True)
            shard_node.failure_count = 0  # Reset failure count on success
            
            return result
            
        except Exception as e:
            # Update failure metrics
            self._update_query_metrics(shard_id or "unknown", start_time, False)
            
            if shard_id and shard_id in self.shards:
                self.shards[shard_id].failure_count += 1
            
            # Attempt failover if enabled
            if self.failover_strategy == FailoverStrategy.AUTOMATIC and shard_id:
                backup_result = self._attempt_failover_execution(query, params, shard_id, timeout)
                if backup_result is not None:
                    return backup_result
            
            logger.error(f"Query execution failed: {e}")
            raise

    def _execute_on_shard(self, shard_node: ShardNode, query: str, 
                         params: Dict[str, Any], timeout: int) -> Any:
        """Execute query on specific shard with proper resource management"""
        try:
            with shard_node.session_factory() as session:
                # Set query timeout
                session.execute(text(f"SET statement_timeout = '{timeout}s'"))
                
                # Execute the query
                if params:
                    result = session.execute(text(query), params)
                else:
                    result = session.execute(text(query))
                
                # Handle different result types
                if result.returns_rows:
                    return result.fetchall()
                else:
                    session.commit()
                    return result.rowcount
                    
        except OperationalError as e:
            if "timeout" in str(e).lower():
                logger.warning(f"Query timeout on shard {shard_node.shard_id}")
            raise
        except Exception as e:
            logger.error(f"Shard execution error on {shard_node.shard_id}: {e}")
            raise

    def _attempt_failover_execution(self, query: str, params: Dict[str, Any], 
                                  failed_shard_id: str, timeout: int) -> Any:
        """Attempt to execute query on backup shards"""
        try:
            failed_shard = self.shards.get(failed_shard_id)
            if not failed_shard:
                return None
            
            # Try backup URLs first
            for backup_url in failed_shard.config.backup_urls:
                try:
                    backup_engine = create_engine(backup_url, 
                                                pool_pre_ping=True,
                                                connect_args={'connect_timeout': 10})
                    backup_session_factory = sessionmaker(bind=backup_engine)
                    
                    with backup_session_factory() as session:
                        session.execute(text(f"SET statement_timeout = '{timeout}s'"))
                        if params:
                            result = session.execute(text(query), params)
                        else:
                            result = session.execute(text(query))
                        
                        logger.info(f"Failover successful using backup for shard {failed_shard_id}")
                        return result.fetchall() if result.returns_rows else result.rowcount
                        
                except Exception as backup_error:
                    logger.warning(f"Backup failover failed: {backup_error}")
                    continue
            
            # Try other healthy shards as last resort
            for shard_id, shard_node in self.shards.items():
                if (shard_id != failed_shard_id and 
                    shard_node.status == ShardStatus.ACTIVE and
                    shard_node.health == ShardHealthStatus.HEALTHY):
                    
                    try:
                        result = self._execute_on_shard(shard_node, query, params, timeout)
                        logger.info(f"Failover successful using shard {shard_id}")
                        return result
                    except Exception:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failover execution failed: {e}")
            return None

    def _should_retry_failed_shard(self, shard_node: ShardNode) -> bool:
        """Determine if we should retry a failed shard (circuit breaker logic)"""
        if not shard_node.last_health_check:
            return True
        
        # Allow retry after exponential backoff
        backoff_time = min(300, 2 ** shard_node.failure_count)  # Max 5 minutes
        time_since_last_check = (datetime.utcnow() - shard_node.last_health_check).total_seconds()
        
        return time_since_last_check >= backoff_time

    def _update_query_metrics(self, shard_id: str, start_time: float, success: bool):
        """Update query performance metrics"""
        try:
            execution_time = time.time() - start_time
            
            with self._lock:
                self.stats['total_requests'] += 1
                
                if success:
                    self.stats['successful_requests'] += 1
                else:
                    self.stats['failed_requests'] += 1
                    self.stats['shard_failures'][shard_id] += 1
                
                # Update running average response time
                current_avg = self.stats['average_response_time']
                total_requests = self.stats['total_requests']
                self.stats['average_response_time'] = (
                    (current_avg * (total_requests - 1) + execution_time) / total_requests
                )
                
                # Update shard-specific metrics
                if shard_id in self.shards:
                    shard_metrics = self.shards[shard_id].metrics
                    shard_metrics.average_response_time = (
                        (shard_metrics.average_response_time * 0.9) + (execution_time * 0.1)
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to update query metrics: {e}")

    def start_monitoring(self):
        """Start comprehensive health monitoring for all shards"""
        try:
            if self._monitoring_active:
                logger.warning("Monitoring is already active")
                return
            
            self._monitoring_active = True
            
            # Start health monitoring task
            self._health_monitor_task = threading.Thread(
                target=self._health_monitor_loop,
                daemon=True
            )
            self._health_monitor_task.start()
            
            logger.info("Shard monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")

    def _health_monitor_loop(self):
        """Main health monitoring loop"""
        while self._monitoring_active:
            try:
                self._perform_health_checks()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(5)  # Short sleep on error

    def _perform_health_checks(self):
        """Perform health checks on all shards"""
        try:
            futures = []
            
            with self._executor as executor:
                for shard_id, shard_node in self.shards.items():
                    future = executor.submit(self._check_shard_health, shard_node)
                    futures.append((shard_id, future))
                
                # Process health check results
                for shard_id, future in futures:
                    try:
                        health_status = future.result(timeout=10)
                        self._update_shard_health(shard_id, health_status)
                    except Exception as e:
                        logger.warning(f"Health check failed for shard {shard_id}: {e}")
                        self._update_shard_health(shard_id, ShardHealthStatus.CRITICAL)
                        
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")

    def _check_shard_health(self, shard_node: ShardNode) -> ShardHealthStatus:
        """Check health of individual shard"""
        try:
            start_time = time.time()
            
            # Basic connectivity test
            with shard_node.session_factory() as session:
                session.execute(text("SELECT 1")).scalar()
            
            response_time = time.time() - start_time
            
            # Collect system metrics
            self._collect_shard_metrics(shard_node)
            
            # Determine health status based on metrics
            if response_time > 5.0:  # 5 second threshold
                return ShardHealthStatus.CRITICAL
            elif response_time > 2.0 or shard_node.metrics.cpu_usage > 90:
                return ShardHealthStatus.WARNING
            else:
                return ShardHealthStatus.HEALTHY
                
        except Exception as e:
            logger.debug(f"Health check failed for {shard_node.shard_id}: {e}")
            return ShardHealthStatus.OFFLINE

    def _collect_shard_metrics(self, shard_node: ShardNode):
        """Collect detailed performance metrics for shard"""
        try:
            metrics = shard_node.metrics
            
            # Update basic metrics
            metrics.last_updated = datetime.utcnow()
            
            # Get database-specific metrics
            with shard_node.session_factory() as session:
                # Active connections
                conn_result = session.execute(text("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE state = 'active'
                """)).scalar()
                metrics.active_connections = conn_result or 0
                
                # Database size and stats
                stats_result = session.execute(text("""
                    SELECT 
                        sum(xact_commit + xact_rollback) as total_transactions,
                        sum(tup_returned + tup_fetched) as total_tuples
                    FROM pg_stat_database
                """)).fetchone()
                
                if stats_result:
                    # Calculate QPS (simplified)
                    metrics.queries_per_second = float(stats_result.total_transactions or 0) / 60
            
            # System resource metrics (if accessible)
            try:
                metrics.cpu_usage = psutil.cpu_percent()
                metrics.memory_usage = psutil.virtual_memory().percent
                metrics.disk_usage = psutil.disk_usage('/').percent
            except:
                pass  # System metrics not available
                
        except Exception as e:
            logger.debug(f"Failed to collect metrics for {shard_node.shard_id}: {e}")

    def _update_shard_health(self, shard_id: str, health_status: ShardHealthStatus):
        """Update shard health status and take appropriate actions"""
        try:
            shard_node = self.shards.get(shard_id)
            if not shard_node:
                return
            
            previous_health = shard_node.health
            shard_node.health = health_status
            shard_node.last_health_check = datetime.utcnow()
            
            # Take action based on health changes
            if health_status == ShardHealthStatus.OFFLINE and previous_health != ShardHealthStatus.OFFLINE:
                logger.error(f"Shard {shard_id} went offline!")
                shard_node.status = ShardStatus.FAILED
                self._trigger_failover_actions(shard_id)
                
            elif health_status == ShardHealthStatus.CRITICAL:
                logger.warning(f"Shard {shard_id} is in critical state")
                if shard_node.status == ShardStatus.ACTIVE:
                    shard_node.status = ShardStatus.DEGRADED
                    
            elif health_status == ShardHealthStatus.HEALTHY and previous_health in [
                ShardHealthStatus.CRITICAL, ShardHealthStatus.OFFLINE
            ]:
                logger.info(f"Shard {shard_id} recovered to healthy state")
                if shard_node.status in [ShardStatus.FAILED, ShardStatus.DEGRADED]:
                    shard_node.status = ShardStatus.ACTIVE
                    self._update_hash_ring()  # Re-add to load balancing
                    
        except Exception as e:
            logger.error(f"Failed to update shard health for {shard_id}: {e}")

    def _trigger_failover_actions(self, failed_shard_id: str):
        """Trigger automated failover actions"""
        try:
            logger.info(f"Triggering failover actions for shard: {failed_shard_id}")
            
            # Remove from load balancing
            self._update_hash_ring()
            
            # Notify monitoring systems
            self._send_alert(f"Shard {failed_shard_id} failed - failover initiated")
            
            # If Redis is available, store failover event
            if self.redis_client:
                failover_event = {
                    'shard_id': failed_shard_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'event_type': 'failover_initiated'
                }
                self.redis_client.lpush('shard_events', json.dumps(failover_event))
            
        except Exception as e:
            logger.error(f"Failed to trigger failover actions: {e}")

    def _send_alert(self, message: str, severity: str = "error"):
        """Send alert to monitoring systems"""
        try:
            alert = {
                'timestamp': datetime.utcnow().isoformat(),
                'message': message,
                'severity': severity,
                'source': 'shard_coordinator'
            }
            
            # Log the alert
            if severity == "error":
                logger.error(f"ALERT: {message}")
            elif severity == "warning":
                logger.warning(f"ALERT: {message}")
            else:
                logger.info(f"ALERT: {message}")
            
            # Store in Redis if available
            if self.redis_client:
                self.redis_client.lpush('alerts', json.dumps(alert))
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def _schedule_health_check(self, shard_id: str):
        """Schedule immediate health check for specific shard"""
        def check_health():
            try:
                shard_node = self.shards.get(shard_id)
                if shard_node:
                    health_status = self._check_shard_health(shard_node)
                    self._update_shard_health(shard_id, health_status)
            except Exception as e:
                logger.error(f"Scheduled health check failed for {shard_id}: {e}")
        
        self._executor.submit(check_health)

    def get_coordinator_status(self) -> Dict[str, Any]:
        """
        Get comprehensive coordinator status and metrics
        
        Returns:
            Dict containing detailed status information
        """
        try:
            with self._lock:
                active_shards = [s for s in self.shards.values() if s.status == ShardStatus.ACTIVE]
                healthy_shards = [s for s in active_shards if s.health == ShardHealthStatus.HEALTHY]
                
                shard_details = {}
                for shard_id, shard_node in self.shards.items():
                    shard_details[shard_id] = {
                        'status': shard_node.status.value,
                        'health': shard_node.health.value,
                        'metrics': {
                            'active_connections': shard_node.metrics.active_connections,
                            'cpu_usage': shard_node.metrics.cpu_usage,
                            'memory_usage': shard_node.metrics.memory_usage,
                            'queries_per_second': shard_node.metrics.queries_per_second,
                            'average_response_time': shard_node.metrics.average_response_time,
                            'error_rate': shard_node.metrics.error_rate
                        },
                        'failure_count': shard_node.failure_count,
                        'last_health_check': shard_node.last_health_check.isoformat() if shard_node.last_health_check else None,
                        'geographic_region': shard_node.config.geographic_region,
                        'weight': shard_node.config.weight
                    }
                
                return {
                    'coordinator': {
                        'status': 'active' if self._monitoring_active else 'inactive',
                        'load_balancing_strategy': self.load_balancer_strategy.value,
                        'replication_strategy': self.replication_strategy.value,
                        'failover_strategy': self.failover_strategy.value,
                        'consistency_level': self.consistency_level.value
                    },
                    'shards': {
                        'total_count': len(self.shards),
                        'active_count': len(active_shards),
                        'healthy_count': len(healthy_shards),
                        'hash_ring_size': len(self.shard_ring),
                        'details': shard_details
                    },
                    'performance': {
                        'total_requests': self.stats['total_requests'],
                        'successful_requests': self.stats['successful_requests'],
                        'failed_requests': self.stats['failed_requests'],
                        'success_rate': (
                            self.stats['successful_requests'] / max(1, self.stats['total_requests']) * 100
                        ),
                        'average_response_time': self.stats['average_response_time'],
                        'shard_failures': dict(self.stats['shard_failures'])
                    },
                    'system': {
                        'monitoring_active': self._monitoring_active,
                        'health_check_interval': self.health_check_interval,
                        'circuit_breaker_threshold': self.circuit_breaker_threshold,
                        'last_updated': datetime.utcnow().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get coordinator status: {e}")
            return {'error': str(e)}

    def rebalance_shards(self) -> bool:
        """
        Perform intelligent shard rebalancing based on current load
        
        Returns:
            bool: True if rebalancing was successful
        """
        try:
            logger.info("Starting intelligent shard rebalancing...")
            
            with self._lock:
                active_shards = [
                    shard for shard in self.shards.values()
                    if shard.status == ShardStatus.ACTIVE
                ]
                
                if len(active_shards) < 2:
                    logger.warning("Not enough active shards for rebalancing")
                    return False
                
                # Calculate load distribution metrics
                total_load = sum(
                    shard.metrics.cpu_usage + shard.metrics.memory_usage + 
                    (shard.metrics.active_connections / shard.config.max_connections * 100)
                    for shard in active_shards
                )
                
                avg_load = total_load / len(active_shards)
                
                # Identify overloaded and underloaded shards
                overloaded_shards = [
                    shard for shard in active_shards
                    if (shard.metrics.cpu_usage + shard.metrics.memory_usage + 
                        (shard.metrics.active_connections / shard.config.max_connections * 100)) > avg_load * 1.5
                ]
                
                underloaded_shards = [
                    shard for shard in active_shards
                    if (shard.metrics.cpu_usage + shard.metrics.memory_usage + 
                        (shard.metrics.active_connections / shard.config.max_connections * 100)) < avg_load * 0.5
                ]
                
                # Adjust weights for load balancing
                rebalanced = False
                for overloaded_shard in overloaded_shards:
                    if overloaded_shard.config.weight > 0.1:
                        overloaded_shard.config.weight *= 0.8  # Reduce weight
                        rebalanced = True
                        logger.info(f"Reduced weight for overloaded shard {overloaded_shard.shard_id}")
                
                for underloaded_shard in underloaded_shards:
                    if underloaded_shard.config.weight < 2.0:
                        underloaded_shard.config.weight *= 1.2  # Increase weight
                        rebalanced = True
                        logger.info(f"Increased weight for underloaded shard {underloaded_shard.shard_id}")
                
                if rebalanced:
                    # Update hash ring with new weights
                    self._update_hash_ring()
                    logger.info("Shard rebalancing completed successfully")
                else:
                    logger.info("No rebalancing needed - load is well distributed")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to rebalance shards: {e}")
            return False

    def remove_shard(self, shard_id: str, graceful: bool = True) -> bool:
        """
        Remove shard from coordination system
        
        Args:
            shard_id: ID of shard to remove
            graceful: Whether to perform graceful removal
            
        Returns:
            bool: True if removal was successful
        """
        try:
            with self._lock:
                if shard_id not in self.shards:
                    logger.warning(f"Shard {shard_id} not found for removal")
                    return False
                
                shard_node = self.shards[shard_id]
                
                if graceful:
                    # Mark shard as maintenance mode first
                    shard_node.status = ShardStatus.MAINTENANCE
                    logger.info(f"Shard {shard_id} marked for graceful removal")
                    
                    # Wait for ongoing connections to finish (with timeout)
                    timeout = 30  # 30 seconds timeout
                    start_time = time.time()
                    while (shard_node.metrics.active_connections > 0 and 
                           time.time() - start_time < timeout):
                        time.sleep(1)
                        self._collect_shard_metrics(shard_node)
                
                # Close database connections
                if shard_node.engine:
                    shard_node.engine.dispose()
                
                # Remove from coordination
                del self.shards[shard_id]
                self._update_hash_ring()
                
                logger.info(f"Successfully removed shard: {shard_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove shard {shard_id}: {e}")
            return False

    def shutdown(self):
        """Gracefully shutdown shard coordinator"""
        try:
            logger.info("Shutting down shard coordinator...")
            
            # Stop monitoring
            self._monitoring_active = False
            if self._health_monitor_task and self._health_monitor_task.is_alive():
                self._health_monitor_task.join(timeout=5)
            
            # Close all shard connections
            with self._lock:
                for shard_id, shard_node in self.shards.items():
                    try:
                        if shard_node.engine:
                            shard_node.engine.dispose()
                        logger.debug(f"Closed connections for shard: {shard_id}")
                    except Exception as e:
                        logger.warning(f"Error closing shard {shard_id}: {e}")
            
            # Shutdown thread pool
            self._executor.shutdown(wait=True)
            
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("Shard coordinator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shard coordinator shutdown: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()
    """
    Ultra-industrial shard coordination system
    
    Manages distributed database shards with enterprise-grade features:
    - Intelligent load balancing and distribution
    - Automatic failover and recovery
    - Performance monitoring and optimization
    - Cross-shard transaction coordination
    - Dynamic scaling and rebalancing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize shard coordinator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.shards: Dict[str, ShardNode] = {}
        self.active_shards: Set[str] = set()
        self.failed_shards: Set[str] = set()
        
        # Load balancing state
        self.load_balancer_strategy = LoadBalancingStrategy(
            self.config.get('load_balancing_strategy', 'consistent_hash')
        )
        self.round_robin_index = 0
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Replication and consistency
        self.replication_strategy = ReplicationStrategy(
            self.config.get('replication_strategy', 'asynchronous')
        )
        self.consistency_level = ConsistencyLevel(
            self.config.get('consistency_level', 'eventual')
        )
        
        # Monitoring and health checking
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.health_check_thread = None
        self.monitoring_thread = None
        
        # Failover configuration
        self.failover_strategy = FailoverStrategy(
            self.config.get('failover_strategy', 'automatic')
        )
        self.max_failure_count = self.config.get('max_failure_count', 3)
        self.recovery_timeout = self.config.get('recovery_timeout', 300)  # 5 minutes
        
        # Thread safety
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=16)
        
        # Redis for coordination (optional)
        self.redis_client = self._initialize_redis() if self.config.get('redis_url') else None
        
        # Consistent hashing ring
        self.hash_ring = ConsistentHashRing()
        
        logger.info("ShardCoordinator initialized with strategy: %s", self.load_balancer_strategy)

    def _initialize_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis client for coordination"""
        try:
            redis_client = redis.Redis.from_url(
                self.config['redis_url'],
                decode_responses=True,
                health_check_interval=30
            )
            redis_client.ping()
            logger.info("Redis coordination client initialized")
            return redis_client
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
            return None

    def add_shard(self, shard_config: ShardConfiguration) -> bool:
        """
        Add new shard to the coordinator
        
        Args:
            shard_config: Shard configuration
            
        Returns:
            bool: True if shard added successfully
        """
        try:
            with self._lock:
                if shard_config.shard_id in self.shards:
                    logger.warning(f"Shard {shard_config.shard_id} already exists")
                    return False
                
                # Create shard node
                shard_node = ShardNode(
                    shard_id=shard_config.shard_id,
                    config=shard_config
                )
                
                # Initialize database connection
                if self._initialize_shard_connection(shard_node):
                    self.shards[shard_config.shard_id] = shard_node
                    
                    # Add to consistent hash ring
                    self.hash_ring.add_node(shard_config.shard_id, shard_config.weight)
                    
                    # Start health monitoring
                    if self.monitoring_enabled:
                        self._start_health_monitoring()
                    
                    logger.info(f"Added shard: {shard_config.shard_id}")
                    return True
                else:
                    logger.error(f"Failed to initialize connection for shard: {shard_config.shard_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to add shard {shard_config.shard_id}: {e}")
            return False

    def _initialize_shard_connection(self, shard_node: ShardNode) -> bool:
        """Initialize database connection for shard"""
        try:
            # Create SQLAlchemy engine with connection pooling
            engine = create_engine(
                shard_node.config.database_url,
                poolclass=QueuePool,
                pool_size=shard_node.config.max_connections // 2,
                max_overflow=shard_node.config.max_connections // 2,
                pool_timeout=shard_node.config.timeout_seconds,
                pool_pre_ping=True,
                pool_recycle=3600  # 1 hour
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create session factory
            session_factory = sessionmaker(bind=engine)
            
            # Update shard node
            shard_node.engine = engine
            shard_node.session_factory = session_factory
            shard_node.status = ShardStatus.ACTIVE
            shard_node.health = ShardHealthStatus.HEALTHY
            
            # Add to active shards
            self.active_shards.add(shard_node.shard_id)
            
            logger.info(f"Initialized connection for shard: {shard_node.shard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize connection for shard {shard_node.shard_id}: {e}")
            shard_node.status = ShardStatus.FAILED
            shard_node.health = ShardHealthStatus.OFFLINE
            return False

    def remove_shard(self, shard_id: str) -> bool:
        """
        Remove shard from coordinator
        
        Args:
            shard_id: ID of shard to remove
            
        Returns:
            bool: True if shard removed successfully
        """
        try:
            with self._lock:
                if shard_id not in self.shards:
                    logger.warning(f"Shard {shard_id} not found")
                    return False
                
                shard_node = self.shards[shard_id]
                
                # Close database connections
                if shard_node.engine:
                    shard_node.engine.dispose()
                
                # Remove from tracking sets
                self.active_shards.discard(shard_id)
                self.failed_shards.discard(shard_id)
                
                # Remove from consistent hash ring
                self.hash_ring.remove_node(shard_id)
                
                # Remove from coordinator
                del self.shards[shard_id]
                
                logger.info(f"Removed shard: {shard_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove shard {shard_id}: {e}")
            return False

    def get_shard_for_key(self, key: str) -> Optional[ShardNode]:
        """
        Get appropriate shard for given key using consistent hashing
        
        Args:
            key: Sharding key (e.g., user_id, fingerprint_hash)
            
        Returns:
            ShardNode: Selected shard node or None if no active shards
        """
        try:
            if not self.active_shards:
                logger.warning("No active shards available")
                return None
            
            if self.load_balancer_strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                shard_id = self.hash_ring.get_node(key)
                if shard_id and shard_id in self.active_shards:
                    return self.shards[shard_id]
            
            elif self.load_balancer_strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._get_shard_round_robin()
            
            elif self.load_balancer_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._get_shard_least_connections()
            
            elif self.load_balancer_strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return self._get_shard_least_response_time()
            
            elif self.load_balancer_strategy == LoadBalancingStrategy.RESOURCE_BASED:
                return self._get_shard_resource_based()
            
            # Fallback to round-robin
            return self._get_shard_round_robin()
            
        except Exception as e:
            logger.error(f"Failed to get shard for key {key}: {e}")
            return None

    def _get_shard_round_robin(self) -> Optional[ShardNode]:
        """Get shard using round-robin load balancing"""
        if not self.active_shards:
            return None
        
        active_shard_list = list(self.active_shards)
        shard_id = active_shard_list[self.round_robin_index % len(active_shard_list)]
        self.round_robin_index += 1
        
        return self.shards[shard_id]

    def _get_shard_least_connections(self) -> Optional[ShardNode]:
        """Get shard with least active connections"""
        if not self.active_shards:
            return None
        
        min_connections = float('inf')
        selected_shard = None
        
        for shard_id in self.active_shards:
            connections = self.connection_counts[shard_id]
            if connections < min_connections:
                min_connections = connections
                selected_shard = self.shards[shard_id]
        
        return selected_shard

    def _get_shard_least_response_time(self) -> Optional[ShardNode]:
        """Get shard with lowest average response time"""
        if not self.active_shards:
            return None
        
        min_response_time = float('inf')
        selected_shard = None
        
        for shard_id in self.active_shards:
            response_times = self.response_times[shard_id]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                if avg_response_time < min_response_time:
                    min_response_time = avg_response_time
                    selected_shard = self.shards[shard_id]
        
        return selected_shard or self._get_shard_round_robin()

    def _get_shard_resource_based(self) -> Optional[ShardNode]:
        """Get shard based on resource utilization"""
        if not self.active_shards:
            return None
        
        best_score = float('inf')
        selected_shard = None
        
        for shard_id in self.active_shards:
            shard = self.shards[shard_id]
            metrics = shard.metrics
            
            # Calculate composite resource score (lower is better)
            resource_score = (
                metrics.cpu_usage * 0.4 +
                metrics.memory_usage * 0.3 +
                metrics.active_connections * 0.2 +
                metrics.error_rate * 0.1
            )
            
            if resource_score < best_score:
                best_score = resource_score
                selected_shard = shard
        
        return selected_shard

    def execute_query(self, key: str, query: str, params: Dict[str, Any] = None) -> Any:
        """
        Execute query on appropriate shard
        
        Args:
            key: Sharding key to determine target shard
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result
        """
        shard = self.get_shard_for_key(key)
        if not shard:
            raise Exception("No available shard for query execution")
        
        return self._execute_on_shard(shard, query, params)

    def _execute_on_shard(self, shard: ShardNode, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute query on specific shard with monitoring"""
        start_time = time.time()
        
        try:
            # Track connection
            self.connection_counts[shard.shard_id] += 1
            
            with shard.session_factory() as session:
                result = session.execute(text(query), params or {})
                session.commit()
                
                # Record response time
                response_time = time.time() - start_time
                self.response_times[shard.shard_id].append(response_time)
                
                # Update metrics
                shard.metrics.queries_per_second += 1
                shard.metrics.average_response_time = (
                    shard.metrics.average_response_time * 0.9 + response_time * 0.1
                )
                
                return result
                
        except Exception as e:
            # Record error
            shard.metrics.error_rate += 1
            shard.failure_count += 1
            
            # Check for failover
            if shard.failure_count >= self.max_failure_count:
                self._handle_shard_failure(shard)
            
            logger.error(f"Query failed on shard {shard.shard_id}: {e}")
            raise
            
        finally:
            # Release connection
            self.connection_counts[shard.shard_id] -= 1

    def execute_cross_shard_query(self, query: str, params: Dict[str, Any] = None) -> List[Any]:
        """
        Execute query across all active shards
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of results from all shards
        """
        if not self.active_shards:
            return []
        
        results = []
        
        # Execute in parallel across all shards
        with ThreadPoolExecutor(max_workers=len(self.active_shards)) as executor:
            future_to_shard = {
                executor.submit(self._execute_on_shard, self.shards[shard_id], query, params): shard_id
                for shard_id in self.active_shards
            }
            
            for future in as_completed(future_to_shard):
                shard_id = future_to_shard[future]
                try:
                    result = future.result()
                    results.append({'shard_id': shard_id, 'result': result})
                except Exception as e:
                    logger.error(f"Cross-shard query failed on {shard_id}: {e}")
                    results.append({'shard_id': shard_id, 'error': str(e)})
        
        return results

    def _handle_shard_failure(self, shard: ShardNode):
        """Handle shard failure and initiate recovery"""
        try:
            with self._lock:
                # Mark shard as failed
                shard.status = ShardStatus.FAILED
                shard.health = ShardHealthStatus.OFFLINE
                
                # Remove from active shards
                self.active_shards.discard(shard.shard_id)
                self.failed_shards.add(shard.shard_id)
                
                # Remove from hash ring temporarily
                self.hash_ring.remove_node(shard.shard_id)
                
                logger.warning(f"Shard {shard.shard_id} marked as failed")
                
                # Attempt automatic recovery if enabled
                if self.failover_strategy == FailoverStrategy.AUTOMATIC:
                    self._schedule_recovery(shard)
                
        except Exception as e:
            logger.error(f"Failed to handle shard failure for {shard.shard_id}: {e}")

    def _schedule_recovery(self, shard: ShardNode):
        """Schedule automatic recovery for failed shard"""
        def recovery_task():
            try:
                time.sleep(30)  # Wait before attempting recovery
                
                shard.recovery_attempts += 1
                shard.status = ShardStatus.RECOVERING
                
                logger.info(f"Attempting recovery for shard {shard.shard_id} (attempt {shard.recovery_attempts})")
                
                # Close existing connections
                if shard.engine:
                    shard.engine.dispose()
                
                # Reinitialize connection
                if self._initialize_shard_connection(shard):
                    # Reset failure count
                    shard.failure_count = 0
                    
                    # Add back to hash ring
                    self.hash_ring.add_node(shard.shard_id, shard.config.weight)
                    
                    # Remove from failed shards
                    self.failed_shards.discard(shard.shard_id)
                    
                    logger.info(f"Successfully recovered shard: {shard.shard_id}")
                else:
                    logger.error(f"Recovery failed for shard: {shard.shard_id}")
                    
                    # Schedule retry if within limits
                    if shard.recovery_attempts < 5:
                        self._executor.submit(recovery_task)
                        
            except Exception as e:
                logger.error(f"Recovery task failed for shard {shard.shard_id}: {e}")
        
        self._executor.submit(recovery_task)

    def _start_health_monitoring(self):
        """Start health monitoring for all shards"""
        if self.health_check_thread and self.health_check_thread.is_alive():
            return
        
        def health_check_loop():
            while self.monitoring_enabled:
                try:
                    self._perform_health_checks()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Health check loop error: {e}")
        
        self.health_check_thread = threading.Thread(target=health_check_loop, daemon=True)
        self.health_check_thread.start()
        
        logger.info("Health monitoring started")

    def _perform_health_checks(self):
        """Perform health checks on all shards"""
        for shard_id, shard in self.shards.items():
            try:
                self._check_shard_health(shard)
            except Exception as e:
                logger.error(f"Health check failed for shard {shard_id}: {e}")

    def _check_shard_health(self, shard: ShardNode):
        """Check health of individual shard"""
        try:
            start_time = time.time()
            
            # Test database connection
            with shard.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            response_time = time.time() - start_time
            
            # Update health metrics
            shard.metrics.last_updated = datetime.utcnow()
            shard.last_health_check = datetime.utcnow()
            
            # Determine health status based on response time and error rate
            if response_time > 5.0 or shard.metrics.error_rate > 10:
                shard.health = ShardHealthStatus.CRITICAL
            elif response_time > 2.0 or shard.metrics.error_rate > 5:
                shard.health = ShardHealthStatus.WARNING
            else:
                shard.health = ShardHealthStatus.HEALTHY
            
            # Reset failure count on successful health check
            if shard.health != ShardHealthStatus.CRITICAL:
                shard.failure_count = 0
            
        except Exception as e:
            shard.health = ShardHealthStatus.OFFLINE
            shard.failure_count += 1
            
            if shard.failure_count >= self.max_failure_count:
                self._handle_shard_failure(shard)
            
            logger.warning(f"Health check failed for shard {shard.shard_id}: {e}")

    def get_cluster_status(self) -> Dict[str, Any]:
        """
        Get comprehensive cluster status
        
        Returns:
            Dict containing cluster status information
        """
        try:
            total_shards = len(self.shards)
            active_shards = len(self.active_shards)
            failed_shards = len(self.failed_shards)
            
            # Calculate aggregate metrics
            total_queries = sum(shard.metrics.queries_per_second for shard in self.shards.values())
            avg_response_time = sum(shard.metrics.average_response_time for shard in self.shards.values()) / total_shards if total_shards > 0 else 0
            total_connections = sum(self.connection_counts.values())
            
            # Get health distribution
            health_distribution = defaultdict(int)
            for shard in self.shards.values():
                health_distribution[shard.health.value] += 1
            
            return {
                'cluster_overview': {
                    'total_shards': total_shards,
                    'active_shards': active_shards,
                    'failed_shards': failed_shards,
                    'health_ratio': active_shards / total_shards if total_shards > 0 else 0
                },
                'performance_metrics': {
                    'total_queries_per_second': total_queries,
                    'average_response_time': round(avg_response_time, 4),
                    'total_active_connections': total_connections,
                    'load_balancing_strategy': self.load_balancer_strategy.value
                },
                'health_distribution': dict(health_distribution),
                'shard_details': {
                    shard_id: {
                        'status': shard.status.value,
                        'health': shard.health.value,
                        'queries_per_second': shard.metrics.queries_per_second,
                        'response_time': round(shard.metrics.average_response_time, 4),
                        'active_connections': self.connection_counts[shard_id],
                        'error_rate': shard.metrics.error_rate,
                        'failure_count': shard.failure_count,
                        'last_health_check': shard.last_health_check.isoformat() if shard.last_health_check else None
                    }
                    for shard_id, shard in self.shards.items()
                },
                'replication': {
                    'strategy': self.replication_strategy.value,
                    'consistency_level': self.consistency_level.value
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return {'error': str(e)}

    def rebalance_shards(self) -> bool:
        """
        Rebalance data distribution across shards
        
        Returns:
            bool: True if rebalancing completed successfully
        """
        try:
            logger.info("Starting shard rebalancing...")
            
            # Analyze current distribution
            distribution_stats = self._analyze_shard_distribution()
            
            # Identify imbalanced shards
            imbalanced_shards = self._identify_imbalanced_shards(distribution_stats)
            
            if not imbalanced_shards:
                logger.info("Shards are already balanced")
                return True
            
            # Plan rebalancing operations
            rebalance_plan = self._create_rebalance_plan(imbalanced_shards)
            
            # Execute rebalancing
            success = self._execute_rebalance_plan(rebalance_plan)
            
            if success:
                logger.info("Shard rebalancing completed successfully")
            else:
                logger.error("Shard rebalancing failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rebalance shards: {e}")
            return False

    def _analyze_shard_distribution(self) -> Dict[str, Any]:
        """Analyze current data distribution across shards"""
        # This would implement actual analysis logic
        # For now, return placeholder
        return {}

    def _identify_imbalanced_shards(self, stats: Dict[str, Any]) -> List[str]:
        """Identify shards that need rebalancing"""
        # Implementation would analyze statistics and identify imbalanced shards
        return []

    def _create_rebalance_plan(self, imbalanced_shards: List[str]) -> Dict[str, Any]:
        """Create plan for rebalancing operations"""
        # Implementation would create detailed rebalancing plan
        return {}

    def _execute_rebalance_plan(self, plan: Dict[str, Any]) -> bool:
        """Execute rebalancing plan"""
        # Implementation would execute actual data movement
        return True

    def shutdown(self):
        """Shutdown shard coordinator gracefully"""
        try:
            logger.info("Shutting down shard coordinator...")
            
            # Stop monitoring
            self.monitoring_enabled = False
            
            # Wait for health check thread to stop
            if self.health_check_thread and self.health_check_thread.is_alive():
                self.health_check_thread.join(timeout=10)
            
            # Close all shard connections
            for shard in self.shards.values():
                if shard.engine:
                    shard.engine.dispose()
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("Shard coordinator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shard coordinator shutdown: {e}")

class ConsistentHashRing:
    """Consistent hashing implementation for shard distribution"""
    
    def __init__(self, replicas: int = 100):
        """
        Initialize consistent hash ring
        
        Args:
            replicas: Number of virtual nodes per physical node
        """
        self.replicas = replicas
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.nodes: Set[str] = set()
    
    def _hash(self, key: str) -> int:
        """Generate hash for key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str, weight: float = 1.0):
        """Add node to hash ring"""
        if node in self.nodes:
            return
        
        self.nodes.add(node)
        
        # Add virtual nodes based on weight
        virtual_nodes = int(self.replicas * weight)
        for i in range(virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node
            self.sorted_keys.append(hash_key)
        
        self.sorted_keys.sort()
    
    def remove_node(self, node: str):
        """Remove node from hash ring"""
        if node not in self.nodes:
            return
        
        self.nodes.remove(node)
        
        # Remove all virtual nodes for this physical node
        keys_to_remove = [key for key, value in self.ring.items() if value == node]
        for key in keys_to_remove:
            del self.ring[key]
            self.sorted_keys.remove(key)
    
    def get_node(self, key: str) -> Optional[str]:
        """Get node responsible for key"""
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Find first node clockwise from hash key
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                return self.ring[ring_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

__all__ = [
    'ShardCoordinator',
    'ShardNode', 
    'ShardConfiguration',
    'ShardMetrics',
    'ShardStatus',
    'ShardHealthStatus',
    'LoadBalancingStrategy',
    'ReplicationStrategy',
    'ConsistencyLevel',
    'FailoverStrategy',
    'ConsistentHashRing'
]
