"""Cache Warming Configuration for IA-Influencer Agent Platform
============================================================

Advanced cache warming strategies for proactive data loading
and performance optimization in multi-tenant environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, validator
import crontab


class WarmingStrategy(str, Enum):
    """
Cache warming strategies"""

    PROACTIVE = "proactive"  # Pre-load based on predictions
    SCHEDULED = "scheduled"  # Time-based warming
    ACCESS_PATTERN = "access_pattern"  # Based on historical access patterns
    DEPENDENCY_DRIVEN = "dependency_driven"  # Warm dependent data
    EVENT_TRIGGERED = "event_triggered"  # Triggered by specific events
    POPULARITY_BASED = "popularity_based"  # Based on data popularity
    PREDICTIVE = "predictive"  # ML-based predictions


class WarmingTrigger(str, Enum):
    """Events that can trigger cache warming"""

    APPLICATION_START = "application_start"
    SCHEDULED_TIME = "scheduled_time"
    LOW_HIT_RATIO = "low_hit_ratio"
    CACHE_MISS_SPIKE = "cache_miss_spike"
    DATA_UPDATE = "data_update"
    USER_LOGIN = "user_login"
    TENANT_ACTIVATION = "tenant_activation"
    CONTENT_UPLOAD = "content_upload"
    HIGH_TRAFFIC_PREDICTED = "high_traffic_predicted"
    SYSTEM_IDLE = "system_idle"


class WarmingPriority(int, Enum):
    """Priority levels for warming operations"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class WarmingRule:
    """
Cache warming rule definition"""
    name: str
    strategy: WarmingStrategy
    triggers: List[WarmingTrigger] = field(default_factory=list)
    priority: WarmingPriority = WarmingPriority.MEDIUM
    
    # Data selection
    data_source: str = ""  # SQL query, API endpoint, etc.
    key_pattern: str = ""
    key_generator: Optional[Callable] = None
    value_loader: Optional[Callable] = None
    
    # Timing and scheduling
    schedule: Optional[str] = None  # Cron expression
    warm_ahead_minutes: int = 60
    batch_size: int = 100
    concurrent_workers: int = 5
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    tenant_filter: Optional[List[str]] = None
    region_filter: Optional[List[str]] = None
    
    # Performance controls
    rate_limit_per_second: int = 50
    max_memory_mb: int = 1000
    timeout_seconds: int = 300
    
    # TTL and expiry
    cache_ttl: Optional[int] = None
    refresh_threshold: float = 0.8  # Refresh when 80% of TTL elapsed
    
    # Validation
    enabled: bool = True
    dry_run: bool = False
    
    def matches_trigger(self, trigger: WarmingTrigger) -> bool:
        """Check if rule applies to given trigger"""
        return trigger in self.triggers
    
    def matches_conditions(self, context: Dict[str, Any]) -> bool:
        """
Check if rule conditions are met"""
        if not self.conditions:
            return True
        
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            if isinstance(expected_value, dict) and expected_value.get("operator"):
                if not self._evaluate_condition(actual_value, expected_value):
                    return False
            elif actual_value != expected_value:
                return False
        
        return True
    
    def _evaluate_condition(self, actual: Any, condition: Dict[str, Any]) -> bool:
        """Evaluate complex conditions"""
        operator = condition["operator"]
        expected = condition["value"]
        
        if operator == "eq":
            return actual == expected
        elif operator == "ne":
            return actual != expected
        elif operator == "gt":
            return actual > expected
        elif operator == "gte":
            return actual >= expected
        elif operator == "lt":
            return actual < expected
        elif operator == "lte":
            return actual <= expected
        elif operator == "in":
            return actual in expected
        elif operator == "not_in":
            return actual not in expected
        elif operator == "contains":
            return expected in actual
        
        return False


@dataclass
class WarmingMetrics:
    """Cache warming performance metrics"""
    total_warming_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    keys_warmed: int = 0
    keys_failed: int = 0
    total_warming_time: float = 0.0
    average_warming_time: float = 0.0
    memory_used_mb: float = 0.0
    hit_ratio_improvement: float = 0.0
    last_warming_run: Optional[datetime] = None


