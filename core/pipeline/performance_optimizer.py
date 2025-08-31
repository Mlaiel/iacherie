"""Performance Optimizer

Ultra-advanced performance optimization system for pipeline executions
with AI-powered analysis, real-time adaptation, and intelligent tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Performance Profiling → Bottleneck Detection → Optimization Strategy → Implementation → Continuous Monitoring
"""
import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Performance metrics"""
    EXECUTION_TIME = "execution_time"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CONCURRENCY = "concurrency"
    ERROR_RATE = "error_rate"
    RESOURCE_EFFICIENCY = "resource_efficiency"


class OptimizationType(Enum):
    """Optimization types"""
    ALGORITHM = "algorithm"
    RESOURCE = "resource"
    CACHING = "caching"
    PARALLELIZATION = "parallelization"
    CONFIGURATION = "configuration"
    SCHEDULING = "scheduling"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"


class OptimizationPriority(Enum):
    """Optimization priorities"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class PerformanceStatus(Enum):
    """Performance status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceBenchmark:
    """Performance benchmark"""
    metric: PerformanceMetric = PerformanceMetric.EXECUTION_TIME
    baseline_value: float = 0.0
    target_value: float = 0.0
    threshold_warning: float = 0.0
    threshold_critical: float = 0.0
    unit: str = "seconds"
    weight: float = 1.0
    description: str = ""


@dataclass
class PerformanceMeasurement:
    """Performance measurement"""
    metric: PerformanceMetric = PerformanceMetric.EXECUTION_TIME
    value: float = 0.0
    unit: str = "seconds"
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceProfile:
    """Performance profile"""
    profile_id: str = ""
    component_name: str = ""
    measurements: List[PerformanceMeasurement] = field(default_factory=list)
    benchmarks: Dict[PerformanceMetric, PerformanceBenchmark] = field(default_factory=dict)
    
    # Statistical data
    statistics: Dict[str, Any] = field(default_factory=dict)
    trends: Dict[str, Any] = field(default_factory=dict)
    
    # Profiling period
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    
    # Analysis results
    bottlenecks: List[Dict[str, Any]] = field(default_factory=list)
    performance_status: PerformanceStatus = PerformanceStatus.AVERAGE
    overall_score: float = 0.0


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_id: str = ""
    optimization_type: OptimizationType = OptimizationType.ALGORITHM
    priority: OptimizationPriority = OptimizationPriority.MEDIUM
    title: str = ""
    description: str = ""
    impact_estimate: Dict[str, float] = field(default_factory=dict)
    implementation_effort: str = "medium"
    prerequisites: List[str] = field(default_factory=list)
    risk_level: str = "low"
    
    # Implementation details
    implementation_steps: List[str] = field(default_factory=list)
    configuration_changes: Dict[str, Any] = field(default_factory=dict)
    code_changes: List[str] = field(default_factory=list)
    
    # Validation
    success_criteria: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    estimated_completion_time: Optional[datetime] = None


@dataclass
class OptimizationResult:
    """Optimization implementation result"""
    recommendation_id: str = ""
    implementation_status: str = "pending"
    actual_impact: Dict[str, float] = field(default_factory=dict)
    implementation_time: float = 0.0
    success: bool = False
    
    # Before/after comparison
    before_metrics: Dict[str, float] = field(default_factory=dict)
    after_metrics: Dict[str, float] = field(default_factory=dict)
    improvement_percentage: Dict[str, float] = field(default_factory=dict)
    
    # Implementation details
    changes_applied: List[str] = field(default_factory=list)
    issues_encountered: List[str] = field(default_factory=list)
    
    # Validation results
    validation_passed: bool = False
    validation_details: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class PerformanceProfiler:
    """Advanced performance profiler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PerformanceProfiler")
        
        # Profiling state
        self.active_profiles: Dict[str, PerformanceProfile] = {}
        self.completed_profiles: Dict[str, PerformanceProfile] = {}
        
        # Measurement storage
        self.measurement_buffer: deque = deque(maxlen=10000)
        self.real_time_metrics: Dict[str, Any] = {}
        
        # Profiling tasks
        self.profiling_tasks: Dict[str, asyncio.Task] = {}
        
        # System monitoring
        self.system_monitor_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
        # Start system monitoring
        self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Start system-wide performance monitoring"""
        self.monitoring_active = True
        self.system_monitor_task = asyncio.create_task(self._monitor_system_performance())
    
    async def _monitor_system_performance(self):
        """Monitor system-wide performance"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Store real-time metrics
                self.real_time_metrics = {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "memory_available": memory.available / (1024**3),  # GB
                    "disk_usage": (disk.used / disk.total) * 100,
                    "disk_free": disk.free / (1024**3),  # GB
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to measurement buffer
                system_measurement = PerformanceMeasurement(
                    metric=PerformanceMetric.CPU_USAGE,
                    value=cpu_percent,
                    unit="percent",
                    context=self.real_time_metrics,
                    tags=["system", "realtime"]
                )
                self.measurement_buffer.append(system_measurement)
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def start_profiling(
        self,
        component_name: str,
        benchmarks: Optional[Dict[PerformanceMetric, PerformanceBenchmark]] = None
    ) -> str:
        """Start performance profiling for component"""
        profile_id = f"profile_{component_name}_{uuid.uuid4().hex[:8]}"
        
        profile = PerformanceProfile(
            profile_id=profile_id,
            component_name=component_name,
            benchmarks=benchmarks or self._get_default_benchmarks()
        )
        
        self.active_profiles[profile_id] = profile
        
        # Start profiling task
        profiling_task = asyncio.create_task(
            self._profile_component(profile_id)
        )
        self.profiling_tasks[profile_id] = profiling_task
        
        self.logger.info(f"Started profiling: {profile_id} for component {component_name}")
        return profile_id
    
    async def _profile_component(self, profile_id: str):
        """Profile component performance"""
        profile = self.active_profiles.get(profile_id)
        if not profile:
            return
        
        profiling_interval = self.config.get("profiling_interval", 2.0)
        
        while profile_id in self.active_profiles:
            try:
                # Collect component-specific measurements
                measurements = await self._collect_component_measurements(profile.component_name)
                
                # Add measurements to profile
                profile.measurements.extend(measurements)
                
                # Update statistics
                self._update_profile_statistics(profile)
                
                # Check for bottlenecks
                bottlenecks = await self._detect_bottlenecks(profile)
                if bottlenecks:
                    profile.bottlenecks.extend(bottlenecks)
                
                # Update performance status
                profile.performance_status = self._calculate_performance_status(profile)
                profile.overall_score = self._calculate_overall_score(profile)
                
                await asyncio.sleep(profiling_interval)
                
            except Exception as e:
                self.logger.error(f"Profiling error for {profile_id}: {e}")
                await asyncio.sleep(profiling_interval * 2)
    
    async def _collect_component_measurements(self, component_name: str) -> List[PerformanceMeasurement]:
        """Collect performance measurements for component"""
        measurements = []
        current_time = datetime.now()
        
        # Simulate component-specific measurements
        # In real implementation, this would collect actual metrics
        
        # Execution time measurement
        exec_time = self._simulate_execution_time_measurement(component_name)
        measurements.append(PerformanceMeasurement(
            metric=PerformanceMetric.EXECUTION_TIME,
            value=exec_time,
            unit="seconds",
            timestamp=current_time,
            context={"component": component_name},
            tags=[component_name, "execution"]
        ))
        
        # Throughput measurement
        throughput = self._simulate_throughput_measurement(component_name)
        measurements.append(PerformanceMeasurement(
            metric=PerformanceMetric.THROUGHPUT,
            value=throughput,
            unit="operations/second",
            timestamp=current_time,
            context={"component": component_name},
            tags=[component_name, "throughput"]
        ))
        
        # Memory usage measurement
        memory_usage = self._simulate_memory_measurement(component_name)
        measurements.append(PerformanceMeasurement(
            metric=PerformanceMetric.MEMORY_USAGE,
            value=memory_usage,
            unit="MB",
            timestamp=current_time,
            context={"component": component_name},
            tags=[component_name, "memory"]
        ))
        
        return measurements
    
    def _simulate_execution_time_measurement(self, component_name: str) -> float:
        """Simulate execution time measurement"""
        # Base execution time with some variation
        base_times = {
            "content_processing": 2.5,
            "ai_analysis": 3.2,
            "protection": 1.8,
            "optimization": 2.1,
            "distribution": 4.5
        }
        
        base_time = base_times.get(component_name, 2.0)
        # Add random variation ±20%
        import random
        variation = random.uniform(-0.2, 0.2)
        return base_time * (1 + variation)
    
    def _simulate_throughput_measurement(self, component_name: str) -> float:
        """Simulate throughput measurement"""
        base_throughput = {
            "content_processing": 50.0,
            "ai_analysis": 30.0,
            "protection": 75.0,
            "optimization": 45.0,
            "distribution": 25.0
        }
        
        base = base_throughput.get(component_name, 40.0)
        import random
        variation = random.uniform(-0.15, 0.15)
        return base * (1 + variation)
    
    def _simulate_memory_measurement(self, component_name: str) -> float:
        """Simulate memory usage measurement"""
        base_memory = {
            "content_processing": 512.0,
            "ai_analysis": 1024.0,
            "protection": 256.0,
            "optimization": 768.0,
            "distribution": 384.0
        }
        
        base = base_memory.get(component_name, 512.0)
        import random
        variation = random.uniform(-0.1, 0.1)
        return base * (1 + variation)
    
    def _get_default_benchmarks(self) -> Dict[PerformanceMetric, PerformanceBenchmark]:
        """Get default performance benchmarks"""
        return {
            PerformanceMetric.EXECUTION_TIME: PerformanceBenchmark(
                metric=PerformanceMetric.EXECUTION_TIME,
                baseline_value=5.0,
                target_value=2.0,
                threshold_warning=8.0,
                threshold_critical=12.0,
                unit="seconds",
                weight=1.0,
                description="Component execution time"
            ),
            PerformanceMetric.THROUGHPUT: PerformanceBenchmark(
                metric=PerformanceMetric.THROUGHPUT,
                baseline_value=30.0,
                target_value=50.0,
                threshold_warning=20.0,
                threshold_critical=10.0,
                unit="operations/second",
                weight=0.8,
                description="Component throughput"
            ),
            PerformanceMetric.MEMORY_USAGE: PerformanceBenchmark(
                metric=PerformanceMetric.MEMORY_USAGE,
                baseline_value=1024.0,
                target_value=512.0,
                threshold_warning=2048.0,
                threshold_critical=4096.0,
                unit="MB",
                weight=0.6,
                description="Component memory usage"
            )
        }
    
    def _update_profile_statistics(self, profile: PerformanceProfile):
        """Update profile statistics"""
        if not profile.measurements:
            return
        
        # Group measurements by metric
        metric_groups = defaultdict(list)
        for measurement in profile.measurements:
            metric_groups[measurement.metric].append(measurement.value)
        
        # Calculate statistics for each metric
        for metric, values in metric_groups.items():
            if values:
                profile.statistics[metric.value] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1] if values else 0
                }
    
    async def _detect_bottlenecks(self, profile: PerformanceProfile) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        for metric, benchmark in profile.benchmarks.items():
            stats = profile.statistics.get(metric.value)
            if not stats:
                continue
            
            current_value = stats["latest"]
            
            # Check against thresholds
            if current_value >= benchmark.threshold_critical:
                bottlenecks.append({
                    "type": "critical",
                    "metric": metric.value,
                    "current_value": current_value,
                    "threshold": benchmark.threshold_critical,
                    "severity": "critical",
                    "description": f"{metric.value} is critically high: {current_value} >= {benchmark.threshold_critical}"
                })
            elif current_value >= benchmark.threshold_warning:
                bottlenecks.append({
                    "type": "warning",
                    "metric": metric.value,
                    "current_value": current_value,
                    "threshold": benchmark.threshold_warning,
                    "severity": "warning",
                    "description": f"{metric.value} is above warning threshold: {current_value} >= {benchmark.threshold_warning}"
                })
        
        return bottlenecks
    
    def _calculate_performance_status(self, profile: PerformanceProfile) -> PerformanceStatus:
        """Calculate overall performance status"""
        if not profile.statistics:
            return PerformanceStatus.AVERAGE
        
        critical_issues = sum(1 for b in profile.bottlenecks if b.get("severity") == "critical")
        warning_issues = sum(1 for b in profile.bottlenecks if b.get("severity") == "warning")
        
        if critical_issues > 0:
            return PerformanceStatus.CRITICAL
        elif warning_issues > 2:
            return PerformanceStatus.POOR
        elif warning_issues > 0:
            return PerformanceStatus.AVERAGE
        else:
            # Check if meeting targets
            targets_met = 0
            total_targets = 0
            
            for metric, benchmark in profile.benchmarks.items():
                stats = profile.statistics.get(metric.value)
                if stats:
                    total_targets += 1
                    current_value = stats["latest"]
                    
                    # For metrics where lower is better (execution_time, memory_usage)
                    if metric in [PerformanceMetric.EXECUTION_TIME, PerformanceMetric.MEMORY_USAGE]:
                        if current_value <= benchmark.target_value:
                            targets_met += 1
                    else:
                        # For metrics where higher is better (throughput)
                        if current_value >= benchmark.target_value:
                            targets_met += 1
            
            if total_targets > 0:
                target_ratio = targets_met / total_targets
                if target_ratio >= 0.9:
                    return PerformanceStatus.EXCELLENT
                elif target_ratio >= 0.7:
                    return PerformanceStatus.GOOD
                else:
                    return PerformanceStatus.AVERAGE
            
            return PerformanceStatus.AVERAGE
    
    def _calculate_overall_score(self, profile: PerformanceProfile) -> float:
        """Calculate overall performance score"""
        if not profile.statistics or not profile.benchmarks:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, benchmark in profile.benchmarks.items():
            stats = profile.statistics.get(metric.value)
            if not stats:
                continue
            
            current_value = stats["latest"]
            
            # Calculate normalized score (0-1)
            if metric in [PerformanceMetric.EXECUTION_TIME, PerformanceMetric.MEMORY_USAGE]:
                # For metrics where lower is better
                if current_value <= benchmark.target_value:
                    score = 1.0
                elif current_value >= benchmark.threshold_critical:
                    score = 0.0
                else:
                    # Linear interpolation between target and critical
                    score = 1.0 - ((current_value - benchmark.target_value) / 
                                 (benchmark.threshold_critical - benchmark.target_value))
            else:
                # For metrics where higher is better
                if current_value >= benchmark.target_value:
                    score = 1.0
                elif current_value <= benchmark.threshold_critical:
                    score = 0.0
                else:
                    # Linear interpolation between critical and target
                    score = (current_value - benchmark.threshold_critical) / \
                           (benchmark.target_value - benchmark.threshold_critical)
            
            # Apply weight
            total_score += score * benchmark.weight
            total_weight += benchmark.weight
        
        return total_score / max(total_weight, 1.0)
    
    async def stop_profiling(self, profile_id: str) -> PerformanceProfile:
        """Stop profiling and return final profile"""
        if profile_id not in self.active_profiles:
            raise ValueError(f"Profile {profile_id} not found")
        
        profile = self.active_profiles[profile_id]
        profile.end_time = datetime.now()
        profile.duration = (profile.end_time - profile.start_time).total_seconds()
        
        # Cancel profiling task
        if profile_id in self.profiling_tasks:
            self.profiling_tasks[profile_id].cancel()
            del self.profiling_tasks[profile_id]
        
        # Move to completed profiles
        self.completed_profiles[profile_id] = profile
        del self.active_profiles[profile_id]
        
        self.logger.info(f"Stopped profiling: {profile_id}")
        return profile
    
    def get_profile(self, profile_id: str) -> Optional[PerformanceProfile]:
        """Get profile by ID"""
        return (self.active_profiles.get(profile_id) or 
                self.completed_profiles.get(profile_id))
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        return self.real_time_metrics.copy()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.system_monitor_task:
            self.system_monitor_task.cancel()
        
        # Cancel all profiling tasks
        for task in self.profiling_tasks.values():
            task.cancel()
        self.profiling_tasks.clear()


