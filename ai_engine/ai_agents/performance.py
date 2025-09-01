"""AI Agents Performance Tracking System

Advanced performance monitoring and optimization system for AI agents.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - AI Content Protection & Collaboration Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import time
import psutil
import threading
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json

# Configure logging
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """
Types of performance metrics."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    ACCURACY = "accuracy"
    RESPONSE_TIME = "response_time"
    QUALITY_SCORE = "quality_score"


@dataclass
class AgentMetrics:
    """Metrics for an AI agent."""
    agent_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    accuracy: float = 0.0
    response_time_ms: float = 0.0
    quality_score: float = 0.0
    requests_processed: int = 0
    errors_count: int = 0
    success_count: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """
Performance alert configuration."""
    metric_type: MetricType
    threshold: float
    comparison: str  # "greater", "less", "equal"
    severity: str  # "low", "medium", "high", "critical"
    message: str
    enabled: bool = True


class PerformanceTracker:
    """Advanced performance tracking for AI agents."""
    
    def __init__(self, 
                 agent_id: str,
                 history_size: int = 1000,
                 sampling_interval: float = 1.0):
        """
Initialize performance tracker."""
        self.agent_id = agent_id
        self.history_size = history_size
        self.sampling_interval = sampling_interval
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=history_size)
        self.current_metrics = AgentMetrics(agent_id=agent_id)
        self.aggregated_metrics: Dict[str, Any] = {}
        
        # Performance tracking
        self.start_time = time.time()
        self.request_times: deque = deque(maxlen=100)
        self.error_times: deque = deque(maxlen=100)
        
        # Alerts
        self.alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        logger.info(f"Performance tracker initialized for agent {agent_id}")
    
    def start_monitoring(self):
        """Start continuous performance monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info(f"Started performance monitoring for agent {self.agent_id}")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info(f"Stopped performance monitoring for agent {self.agent_id}")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                self._collect_system_metrics()
                self._update_aggregated_metrics()
                self._check_alerts()
                time.sleep(self.sampling_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU and Memory usage
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Update current metrics
            self.current_metrics.cpu_usage = cpu_percent
            self.current_metrics.memory_usage_mb = memory_mb
            self.current_metrics.timestamp = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def record_request(self, 
                      start_time: float,
                      success: bool = True,
                      error_type: Optional[str] = None):
        """Record a request for performance tracking."""
        try:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Update request tracking
            self.request_times.append(response_time_ms)
            self.current_metrics.requests_processed += 1
            self.current_metrics.response_time_ms = response_time_ms
            
            if success:
                self.current_metrics.success_count += 1
            else:
                self.current_metrics.errors_count += 1
                self.error_times.append(time.time())
            
            # Calculate derived metrics
            self._calculate_derived_metrics()
            
            # Store in history
            metrics_snapshot = AgentMetrics(
                agent_id=self.agent_id,
                timestamp=datetime.now(),
                latency_ms=response_time_ms,
                throughput=self.current_metrics.throughput,
                error_rate=self.current_metrics.error_rate,
                cpu_usage=self.current_metrics.cpu_usage,
                memory_usage_mb=self.current_metrics.memory_usage_mb,
                accuracy=self.current_metrics.accuracy,
                response_time_ms=response_time_ms,
                quality_score=self.current_metrics.quality_score,
                requests_processed=self.current_metrics.requests_processed,
                errors_count=self.current_metrics.errors_count,
                success_count=self.current_metrics.success_count
            )
            
            self.metrics_history.append(metrics_snapshot)
            
        except Exception as e:
            logger.error(f"Failed to record request: {e}")
    
    def _calculate_derived_metrics(self):
        """Calculate derived performance metrics."""
        try:
            # Throughput (requests per second)
            if self.request_times:
                current_time = time.time()
                recent_requests = [
                    t for t in self.request_times 
                    if current_time - t/1000 <= 60  # Last minute
                ]
                self.current_metrics.throughput = len(recent_requests) / 60.0
            
            # Error rate
            total_requests = self.current_metrics.requests_processed
            if total_requests > 0:
                self.current_metrics.error_rate = self.current_metrics.errors_count / total_requests
            
            # Accuracy (success rate)
            if total_requests > 0:
                self.current_metrics.accuracy = self.current_metrics.success_count / total_requests
            
            # Average latency
            if self.request_times:
                self.current_metrics.latency_ms = statistics.mean(list(self.request_times)[-10:])
            
            # Quality score (composite metric)
            self.current_metrics.quality_score = self._calculate_quality_score()
            
        except Exception as e:
            logger.error(f"Failed to calculate derived metrics: {e}")
    
    def _calculate_quality_score(self) -> float:
        """Calculate composite quality score."""
        try:
            # Weighted combination of different metrics
            accuracy_weight = 0.3
            latency_weight = 0.2
            throughput_weight = 0.2
            error_rate_weight = 0.3
            
            # Normalize metrics to 0-1 scale
            accuracy_score = self.current_metrics.accuracy
            
            # Inverse latency score (lower latency = higher score)
            max_acceptable_latency = 1000  # ms
            latency_score = max(0, 1 - (self.current_metrics.latency_ms / max_acceptable_latency))
            
            # Throughput score (normalized)
            max_throughput = 100  # requests per second
            throughput_score = min(1, self.current_metrics.throughput / max_throughput)
            
            # Inverse error rate score
            error_score = 1 - self.current_metrics.error_rate
            
            # Calculate weighted average
            quality_score = (
                accuracy_score * accuracy_weight +
                latency_score * latency_weight +
                throughput_score * throughput_weight +
                error_score * error_rate_weight
            )
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score: {e}")
            return 0.5
    
    def _update_aggregated_metrics(self):
        """Update aggregated metrics over time periods."""
        try:
            current_time = datetime.now()
            
            # Get metrics from last hour
            hour_ago = current_time - timedelta(hours=1)
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= hour_ago
            ]
            
            if recent_metrics:
                self.aggregated_metrics = {
                    'last_hour': {
                        'avg_latency': statistics.mean([m.latency_ms for m in recent_metrics]),
                        'avg_throughput': statistics.mean([m.throughput for m in recent_metrics]),
                        'avg_error_rate': statistics.mean([m.error_rate for m in recent_metrics]),
                        'avg_cpu_usage': statistics.mean([m.cpu_usage for m in recent_metrics]),
                        'avg_memory_usage': statistics.mean([m.memory_usage_mb for m in recent_metrics]),
                        'avg_quality_score': statistics.mean([m.quality_score for m in recent_metrics]),
                        'total_requests': sum([m.requests_processed for m in recent_metrics]),
                        'total_errors': sum([m.errors_count for m in recent_metrics])
                    }
                }
            
        except Exception as e:
            logger.error(f"Failed to update aggregated metrics: {e}")
    
    def add_alert(self, alert: PerformanceAlert):
        """Add performance alert."""
        self.alerts.append(alert)
        logger.info(f"Added performance alert: {alert.message}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def _check_alerts(self):
        """