@dataclass
class AccessPattern:
    """
Data access pattern analysis"""
    key: str
    access_count: int = 0
    last_access: Optional[datetime] = None
    access_frequency_per_hour: float = 0.0
    peak_hours: List[int] = field(default_factory=list)
    avg_response_time: float = 0.0
    cache_hit_ratio: float = 0.0
    tenant_id: Optional[str] = None
    
    def calculate_warming_score(self) -> float:
        """
Calculate score for warming priority"""
        frequency_score = min(self.access_frequency_per_hour / 10.0, 1.0)
        hit_ratio_penalty = (1.0 - self.cache_hit_ratio) * 0.5
        recency_bonus = 0.2 if self.last_access and \
                       (datetime.utcnow() - self.last_access).total_seconds() < 3600 else 0.0
        
        return frequency_score + hit_ratio_penalty + recency_bonus


class CacheWarmingConfig(BaseModel):
    """
    Comprehensive cache warming configuration
    """
    
    # General settings
    enabled: bool = True
    warming_on_startup: bool = True
    
    # Warming rules
    rules: List[WarmingRule] = field(default_factory=list)
    
    # Scheduler settings
    scheduler_enabled: bool = True
    scheduler_interval: int = 60  # seconds
    max_concurrent_jobs: int = 5
    
    # Performance settings
    global_rate_limit: int = 1000  # operations per second
    max_memory_usage_mb: int = 2000
    worker_thread_pool_size: int = 20
    queue_size: int = 10000
    
    # Pattern analysis
    access_pattern_tracking: bool = True
    pattern_analysis_window_hours: int = 24
    min_access_frequency: float = 0.1  # per hour
    pattern_update_interval: int = 3600  # seconds
    
    # Predictive warming
    predictive_warming_enabled: bool = True
    prediction_horizon_minutes: int = 120
    ml_model_path: Optional[str] = None
    prediction_confidence_threshold: float = 0.7
    
    # Multi-tenant warming
    tenant_isolation: bool = True
    tenant_priority_weights: Dict[str, float] = field(default_factory=dict)
    max_tenants_concurrent: int = 10
    
    # Monitoring and metrics
    enable_metrics: bool = True
    metrics_retention_hours: int = 168  # 1 week
    log_warming_operations: bool = True
    performance_threshold_ms: int = 5000
    
    # Failure handling
    retry_failed_warming: bool = True
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 10
    
    # Resource management
    cpu_usage_threshold: float = 80.0  # percentage
    memory_usage_threshold: float = 80.0  # percentage
    pause_on_high_load: bool = True
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('rules')
    def validate_rules(cls, v):
        # Check for duplicate rule names
        names = [rule.name for rule in v]
        if len(names) != len(set(names)):
            raise ValueError("Rule names must be unique")
        return v
    
    @validator('global_rate_limit')
    def validate_rate_limit(cls, v):
        if v <= 0:
            raise ValueError("Rate limit must be positive")
        return v
    
    def add_rule(self, rule: WarmingRule):
        """Add warming rule"""
        if any(r.name == rule.name for r in self.rules):
            raise ValueError(f"Rule with name '{rule.name}' already exists")
        
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove warming rule"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def get_rules_for_trigger(self, trigger: WarmingTrigger) -> List[WarmingRule]:
        """
Get rules that apply to specific trigger"""
        matching_rules = []
        
        for rule in self.rules:
            if rule.enabled and rule.matches_trigger(trigger):
                matching_rules.append(rule)
        
        # Sort by priority (higher priority first)
        return sorted(matching_rules, key=lambda r: r.priority.value)
    
    def get_scheduled_rules(self) -> List[WarmingRule]:
        """
Get rules with schedule configuration"""
        return [rule for rule in self.rules 
                if rule.enabled and rule.schedule and rule.strategy == WarmingStrategy.SCHEDULED]
    
    def should_warm_key(self, pattern: AccessPattern) -> bool:
        """
Determine if key should be warmed based on access pattern"""
        if not self.access_pattern_tracking:
            return False
        
        warming_score = pattern.calculate_warming_score()
        return (warming_score > 0.5 and 
                pattern.access_frequency_per_hour >= self.min_access_frequency)
    
    def get_tenant_weight(self, tenant_id: str) -> float:
        """
Get warming priority weight for tenant"""
        return self.tenant_priority_weights.get(tenant_id, 1.0)
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
Get configuration summary for monitoring"""
        return {
            "enabled": self.enabled,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules if r.enabled]),
            "scheduled_rules": len(self.get_scheduled_rules()),
            "predictive_warming": self.predictive_warming_enabled,
            "access_pattern_tracking": self.access_pattern_tracking,
            "tenant_isolation": self.tenant_isolation,
            "global_rate_limit": self.global_rate_limit,
            "max_memory_usage_mb": self.max_memory_usage_mb
        }


class CacheWarmingEngine:
    """
    Cache warming execution engine
    """
    
    def __init__(self, config: CacheWarmingConfig):
        self.config = config
        self.metrics = WarmingMetrics()
        self.access_patterns: Dict[str, AccessPattern] = {}
        self.warming_queue = asyncio.Queue(maxsize=config.queue_size)
        self.scheduler_task = None
        self.pattern_analyzer_task = None
        self.workers: List[asyncio.Task] = []
        self.running = False
    
    async def start(self):
        """
