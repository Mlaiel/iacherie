"""Performance Tracker for IA Influencer Agent Platform
====================================================

Industrial-grade performance monitoring with AI-powered bottleneck detection,
predictive performance analytics, and automated optimization for content
protection, fingerprinting, and revenue tracking systems.

Features:
    - Real-time performance profiling with microsecond precision
- AI-powered bottleneck detection and root cause analysis
- Content fingerprinting performance optimization
- Revenue tracking system performance monitoring
- User experience impact assessment
- Predictive performance degradation alerts
- Automated scaling recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""

import asyncio
import time
import threading
import psutil
import logging
import numpy as np
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import aioredis
import json
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceCategory(Enum):
    """
Performance monitoring categories"""

    API_ENDPOINT = "api_endpoint"
    DATABASE_QUERY = "database_query"
    AI_PROCESSING = "ai_processing"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    CONTENT_PROTECTION = "content_protection"
    REVENUE_CALCULATION = "revenue_calculation"
    USER_AUTHENTICATION = "user_authentication"
    FILE_PROCESSING = "file_processing"
    EXTERNAL_API_CALL = "external_api_call"
    CACHE_OPERATION = "cache_operation"


class PerformanceImpact(Enum):
    """Business impact levels for performance issues"""

    CRITICAL = "critical"  # Affects core business functions
    HIGH = "high"         # Affects user experience significantly
    MEDIUM = "medium"     # Noticeable but manageable
    LOW = "low"          # Minor optimization opportunity


@dataclass
class PerformanceMetric:
    """Enhanced performance metric with business context"""
    name: str
    value: float
    timestamp: datetime
    category: PerformanceCategory
    unit: str = "ms"
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    business_impact: PerformanceImpact = PerformanceImpact.MEDIUM
    user_experience_score: float = 1.0  # 0.0 to 1.0, higher is better
    optimization_potential: float = 0.0  # 0.0 to 1.0, higher means more optimization potential


@dataclass
class PerformanceProfile:
    """Enhanced performance profile with statistical analysis"""
    operation: str
    category: PerformanceCategory
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    median_time: float = 0.0
    p50_time: float = 0.0
    p90_time: float = 0.0
    p95_time: float = 0.0
    p99_time: float = 0.0
    std_deviation: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    last_call: Optional[datetime] = None
    samples: deque = field(default_factory=lambda: deque(maxlen=1000))
    hourly_stats: Dict[int, Dict[str, float]] = field(default_factory=dict)
    trend_coefficient: float = 0.0  # Performance trend over time
    bottleneck_score: float = 0.0   # 0.0 to 1.0, higher means more likely bottleneck
    optimization_recommendations: List[str] = field(default_factory=list)


@dataclass
class ResourceUsage:
    """
Enhanced system resource usage with trend analysis"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    active_threads: int
    open_files: int
    # AI-specific metrics
    gpu_utilization: float = 0.0
    gpu_memory_used: int = 0
    # Business-specific metrics
    active_fingerprint_jobs: int = 0
    revenue_calculation_queue: int = 0
    content_protection_alerts: int = 0
    # Performance scores
    overall_health_score: float = 1.0
    bottleneck_probability: float = 0.0


@dataclass
class PerformanceAlert:
    """
Enhanced performance alert with intelligent thresholds"""
    name: str
    metric: str
    threshold: float
    comparison: str  # "greater_than", "less_than", "anomaly"
    duration: int  # seconds
    enabled: bool = True
    category: PerformanceCategory = PerformanceCategory.API_ENDPOINT
    business_impact: PerformanceImpact = PerformanceImpact.MEDIUM
    auto_scaling_trigger: bool = False
    notification_channels: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)


@dataclass
class BottleneckAnalysis:
    """Bottleneck detection and analysis results"""
    operation: str
    bottleneck_type: str  # "cpu", "memory", "io", "network", "database", "ai_processing"
    severity: PerformanceImpact
    confidence_score: float  # 0.0 to 1.0
    root_cause: str
    affected_operations: List[str]
    recommended_actions: List[str]
    estimated_improvement: float  # Expected performance improvement percentage
    business_impact_description: str


@dataclass
class PerformanceInsight:
    """AI-generated performance insights and recommendations"""
    insight_type: str  # "optimization", "scaling", "bottleneck", "trend"
    description: str
    confidence: float
    impact_score: float
    implementation_effort: str  # "low", "medium", "high"
    expected_benefit: str
    recommended_actions: List[str]
    metrics_supporting: List[str]


