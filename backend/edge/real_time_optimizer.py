"""Real-time Optimizer for Edge Computing
=====================================

Advanced real-time optimization engine for edge computing infrastructure,
providing ultra-low latency optimization, resource allocation, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class OptimizationStrategy(str, Enum):
    """Real-time optimization strategies."""
    LATENCY_FIRST = "latency_first"
    THROUGHPUT_FIRST = "throughput_first"
    BALANCED = "balanced"
    ENERGY_EFFICIENT = "energy_efficient"
    COST_OPTIMIZED = "cost_optimized"
    ADAPTIVE = "adaptive"


class OptimizationScope(str, Enum):
    """Optimization scope levels."""
    GLOBAL = "global"
    REGIONAL = "regional"
    LOCAL = "local"
    APPLICATION = "application"
    SERVICE = "service"
    REQUEST = "request"


class MetricType(str, Enum):
    """Performance metric types."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    NETWORK_BANDWIDTH = "network_bandwidth"
    DISK_IO = "disk_io"
    CACHE_HIT_RATIO = "cache_hit_ratio"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"
    RESPONSE_TIME = "response_time"


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    source: str
    tags: Dict[str, str]
    confidence: float = 1.0


@dataclass
class OptimizationTarget:
    """Optimization target configuration."""
    metric_type: MetricType
    target_value: float
    tolerance: float
    priority: int
    weight: float = 1.0


@dataclass
class OptimizationResult:
    """Optimization result."""
    optimization_id: str
    timestamp: datetime
    strategy: OptimizationStrategy
    improvements: Dict[str, float]
    actions_taken: List[str]
    success: bool
    execution_time: float
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]


