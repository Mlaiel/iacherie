"""⚡ Gateway Performance Optimizer
==================================

Enterprise performance optimizer for payment gateway response optimization.
Handles response time optimization, connection pooling, batch processing,
and asynchronous processing support.

Features:
- Response time optimization
- Connection pooling and reuse
- Batch processing capabilities
- Asynchronous processing support
- Performance monitoring and tuning
- Resource utilization optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
import time
import statistics
from collections import defaultdict, deque
import aiohttp
import aioredis
from concurrent.futures import ThreadPoolExecutor
import psutil
import numpy as np

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of performance optimizations"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CONNECTION_POOL = "connection_pool"
    BATCH_PROCESSING = "batch_processing"
    CACHE_HIT_RATE = "cache_hit_rate"


class ProcessingMode(Enum):
    """Processing modes"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"
    PARALLEL = "parallel"


class ResourceType(Enum):
    """Types of system resources"""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    DISK = "disk"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    metric_id: str
    metric_type: OptimizationType
    value: float
    unit: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRule:
    """Performance optimization rule"""
    rule_id: str
    name: str
    condition: str  # Condition expression
    action: str  # Action to take
    threshold: float
    optimization_type: OptimizationType
    is_active: bool = True
    priority: int = 100
    cooldown_seconds: int = 300
    last_triggered: Optional[datetime] = None


@dataclass
class ConnectionPool:
    """Connection pool configuration"""
    pool_id: str
    target_host: str
    pool_size: int
    max_connections: int
    timeout_seconds: int
    keep_alive: bool
    active_connections: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BatchOperation:
    """Batch operation definition"""
    batch_id: str
    operation_type: str
    items: List[Any]
    batch_size: int
    processing_mode: ProcessingMode
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0