class AIPerformanceAnalyzer:
    """AI-powered performance analysis and optimization"""
    
    def __init__(self) -> None:
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_performance: Dict[str, float] = {}
        self.anomaly_thresholds: Dict[str, Tuple[float, float]] = {}
        
    def analyze_bottlenecks(self, profiles: Dict[str, PerformanceProfile]) -> List[BottleneckAnalysis]:
        """
Analyze performance profiles to identify bottlenecks"""
        bottlenecks = []
        
        for operation, profile in profiles.items():
            if len(profile.samples) < 10:
                continue
                
            # Calculate bottleneck probability
            avg_time = profile.avg_time
            p95_time = profile.p95_time
            variance = profile.std_deviation
            
            # Bottleneck indicators
            high_variance = variance > (avg_time * 0.5)
            high_p95_ratio = p95_time > (avg_time * 2.0)
            high_absolute_time = avg_time > self._get_time_threshold(profile.category)
            
            if high_variance or high_p95_ratio or high_absolute_time:
                bottleneck_type = self._identify_bottleneck_type(profile)
                severity = self._calculate_severity(profile)
                confidence = self._calculate_confidence(profile, high_variance, high_p95_ratio, high_absolute_time)
                
                bottleneck = BottleneckAnalysis(
                    operation=operation,
                    bottleneck_type=bottleneck_type,
                    severity=severity,
                    confidence_score=confidence,
                    root_cause=self._determine_root_cause(profile, bottleneck_type),
                    affected_operations=self._find_affected_operations(operation, profiles),
                    recommended_actions=self._generate_recommendations(profile, bottleneck_type),
                    estimated_improvement=self._estimate_improvement(profile),
                    business_impact_description=self._describe_business_impact(profile)
                )
                
                bottlenecks.append(bottleneck)
                
        return sorted(bottlenecks, key=lambda x: x.confidence_score, reverse=True)
    
    def _get_time_threshold(self, category: PerformanceCategory) -> float:
        """
Get acceptable time thresholds by category"""
        thresholds = {
            PerformanceCategory.API_ENDPOINT: 500.0,  # 500ms
            PerformanceCategory.DATABASE_QUERY: 100.0,  # 100ms
            PerformanceCategory.AI_PROCESSING: 5000.0,  # 5s
            PerformanceCategory.FINGERPRINT_GENERATION: 3000.0,  # 3s
            PerformanceCategory.CONTENT_PROTECTION: 1000.0,  # 1s
            PerformanceCategory.REVENUE_CALCULATION: 2000.0,  # 2s
            PerformanceCategory.USER_AUTHENTICATION: 200.0,  # 200ms
            PerformanceCategory.FILE_PROCESSING: 10000.0,  # 10s
            PerformanceCategory.EXTERNAL_API_CALL: 3000.0,  # 3s
            PerformanceCategory.CACHE_OPERATION: 10.0  # 10ms
        }
        return thresholds.get(category, 1000.0)
    
    def _identify_bottleneck_type(self, profile: PerformanceProfile) -> str:
        """
Identify the type of bottleneck based on performance patterns"""
        if profile.category == PerformanceCategory.DATABASE_QUERY:
            return "database"
        elif profile.category in [PerformanceCategory.AI_PROCESSING, PerformanceCategory.FINGERPRINT_GENERATION]:
            return "ai_processing"
        elif profile.category == PerformanceCategory.FILE_PROCESSING:
            return "io"
        elif profile.category == PerformanceCategory.EXTERNAL_API_CALL:
            return "network"
        else:
            # Analyze based on system metrics correlation
            if profile.avg_time > 2000:
                return "cpu"
            elif profile.std_deviation > profile.avg_time:
                return "memory"
            else:
                return "general"
    
    def _calculate_severity(self, profile: PerformanceProfile) -> PerformanceImpact:
        """Calculate the severity of the performance issue"""
        threshold = self._get_time_threshold(profile.category)
        ratio = profile.avg_time / threshold
        
        if ratio > 5.0:
            return PerformanceImpact.CRITICAL
        elif ratio > 3.0:
            return PerformanceImpact.HIGH
        elif ratio > 2.0:
            return PerformanceImpact.MEDIUM
        else:
            return PerformanceImpact.LOW
    
    def _calculate_confidence(self, profile: PerformanceProfile, *indicators: bool) -> float:
        """
Calculate confidence score for bottleneck detection"""
        base_confidence = 0.5
        
        # Sample size factor
        sample_factor = min(len(profile.samples) / 100.0, 1.0) * 0.2
        
        # Indicator factor
        indicator_factor = sum(indicators) / len(indicators) * 0.3
        
        return min(base_confidence + sample_factor + indicator_factor, 1.0)
    
    def _determine_root_cause(self, profile: PerformanceProfile, bottleneck_type: str) -> str:
        """
Determine the root cause of the performance issue"""
        causes = {
            "database": "Slow database queries or connection pool exhaustion",
            "ai_processing": "AI model processing overhead or insufficient GPU resources",
            "io": "Disk I/O bottleneck or large file processing",
            "network": "Network latency or external API rate limiting",
            "cpu": "High CPU utilization or inefficient algorithms",
            "memory": "Memory allocation patterns or garbage collection",
            "general": "General system resource contention"
        }
        return causes.get(bottleneck_type, "Unknown performance bottleneck")
    
    def _find_affected_operations(self, operation: str, profiles: Dict[str, PerformanceProfile]) -> List[str]:
        """Find operations that might be affected by this bottleneck"""
        affected = []
        current_category = profiles[operation].category
        
        for other_op, other_profile in profiles.items():
            if other_op != operation and other_profile.category == current_category:
                if other_profile.avg_time > self._get_time_threshold(current_category):
                    affected.append(other_op)
                    
        return affected
    
    def _generate_recommendations(self, profile: PerformanceProfile, bottleneck_type: str) -> List[str]:
        """
Generate optimization recommendations"""
        recommendations = {
            "database": [
                "Add database indexes for frequently queried columns",
                "Implement query result caching",
                "Consider database connection pooling optimization",
                "Review and optimize slow queries"
            ],
            "ai_processing": [
                "Implement model result caching",
                "Consider model quantization for faster inference",
                "Scale GPU resources or use model parallelization",
                "Optimize batch processing for AI operations"
            ],
            "io": [
                "Implement asynchronous file processing",
                "Add file compression to reduce I/O overhead",
                "Consider using faster storage (SSD)",
                "Implement file processing queues"
            ],
            "network": [
                "Implement request caching and retry logic",
                "Consider using CDN for static content",
                "Optimize API payload sizes",
                "Implement connection pooling for external APIs"
            ],
            "cpu": [
                "Optimize algorithms and data structures",
                "Implement horizontal scaling",
                "Consider async processing for CPU-intensive tasks",
                "Profile and optimize hot code paths"
            ],
            "memory": [
                "Implement object pooling",
                "Optimize memory allocation patterns",
                "Consider garbage collection tuning",
                "Review memory-intensive operations"
            ]
        }
        return recommendations.get(bottleneck_type, ["General performance optimization needed"])
    
    def _estimate_improvement(self, profile: PerformanceProfile) -> float:
        """Estimate potential performance improvement percentage"""
        threshold = self._get_time_threshold(profile.category)
        current_time = profile.avg_time
        
        if current_time <= threshold:
            return 10.0  # Minor improvement possible
        
        # Calculate potential improvement based on how far we are from threshold
        ratio = current_time / threshold
        if ratio > 5.0:
            return 70.0  # High improvement potential
        elif ratio > 3.0:
            return 50.0
        elif ratio > 2.0:
            return 30.0
        else:
            return 15.0
    
    def _describe_business_impact(self, profile: PerformanceProfile) -> str:
        """
Describe the business impact of the performance issue"""
        impacts = {
            PerformanceCategory.API_ENDPOINT: "Affects user experience and platform responsiveness",
            PerformanceCategory.DATABASE_QUERY: "Impacts data access speed and system scalability",
            PerformanceCategory.AI_PROCESSING: "Affects content analysis speed and accuracy",
            PerformanceCategory.FINGERPRINT_GENERATION: "Delays content protection and violation detection",
            PerformanceCategory.CONTENT_PROTECTION: "Impacts intellectual property protection effectiveness",
            PerformanceCategory.REVENUE_CALCULATION: "Affects monetization accuracy and creator payouts",
            PerformanceCategory.USER_AUTHENTICATION: "Impacts user login experience and security",
            PerformanceCategory.FILE_PROCESSING: "Affects content upload and processing speed",
            PerformanceCategory.EXTERNAL_API_CALL: "Impacts third-party integrations and data synchronization",
            PerformanceCategory.CACHE_OPERATION: "Affects system performance and response times"
        }
        return impacts.get(profile.category, "General system performance impact")


