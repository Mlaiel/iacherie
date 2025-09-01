"""Performance Validation Engine for Crawler System
===============================================

Advanced performance validation and optimization system for the IA Influencer Agent Platform
providing comprehensive performance metrics, bottleneck detection, and optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use, reproduction, or distribution strictly prohibited

Features:
- Real-time performance monitoring
- Resource utilization validation
- Scalability assessment
- Performance bottleneck detection
- Optimization recommendations
"""
import time
import psutil
import threading
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import statistics

from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Performance metric types"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_PERFORMANCE = "database_performance"
    CONCURRENT_USERS = "concurrent_users"


class PerformanceLevel(Enum):
    """Performance level classifications"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


class ResourceType(Enum):
    """System resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class PerformanceMeasurement:
    """Individual performance measurement"""
    metric: PerformanceMetric
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    threshold_passed: bool = True
    baseline_value: Optional[float] = None
    
    @property
    def deviation_from_baseline(self) -> Optional[float]:
        """Calculate deviation from baseline"""
        if self.baseline_value is not None:
            return ((self.value - self.baseline_value) / self.baseline_value) * 100
        return None


@dataclass
class PerformanceProfile:
    """Comprehensive performance profile"""
    overall_score: float
    performance_level: PerformanceLevel
    measurements: Dict[PerformanceMetric, PerformanceMeasurement] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    resource_utilization: Dict[ResourceType, float] = field(default_factory=dict)
    scalability_score: float = 0.0
    reliability_score: float = 0.0
    efficiency_score: float = 0.0
    assessment_duration: float = 0.0
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def critical_issues(self) -> List[str]:
        """Get critical performance issues"""
        return [issue for issue in self.bottlenecks if "critical" in issue.lower()]
    
    @property
    def passed_metrics_count(self) -> int:
        """Count of metrics that passed thresholds"""
        return sum(1 for m in self.measurements.values() if m.threshold_passed)
    
    @property
    def total_metrics_count(self) -> int:
        """Total number of metrics measured"""
        return len(self.measurements)
    
    @property
    def success_rate(self) -> float:
        """Calculate metric success rate"""
        if self.total_metrics_count == 0:
            return 0.0
        return self.passed_metrics_count / self.total_metrics_count