Start cache warming engine"""
        if self.running:
            return
        
        self.running = True
        
        # Start scheduler
        if self.config.scheduler_enabled:
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Start pattern analyzer
        if self.config.access_pattern_tracking:
            self.pattern_analyzer_task = asyncio.create_task(self._pattern_analysis_loop())
        
        # Start worker tasks
        for i in range(self.config.max_concurrent_jobs):
            worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.workers.append(worker)
        
        # Warm on startup if enabled
        if self.config.warming_on_startup:
            await self._trigger_startup_warming()
    
    async def stop(self):
        """Stop cache warming engine"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel scheduler
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel pattern analyzer
        if self.pattern_analyzer_task:
            self.pattern_analyzer_task.cancel()
            try:
                await self.pattern_analyzer_task
            except asyncio.CancelledError:
                pass
        
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
    
    async def trigger_warming(self, trigger: WarmingTrigger, context: Dict[str, Any] = None):
        """
Trigger cache warming for specific event"""
        if not self.config.enabled or not self.running:
            return
        
        if context is None:
            context = {}
        
        context["trigger"] = trigger
        context["timestamp"] = datetime.utcnow()
        
        # Get applicable rules
        rules = self.config.get_rules_for_trigger(trigger)
        
        for rule in rules:
            if rule.matches_conditions(context):
                await self._queue_warming_job(rule, context)
    
    async def warm_key(self, key: str, value_loader: Callable, cache_client: Any, 
                      ttl: Optional[int] = None) -> bool:
        """Warm specific cache key"""
        try:
            # Load value
            if asyncio.iscoroutinefunction(value_loader):
                value = await value_loader(key)
            else:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    value = await loop.run_in_executor(executor, value_loader, key)
            
            if value is None:
                return False
            
            # Store in cache
            if hasattr(cache_client, 'set'):
                if asyncio.iscoroutinefunction(cache_client.set):
                    result = await cache_client.set(key, value, ttl)
                else:
                    result = cache_client.set(key, value, ttl)
                
                if result:
                    self.metrics.keys_warmed += 1
                    return True
            
            return False
            
        except Exception as e:
            self.metrics.keys_failed += 1
            return False
    
    def track_access(self, key: str, tenant_id: Optional[str] = None, 
                    response_time: float = 0.0, hit: bool = True):
        """
Track key access for pattern analysis"""
        if not self.config.access_pattern_tracking:
            return
        
        if key not in self.access_patterns:
            self.access_patterns[key] = AccessPattern(
                key=key,
                tenant_id=tenant_id
            )
        
        pattern = self.access_patterns[key]
        pattern.access_count += 1
        pattern.last_access = datetime.utcnow()
        
        # Update response time (moving average)
        if pattern.avg_response_time == 0:
            pattern.avg_response_time = response_time
        else:
            pattern.avg_response_time = (pattern.avg_response_time * 0.9 + response_time * 0.1)
        
        # Update hit ratio (moving average)
        hit_value = 1.0 if hit else 0.0
        if pattern.cache_hit_ratio == 0:
            pattern.cache_hit_ratio = hit_value
        else:
            pattern.cache_hit_ratio = (pattern.cache_hit_ratio * 0.9 + hit_value * 0.1)
    
    def get_warming_recommendations(self, limit: int = 100) -> List[AccessPattern]:
        """
Get recommendations for keys to warm"""
        if not self.access_patterns:
            return []
        
        # Calculate warming scores and filter
        candidates = []
        for pattern in self.access_patterns.values():
            if self.config.should_warm_key(pattern):
                candidates.append(pattern)
        
        # Sort by warming score
        candidates.sort(key=lambda p: p.calculate_warming_score(), reverse=True)
        
        return candidates[:limit]
    
    async def _scheduler_loop(self):
        """
Main scheduler loop for time-based warming"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                scheduled_rules = self.config.get_scheduled_rules()
                
                for rule in scheduled_rules:
                    if self._should_run_scheduled_rule(rule, current_time):
                        context = {"trigger": WarmingTrigger.SCHEDULED_TIME, "timestamp": current_time}
                        await self._queue_warming_job(rule, context)
                
                # Sleep until next check
                await asyncio.sleep(self.config.scheduler_interval)
                
            except Exception as e:
                # Log error and continue
                await asyncio.sleep(self.config.scheduler_interval)
    
    async def _pattern_analysis_loop(self):
        """Pattern analysis and predictive warming loop"""
        while self.running:
            try:
                await self._update_access_frequencies()
                
                if self.config.predictive_warming_enabled:
                    await self._perform_predictive_warming()
                
                await asyncio.sleep(self.config.pattern_update_interval)
                
            except Exception as e:
                # Log error and continue
                await asyncio.sleep(self.config.pattern_update_interval)
    
    async def _worker_loop(self, worker_id: str):
        """