class PerformanceTracker:
    """
    Industrial-grade performance tracking system with AI-powered analytics,
    specialized for content protection, fingerprinting, and revenue optimization.
    """
    
    def __init__(
        self,
        redis_client -> None: Optional[aioredis.Redis] = None,
        collection_interval -> None: int = 10,
        retention_hours -> None: int = 24,
        sample_rate -> None: float = 1.0,
        enable_ai_analysis -> None: bool = True
    ) -> None:
        self.redis_client = redis_client
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.sample_rate = sample_rate
        self.enable_ai_analysis = enable_ai_analysis
        
        # Performance profiles
        self._profiles: Dict[str, PerformanceProfile] = {}
        self._profiles_lock = threading.Lock()
        
        # Resource tracking
        self._resource_history: deque = deque(maxlen=1000)
        self._baseline_resources: Optional[ResourceUsage] = None
        
        # Active tracking
        self._active_operations: Dict[str, Dict[str, Any]] = {}
        self._operation_counter = 0
        
        # Monitoring state
        self._tracking = False
        self._tracker_task: Optional[asyncio.Task] = None
        
        # Performance alerts
        self._performance_alerts: Dict[str, PerformanceAlert] = {}
        self._alert_states: Dict[str, Dict[str, Any]] = {}
        
        # Bottleneck detection
        self._bottleneck_detector = BottleneckDetector()
        
        # Optimization recommendations
        self._optimizer = PerformanceOptimizer()
        
    async def start_tracking(self) -> None:
        """
Start performance tracking"""
        if self._tracking:
            logger.warning("Performance tracking already running")
            return
            
        self._tracking = True
        self._tracker_task = asyncio.create_task(self._tracking_loop())
        
        # Set baseline
        await self._set_baseline()
        
        logger.info("Performance tracking started")
        
    async def stop_tracking(self) -> None:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "stop_tracking",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric stop_tracking collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection stop_tracking failed: {e}")
                    return None
    async def _tracking_loop(self) -> None:
        """Main tracking loop"""
        while self._tracking:
            try:
                await self._collect_resource_metrics()
                await self._update_profiles()
                await self._check_performance_alerts()
                await self._detect_bottlenecks()
                await self._save_metrics()
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance tracking loop: {e}")
                await asyncio.sleep(5)
                
    async def _collect_resource_metrics(self) -> None:
        """Collect system resource metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes if disk_io else 0
            disk_write = disk_io.write_bytes if disk_io else 0
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_sent = network_io.bytes_sent if network_io else 0
            network_recv = network_io.bytes_recv if network_io else 0
            
            # Process info
            process = psutil.Process()
            active_threads = process.num_threads()
            open_files = len(process.open_files())
            
            resource_usage = ResourceUsage(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_available=memory.available,
                disk_io_read=disk_read,
                disk_io_write=disk_write,
                network_io_sent=network_sent,
                network_io_recv=network_recv,
                active_threads=active_threads,
                open_files=open_files
            )
            
            self._resource_history.append(resource_usage)
            
        except Exception as e:
            logger.error(f"Error collecting resource metrics: {e}")
            
    async def _set_baseline(self) -> None:
        """Set performance baseline"""
        await self._collect_resource_metrics()
        if self._resource_history:
            self._baseline_resources = self._resource_history[-1]
            logger.info("Performance baseline set")
            
    @asynccontextmanager
    async def track_operation(self, operation -> None: str, **labels) -> None:
        """Async context manager for tracking operation performance"""
        start_time = time.time()
        operation_id = f"{operation}_{self._operation_counter}"
        self._operation_counter += 1
        
        # Record start
        self._active_operations[operation_id] = {
            "operation": operation,
            "start_time": start_time,
            "labels": labels
        }
        
        try:
            yield operation_id
        except Exception as e:
            # Record error
            if operation in self._profiles:
                self._profiles[operation].error_count += 1
            raise
        finally:
            # Record completion
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            await self._record_performance(operation, duration, labels)
            
            if operation_id in self._active_operations:
                del self._active_operations[operation_id]
                
    @contextmanager
    def track_sync_operation(self, operation -> None: str, **labels) -> None:
        """Synchronous context manager for tracking operation performance"""
        start_time = time.time()
        
        try:
            yield
        except Exception as e:
            # Record error
            with self._profiles_lock:
                if operation in self._profiles:
                    self._profiles[operation].error_count += 1
            raise
        finally:
            # Record completion
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self._record_performance_sync(operation, duration, labels)
            
    def track_function(self, operation -> None: Optional[str] = None, **labels) -> None:
        try:
            logger.info(f"Executing async_wrapper")
            
            # Implementation for async_wrapper
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"async_wrapper completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing sync_wrapper")
            
            # Implementation for sync_wrapper
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"sync_wrapper completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"sync_wrapper failed: {e}")
            raise
            logger.info(f"async_wrapper completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"async_wrapper failed: {e}")
            raise
Decorator for tracking function performance"""
        def decorator(func) -> None:
            op_name = operation or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs) -> None:
                    async with self.track_operation(op_name, **labels):
                        return await func(*args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs) -> None:
                    with self.track_sync_operation(op_name, **labels):
                        return func(*args, **kwargs)
                return sync_wrapper
                
        return decorator
        
    async def _record_performance(self, operation -> None: str, duration -> None: float, labels -> None: Dict[str, str]) -> None:
        """Record performance metric asynchronously"""
        # Apply sampling
        if self.sample_rate < 1.0 and time.time() % 1 > self.sample_rate:
            return
            
        with self._profiles_lock:
            if operation not in self._profiles:
                self._profiles[operation] = PerformanceProfile(operation=operation)
                
            profile = self._profiles[operation]
            profile.total_calls += 1
            profile.total_time += duration
            profile.min_time = min(profile.min_time, duration)
            profile.max_time = max(profile.max_time, duration)
            profile.last_call = datetime.utcnow()
            profile.samples.append(duration)
            
            # Update percentiles
            if len(profile.samples) > 0:
                sorted_samples = sorted(profile.samples)
                profile.avg_time = profile.total_time / profile.total_calls
                profile.p50_time = statistics.median(sorted_samples)
                if len(sorted_samples) > 20:  # Need enough samples for percentiles
                    profile.p95_time = sorted_samples[int(len(sorted_samples) * 0.95)]
                    profile.p99_time = sorted_samples[int(len(sorted_samples) * 0.99)]
                    
        # Store metric
        metric = PerformanceMetric(
            name=f"operation.{operation}.duration",
            value=duration,
            timestamp=datetime.utcnow(),
            unit="ms",
            labels=labels
        )
        
        if self.redis_client:
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _update_profiles completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _update_profiles failed: {e}")
                    raise
            unit="ms",
            labels=labels
        )
        
        if self.redis_client:
            await self._store_metric(metric)
            
    def _record_performance_sync(self, operation -> None: str, duration -> None: float, labels -> None: Dict[str, str]) -> None:
        """Record performance metric synchronously"""
        # Apply sampling
        if self.sample_rate < 1.0 and time.time() % 1 > self.sample_rate:
            return
            
        with self._profiles_lock:
            if operation not in self._profiles:
                self._profiles[operation] = PerformanceProfile(operation=operation)
                
            profile = self._profiles[operation]
            profile.total_calls += 1
            profile.total_time += duration
            profile.min_time = min(profile.min_time, duration)
            profile.max_time = max(profile.max_time, duration)
            profile.last_call = datetime.utcnow()
            profile.samples.append(duration)
            
            # Update percentiles
            if len(profile.samples) > 0:
                sorted_samples = sorted(profile.samples)
                profile.avg_time = profile.total_time / profile.total_calls
                profile.p50_time = statistics.median(sorted_samples)
                if len(sorted_samples) > 20:
                    profile.p95_time = sorted_samples[int(len(sorted_samples) * 0.95)]
                    profile.p99_time = sorted_samples[int(len(sorted_samples) * 0.99)]
                    
    async def _update_profiles(self) -> None:
        """
Update performance profiles with calculated metrics"""
        # This method is called periodically to update derived metrics
        pass
        
    async def _check_performance_alerts(self) -> None:
        """
Check performance thresholds and trigger alerts"""
        for alert_name, alert in self._performance_alerts.items():
            if not alert.enabled:
                continue
                
            try:
                # Get current metric value
                current_value = await self._get_current_metric_value(alert.metric)
                if current_value is None:
                    continue
                    
                # Check threshold
                threshold_exceeded = False
                if alert.comparison == "greater_than" and current_value > alert.threshold:
                    threshold_exceeded = True
                elif alert.comparison == "less_than" and current_value < alert.threshold:
                    threshold_exceeded = True
                    
                # Track alert state
                if alert_name not in self._alert_states:
                    self._alert_states[alert_name] = {
                        "triggered": False,
                        "trigger_time": None,
                        "last_check": datetime.utcnow()
                    }
                    
                alert_state = self._alert_states[alert_name]
                
                if threshold_exceeded:
                    if not alert_state["triggered"]:
                        alert_state["triggered"] = True
                        alert_state["trigger_time"] = datetime.utcnow()
                    elif alert_state["trigger_time"]:
                        # Check if alert duration exceeded
                        duration = (datetime.utcnow() - alert_state["trigger_time"]).total_seconds()
                        if duration >= alert.duration:
                            await self._fire_performance_alert(alert, current_value)
                else:
                    # Reset alert state
                    alert_state["triggered"] = False
                    alert_state["trigger_time"] = None
                    
                alert_state["last_check"] = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error checking performance alert {alert_name}: {e}")
                
    async def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric"""
        if metric_name.startswith("operation."):
            # Extract operation name from metric
            parts = metric_name.split(".")
            if len(parts) >= 3:
                operation = parts[1]
                metric_type = parts[2]  # duration, calls, errors
                
                with self._profiles_lock:
                    if operation in self._profiles:
                        profile = self._profiles[operation]
                        if metric_type == "duration":
                            return profile.avg_time
                        elif metric_type == "calls":
                            return float(profile.total_calls)
                        elif metric_type == "errors":
                            return float(profile.error_count)
                            
        elif metric_name.startswith("resource."):
            # Resource metrics
            if not self._resource_history:
                return None
                
            latest = self._resource_history[-1]
            if metric_name == "resource.cpu_percent":
                return latest.cpu_percent
            elif metric_name == "resource.memory_percent":
                return latest.memory_percent
            elif metric_name == "resource.active_threads":
                return float(latest.active_threads)
            elif metric_name == "resource.open_files":
                return float(latest.open_files)
                
        return None
        
    async def _fire_performance_alert(self, alert -> None: PerformanceAlert, current_value -> None: float) -> None:
        """Fire a performance alert"""
        logger.warning(f"Performance alert triggered: {alert.name} - {alert.metric} = {current_value}")
        
        # Here you would integrate with the AlertManager to send notifications
        # For now, just log the alert
        
    async def _detect_bottlenecks(self) -> None:
        """Detect performance bottlenecks"""
        bottlenecks = self._bottleneck_detector.analyze(
            self._profiles,
            self._resource_history
        )
        
        if bottlenecks:
            logger.info(f"Detected {len(bottlenecks)} performance bottlenecks")
            # Store bottleneck information
            if self.redis_client:
                await self.redis_client.set(
                    "performance:bottlenecks",
                    json.dumps([b.__dict__ for b in bottlenecks]),
                    ex=3600  # 1 hour TTL
                )
                
    async def _store_metric(self, metric -> None: PerformanceMetric) -> None:
        """Store metric in Redis"""
        if not self.redis_client:
            return
            
        try:
            # Store in time series
            key = f"performance:metrics:{metric.name}"
            value = {
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat(),
                "unit": metric.unit,
                "labels": metric.labels,
                "metadata": metric.metadata
            }
            
            await self.redis_client.zadd(
                key,
                {json.dumps(value): metric.timestamp.timestamp()}
            )
            
            # Cleanup old metrics
            cutoff = time.time() - (self.retention_hours * 3600)
            await self.redis_client.zremrangebyscore(key, 0, cutoff)
            
        except Exception as e:
            logger.error(f"Error storing performance metric: {e}")
            
    async def _save_metrics(self) -> None:
        """Save current metrics to Redis"""
        if not self.redis_client:
            return
            
        try:
            # Save profiles summary
            profiles_summary = {}
            with self._profiles_lock:
                for operation, profile in self._profiles.items():
                    profiles_summary[operation] = {
                        "total_calls": profile.total_calls,
                        "avg_time": profile.avg_time,
                        "p95_time": profile.p95_time,
                        "error_count": profile.error_count,
                        "last_call": profile.last_call.isoformat() if profile.last_call else None
                    }
                    
            await self.redis_client.set(
                "performance:profiles",
                json.dumps(profiles_summary),
                ex=300  # 5 minutes TTL
            )
            
            # Save resource summary
            if self._resource_history:
                latest_resource = self._resource_history[-1]
                resource_summary = {
                    "timestamp": latest_resource.timestamp.isoformat(),
                    "cpu_percent": latest_resource.cpu_percent,
                    "memory_percent": latest_resource.memory_percent,
                    "active_threads": latest_resource.active_threads,
                    "open_files": latest_resource.open_files
                }
                
                await self.redis_client.set(
                    "performance:resources",
                    json.dumps(resource_summary),
                    ex=300  # 5 minutes TTL
                )
                
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
            
    async def _save_state(self) -> None:
        """Save tracker state"""
        # Save final performance summary
        await self._save_metrics()
        
    # Public interface methods
    def add_performance_alert(self, alert -> None: PerformanceAlert) -> None:
        """