class PerformanceThresholds:
    """Performance threshold definitions"""
    
    def __init__(self):
        self.thresholds = {
            PerformanceMetric.RESPONSE_TIME: {'good': 200, 'acceptable': 500, 'poor': 2000},  # ms
            PerformanceMetric.THROUGHPUT: {'good': 1000, 'acceptable': 500, 'poor': 100},  # requests/sec
            PerformanceMetric.CPU_USAGE: {'good': 60, 'acceptable': 80, 'poor': 95},  # %
            PerformanceMetric.MEMORY_USAGE: {'good': 70, 'acceptable': 85, 'poor': 95},  # %
            PerformanceMetric.DISK_IO: {'good': 100, 'acceptable': 200, 'poor': 500},  # MB/s
            PerformanceMetric.NETWORK_IO: {'good': 100, 'acceptable': 200, 'poor': 500},  # MB/s
            PerformanceMetric.ERROR_RATE: {'good': 1, 'acceptable': 5, 'poor': 10},  # %
            PerformanceMetric.CACHE_HIT_RATE: {'good': 90, 'acceptable': 80, 'poor': 60},  # %
            PerformanceMetric.DATABASE_PERFORMANCE: {'good': 50, 'acceptable': 100, 'poor': 500},  # ms
            PerformanceMetric.CONCURRENT_USERS: {'good': 1000, 'acceptable': 500, 'poor': 100}  # users
        }
    
    def get_threshold_level(self, metric: PerformanceMetric, value: float) -> PerformanceLevel:
        """Get performance level based on metric value"""
        thresholds = self.thresholds.get(metric, {})
        
        if metric == PerformanceMetric.ERROR_RATE:
            # Lower is better for error rate
            if value <= thresholds.get('good', 1):
                return PerformanceLevel.EXCELLENT
            elif value <= thresholds.get('acceptable', 5):
                return PerformanceLevel.GOOD
            elif value <= thresholds.get('poor', 10):
                return PerformanceLevel.ACCEPTABLE
            else:
                return PerformanceLevel.CRITICAL
        
        elif metric in [PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE]:
            # Lower is better for resource usage
            if value <= thresholds.get('good', 60):
                return PerformanceLevel.EXCELLENT
            elif value <= thresholds.get('acceptable', 80):
                return PerformanceLevel.GOOD
            elif value <= thresholds.get('poor', 95):
                return PerformanceLevel.ACCEPTABLE
            else:
                return PerformanceLevel.CRITICAL
        
        elif metric == PerformanceMetric.CACHE_HIT_RATE:
            # Higher is better for cache hit rate
            if value >= thresholds.get('good', 90):
                return PerformanceLevel.EXCELLENT
            elif value >= thresholds.get('acceptable', 80):
                return PerformanceLevel.GOOD
            elif value >= thresholds.get('poor', 60):
                return PerformanceLevel.ACCEPTABLE
            else:
                return PerformanceLevel.CRITICAL
        
        else:
            # For response time, throughput, etc. - context dependent
            if metric == PerformanceMetric.RESPONSE_TIME:
                # Lower is better
                if value <= thresholds.get('good', 200):
                    return PerformanceLevel.EXCELLENT
                elif value <= thresholds.get('acceptable', 500):
                    return PerformanceLevel.GOOD
                elif value <= thresholds.get('poor', 2000):
                    return PerformanceLevel.ACCEPTABLE
                else:
                    return PerformanceLevel.CRITICAL
            else:
                # Higher is better (throughput, concurrent users)
                if value >= thresholds.get('good', 1000):
                    return PerformanceLevel.EXCELLENT
                elif value >= thresholds.get('acceptable', 500):
                    return PerformanceLevel.GOOD
                elif value >= thresholds.get('poor', 100):
                    return PerformanceLevel.ACCEPTABLE
                else:
                    return PerformanceLevel.CRITICAL


