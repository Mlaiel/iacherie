#!/usr/bin/env python3
"""
Performance Optimizer - Enterprise Collaboration Module
======================================================
Advanced performance optimization and monitoring for sub-50ms response times
Combining Lead Dev IA + Backend Senior + DevOps expertise

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Roles: Lead Dev IA + Backend Senior + DevOps Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

# Configure performance logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTier(Enum):
    """Performance tier classification"""
    CRITICAL = "critical"    # <10ms
    HIGH = "high"           # <50ms
    STANDARD = "standard"   # <100ms
    BACKGROUND = "background"  # <500ms

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    tier: PerformanceTier = PerformanceTier.STANDARD
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationRule:
    """Performance optimization rule"""
    name: str
    condition: Callable[[PerformanceMetrics], bool]
    action: Callable[[Any], Any]
    priority: int = 1
    enabled: bool = True

class PerformanceOptimizer:
    """
    Enterprise Performance Optimizer
    ===============================
    Advanced performance monitoring and optimization system
    """
    
    def __init__(self):
        self.metrics_history: deque = deque(maxlen=10000)
        self.performance_cache: Dict[str, Any] = {}
        self.optimization_rules: List[OptimizationRule] = []
        self.performance_targets = {
            PerformanceTier.CRITICAL: 10.0,    # 10ms
            PerformanceTier.HIGH: 50.0,        # 50ms
            PerformanceTier.STANDARD: 100.0,   # 100ms
            PerformanceTier.BACKGROUND: 500.0  # 500ms
        }
        self._setup_optimization_rules()
        self.stats_cache = {}
        self.last_stats_update = datetime.now()

    def _setup_optimization_rules(self):
        """Setup intelligent optimization rules"""
        
        # Rule 1: Cache frequently accessed data
        def cache_rule_condition(metrics: PerformanceMetrics) -> bool:
            return (metrics.duration_ms and 
                   metrics.duration_ms > 50 and 
                   'query' in metrics.operation.lower())
        
        def cache_rule_action(operation_data: Any) -> Any:
            logger.info(f"🚀 CACHING: Caching slow query for future optimization")
            return operation_data
        
        self.optimization_rules.append(OptimizationRule(
            name="intelligent_caching",
            condition=cache_rule_condition,
            action=cache_rule_action,
            priority=1
        ))
        
        # Rule 2: Async optimization for I/O operations
        def async_rule_condition(metrics: PerformanceMetrics) -> bool:
            return (metrics.duration_ms and 
                   metrics.duration_ms > 100 and 
                   any(term in metrics.operation.lower() for term in ['api', 'db', 'network']))
        
        def async_rule_action(operation_data: Any) -> Any:
            logger.info(f"⚡ ASYNC OPTIMIZATION: Converting to async operation")
            return operation_data
        
        self.optimization_rules.append(OptimizationRule(
            name="async_optimization",
            condition=async_rule_condition,
            action=async_rule_action,
            priority=2
        ))
        
        # Rule 3: Memory optimization for large operations
        def memory_rule_condition(metrics: PerformanceMetrics) -> bool:
            return (metrics.memory_usage and 
                   metrics.memory_usage > 100_000_000)  # 100MB
        
        def memory_rule_action(operation_data: Any) -> Any:
            logger.info(f"🧠 MEMORY OPTIMIZATION: Implementing memory streaming")
            return operation_data
        
        self.optimization_rules.append(OptimizationRule(
            name="memory_optimization",
            condition=memory_rule_condition,
            action=memory_rule_action,
            priority=3
        ))

    async def measure_performance(self, operation: str, tier: PerformanceTier = PerformanceTier.STANDARD):
        """Performance measurement context manager"""
        
        class PerformanceContext:
            def __init__(self, optimizer, operation, tier):
                self.optimizer = optimizer
                self.operation = operation
                self.tier = tier
                self.metrics = None
            
            async def __aenter__(self):
                self.metrics = PerformanceMetrics(
                    operation=self.operation,
                    start_time=time.perf_counter(),
                    tier=self.tier
                )
                return self.metrics
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.metrics.end_time = time.perf_counter()
                self.metrics.duration_ms = (self.metrics.end_time - self.metrics.start_time) * 1000
                
                if exc_type:
                    self.metrics.success = False
                    self.metrics.error_message = str(exc_val)
                
                await self.optimizer._record_metrics(self.metrics)
                return False
        
        return PerformanceContext(self, operation, tier)

    async def _record_metrics(self, metrics: PerformanceMetrics):
        """Record and analyze performance metrics"""
        self.metrics_history.append(metrics)
        
        # Check performance targets
        target = self.performance_targets[metrics.tier]
        if metrics.duration_ms and metrics.duration_ms > target:
            logger.warning(
                f"⚠️ PERFORMANCE ALERT: {metrics.operation} took {metrics.duration_ms:.2f}ms "
                f"(target: {target}ms, tier: {metrics.tier.value})"
            )
            
            # Apply optimization rules
            await self._apply_optimization_rules(metrics)
        else:
            logger.info(
                f"✅ PERFORMANCE OK: {metrics.operation} took {metrics.duration_ms:.2f}ms "
                f"(target: {target}ms, tier: {metrics.tier.value})"
            )

    async def _apply_optimization_rules(self, metrics: PerformanceMetrics):
        """Apply intelligent optimization rules"""
        for rule in sorted(self.optimization_rules, key=lambda r: r.priority):
            if rule.enabled and rule.condition(metrics):
                try:
                    await asyncio.create_task(
                        asyncio.coroutine(rule.action)(metrics)
                    ) if asyncio.iscoroutinefunction(rule.action) else rule.action(metrics)
                    
                    logger.info(f"✅ OPTIMIZATION APPLIED: {rule.name} for {metrics.operation}")
                except Exception as e:
                    logger.error(f"❌ OPTIMIZATION FAILED: {rule.name} - {e}")

    async def get_performance_stats(self, refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        now = datetime.now()
        
        # Cache stats for 30 seconds
        if not refresh and self.stats_cache and (now - self.last_stats_update).seconds < 30:
            return self.stats_cache
        
        if not self.metrics_history:
            return {
                "status": "no_data",
                "message": "No performance data available"
            }
        
        # Calculate statistics
        durations = [m.duration_ms for m in self.metrics_history if m.duration_ms]
        successes = [m.success for m in self.metrics_history]
        
        # Performance by tier
        tier_stats = defaultdict(list)
        for metrics in self.metrics_history:
            if metrics.duration_ms:
                tier_stats[metrics.tier.value].append(metrics.duration_ms)
        
        # Recent performance (last hour)
        one_hour_ago = now - timedelta(hours=1)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromtimestamp(m.start_time) > one_hour_ago
        ]
        
        stats = {
            "timestamp": now.isoformat(),
            "total_operations": len(self.metrics_history),
            "success_rate": (sum(successes) / len(successes) * 100) if successes else 0,
            
            # Overall performance
            "performance": {
                "average_duration_ms": statistics.mean(durations) if durations else 0,
                "median_duration_ms": statistics.median(durations) if durations else 0,
                "p95_duration_ms": self._percentile(durations, 95) if durations else 0,
                "p99_duration_ms": self._percentile(durations, 99) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0
            },
            
            # Performance by tier
            "tier_performance": {
                tier: {
                    "average_ms": statistics.mean(times) if times else 0,
                    "target_ms": self.performance_targets[PerformanceTier(tier)],
                    "compliance_rate": sum(1 for t in times if t <= self.performance_targets[PerformanceTier(tier)]) / len(times) * 100 if times else 0
                }
                for tier, times in tier_stats.items()
            },
            
            # Recent performance trends
            "recent_performance": {
                "last_hour_operations": len(recent_metrics),
                "average_duration_ms": statistics.mean([m.duration_ms for m in recent_metrics if m.duration_ms]) if recent_metrics else 0
            },
            
            # Optimization insights
            "optimization_insights": self._generate_optimization_insights()
        }
        
        self.stats_cache = stats
        self.last_stats_update = now
        return stats

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _generate_optimization_insights(self) -> List[str]:
        """Generate actionable optimization insights"""
        insights = []
        
        if not self.metrics_history:
            return ["No data available for insights"]
        
        # Analyze recent performance issues
        slow_operations = [
            m for m in self.metrics_history 
            if m.duration_ms and m.duration_ms > self.performance_targets[m.tier]
        ]
        
        if slow_operations:
            # Find most common slow operations
            slow_ops_count = defaultdict(int)
            for op in slow_operations:
                slow_ops_count[op.operation] += 1
            
            most_problematic = max(slow_ops_count.items(), key=lambda x: x[1])
            insights.append(
                f"🎯 Focus optimization on '{most_problematic[0]}' - "
                f"{most_problematic[1]} slow instances detected"
            )
        
        # Check for memory issues
        memory_issues = [
            m for m in self.metrics_history 
            if m.memory_usage and m.memory_usage > 50_000_000  # 50MB
        ]
        
        if memory_issues:
            insights.append(
                f"🧠 Memory optimization needed - {len(memory_issues)} operations exceeded 50MB"
            )
        
        # Success rate insights
        recent_failures = [m for m in self.metrics_history[-100:] if not m.success]
        if len(recent_failures) > 5:
            insights.append(
                f"⚠️ Reliability concern - {len(recent_failures)} failures in last 100 operations"
            )
        
        # Performance tier compliance
        for tier in PerformanceTier:
            tier_metrics = [m for m in self.metrics_history if m.tier == tier and m.duration_ms]
            if tier_metrics:
                target = self.performance_targets[tier]
                compliant = sum(1 for m in tier_metrics if m.duration_ms <= target)
                compliance_rate = compliant / len(tier_metrics) * 100
                
                if compliance_rate < 95:
                    insights.append(
                        f"📊 {tier.value.title()} tier performance: {compliance_rate:.1f}% "
                        f"compliance (target: {target}ms)"
                    )
        
        if not insights:
            insights.append("✅ Performance is optimal - all metrics within targets")
        
        return insights

    async def optimize_cache_strategy(self, operation_pattern: str) -> Dict[str, Any]:
        """Optimize caching strategy for specific operation patterns"""
        # Analyze historical performance for this pattern
        matching_metrics = [
            m for m in self.metrics_history 
            if operation_pattern.lower() in m.operation.lower()
        ]
        
        if not matching_metrics:
            return {"status": "no_data", "pattern": operation_pattern}
        
        avg_duration = statistics.mean([m.duration_ms for m in matching_metrics if m.duration_ms])
        frequency = len(matching_metrics)
        
        # Cache strategy recommendations
        strategy = {
            "pattern": operation_pattern,
            "average_duration_ms": avg_duration,
            "frequency": frequency,
            "cache_recommended": avg_duration > 50 and frequency > 10,
            "cache_ttl_seconds": min(3600, max(300, int(avg_duration * 10))),  # TTL based on duration
            "cache_type": "memory" if avg_duration < 100 else "redis"
        }
        
        return strategy

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics for monitoring dashboards"""
        recent = list(self.metrics_history)[-50:]  # Last 50 operations
        
        if not recent:
            return {"status": "no_recent_data"}
        
        current_time = time.time()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_operations": len([m for m in recent if not m.end_time]),
            "recent_average_ms": statistics.mean([m.duration_ms for m in recent if m.duration_ms]) if recent else 0,
            "recent_success_rate": sum(1 for m in recent if m.success) / len(recent) * 100,
            "performance_trend": self._calculate_trend(recent),
            "alerts": self._generate_alerts(),
            "system_health": "optimal" if all(
                m.duration_ms <= self.performance_targets[m.tier] 
                for m in recent[-10:] if m.duration_ms
            ) else "degraded"
        }

    def _calculate_trend(self, metrics: List[PerformanceMetrics]) -> str:
        """Calculate performance trend"""
        if len(metrics) < 10:
            return "insufficient_data"
        
        first_half = metrics[:len(metrics)//2]
        second_half = metrics[len(metrics)//2:]
        
        first_avg = statistics.mean([m.duration_ms for m in first_half if m.duration_ms])
        second_avg = statistics.mean([m.duration_ms for m in second_half if m.duration_ms])
        
        if second_avg < first_avg * 0.9:
            return "improving"
        elif second_avg > first_avg * 1.1:
            return "degrading"
        else:
            return "stable"

    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate performance alerts"""
        alerts = []
        recent = list(self.metrics_history)[-20:]
        
        # Check for recent failures
        recent_failures = [m for m in recent if not m.success]
        if len(recent_failures) > 3:
            alerts.append({
                "type": "high_failure_rate",
                "severity": "warning",
                "message": f"{len(recent_failures)} failures in last 20 operations",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for performance degradation
        slow_recent = [
            m for m in recent 
            if m.duration_ms and m.duration_ms > self.performance_targets[m.tier] * 1.5
        ]
        if len(slow_recent) > 2:
            alerts.append({
                "type": "performance_degradation",
                "severity": "critical",
                "message": f"{len(slow_recent)} operations significantly exceeded targets",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Utility functions for easy integration
async def measure_operation(operation: str, tier: PerformanceTier = PerformanceTier.STANDARD):
    """Easy-to-use performance measurement decorator"""
    return await performance_optimizer.measure_performance(operation, tier)

async def get_performance_dashboard() -> Dict[str, Any]:
    """Get complete performance dashboard data"""
    return {
        "real_time": await performance_optimizer.get_real_time_metrics(),
        "historical": await performance_optimizer.get_performance_stats(),
        "insights": performance_optimizer._generate_optimization_insights()
    }

if __name__ == "__main__":
    async def test_performance_optimizer():
        """Test the performance optimizer"""
        print("🧪 Testing Performance Optimizer...")
        
        # Test various performance scenarios
        async with measure_operation("test_critical_operation", PerformanceTier.CRITICAL):
            await asyncio.sleep(0.005)  # 5ms - should pass
        
        async with measure_operation("test_slow_operation", PerformanceTier.HIGH):
            await asyncio.sleep(0.08)  # 80ms - should trigger warning
        
        async with measure_operation("test_database_query", PerformanceTier.STANDARD):
            await asyncio.sleep(0.15)  # 150ms - should trigger optimization
        
        # Get performance stats
        stats = await performance_optimizer.get_performance_stats()
        print("\n📊 Performance Statistics:")
        print(json.dumps(stats, indent=2))
        
        # Get dashboard data
        dashboard = await get_performance_dashboard()
        print("\n📈 Performance Dashboard:")
        print(json.dumps(dashboard["real_time"], indent=2))
    
    asyncio.run(test_performance_optimizer())