class GatewayPerformanceOptimizer:
    """Enterprise performance optimizer for payment gateway"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.performance_metrics: deque = deque(maxlen=10000)
        self.batch_operations: Dict[str, BatchOperation] = {}
        self.thread_pool = None
        self.is_initialized = False
        
        # Performance configuration
        self.optimization_interval = config.get('optimization_interval', 60)
        self.metrics_collection_interval = config.get('metrics_collection_interval', 30)
        self.max_threads = config.get('max_threads', 10)
        self.batch_size = config.get('default_batch_size', 100)
        self.connection_timeout = config.get('connection_timeout', 30)
        
        # Performance targets
        self.performance_targets = config.get('performance_targets', {
            'max_response_time': 2000,  # milliseconds
            'min_throughput': 1000,     # requests per minute
            'max_cpu_usage': 80,        # percentage
            'max_memory_usage': 80,     # percentage
            'min_cache_hit_rate': 80    # percentage
        })
        
        # Optimization strategies
        self.optimization_strategies = {
            OptimizationType.RESPONSE_TIME: self._optimize_response_time,
            OptimizationType.THROUGHPUT: self._optimize_throughput,
            OptimizationType.MEMORY_USAGE: self._optimize_memory_usage,
            OptimizationType.CPU_USAGE: self._optimize_cpu_usage,
            OptimizationType.CONNECTION_POOL: self._optimize_connection_pool,
            OptimizationType.BATCH_PROCESSING: self._optimize_batch_processing,
            OptimizationType.CACHE_HIT_RATE: self._optimize_cache_hit_rate
        }
        
        # Current optimization state
        self.optimization_state = {
            'connection_pool_size': config.get('initial_pool_size', 20),
            'batch_processing_enabled': True,
            'async_processing_enabled': True,
            'cache_enabled': True,
            'compression_enabled': False,
            'keep_alive_enabled': True
        }
        
    async def initialize(self):
        """Initialize the performance optimizer"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = aioredis.from_url(
                f"redis://{redis_config.get('host', 'localhost')}:"
                f"{redis_config.get('port', 6379)}"
            )
            
            # Initialize thread pool for CPU-bound tasks
            self.thread_pool = ThreadPoolExecutor(max_workers=self.max_threads)
            
            # Load existing configuration
            await self._load_configuration()
            
            # Initialize default optimization rules
            await self._initialize_default_rules()
            
            # Initialize connection pools
            await self._initialize_connection_pools()
            
            # Start monitoring and optimization tasks
            asyncio.create_task(self._collect_performance_metrics())
            asyncio.create_task(self._run_optimization_engine())
            asyncio.create_task(self._monitor_system_resources())
            asyncio.create_task(self._process_batch_operations())
            
            self.is_initialized = True
            logger.info("Gateway Performance Optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gateway Performance Optimizer: {e}")
            raise
    
    async def _load_configuration(self):
        """Load existing configuration from storage"""
        try:
            # Load optimization rules
            rules_data = await self.redis_client.get("optimizer:rules")
            if rules_data:
                rules_dict = json.loads(rules_data.decode())
                for rule_id, rule_info in rules_dict.items():
                    self.optimization_rules[rule_id] = OptimizationRule(
                        rule_id=rule_info['rule_id'],
                        name=rule_info['name'],
                        condition=rule_info['condition'],
                        action=rule_info['action'],
                        threshold=rule_info['threshold'],
                        optimization_type=OptimizationType(rule_info['optimization_type']),
                        is_active=rule_info['is_active'],
                        priority=rule_info.get('priority', 100),
                        cooldown_seconds=rule_info.get('cooldown_seconds', 300),
                        last_triggered=datetime.fromisoformat(rule_info['last_triggered']) if rule_info.get('last_triggered') else None
                    )
            
            # Load connection pools
            pools_data = await self.redis_client.get("optimizer:pools")
            if pools_data:
                pools_dict = json.loads(pools_data.decode())
                for pool_id, pool_info in pools_dict.items():
                    self.connection_pools[pool_id] = ConnectionPool(
                        pool_id=pool_info['pool_id'],
                        target_host=pool_info['target_host'],
                        pool_size=pool_info['pool_size'],
                        max_connections=pool_info['max_connections'],
                        timeout_seconds=pool_info['timeout_seconds'],
                        keep_alive=pool_info['keep_alive'],
                        active_connections=pool_info.get('active_connections', 0),
                        total_requests=pool_info.get('total_requests', 0),
                        avg_response_time=pool_info.get('avg_response_time', 0.0),
                        created_at=datetime.fromisoformat(pool_info['created_at'])
                    )
                    
            logger.info("Performance optimizer configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load optimizer configuration: {e}")
    
    async def _initialize_default_rules(self):
        """Initialize default optimization rules"""
        try:
            default_rules = [
                {
                    'rule_id': 'high_response_time',
                    'name': 'High Response Time Optimization',
                    'condition': 'avg_response_time > threshold',
                    'action': 'optimize_response_time',
                    'threshold': 2000,  # 2 seconds
                    'optimization_type': OptimizationType.RESPONSE_TIME
                },
                {
                    'rule_id': 'low_throughput',
                    'name': 'Low Throughput Optimization',
                    'condition': 'requests_per_minute < threshold',
                    'action': 'optimize_throughput',
                    'threshold': 1000,
                    'optimization_type': OptimizationType.THROUGHPUT
                },
                {
                    'rule_id': 'high_cpu_usage',
                    'name': 'High CPU Usage Optimization',
                    'condition': 'cpu_usage > threshold',
                    'action': 'optimize_cpu_usage',
                    'threshold': 80,
                    'optimization_type': OptimizationType.CPU_USAGE
                },
                {
                    'rule_id': 'high_memory_usage',
                    'name': 'High Memory Usage Optimization',
                    'condition': 'memory_usage > threshold',
                    'action': 'optimize_memory_usage',
                    'threshold': 80,
                    'optimization_type': OptimizationType.MEMORY_USAGE
                },
                {
                    'rule_id': 'low_cache_hit_rate',
                    'name': 'Low Cache Hit Rate Optimization',
                    'condition': 'cache_hit_rate < threshold',
                    'action': 'optimize_cache_hit_rate',
                    'threshold': 80,
                    'optimization_type': OptimizationType.CACHE_HIT_RATE
                }
            ]
            
            for rule_config in default_rules:
                if rule_config['rule_id'] not in self.optimization_rules:
                    self.optimization_rules[rule_config['rule_id']] = OptimizationRule(
                        rule_id=rule_config['rule_id'],
                        name=rule_config['name'],
                        condition=rule_config['condition'],
                        action=rule_config['action'],
                        threshold=rule_config['threshold'],
                        optimization_type=rule_config['optimization_type']
                    )
            
            await self._save_optimization_rules()
            
        except Exception as e:
            logger.error(f"Failed to initialize default rules: {e}")
    
    async def _initialize_connection_pools(self):
        """Initialize connection pools for external services"""
        try:
            default_pools = [
                {
                    'pool_id': 'stripe_pool',
                    'target_host': 'api.stripe.com',
                    'pool_size': 20,
                    'max_connections': 50
                },
                {
                    'pool_id': 'paypal_pool',
                    'target_host': 'api.paypal.com',
                    'pool_size': 15,
                    'max_connections': 40
                },
                {
                    'pool_id': 'wise_pool',
                    'target_host': 'api.wise.com',
                    'pool_size': 10,
                    'max_connections': 30
                },
                {
                    'pool_id': 'redis_pool',
                    'target_host': 'localhost:6379',
                    'pool_size': 25,
                    'max_connections': 100
                }
            ]
            
            for pool_config in default_pools:
                if pool_config['pool_id'] not in self.connection_pools:
                    self.connection_pools[pool_config['pool_id']] = ConnectionPool(
                        pool_id=pool_config['pool_id'],
                        target_host=pool_config['target_host'],
                        pool_size=pool_config['pool_size'],
                        max_connections=pool_config['max_connections'],
                        timeout_seconds=self.connection_timeout,
                        keep_alive=True
                    )
            
            await self._save_connection_pools()
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pools: {e}")
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics continuously"""
        while True:
            try:
                current_time = datetime.now()
                
                # Collect system metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                disk_usage = psutil.disk_usage('/').percent
                network_io = psutil.net_io_counters()
                
                # Store system metrics
                await self._store_metric(
                    OptimizationType.CPU_USAGE,
                    cpu_usage,
                    "percent",
                    "system"
                )
                
                await self._store_metric(
                    OptimizationType.MEMORY_USAGE,
                    memory_usage,
                    "percent",
                    "system"
                )
                
                # Collect application metrics from Redis
                try:
                    # Response time metrics
                    response_times = await self.redis_client.lrange("metrics:response_times", 0, -1)
                    if response_times:
                        times = [float(rt.decode()) for rt in response_times[-100:]]  # Last 100
                        avg_response_time = statistics.mean(times)
                        
                        await self._store_metric(
                            OptimizationType.RESPONSE_TIME,
                            avg_response_time,
                            "milliseconds",
                            "application"
                        )
                    
                    # Throughput metrics
                    throughput = await self.redis_client.get("metrics:requests_per_minute")
                    if throughput:
                        await self._store_metric(
                            OptimizationType.THROUGHPUT,
                            float(throughput.decode()),
                            "requests/minute",
                            "application"
                        )
                    
                    # Cache hit rate
                    cache_hits = await self.redis_client.get("metrics:cache_hits")
                    cache_misses = await self.redis_client.get("metrics:cache_misses")
                    
                    if cache_hits and cache_misses:
                        hits = int(cache_hits.decode())
                        misses = int(cache_misses.decode())
                        total = hits + misses
                        
                        if total > 0:
                            hit_rate = (hits / total) * 100
                            await self._store_metric(
                                OptimizationType.CACHE_HIT_RATE,
                                hit_rate,
                                "percent",
                                "cache"
                            )
                    
                except Exception as e:
                    logger.debug(f"Error collecting Redis metrics: {e}")
                
                await asyncio.sleep(self.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"Error in performance metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def _store_metric(
        self,
        metric_type: OptimizationType,
        value: float,
        unit: str,
        source: str
    ):
        """Store performance metric"""
        try:
            metric = PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=metric_type,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                source=source
            )
            
            self.performance_metrics.append(metric)
            
            # Store in Redis for persistence
            await self.redis_client.lpush(
                f"metrics:{metric_type.value}",
                json.dumps({
                    'value': value,
                    'unit': unit,
                    'timestamp': metric.timestamp.isoformat(),
                    'source': source
                })
            )
            
            # Keep only last 1000 entries per metric type
            await self.redis_client.ltrim(f"metrics:{metric_type.value}", 0, 999)
            
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    async def _run_optimization_engine(self):
        """Run the main optimization engine"""
        while True:
            try:
                # Evaluate optimization rules
                for rule in self.optimization_rules.values():
                    if not rule.is_active:
                        continue
                    
                    # Check cooldown
                    if (rule.last_triggered and 
                        (datetime.now() - rule.last_triggered).total_seconds() < rule.cooldown_seconds):
                        continue
                    
                    # Evaluate condition
                    if await self._evaluate_rule_condition(rule):
                        # Execute optimization
                        await self._execute_optimization(rule)
                        rule.last_triggered = datetime.now()
                
                await asyncio.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in optimization engine: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_rule_condition(self, rule: OptimizationRule) -> bool:
        """Evaluate if optimization rule condition is met"""
        try:
            # Get recent metrics for the rule's optimization type
            recent_metrics = [
                m for m in self.performance_metrics
                if (m.metric_type == rule.optimization_type and
                    (datetime.now() - m.timestamp).total_seconds() < 300)  # Last 5 minutes
            ]
            
            if not recent_metrics:
                return False
            
            # Calculate average value
            avg_value = statistics.mean([m.value for m in recent_metrics])
            
            # Evaluate condition (simplified evaluation)
            if 'avg_response_time > threshold' in rule.condition:
                return avg_value > rule.threshold
            elif 'requests_per_minute < threshold' in rule.condition:
                return avg_value < rule.threshold
            elif 'cpu_usage > threshold' in rule.condition:
                return avg_value > rule.threshold
            elif 'memory_usage > threshold' in rule.condition:
                return avg_value > rule.threshold
            elif 'cache_hit_rate < threshold' in rule.condition:
                return avg_value < rule.threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating rule condition: {e}")
            return False
    
    async def _execute_optimization(self, rule: OptimizationRule):
        """Execute optimization based on rule"""
        try:
            optimization_type = rule.optimization_type
            
            if optimization_type in self.optimization_strategies:
                await self.optimization_strategies[optimization_type](rule)
                logger.info(f"Executed optimization: {rule.name}")
            else:
                logger.warning(f"No optimization strategy for type: {optimization_type}")
                
        except Exception as e:
            logger.error(f"Error executing optimization {rule.name}: {e}")
    
    async def _optimize_response_time(self, rule: OptimizationRule):
        """Optimize response time"""
        try:
            optimizations_applied = []
            
            # Enable compression if not already enabled
            if not self.optimization_state['compression_enabled']:
                self.optimization_state['compression_enabled'] = True
                optimizations_applied.append("Enabled compression")
            
            # Increase connection pool sizes
            for pool in self.connection_pools.values():
                if pool.pool_size < pool.max_connections * 0.8:
                    new_size = min(pool.pool_size + 5, pool.max_connections)
                    pool.pool_size = new_size
                    optimizations_applied.append(f"Increased {pool.pool_id} pool size to {new_size}")
            
            # Enable keep-alive if not enabled
            for pool in self.connection_pools.values():
                if not pool.keep_alive:
                    pool.keep_alive = True
                    optimizations_applied.append(f"Enabled keep-alive for {pool.pool_id}")
            
            if optimizations_applied:
                await self._save_connection_pools()
                logger.info(f"Response time optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in response time optimization: {e}")
    
    async def _optimize_throughput(self, rule: OptimizationRule):
        """Optimize throughput"""
        try:
            optimizations_applied = []
            
            # Enable batch processing if not enabled
            if not self.optimization_state['batch_processing_enabled']:
                self.optimization_state['batch_processing_enabled'] = True
                optimizations_applied.append("Enabled batch processing")
            
            # Enable async processing if not enabled
            if not self.optimization_state['async_processing_enabled']:
                self.optimization_state['async_processing_enabled'] = True
                optimizations_applied.append("Enabled async processing")
            
            # Increase connection pool sizes for throughput
            for pool in self.connection_pools.values():
                if pool.pool_size < pool.max_connections:
                    new_size = min(pool.pool_size + 10, pool.max_connections)
                    pool.pool_size = new_size
                    optimizations_applied.append(f"Increased {pool.pool_id} pool size to {new_size}")
            
            if optimizations_applied:
                await self._save_connection_pools()
                logger.info(f"Throughput optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in throughput optimization: {e}")
    
    async def _optimize_memory_usage(self, rule: OptimizationRule):
        """Optimize memory usage"""
        try:
            optimizations_applied = []
            
            # Reduce connection pool sizes
            for pool in self.connection_pools.values():
                if pool.pool_size > 5:
                    new_size = max(pool.pool_size - 5, 5)
                    pool.pool_size = new_size
                    optimizations_applied.append(f"Reduced {pool.pool_id} pool size to {new_size}")
            
            # Clear old metrics
            cutoff_time = datetime.now() - timedelta(hours=1)
            original_size = len(self.performance_metrics)
            
            # Keep only recent metrics
            self.performance_metrics = deque(
                [m for m in self.performance_metrics if m.timestamp > cutoff_time],
                maxlen=10000
            )
            
            cleared_count = original_size - len(self.performance_metrics)
            if cleared_count > 0:
                optimizations_applied.append(f"Cleared {cleared_count} old metrics")
            
            if optimizations_applied:
                await self._save_connection_pools()
                logger.info(f"Memory optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in memory optimization: {e}")
    
    async def _optimize_cpu_usage(self, rule: OptimizationRule):
        """Optimize CPU usage"""
        try:
            optimizations_applied = []
            
            # Reduce thread pool size if high CPU usage
            if self.thread_pool._max_workers > 5:
                new_max_workers = max(self.thread_pool._max_workers - 2, 5)
                # Note: ThreadPoolExecutor doesn't support dynamic resizing
                # This would require recreating the pool in a real implementation
                optimizations_applied.append(f"Would reduce thread pool to {new_max_workers}")
            
            # Enable batch processing to reduce CPU overhead
            if not self.optimization_state['batch_processing_enabled']:
                self.optimization_state['batch_processing_enabled'] = True
                optimizations_applied.append("Enabled batch processing to reduce CPU overhead")
            
            if optimizations_applied:
                logger.info(f"CPU optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in CPU optimization: {e}")
    
    async def _optimize_connection_pool(self, rule: OptimizationRule):
        """Optimize connection pool configuration"""
        try:
            optimizations_applied = []
            
            for pool in self.connection_pools.values():
                # Analyze pool utilization
                if pool.total_requests > 0:
                    utilization = pool.active_connections / pool.pool_size
                    
                    # Increase pool size if high utilization
                    if utilization > 0.8 and pool.pool_size < pool.max_connections:
                        new_size = min(pool.pool_size + 5, pool.max_connections)
                        pool.pool_size = new_size
                        optimizations_applied.append(f"Increased {pool.pool_id} pool size to {new_size}")
                    
                    # Decrease pool size if low utilization
                    elif utilization < 0.3 and pool.pool_size > 5:
                        new_size = max(pool.pool_size - 2, 5)
                        pool.pool_size = new_size
                        optimizations_applied.append(f"Decreased {pool.pool_id} pool size to {new_size}")
            
            if optimizations_applied:
                await self._save_connection_pools()
                logger.info(f"Connection pool optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in connection pool optimization: {e}")
    
    async def _optimize_batch_processing(self, rule: OptimizationRule):
        """Optimize batch processing"""
        try:
            optimizations_applied = []
            
            # Enable batch processing if not enabled
            if not self.optimization_state['batch_processing_enabled']:
                self.optimization_state['batch_processing_enabled'] = True
                optimizations_applied.append("Enabled batch processing")
            
            # Adjust batch size based on current performance
            current_batch_size = self.batch_size
            
            # Get recent response time metrics
            recent_metrics = [
                m for m in self.performance_metrics
                if (m.metric_type == OptimizationType.RESPONSE_TIME and
                    (datetime.now() - m.timestamp).total_seconds() < 300)
            ]
            
            if recent_metrics:
                avg_response_time = statistics.mean([m.value for m in recent_metrics])
                
                # Increase batch size if response time is good
                if avg_response_time < 1000 and current_batch_size < 200:
                    self.batch_size = min(current_batch_size + 20, 200)
                    optimizations_applied.append(f"Increased batch size to {self.batch_size}")
                
                # Decrease batch size if response time is poor
                elif avg_response_time > 3000 and current_batch_size > 50:
                    self.batch_size = max(current_batch_size - 20, 50)
                    optimizations_applied.append(f"Decreased batch size to {self.batch_size}")
            
            if optimizations_applied:
                logger.info(f"Batch processing optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in batch processing optimization: {e}")
    
    async def _optimize_cache_hit_rate(self, rule: OptimizationRule):
        """Optimize cache hit rate"""
        try:
            optimizations_applied = []
            
            # Enable cache if not enabled
            if not self.optimization_state['cache_enabled']:
                self.optimization_state['cache_enabled'] = True
                optimizations_applied.append("Enabled caching")
            
            # Send cache warming signal
            await self.redis_client.publish("cache:warm", "trigger_warming")
            optimizations_applied.append("Triggered cache warming")
            
            # Adjust cache TTL values (would interact with cache system)
            await self.redis_client.publish("cache:optimize", "increase_ttl")
            optimizations_applied.append("Increased cache TTL values")
            
            if optimizations_applied:
                logger.info(f"Cache optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error in cache optimization: {e}")
    
    async def _monitor_system_resources(self):
        """Monitor system resources continuously"""
        while True:
            try:
                # Get system resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage('/')
                
                # Check for resource exhaustion
                if cpu_percent > 90:
                    logger.warning(f"High CPU usage detected: {cpu_percent}%")
                    await self._handle_resource_exhaustion(ResourceType.CPU, cpu_percent)
                
                if memory_info.percent > 90:
                    logger.warning(f"High memory usage detected: {memory_info.percent}%")
                    await self._handle_resource_exhaustion(ResourceType.MEMORY, memory_info.percent)
                
                if disk_info.percent > 90:
                    logger.warning(f"High disk usage detected: {disk_info.percent}%")
                    await self._handle_resource_exhaustion(ResourceType.DISK, disk_info.percent)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system resource monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _handle_resource_exhaustion(self, resource_type: ResourceType, usage: float):
        """Handle resource exhaustion scenarios"""
        try:
            if resource_type == ResourceType.CPU:
                # Reduce processing load
                self.optimization_state['batch_processing_enabled'] = True
                # Reduce connection pool sizes
                for pool in self.connection_pools.values():
                    pool.pool_size = max(pool.pool_size - 3, 5)
                
            elif resource_type == ResourceType.MEMORY:
                # Clear caches and reduce memory usage
                await self.redis_client.publish("cache:clear", "emergency_clear")
                # Clear old metrics
                self.performance_metrics.clear()
                
            elif resource_type == ResourceType.DISK:
                # Clean up temporary files and logs
                await self.redis_client.publish("cleanup:disk", "emergency_cleanup")
            
            logger.info(f"Applied emergency optimization for {resource_type.value} usage: {usage}%")
            
        except Exception as e:
            logger.error(f"Error handling resource exhaustion: {e}")
    
    async def _process_batch_operations(self):
        """Process batch operations queue"""
        while True:
            try:
                if not self.optimization_state['batch_processing_enabled']:
                    await asyncio.sleep(10)
                    continue
                
                # Get batch operations from queue
                batch_data = await self.redis_client.brpop("optimizer:batch_queue", timeout=10)
                
                if batch_data:
                    batch_info = json.loads(batch_data[1].decode())
                    await self._execute_batch_operation(batch_info)
                
            except Exception as e:
                logger.error(f"Error in batch operation processing: {e}")
                await asyncio.sleep(10)
    
    async def _execute_batch_operation(self, batch_info: Dict[str, Any]):
        """Execute a batch operation"""
        try:
            batch_id = batch_info['batch_id']
            operation_type = batch_info['operation_type']
            items = batch_info['items']
            
            # Create batch operation record
            batch_op = BatchOperation(
                batch_id=batch_id,
                operation_type=operation_type,
                items=items,
                batch_size=len(items),
                processing_mode=ProcessingMode.BATCH,
                created_at=datetime.now(),
                started_at=datetime.now()
            )
            
            self.batch_operations[batch_id] = batch_op
            
            # Process items in batches
            chunk_size = min(self.batch_size, len(items))
            
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                
                try:
                    # Process chunk (simplified - would call actual processing function)
                    await self._process_batch_chunk(operation_type, chunk)
                    batch_op.success_count += len(chunk)
                    
                except Exception as e:
                    logger.error(f"Error processing batch chunk: {e}")
                    batch_op.failure_count += len(chunk)
            
            batch_op.completed_at = datetime.now()
            
            logger.info(f"Completed batch operation {batch_id}: "
                       f"{batch_op.success_count} success, {batch_op.failure_count} failed")
            
        except Exception as e:
            logger.error(f"Error executing batch operation: {e}")
    
    async def _process_batch_chunk(self, operation_type: str, chunk: List[Any]):
        """Process a chunk of batch operations"""
        try:
            # Simulate batch processing based on operation type
            if operation_type == "payment_validation":
                # Simulate validation processing
                await asyncio.sleep(0.1)  # Simulate processing time
                
            elif operation_type == "fraud_check":
                # Simulate fraud checking
                await asyncio.sleep(0.2)
                
            elif operation_type == "notification_send":
                # Simulate notification sending
                await asyncio.sleep(0.05)
                
            else:
                # Default processing
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error processing batch chunk: {e}")
            raise
    
    async def create_batch_operation(
        self,
        operation_type: str,
        items: List[Any],
        processing_mode: ProcessingMode = ProcessingMode.BATCH
    ) -> str:
        """Create a new batch operation"""
        try:
            batch_id = str(uuid.uuid4())
            
            batch_info = {
                'batch_id': batch_id,
                'operation_type': operation_type,
                'items': items,
                'processing_mode': processing_mode.value,
                'created_at': datetime.now().isoformat()
            }
            
            # Add to processing queue
            await self.redis_client.lpush(
                "optimizer:batch_queue",
                json.dumps(batch_info)
            )
            
            logger.info(f"Created batch operation {batch_id} with {len(items)} items")
            return batch_id
            
        except Exception as e:
            logger.error(f"Failed to create batch operation: {e}")
            raise
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            current_time = datetime.now()
            
            # Calculate metrics for different time periods
            metrics_1h = [m for m in self.performance_metrics 
                         if (current_time - m.timestamp).total_seconds() < 3600]
            metrics_24h = [m for m in self.performance_metrics 
                          if (current_time - m.timestamp).total_seconds() < 86400]
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in metrics_1h:
                metrics_by_type[metric.metric_type.value].append(metric.value)
            
            # Calculate statistics
            performance_stats = {}
            for metric_type, values in metrics_by_type.items():
                if values:
                    performance_stats[metric_type] = {
                        'current': values[-1] if values else 0,
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'median': statistics.median(values),
                        'count': len(values)
                    }
            
            # Connection pool statistics
            pool_stats = {}
            for pool_id, pool in self.connection_pools.items():
                pool_stats[pool_id] = {
                    'pool_size': pool.pool_size,
                    'max_connections': pool.max_connections,
                    'active_connections': pool.active_connections,
                    'total_requests': pool.total_requests,
                    'avg_response_time': pool.avg_response_time,
                    'utilization': (pool.active_connections / pool.pool_size * 100) if pool.pool_size > 0 else 0
                }
            
            # Optimization state
            optimization_summary = {
                'total_rules': len(self.optimization_rules),
                'active_rules': len([r for r in self.optimization_rules.values() if r.is_active]),
                'recent_optimizations': len([
                    r for r in self.optimization_rules.values()
                    if r.last_triggered and (current_time - r.last_triggered).total_seconds() < 3600
                ]),
                'current_state': self.optimization_state
            }
            
            # Batch operations statistics
            active_batches = len([b for b in self.batch_operations.values() if not b.completed_at])
            completed_batches = len([b for b in self.batch_operations.values() if b.completed_at])
            
            return {
                'report_generated_at': current_time.isoformat(),
                'performance_stats': performance_stats,
                'connection_pools': pool_stats,
                'optimization_summary': optimization_summary,
                'batch_operations': {
                    'active_batches': active_batches,
                    'completed_batches': completed_batches,
                    'current_batch_size': self.batch_size
                },
                'system_resources': {
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent
                },
                'performance_targets': self.performance_targets
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    async def apply_manual_optimization(
        self,
        optimization_type: OptimizationType,
        parameters: Dict[str, Any]
    ) -> bool:
        """Apply manual optimization"""
        try:
            if optimization_type == OptimizationType.CONNECTION_POOL:
                # Update connection pool settings
                pool_id = parameters.get('pool_id')
                new_size = parameters.get('pool_size')
                
                if pool_id in self.connection_pools and new_size:
                    self.connection_pools[pool_id].pool_size = new_size
                    await self._save_connection_pools()
                    logger.info(f"Manual optimization: Updated {pool_id} pool size to {new_size}")
                    return True
                    
            elif optimization_type == OptimizationType.BATCH_PROCESSING:
                # Update batch processing settings
                new_batch_size = parameters.get('batch_size')
                if new_batch_size:
                    self.batch_size = new_batch_size
                    logger.info(f"Manual optimization: Updated batch size to {new_batch_size}")
                    return True
            
            # Add more manual optimization types as needed
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to apply manual optimization: {e}")
            return False
    
    async def _save_optimization_rules(self):
        """Save optimization rules to storage"""
        try:
            rules_dict = {}
            for rule_id, rule in self.optimization_rules.items():
                rules_dict[rule_id] = {
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'condition': rule.condition,
                    'action': rule.action,
                    'threshold': rule.threshold,
                    'optimization_type': rule.optimization_type.value,
                    'is_active': rule.is_active,
                    'priority': rule.priority,
                    'cooldown_seconds': rule.cooldown_seconds,
                    'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
                }
            
            await self.redis_client.set(
                "optimizer:rules",
                json.dumps(rules_dict),
                ex=86400 * 7  # 1 week expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save optimization rules: {e}")
    
    async def _save_connection_pools(self):
        """Save connection pools to storage"""
        try:
            pools_dict = {}
            for pool_id, pool in self.connection_pools.items():
                pools_dict[pool_id] = {
                    'pool_id': pool.pool_id,
                    'target_host': pool.target_host,
                    'pool_size': pool.pool_size,
                    'max_connections': pool.max_connections,
                    'timeout_seconds': pool.timeout_seconds,
                    'keep_alive': pool.keep_alive,
                    'active_connections': pool.active_connections,
                    'total_requests': pool.total_requests,
                    'avg_response_time': pool.avg_response_time,
                    'created_at': pool.created_at.isoformat()
                }
            
            await self.redis_client.set(
                "optimizer:pools",
                json.dumps(pools_dict),
                ex=86400  # 1 day expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save connection pools: {e}")
    
    async def close(self):
        """Close the optimizer and cleanup resources"""
        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Gateway Performance Optimizer closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close Gateway Performance Optimizer: {e}")