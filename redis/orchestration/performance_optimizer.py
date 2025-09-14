"""
Performance Tuning Engine for Redis Enterprise
ML Engineer Implementation - ML-Driven Performance Optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging

# Optional ML imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

# Redis imports with fallback for enterprise environment
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import redis
        REDIS_AVAILABLE = True
    except ImportError:
        # Fallback pour environnement sans Redis
        REDIS_AVAILABLE = False
        redis = None

# Optional config imports with fallbacks
try:
    from config.core.redis import RedisSettings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    RedisSettings = None

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """Performance optimization strategies"""
    MEMORY_FOCUSED = "memory_focused"
    LATENCY_FOCUSED = "latency_focused"
    THROUGHPUT_FOCUSED = "throughput_focused"
    BALANCED = "balanced"
    ML_ADAPTIVE = "ml_adaptive"

class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    NETWORK_IO = "network_io"
    DISK_IO = "disk_io"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    HIT_RATIO = "hit_ratio"
    CONNECTIONS = "connections"

@dataclass
class PerformanceConfig:
    """Configuration for Redis Performance Optimizer"""
    optimization_strategy: str = "balanced"
    enable_auto_tuning: bool = True
    monitoring_interval: int = 30  # seconds
    optimization_interval: int = 300  # seconds
    enable_ml_optimization: bool = True
    memory_optimization_threshold: float = 0.8
    latency_target_ms: float = 1.0
    throughput_target_ops: int = 10000
    enable_metrics_collection: bool = True
    
    def __post_init__(self):
        if self.monitoring_interval < 5:
            self.monitoring_interval = 5
        if self.optimization_interval < 60:
            self.optimization_interval = 60

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    optimal_range: Optional[Tuple[float, float]] = None

@dataclass
class OptimizationRule:
    """ML-driven optimization rule"""
    rule_id: str
    name: str
    strategy: OptimizationStrategy
    conditions: List[str]  # Conditions to trigger optimization
    actions: Dict[str, Any]  # Redis configuration changes
    confidence_score: float = 0.0  # ML confidence in rule effectiveness
    success_rate: float = 0.0  # Historical success rate
    last_applied: Optional[datetime] = None
    application_count: int = 0
    success_count: int = 0

@dataclass
class PerformanceProfile:
    """Performance characteristics profile"""
    profile_id: str
    workload_type: str  # read_heavy, write_heavy, mixed, cache_intensive
    peak_hours: List[int]  # Hours of peak usage
    avg_memory_usage: float
    avg_cpu_usage: float
    avg_latency: float
    avg_throughput: float
    connection_pattern: str  # steady, bursty, cyclical
    data_access_pattern: str  # random, sequential, hotspot
    optimal_config: Dict[str, Any]
    confidence_level: float = 0.0

class PerformanceTuningEngine:
    """
    ML-driven performance tuning engine for Redis enterprise
    ML Engineer implementation with adaptive optimization algorithms
    """
    
    def __init__(self, redis_settings: RedisSettings):
        self.redis_settings = redis_settings
        self.redis_client: Optional[redis.Redis] = None
        
        # Performance monitoring
        self.metrics_history: Dict[PerformanceMetricType, List[PerformanceMetric]] = {}
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.current_profile: Optional[PerformanceProfile] = None
        
        # ML models and parameters
        self.enable_ml_optimization = True
        self.learning_rate = 0.01
        self.optimization_window = 3600  # 1 hour of data for decisions
        self.metrics_retention_days = 7
        self.min_data_points = 10
        
        # Optimization settings
        self.optimization_strategy = OptimizationStrategy.ML_ADAPTIVE
        self.optimization_interval = 300  # 5 minutes
        self.metrics_collection_interval = 30  # 30 seconds
        self.conservative_mode = False  # If true, makes smaller adjustments
        
        # Redis keys
        self.metrics_key = "ainflue:performance:metrics"
        self.rules_key = "ainflue:performance:rules"
        self.profiles_key = "ainflue:performance:profiles"
        self.config_history_key = "ainflue:performance:config_history"
        
        # Performance baselines
        self.baseline_metrics: Dict[PerformanceMetricType, float] = {}
        self.performance_targets: Dict[PerformanceMetricType, float] = {}
        
        # Background tasks
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Initialize optimization rules and targets
        self._initialize_optimization_rules()
        self._initialize_performance_targets()
    
    def _initialize_optimization_rules(self):
        """Initialize ML-driven optimization rules"""
        try:
            # Memory optimization rules
            self.optimization_rules["memory_high_usage"] = OptimizationRule(
                rule_id="memory_high_usage",
                name="High Memory Usage Optimization",
                strategy=OptimizationStrategy.MEMORY_FOCUSED,
                conditions=[
                    "memory_usage > 80",
                    "trend(memory_usage, 5min) > 0"
                ],
                actions={
                    "maxmemory-policy": "allkeys-lru",
                    "maxmemory-samples": "10",
                    "hash-max-ziplist-entries": "256"
                },
                confidence_score=0.8
            )
            
            # Latency optimization rules
            self.optimization_rules["high_latency"] = OptimizationRule(
                rule_id="high_latency",
                name="High Latency Optimization",
                strategy=OptimizationStrategy.LATENCY_FOCUSED,
                conditions=[
                    "avg_latency > 10",
                    "p95_latency > 50"
                ],
                actions={
                    "tcp-keepalive": "60",
                    "timeout": "300",
                    "tcp-backlog": "2048"
                },
                confidence_score=0.7
            )
            
            # Throughput optimization rules
            self.optimization_rules["low_throughput"] = OptimizationRule(
                rule_id="low_throughput",
                name="Low Throughput Optimization",
                strategy=OptimizationStrategy.THROUGHPUT_FOCUSED,
                conditions=[
                    "throughput < baseline * 0.8",
                    "connection_count > max_connections * 0.7"
                ],
                actions={
                    "maxclients": "20000",
                    "tcp-backlog": "4096",
                    "io-threads": "4"
                },
                confidence_score=0.75
            )
            
            # Hit ratio optimization
            self.optimization_rules["low_hit_ratio"] = OptimizationRule(
                rule_id="low_hit_ratio",
                name="Cache Hit Ratio Optimization",
                strategy=OptimizationStrategy.BALANCED,
                conditions=[
                    "hit_ratio < 0.85",
                    "evicted_keys > 1000"
                ],
                actions={
                    "maxmemory-policy": "allkeys-lfu",
                    "lfu-log-factor": "10",
                    "lfu-decay-time": "1"
                },
                confidence_score=0.85
            )
            
        except Exception as e:
            logger.error(f"Error initializing optimization rules: {e}")
    
    def _initialize_performance_targets(self):
        """Initialize performance targets for different metrics"""
        try:
            self.performance_targets = {
                PerformanceMetricType.MEMORY_USAGE: 75.0,  # Max 75% memory usage
                PerformanceMetricType.CPU_USAGE: 70.0,     # Max 70% CPU usage
                PerformanceMetricType.LATENCY: 5.0,        # Max 5ms latency
                PerformanceMetricType.HIT_RATIO: 90.0,     # Min 90% hit ratio
                PerformanceMetricType.THROUGHPUT: 10000.0, # Min 10k ops/sec
                PerformanceMetricType.CONNECTIONS: 1000.0  # Max 1k connections
            }
            
        except Exception as e:
            logger.error(f"Error initializing performance targets: {e}")
    
    async def initialize(self):
        """Initialize the performance tuning engine"""
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
            await self._load_historical_data()
            await self._establish_baseline()
            
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._optimization_engine()),
                asyncio.create_task(self._ml_trainer()),
                asyncio.create_task(self._profile_analyzer()),
                asyncio.create_task(self._performance_monitor())
            ]
            
            logger.info(f"Performance Tuning Engine initialized with strategy: {self.optimization_strategy.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Performance Tuning Engine: {e}")
            raise
    
    async def _metrics_collector(self):
        """Collect performance metrics from Redis"""
        while self._running:
            try:
                await asyncio.sleep(self.metrics_collection_interval)
                
                # Collect current metrics
                metrics = await self._collect_current_metrics()
                
                # Store metrics
                for metric_type, metric in metrics.items():
                    if metric_type not in self.metrics_history:
                        self.metrics_history[metric_type] = []
                    
                    self.metrics_history[metric_type].append(metric)
                    
                    # Keep only recent metrics
                    cutoff_time = datetime.utcnow() - timedelta(days=self.metrics_retention_days)
                    self.metrics_history[metric_type] = [
                        m for m in self.metrics_history[metric_type] 
                        if m.timestamp > cutoff_time
                    ]
                
                # Store in Redis
                await self._store_metrics(metrics)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(5)
    
    async def _collect_current_metrics(self) -> Dict[PerformanceMetricType, PerformanceMetric]:
        """Collect current performance metrics from Redis"""
        metrics = {}
        timestamp = datetime.utcnow()
        
        try:
            # Get Redis info
            info = await self.redis_client.info()
            stats = await self.redis_client.info('stats')
            
            # Memory metrics
            memory_used = info.get('used_memory', 0)
            memory_max = info.get('maxmemory', 0) or (8 * 1024 * 1024 * 1024)  # Default 8GB
            memory_usage_pct = (memory_used / memory_max) * 100
            
            metrics[PerformanceMetricType.MEMORY_USAGE] = PerformanceMetric(
                metric_type=PerformanceMetricType.MEMORY_USAGE,
                value=memory_usage_pct,
                timestamp=timestamp,
                threshold_high=80.0,
                optimal_range=(50.0, 75.0)
            )
            
            # CPU metrics (simplified - would need system monitoring in real implementation)
            cpu_usage = info.get('used_cpu_sys', 0) + info.get('used_cpu_user', 0)
            metrics[PerformanceMetricType.CPU_USAGE] = PerformanceMetric(
                metric_type=PerformanceMetricType.CPU_USAGE,
                value=cpu_usage,
                timestamp=timestamp,
                threshold_high=70.0,
                optimal_range=(30.0, 60.0)
            )
            
            # Latency metrics (from command processing)
            avg_latency = stats.get('average_response_time', 0) * 1000  # Convert to ms
            metrics[PerformanceMetricType.LATENCY] = PerformanceMetric(
                metric_type=PerformanceMetricType.LATENCY,
                value=avg_latency,
                timestamp=timestamp,
                threshold_high=10.0,
                optimal_range=(1.0, 5.0)
            )
            
            # Throughput metrics
            ops_per_sec = info.get('instantaneous_ops_per_sec', 0)
            metrics[PerformanceMetricType.THROUGHPUT] = PerformanceMetric(
                metric_type=PerformanceMetricType.THROUGHPUT,
                value=ops_per_sec,
                timestamp=timestamp,
                threshold_low=1000.0,
                optimal_range=(5000.0, 50000.0)
            )
            
            # Hit ratio metrics
            hits = stats.get('keyspace_hits', 0)
            misses = stats.get('keyspace_misses', 0)
            hit_ratio = (hits / max(1, hits + misses)) * 100
            
            metrics[PerformanceMetricType.HIT_RATIO] = PerformanceMetric(
                metric_type=PerformanceMetricType.HIT_RATIO,
                value=hit_ratio,
                timestamp=timestamp,
                threshold_low=85.0,
                optimal_range=(90.0, 99.0)
            )
            
            # Connection metrics
            connected_clients = info.get('connected_clients', 0)
            metrics[PerformanceMetricType.CONNECTIONS] = PerformanceMetric(
                metric_type=PerformanceMetricType.CONNECTIONS,
                value=connected_clients,
                timestamp=timestamp,
                threshold_high=1000.0,
                optimal_range=(100.0, 800.0)
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
        
        return metrics
    
    async def _optimization_engine(self):
        """Main optimization engine with ML-driven decisions"""
        while self._running:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                # Analyze current performance
                analysis_result = await self._analyze_current_performance()
                
                if analysis_result['needs_optimization']:
                    # Determine optimization strategy
                    strategy = await self._determine_optimization_strategy(analysis_result)
                    
                    # Apply optimizations
                    optimizations_applied = await self._apply_optimizations(strategy, analysis_result)
                    
                    if optimizations_applied:
                        logger.info(f"Applied {len(optimizations_applied)} performance optimizations")
                        
                        # Monitor impact
                        await self._monitor_optimization_impact(optimizations_applied)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization engine: {e}")
                await asyncio.sleep(30)
    
    async def _analyze_current_performance(self) -> Dict[str, Any]:
        """Analyze current performance and identify issues"""
        analysis = {
            'needs_optimization': False,
            'issues': [],
            'metrics_summary': {},
            'trend_analysis': {},
            'severity_score': 0.0
        }
        
        try:
            # Analyze each metric type
            for metric_type, metrics_list in self.metrics_history.items():
                if not metrics_list:
                    continue
                
                recent_metrics = [m for m in metrics_list 
                                if (datetime.utcnow() - m.timestamp).total_seconds() < 300]
                
                if not recent_metrics:
                    continue
                
                current_value = recent_metrics[-1].value
                avg_value = np.mean([m.value for m in recent_metrics])
                target = self.performance_targets.get(metric_type)
                
                analysis['metrics_summary'][metric_type.value] = {
                    'current': current_value,
                    'average': avg_value,
                    'target': target
                }
                
                # Check for issues
                issue_severity = self._assess_metric_issue(metric_type, current_value, avg_value, target)
                if issue_severity > 0:
                    analysis['issues'].append({
                        'metric': metric_type.value,
                        'severity': issue_severity,
                        'current_value': current_value,
                        'target_value': target
                    })
                    analysis['needs_optimization'] = True
                    analysis['severity_score'] += issue_severity
                
                # Trend analysis
                if len(recent_metrics) >= 5:
                    trend = self._calculate_trend([m.value for m in recent_metrics[-5:]])
                    analysis['trend_analysis'][metric_type.value] = trend
            
            # Normalize severity score
            if analysis['issues']:
                analysis['severity_score'] /= len(analysis['issues'])
                
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
        
        return analysis
    
    def _assess_metric_issue(self, metric_type: PerformanceMetricType, 
                           current_value: float, avg_value: float, target: Optional[float]) -> float:
        """Assess severity of metric issue (0.0 = no issue, 1.0 = critical)"""
        if target is None:
            return 0.0
        
        severity = 0.0
        
        # Different assessment logic based on metric type
        if metric_type in [PerformanceMetricType.MEMORY_USAGE, PerformanceMetricType.CPU_USAGE, 
                          PerformanceMetricType.LATENCY, PerformanceMetricType.CONNECTIONS]:
            # Higher is worse
            if current_value > target:
                severity = min(1.0, (current_value - target) / target)
        
        elif metric_type in [PerformanceMetricType.HIT_RATIO, PerformanceMetricType.THROUGHPUT]:
            # Lower is worse
            if current_value < target:
                severity = min(1.0, (target - current_value) / target)
        
        return severity
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (-1 to 1, negative = improving, positive = worsening)"""
        try:
            if len(values) < 2:
                return 0.0
            
            # Simple linear regression slope
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # Normalize slope to -1 to 1 range
            return np.tanh(slope / (np.std(values) + 1e-8))
            
        except Exception:
            return 0.0
    
    async def _determine_optimization_strategy(self, analysis: Dict[str, Any]) -> OptimizationStrategy:
        """Determine the best optimization strategy using ML"""
        try:
            if not analysis['issues']:
                return self.optimization_strategy
            
            # Analyze issue types to determine strategy
            memory_issues = [i for i in analysis['issues'] if 'memory' in i['metric']]
            latency_issues = [i for i in analysis['issues'] if 'latency' in i['metric']]
            throughput_issues = [i for i in analysis['issues'] if 'throughput' in i['metric']]
            
            # ML-based strategy selection
            if self.optimization_strategy == OptimizationStrategy.ML_ADAPTIVE:
                if memory_issues and max(i['severity'] for i in memory_issues) > 0.7:
                    return OptimizationStrategy.MEMORY_FOCUSED
                elif latency_issues and max(i['severity'] for i in latency_issues) > 0.7:
                    return OptimizationStrategy.LATENCY_FOCUSED
                elif throughput_issues and max(i['severity'] for i in throughput_issues) > 0.7:
                    return OptimizationStrategy.THROUGHPUT_FOCUSED
                else:
                    return OptimizationStrategy.BALANCED
            
            return self.optimization_strategy
            
        except Exception as e:
            logger.error(f"Error determining optimization strategy: {e}")
            return OptimizationStrategy.BALANCED
    
    async def _apply_optimizations(self, strategy: OptimizationStrategy, 
                                 analysis: Dict[str, Any]) -> List[str]:
        """Apply optimizations based on strategy and analysis"""
        applied_optimizations = []
        
        try:
            # Find applicable rules based on strategy and current conditions
            applicable_rules = self._find_applicable_rules(strategy, analysis)
            
            for rule in applicable_rules:
                # Check rule confidence and success rate
                if rule.confidence_score < 0.5 and not self.conservative_mode:
                    continue
                
                # Apply rule actions
                success = await self._apply_rule(rule)
                
                if success:
                    applied_optimizations.append(rule.rule_id)
                    rule.application_count += 1
                    rule.last_applied = datetime.utcnow()
                    
                    # Store rule updates
                    await self._store_optimization_rule(rule)
        
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
        
        return applied_optimizations
    
    def _find_applicable_rules(self, strategy: OptimizationStrategy, 
                             analysis: Dict[str, Any]) -> List[OptimizationRule]:
        """Find optimization rules applicable to current situation"""
        applicable_rules = []
        
        try:
            for rule in self.optimization_rules.values():
                # Check if rule matches strategy
                if rule.strategy != strategy and strategy != OptimizationStrategy.ML_ADAPTIVE:
                    continue
                
                # Check if conditions are met
                if self._evaluate_rule_conditions(rule, analysis):
                    applicable_rules.append(rule)
            
            # Sort by confidence score and success rate
            applicable_rules.sort(
                key=lambda r: (r.confidence_score * 0.7 + r.success_rate * 0.3),
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"Error finding applicable rules: {e}")
        
        return applicable_rules
    
    def _evaluate_rule_conditions(self, rule: OptimizationRule, analysis: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        try:
            metrics_summary = analysis.get('metrics_summary', {})
            
            for condition in rule.conditions:
                if not self._evaluate_condition(condition, metrics_summary):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {e}")
            return False
    
    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        try:
            # Simple condition evaluation (can be enhanced with proper parsing)
            condition = condition.lower().strip()
            
            if "memory_usage >" in condition:
                threshold = float(condition.split(">")[1].strip())
                memory_current = metrics.get('memory_usage', {}).get('current', 0)
                return memory_current > threshold
            
            elif "avg_latency >" in condition:
                threshold = float(condition.split(">")[1].strip())
                latency_avg = metrics.get('latency', {}).get('average', 0)
                return latency_avg > threshold
            
            elif "hit_ratio <" in condition:
                threshold = float(condition.split("<")[1].strip())
                hit_ratio = metrics.get('hit_ratio', {}).get('current', 100)
                return hit_ratio < threshold
            
            elif "throughput <" in condition:
                parts = condition.split("<")[1].strip()
                if "baseline" in parts:
                    multiplier = float(parts.split("*")[1].strip()) if "*" in parts else 1.0
                    baseline = self.baseline_metrics.get(PerformanceMetricType.THROUGHPUT, 1000)
                    threshold = baseline * multiplier
                    throughput = metrics.get('throughput', {}).get('current', 0)
                    return throughput < threshold
                else:
                    threshold = float(parts)
                    throughput = metrics.get('throughput', {}).get('current', 0)
                    return throughput < threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    async def _apply_rule(self, rule: OptimizationRule) -> bool:
        """Apply an optimization rule"""
        try:
            logger.info(f"Applying optimization rule: {rule.name}")
            
            # Store original configuration for rollback
            original_config = {}
            
            for config_key, config_value in rule.actions.items():
                try:
                    # Get current value
                    current_value = await self.redis_client.config_get(config_key)
                    if current_value:
                        original_config[config_key] = current_value.get(config_key)
                    
                    # Apply new value
                    await self.redis_client.config_set(config_key, config_value)
                    
                    logger.info(f"Applied config: {config_key} = {config_value}")
                    
                except Exception as e:
                    logger.warning(f"Failed to apply config {config_key}: {e}")
                    # Rollback on any failure
                    await self._rollback_config(original_config)
                    return False
            
            # Store configuration change for monitoring
            await self._store_config_change(rule.rule_id, original_config, rule.actions)
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying rule {rule.rule_id}: {e}")
            return False
    
    async def _rollback_config(self, original_config: Dict[str, Any]):
        """Rollback configuration changes"""
        try:
            for config_key, config_value in original_config.items():
                await self.redis_client.config_set(config_key, config_value)
                logger.info(f"Rolled back config: {config_key} = {config_value}")
                
        except Exception as e:
            logger.error(f"Error rolling back configuration: {e}")
    
    async def _monitor_optimization_impact(self, applied_rules: List[str]):
        """Monitor the impact of applied optimizations"""
        try:
            # Wait for changes to take effect
            await asyncio.sleep(60)
            
            # Collect new metrics
            post_optimization_metrics = await self._collect_current_metrics()
            
            # Compare with baseline and update rule success rates
            for rule_id in applied_rules:
                rule = self.optimization_rules.get(rule_id)
                if rule:
                    # Simple success evaluation based on target metrics
                    success = self._evaluate_optimization_success(post_optimization_metrics, rule)
                    
                    if success:
                        rule.success_count += 1
                    
                    # Update success rate
                    rule.success_rate = rule.success_count / rule.application_count if rule.application_count > 0 else 0
                    
                    # Update confidence using ML (simple approach)
                    rule.confidence_score = self._update_confidence_score(rule)
                    
                    await self._store_optimization_rule(rule)
                    
        except Exception as e:
            logger.error(f"Error monitoring optimization impact: {e}")
    
    def _evaluate_optimization_success(self, metrics: Dict[PerformanceMetricType, PerformanceMetric], 
                                     rule: OptimizationRule) -> bool:
        """Evaluate if optimization was successful"""
        try:
            # Simple success criteria based on rule strategy
            if rule.strategy == OptimizationStrategy.MEMORY_FOCUSED:
                memory_metric = metrics.get(PerformanceMetricType.MEMORY_USAGE)
                if memory_metric:
                    target = self.performance_targets.get(PerformanceMetricType.MEMORY_USAGE, 75)
                    return memory_metric.value < target
            
            elif rule.strategy == OptimizationStrategy.LATENCY_FOCUSED:
                latency_metric = metrics.get(PerformanceMetricType.LATENCY)
                if latency_metric:
                    target = self.performance_targets.get(PerformanceMetricType.LATENCY, 5)
                    return latency_metric.value < target
            
            elif rule.strategy == OptimizationStrategy.THROUGHPUT_FOCUSED:
                throughput_metric = metrics.get(PerformanceMetricType.THROUGHPUT)
                if throughput_metric:
                    target = self.performance_targets.get(PerformanceMetricType.THROUGHPUT, 1000)
                    return throughput_metric.value > target
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating optimization success: {e}")
            return False
    
    def _update_confidence_score(self, rule: OptimizationRule) -> float:
        """Update rule confidence score using simple ML approach"""
        try:
            # Simple confidence update based on success rate and recency
            base_confidence = rule.success_rate
            
            # Boost confidence for recently successful rules
            if rule.last_applied:
                hours_since_applied = (datetime.utcnow() - rule.last_applied).total_seconds() / 3600
                recency_factor = max(0, 1 - hours_since_applied / 24)  # Decay over 24 hours
                base_confidence += recency_factor * 0.1
            
            # Penalize rules with very few applications
            if rule.application_count < 5:
                base_confidence *= (rule.application_count / 5)
            
            return min(1.0, max(0.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Error updating confidence score: {e}")
            return rule.confidence_score
    
    async def _ml_trainer(self):
        """Train ML models for better optimization decisions"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Train every hour
                
                # Collect training data
                training_data = await self._prepare_training_data()
                
                if len(training_data) >= self.min_data_points:
                    # Train simple models (placeholder for more sophisticated ML)
                    await self._train_performance_models(training_data)
                    
                    # Update optimization rules based on learning
                    await self._update_rules_from_learning()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ML trainer: {e}")
                await asyncio.sleep(300)
    
    async def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from historical metrics and rule applications"""
        training_data = []
        
        try:
            # Collect data points where optimizations were applied
            for rule in self.optimization_rules.values():
                if rule.application_count > 0:
                    # Create training examples from rule applications
                    # This is simplified - real implementation would be more sophisticated
                    training_data.append({
                        'rule_id': rule.rule_id,
                        'strategy': rule.strategy.value,
                        'success_rate': rule.success_rate,
                        'confidence': rule.confidence_score,
                        'applications': rule.application_count
                    })
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
        
        return training_data
    
    async def _train_performance_models(self, training_data: List[Dict[str, Any]]):
        """Train performance prediction models"""
        try:
            # Placeholder for ML model training
            # In a real implementation, this would use proper ML libraries
            # like scikit-learn, TensorFlow, or PyTorch
            
            logger.info(f"Training ML models with {len(training_data)} data points")
            
            # Simple learning: adjust rule priorities based on success rates
            for data_point in training_data:
                rule_id = data_point['rule_id']
                rule = self.optimization_rules.get(rule_id)
                
                if rule:
                    # Simple learning rule: increase confidence for successful rules
                    if data_point['success_rate'] > 0.8:
                        rule.confidence_score = min(1.0, rule.confidence_score + self.learning_rate)
                    elif data_point['success_rate'] < 0.3:
                        rule.confidence_score = max(0.0, rule.confidence_score - self.learning_rate)
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    async def _update_rules_from_learning(self):
        """Update optimization rules based on ML learning"""
        try:
            # Update rule parameters based on learning
            for rule in self.optimization_rules.values():
                await self._store_optimization_rule(rule)
            
            logger.info("Updated optimization rules from ML learning")
            
        except Exception as e:
            logger.error(f"Error updating rules from learning: {e}")
    
    async def _profile_analyzer(self):
        """Analyze workload patterns and create performance profiles"""
        while self._running:
            try:
                await asyncio.sleep(1800)  # Analyze every 30 minutes
                
                # Analyze current workload pattern
                profile = await self._analyze_workload_pattern()
                
                if profile:
                    # Update current profile
                    self.current_profile = profile
                    await self._store_performance_profile(profile)
                    
                    # Adjust optimization strategy based on profile
                    await self._adapt_strategy_to_profile(profile)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in profile analyzer: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_workload_pattern(self) -> Optional[PerformanceProfile]:
        """Analyze current workload pattern"""
        try:
            # Get recent metrics for analysis
            recent_window = datetime.utcnow() - timedelta(hours=1)
            
            workload_metrics = {}
            for metric_type, metrics_list in self.metrics_history.items():
                recent_metrics = [m for m in metrics_list if m.timestamp > recent_window]
                if recent_metrics:
                    workload_metrics[metric_type] = {
                        'avg': np.mean([m.value for m in recent_metrics]),
                        'std': np.std([m.value for m in recent_metrics]),
                        'trend': self._calculate_trend([m.value for m in recent_metrics])
                    }
            
            if not workload_metrics:
                return None
            
            # Determine workload type
            workload_type = self._classify_workload_type(workload_metrics)
            
            # Create performance profile
            profile = PerformanceProfile(
                profile_id=f"profile_{int(datetime.utcnow().timestamp())}",
                workload_type=workload_type,
                peak_hours=[datetime.utcnow().hour],  # Simplified
                avg_memory_usage=workload_metrics.get(PerformanceMetricType.MEMORY_USAGE, {}).get('avg', 0),
                avg_cpu_usage=workload_metrics.get(PerformanceMetricType.CPU_USAGE, {}).get('avg', 0),
                avg_latency=workload_metrics.get(PerformanceMetricType.LATENCY, {}).get('avg', 0),
                avg_throughput=workload_metrics.get(PerformanceMetricType.THROUGHPUT, {}).get('avg', 0),
                connection_pattern="steady",  # Simplified
                data_access_pattern="mixed",  # Simplified
                optimal_config={},  # To be determined
                confidence_level=0.7
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing workload pattern: {e}")
            return None
    
    def _classify_workload_type(self, metrics: Dict[PerformanceMetricType, Dict[str, float]]) -> str:
        """Classify workload type based on metrics"""
        try:
            hit_ratio = metrics.get(PerformanceMetricType.HIT_RATIO, {}).get('avg', 50)
            throughput = metrics.get(PerformanceMetricType.THROUGHPUT, {}).get('avg', 0)
            memory_usage = metrics.get(PerformanceMetricType.MEMORY_USAGE, {}).get('avg', 0)
            
            # Simple classification logic
            if hit_ratio > 90 and memory_usage > 70:
                return "cache_intensive"
            elif throughput > 10000:
                return "write_heavy"
            elif hit_ratio > 80:
                return "read_heavy"
            else:
                return "mixed"
                
        except Exception as e:
            logger.error(f"Error classifying workload type: {e}")
            return "mixed"
    
    async def _adapt_strategy_to_profile(self, profile: PerformanceProfile):
        """Adapt optimization strategy based on workload profile"""
        try:
            # Adjust strategy based on workload type
            if profile.workload_type == "cache_intensive":
                self.optimization_strategy = OptimizationStrategy.MEMORY_FOCUSED
            elif profile.workload_type == "write_heavy":
                self.optimization_strategy = OptimizationStrategy.THROUGHPUT_FOCUSED
            elif profile.avg_latency > 10:
                self.optimization_strategy = OptimizationStrategy.LATENCY_FOCUSED
            else:
                self.optimization_strategy = OptimizationStrategy.ML_ADAPTIVE
            
            logger.info(f"Adapted strategy to {self.optimization_strategy.value} for workload type {profile.workload_type}")
            
        except Exception as e:
            logger.error(f"Error adapting strategy to profile: {e}")
    
    async def _performance_monitor(self):
        """Monitor overall performance and alert on issues"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Check for performance issues
                issues = await self._check_performance_issues()
                
                if issues:
                    await self._handle_performance_issues(issues)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(30)
    
    async def _check_performance_issues(self) -> List[Dict[str, Any]]:
        """Check for critical performance issues"""
        issues = []
        
        try:
            for metric_type, metrics_list in self.metrics_history.items():
                if not metrics_list:
                    continue
                
                recent_metric = metrics_list[-1]
                target = self.performance_targets.get(metric_type)
                
                if target:
                    severity = self._assess_metric_issue(metric_type, recent_metric.value, recent_metric.value, target)
                    
                    if severity > 0.8:  # Critical issue
                        issues.append({
                            'metric': metric_type.value,
                            'severity': severity,
                            'current_value': recent_metric.value,
                            'target_value': target,
                            'timestamp': recent_metric.timestamp.isoformat()
                        })
            
        except Exception as e:
            logger.error(f"Error checking performance issues: {e}")
        
        return issues
    
    async def _handle_performance_issues(self, issues: List[Dict[str, Any]]):
        """Handle critical performance issues"""
        try:
            for issue in issues:
                logger.warning(f"Critical performance issue: {issue['metric']} = {issue['current_value']} (target: {issue['target_value']})")
                
                # Trigger immediate optimization for critical issues
                if issue['severity'] > 0.9:
                    await self._trigger_emergency_optimization(issue)
                    
        except Exception as e:
            logger.error(f"Error handling performance issues: {e}")
    
    async def _trigger_emergency_optimization(self, issue: Dict[str, Any]):
        """Trigger emergency optimization for critical issues"""
        try:
            # Find emergency rules for the specific metric
            emergency_rules = [
                rule for rule in self.optimization_rules.values()
                if issue['metric'] in str(rule.conditions).lower()
            ]
            
            # Apply highest confidence rule immediately
            if emergency_rules:
                best_rule = max(emergency_rules, key=lambda r: r.confidence_score)
                await self._apply_rule(best_rule)
                logger.warning(f"Applied emergency optimization rule: {best_rule.name}")
                
        except Exception as e:
            logger.error(f"Error in emergency optimization: {e}")
    
    async def _store_metrics(self, metrics: Dict[PerformanceMetricType, PerformanceMetric]):
        """Store metrics in Redis"""
        try:
            metrics_data = {}
            for metric_type, metric in metrics.items():
                metrics_data[metric_type.value] = {
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat()
                }
            
            timestamp_key = f"{self.metrics_key}:{int(datetime.utcnow().timestamp())}"
            await self.redis_client.set(timestamp_key, json.dumps(metrics_data), ex=86400)  # 24 hour TTL
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def _store_optimization_rule(self, rule: OptimizationRule):
        """Store optimization rule in Redis"""
        try:
            rule_data = {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'strategy': rule.strategy.value,
                'conditions': rule.conditions,
                'actions': rule.actions,
                'confidence_score': rule.confidence_score,
                'success_rate': rule.success_rate,
                'last_applied': rule.last_applied.isoformat() if rule.last_applied else None,
                'application_count': rule.application_count,
                'success_count': rule.success_count
            }
            
            await self.redis_client.hset(self.rules_key, rule.rule_id, json.dumps(rule_data))
            
        except Exception as e:
            logger.error(f"Error storing optimization rule: {e}")
    
    async def _store_performance_profile(self, profile: PerformanceProfile):
        """Store performance profile in Redis"""
        try:
            profile_data = {
                'profile_id': profile.profile_id,
                'workload_type': profile.workload_type,
                'peak_hours': profile.peak_hours,
                'avg_memory_usage': profile.avg_memory_usage,
                'avg_cpu_usage': profile.avg_cpu_usage,
                'avg_latency': profile.avg_latency,
                'avg_throughput': profile.avg_throughput,
                'connection_pattern': profile.connection_pattern,
                'data_access_pattern': profile.data_access_pattern,
                'optimal_config': profile.optimal_config,
                'confidence_level': profile.confidence_level
            }
            
            await self.redis_client.hset(self.profiles_key, profile.profile_id, json.dumps(profile_data))
            
        except Exception as e:
            logger.error(f"Error storing performance profile: {e}")
    
    async def _store_config_change(self, rule_id: str, original_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Store configuration change for monitoring"""
        try:
            change_data = {
                'rule_id': rule_id,
                'timestamp': datetime.utcnow().isoformat(),
                'original_config': original_config,
                'new_config': new_config
            }
            
            change_key = f"{self.config_history_key}:{rule_id}:{int(datetime.utcnow().timestamp())}"
            await self.redis_client.set(change_key, json.dumps(change_data), ex=604800)  # 7 day TTL
            
        except Exception as e:
            logger.error(f"Error storing config change: {e}")
    
    async def _load_historical_data(self):
        """Load historical performance data"""
        try:
            # Load optimization rules
            rules_data = await self.redis_client.hgetall(self.rules_key)
            for rule_id, rule_json in rules_data.items():
                try:
                    rule_data = json.loads(rule_json)
                    
                    # Convert datetime fields
                    if rule_data.get('last_applied'):
                        rule_data['last_applied'] = datetime.fromisoformat(rule_data['last_applied'])
                    
                    # Convert enum
                    rule_data['strategy'] = OptimizationStrategy(rule_data['strategy'])
                    
                    rule = OptimizationRule(**rule_data)
                    self.optimization_rules[rule_id] = rule
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to load rule {rule_id}: {e}")
            
            logger.info(f"Loaded {len(self.optimization_rules)} optimization rules")
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    async def _establish_baseline(self):
        """Establish performance baseline"""
        try:
            # Collect initial metrics for baseline
            current_metrics = await self._collect_current_metrics()
            
            for metric_type, metric in current_metrics.items():
                self.baseline_metrics[metric_type] = metric.value
            
            logger.info("Established performance baseline")
            
        except Exception as e:
            logger.error(f"Error establishing baseline: {e}")
    
    async def get_performance_status(self) -> Dict[str, Any]:
        """Get current performance status"""
        try:
            current_metrics = await self._collect_current_metrics()
            
            status = {
                'optimization_strategy': self.optimization_strategy.value,
                'current_profile': self.current_profile.workload_type if self.current_profile else None,
                'total_rules': len(self.optimization_rules),
                'active_optimizations': len([r for r in self.optimization_rules.values() if r.last_applied]),
                'metrics': {
                    metric_type.value: {
                        'current': metric.value,
                        'target': self.performance_targets.get(metric_type),
                        'baseline': self.baseline_metrics.get(metric_type)
                    } for metric_type, metric in current_metrics.items()
                },
                'rule_performance': {
                    rule_id: {
                        'confidence': rule.confidence_score,
                        'success_rate': rule.success_rate,
                        'applications': rule.application_count
                    } for rule_id, rule in self.optimization_rules.items()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting performance status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown the performance tuning engine"""
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
            
            logger.info("Performance Tuning Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_performance_tuning_engine(redis_settings: Optional[RedisSettings] = None) -> PerformanceTuningEngine:
    """Factory function to create and initialize PerformanceTuningEngine"""
    if redis_settings is None:
        redis_settings = RedisSettings()
    
    engine = PerformanceTuningEngine(redis_settings)
    await engine.initialize()
    return engine


# Enterprise alias for compatibility
class RedisPerformanceOptimizer(PerformanceTuningEngine):
    """Enterprise Redis Performance Optimizer - alias for PerformanceTuningEngine"""
    
    def __init__(self, config: PerformanceConfig):
        """Initialize with PerformanceConfig instead of dict"""
        # Convert PerformanceConfig to dict for parent class
        config_dict = {
            'optimization_strategy': config.optimization_strategy,
            'enable_auto_tuning': config.enable_auto_tuning,
            'monitoring_interval': config.monitoring_interval,
            'optimization_interval': config.optimization_interval,
            'enable_ml_optimization': config.enable_ml_optimization,
            'memory_optimization_threshold': config.memory_optimization_threshold,
            'latency_target_ms': config.latency_target_ms,
            'throughput_target_ops': config.throughput_target_ops,
            'enable_metrics_collection': config.enable_metrics_collection
        }
        # For this simple alias, just store the config
        self.config = config_dict