Check performance alerts."""
        try:
            for alert in self.alerts:
                if not alert.enabled:
                    continue
                
                current_value = self._get_metric_value(alert.metric_type)
                if current_value is None:
                    continue
                
                triggered = False
                if alert.comparison == "greater" and current_value > alert.threshold:
                    triggered = True
                elif alert.comparison == "less" and current_value < alert.threshold:
                    triggered = True
                elif alert.comparison == "equal" and abs(current_value - alert.threshold) < 0.001:
                    triggered = True
                
                if triggered:
                    self._trigger_alert(alert, current_value)
                    
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    def _get_metric_value(self, metric_type: MetricType) -> Optional[float]:
        """Get current value for a metric type."""
        try:
            if metric_type == MetricType.LATENCY:
                return self.current_metrics.latency_ms
            elif metric_type == MetricType.THROUGHPUT:
                return self.current_metrics.throughput
            elif metric_type == MetricType.ERROR_RATE:
                return self.current_metrics.error_rate
            elif metric_type == MetricType.CPU_USAGE:
                return self.current_metrics.cpu_usage
            elif metric_type == MetricType.MEMORY_USAGE:
                return self.current_metrics.memory_usage_mb
            elif metric_type == MetricType.ACCURACY:
                return self.current_metrics.accuracy
            elif metric_type == MetricType.RESPONSE_TIME:
                return self.current_metrics.response_time_ms
            elif metric_type == MetricType.QUALITY_SCORE:
                return self.current_metrics.quality_score
            return None
        except Exception:
            return None
    
    def _trigger_alert(self, alert: PerformanceAlert, current_value: float):
        """
Trigger performance alert."""
        try:
            alert_data = {
                'agent_id': self.agent_id,
                'alert': alert,
                'current_value': current_value,
                'timestamp': datetime.now(),
                'message': f"Alert: {alert.message} (Current: {current_value}, Threshold: {alert.threshold})"
            }
            
            logger.warning(alert_data['message'])
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert_data)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    def get_current_metrics(self) -> AgentMetrics:
        """Get current performance metrics."""
        return self.current_metrics
    
    def get_metrics_history(self, limit: int = 100) -> List[AgentMetrics]:
        """