Worker loop for processing warming jobs"""
        while self.running:
            try:
                # Get job from queue
                job = await asyncio.wait_for(self.warming_queue.get(), timeout=1.0)
                
                # Execute warming job
                await self._execute_warming_job(job, worker_id)
                
                # Mark job as done
                self.warming_queue.task_done()
                
            except asyncio.TimeoutError:
                # No job available, continue
                continue
            except Exception as e:
                # Log error and continue
                continue
    
    async def _trigger_startup_warming(self):
        """
Trigger warming on application startup"""
        context = {"trigger": WarmingTrigger.APPLICATION_START}
        await self.trigger_warming(WarmingTrigger.APPLICATION_START, context)
    
    async def _queue_warming_job(self, rule: WarmingRule, context: Dict[str, Any]):
        """Queue warming job for execution"""
        job = {
            "rule": rule,
            "context": context,
            "queued_at": datetime.utcnow()
        }
        
        try:
            await self.warming_queue.put(job)
        except asyncio.QueueFull:
            # Queue full, skip this job
            pass
    
    async def _execute_warming_job(self, job: Dict[str, Any], worker_id: str):
        """Execute a warming job"""
        rule = job["rule"]
        context = job["context"]
        start_time = time.time()
        
        try:
            self.metrics.total_warming_runs += 1
            
            # Check resource constraints
            if not self._check_resource_constraints():
                return
            
            # Execute rule-specific warming logic
            if rule.strategy == WarmingStrategy.ACCESS_PATTERN:
                await self._warm_by_access_pattern(rule, context)
            elif rule.strategy == WarmingStrategy.POPULARITY_BASED:
                await self._warm_by_popularity(rule, context)
            elif rule.strategy == WarmingStrategy.SCHEDULED:
                await self._warm_scheduled(rule, context)
            else:
                # Default warming logic
                await self._warm_default(rule, context)
            
            self.metrics.successful_runs += 1
            
        except Exception as e:
            self.metrics.failed_runs += 1
            
        finally:
            elapsed = time.time() - start_time
            self.metrics.total_warming_time += elapsed
            self.metrics.average_warming_time = (
                self.metrics.total_warming_time / max(self.metrics.total_warming_runs, 1)
            )
            self.metrics.last_warming_run = datetime.utcnow()
    
    def _should_run_scheduled_rule(self, rule: WarmingRule, current_time: datetime) -> bool:
        """Check if scheduled rule should run"""
        if not rule.schedule:
            return False
        
        try:
            cron = crontab.CronTab(rule.schedule)
            return cron.next(current_time) == 0
        except:
            return False
    
    async def _warm_by_access_pattern(self, rule: WarmingRule, context: Dict[str, Any]):
        """