class PerformanceValidator:
    """
    Enterprise-grade performance validation engine for crawler systems.
    
    Provides comprehensive performance assessment including:
    - Real-time performance monitoring
    - Resource utilization validation
    - Scalability assessment
    - Bottleneck detection and analysis
    - Performance optimization recommendations
    """
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.thresholds = PerformanceThresholds()
        self.monitoring_interval = monitoring_interval
        self.baseline_measurements = {}
        self.historical_data = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Performance tracking
        self.measurement_history = []
        self.max_history_size = 1000
        
        logger.info("PerformanceValidator initialized")
    
    def validate_performance(
        self,
        operation_func: Callable[[], Any],
        operation_name: str = "unknown_operation",
        expected_load: Optional[Dict[str, Any]] = None,
        custom_thresholds: Optional[Dict[PerformanceMetric, Dict[str, float]]] = None
    ) -> PerformanceProfile:
        """
        Validate performance of a specific operation.
        
        Args:
            operation_func: Function to execute and measure
            operation_name: Name of the operation being measured
            expected_load: Expected load characteristics
            custom_thresholds: Custom performance thresholds
            
        Returns:
            PerformanceProfile: Comprehensive performance assessment
        """
        start_time = time.time()
        
        profile = PerformanceProfile(
            overall_score=0.0,
            performance_level=PerformanceLevel.GOOD
        )
        
        # Apply custom thresholds if provided
        if custom_thresholds:
            for metric, threshold_dict in custom_thresholds.items():
                self.thresholds.thresholds[metric] = threshold_dict
        
        try:
            # Start monitoring
            self._start_performance_monitoring()
            
            # Measure operation execution
            execution_start = time.time()
            result = operation_func()
            execution_time = (time.time() - execution_start) * 1000  # ms
            
            # Stop monitoring and collect measurements
            measurements = self._stop_performance_monitoring()
            
            # Add execution time measurement
            profile.measurements[PerformanceMetric.RESPONSE_TIME] = PerformanceMeasurement(
                metric=PerformanceMetric.RESPONSE_TIME,
                value=execution_time,
                unit="ms",
                context={'operation': operation_name, 'result_type': type(result).__name__}
            )
            
            # Add system resource measurements
            for metric, measurement in measurements.items():
                profile.measurements[metric] = measurement
            
            # Validate against thresholds
            self._validate_thresholds(profile)
            
            # Assess resource utilization
            self._assess_resource_utilization(profile)
            
            # Detect bottlenecks
            self._detect_bottlenecks(profile)
            
            # Calculate scores
            self._calculate_performance_scores(profile)
            
            # Generate recommendations
            self._generate_recommendations(profile, expected_load)
            
            # Determine overall performance level
            self._determine_performance_level(profile)
            
        except Exception as e:
            logger.error(f"Performance validation failed: {str(e)}")
            profile.bottlenecks.append(f"Performance validation error: {str(e)}")
            profile.performance_level = PerformanceLevel.CRITICAL
        
        # Record assessment duration
        profile.assessment_duration = time.time() - start_time
        
        # Store in history
        self._store_measurement_history(profile)
        
        logger.debug(f"Performance validation completed for '{operation_name}'")
        return profile
    
    def continuous_monitoring(
        self,
        duration_seconds: float,
        sample_interval: float = 1.0
    ) -> List[PerformanceProfile]:
        """
        Perform continuous performance monitoring.
        
        Args:
            duration_seconds: Duration of monitoring in seconds
            sample_interval: Interval between samples in seconds
            
        Returns:
            List[PerformanceProfile]: Time series of performance profiles
        """
        profiles = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            sample_start = time.time()
            
            # Take performance snapshot
            profile = self._take_performance_snapshot()
            profiles.append(profile)
            
            # Wait for next sample
            elapsed = time.time() - sample_start
            if elapsed < sample_interval:
                time.sleep(sample_interval - elapsed)
        
        logger.info(f"Continuous monitoring completed: {len(profiles)} samples")
        return profiles
    
    def validate_scalability(
        self,
        operation_func: Callable[[int], Any],
        load_levels: List[int],
        operation_name: str = "scalability_test"
    ) -> Dict[str, Any]:
        """
        Validate system scalability under different load levels.
        
        Args:
            operation_func: Function that accepts load level parameter
            load_levels: List of load levels to test
            operation_name: Name of the scalability test
            
        Returns:
            Dict[str, Any]: Scalability assessment results
        """
        scalability_results = {
            'load_profiles': {},
            'scalability_score': 0.0,
            'bottleneck_load_level': None,
            'recommended_max_load': None,
            'linear_scalability': False
        }
        
        response_times = []
        throughputs = []
        
        for load_level in load_levels:
            logger.info(f"Testing scalability at load level: {load_level}")
            
            profile = self.validate_performance(
                lambda: operation_func(load_level),
                f"{operation_name}_load_{load_level}"
            )
            
            scalability_results['load_profiles'][load_level] = profile
            
            # Extract key metrics
            response_time = profile.measurements.get(PerformanceMetric.RESPONSE_TIME)
            if response_time:
                response_times.append((load_level, response_time.value))
            
            # Calculate throughput if possible
            if response_time and response_time.value > 0:
                throughput = (load_level / response_time.value) * 1000  # requests per second
                throughputs.append((load_level, throughput))
            
            # Check for critical performance degradation
            if profile.performance_level == PerformanceLevel.CRITICAL:
                scalability_results['bottleneck_load_level'] = load_level
                break
        
        # Analyze scalability patterns
        scalability_results.update(self._analyze_scalability_patterns(
            response_times, throughputs, load_levels
        ))
        
        return scalability_results
    
    def benchmark_against_baseline(
        self,
        operation_func: Callable[[], Any],
        baseline_name: str,
        operation_name: str = "benchmark_test"
    ) -> Dict[str, Any]:
        """
        Benchmark performance against established baseline.
        
        Args:
            operation_func: Function to benchmark
            baseline_name: Name of baseline to compare against
            operation_name: Name of the benchmark operation
            
        Returns:
            Dict[str, Any]: Benchmark comparison results
        """
        # Execute performance validation
        current_profile = self.validate_performance(operation_func, operation_name)
        
        # Get baseline measurements
        baseline_measurements = self.baseline_measurements.get(baseline_name, {})
        
        benchmark_results = {
            'current_profile': current_profile,
            'baseline_comparison': {},
            'performance_regression': False,
            'improvement_areas': [],
            'regression_areas': []
        }
        
        # Compare against baseline
        for metric, current_measurement in current_profile.measurements.items():
            baseline_value = baseline_measurements.get(metric)
            
            if baseline_value is not None:
                current_measurement.baseline_value = baseline_value
                deviation = current_measurement.deviation_from_baseline
                
                comparison = {
                    'current_value': current_measurement.value,
                    'baseline_value': baseline_value,
                    'deviation_percent': deviation,
                    'improved': False,
                    'regressed': False
                }
                
                # Determine improvement/regression based on metric type
                if metric in [PerformanceMetric.RESPONSE_TIME, PerformanceMetric.CPU_USAGE, 
                             PerformanceMetric.MEMORY_USAGE, PerformanceMetric.ERROR_RATE]:
                    # Lower is better
                    if deviation < -5:  # 5% improvement threshold
                        comparison['improved'] = True
                        benchmark_results['improvement_areas'].append(metric.value)
                    elif deviation > 10:  # 10% regression threshold
                        comparison['regressed'] = True
                        benchmark_results['regression_areas'].append(metric.value)
                        benchmark_results['performance_regression'] = True
                else:
                    # Higher is better
                    if deviation > 5:  # 5% improvement threshold
                        comparison['improved'] = True
                        benchmark_results['improvement_areas'].append(metric.value)
                    elif deviation < -10:  # 10% regression threshold
                        comparison['regressed'] = True
                        benchmark_results['regression_areas'].append(metric.value)
                        benchmark_results['performance_regression'] = True
                
                benchmark_results['baseline_comparison'][metric.value] = comparison
        
        return benchmark_results
    
    def set_baseline(self, baseline_name: str, measurements: Dict[PerformanceMetric, float]) -> None:
        """Set performance baseline for future comparisons"""
        self.baseline_measurements[baseline_name] = measurements
        logger.info(f"Set performance baseline: {baseline_name}")
    
    def get_performance_trends(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Filter historical data
        recent_measurements = [
            profile for profile in self.measurement_history
            if profile.assessed_at >= cutoff_time
        ]
        
        if not recent_measurements:
            return {'message': 'No recent performance data available'}
        
        trends = {}
        
        # Analyze trends for each metric
        for metric in PerformanceMetric:
            values = []
            timestamps = []
            
            for profile in recent_measurements:
                if metric in profile.measurements:
                    values.append(profile.measurements[metric].value)
                    timestamps.append(profile.assessed_at)
            
            if len(values) >= 2:
                # Calculate trend direction
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                
                trend_direction = "improving" if second_avg < first_avg else "degrading"
                if metric in [PerformanceMetric.THROUGHPUT, PerformanceMetric.CACHE_HIT_RATE]:
                    trend_direction = "improving" if second_avg > first_avg else "degrading"
                
                trends[metric.value] = {
                    'direction': trend_direction,
                    'first_period_avg': first_avg,
                    'second_period_avg': second_avg,
                    'change_percent': ((second_avg - first_avg) / first_avg) * 100,
                    'sample_count': len(values),
                    'min_value': min(values),
                    'max_value': max(values),
                    'std_deviation': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return {
            'time_window_hours': time_window_hours,
            'sample_count': len(recent_measurements),
            'trends': trends,
            'overall_stability': self._assess_overall_stability(recent_measurements)
        }
    
    # Helper methods
    
    def _start_performance_monitoring(self) -> None:
        """Start performance monitoring"""
        self.monitoring_active = True
        self.current_measurements = {}
    
    def _stop_performance_monitoring(self) -> Dict[PerformanceMetric, PerformanceMeasurement]:
        """Stop monitoring and return measurements"""
        self.monitoring_active = False
        
        measurements = {}
        
        # Get system resource measurements
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            measurements[PerformanceMetric.CPU_USAGE] = PerformanceMeasurement(
                metric=PerformanceMetric.CPU_USAGE,
                value=cpu_percent,
                unit="%"
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            measurements[PerformanceMetric.MEMORY_USAGE] = PerformanceMeasurement(
                metric=PerformanceMetric.MEMORY_USAGE,
                value=memory.percent,
                unit="%"
            )
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_speed = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)  # MB
                measurements[PerformanceMetric.DISK_IO] = PerformanceMeasurement(
                    metric=PerformanceMetric.DISK_IO,
                    value=disk_speed,
                    unit="MB/s"
                )
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                network_speed = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)  # MB
                measurements[PerformanceMetric.NETWORK_IO] = PerformanceMeasurement(
                    metric=PerformanceMetric.NETWORK_IO,
                    value=network_speed,
                    unit="MB/s"
                )
            
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {str(e)}")
        
        return measurements
    
    def _take_performance_snapshot(self) -> PerformanceProfile:
        """Take a performance snapshot at current moment"""
        profile = PerformanceProfile(
            overall_score=0.0,
            performance_level=PerformanceLevel.GOOD
        )
        
        # Collect system metrics
        measurements = self._stop_performance_monitoring()
        profile.measurements = measurements
        
        # Validate against thresholds
        self._validate_thresholds(profile)
        
        # Calculate basic scores
        self._calculate_performance_scores(profile)
        
        return profile
    
    def _validate_thresholds(self, profile: PerformanceProfile) -> None:
        """Validate measurements against performance thresholds"""
        for metric, measurement in profile.measurements.items():
            threshold_level = self.thresholds.get_threshold_level(metric, measurement.value)
            measurement.threshold_passed = threshold_level in [
                PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD, PerformanceLevel.ACCEPTABLE
            ]
    
    def _assess_resource_utilization(self, profile: PerformanceProfile) -> None:
        """Assess resource utilization levels"""
        resource_mapping = {
            PerformanceMetric.CPU_USAGE: ResourceType.CPU,
            PerformanceMetric.MEMORY_USAGE: ResourceType.MEMORY,
            PerformanceMetric.DISK_IO: ResourceType.DISK,
            PerformanceMetric.NETWORK_IO: ResourceType.NETWORK
        }
        
        for metric, resource_type in resource_mapping.items():
            if metric in profile.measurements:
                utilization = profile.measurements[metric].value
                profile.resource_utilization[resource_type] = utilization
    
    def _detect_bottlenecks(self, profile: PerformanceProfile) -> None:
        """Detect performance bottlenecks"""
        
        # Check for resource bottlenecks
        for resource_type, utilization in profile.resource_utilization.items():
            if utilization > 90:
                profile.bottlenecks.append(f"Critical {resource_type.value} utilization: {utilization:.1f}%")
            elif utilization > 80:
                profile.bottlenecks.append(f"High {resource_type.value} utilization: {utilization:.1f}%")
        
        # Check for response time bottlenecks
        if PerformanceMetric.RESPONSE_TIME in profile.measurements:
            response_time = profile.measurements[PerformanceMetric.RESPONSE_TIME].value
            if response_time > 5000:  # 5 seconds
                profile.bottlenecks.append(f"Critical response time: {response_time:.0f}ms")
            elif response_time > 2000:  # 2 seconds
                profile.bottlenecks.append(f"High response time: {response_time:.0f}ms")
        
        # Check for error rate bottlenecks
        if PerformanceMetric.ERROR_RATE in profile.measurements:
            error_rate = profile.measurements[PerformanceMetric.ERROR_RATE].value
            if error_rate > 10:
                profile.bottlenecks.append(f"Critical error rate: {error_rate:.1f}%")
            elif error_rate > 5:
                profile.bottlenecks.append(f"High error rate: {error_rate:.1f}%")
    
    def _calculate_performance_scores(self, profile: PerformanceProfile) -> None:
        """Calculate various performance scores"""
        
        # Scalability score (based on resource efficiency)
        resource_scores = []
        for utilization in profile.resource_utilization.values():
            if utilization <= 70:
                resource_scores.append(1.0)
            elif utilization <= 85:
                resource_scores.append(0.8)
            elif utilization <= 95:
                resource_scores.append(0.6)
            else:
                resource_scores.append(0.2)
        
        profile.scalability_score = statistics.mean(resource_scores) if resource_scores else 0.5
        
        # Reliability score (based on error rates and stability)
        if PerformanceMetric.ERROR_RATE in profile.measurements:
            error_rate = profile.measurements[PerformanceMetric.ERROR_RATE].value
            profile.reliability_score = max(0.0, 1.0 - (error_rate / 100))
        else:
            profile.reliability_score = 0.8  # Default moderate score
        
        # Efficiency score (based on response time and throughput)
        efficiency_factors = []
        
        if PerformanceMetric.RESPONSE_TIME in profile.measurements:
            response_time = profile.measurements[PerformanceMetric.RESPONSE_TIME].value
            if response_time <= 200:
                efficiency_factors.append(1.0)
            elif response_time <= 500:
                efficiency_factors.append(0.8)
            elif response_time <= 1000:
                efficiency_factors.append(0.6)
            else:
                efficiency_factors.append(0.4)
        
        if PerformanceMetric.THROUGHPUT in profile.measurements:
            throughput = profile.measurements[PerformanceMetric.THROUGHPUT].value
            if throughput >= 1000:
                efficiency_factors.append(1.0)
            elif throughput >= 500:
                efficiency_factors.append(0.8)
            elif throughput >= 100:
                efficiency_factors.append(0.6)
            else:
                efficiency_factors.append(0.4)
        
        profile.efficiency_score = statistics.mean(efficiency_factors) if efficiency_factors else 0.7
        
        # Overall score (weighted average)
        weights = {'scalability': 0.3, 'reliability': 0.4, 'efficiency': 0.3}
        profile.overall_score = (
            profile.scalability_score * weights['scalability'] +
            profile.reliability_score * weights['reliability'] +
            profile.efficiency_score * weights['efficiency']
        )
    
    def _generate_recommendations(
        self, 
        profile: PerformanceProfile, 
        expected_load: Optional[Dict[str, Any]] = None
    ) -> None:
        """Generate performance optimization recommendations"""
        
        # Resource-based recommendations
        for resource_type, utilization in profile.resource_utilization.items():
            if utilization > 85:
                if resource_type == ResourceType.CPU:
                    profile.recommendations.append("Consider CPU optimization or horizontal scaling")
                elif resource_type == ResourceType.MEMORY:
                    profile.recommendations.append("Optimize memory usage or increase available memory")
                elif resource_type == ResourceType.DISK:
                    profile.recommendations.append("Optimize disk I/O or upgrade storage performance")
                elif resource_type == ResourceType.NETWORK:
                    profile.recommendations.append("Optimize network usage or increase bandwidth")
        
        # Response time recommendations
        if PerformanceMetric.RESPONSE_TIME in profile.measurements:
            response_time = profile.measurements[PerformanceMetric.RESPONSE_TIME].value
            if response_time > 1000:
                profile.recommendations.append("Implement caching and optimize database queries")
                profile.recommendations.append("Consider asynchronous processing for long operations")
        
        # Cache recommendations
        if PerformanceMetric.CACHE_HIT_RATE in profile.measurements:
            cache_hit_rate = profile.measurements[PerformanceMetric.CACHE_HIT_RATE].value
            if cache_hit_rate < 80:
                profile.recommendations.append("Optimize caching strategy and cache key design")
        
        # Error rate recommendations
        if PerformanceMetric.ERROR_RATE in profile.measurements:
            error_rate = profile.measurements[PerformanceMetric.ERROR_RATE].value
            if error_rate > 5:
                profile.recommendations.append("Investigate and fix error sources")
                profile.recommendations.append("Implement better error handling and retry mechanisms")
        
        # General recommendations based on overall score
        if profile.overall_score < 0.6:
            profile.recommendations.append("Consider comprehensive performance audit and optimization")
        elif profile.overall_score < 0.8:
            profile.recommendations.append("Focus on identified bottlenecks for targeted improvements")
    
    def _determine_performance_level(self, profile: PerformanceProfile) -> None:
        """Determine overall performance level"""
        score = profile.overall_score
        
        if len(profile.critical_issues) > 0:
            profile.performance_level = PerformanceLevel.CRITICAL
        elif score >= 0.9:
            profile.performance_level = PerformanceLevel.EXCELLENT
        elif score >= 0.8:
            profile.performance_level = PerformanceLevel.GOOD
        elif score >= 0.6:
            profile.performance_level = PerformanceLevel.ACCEPTABLE
        elif score >= 0.4:
            profile.performance_level = PerformanceLevel.POOR
        else:
            profile.performance_level = PerformanceLevel.CRITICAL
    
    def _analyze_scalability_patterns(
        self, 
        response_times: List[Tuple[int, float]], 
        throughputs: List[Tuple[int, float]], 
        load_levels: List[int]
    ) -> Dict[str, Any]:
        """Analyze scalability patterns from test results"""
        
        analysis = {
            'scalability_score': 0.0,
            'linear_scalability': False,
            'recommended_max_load': None,
            'scalability_pattern': 'unknown'
        }
        
        if len(response_times) < 2:
            return analysis
        
        # Analyze response time trend
        load_increase_ratio = response_times[-1][0] / response_times[0][0] if response_times[0][0] > 0 else 1
        response_time_increase_ratio = response_times[-1][1] / response_times[0][1] if response_times[0][1] > 0 else 1
        
        # Determine scalability pattern
        if response_time_increase_ratio <= load_increase_ratio * 1.2:
            analysis['scalability_pattern'] = 'linear'
            analysis['linear_scalability'] = True
            analysis['scalability_score'] = 0.9
        elif response_time_increase_ratio <= load_increase_ratio * 2:
            analysis['scalability_pattern'] = 'sub_linear'
            analysis['scalability_score'] = 0.7
        elif response_time_increase_ratio <= load_increase_ratio * 4:
            analysis['scalability_pattern'] = 'poor'
            analysis['scalability_score'] = 0.4
        else:
            analysis['scalability_pattern'] = 'critical'
            analysis['scalability_score'] = 0.2
        
        # Recommend maximum load
        acceptable_response_time = 2000  # 2 seconds
        for load, response_time in response_times:
            if response_time > acceptable_response_time:
                analysis['recommended_max_load'] = max(1, load - 1)
                break
        else:
            analysis['recommended_max_load'] = load_levels[-1]
        
        return analysis
    
    def _assess_overall_stability(self, recent_measurements: List[PerformanceProfile]) -> Dict[str, Any]:
        """Assess overall system stability from recent measurements"""
        if not recent_measurements:
            return {'stability_score': 0.0, 'stability_level': 'unknown'}
        
        # Calculate coefficient of variation for key metrics
        stability_scores = []
        
        for metric in [PerformanceMetric.RESPONSE_TIME, PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE]:
            values = []
            for profile in recent_measurements:
                if metric in profile.measurements:
                    values.append(profile.measurements[metric].value)
            
            if len(values) > 1:
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values)
                cv = (std_val / mean_val) if mean_val > 0 else 0
                
                # Lower coefficient of variation = higher stability
                stability_score = max(0.0, 1.0 - cv)
                stability_scores.append(stability_score)
        
        overall_stability = statistics.mean(stability_scores) if stability_scores else 0.5
        
        if overall_stability >= 0.9:
            stability_level = 'excellent'
        elif overall_stability >= 0.8:
            stability_level = 'good'
        elif overall_stability >= 0.6:
            stability_level = 'acceptable'
        elif overall_stability >= 0.4:
            stability_level = 'poor'
        else:
            stability_level = 'critical'
        
        return {
            'stability_score': overall_stability,
            'stability_level': stability_level,
            'sample_count': len(recent_measurements)
        }
    
    def _store_measurement_history(self, profile: PerformanceProfile) -> None:
        """Store measurement in history for trend analysis"""
        self.measurement_history.append(profile)
        
        # Limit history size
        if len(self.measurement_history) > self.max_history_size:
            self.measurement_history = self.measurement_history[-self.max_history_size:]