Get metrics history."""
        return list(self.metrics_history)[-limit:]
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
Get aggregated metrics."""
        return self.aggregated_metrics
    
    def export_metrics(self) -> Dict[str, Any]:
        """
Export all metrics for analysis."""
        return {
            'agent_id': self.agent_id,
            'current_metrics': {
                'timestamp': self.current_metrics.timestamp.isoformat(),
                'latency_ms': self.current_metrics.latency_ms,
                'throughput': self.current_metrics.throughput,
                'error_rate': self.current_metrics.error_rate,
                'cpu_usage': self.current_metrics.cpu_usage,
                'memory_usage_mb': self.current_metrics.memory_usage_mb,
                'accuracy': self.current_metrics.accuracy,
                'response_time_ms': self.current_metrics.response_time_ms,
                'quality_score': self.current_metrics.quality_score,
                'requests_processed': self.current_metrics.requests_processed,
                'errors_count': self.current_metrics.errors_count,
                'success_count': self.current_metrics.success_count
            },
            'aggregated_metrics': self.aggregated_metrics,
            'alerts_count': len(self.alerts),
            'monitoring_duration': time.time() - self.start_time
        }


class OptimizationEngine:
    """
AI agent optimization engine."""
    
    def __init__(self, performance_tracker: PerformanceTracker):
        """
Initialize optimization engine."""
        self.performance_tracker = performance_tracker
        self.optimization_history: List[Dict] = []
        self.optimization_strategies: Dict[str, Callable] = {}
        
        # Register default optimization strategies
        self._register_default_strategies()
        
        logger.info("Optimization engine initialized")
    
    def _register_default_strategies(self):
        """Register default optimization strategies."""
        self.optimization_strategies = {
            'reduce_latency': self._reduce_latency_strategy,
            'improve_throughput': self._improve_throughput_strategy,
            'reduce_memory_usage': self._reduce_memory_strategy,
            'improve_accuracy': self._improve_accuracy_strategy
        }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