Add a performance alert"""
        self._performance_alerts[alert.name] = alert
        logger.info(f"Added performance alert: {alert.name}")
        
    def remove_performance_alert(self, alert_name -> None: str) -> None:
        """Remove a performance alert"""
        if alert_name in self._performance_alerts:
            del self._performance_alerts[alert_name]
            if alert_name in self._alert_states:
                del self._alert_states[alert_name]
            logger.info(f"Removed performance alert: {alert_name}")
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        with self._profiles_lock:
            profiles_summary = {
                operation: {
                    "total_calls": profile.total_calls,
                    "avg_time": profile.avg_time,
                    "p95_time": profile.p95_time,
                    "p99_time": profile.p99_time,
                    "error_rate": profile.error_count / max(profile.total_calls, 1),
                    "last_call": profile.last_call.isoformat() if profile.last_call else None
                }
                for operation, profile in self._profiles.items()
            }
            
        resource_summary = {}
        if self._resource_history:
            latest = self._resource_history[-1]
            resource_summary = {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "active_threads": latest.active_threads,
                "open_files": latest.open_files,
                "timestamp": latest.timestamp.isoformat()
            }
            
        return {
            "operations": profiles_summary,
            "resources": resource_summary,
            "tracking_active": self._tracking,
            "total_operations": len(self._profiles),
            "active_operations": len(self._active_operations)
        }
        
    def get_operation_profile(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile for a specific operation"""
        with self._profiles_lock:
            if operation not in self._profiles:
                return None
                
            profile = self._profiles[operation]
            return {
                "operation": profile.operation,
                "total_calls": profile.total_calls,
                "total_time": profile.total_time,
                "min_time": profile.min_time,
                "max_time": profile.max_time,
                "avg_time": profile.avg_time,
                "p50_time": profile.p50_time,
                "p95_time": profile.p95_time,
                "p99_time": profile.p99_time,
                "error_count": profile.error_count,
                "error_rate": profile.error_count / max(profile.total_calls, 1),
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
                "sample_count": len(profile.samples)
            }
            
    def get_resource_trends(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get resource usage trends"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        trends = {
            "cpu": [],
            "memory": [],
            "threads": [],
            "files": []
        }
        
        for resource in self._resource_history:
            if resource.timestamp > cutoff:
                timestamp = resource.timestamp.isoformat()
                trends["cpu"].append({
                    "timestamp": timestamp,
                    "value": resource.cpu_percent
                })
                trends["memory"].append({
                    "timestamp": timestamp,
                    "value": resource.memory_percent
                })
                trends["threads"].append({
                    "timestamp": timestamp,
                    "value": resource.active_threads
                })
                trends["files"].append({
                    "timestamp": timestamp,
                    "value": resource.open_files
                })
                
        return trends
        
    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """Get current performance bottlenecks"""
        return self._bottleneck_detector.get_current_bottlenecks()
        
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
Get performance optimization recommendations"""
        return self._optimizer.generate_recommendations(
            self._profiles,
            self._resource_history
        )


class BottleneckDetector:
    """
