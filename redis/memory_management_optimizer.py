"""
Memory Management Optimizer for Redis Enterprise  
DBA Implementation - Intelligent Memory Optimization and Management

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
import gc
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
from config.core.redis import RedisSettings

logger = logging.getLogger(__name__)

class MemoryOptimizationType(Enum):
    """Types of memory optimization"""
    EVICTION_POLICY = "eviction_policy"
    COMPRESSION = "compression"
    FRAGMENTATION = "fragmentation"
    KEY_EXPIRATION = "key_expiration"
    DATA_STRUCTURE = "data_structure"
    MEMORY_MAPPING = "memory_mapping"

class DataType(Enum):
    """Redis data types for optimization"""
    STRING = "string"
    HASH = "hash"
    LIST = "list"
    SET = "set"
    ZSET = "zset"
    STREAM = "stream"
    BITMAP = "bitmap"
    HYPERLOGLOG = "hyperloglog"

@dataclass
class MemoryUsageAnalysis:
    """Memory usage analysis result"""
    total_memory: int
    used_memory: int
    peak_memory: int
    fragmentation_ratio: float
    evicted_keys: int
    expired_keys: int
    memory_efficiency: float
    optimization_potential: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass 
class DataStructureAnalysis:
    """Analysis of data structure memory usage"""
    data_type: DataType
    key_count: int
    total_memory: int
    avg_memory_per_key: float
    compression_ratio: float
    optimization_suggestions: List[str] = field(default_factory=list)

@dataclass
class MemoryOptimizationRule:
    """Memory optimization rule"""
    rule_id: str
    name: str
    optimization_type: MemoryOptimizationType
    trigger_conditions: List[str]
    optimization_actions: Dict[str, Any]
    expected_memory_savings: float  # Percentage
    priority: int = 50  # 1-100, higher = more important
    enabled: bool = True
    last_applied: Optional[datetime] = None
    success_count: int = 0
    total_applications: int = 0

@dataclass
class FragmentationInfo:
    """Memory fragmentation information"""
    fragmentation_ratio: float
    fragmented_bytes: int
    defrag_running: bool
    defrag_progress: float
    last_defrag: Optional[datetime] = None
    defrag_count: int = 0

class MemoryManagementOptimizer:
    """
    Intelligent memory management optimizer for Redis enterprise
    DBA implementation with advanced memory optimization strategies
    """
    
    def __init__(self, redis_settings -> None: RedisSettings) -> None:
        self.redis_settings = redis_settings
        self.redis_client: Optional[redis.Redis] = None
        
        # Memory management state
        self.memory_analysis_history: List[MemoryUsageAnalysis] = []
        self.optimization_rules: Dict[str, MemoryOptimizationRule] = {}
        self.data_structure_analysis: Dict[DataType, DataStructureAnalysis] = {}
        self.fragmentation_info = FragmentationInfo(0.0, 0, False, 0.0)
        
        # Optimization settings
        self.memory_threshold_warning = 80.0  # %
        self.memory_threshold_critical = 90.0  # %
        self.fragmentation_threshold = 1.5
        self.optimization_interval = 300  # 5 minutes
        self.analysis_interval = 60  # 1 minute
        self.max_memory_samples = 1440  # 24 hours at 1-minute intervals
        
        # Redis configuration optimization
        self.optimal_configs: Dict[str, Any] = {}
        self.config_baseline: Dict[str, Any] = {}
        
        # Redis keys for persistence
        self.memory_analysis_key = "ainflue:memory:analysis"
        self.optimization_rules_key = "ainflue:memory:rules"
        self.fragmentation_key = "ainflue:memory:fragmentation"
        self.config_optimization_key = "ainflue:memory:config"
        
        # Background tasks
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Memory optimization strategies
        self.compression_enabled = True
        self.auto_defrag_enabled = True
        self.intelligent_eviction = True
        self.key_expiration_optimization = True
        
        # Initialize optimization rules
        self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self) -> None:
        """Initialize memory optimization rules"""
        try:
            # High memory usage rule
            self.optimization_rules["high_memory_usage"] = MemoryOptimizationRule(
                rule_id="high_memory_usage",
                name="High Memory Usage Optimization",
                optimization_type=MemoryOptimizationType.EVICTION_POLICY,
                trigger_conditions=[
                    "memory_usage > 80",
                    "trend(memory_usage, 5min) > 0"
                ],
                optimization_actions={
                    "maxmemory-policy": "allkeys-lru",
                    "maxmemory-samples": "10"
                },
                expected_memory_savings=15.0,
                priority=90
            )
            
            # Fragmentation optimization rule
            self.optimization_rules["high_fragmentation"] = MemoryOptimizationRule(
                rule_id="high_fragmentation",
                name="Memory Fragmentation Optimization",
                optimization_type=MemoryOptimizationType.FRAGMENTATION,
                trigger_conditions=[
                    "fragmentation_ratio > 1.5",
                    "fragmented_bytes > 100MB"
                ],
                optimization_actions={
                    "activedefrag": "yes",
                    "active-defrag-ignore-bytes": "100mb",
                    "active-defrag-threshold-lower": "10"
                },
                expected_memory_savings=20.0,
                priority=80
            )
            
            # Compression optimization rule
            self.optimization_rules["compression_optimization"] = MemoryOptimizationRule(
                rule_id="compression_optimization",
                name="Data Compression Optimization",
                optimization_type=MemoryOptimizationType.COMPRESSION,
                trigger_conditions=[
                    "memory_usage > 60",
                    "avg_value_size > 1KB"
                ],
                optimization_actions={
                    "hash-max-ziplist-entries": "512",
                    "hash-max-ziplist-value": "64",
                    "list-max-ziplist-size": "-2",
                    "set-max-intset-entries": "512"
                },
                expected_memory_savings=25.0,
                priority=70
            )
            
            # Key expiration optimization rule
            self.optimization_rules["key_expiration"] = MemoryOptimizationRule(
                rule_id="key_expiration",
                name="Key Expiration Optimization",
                optimization_type=MemoryOptimizationType.KEY_EXPIRATION,
                trigger_conditions=[
                    "memory_usage > 75",
                    "keys_without_ttl > 50%"
                ],
                optimization_actions={
                    "default_ttl": "3600",
                    "maxmemory-policy": "volatile-lru"
                },
                expected_memory_savings=30.0,
                priority=75
            )
            
        except Exception as e:
            logger.error(f"Error initializing optimization rules: {e}")
    
    async def initialize(self) -> None:
        """Initialize the memory management optimizer"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_settings.redis_dsn,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.redis_settings.redis_max_connections
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load existing data
            await self._load_optimization_history()
            await self._capture_config_baseline()
            
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._memory_analyzer()),
                asyncio.create_task(self._optimization_engine()),
                asyncio.create_task(self._fragmentation_monitor()),
                asyncio.create_task(self._data_structure_analyzer()),
                asyncio.create_task(self._memory_cleaner())
            ]
            
            logger.info("Memory Management Optimizer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Memory Management Optimizer: {e}")
            raise
    
    async def _memory_analyzer(self) -> None:
        """Continuous memory analysis"""
        while self._running:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                # Collect memory metrics
                analysis = await self._analyze_memory_usage()
                
                # Store analysis
                self.memory_analysis_history.append(analysis)
                
                # Keep only recent samples
                if len(self.memory_analysis_history) > self.max_memory_samples:
                    self.memory_analysis_history = self.memory_analysis_history[-self.max_memory_samples:]
                
                # Store in Redis
                await self._store_memory_analysis(analysis)
                
                # Check for immediate optimization needs
                if analysis.memory_efficiency < 0.6:  # Poor efficiency
                    await self._trigger_immediate_optimization(analysis)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in memory analyzer: {e}")
                await asyncio.sleep(30)
    
    async def _analyze_memory_usage(self) -> MemoryUsageAnalysis:
        """Analyze current memory usage"""
        try:
            # Get memory info from Redis
            info = await self.redis_client.info('memory')
            stats = await self.redis_client.info('stats')
            
            # Calculate memory metrics
            used_memory = info.get('used_memory', 0)
            used_memory_peak = info.get('used_memory_peak', 0)
            maxmemory = info.get('maxmemory', 0)
            
            # If maxmemory is 0, estimate based on system
            if maxmemory == 0:
                maxmemory = 8 * 1024 * 1024 * 1024  # Default 8GB
            
            memory_usage_pct = (used_memory / maxmemory) * 100
            fragmentation_ratio = info.get('mem_fragmentation_ratio', 1.0)
            
            # Get eviction/expiration stats
            evicted_keys = stats.get('evicted_keys', 0)
            expired_keys = stats.get('expired_keys', 0)
            
            # Calculate memory efficiency
            efficiency = self._calculate_memory_efficiency(info)
            
            # Calculate optimization potential
            optimization_potential = self._calculate_optimization_potential(info, stats)
            
            analysis = MemoryUsageAnalysis(
                total_memory=maxmemory,
                used_memory=used_memory,
                peak_memory=used_memory_peak,
                fragmentation_ratio=fragmentation_ratio,
                evicted_keys=evicted_keys,
                expired_keys=expired_keys,
                memory_efficiency=efficiency,
                optimization_potential=optimization_potential
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing memory usage: {e}")
            return MemoryUsageAnalysis(0, 0, 0, 1.0, 0, 0, 0.5, 0.0)
    
    def _calculate_memory_efficiency(self, info: Dict[str, Any]) -> float:
        """Calculate memory efficiency score (0-1)"""
        try:
            efficiency_score = 1.0
            
            # Factor 1: Fragmentation penalty
            fragmentation_ratio = info.get('mem_fragmentation_ratio', 1.0)
            if fragmentation_ratio > 1.2:
                efficiency_score -= (fragmentation_ratio - 1.0) * 0.3
            
            # Factor 2: Memory usage efficiency
            used_memory = info.get('used_memory', 0)
            maxmemory = info.get('maxmemory', 0) or (8 * 1024 * 1024 * 1024)
            usage_ratio = used_memory / maxmemory
            
            # Penalize very high or very low usage
            if usage_ratio > 0.9:
                efficiency_score -= (usage_ratio - 0.9) * 2
            elif usage_ratio < 0.1:
                efficiency_score -= (0.1 - usage_ratio) * 0.5
            
            # Factor 3: Memory overhead
            memory_overhead = info.get('used_memory_overhead', 0)
            if memory_overhead > used_memory * 0.2:  # More than 20% overhead
                efficiency_score -= 0.2
            
            return max(0.0, min(1.0, efficiency_score))
            
        except Exception as e:
            logger.error(f"Error calculating memory efficiency: {e}")
            return 0.5
    
    def _calculate_optimization_potential(self, info: Dict[str, Any], stats: Dict[str, Any]) -> float:
        """Calculate optimization potential (0-100%)"""
        try:
            potential = 0.0
            
            # Fragmentation optimization potential
            fragmentation_ratio = info.get('mem_fragmentation_ratio', 1.0)
            if fragmentation_ratio > 1.3:
                potential += min(30.0, (fragmentation_ratio - 1.0) * 20)
            
            # Compression optimization potential
            used_memory_dataset = info.get('used_memory_dataset', 0)
            used_memory = info.get('used_memory', 0)
            if used_memory > 0:
                dataset_ratio = used_memory_dataset / used_memory
                if dataset_ratio > 0.8:  # High data-to-overhead ratio
                    potential += 20.0
            
            # Eviction optimization potential
            evicted_keys = stats.get('evicted_keys', 0)
            if evicted_keys > 1000:
                potential += 15.0
            
            # TTL optimization potential (estimate)
            # This would require key analysis in real implementation
            potential += 10.0  # Baseline assumption
            
            return min(100.0, potential)
            
        except Exception as e:
            logger.error(f"Error calculating optimization potential: {e}")
            return 0.0
    
    async def _optimization_engine(self) -> None:
        """Main optimization engine"""
        while self._running:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                # Get latest memory analysis
                if not self.memory_analysis_history:
                    continue
                
                latest_analysis = self.memory_analysis_history[-1]
                
                # Check if optimization is needed
                if self._needs_optimization(latest_analysis):
                    # Find applicable optimization rules
                    applicable_rules = await self._find_applicable_rules(latest_analysis)
                    
                    # Apply optimizations
                    await self._apply_optimizations(applicable_rules, latest_analysis)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization engine: {e}")
                await asyncio.sleep(60)
    
    def _needs_optimization(self, analysis: MemoryUsageAnalysis) -> bool:
        """Check if optimization is needed"""
        try:
            # Check memory usage thresholds
            memory_usage_pct = (analysis.used_memory / analysis.total_memory) * 100
            
            if memory_usage_pct > self.memory_threshold_warning:
                return True
            
            # Check fragmentation
            if analysis.fragmentation_ratio > self.fragmentation_threshold:
                return True
            
            # Check efficiency
            if analysis.memory_efficiency < 0.7:
                return True
            
            # Check optimization potential
            if analysis.optimization_potential > 20.0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking optimization need: {e}")
            return False
    
    async def _find_applicable_rules(self, analysis: MemoryUsageAnalysis) -> List[MemoryOptimizationRule]:
        """Find applicable optimization rules"""
        applicable_rules = []
        
        try:
            for rule in self.optimization_rules.values():
                if not rule.enabled:
                    continue
                
                # Check if rule conditions are met
                if await self._evaluate_rule_conditions(rule, analysis):
                    applicable_rules.append(rule)
            
            # Sort by priority
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding applicable rules: {e}")
        
        return applicable_rules
    
    async def _evaluate_rule_conditions(self, rule: MemoryOptimizationRule, 
                                      analysis: MemoryUsageAnalysis) -> bool:
        """Evaluate if rule conditions are met"""
        try:
            memory_usage_pct = (analysis.used_memory / analysis.total_memory) * 100
            
            for condition in rule.trigger_conditions:
                condition = condition.lower().strip()
                
                if "memory_usage >" in condition:
                    threshold = float(condition.split(">")[1].strip())
                    if memory_usage_pct <= threshold:
                        return False
                
                elif "fragmentation_ratio >" in condition:
                    threshold = float(condition.split(">")[1].strip())
                    if analysis.fragmentation_ratio <= threshold:
                        return False
                
                elif "fragmented_bytes >" in condition:
                    # Parse threshold (e.g., "100MB")
                    threshold_str = condition.split(">")[1].strip()
                    threshold_bytes = self._parse_byte_size(threshold_str)
                    fragmented_bytes = analysis.used_memory * (analysis.fragmentation_ratio - 1.0)
                    if fragmented_bytes <= threshold_bytes:
                        return False
                
                elif "trend(" in condition:
                    # Simple trend check
                    if len(self.memory_analysis_history) < 5:
                        return False
                    
                    recent_usage = [(a.used_memory / a.total_memory) * 100 
                                  for a in self.memory_analysis_history[-5:]]
                    trend = recent_usage[-1] - recent_usage[0]
                    
                    if "trend(memory_usage, 5min) > 0" in condition and trend <= 0:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {e}")
            return False
    
    def _parse_byte_size(self, size_str: str) -> int:
        """Parse byte size string (e.g., '100MB', '1GB')"""
        try:
            size_str = size_str.upper().strip()
            
            if size_str.endswith('KB'):
                return int(float(size_str[:-2]) * 1024)
            elif size_str.endswith('MB'):
                return int(float(size_str[:-2]) * 1024 * 1024)
            elif size_str.endswith('GB'):
                return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
            else:
                return int(float(size_str))
                
        except Exception:
            return 0
    
    async def _apply_optimizations(self, rules -> None: List[MemoryOptimizationRule], 
                                 analysis -> None: MemoryUsageAnalysis) -> None:
        """Apply optimization rules"""
        try:
            optimizations_applied = 0
            
            for rule in rules:
                # Check if rule was recently applied
                if (rule.last_applied and 
                    (datetime.utcnow() - rule.last_applied).total_seconds() < 300):
                    continue
                
                # Apply rule
                success = await self._apply_optimization_rule(rule, analysis)
                
                if success:
                    optimizations_applied += 1
                    rule.total_applications += 1
                    rule.success_count += 1
                    rule.last_applied = datetime.utcnow()
                    
                    # Store updated rule
                    await self._store_optimization_rule(rule)
                    
                    logger.info(f"Applied optimization rule: {rule.name}")
                    
                    # Wait between optimizations to avoid system stress
                    await asyncio.sleep(10)
            
            if optimizations_applied > 0:
                logger.info(f"Applied {optimizations_applied} memory optimizations")
                
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
    
    async def _apply_optimization_rule(self, rule: MemoryOptimizationRule, 
                                     analysis: MemoryUsageAnalysis) -> bool:
        """Apply a specific optimization rule"""
        try:
            # Store original configuration for potential rollback
            original_config = {}
            
            for config_key, config_value in rule.optimization_actions.items():
                # Handle special actions
                if config_key == "default_ttl":
                    await self._apply_default_ttl_optimization(int(config_value))
                    continue
                
                # Regular Redis configuration
                try:
                    # Get current value
                    current_config = await self.redis_client.config_get(config_key)
                    if current_config:
                        original_config[config_key] = current_config.get(config_key)
                    
                    # Apply new value
                    await self.redis_client.config_set(config_key, config_value)
                    
                    logger.debug(f"Applied config: {config_key} = {config_value}")
                    
                except Exception as e:
                    logger.warning(f"Failed to apply config {config_key}: {e}")
                    # Rollback on failure
                    await self._rollback_config(original_config)
                    return False
            
            # Monitor impact
            asyncio.create_task(self._monitor_optimization_impact(rule, analysis, original_config))
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying optimization rule {rule.rule_id}: {e}")
            return False
    
    async def _apply_default_ttl_optimization(self, default_ttl -> None: int) -> None:
        """Apply default TTL to keys without expiration"""
        try:
            # Find keys without TTL (this is a sample - real implementation would be more efficient)
            keys_processed = 0
            batch_size = 1000
            
            # Use SCAN to iterate through keys
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, count=batch_size)
                
                # Check TTL for each key
                pipeline = self.redis_client.pipeline()
                for key in keys:
                    pipeline.ttl(key)
                
                ttls = await pipeline.execute()
                
                # Set TTL for keys without expiration
                pipeline = self.redis_client.pipeline()
                ttl_sets = 0
                
                for key, ttl in zip(keys, ttls):
                    if ttl == -1:  # No expiration set
                        pipeline.expire(key, default_ttl)
                        ttl_sets += 1
                
                if ttl_sets > 0:
                    await pipeline.execute()
                    keys_processed += ttl_sets
                
                if cursor == 0:
                    break
                
                # Avoid overwhelming the system
                if keys_processed >= 10000:  # Limit per optimization run
                    break
                
                await asyncio.sleep(0.01)  # Small delay
            
            logger.info(f"Applied default TTL to {keys_processed} keys")
            
        except Exception as e:
            logger.error(f"Error applying default TTL optimization: {e}")
    
    async def _rollback_config(self, original_config -> None: Dict[str, Any]) -> None:
        """Rollback configuration changes"""
        try:
            for config_key, config_value in original_config.items():
                await self.redis_client.config_set(config_key, config_value)
                logger.info(f"Rolled back config: {config_key} = {config_value}")
                
        except Exception as e:
            logger.error(f"Error rolling back config: {e}")
    
    async def _monitor_optimization_impact(self, rule -> None: MemoryOptimizationRule, 
                                         before_analysis -> None: MemoryUsageAnalysis,
                                         original_config -> None: Dict[str, Any]) -> None:
        """Monitor the impact of optimization"""
        try:
            # Wait for optimization to take effect
            await asyncio.sleep(120)  # 2 minutes
            
            # Analyze memory after optimization
            after_analysis = await self._analyze_memory_usage()
            
            # Calculate improvement
            memory_before = (before_analysis.used_memory / before_analysis.total_memory) * 100
            memory_after = (after_analysis.used_memory / after_analysis.total_memory) * 100
            
            memory_improvement = memory_before - memory_after
            efficiency_improvement = after_analysis.memory_efficiency - before_analysis.memory_efficiency
            
            # Evaluate success
            expected_savings = rule.expected_memory_savings
            actual_savings = memory_improvement
            
            success_threshold = expected_savings * 0.5  # At least 50% of expected savings
            
            if actual_savings >= success_threshold and efficiency_improvement > 0:
                logger.info(f"Optimization successful: {rule.name} - "
                          f"Memory savings: {actual_savings:.1f}% (expected: {expected_savings:.1f}%)")
            else:
                logger.warning(f"Optimization underperformed: {rule.name} - "
                             f"Memory savings: {actual_savings:.1f}% (expected: {expected_savings:.1f}%)")
                
                # Consider rollback if optimization made things worse
                if actual_savings < 0 and efficiency_improvement < -0.1:
                    logger.warning(f"Rolling back optimization: {rule.name}")
                    await self._rollback_config(original_config)
                    rule.success_count = max(0, rule.success_count - 1)
            
            # Store impact analysis
            await self._store_optimization_impact(rule, before_analysis, after_analysis)
            
        except Exception as e:
            logger.error(f"Error monitoring optimization impact: {e}")
    
    async def _fragmentation_monitor(self) -> None:
        """Monitor and handle memory fragmentation"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Get fragmentation info
                info = await self.redis_client.info('memory')
                fragmentation_ratio = info.get('mem_fragmentation_ratio', 1.0)
                used_memory = info.get('used_memory', 0)
                
                # Update fragmentation info
                self.fragmentation_info.fragmentation_ratio = fragmentation_ratio
                self.fragmentation_info.fragmented_bytes = int(used_memory * (fragmentation_ratio - 1.0))
                
                # Check if defragmentation is needed
                if (fragmentation_ratio > self.fragmentation_threshold and 
                    self.auto_defrag_enabled and 
                    not self.fragmentation_info.defrag_running):
                    
                    await self._start_defragmentation()
                
                # Monitor active defragmentation
                if self.fragmentation_info.defrag_running:
                    await self._monitor_defragmentation()
                
                # Store fragmentation info
                await self._store_fragmentation_info()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in fragmentation monitor: {e}")
                await asyncio.sleep(60)
    
    async def _start_defragmentation(self) -> None:
        """Start active defragmentation"""
        try:
            # Check if defragmentation is supported and enabled
            config = await self.redis_client.config_get('activedefrag')
            if not config or config.get('activedefrag') != 'yes':
                # Enable defragmentation
                await self.redis_client.config_set('activedefrag', 'yes')
                await self.redis_client.config_set('active-defrag-ignore-bytes', '100mb')
                await self.redis_client.config_set('active-defrag-threshold-lower', '10')
                await self.redis_client.config_set('active-defrag-threshold-upper', '100')
            
            # Trigger defragmentation
            result = await self.redis_client.memory_doctor()
            
            self.fragmentation_info.defrag_running = True
            self.fragmentation_info.defrag_count += 1
            self.fragmentation_info.last_defrag = datetime.utcnow()
            
            logger.info("Started active memory defragmentation")
            
        except Exception as e:
            logger.error(f"Error starting defragmentation: {e}")
    
    async def _monitor_defragmentation(self) -> None:
        """Monitor defragmentation progress"""
        try:
            # Check defragmentation status
            info = await self.redis_client.info('memory')
            
            # Simple progress estimation based on fragmentation ratio change
            current_ratio = info.get('mem_fragmentation_ratio', 1.0)
            initial_ratio = 1.5  # Assume we started at threshold
            
            if current_ratio <= 1.2:  # Good fragmentation level
                self.fragmentation_info.defrag_running = False
                self.fragmentation_info.defrag_progress = 100.0
                logger.info("Defragmentation completed successfully")
            else:
                # Estimate progress
                progress = max(0, min(100, ((initial_ratio - current_ratio) / (initial_ratio - 1.2)) * 100))
                self.fragmentation_info.defrag_progress = progress
                
                # Check for timeout (defrag taking too long)
                if (self.fragmentation_info.last_defrag and 
                    (datetime.utcnow() - self.fragmentation_info.last_defrag).total_seconds() > 3600):
                    self.fragmentation_info.defrag_running = False
                    logger.warning("Defragmentation timeout - stopped monitoring")
            
        except Exception as e:
            logger.error(f"Error monitoring defragmentation: {e}")
    
    async def _data_structure_analyzer(self) -> None:
        """Analyze data structures for optimization opportunities"""
        while self._running:
            try:
                await asyncio.sleep(1800)  # Analyze every 30 minutes
                
                # Analyze each data type
                for data_type in DataType:
                    analysis = await self._analyze_data_type(data_type)
                    if analysis:
                        self.data_structure_analysis[data_type] = analysis
                
                # Store analysis results
                await self._store_data_structure_analysis()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in data structure analyzer: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_data_type(self, data_type: DataType) -> Optional[DataStructureAnalysis]:
        """Analyze specific data type usage"""
        try:
            # This is a simplified analysis - real implementation would be more detailed
            info = await self.redis_client.info('keyspace')
            
            # Count keys by type (simplified - would need TYPE command for each key)
            total_keys = sum(info.get(f'db{i}', {}).get('keys', 0) for i in range(16))
            
            if total_keys == 0:
                return None
            
            # Estimate type distribution (would need actual key scanning)
            estimated_type_keys = max(1, total_keys // len(DataType))
            
            # Get memory info
            memory_info = await self.redis_client.info('memory')
            used_memory_dataset = memory_info.get('used_memory_dataset', 0)
            
            # Estimate memory per type
            estimated_memory = used_memory_dataset // len(DataType)
            avg_memory_per_key = estimated_memory / estimated_type_keys if estimated_type_keys > 0 else 0
            
            # Generate optimization suggestions based on data type
            suggestions = self._generate_data_type_suggestions(data_type, avg_memory_per_key)
            
            analysis = DataStructureAnalysis(
                data_type=data_type,
                key_count=estimated_type_keys,
                total_memory=estimated_memory,
                avg_memory_per_key=avg_memory_per_key,
                compression_ratio=0.7,  # Estimated
                optimization_suggestions=suggestions
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data type {data_type}: {e}")
            return None
    
    def _generate_data_type_suggestions(self, data_type: DataType, avg_memory_per_key: float) -> List[str]:
        """Generate optimization suggestions for data type"""
        suggestions = []
        
        try:
            if data_type == DataType.HASH:
                if avg_memory_per_key > 1024:  # > 1KB
                    suggestions.extend([
                        "Consider using hash-max-ziplist-entries for small hashes",
                        "Use hash-max-ziplist-value to compress values",
                        "Consider field name optimization"
                    ])
                    
            elif data_type == DataType.LIST:
                suggestions.extend([
                    "Use list-max-ziplist-size for memory efficiency",
                    "Consider list-compress-depth for large lists"
                ])
                
            elif data_type == DataType.SET:
                if avg_memory_per_key < 100:  # Small sets
                    suggestions.append("Use set-max-intset-entries for integer sets")
                    
            elif data_type == DataType.ZSET:
                suggestions.extend([
                    "Use zset-max-ziplist-entries for small sorted sets",
                    "Consider zset-max-ziplist-value optimization"
                ])
                
            elif data_type == DataType.STRING:
                if avg_memory_per_key > 10240:  # > 10KB
                    suggestions.extend([
                        "Consider compression for large strings",
                        "Evaluate if hash structure would be more efficient"
                    ])
            
            # Common suggestions
            if avg_memory_per_key > 5120:  # > 5KB
                suggestions.append("Consider data compression or alternative storage")
                
        except Exception as e:
            logger.error(f"Error generating suggestions for {data_type}: {e}")
        
        return suggestions
    
    async def _memory_cleaner(self) -> None:
        """Clean up memory by removing expired keys and optimizing storage"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Clean every hour
                
                # Force garbage collection
                await self._force_garbage_collection()
                
                # Clean expired keys
                cleaned_keys = await self._clean_expired_keys()
                
                # Optimize key TTLs
                await self._optimize_key_ttls()
                
                if cleaned_keys > 0:
                    logger.info(f"Memory cleaner processed {cleaned_keys} expired keys")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in memory cleaner: {e}")
                await asyncio.sleep(300)
    
    async def _force_garbage_collection(self) -> None:
        """Force Redis garbage collection"""
        try:
            # Python garbage collection
            gc.collect()
            
            # Redis memory purge (if available)
            try:
                await self.redis_client.memory_purge()
            except Exception:
                # MEMORY PURGE command might not be available in all Redis versions
                pass
            
        except Exception as e:
            logger.error(f"Error in garbage collection: {e}")
    
    async def _clean_expired_keys(self) -> int:
        """Clean expired keys proactively"""
        try:
            # Get initial stats
            stats_before = await self.redis_client.info('stats')
            expired_before = stats_before.get('expired_keys', 0)
            
            # Trigger active expiration
            await self.redis_client.config_set('hz', '100')  # Increase background task frequency
            await asyncio.sleep(30)  # Let Redis process
            await self.redis_client.config_set('hz', '10')  # Reset to default
            
            # Get final stats
            stats_after = await self.redis_client.info('stats')
            expired_after = stats_after.get('expired_keys', 0)
            
            return expired_after - expired_before
            
        except Exception as e:
            logger.error(f"Error cleaning expired keys: {e}")
            return 0
    
    async def _optimize_key_ttls(self) -> None:
        """Optimize TTL values for memory efficiency"""
        try:
            if not self.key_expiration_optimization:
                return
            
            # Sample keys to analyze TTL patterns
            sample_size = 1000
            cursor = 0
            keys_analyzed = 0
            ttl_patterns = {}
            
            while keys_analyzed < sample_size:
                cursor, keys = await self.redis_client.scan(cursor, count=100)
                
                for key in keys:
                    ttl = await self.redis_client.ttl(key)
                    
                    if ttl > 0:
                        # Categorize TTL ranges
                        if ttl < 3600:  # < 1 hour
                            ttl_patterns['short'] = ttl_patterns.get('short', 0) + 1
                        elif ttl < 86400:  # < 1 day
                            ttl_patterns['medium'] = ttl_patterns.get('medium', 0) + 1
                        else:  # > 1 day
                            ttl_patterns['long'] = ttl_patterns.get('long', 0) + 1
                    elif ttl == -1:  # No expiration
                        ttl_patterns['persistent'] = ttl_patterns.get('persistent', 0) + 1
                    
                    keys_analyzed += 1
                    if keys_analyzed >= sample_size:
                        break
                
                if cursor == 0:
                    break
            
            # Log TTL analysis
            if ttl_patterns:
                logger.info(f"TTL analysis: {ttl_patterns}")
            
        except Exception as e:
            logger.error(f"Error optimizing key TTLs: {e}")
    
    async def _trigger_immediate_optimization(self, analysis -> None: MemoryUsageAnalysis) -> None:
        """Trigger immediate optimization for critical situations"""
        try:
            memory_usage_pct = (analysis.used_memory / analysis.total_memory) * 100
            
            if memory_usage_pct > self.memory_threshold_critical:
                logger.warning(f"Critical memory usage: {memory_usage_pct:.1f}%")
                
                # Apply emergency optimizations
                emergency_rules = [
                    rule for rule in self.optimization_rules.values()
                    if rule.optimization_type in [
                        MemoryOptimizationType.EVICTION_POLICY,
                        MemoryOptimizationType.KEY_EXPIRATION
                    ]
                ]
                
                for rule in sorted(emergency_rules, key=lambda r: r.priority, reverse=True):
                    await self._apply_optimization_rule(rule, analysis)
                    await asyncio.sleep(5)  # Brief pause between optimizations
                    
                    # Check if situation improved
                    current_analysis = await self._analyze_memory_usage()
                    current_usage = (current_analysis.used_memory / current_analysis.total_memory) * 100
                    
                    if current_usage < self.memory_threshold_critical:
                        break
                        
        except Exception as e:
            logger.error(f"Error in immediate optimization: {e}")
    
    async def _store_memory_analysis(self, analysis -> None: MemoryUsageAnalysis) -> None:
        """Store memory analysis in Redis"""
        try:
            analysis_data = {
                'total_memory': analysis.total_memory,
                'used_memory': analysis.used_memory,
                'peak_memory': analysis.peak_memory,
                'fragmentation_ratio': analysis.fragmentation_ratio,
                'evicted_keys': analysis.evicted_keys,
                'expired_keys': analysis.expired_keys,
                'memory_efficiency': analysis.memory_efficiency,
                'optimization_potential': analysis.optimization_potential,
                'timestamp': analysis.timestamp.isoformat()
            }
            
            # Store with timestamp key
            key = f"{self.memory_analysis_key}:{int(analysis.timestamp.timestamp())}"
            await self.redis_client.set(key, json.dumps(analysis_data), ex=604800)  # 7 day TTL
            
        except Exception as e:
            logger.error(f"Error storing memory analysis: {e}")
    
    async def _store_optimization_rule(self, rule -> None: MemoryOptimizationRule) -> None:
        """Store optimization rule in Redis"""
        try:
            rule_data = {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'optimization_type': rule.optimization_type.value,
                'trigger_conditions': rule.trigger_conditions,
                'optimization_actions': rule.optimization_actions,
                'expected_memory_savings': rule.expected_memory_savings,
                'priority': rule.priority,
                'enabled': rule.enabled,
                'last_applied': rule.last_applied.isoformat() if rule.last_applied else None,
                'success_count': rule.success_count,
                'total_applications': rule.total_applications
            }
            
            await self.redis_client.hset(self.optimization_rules_key, rule.rule_id, json.dumps(rule_data))
            
        except Exception as e:
            logger.error(f"Error storing optimization rule: {e}")
    
    async def _store_fragmentation_info(self) -> None:
        """Store fragmentation information in Redis"""
        try:
            frag_data = {
                'fragmentation_ratio': self.fragmentation_info.fragmentation_ratio,
                'fragmented_bytes': self.fragmentation_info.fragmented_bytes,
                'defrag_running': self.fragmentation_info.defrag_running,
                'defrag_progress': self.fragmentation_info.defrag_progress,
                'last_defrag': self.fragmentation_info.last_defrag.isoformat() if self.fragmentation_info.last_defrag else None,
                'defrag_count': self.fragmentation_info.defrag_count
            }
            
            await self.redis_client.set(self.fragmentation_key, json.dumps(frag_data))
            
        except Exception as e:
            logger.error(f"Error storing fragmentation info: {e}")
    
    async def _store_data_structure_analysis(self) -> None:
        """Store data structure analysis in Redis"""
        try:
            analysis_data = {}
            
            for data_type, analysis in self.data_structure_analysis.items():
                analysis_data[data_type.value] = {
                    'key_count': analysis.key_count,
                    'total_memory': analysis.total_memory,
                    'avg_memory_per_key': analysis.avg_memory_per_key,
                    'compression_ratio': analysis.compression_ratio,
                    'optimization_suggestions': analysis.optimization_suggestions
                }
            
            key = f"ainflue:memory:datastructures:{int(datetime.utcnow().timestamp())}"
            await self.redis_client.set(key, json.dumps(analysis_data), ex=86400)  # 24 hour TTL
            
        except Exception as e:
            logger.error(f"Error storing data structure analysis: {e}")
    
    async def _store_optimization_impact(self, rule -> None: MemoryOptimizationRule,
                                       before -> None: MemoryUsageAnalysis, after -> None: MemoryUsageAnalysis) -> None:
        """Store optimization impact analysis"""
        try:
            impact_data = {
                'rule_id': rule.rule_id,
                'timestamp': datetime.utcnow().isoformat(),
                'before': {
                    'used_memory': before.used_memory,
                    'memory_efficiency': before.memory_efficiency,
                    'fragmentation_ratio': before.fragmentation_ratio
                },
                'after': {
                    'used_memory': after.used_memory,
                    'memory_efficiency': after.memory_efficiency,
                    'fragmentation_ratio': after.fragmentation_ratio
                },
                'improvements': {
                    'memory_saved_bytes': before.used_memory - after.used_memory,
                    'memory_saved_percent': ((before.used_memory - after.used_memory) / before.used_memory) * 100,
                    'efficiency_improvement': after.memory_efficiency - before.memory_efficiency
                }
            }
            
            key = f"ainflue:memory:impact:{rule.rule_id}:{int(datetime.utcnow().timestamp())}"
            await self.redis_client.set(key, json.dumps(impact_data), ex=604800)  # 7 day TTL
            
        except Exception as e:
            logger.error(f"Error storing optimization impact: {e}")
    
    async def _load_optimization_history(self) -> None:
        """Load optimization history from Redis"""
        try:
            # Load optimization rules
            rules_data = await self.redis_client.hgetall(self.optimization_rules_key)
            
            for rule_id, rule_json in rules_data.items():
                try:
                    rule_data = json.loads(rule_json)
                    
                    # Convert datetime fields
                    if rule_data.get('last_applied'):
                        rule_data['last_applied'] = datetime.fromisoformat(rule_data['last_applied'])
                    
                    # Convert enum
                    rule_data['optimization_type'] = MemoryOptimizationType(rule_data['optimization_type'])
                    
                    rule = MemoryOptimizationRule(**rule_data)
                    self.optimization_rules[rule_id] = rule
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to load optimization rule {rule_id}: {e}")
            
            logger.info(f"Loaded {len(self.optimization_rules)} optimization rules")
            
        except Exception as e:
            logger.error(f"Error loading optimization history: {e}")
    
    async def _capture_config_baseline(self) -> None:
        """Capture baseline Redis configuration"""
        try:
            # Capture key memory-related configurations
            memory_configs = [
                'maxmemory', 'maxmemory-policy', 'maxmemory-samples',
                'hash-max-ziplist-entries', 'hash-max-ziplist-value',
                'list-max-ziplist-size', 'set-max-intset-entries',
                'zset-max-ziplist-entries', 'zset-max-ziplist-value',
                'activedefrag', 'active-defrag-ignore-bytes',
                'active-defrag-threshold-lower', 'active-defrag-threshold-upper'
            ]
            
            for config_name in memory_configs:
                try:
                    config_value = await self.redis_client.config_get(config_name)
                    if config_value:
                        self.config_baseline[config_name] = config_value.get(config_name)
                except Exception:
                    # Config might not exist in all Redis versions
                    pass
            
            logger.info("Captured Redis configuration baseline")
            
        except Exception as e:
            logger.error(f"Error capturing config baseline: {e}")
    
    async def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory management status"""
        try:
            # Get latest analysis
            latest_analysis = self.memory_analysis_history[-1] if self.memory_analysis_history else None
            
            status = {
                'memory_optimizer_status': 'running' if self._running else 'stopped',
                'total_optimization_rules': len(self.optimization_rules),
                'active_rules': len([r for r in self.optimization_rules.values() if r.enabled]),
                'fragmentation_info': {
                    'ratio': self.fragmentation_info.fragmentation_ratio,
                    'fragmented_bytes': self.fragmentation_info.fragmented_bytes,
                    'defrag_running': self.fragmentation_info.defrag_running,
                    'defrag_progress': self.fragmentation_info.defrag_progress
                }
            }
            
            if latest_analysis:
                memory_usage_pct = (latest_analysis.used_memory / latest_analysis.total_memory) * 100
                status.update({
                    'current_memory_usage': {
                        'used_memory_bytes': latest_analysis.used_memory,
                        'total_memory_bytes': latest_analysis.total_memory,
                        'usage_percentage': memory_usage_pct,
                        'memory_efficiency': latest_analysis.memory_efficiency,
                        'optimization_potential': latest_analysis.optimization_potential
                    },
                    'recent_optimizations': len([
                        r for r in self.optimization_rules.values()
                        if r.last_applied and (datetime.utcnow() - r.last_applied).total_seconds() < 3600
                    ])
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting memory status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown the memory management optimizer"""
        try:
            self._running = False
            
            # Cancel background tasks
            for task in self._tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Memory Management Optimizer shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_memory_management_optimizer(redis_settings: Optional[RedisSettings] = None) -> MemoryManagementOptimizer:
    """Factory function to create and initialize MemoryManagementOptimizer"""
    if redis_settings is None:
        redis_settings = RedisSettings()
    
    optimizer = MemoryManagementOptimizer(redis_settings)
    await optimizer.initialize()
    return optimizer