class OptimizationEngine:
    """AI-powered optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.OptimizationEngine")
        
        # Optimization knowledge base
        self.optimization_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.implementation_history: List[OptimizationResult] = []
        
        # Initialize optimization patterns
        self._initialize_optimization_patterns()
    
    def _initialize_optimization_patterns(self):
        """Initialize optimization patterns"""
        self.optimization_patterns = {
            "high_execution_time": [
                {
                    "type": OptimizationType.ALGORITHM,
                    "title": "Algorithm Optimization",
                    "description": "Optimize core algorithms for better performance",
                    "impact": {"execution_time": -0.3, "cpu_usage": -0.2},
                    "effort": "high",
                    "risk": "medium"
                },
                {
                    "type": OptimizationType.PARALLELIZATION,
                    "title": "Parallel Processing",
                    "description": "Implement parallel processing for CPU-intensive tasks",
                    "impact": {"execution_time": -0.4, "throughput": 0.5},
                    "effort": "medium",
                    "risk": "low"
                },
                {
                    "type": OptimizationType.CACHING,
                    "title": "Intelligent Caching",
                    "description": "Implement result caching for repeated operations",
                    "impact": {"execution_time": -0.6, "cpu_usage": -0.3},
                    "effort": "low",
                    "risk": "low"
                }
            ],
            "high_memory_usage": [
                {
                    "type": OptimizationType.MEMORY,
                    "title": "Memory Pool Optimization",
                    "description": "Implement memory pooling and reuse strategies",
                    "impact": {"memory_usage": -0.4, "gc_time": -0.3},
                    "effort": "medium",
                    "risk": "low"
                },
                {
                    "type": OptimizationType.ALGORITHM,
                    "title": "Memory-Efficient Algorithms",
                    "description": "Replace memory-intensive algorithms with efficient alternatives",
                    "impact": {"memory_usage": -0.5, "execution_time": -0.1},
                    "effort": "high",
                    "risk": "medium"
                }
            ],
            "low_throughput": [
                {
                    "type": OptimizationType.PARALLELIZATION,
                    "title": "Concurrent Processing",
                    "description": "Increase concurrency for higher throughput",
                    "impact": {"throughput": 0.8, "resource_usage": 0.3},
                    "effort": "medium",
                    "risk": "low"
                },
                {
                    "type": OptimizationType.IO,
                    "title": "I/O Optimization",
                    "description": "Optimize I/O operations for better throughput",
                    "impact": {"throughput": 0.4, "latency": -0.2},
                    "effort": "low",
                    "risk": "low"
                }
            ]
        }
    
    async def analyze_performance_profile(self, profile: PerformanceProfile) -> List[OptimizationRecommendation]:
        """Analyze profile and generate optimization recommendations"""
        recommendations = []
        
        # Analyze bottlenecks
        for bottleneck in profile.bottlenecks:
            bottleneck_recommendations = await self._generate_bottleneck_recommendations(
                bottleneck, profile
            )
            recommendations.extend(bottleneck_recommendations)
        
        # Analyze overall performance patterns
        pattern_recommendations = await self._analyze_performance_patterns(profile)
        recommendations.extend(pattern_recommendations)
        
        # Prioritize recommendations
        recommendations = self._prioritize_recommendations(recommendations)
        
        # Add implementation details
        for recommendation in recommendations:
            await self._enhance_recommendation_details(recommendation, profile)
        
        return recommendations
    
    async def _generate_bottleneck_recommendations(
        self,
        bottleneck: Dict[str, Any],
        profile: PerformanceProfile
    ) -> List[OptimizationRecommendation]:
        """Generate recommendations for specific bottleneck"""
        recommendations = []
        metric = bottleneck["metric"]
        severity = bottleneck["severity"]
        
        # Map bottleneck to optimization patterns
        pattern_key = None
        if metric == "execution_time":
            pattern_key = "high_execution_time"
        elif metric == "memory_usage":
            pattern_key = "high_memory_usage"
        elif metric == "throughput":
            pattern_key = "low_throughput"
        
        if pattern_key and pattern_key in self.optimization_patterns:
            patterns = self.optimization_patterns[pattern_key]
            
            for pattern in patterns:
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=pattern["type"],
                    priority=OptimizationPriority.CRITICAL if severity == "critical" else OptimizationPriority.HIGH,
                    title=pattern["title"],
                    description=pattern["description"],
                    impact_estimate=pattern["impact"],
                    implementation_effort=pattern["effort"],
                    risk_level=pattern["risk"]
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _analyze_performance_patterns(self, profile: PerformanceProfile) -> List[OptimizationRecommendation]:
        """Analyze performance patterns for additional recommendations"""
        recommendations = []
        
        # Check for general performance improvement opportunities
        if profile.overall_score < 0.7:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                optimization_type=OptimizationType.CONFIGURATION,
                priority=OptimizationPriority.HIGH,
                title="Configuration Tuning",
                description="Optimize configuration parameters for better performance",
                impact_estimate={"overall_score": 0.2},
                implementation_effort="low",
                risk_level="low"
            ))
        
        # Check for resource efficiency
        cpu_stats = profile.statistics.get("cpu_usage")
        memory_stats = profile.statistics.get("memory_usage")
        
        if cpu_stats and memory_stats:
            if cpu_stats["mean"] > 80 and memory_stats["mean"] > 1024:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RESOURCE,
                    priority=OptimizationPriority.MEDIUM,
                    title="Resource Balancing",
                    description="Balance CPU and memory usage for optimal resource utilization",
                    impact_estimate={"resource_efficiency": 0.3},
                    implementation_effort="medium",
                    risk_level="low"
                ))
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Prioritize optimization recommendations"""
        def priority_score(rec):
            priority_weight = {
                OptimizationPriority.CRITICAL: 4,
                OptimizationPriority.HIGH: 3,
                OptimizationPriority.MEDIUM: 2,
                OptimizationPriority.LOW: 1
            }
            
            effort_weight = {"low": 3, "medium": 2, "high": 1}
            risk_weight = {"low": 3, "medium": 2, "high": 1}
            
            priority = priority_weight.get(rec.priority, 2)
            effort = effort_weight.get(rec.implementation_effort, 2)
            risk = risk_weight.get(rec.risk_level, 2)
            
            # Calculate expected impact
            impact_sum = sum(abs(v) for v in rec.impact_estimate.values())
            
            return priority * effort * risk * impact_sum
        
        return sorted(recommendations, key=priority_score, reverse=True)
    
    async def _enhance_recommendation_details(
        self,
        recommendation: OptimizationRecommendation,
        profile: PerformanceProfile
    ):
        """Enhance recommendation with implementation details"""
        # Add implementation steps based on optimization type
        if recommendation.optimization_type == OptimizationType.CACHING:
            recommendation.implementation_steps = [
                "Identify cacheable operations",
                "Implement cache layer with appropriate TTL",
                "Add cache invalidation logic",
                "Monitor cache hit rates",
                "Tune cache size and policies"
            ]
            
            recommendation.configuration_changes = {
                "cache_enabled": True,
                "cache_size": "1GB",
                "cache_ttl": 3600,
                "cache_policy": "LRU"
            }
        
        elif recommendation.optimization_type == OptimizationType.PARALLELIZATION:
            recommendation.implementation_steps = [
                "Identify parallelizable tasks",
                "Implement task partitioning",
                "Add thread/process pool management",
                "Implement result aggregation",
                "Monitor concurrency metrics"
            ]
            
            recommendation.configuration_changes = {
                "max_workers": 8,
                "parallel_execution": True,
                "task_batch_size": 100
            }
        
        elif recommendation.optimization_type == OptimizationType.MEMORY:
            recommendation.implementation_steps = [
                "Profile memory usage patterns",
                "Implement object pooling",
                "Add memory monitoring",
                "Optimize data structures",
                "Implement garbage collection tuning"
            ]
            
            recommendation.configuration_changes = {
                "memory_pool_enabled": True,
                "max_memory_usage": "2GB",
                "gc_threshold": 0.8
            }
        
        # Add success criteria
        recommendation.success_criteria = [
            f"Improve {list(recommendation.impact_estimate.keys())[0]} by target percentage",
            "No degradation in other metrics",
            "System stability maintained",
            "Performance tests pass"
        ]
        
        # Add rollback plan
        recommendation.rollback_plan = [
            "Revert configuration changes",
            "Restore previous implementation",
            "Validate system functionality",
            "Monitor for stability"
        ]
    
    async def implement_optimization(
        self,
        recommendation: OptimizationRecommendation,
        dry_run: bool = False
    ) -> OptimizationResult:
        """Implement optimization recommendation"""
        result = OptimizationResult(
            recommendation_id=recommendation.recommendation_id,
            implementation_status="started"
        )
        
        try:
            self.logger.info(f"Implementing optimization: {recommendation.title}")
            
            if not dry_run:
                # Collect before metrics
                result.before_metrics = await self._collect_current_metrics()
                
                # Apply optimization
                await self._apply_optimization(recommendation, result)
                
                # Collect after metrics
                await asyncio.sleep(5)  # Wait for metrics to stabilize
                result.after_metrics = await self._collect_current_metrics()
                
                # Calculate improvement
                result.improvement_percentage = self._calculate_improvement(
                    result.before_metrics, result.after_metrics
                )
                
                # Validate results
                result.validation_passed = await self._validate_optimization(
                    recommendation, result
                )
                
                result.success = result.validation_passed
                result.implementation_status = "completed" if result.success else "failed"
            else:
                # Dry run - simulate implementation
                result.success = True
                result.implementation_status = "dry_run_completed"
                result.actual_impact = recommendation.impact_estimate.copy()
            
            result.completed_at = datetime.now()
            result.implementation_time = (result.completed_at - result.started_at).total_seconds()
            
            # Store in history
            self.implementation_history.append(result)
            
            return result
            
        except Exception as e:
            result.success = False
            result.implementation_status = "failed"
            result.issues_encountered.append(str(e))
            result.completed_at = datetime.now()
            
            self.logger.error(f"Optimization implementation failed: {e}")
            return result
    
    async def _collect_current_metrics(self) -> Dict[str, float]:
        """Collect current performance metrics"""
        # Simulate metric collection
        await asyncio.sleep(0.1)
        
        return {
            "execution_time": 2.5,
            "throughput": 45.0,
            "memory_usage": 512.0,
            "cpu_usage": 65.0,
            "response_time": 1.2
        }
    
    async def _apply_optimization(
        self,
        recommendation: OptimizationRecommendation,
        result: OptimizationResult
    ):
        """Apply optimization changes"""
        # Simulate optimization implementation
        await asyncio.sleep(1.0)
        
        # Record applied changes
        result.changes_applied = [
            f"Applied {recommendation.optimization_type.value} optimization",
            f"Updated configuration: {recommendation.configuration_changes}",
            "Restarted affected components"
        ]
    
    def _calculate_improvement(
        self,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate improvement percentages"""
        improvements = {}
        
        for metric, after_value in after_metrics.items():
            if metric in before_metrics:
                before_value = before_metrics[metric]
                
                if before_value != 0:
                    # For metrics where lower is better (execution_time, memory_usage)
                    if metric in ["execution_time", "memory_usage", "response_time"]:
                        improvement = ((before_value - after_value) / before_value) * 100
                    else:
                        # For metrics where higher is better (throughput)
                        improvement = ((after_value - before_value) / before_value) * 100
                    
                    improvements[metric] = improvement
        
        return improvements
    
    async def _validate_optimization(
        self,
        recommendation: OptimizationRecommendation,
        result: OptimizationResult
    ) -> bool:
        """Validate optimization results"""
        # Check if success criteria are met
        validation_details = {}
        
        for criterion in recommendation.success_criteria:
            # Simplified validation logic
            if "improve" in criterion.lower():
                # Check if any metric improved
                has_improvement = any(
                    improvement > 0 for improvement in result.improvement_percentage.values()
                )
                validation_details[criterion] = has_improvement
            else:
                # Default to passed for other criteria
                validation_details[criterion] = True
        
        result.validation_details = validation_details
        
        # Overall validation passes if most criteria are met
        passed_criteria = sum(1 for passed in validation_details.values() if passed)
        total_criteria = len(validation_details)
        
        return passed_criteria >= (total_criteria * 0.8)  # 80% threshold
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get optimization implementation history"""
        return self.implementation_history.copy()


class PerformanceOptimizer:
    """
    Ultra-advanced performance optimization system for pipeline executions
    with AI-powered analysis, real-time adaptation, and intelligent tuning.
    
    Features:
    - Comprehensive performance profiling and monitoring
    - AI-powered bottleneck detection and analysis
    - Intelligent optimization recommendation engine
    - Automated optimization implementation
    - Real-time performance tracking and adaptation
    - Performance trend analysis and prediction
    - Resource utilization optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core components
        self.profiler = PerformanceProfiler(self.config.get("profiling", {}))
        self.optimization_engine = OptimizationEngine(self.config.get("optimization", {}))
        
        # Optimization state
        self.active_optimizations: Dict[str, OptimizationResult] = {}
        self.optimization_metrics: Dict[str, Any] = {}
        
        # Performance monitoring
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
        # Auto-optimization
        self.auto_optimization_enabled = self.config.get("auto_optimization", {}).get("enabled", False)
        self.auto_optimization_task: Optional[asyncio.Task] = None
        
        # Start monitoring if enabled
        if self.config.get("monitoring", {}).get("enabled", True):
            self._start_monitoring()
        
        self.logger.info("Performance Optimizer initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "profiling": {
                "profiling_interval": 2.0,
                "max_profiles": 100,
                "auto_profiling": True
            },
            "optimization": {
                "auto_implementation": False,
                "dry_run_first": True,
                "validation_required": True,
                "rollback_on_failure": True
            },
            "monitoring": {
                "enabled": True,
                "monitoring_interval": 30.0,
                "performance_alerts": True
            },
            "auto_optimization": {
                "enabled": False,
                "optimization_threshold": 0.7,
                "optimization_interval": 300.0,  # 5 minutes
                "max_optimizations_per_cycle": 3
            },
            "thresholds": {
                "execution_time_warning": 5.0,
                "execution_time_critical": 10.0,
                "memory_usage_warning": 1024.0,
                "memory_usage_critical": 2048.0,
                "throughput_warning": 30.0,
                "throughput_critical": 15.0
            }
        }
    
    def _start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        if self.auto_optimization_enabled:
            self.auto_optimization_task = asyncio.create_task(self._auto_optimization_loop())
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        monitoring_interval = self.config["monitoring"]["monitoring_interval"]
        
        while self.monitoring_active:
            try:
                await self._update_optimization_metrics()
                await self._check_performance_alerts()
                
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(monitoring_interval * 2)
    
    async def _auto_optimization_loop(self):
        """Auto-optimization loop"""
        optimization_interval = self.config["auto_optimization"]["optimization_interval"]
        
        while self.monitoring_active:
            try:
                await self._run_auto_optimization()
                await asyncio.sleep(optimization_interval)
                
            except Exception as e:
                self.logger.error(f"Auto-optimization error: {e}")
                await asyncio.sleep(optimization_interval * 2)
    
    async def _update_optimization_metrics(self):
        """Update optimization metrics"""
        # Get real-time metrics
        real_time_metrics = self.profiler.get_real_time_metrics()
        
        # Get optimization history
        optimization_history = self.optimization_engine.get_optimization_history()
        
        # Calculate optimization metrics
        self.optimization_metrics = {
            "real_time_metrics": real_time_metrics,
            "total_optimizations": len(optimization_history),
            "successful_optimizations": sum(1 for opt in optimization_history if opt.success),
            "active_profiles": len(self.profiler.active_profiles),
            "completed_profiles": len(self.profiler.completed_profiles),
            "active_optimizations": len(self.active_optimizations),
            "optimization_success_rate": (
                sum(1 for opt in optimization_history if opt.success) / 
                max(len(optimization_history), 1)
            ),
            "average_improvement": self._calculate_average_improvement(optimization_history),
            "updated_at": datetime.now().isoformat()
        }
    
    def _calculate_average_improvement(self, optimization_history: List[OptimizationResult]) -> Dict[str, float]:
        """Calculate average improvement from optimization history"""
        if not optimization_history:
            return {}
        
        improvements_by_metric = defaultdict(list)
        
        for opt in optimization_history:
            if opt.success and opt.improvement_percentage:
                for metric, improvement in opt.improvement_percentage.items():
                    improvements_by_metric[metric].append(improvement)
        
        return {
            metric: statistics.mean(improvements) 
            for metric, improvements in improvements_by_metric.items()
            if improvements
        }
    
    async def _check_performance_alerts(self):
        """Check for performance alerts"""
        real_time_metrics = self.profiler.get_real_time_metrics()
        thresholds = self.config["thresholds"]
        
        alerts = []
        
        # Check CPU usage
        cpu_usage = real_time_metrics.get("cpu_usage", 0)
        if cpu_usage > 90:
            alerts.append(f"High CPU usage: {cpu_usage}%")
        
        # Check memory usage
        memory_usage = real_time_metrics.get("memory_usage", 0)
        if memory_usage > 85:
            alerts.append(f"High memory usage: {memory_usage}%")
        
        # Check disk usage
        disk_usage = real_time_metrics.get("disk_usage", 0)
        if disk_usage > 90:
            alerts.append(f"High disk usage: {disk_usage}%")
        
        if alerts and self.config["monitoring"]["performance_alerts"]:
            for alert in alerts:
                self.logger.warning(f"Performance Alert: {alert}")
    
    async def _run_auto_optimization(self):
        """Run automatic optimization"""
        if not self.auto_optimization_enabled:
            return
        
        threshold = self.config["auto_optimization"]["optimization_threshold"]
        max_optimizations = self.config["auto_optimization"]["max_optimizations_per_cycle"]
        
        # Get active profiles with low performance scores
        candidates = []
        for profile in self.profiler.active_profiles.values():
            if profile.overall_score < threshold:
                candidates.append(profile)
        
        # Sort by performance score (lowest first)
        candidates.sort(key=lambda p: p.overall_score)
        
        # Apply optimizations to worst performing profiles
        optimizations_applied = 0
        
        for profile in candidates[:max_optimizations]:
            try:
                recommendations = await self.optimization_engine.analyze_performance_profile(profile)
                
                if recommendations:
                    # Apply the highest priority recommendation
                    recommendation = recommendations[0]
                    
                    if self.config["optimization"]["dry_run_first"]:
                        # Run dry run first
                        dry_result = await self.optimization_engine.implement_optimization(
                            recommendation, dry_run=True
                        )
                        
                        if dry_result.success:
                            # Apply actual optimization
                            result = await self.optimization_engine.implement_optimization(
                                recommendation, dry_run=False
                            )
                            
                            if result.success:
                                optimizations_applied += 1
                                self.logger.info(f"Auto-optimization applied: {recommendation.title}")
                    else:
                        # Apply optimization directly
                        result = await self.optimization_engine.implement_optimization(
                            recommendation, dry_run=False
                        )
                        
                        if result.success:
                            optimizations_applied += 1
                            self.logger.info(f"Auto-optimization applied: {recommendation.title}")
                
            except Exception as e:
                self.logger.error(f"Auto-optimization failed for profile {profile.profile_id}: {e}")
        
        if optimizations_applied > 0:
            self.logger.info(f"Applied {optimizations_applied} auto-optimizations")
    
    # Public API methods
    async def start_performance_profiling(
        self,
        component_name: str,
        benchmarks: Optional[Dict[PerformanceMetric, PerformanceBenchmark]] = None
    ) -> str:
        """Start performance profiling for component"""
        return await self.profiler.start_profiling(component_name, benchmarks)
    
    async def stop_performance_profiling(self, profile_id: str) -> PerformanceProfile:
        """Stop performance profiling"""
        return await self.profiler.stop_profiling(profile_id)
    
    async def analyze_performance(self, profile_id: str) -> List[OptimizationRecommendation]:
        """Analyze performance profile and get recommendations"""
        profile = self.profiler.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        return await self.optimization_engine.analyze_performance_profile(profile)
    
    async def optimize_performance(
        self,
        recommendations: List[OptimizationRecommendation],
        auto_apply: bool = False,
        dry_run: bool = False
    ) -> List[OptimizationResult]:
        """Optimize performance based on recommendations"""
        results = []
        
        for recommendation in recommendations:
            try:
                if auto_apply or dry_run:
                    result = await self.optimization_engine.implement_optimization(
                        recommendation, dry_run=dry_run
                    )
                    results.append(result)
                    
                    if not dry_run and result.success:
                        self.active_optimizations[result.recommendation_id] = result
                
            except Exception as e:
                self.logger.error(f"Failed to optimize {recommendation.title}: {e}")
        
        return results
    
    async def comprehensive_performance_analysis(
        self,
        component_name: str,
        duration: float = 60.0
    ) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        # Start profiling
        profile_id = await self.start_performance_profiling(component_name)
        
        # Wait for profiling duration
        await asyncio.sleep(duration)
        
        # Stop profiling
        profile = await self.stop_performance_profiling(profile_id)
        
        # Analyze performance
        recommendations = await self.analyze_performance(profile_id)
        
        # Run dry-run optimizations
        optimization_results = await self.optimize_performance(
            recommendations, auto_apply=False, dry_run=True
        )
        
        return {
            "profile": profile,
            "recommendations": recommendations,
            "optimization_preview": optimization_results,
            "analysis_summary": {
                "performance_status": profile.performance_status.value,
                "overall_score": profile.overall_score,
                "bottlenecks_found": len(profile.bottlenecks),
                "recommendations_count": len(recommendations),
                "potential_improvements": {
                    result.recommendation_id: result.actual_impact
                    for result in optimization_results
                    if result.success
                }
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.optimization_metrics.copy()
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        return self.profiler.get_real_time_metrics()
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get optimization history"""
        return self.optimization_engine.get_optimization_history()
    
    def enable_auto_optimization(self):
        """Enable automatic optimization"""
        self.auto_optimization_enabled = True
        if self.monitoring_active and not self.auto_optimization_task:
            self.auto_optimization_task = asyncio.create_task(self._auto_optimization_loop())
        self.logger.info("Auto-optimization enabled")
    
    def disable_auto_optimization(self):
        """Disable automatic optimization"""
        self.auto_optimization_enabled = False
        if self.auto_optimization_task:
            self.auto_optimization_task.cancel()
            self.auto_optimization_task = None
        self.logger.info("Auto-optimization disabled")
    
    async def shutdown(self):
        """Shutdown performance optimizer"""
        self.logger.info("Shutting down performance optimizer")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        if self.auto_optimization_task:
            self.auto_optimization_task.cancel()
        
        # Stop profiler
        self.profiler.stop_monitoring()
        
        self.logger.info("Performance optimizer shutdown complete")


class AdvancedPerformanceAnalyzer:
    """Advanced AI-powered performance analyzer with machine learning capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AdvancedPerformanceAnalyzer")
        
        # Machine learning models for prediction
        self.prediction_models: Dict[str, Any] = {}
        
        # Performance patterns database
        self.performance_patterns: Dict[str, List[Dict[str, Any]]] = {}
        
        # Historical performance data
        self.historical_data: deque = deque(maxlen=100000)
        
        # Real-time analytics
        self.real_time_analytics = {}
        
        # Initialize ML models
        self._initialize_ml_models()
        
    def _initialize_ml_models(self):
        """Initialize machine learning models for performance prediction"""
        try:
            import numpy as np
            
            # Simple linear regression for performance prediction
            self.prediction_models = {
                "execution_time_predictor": {
                    "type": "linear_regression",
                    "features": ["cpu_usage", "memory_usage", "disk_io", "network_io"],
                    "target": "execution_time",
                    "model": None,
                    "trained": False
                },
                "bottleneck_detector": {
                    "type": "anomaly_detection", 
                    "features": ["cpu_usage", "memory_usage", "throughput", "latency"],
                    "model": None,
                    "trained": False
                },
                "optimization_recommender": {
                    "type": "classification",
                    "features": ["performance_metrics", "resource_usage", "workload_type"],
                    "target": "optimization_strategy",
                    "model": None,
                    "trained": False
                }
            }
            
            self.logger.info("ML models initialized for performance analysis")
            
        except ImportError:
            self.logger.warning("ML dependencies not available, using rule-based analysis")
    
    def analyze_performance_trends(self, profile: PerformanceProfile) -> Dict[str, Any]:
        """Analyze performance trends using AI/ML"""
        analysis_results = {
            "trend_analysis": {},
            "anomaly_detection": {},
            "performance_prediction": {},
            "optimization_opportunities": [],
            "risk_assessment": {}
        }
        
        if not profile.measurements:
            return analysis_results
        
        try:
            # Extract time series data
            metrics_data = self._extract_metrics_timeseries(profile.measurements)
            
            # Trend analysis
            analysis_results["trend_analysis"] = self._analyze_trends(metrics_data)
            
            # Anomaly detection
            analysis_results["anomaly_detection"] = self._detect_anomalies(metrics_data)
            
            # Performance prediction
            analysis_results["performance_prediction"] = self._predict_performance(metrics_data)
            
            # Optimization opportunities
            analysis_results["optimization_opportunities"] = self._identify_optimization_opportunities(metrics_data)
            
            # Risk assessment
            analysis_results["risk_assessment"] = self._assess_performance_risks(metrics_data)
            
        except Exception as e:
            self.logger.error(f"Performance analysis error: {e}")
            
        return analysis_results
    
    def _extract_metrics_timeseries(self, measurements: List[PerformanceMeasurement]) -> Dict[str, List[float]]:
        """Extract time series data from measurements"""
        metrics_data = defaultdict(list)
        
        for measurement in measurements:
            metrics_data[measurement.metric.value].append(measurement.value)
            metrics_data["timestamp"].append(measurement.timestamp.timestamp())
        
        return dict(metrics_data)
    
    def _analyze_trends(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze performance trends"""
        trends = {}
        
        for metric, values in metrics_data.items():
            if metric == "timestamp" or len(values) < 2:
                continue
                
            try:
                # Calculate trend direction and strength
                x = list(range(len(values)))
                
                # Simple linear trend calculation
                if len(values) >= 3:
                    trend_slope = (values[-1] - values[0]) / len(values)
                    trend_direction = "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable"
                    
                    # Calculate trend strength (coefficient of determination)
                    mean_value = sum(values) / len(values)
                    ss_tot = sum((v - mean_value) ** 2 for v in values)
                    trend_strength = abs(trend_slope) / (mean_value + 1e-6)  # Avoid division by zero
                    
                    trends[metric] = {
                        "direction": trend_direction,
                        "slope": trend_slope,
                        "strength": min(trend_strength, 1.0),  # Cap at 1.0
                        "stability": self._calculate_stability(values),
                        "volatility": self._calculate_volatility(values)
                    }
                    
            except Exception as e:
                self.logger.warning(f"Trend analysis error for {metric}: {e}")
                
        return trends
    
    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate stability metric (inverse of coefficient of variation)"""
        if len(values) < 2:
            return 1.0
            
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return 1.0
            
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean_val  # Coefficient of variation
        
        return max(0.0, 1.0 - cv)  # Higher stability = lower CV
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility metric"""
        if len(values) < 2:
            return 0.0
            
        changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
        mean_change = sum(changes) / len(changes) if changes else 0.0
        mean_value = sum(values) / len(values)
        
        return mean_change / (mean_value + 1e-6)  # Normalized volatility
    
    def _detect_anomalies(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Detect performance anomalies"""
        anomalies = {
            "detected_anomalies": [],
            "anomaly_score": 0.0,
            "severity": "low"
        }
        
        for metric, values in metrics_data.items():
            if metric == "timestamp" or len(values) < 5:
                continue
                
            try:
                # Statistical anomaly detection using IQR method
                sorted_values = sorted(values)
                n = len(sorted_values)
                q1_idx = n // 4
                q3_idx = 3 * n // 4
                
                q1 = sorted_values[q1_idx]
                q3 = sorted_values[q3_idx]
                iqr = q3 - q1
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Find anomalies
                metric_anomalies = []
                for i, value in enumerate(values):
                    if value < lower_bound or value > upper_bound:
                        anomaly_score = abs(value - (q1 + q3) / 2) / (iqr + 1e-6)
                        metric_anomalies.append({
                            "index": i,
                            "value": value,
                            "expected_range": [lower_bound, upper_bound],
                            "anomaly_score": anomaly_score
                        })
                
                if metric_anomalies:
                    anomalies["detected_anomalies"].append({
                        "metric": metric,
                        "anomalies": metric_anomalies,
                        "anomaly_rate": len(metric_anomalies) / len(values)
                    })
                    
            except Exception as e:
                self.logger.warning(f"Anomaly detection error for {metric}: {e}")
        
        # Calculate overall anomaly score
        if anomalies["detected_anomalies"]:
            total_anomalies = sum(len(ma["anomalies"]) for ma in anomalies["detected_anomalies"])
            total_measurements = sum(len(values) for metric, values in metrics_data.items() if metric != "timestamp")
            anomalies["anomaly_score"] = total_anomalies / max(total_measurements, 1)
            
            # Determine severity
            if anomalies["anomaly_score"] > 0.2:
                anomalies["severity"] = "high"
            elif anomalies["anomaly_score"] > 0.1:
                anomalies["severity"] = "medium"
            else:
                anomalies["severity"] = "low"
        
        return anomalies
    
    def _predict_performance(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Predict future performance based on trends"""
        predictions = {
            "short_term": {},  # Next 5 measurements
            "medium_term": {},  # Next 20 measurements
            "confidence_level": 0.0,
            "prediction_accuracy": "unknown"
        }
        
        for metric, values in metrics_data.items():
            if metric == "timestamp" or len(values) < 3:
                continue
                
            try:
                # Simple linear extrapolation for prediction
                recent_values = values[-min(10, len(values)):]  # Use last 10 values
                
                if len(recent_values) >= 3:
                    # Calculate trend
                    x = list(range(len(recent_values)))
                    n = len(recent_values)
                    
                    # Linear regression coefficients
                    sum_x = sum(x)
                    sum_y = sum(recent_values)
                    sum_xy = sum(x[i] * recent_values[i] for i in range(n))
                    sum_x2 = sum(xi * xi for xi in x)
                    
                    # Calculate slope and intercept
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x + 1e-6)
                    intercept = (sum_y - slope * sum_x) / n
                    
                    # Make predictions
                    next_x = len(recent_values)
                    short_term_pred = slope * (next_x + 4) + intercept  # 5 steps ahead
                    medium_term_pred = slope * (next_x + 19) + intercept  # 20 steps ahead
                    
                    predictions["short_term"][metric] = max(0, short_term_pred)  # Ensure non-negative
                    predictions["medium_term"][metric] = max(0, medium_term_pred)
                    
            except Exception as e:
                self.logger.warning(f"Prediction error for {metric}: {e}")
        
        # Calculate confidence level based on trend stability
        if predictions["short_term"]:
            stability_scores = []
            for metric, values in metrics_data.items():
                if metric != "timestamp" and len(values) >= 3:
                    stability = self._calculate_stability(values[-10:])  # Recent stability
                    stability_scores.append(stability)
            
            predictions["confidence_level"] = sum(stability_scores) / len(stability_scores) if stability_scores else 0.0
        
        return predictions
    
    def _identify_optimization_opportunities(self, metrics_data: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities based on performance patterns"""
        opportunities = []
        
        try:
            # Analyze CPU usage patterns
            if "cpu_usage" in metrics_data and metrics_data["cpu_usage"]:
                cpu_values = metrics_data["cpu_usage"]
                avg_cpu = sum(cpu_values) / len(cpu_values)
                max_cpu = max(cpu_values)
                
                if avg_cpu > 80:
                    opportunities.append({
                        "type": "cpu_optimization",
                        "priority": "high",
                        "description": f"High average CPU usage ({avg_cpu:.1f}%). Consider CPU optimization strategies.",
                        "recommendations": [
                            "Implement parallel processing for CPU-intensive tasks",
                            "Optimize algorithms for better CPU efficiency",
                            "Consider load balancing across multiple cores"
                        ],
                        "expected_impact": "20-40% CPU usage reduction"
                    })
                elif max_cpu > 95:
                    opportunities.append({
                        "type": "cpu_spike_optimization",
                        "priority": "medium",
                        "description": f"CPU spikes detected (max: {max_cpu:.1f}%). Consider spike prevention.",
                        "recommendations": [
                            "Implement request throttling",
                            "Add CPU usage monitoring and alerts",
                            "Optimize resource-intensive operations"
                        ],
                        "expected_impact": "Reduced CPU spikes and better stability"
                    })
            
            # Analyze memory usage patterns
            if "memory_usage" in metrics_data and metrics_data["memory_usage"]:
                memory_values = metrics_data["memory_usage"]
                avg_memory = sum(memory_values) / len(memory_values)
                max_memory = max(memory_values)
                memory_trend = self._analyze_trends({"memory_usage": memory_values})
                
                if avg_memory > 85:
                    opportunities.append({
                        "type": "memory_optimization",
                        "priority": "high",
                        "description": f"High memory usage ({avg_memory:.1f}%). Memory optimization needed.",
                        "recommendations": [
                            "Implement memory pooling and reuse strategies",
                            "Optimize data structures for memory efficiency",
                            "Add memory leak detection and prevention"
                        ],
                        "expected_impact": "15-30% memory usage reduction"
                    })
                
                if memory_trend.get("memory_usage", {}).get("direction") == "increasing":
                    opportunities.append({
                        "type": "memory_leak_prevention",
                        "priority": "medium",
                        "description": "Increasing memory usage trend detected. Potential memory leak.",
                        "recommendations": [
                            "Investigate memory leak sources",
                            "Implement automatic memory cleanup",
                            "Add memory profiling and monitoring"
                        ],
                        "expected_impact": "Prevent memory leaks and improve stability"
                    })
            
            # Analyze execution time patterns  
            if "execution_time" in metrics_data and metrics_data["execution_time"]:
                exec_values = metrics_data["execution_time"]
                avg_exec = sum(exec_values) / len(exec_values)
                max_exec = max(exec_values)
                
                if avg_exec > 5.0:  # More than 5 seconds average
                    opportunities.append({
                        "type": "execution_time_optimization",
                        "priority": "high",
                        "description": f"High execution time ({avg_exec:.2f}s avg). Performance optimization needed.",
                        "recommendations": [
                            "Implement result caching for expensive operations",
                            "Optimize database queries and indexing",
                            "Consider asynchronous processing for long-running tasks"
                        ],
                        "expected_impact": "30-60% execution time reduction"
                    })
                
                exec_volatility = self._calculate_volatility(exec_values)
                if exec_volatility > 0.5:  # High variability
                    opportunities.append({
                        "type": "performance_consistency",
                        "priority": "medium", 
                        "description": f"High execution time variability detected. Inconsistent performance.",
                        "recommendations": [
                            "Implement performance consistency measures",
                            "Add request queuing and load balancing",
                            "Optimize resource allocation strategies"
                        ],
                        "expected_impact": "More consistent and predictable performance"
                    })
            
            # Analyze throughput patterns
            if "throughput" in metrics_data and metrics_data["throughput"]:
                throughput_values = metrics_data["throughput"]
                avg_throughput = sum(throughput_values) / len(throughput_values)
                min_throughput = min(throughput_values)
                
                throughput_stability = self._calculate_stability(throughput_values)
                if throughput_stability < 0.7:  # Low stability
                    opportunities.append({
                        "type": "throughput_optimization",
                        "priority": "medium",
                        "description": f"Unstable throughput detected (stability: {throughput_stability:.2f}).",
                        "recommendations": [
                            "Implement throughput optimization strategies",
                            "Add request batching and processing optimization",
                            "Consider horizontal scaling for increased throughput"
                        ],
                        "expected_impact": "20-50% throughput improvement and stability"
                    })
        
        except Exception as e:
            self.logger.error(f"Optimization opportunity analysis error: {e}")
        
        return opportunities
    
    def _assess_performance_risks(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Assess performance-related risks"""
        risks = {
            "overall_risk_level": "low",
            "risk_factors": [],
            "critical_thresholds": {},
            "mitigation_strategies": []
        }
        
        try:
            risk_score = 0.0
            
            # CPU risk assessment
            if "cpu_usage" in metrics_data and metrics_data["cpu_usage"]:
                cpu_values = metrics_data["cpu_usage"]
                max_cpu = max(cpu_values)
                avg_cpu = sum(cpu_values) / len(cpu_values)
                
                if max_cpu > 95:
                    risk_score += 0.3
                    risks["risk_factors"].append({
                        "factor": "cpu_overload",
                        "severity": "high",
                        "description": f"CPU usage reaching critical levels ({max_cpu:.1f}%)",
                        "potential_impact": "System slowdown or failure"
                    })
                elif avg_cpu > 80:
                    risk_score += 0.2
                    risks["risk_factors"].append({
                        "factor": "high_cpu_usage",
                        "severity": "medium", 
                        "description": f"Sustained high CPU usage ({avg_cpu:.1f}%)",
                        "potential_impact": "Reduced responsiveness and scalability"
                    })
            
            # Memory risk assessment
            if "memory_usage" in metrics_data and metrics_data["memory_usage"]:
                memory_values = metrics_data["memory_usage"]
                max_memory = max(memory_values)
                avg_memory = sum(memory_values) / len(memory_values)
                
                if max_memory > 95:
                    risk_score += 0.4
                    risks["risk_factors"].append({
                        "factor": "memory_exhaustion",
                        "severity": "critical",
                        "description": f"Memory usage near exhaustion ({max_memory:.1f}%)",
                        "potential_impact": "Out of memory errors and system crashes"
                    })
                elif avg_memory > 85:
                    risk_score += 0.25
                    risks["risk_factors"].append({
                        "factor": "high_memory_pressure",
                        "severity": "high",
                        "description": f"High memory pressure ({avg_memory:.1f}%)",
                        "potential_impact": "Increased garbage collection and performance degradation"
                    })
            
            # Performance consistency risk
            for metric in ["execution_time", "throughput", "latency"]:
                if metric in metrics_data and metrics_data[metric]:
                    values = metrics_data[metric]
                    volatility = self._calculate_volatility(values)
                    
                    if volatility > 0.8:  # Very high volatility
                        risk_score += 0.15
                        risks["risk_factors"].append({
                            "factor": f"{metric}_volatility",
                            "severity": "medium",
                            "description": f"High {metric} volatility ({volatility:.2f})",
                            "potential_impact": "Unpredictable user experience and SLA violations"
                        })
            
            # Determine overall risk level
            if risk_score >= 0.7:
                risks["overall_risk_level"] = "critical"
            elif risk_score >= 0.4:
                risks["overall_risk_level"] = "high"
            elif risk_score >= 0.2:
                risks["overall_risk_level"] = "medium"
            else:
                risks["overall_risk_level"] = "low"
            
            # Set critical thresholds
            risks["critical_thresholds"] = {
                "cpu_usage": 95.0,
                "memory_usage": 90.0,
                "execution_time": 10.0,
                "error_rate": 5.0
            }
            
            # Suggest mitigation strategies based on risk level
            if risks["overall_risk_level"] in ["critical", "high"]:
                risks["mitigation_strategies"] = [
                    "Implement immediate performance monitoring and alerting",
                    "Set up automatic scaling mechanisms",
                    "Create performance degradation response procedures",
                    "Establish resource usage limits and circuit breakers"
                ]
            elif risks["overall_risk_level"] == "medium":
                risks["mitigation_strategies"] = [
                    "Enhance performance monitoring coverage",
                    "Implement proactive optimization measures",
                    "Set up early warning systems for resource usage"
                ]
            else:
                risks["mitigation_strategies"] = [
                    "Continue regular performance monitoring",
                    "Maintain performance optimization best practices"
                ]
                
        except Exception as e:
            self.logger.error(f"Risk assessment error: {e}")
        
        return risks


class RealTimePerformanceMonitor:
    """Real-time performance monitoring with streaming analytics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.RealTimePerformanceMonitor")
        
        # Streaming data
        self.metric_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Performance analytics
        self.analytics_engine = AdvancedPerformanceAnalyzer(config)
        
        # Initialize monitoring
        self._initialize_thresholds()
    
    def _initialize_thresholds(self):
        """Initialize performance alert thresholds"""
        self.alert_thresholds = {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 75.0, "critical": 90.0},
            "execution_time": {"warning": 3.0, "critical": 10.0},
            "throughput": {"warning": 10.0, "critical": 5.0},  # Lower is worse for throughput
            "error_rate": {"warning": 1.0, "critical": 5.0},
            "latency": {"warning": 1.0, "critical": 5.0}
        }
    
    async def start_monitoring(self):
        """Start real-time performance monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Real-time performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop real-time performance monitoring"""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Real-time performance monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect real-time metrics
                metrics = await self._collect_realtime_metrics()
                
                # Update metric streams
                self._update_metric_streams(metrics)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Perform real-time analysis
                analysis = await self._perform_realtime_analysis()
                
                # Update analytics
                self._update_analytics(analysis)
                
                await asyncio.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5.0)
    
    async def _collect_realtime_metrics(self) -> Dict[str, float]:
        """Collect real-time performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network metrics if available
            try:
                network = psutil.net_io_counters()
                network_bytes = network.bytes_sent + network.bytes_recv
            except:
                network_bytes = 0
            
            metrics = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": (disk.used / disk.total) * 100,
                "memory_available_gb": memory.available / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
                "network_bytes_total": network_bytes,
                "timestamp": time.time()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
            return {}
    
    def _update_metric_streams(self, metrics: Dict[str, float]):
        """Update metric streams with new data"""
        for metric_name, value in metrics.items():
            if metric_name != "timestamp":
                self.metric_streams[metric_name].append({
                    "value": value,
                    "timestamp": metrics.get("timestamp", time.time())
                })
    
    async def _check_alerts(self, metrics: Dict[str, float]):
        """Check for performance alerts"""
        current_time = time.time()
        
        for metric_name, value in metrics.items():
            if metric_name in self.alert_thresholds and metric_name != "timestamp":
                thresholds = self.alert_thresholds[metric_name]
                
                alert_level = None
                if value >= thresholds.get("critical", float('inf')):
                    alert_level = "critical"
                elif value >= thresholds.get("warning", float('inf')):
                    alert_level = "warning"
                
                # Special handling for throughput (lower is worse)
                if metric_name == "throughput":
                    if value <= thresholds.get("critical", 0):
                        alert_level = "critical"
                    elif value <= thresholds.get("warning", 0):
                        alert_level = "warning"
                
                # Manage alerts
                alert_key = f"{metric_name}_{alert_level}" if alert_level else None
                
                if alert_level:
                    if alert_key not in self.active_alerts:
                        # New alert
                        self.active_alerts[alert_key] = {
                            "metric": metric_name,
                            "level": alert_level,
                            "value": value,
                            "threshold": thresholds.get(alert_level),
                            "started_at": current_time,
                            "count": 1
                        }
                        await self._trigger_alert(self.active_alerts[alert_key])
                    else:
                        # Update existing alert
                        self.active_alerts[alert_key]["count"] += 1
                        self.active_alerts[alert_key]["value"] = value
                else:
                    # Clear alerts for this metric if they exist
                    keys_to_remove = [k for k in self.active_alerts.keys() if k.startswith(f"{metric_name}_")]
                    for key in keys_to_remove:
                        await self._clear_alert(self.active_alerts[key])
                        del self.active_alerts[key]
    
    async def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger a performance alert"""
        self.logger.warning(
            f"PERFORMANCE ALERT - {alert['level'].upper()}: "
            f"{alert['metric']} = {alert['value']:.2f} "
            f"(threshold: {alert['threshold']:.2f})"
        )
        
        # Here you could integrate with external alerting systems
        # like Slack, email, PagerDuty, etc.
    
    async def _clear_alert(self, alert: Dict[str, Any]):
        """Clear a performance alert"""
        duration = time.time() - alert["started_at"]
        self.logger.info(
            f"PERFORMANCE ALERT CLEARED: {alert['metric']} "
            f"(duration: {duration:.1f}s, count: {alert['count']})"
        )
    
    async def _perform_realtime_analysis(self) -> Dict[str, Any]:
        """Perform real-time performance analysis"""
        analysis = {
            "current_metrics": {},
            "trends": {},
            "alerts": len(self.active_alerts),
            "health_score": 100.0
        }
        
        try:
            # Calculate current metric summaries
            for metric_name, stream in self.metric_streams.items():
                if stream:
                    recent_values = [item["value"] for item in list(stream)[-10:]]  # Last 10 values
                    analysis["current_metrics"][metric_name] = {
                        "current": recent_values[-1] if recent_values else 0,
                        "average": sum(recent_values) / len(recent_values),
                        "min": min(recent_values),
                        "max": max(recent_values)
                    }
            
            # Calculate simple trends
            for metric_name, stream in self.metric_streams.items():
                if len(stream) >= 5:
                    recent_values = [item["value"] for item in list(stream)[-5:]]
                    trend = "stable"
                    if recent_values[-1] > recent_values[0] * 1.1:
                        trend = "increasing"
                    elif recent_values[-1] < recent_values[0] * 0.9:
                        trend = "decreasing"
                    
                    analysis["trends"][metric_name] = trend
            
            # Calculate health score
            health_score = 100.0
            
            # Penalize for active alerts
            health_score -= len(self.active_alerts) * 10
            
            # Penalize for high resource usage
            current_metrics = analysis["current_metrics"]
            if "cpu_usage" in current_metrics:
                cpu_usage = current_metrics["cpu_usage"]["current"]
                if cpu_usage > 80:
                    health_score -= (cpu_usage - 80) * 0.5
            
            if "memory_usage" in current_metrics:
                memory_usage = current_metrics["memory_usage"]["current"]
                if memory_usage > 80:
                    health_score -= (memory_usage - 80) * 0.3
            
            analysis["health_score"] = max(0.0, health_score)
            
        except Exception as e:
            self.logger.error(f"Real-time analysis error: {e}")
        
        return analysis
    
    def _update_analytics(self, analysis: Dict[str, Any]):
        """Update analytics with real-time data"""
        # Store analysis results for historical tracking
        if hasattr(self.analytics_engine, 'real_time_analytics'):
            self.analytics_engine.real_time_analytics = analysis
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current performance status"""
        return {
            "monitoring_active": self.monitoring_active,
            "active_alerts": len(self.active_alerts),
            "alert_details": list(self.active_alerts.values()),
            "metric_streams_count": {name: len(stream) for name, stream in self.metric_streams.items()},
            "health_score": getattr(self.analytics_engine, 'real_time_analytics', {}).get('health_score', 100.0)
        }
    
    def get_metric_history(self, metric_name: str, duration_minutes: int = 10) -> List[Dict[str, Any]]:
        """Get metric history for specified duration"""
        if metric_name not in self.metric_streams:
            return []
        
        cutoff_time = time.time() - (duration_minutes * 60)
        return [
            item for item in self.metric_streams[metric_name]
            if item["timestamp"] >= cutoff_time
        ]