Detect performance bottlenecks"""
    
    def __init__(self) -> None:
        self._current_bottlenecks = []
        
    def analyze(self, profiles: Dict[str, PerformanceProfile], resource_history: deque) -> List[Dict[str, Any]]:
        """
Analyze for bottlenecks"""
        bottlenecks = []
        
        # Analyze operation performance
        for operation, profile in profiles.items():
            if profile.total_calls > 10:  # Need sufficient data
                # Check for slow operations
                if profile.p95_time > 5000:  # > 5 seconds
                    bottlenecks.append({
                        "type": "slow_operation",
                        "operation": operation,
                        "p95_time": profile.p95_time,
                        "severity": "high" if profile.p95_time > 10000 else "medium"
                    })
                    
                # Check for high error rates
                error_rate = profile.error_count / profile.total_calls
                if error_rate > 0.05:  # > 5% error rate
                    bottlenecks.append({
                        "type": "high_error_rate",
                        "operation": operation,
                        "error_rate": error_rate,
                        "severity": "high" if error_rate > 0.1 else "medium"
                    })
                    
        # Analyze resource usage
        if resource_history:
            recent_resources = list(resource_history)[-10:]  # Last 10 samples
            
            avg_cpu = sum(r.cpu_percent for r in recent_resources) / len(recent_resources)
            avg_memory = sum(r.memory_percent for r in recent_resources) / len(recent_resources)
            
            if avg_cpu > 80:
                bottlenecks.append({
                    "type": "high_cpu_usage",
                    "value": avg_cpu,
                    "severity": "high" if avg_cpu > 95 else "medium"
                })
                
            if avg_memory > 85:
                bottlenecks.append({
                    "type": "high_memory_usage",
                    "value": avg_memory,
                    "severity": "high" if avg_memory > 95 else "medium"
                })
                
        self._current_bottlenecks = bottlenecks
        return bottlenecks
        
    def get_current_bottlenecks(self) -> List[Dict[str, Any]]:
        """Get current bottlenecks"""
        return self._current_bottlenecks


class PerformanceOptimizer:
    """