Warm cache based on access patterns"""
        recommendations = self.get_warming_recommendations(rule.batch_size)
        
        for pattern in recommendations:
            if rule.value_loader:
                # Implementation would use actual cache client
                pass
    
    async def _warm_by_popularity(self, rule: WarmingRule, context: Dict[str, Any]):
        """
Warm cache based on data popularity"""
        # Get popular keys based on access frequency
        popular_patterns = sorted(
            self.access_patterns.values(),
            key=lambda p: p.access_frequency_per_hour,
            reverse=True
        )[:rule.batch_size]
        
        for pattern in popular_patterns:
            if rule.value_loader:
                # Implementation would use actual cache client
                pass
    
    async def _warm_scheduled(self, rule: WarmingRule, context: Dict[str, Any]):
        """
Execute scheduled warming"""
        # Implementation would execute the scheduled warming logic
        pass
    
    async def _warm_default(self, rule: WarmingRule, context: Dict[str, Any]):
        """
Default warming implementation"""
        # Implementation would execute generic warming logic
        pass
    
    async def _update_access_frequencies(self):
        """
Update access frequencies for all patterns"""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(hours=self.config.pattern_analysis_window_hours)
        
        for pattern in self.access_patterns.values():
            if pattern.last_access and pattern.last_access >= window_start:
                # Calculate frequency based on recent accesses
                hours_elapsed = (current_time - window_start).total_seconds() / 3600
                pattern.access_frequency_per_hour = pattern.access_count / hours_elapsed
            else:
                pattern.access_frequency_per_hour = 0.0
    
    async def _perform_predictive_warming(self):
        """
Perform ML-based predictive warming"""
        if not self.config.ml_model_path:
            return
        
        # This would integrate with ML models to predict future cache needs
        # Placeholder implementation
        pass
    
    def _check_resource_constraints(self) -> bool:
        """
Check if system resources allow warming"""
        if self.config.pause_on_high_load:
            # Check CPU and memory usage
            # This would integrate with system monitoring
            # Placeholder implementation
            return True
        
        return True


# Predefined warming rules for common scenarios
DEFAULT_RULES = [
    WarmingRule(
        name="startup_critical_data",
        strategy=WarmingStrategy.PROACTIVE,
        triggers=[WarmingTrigger.APPLICATION_START],
        priority=WarmingPriority.CRITICAL,
        data_source="SELECT * FROM critical_cache_keys",
        batch_size=50,
        concurrent_workers=10
    ),
    WarmingRule(
        name="user_session_data",
        strategy=WarmingStrategy.EVENT_TRIGGERED,
        triggers=[WarmingTrigger.USER_LOGIN],
        priority=WarmingPriority.HIGH,
        key_pattern="user:{user_id}:*",
        batch_size=20,
        cache_ttl=3600
    ),
    WarmingRule(
        name="popular_content",
        strategy=WarmingStrategy.POPULARITY_BASED,
        triggers=[WarmingTrigger.SCHEDULED_TIME],
        priority=WarmingPriority.MEDIUM,
        schedule="0 */4 * * *",  # Every 4 hours
        batch_size=100,
        min_access_frequency=5.0
    ),
    WarmingRule(
        name="tenant_activation_data",
        strategy=WarmingStrategy.DEPENDENCY_DRIVEN,
        triggers=[WarmingTrigger.TENANT_ACTIVATION],
        priority=WarmingPriority.HIGH,
        key_pattern="tenant:{tenant_id}:*",
        batch_size=30,
        concurrent_workers=5
    )
]

# Default configurations
DEFAULT_CONFIG = CacheWarmingConfig(rules=DEFAULT_RULES)

PRODUCTION_CONFIG = CacheWarmingConfig(
    rules=DEFAULT_RULES,
    enabled=True,
    warming_on_startup=True,
    global_rate_limit=2000,
    max_memory_usage_mb=4000,
    predictive_warming_enabled=True,
    access_pattern_tracking=True,
    max_concurrent_jobs=10,
    worker_thread_pool_size=50
)

DEVELOPMENT_CONFIG = CacheWarmingConfig(
    rules=DEFAULT_RULES[:2],  # Only critical rules
    global_rate_limit=500,
    max_memory_usage_mb=1000,
    predictive_warming_enabled=False,
    log_warming_operations=True,
    max_concurrent_jobs=3
)