class RealTimeOptimizer:
    """Advanced real-time optimizer for edge computing."""
    
    def __init__(self, 
                 strategy -> None: OptimizationStrategy = OptimizationStrategy.ADAPTIVE,
                 optimization_interval -> None: float = 1.0,
                 metrics_window -> None: int = 100) -> None:
        self.strategy = strategy
        self.optimization_interval = optimization_interval
        self.metrics_window = metrics_window
        
        # Metrics storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=metrics_window))
        self.current_metrics: Dict[str, PerformanceMetric] = {}
        
        # Optimization state
        self.optimization_targets: List[OptimizationTarget] = []
        self.optimization_history: List[OptimizationResult] = []
        self.active_optimizations: Dict[str, asyncio.Task] = {}
        
        # Real-time analysis
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.prediction_engine = PredictionEngine()
        
        # Control flags
        self.running = False
        self.optimization_task: Optional[asyncio.Task] = None
        
        logger.info(f"RealTimeOptimizer initialized with strategy: {strategy}")
    
    async def start(self) -> None:
        """Start the real-time optimization engine."""
        if self.running:
            logger.warning("Optimizer already running")
            return
        
        self.running = True
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        logger.info("Real-time optimizer started")
    
    async def stop(self) -> None:
        """Stop the real-time optimization engine."""
        self.running = False
        
        # Cancel active optimizations
        for task in self.active_optimizations.values():
            task.cancel()
        
        if self.optimization_task:
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Real-time optimizer stopped")
    
    async def add_metric(self, metric -> None: PerformanceMetric) -> None:
        """Add a performance metric for optimization."""
        metric_key = f"{metric.source}_{metric.metric_type.value}"
        
        # Store current metric
        self.current_metrics[metric_key] = metric
        
        # Add to history
        self.metrics_history[metric_key].append(metric)
        
        # Update analyzers
        await self.trend_analyzer.update(metric)
        await self.anomaly_detector.update(metric)
        await self.prediction_engine.update(metric)
    
    def add_optimization_target(self, target -> None: OptimizationTarget) -> None:
        """Add an optimization target."""
        self.optimization_targets.append(target)
        logger.info(f"Added optimization target: {target.metric_type.value} = {target.target_value}")
    
    async def trigger_optimization(self, scope: OptimizationScope = OptimizationScope.LOCAL) -> OptimizationResult:
        """Trigger immediate optimization."""
        optimization_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Analyze current state
            analysis = await self._analyze_performance()
            
            # Determine optimization actions
            actions = await self._determine_actions(analysis, scope)
            
            # Execute optimizations
            execution_results = await self._execute_optimizations(actions)
            
            # Measure improvements
            improvements = await self._measure_improvements(analysis)
            
            result = OptimizationResult(
                optimization_id=optimization_id,
                timestamp=datetime.now(),
                strategy=self.strategy,
                improvements=improvements,
                actions_taken=[action['type'] for action in actions],
                success=execution_results['success'],
                execution_time=time.time() - start_time,
                metrics_before=analysis['current_metrics'],
                metrics_after=await self._get_current_metrics_summary()
            )
            
            self.optimization_history.append(result)
            
            logger.info(f"Optimization {optimization_id} completed: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return OptimizationResult(
                optimization_id=optimization_id,
                timestamp=datetime.now(),
                strategy=self.strategy,
                improvements={},
                actions_taken=[],
                success=False,
                execution_time=time.time() - start_time,
                metrics_before={},
                metrics_after={}
            )
    
    async def _optimization_loop(self) -> None:
        """Main optimization loop."""
        while self.running:
            try:
                # Check if optimization is needed
                if await self._should_optimize():
                    await self.trigger_optimization()
                
                await asyncio.sleep(self.optimization_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(self.optimization_interval)
    
    async def _should_optimize(self) -> bool:
        """Determine if optimization should be triggered."""
        # Check if we have enough metrics
        if not self.current_metrics:
            return False
        
        # Check for target violations
        for target in self.optimization_targets:
            current_value = await self._get_metric_value(target.metric_type)
            if current_value is None:
                continue
            
            deviation = abs(current_value - target.target_value) / target.target_value
            if deviation > target.tolerance:
                return True
        
        # Check for anomalies
        if await self.anomaly_detector.has_anomalies():
            return True
        
        # Check for negative trends
        if await self.trend_analyzer.has_negative_trends():
            return True
        
        return False
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance state."""
        analysis = {
            'current_metrics': await self._get_current_metrics_summary(),
            'trends': await self.trend_analyzer.get_trends(),
            'anomalies': await self.anomaly_detector.get_anomalies(),
            'predictions': await self.prediction_engine.get_predictions(),
            'bottlenecks': await self._identify_bottlenecks(),
            'target_violations': await self._check_target_violations()
        }
        return analysis
    
    async def _determine_actions(self, analysis: Dict[str, Any], scope: OptimizationScope) -> List[Dict[str, Any]]:
        """Determine optimization actions based on analysis."""
        actions = []
        
        # Strategy-specific action determination
        if self.strategy == OptimizationStrategy.LATENCY_FIRST:
            actions.extend(await self._get_latency_actions(analysis))
        elif self.strategy == OptimizationStrategy.THROUGHPUT_FIRST:
            actions.extend(await self._get_throughput_actions(analysis))
        elif self.strategy == OptimizationStrategy.BALANCED:
            actions.extend(await self._get_balanced_actions(analysis))
        elif self.strategy == OptimizationStrategy.ADAPTIVE:
            actions.extend(await self._get_adaptive_actions(analysis))
        
        # Filter actions by scope
        actions = [action for action in actions if action.get('scope', scope) == scope]
        
        return actions
    
    async def _execute_optimizations(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute optimization actions."""
        results = {'success': True, 'executed': [], 'failed': []}
        
        for action in actions:
            try:
                await self._execute_single_action(action)
                results['executed'].append(action)
                logger.info(f"Executed optimization action: {action['type']}")
            except Exception as e:
                results['failed'].append({'action': action, 'error': str(e)})
                logger.error(f"Failed to execute action {action['type']}: {e}")
                results['success'] = False
        
        return results
    
    async def _execute_single_action(self, action -> None: Dict[str, Any]) -> None:
        """Execute a single optimization action."""
        action_type = action['type']
        
        if action_type == 'adjust_resource_allocation':
            await self._adjust_resource_allocation(action['parameters'])
        elif action_type == 'optimize_caching':
            await self._optimize_caching(action['parameters'])
        elif action_type == 'load_balance':
            await self._optimize_load_balancing(action['parameters'])
        elif action_type == 'scale_resources':
            await self._scale_resources(action['parameters'])
        elif action_type == 'tune_parameters':
            await self._tune_parameters(action['parameters'])
        else:
            logger.warning(f"Unknown action type: {action_type}")
    
    async def _get_latency_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get latency-focused optimization actions."""
        actions = []
        
        if analysis['current_metrics'].get('latency', 0) > 5.0:  # >5ms
            actions.append({
                'type': 'optimize_caching',
                'priority': 1,
                'parameters': {'strategy': 'aggressive_prefetch'}
            })
            
            actions.append({
                'type': 'adjust_resource_allocation',
                'priority': 2,
                'parameters': {'cpu_priority': 'high', 'memory_allocation': 'increased'}
            })
        
        return actions
    
    async def _get_throughput_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get throughput-focused optimization actions."""
        actions = []
        
        if analysis['current_metrics'].get('throughput', 0) < 1000:  # <1000 RPS
            actions.append({
                'type': 'scale_resources',
                'priority': 1,
                'parameters': {'direction': 'up', 'resource_type': 'compute'}
            })
            
            actions.append({
                'type': 'load_balance',
                'priority': 2,
                'parameters': {'strategy': 'round_robin', 'health_check_interval': 1}
            })
        
        return actions
    
    async def _get_balanced_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get balanced optimization actions."""
        actions = []
        
        # Combine latency and throughput optimizations with lower priority
        latency_actions = await self._get_latency_actions(analysis)
        throughput_actions = await self._get_throughput_actions(analysis)
        
        # Reduce priority of all actions
        for action in latency_actions + throughput_actions:
            action['priority'] = action.get('priority', 1) + 1
            actions.append(action)
        
        return actions
    
    async def _get_adaptive_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get adaptive optimization actions based on current conditions."""
        actions = []
        
        # Analyze which optimization is most needed
        metrics = analysis['current_metrics']
        
        latency_score = metrics.get('latency', 0) / 10.0  # Normalize to 0-1
        throughput_score = (1000 - metrics.get('throughput', 1000)) / 1000.0  # Normalize to 0-1
        
        if latency_score > throughput_score:
            actions.extend(await self._get_latency_actions(analysis))
        else:
            actions.extend(await self._get_throughput_actions(analysis))
        
        return actions
    
    async def _get_metric_value(self, metric_type: MetricType) -> Optional[float]:
        """Get current value for a specific metric type."""
        for key, metric in self.current_metrics.items():
            if metric.metric_type == metric_type:
                return metric.value
        return None
    
    async def _get_current_metrics_summary(self) -> Dict[str, float]:
        """Get summary of current metrics."""
        summary = {}
        for key, metric in self.current_metrics.items():
            summary[metric.metric_type.value] = metric.value
        return summary
    
    async def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        metrics = await self._get_current_metrics_summary()
        
        if metrics.get('cpu_utilization', 0) > 80:
            bottlenecks.append('cpu_bottleneck')
        
        if metrics.get('memory_utilization', 0) > 85:
            bottlenecks.append('memory_bottleneck')
        
        if metrics.get('network_bandwidth', 0) > 90:
            bottlenecks.append('network_bottleneck')
        
        if metrics.get('disk_io', 0) > 80:
            bottlenecks.append('disk_bottleneck')
        
        return bottlenecks
    
    async def _check_target_violations(self) -> List[Dict[str, Any]]:
        """Check for optimization target violations."""
        violations = []
        
        for target in self.optimization_targets:
            current_value = await self._get_metric_value(target.metric_type)
            if current_value is None:
                continue
            
            deviation = abs(current_value - target.target_value) / target.target_value
            if deviation > target.tolerance:
                violations.append({
                    'target': target,
                    'current_value': current_value,
                    'deviation': deviation
                })
        
        return violations
    
    async def _measure_improvements(self, baseline_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Measure optimization improvements."""
        improvements = {}
        
        # Wait a moment for metrics to update
        await asyncio.sleep(0.5)
        
        current_metrics = await self._get_current_metrics_summary()
        baseline_metrics = baseline_analysis['current_metrics']
        
        for metric_name, current_value in current_metrics.items():
            baseline_value = baseline_metrics.get(metric_name, 0)
            if baseline_value > 0:
                improvement = (current_value - baseline_value) / baseline_value * 100
                improvements[metric_name] = improvement
        
        return improvements
    
    # Placeholder implementation methods
    async def _adjust_resource_allocation(self, parameters -> None: Dict[str, Any]) -> None:
        """Adjust resource allocation."""
        logger.info(f"Adjusting resource allocation: {parameters}")
        # Implementation would integrate with resource manager
    
    async def _optimize_caching(self, parameters -> None: Dict[str, Any]) -> None:
        """Optimize caching strategy."""
        logger.info(f"Optimizing caching: {parameters}")
        # Implementation would integrate with edge cache
    
    async def _optimize_load_balancing(self, parameters -> None: Dict[str, Any]) -> None:
        """Optimize load balancing."""
        logger.info(f"Optimizing load balancing: {parameters}")
        # Implementation would integrate with load balancer
    
    async def _scale_resources(self, parameters -> None: Dict[str, Any]) -> None:
        """Scale resources up or down."""
        logger.info(f"Scaling resources: {parameters}")
        # Implementation would integrate with orchestration
    
    async def _tune_parameters(self, parameters -> None: Dict[str, Any]) -> None:
        """Tune system parameters."""
        logger.info(f"Tuning parameters: {parameters}")
        # Implementation would tune various system parameters


class TrendAnalyzer:
    """Analyze performance trends."""
    
    def __init__(self) -> None:
        self.trends: Dict[str, List[float]] = defaultdict(list)
    
    async def update(self, metric -> None: PerformanceMetric) -> None:
        """Update trend analysis with new metric."""
        key = f"{metric.source}_{metric.metric_type.value}"
        self.trends[key].append(metric.value)
        
        # Keep only recent values
        if len(self.trends[key]) > 50:
            self.trends[key] = self.trends[key][-50:]
    
    async def get_trends(self) -> Dict[str, str]:
        """Get current trends for all metrics."""
        trends = {}
        
        for key, values in self.trends.items():
            if len(values) >= 5:
                recent_trend = self._calculate_trend(values[-10:])
                trends[key] = recent_trend
        
        return trends
    
    async def has_negative_trends(self) -> bool:
        """Check if there are any negative trends."""
        trends = await self.get_trends()
        return any(trend == 'declining' for trend in trends.values())
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        else:
            return 'stable'


class AnomalyDetector:
    """Detect performance anomalies."""
    
    def __init__(self, sensitivity -> None: float = 2.0) -> None:
        self.sensitivity = sensitivity
        self.baseline_stats: Dict[str, Dict[str, float]] = {}
        self.recent_anomalies: List[Dict[str, Any]] = []
    
    async def update(self, metric -> None: PerformanceMetric) -> None:
        """Update anomaly detection with new metric."""
        key = f"{metric.source}_{metric.metric_type.value}"
        
        # Initialize baseline if not exists
        if key not in self.baseline_stats:
            self.baseline_stats[key] = {'mean': metric.value, 'std': 0, 'count': 1}
            return
        
        # Update baseline statistics
        stats = self.baseline_stats[key]
        stats['count'] += 1
        old_mean = stats['mean']
        stats['mean'] = old_mean + (metric.value - old_mean) / stats['count']
        
        if stats['count'] > 1:
            stats['std'] = (stats['std'] * (stats['count'] - 2) + 
                           (metric.value - old_mean) * (metric.value - stats['mean'])) / (stats['count'] - 1)
        
        # Check for anomaly
        if await self._is_anomaly(metric, stats):
            self.recent_anomalies.append({
                'metric': metric,
                'timestamp': metric.timestamp,
                'deviation': abs(metric.value - stats['mean']) / max(stats['std'], 0.1)
            })
            
            # Keep only recent anomalies
            cutoff_time = datetime.now() - timedelta(minutes=10)
            self.recent_anomalies = [a for a in self.recent_anomalies if a['timestamp'] > cutoff_time]
    
    async def has_anomalies(self) -> bool:
        """Check if there are recent anomalies."""
        return len(self.recent_anomalies) > 0
    
    async def get_anomalies(self) -> List[Dict[str, Any]]:
        """Get recent anomalies."""
        return self.recent_anomalies.copy()
    
    async def _is_anomaly(self, metric: PerformanceMetric, stats: Dict[str, float]) -> bool:
        """Check if metric value is anomalous."""
        if stats['count'] < 10 or stats['std'] == 0:
            return False
        
        z_score = abs(metric.value - stats['mean']) / stats['std']
        return z_score > self.sensitivity


class PredictionEngine:
    """Predict future performance metrics."""
    
    def __init__(self) -> None:
        self.metric_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
    
    async def update(self, metric -> None: PerformanceMetric) -> None:
        """Update prediction engine with new metric."""
        key = f"{metric.source}_{metric.metric_type.value}"
        self.metric_history[key].append((metric.timestamp, metric.value))
        
        # Keep only recent history
        if len(self.metric_history[key]) > 100:
            self.metric_history[key] = self.metric_history[key][-100:]
    
    async def get_predictions(self, horizon_minutes: int = 5) -> Dict[str, float]:
        """Get predictions for specified time horizon."""
        predictions = {}
        
        for key, history in self.metric_history.items():
            if len(history) >= 10:
                prediction = self._predict_value(history, horizon_minutes)
                predictions[key] = prediction
        
        return predictions
    
    def _predict_value(self, history: List[Tuple[datetime, float]], horizon_minutes: int) -> float:
        """Predict future value using simple linear extrapolation."""
        if len(history) < 2:
            return history[-1][1] if history else 0.0
        
        # Use last 10 points for prediction
        recent_history = history[-10:]
        
        # Calculate trend
        values = [point[1] for point in recent_history]
        trend = (values[-1] - values[0]) / len(values)
        
        # Extrapolate
        prediction = values[-1] + trend * horizon_minutes
        return max(0, prediction)  # Ensure non-negative


def create_real_time_optimizer(
    strategy: OptimizationStrategy = OptimizationStrategy.ADAPTIVE,
    optimization_interval: float = 1.0,
    metrics_window: int = 100
) -> RealTimeOptimizer:
    """Create and configure a real-time optimizer instance."""
    return RealTimeOptimizer(
        strategy=strategy,
        optimization_interval=optimization_interval,
        metrics_window=metrics_window
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_optimizer() -> None:
        """Test the real-time optimizer."""
        optimizer = create_real_time_optimizer()
        
        # Add optimization targets
        optimizer.add_optimization_target(OptimizationTarget(
            metric_type=MetricType.LATENCY,
            target_value=2.0,  # 2ms target
            tolerance=0.5,     # 50% tolerance
            priority=1
        ))
        
        # Start optimizer
        await optimizer.start()
        
        # Simulate some metrics
        for i in range(10):
            await optimizer.add_metric(PerformanceMetric(
                metric_type=MetricType.LATENCY,
                value=3.0 + i * 0.5,  # Increasing latency
                timestamp=datetime.now(),
                source="test_service",
                tags={"environment": "test"}
            ))
            
            await asyncio.sleep(0.5)
        
        # Trigger optimization
        result = await optimizer.trigger_optimization()
        print(f"Optimization result: {result.success}")
        
        # Stop optimizer
        await optimizer.stop()
    
    # Run test
    asyncio.run(test_optimizer())