Generate performance optimization recommendations"""
    
    def generate_recommendations(
        self,
        profiles: Dict[str, PerformanceProfile],
        resource_history: deque
    ) -> List[Dict[str, Any]]:
        """
Generate optimization recommendations"""
        recommendations = []
        
        # Analyze operation patterns
        for operation, profile in profiles.items():
            if profile.total_calls > 100:  # Need sufficient data
                
                # Recommend caching for frequently called slow operations
                if profile.avg_time > 1000 and profile.total_calls > 1000:
                    recommendations.append({
                        "type": "caching",
                        "operation": operation,
                        "reason": f"Frequently called operation with {profile.avg_time:.2f}ms average time",
                        "impact": "high",
                        "effort": "medium"
                    })
                    
                # Recommend async processing for slow operations
                if profile.p95_time > 10000:  # > 10 seconds
                    recommendations.append({
                        "type": "async_processing",
                        "operation": operation,
                        "reason": f"Very slow operation with {profile.p95_time:.2f}ms P95 time",
                        "impact": "high",
                        "effort": "high"
                    })
                    
                # Recommend connection pooling for database operations
                if "database" in operation.lower() and profile.avg_time > 500:
                    recommendations.append({
                        "type": "connection_pooling",
                        "operation": operation,
                        "reason": "Database operation could benefit from connection pooling",
                        "impact": "medium",
                        "effort": "low"
                    })
                    
        # Resource-based recommendations
        if resource_history:
            recent_resources = list(resource_history)[-50:]  # Last 50 samples
            
            avg_cpu = sum(r.cpu_percent for r in recent_resources) / len(recent_resources)
            avg_memory = sum(r.memory_percent for r in recent_resources) / len(recent_resources)
            
            if avg_cpu > 70:
                recommendations.append({
                    "type": "cpu_optimization",
                    "reason": f"High CPU usage: {avg_cpu:.1f}%",
                    "suggestions": [
                        "Consider CPU-intensive task optimization",
                        "Implement request rate limiting",
                        "Scale horizontally"
                    ],
                    "impact": "high",
                    "effort": "medium"
                })
                
            if avg_memory > 80:
                recommendations.append({
                    "type": "memory_optimization",
                    "reason": f"High memory usage: {avg_memory:.1f}%",
                    "suggestions": [
                        "Implement memory caching strategies",
                        "Review memory leaks",
                        "Optimize data structures"
                    ],
                    "impact": "high",
                    "effort": "medium"
                })
                
        return recommendations

# File has syntax issues - needs manual review