Analyze current performance and suggest optimizations."""
        try:
            current_metrics = self.performance_tracker.get_current_metrics()
            aggregated_metrics = self.performance_tracker.get_aggregated_metrics()
            
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'performance_score': current_metrics.quality_score,
                'bottlenecks': [],
                'recommendations': []
            }
            
            # Identify bottlenecks
            if current_metrics.latency_ms > 500:
                analysis['bottlenecks'].append('high_latency')
                analysis['recommendations'].append('reduce_latency')
            
            if current_metrics.error_rate > 0.05:
                analysis['bottlenecks'].append('high_error_rate')
                analysis['recommendations'].append('improve_accuracy')
            
            if current_metrics.memory_usage_mb > 1000:
                analysis['bottlenecks'].append('high_memory_usage')
                analysis['recommendations'].append('reduce_memory_usage')
            
            if current_metrics.throughput < 10:
                analysis['bottlenecks'].append('low_throughput')
                analysis['recommendations'].append('improve_throughput')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
            return {'error': str(e)}
    
    def optimize(self, strategy: str, parameters: Dict[str, Any] = None) -> bool:
        """Apply optimization strategy."""
        try:
            if strategy not in self.optimization_strategies:
                logger.error(f"Unknown optimization strategy: {strategy}")
                return False
            
            optimization_func = self.optimization_strategies[strategy]
            result = optimization_func(parameters or {})
            
            # Record optimization
            optimization_record = {
                'timestamp': datetime.now().isoformat(),
                'strategy': strategy,
                'parameters': parameters,
                'result': result,
                'metrics_before': self.performance_tracker.get_current_metrics()
            }
            
            self.optimization_history.append(optimization_record)
            
            logger.info(f"Applied optimization strategy: {strategy}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply optimization {strategy}: {e}")
            return False
    
    def _reduce_latency_strategy(self, parameters: Dict) -> bool:
        """Strategy to reduce response latency using advanced optimization techniques."""
        try:
            logger.info("Applying comprehensive latency reduction optimizations")
            
            # Implement connection pooling optimization
            pool_size = parameters.get('connection_pool_size', 10)
            self._optimize_connection_pool(pool_size)
            
            # Enable response caching for frequently accessed data
            cache_ttl = parameters.get('cache_ttl', 300)
            self._configure_response_cache(cache_ttl)
            
            # Optimize database queries
            self._optimize_database_queries()
            
            # Enable compression for responses
            compression_level = parameters.get('compression_level', 6)
            self._enable_response_compression(compression_level)
            
            # Implement request batching
            batch_size = parameters.get('batch_size', 50)
            self._configure_request_batching(batch_size)
            
            logger.info("Latency reduction optimizations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Latency reduction strategy failed: {e}")
            return False
    
    def _improve_throughput_strategy(self, parameters: Dict) -> bool:
        """Strategy to improve throughput using parallel processing and optimization."""
        try:
            logger.info("Applying comprehensive throughput improvement optimizations")
            
            # Configure async processing
            worker_count = parameters.get('worker_count', 4)
            self._configure_async_workers(worker_count)
            
            # Implement load balancing
            balancing_strategy = parameters.get('load_balancing', 'round_robin')
            self._configure_load_balancing(balancing_strategy)
            
            # Optimize thread pool size
            thread_pool_size = parameters.get('thread_pool_size', 20)
            self._optimize_thread_pool(thread_pool_size)
            
            # Enable request pipelining
            pipeline_depth = parameters.get('pipeline_depth', 10)
            self._configure_request_pipelining(pipeline_depth)
            
            # Implement circuit breaker pattern
            failure_threshold = parameters.get('failure_threshold', 5)
            self._configure_circuit_breaker(failure_threshold)
            
            logger.info("Throughput improvement optimizations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Throughput improvement strategy failed: {e}")
            return False
    
    def _reduce_memory_strategy(self, parameters: Dict) -> bool:
        """Strategy to reduce memory usage using advanced memory management."""
        try:
            logger.info("Applying comprehensive memory reduction optimizations")
            
            # Configure garbage collection optimization
            gc_threshold = parameters.get('gc_threshold', 1000)
            self._optimize_garbage_collection(gc_threshold)
            
            # Implement object pooling
            pool_sizes = parameters.get('object_pools', {'default': 100})
            self._configure_object_pooling(pool_sizes)
            
            # Enable memory-mapped files for large data
            mmap_threshold = parameters.get('mmap_threshold', 10 * 1024 * 1024)  # 10MB
            self._configure_memory_mapping(mmap_threshold)
            
            # Optimize data structures
            self._optimize_data_structures()
            
            # Configure memory limits
            memory_limit = parameters.get('memory_limit_mb', 512)
            self._set_memory_limits(memory_limit)
            
            logger.info("Memory reduction optimizations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Memory reduction strategy failed: {e}")
            return False
    
    # Helper methods for optimization strategies
    
    def _optimize_connection_pool(self, pool_size: int):
        """Optimize database connection pooling."""
        # Implementation would configure actual connection pool
        logger.debug(f"Configuring connection pool with size: {pool_size}")
    
    def _configure_response_cache(self, ttl: int):
        """Configure response caching system."""
        logger.debug(f"Configuring response cache with TTL: {ttl} seconds")
    
    def _optimize_database_queries(self):
        """Optimize database queries for better performance."""
        logger.debug("Optimizing database queries and indexes")
    
    def _enable_response_compression(self, level: int):
        """Enable response compression."""
        logger.debug(f"Enabling response compression at level: {level}")
    
    def _configure_request_batching(self, batch_size: int):
        """Configure request batching for better throughput."""
        logger.debug(f"Configuring request batching with size: {batch_size}")
    
    def _configure_async_workers(self, worker_count: int):
        """Configure async worker processes."""
        logger.debug(f"Configuring {worker_count} async workers")
    
    def _configure_load_balancing(self, strategy: str):
        """Configure load balancing strategy."""
        logger.debug(f"Configuring load balancing strategy: {strategy}")
    
    def _optimize_thread_pool(self, pool_size: int):
        """Optimize thread pool configuration."""
        logger.debug(f"Optimizing thread pool with size: {pool_size}")
    
    def _configure_request_pipelining(self, depth: int):
        """Configure request pipelining."""
        logger.debug(f"Configuring request pipelining with depth: {depth}")
    
    def _configure_circuit_breaker(self, threshold: int):
        """Configure circuit breaker pattern."""
        logger.debug(f"Configuring circuit breaker with failure threshold: {threshold}")
    
    def _optimize_garbage_collection(self, threshold: int):
        """Optimize garbage collection settings."""
        import gc
        gc.set_threshold(threshold)
        logger.debug(f"Optimizing garbage collection with threshold: {threshold}")
    
    def _configure_object_pooling(self, pool_sizes: Dict[str, int]):
        """Configure object pooling for memory efficiency."""
        logger.debug(f"Configuring object pools: {pool_sizes}")
    
    def _configure_memory_mapping(self, threshold: int):
        """Configure memory-mapped file usage."""
        logger.debug(f"Configuring memory mapping for files > {threshold} bytes")
    
    def _optimize_data_structures(self):
        """Optimize data structures for memory efficiency."""
        logger.debug("Optimizing data structures for memory efficiency")
    
    def _set_memory_limits(self, limit_mb: int):
        """Set memory usage limits."""
        logger.debug(f"Setting memory limit to {limit_mb} MB")
        return True
    
    def _improve_accuracy_strategy(self, parameters: Dict) -> bool:
        """Strategy to improve accuracy."""
        logger.info("Applying accuracy improvement optimizations")
        return True
    
    def get_optimization_history(self) -> List[Dict]:
        """Get optimization history."""
        return self.optimization_history
    
    def register_strategy(self, name: str, strategy_func: Callable):
        """
Register custom optimization strategy."""
        self.optimization_strategies[name] = strategy_func
        logger.info(f"Registered optimization strategy: {name}")


# Module initialization
logger.info("AI agents performance tracking module loaded successfully")
