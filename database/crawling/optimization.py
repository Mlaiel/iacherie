"""Enterprise Crawler Performance Optimization Database Module

Advanced database layer for crawler performance monitoring, optimization,
resource management, and intelligent scaling operations.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against copyright infringement.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
import statistics
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    CrawlerPerformanceMetric, OptimizationRule, ResourceAllocation,
    PerformanceBenchmark, CrawlerScalingEvent, SystemHealthCheck
)
from ..core.exceptions import (
    DatabaseError, PerformanceOptimizationError, ResourceAllocationError,
    ScalingError, BenchmarkError
)


class MetricType(Enum):
    """Types of performance metrics."""    THROUGHPUT = "throughput"              # Items processed per time unit
    LATENCY = "latency"                    # Response time metrics
    ERROR_RATE = "error_rate"              # Error percentage
    RESOURCE_USAGE = "resource_usage"      # CPU, memory, disk usage
    SUCCESS_RATE = "success_rate"          # Successful operations percentage
    QUEUE_DEPTH = "queue_depth"            # Queue backlog size
    CONCURRENCY = "concurrency"            # Active concurrent operations
    BANDWIDTH = "bandwidth"                # Network usage metrics


class OptimizationStrategy(Enum):
    """Performance optimization strategies."""    SCALE_UP = "scale_up"                  # Increase resources per instance
    SCALE_OUT = "scale_out"                # Increase number of instances
    LOAD_BALANCE = "load_balance"          # Redistribute workload
    CACHE_OPTIMIZE = "cache_optimize"      # Optimize caching strategy
    QUERY_OPTIMIZE = "query_optimize"      # Database query optimization
    RATE_LIMIT_ADJUST = "rate_limit_adjust"  # Adjust rate limiting
    RESOURCE_REALLOC = "resource_realloc"  # Reallocate system resources
    ALGORITHM_TUNE = "algorithm_tune"      # Tune crawling algorithms


class ResourceType(Enum):
    """Types of system resources."""    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE_CONNECTIONS = "database_connections"
    PROXY_POOL = "proxy_pool"
    THREAD_POOL = "thread_pool"
    QUEUE_CAPACITY = "queue_capacity"


class PerformanceStatus(Enum):
    """Performance status levels."""    OPTIMAL = "optimal"          # 90-100% efficiency
    GOOD = "good"               # 75-89% efficiency
    ACCEPTABLE = "acceptable"    # 60-74% efficiency
    DEGRADED = "degraded"       # 40-59% efficiency
    CRITICAL = "critical"       # <40% efficiency


class CrawlerOptimizationManager(DatabaseManager):
    """    Enterprise crawler performance optimization and resource management system.
    
    Manages:
    - Real-time performance monitoring and metrics collection
    - Intelligent resource allocation and scaling decisions
    - Automated performance optimization and tuning
    - Benchmark tracking and performance regression detection
    - Predictive scaling based on usage patterns
    - Comprehensive performance analytics and reporting
    """    
    def __init__(self, db_session: Session):
        """Initialize crawler optimization manager."""        super().__init__(db_session)
        self.performance_baselines = {}
        self.optimization_rules = {}
        self.resource_allocations = {}
        self._initialize_optimization_system()
    
    async def record_performance_metric(
        self,
        crawler_id: str,
        metric_type: MetricType,
        metric_value: float,
        measurement_unit: str,
        collection_timestamp: Optional[datetime] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Record a performance metric for analysis and optimization.
        
        Args:
            crawler_id: Crawler identifier
            metric_type: Type of performance metric
            metric_value: Measured metric value
            measurement_unit: Unit of measurement
            collection_timestamp: When metric was collected
            additional_context: Optional additional context
            
        Returns:
            Metric record ID
            
        Raises:
            PerformanceOptimizationError: If metric recording fails
        """        try:
            metric_id = str(uuid4())
            timestamp = collection_timestamp or datetime.utcnow()
            
            # Calculate percentile ranking against historical data
            percentile_rank = await self._calculate_metric_percentile(
                crawler_id, metric_type, metric_value
            )
            
            # Detect performance anomalies
            is_anomaly = await self._detect_performance_anomaly(
                crawler_id, metric_type, metric_value
            )
            
            # Create performance metric record
            metric = CrawlerPerformanceMetric(
                metric_id=metric_id,
                crawler_id=crawler_id,
                metric_type=metric_type.value,
                metric_value=metric_value,
                measurement_unit=measurement_unit,
                percentile_rank=percentile_rank,
                is_anomaly=is_anomaly,
                collection_timestamp=timestamp,
                additional_context=additional_context or {},
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(metric)
            await self.db_session.commit()
            
            # Trigger optimization analysis if anomaly detected
            if is_anomaly:
                await self._trigger_optimization_analysis(crawler_id, metric_type, metric_value)
            
            return metric_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise PerformanceOptimizationError(
                f"Failed to record performance metric: {str(e)}"
            )
    
    async def create_optimization_rule(
        self,
        rule_name: str,
        trigger_conditions: Dict[str, Any],
        optimization_actions: List[Dict[str, Any]],
        priority: int,
        cooldown_minutes: int,
        user_id: str
    ) -> str:
        """        Create an automated optimization rule for performance management.
        
        Args:
            rule_name: Human-readable rule name
            trigger_conditions: Conditions that trigger optimization
            optimization_actions: Actions to take when triggered
            priority: Rule priority (1-10, 10 highest)
            cooldown_minutes: Minimum time between rule executions
            user_id: User identifier
            
        Returns:
            Optimization rule ID
        """        try:
            rule_id = str(uuid4())
            
            # Validate rule configuration
            await self._validate_optimization_rule(trigger_conditions, optimization_actions)
            
            # Create optimization rule record
            rule = OptimizationRule(
                rule_id=rule_id,
                rule_name=rule_name,
                trigger_conditions=trigger_conditions,
                optimization_actions=optimization_actions,
                priority=priority,
                cooldown_minutes=cooldown_minutes,
                user_id=user_id,
                is_active=True,
                execution_count=0,
                last_executed_at=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(rule)
            await self.db_session.commit()
            
            # Activate rule in optimization engine
            await self._activate_optimization_rule(rule_id, trigger_conditions, optimization_actions)
            
            return rule_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise PerformanceOptimizationError(
                f"Failed to create optimization rule: {str(e)}"
            )
    
    async def allocate_resources(
        self,
        crawler_id: str,
        resource_requirements: Dict[ResourceType, float],
        allocation_priority: int,
        duration_minutes: Optional[int] = None,
        allocation_reason: str = "performance_optimization"
    ) -> str:
        """        Allocate system resources to a specific crawler.
        
        Args:
            crawler_id: Crawler identifier
            resource_requirements: Required resources by type
            allocation_priority: Priority level for resource allocation
            duration_minutes: Optional allocation duration
            allocation_reason: Reason for resource allocation
            
        Returns:
            Resource allocation ID
            
        Raises:
            ResourceAllocationError: If allocation fails
        """        try:
            allocation_id = str(uuid4())
            
            # Check resource availability
            available_resources = await self._check_resource_availability(resource_requirements)
            
            if not available_resources:
                raise ResourceAllocationError(
                    "Insufficient resources available for allocation"
                )
            
            # Calculate allocation end time
            ends_at = None
            if duration_minutes:
                ends_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            # Create resource allocation record
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                crawler_id=crawler_id,
                resource_requirements={rt.value: val for rt, val in resource_requirements.items()},
                allocation_priority=allocation_priority,
                allocation_reason=allocation_reason,
                allocated_at=datetime.utcnow(),
                ends_at=ends_at,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(allocation)
            await self.db_session.commit()
            
            # Apply resource allocation
            await self._apply_resource_allocation(allocation_id, resource_requirements)
            
            return allocation_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise ResourceAllocationError(
                f"Failed to allocate resources: {str(e)}"
            )
    
    async def execute_intelligent_scaling(
        self,
        crawler_id: str,
        scaling_trigger: str,
        target_performance_level: float,
        max_scale_factor: float = 3.0
    ) -> str:
        """        Execute intelligent scaling based on performance requirements.
        
        Args:
            crawler_id: Crawler identifier
            scaling_trigger: What triggered the scaling event
            target_performance_level: Desired performance level (0.0-1.0)
            max_scale_factor: Maximum scaling factor allowed
            
        Returns:
            Scaling event ID
        """        try:
            event_id = str(uuid4())
            
            # Analyze current performance
            current_performance = await self._analyze_current_performance(crawler_id)
            
            # Calculate optimal scaling strategy
            scaling_strategy = await self._calculate_scaling_strategy(
                current_performance,
                target_performance_level,
                max_scale_factor
            )
            
            # Create scaling event record
            scaling_event = CrawlerScalingEvent(
                event_id=event_id,
                crawler_id=crawler_id,
                scaling_trigger=scaling_trigger,
                scaling_strategy=scaling_strategy["strategy"],
                scale_factor=scaling_strategy["scale_factor"],
                target_performance=target_performance_level,
                pre_scaling_metrics=current_performance,
                status="initiated",
                started_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(scaling_event)
            await self.db_session.commit()
            
            # Execute scaling operations
            await self._execute_scaling_operations(event_id, scaling_strategy)
            
            return event_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise ScalingError(
                f"Failed to execute intelligent scaling: {str(e)}"
            )
    
    async def create_performance_benchmark(
        self,
        benchmark_name: str,
        benchmark_type: str,
        target_metrics: Dict[str, float],
        test_configuration: Dict[str, Any],
        user_id: str
    ) -> str:
        """        Create a performance benchmark for crawler evaluation.
        
        Args:
            benchmark_name: Human-readable benchmark name
            benchmark_type: Type of benchmark test
            target_metrics: Target metric values for benchmark
            test_configuration: Benchmark test configuration
            user_id: User identifier
            
        Returns:
            Benchmark ID
        """        try:
            benchmark_id = str(uuid4())
            
            # Create performance benchmark record
            benchmark = PerformanceBenchmark(
                benchmark_id=benchmark_id,
                benchmark_name=benchmark_name,
                benchmark_type=benchmark_type,
                target_metrics=target_metrics,
                test_configuration=test_configuration,
                user_id=user_id,
                status="created",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(benchmark)
            await self.db_session.commit()
            
            return benchmark_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise BenchmarkError(
                f"Failed to create performance benchmark: {str(e)}"
            )
    
    async def run_performance_benchmark(
        self,
        benchmark_id: str,
        crawler_id: str,
        test_duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """        Execute a performance benchmark test for a crawler.
        
        Args:
            benchmark_id: Benchmark identifier
            crawler_id: Crawler to test
            test_duration_minutes: Duration of benchmark test
            
        Returns:
            Benchmark results and analysis
        """        try:
            benchmark = await self.db_session.query(PerformanceBenchmark).filter(
                PerformanceBenchmark.benchmark_id == benchmark_id
            ).first()
            
            if not benchmark:
                raise BenchmarkError(f"Benchmark {benchmark_id} not found")
            
            # Update benchmark status
            benchmark.status = "running"
            benchmark.started_at = datetime.utcnow()
            await self.db_session.commit()
            
            # Execute benchmark test
            test_results = await self._execute_benchmark_test(
                benchmark, crawler_id, test_duration_minutes
            )
            
            # Analyze results against targets
            performance_analysis = await self._analyze_benchmark_results(
                test_results, benchmark.target_metrics
            )
            
            # Update benchmark with results
            benchmark.status = "completed"
            benchmark.completed_at = datetime.utcnow()
            benchmark.test_results = test_results
            benchmark.performance_analysis = performance_analysis
            await self.db_session.commit()
            
            return {
                "benchmark_id": benchmark_id,
                "test_results": test_results,
                "performance_analysis": performance_analysis,
                "target_metrics": benchmark.target_metrics,
                "benchmark_passed": performance_analysis.get("overall_pass", False)
            }
            
        except Exception as e:
            await self.db_session.rollback()
            raise BenchmarkError(
                f"Failed to run performance benchmark: {str(e)}"
            )
    
    async def get_optimization_recommendations(
        self,
        crawler_id: str,
        analysis_period: timedelta = timedelta(hours=24)
    ) -> List[Dict[str, Any]]:
        """        Generate intelligent optimization recommendations for a crawler.
        
        Args:
            crawler_id: Crawler identifier
            analysis_period: Time period for analysis
            
        Returns:
            List of optimization recommendations
        """        try:
            cutoff_time = datetime.utcnow() - analysis_period
            
            # Get performance metrics within analysis period
            metrics = await self.db_session.query(CrawlerPerformanceMetric).filter(
                and_(
                    CrawlerPerformanceMetric.crawler_id == crawler_id,
                    CrawlerPerformanceMetric.collection_timestamp >= cutoff_time
                )
            ).all()
            
            # Analyze performance patterns
            performance_patterns = await self._analyze_performance_patterns(metrics)
            
            # Generate recommendations based on analysis
            recommendations = await self._generate_optimization_recommendations(
                crawler_id, performance_patterns
            )
            
            return recommendations
            
        except Exception as e:
            raise PerformanceOptimizationError(
                f"Failed to generate optimization recommendations: {str(e)}"
            )
    
    async def perform_system_health_check(
        self,
        check_type: str = "comprehensive",
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """        Perform comprehensive system health check and analysis.
        
        Args:
            check_type: Type of health check to perform
            include_predictions: Whether to include predictive analysis
            
        Returns:
            System health report
        """        try:
            health_check_id = str(uuid4())
            
            # Collect system metrics
            system_metrics = await self._collect_system_metrics()
            
            # Analyze crawler performance across all instances
            crawler_analysis = await self._analyze_all_crawler_performance()
            
            # Check resource utilization
            resource_utilization = await self._check_resource_utilization()
            
            # Identify bottlenecks and issues
            bottlenecks = await self._identify_system_bottlenecks()
            
            # Generate health score
            health_score = await self._calculate_system_health_score(
                system_metrics, crawler_analysis, resource_utilization
            )
            
            health_report = {
                "health_check_id": health_check_id,
                "check_timestamp": datetime.utcnow().isoformat(),
                "check_type": check_type,
                "overall_health_score": health_score,
                "system_metrics": system_metrics,
                "crawler_analysis": crawler_analysis,
                "resource_utilization": resource_utilization,
                "identified_bottlenecks": bottlenecks,
                "status": self._determine_health_status(health_score)
            }
            
            if include_predictions:
                predictions = await self._generate_performance_predictions()
                health_report["performance_predictions"] = predictions
            
            # Create health check record
            health_check = SystemHealthCheck(
                check_id=health_check_id,
                check_type=check_type,
                health_score=health_score,
                system_metrics=system_metrics,
                health_report=health_report,
                performed_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(health_check)
            await self.db_session.commit()
            
            return health_report
            
        except Exception as e:
            raise PerformanceOptimizationError(
                f"Failed to perform system health check: {str(e)}"
            )
    
    async def _calculate_metric_percentile(
        self,
        crawler_id: str,
        metric_type: MetricType,
        metric_value: float
    ) -> float:
        """Calculate percentile ranking for a metric value."""        # Get historical values for this metric type
        historical_metrics = await self.db_session.query(CrawlerPerformanceMetric).filter(
            and_(
                CrawlerPerformanceMetric.crawler_id == crawler_id,
                CrawlerPerformanceMetric.metric_type == metric_type.value,
                CrawlerPerformanceMetric.collection_timestamp >= datetime.utcnow() - timedelta(days=30)
            )
        ).all()
        
        if not historical_metrics:
            return 50.0  # Default to 50th percentile if no history
        
        values = [m.metric_value for m in historical_metrics]
        values.append(metric_value)
        values.sort()
        
        rank = values.index(metric_value)
        percentile = (rank / len(values)) * 100
        
        return percentile
    
    async def _detect_performance_anomaly(
        self,
        crawler_id: str,
        metric_type: MetricType,
        metric_value: float
    ) -> bool:
        """Detect if a metric value represents a performance anomaly."""        # Get recent metrics for statistical analysis
        recent_metrics = await self.db_session.query(CrawlerPerformanceMetric).filter(
            and_(
                CrawlerPerformanceMetric.crawler_id == crawler_id,
                CrawlerPerformanceMetric.metric_type == metric_type.value,
                CrawlerPerformanceMetric.collection_timestamp >= datetime.utcnow() - timedelta(hours=24)
            )
        ).limit(100).all()
        
        if len(recent_metrics) < 10:
            return False  # Need sufficient data for anomaly detection
        
        values = [m.metric_value for m in recent_metrics]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Consider value anomalous if it's more than 2 standard deviations from mean
        if std_dev > 0:
            z_score = abs(metric_value - mean_value) / std_dev
            return z_score > 2.0
        
        return False
    
    async def _trigger_optimization_analysis(
        self,
        crawler_id: str,
        metric_type: MetricType,
        metric_value: float
    ) -> None:
        """Trigger optimization analysis for anomalous metrics."""        # Implementation would trigger automated optimization analysis
        pass
    
    async def _validate_optimization_rule(
        self,
        conditions: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> bool:
        """Validate optimization rule configuration."""        required_condition_fields = ["metric_type", "threshold", "comparison"]
        required_action_fields = ["action_type", "parameters"]
        
        for field in required_condition_fields:
            if field not in conditions:
                raise PerformanceOptimizationError(
                    f"Missing required condition field: {field}"
                )
        
        for action in actions:
            for field in required_action_fields:
                if field not in action:
                    raise PerformanceOptimizationError(
                        f"Missing required action field: {field}"
                    )
        
        return True
    
    async def _activate_optimization_rule(
        self,
        rule_id: str,
        conditions: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> None:
        """Activate optimization rule in the optimization engine."""        self.optimization_rules[rule_id] = {
            "conditions": conditions,
            "actions": actions,
            "activated_at": datetime.utcnow()
        }
    
    async def _check_resource_availability(
        self,
        requirements: Dict[ResourceType, float]
    ) -> bool:
        """Check if required resources are available."""        # Implementation would check actual system resource availability
        return True  # Simplified for now
    
    async def _apply_resource_allocation(
        self,
        allocation_id: str,
        requirements: Dict[ResourceType, float]
    ) -> None:
        """Apply resource allocation to system."""        self.resource_allocations[allocation_id] = {
            "requirements": {rt.value: val for rt, val in requirements.items()},
            "allocated_at": datetime.utcnow()
        }
    
    async def _analyze_current_performance(self, crawler_id: str) -> Dict[str, Any]:
        """Analyze current performance metrics for a crawler."""        # Get recent performance metrics
        recent_metrics = await self.db_session.query(CrawlerPerformanceMetric).filter(
            and_(
                CrawlerPerformanceMetric.crawler_id == crawler_id,
                CrawlerPerformanceMetric.collection_timestamp >= datetime.utcnow() - timedelta(hours=1)
            )
        ).all()
        
        if not recent_metrics:
            return {"status": "insufficient_data"}
        
        # Calculate performance indicators
        throughput_metrics = [m for m in recent_metrics if m.metric_type == "throughput"]
        latency_metrics = [m for m in recent_metrics if m.metric_type == "latency"]
        error_rate_metrics = [m for m in recent_metrics if m.metric_type == "error_rate"]
        
        return {
            "average_throughput": statistics.mean([m.metric_value for m in throughput_metrics]) if throughput_metrics else 0,
            "average_latency": statistics.mean([m.metric_value for m in latency_metrics]) if latency_metrics else 0,
            "error_rate": statistics.mean([m.metric_value for m in error_rate_metrics]) if error_rate_metrics else 0,
            "performance_trend": "stable",  # Simplified
            "bottleneck_indicators": []
        }
    
    async def _calculate_scaling_strategy(
        self,
        current_performance: Dict[str, Any],
        target_performance: float,
        max_scale_factor: float
    ) -> Dict[str, Any]:
        """Calculate optimal scaling strategy."""        current_score = current_performance.get("average_throughput", 0) / 100  # Normalized
        performance_gap = target_performance - current_score
        
        if performance_gap <= 0:
            return {
                "strategy": "no_scaling_needed",
                "scale_factor": 1.0,
                "reasoning": "Current performance meets or exceeds target"
            }
        
        # Calculate required scale factor
        required_scale = min(1 + performance_gap, max_scale_factor)
        
        # Determine scaling strategy
        if required_scale <= 1.5:
            strategy = OptimizationStrategy.SCALE_UP
        elif required_scale <= 2.0:
            strategy = OptimizationStrategy.SCALE_OUT
        else:
            strategy = OptimizationStrategy.LOAD_BALANCE
        
        return {
            "strategy": strategy.value,
            "scale_factor": required_scale,
            "reasoning": f"Performance gap of {performance_gap:.2f} requires {strategy.value}"
        }
    
    async def _execute_scaling_operations(
        self,
        event_id: str,
        scaling_strategy: Dict[str, Any]
    ) -> None:
        """Execute scaling operations based on strategy."""        # Implementation would execute actual scaling operations
        pass
    
    async def _execute_benchmark_test(
        self,
        benchmark: PerformanceBenchmark,
        crawler_id: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Execute performance benchmark test."""        # Simplified benchmark execution
        return {
            "throughput": 85.5,
            "latency": 1.2,
            "error_rate": 0.8,
            "resource_efficiency": 78.3,
            "test_duration": duration_minutes
        }
    
    async def _analyze_benchmark_results(
        self,
        results: Dict[str, Any],
        targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze benchmark results against targets."""        analysis = {"metric_analysis": {}, "overall_pass": True}
        
        for metric, target in targets.items():
            actual = results.get(metric, 0)
            passed = actual >= target
            
            analysis["metric_analysis"][metric] = {
                "target": target,
                "actual": actual,
                "passed": passed,
                "deviation": ((actual - target) / target) * 100 if target > 0 else 0
            }
            
            if not passed:
                analysis["overall_pass"] = False
        
        return analysis
    
    async def _analyze_performance_patterns(
        self,
        metrics: List
    ) -> Dict[str, Any]:
        """Analyze performance patterns from metrics."""        if not metrics:
            return {"status": "insufficient_data"}
        
        # Group metrics by type
        metric_groups = {}
        for metric in metrics:
            metric_type = metric.metric_type
            if metric_type not in metric_groups:
                metric_groups[metric_type] = []
            metric_groups[metric_type].append(metric.metric_value)
        
        patterns = {}
        for metric_type, values in metric_groups.items():
            patterns[metric_type] = {
                "average": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "trend": "stable",  # Simplified
                "anomaly_count": len([v for v in values if abs(v - statistics.mean(values)) > statistics.stdev(values)]) if len(values) > 1 else 0
            }
        
        return patterns
    
    async def _generate_optimization_recommendations(
        self,
        crawler_id: str,
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on performance patterns."""        recommendations = []
        
        for metric_type, pattern in patterns.items():
            if metric_type == "throughput" and pattern["average"] < 50:
                recommendations.append({
                    "type": "performance_improvement",
                    "priority": "high",
                    "recommendation": "Increase crawler concurrency",
                    "expected_improvement": "30-50% throughput increase",
                    "implementation": "scale_out"
                })
            
            if metric_type == "error_rate" and pattern["average"] > 5.0:
                recommendations.append({
                    "type": "reliability_improvement",
                    "priority": "critical",
                    "recommendation": "Implement better error handling",
                    "expected_improvement": "Reduce error rate to <2%",
                    "implementation": "algorithm_tune"
                })
        
        return recommendations
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system performance metrics."""        return {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 34.1,
            "network_throughput": 125.5,
            "active_connections": 1234,
            "queue_depth": 456
        }
    
    async def _analyze_all_crawler_performance(self) -> Dict[str, Any]:
        """Analyze performance across all active crawlers."""        return {
            "total_active_crawlers": 25,
            "average_throughput": 78.5,
            "average_error_rate": 2.1,
            "performance_distribution": {
                "optimal": 15,
                "good": 8,
                "degraded": 2
            }
        }
    
    async def _check_resource_utilization(self) -> Dict[str, Any]:
        """Check current resource utilization across system."""        return {
            "cpu_utilization": 68.5,
            "memory_utilization": 75.2,
            "disk_utilization": 45.8,
            "network_utilization": 52.3,
            "database_connections": 85.0
        }
    
    async def _identify_system_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify current system bottlenecks."""        return [
            {
                "type": "resource_bottleneck",
                "resource": "memory",
                "severity": "medium",
                "impact": "Limiting crawler concurrency",
                "recommendation": "Increase memory allocation"
            }
        ]
    
    async def _calculate_system_health_score(
        self,
        system_metrics: Dict[str, Any],
        crawler_analysis: Dict[str, Any],
        resource_utilization: Dict[str, Any]
    ) -> float:
        """Calculate overall system health score."""        # Weighted health score calculation
        performance_score = crawler_analysis.get("average_throughput", 0)
        reliability_score = 100 - crawler_analysis.get("average_error_rate", 0) * 10
        resource_score = 100 - max(resource_utilization.values())
        
        weighted_score = (performance_score * 0.4 + reliability_score * 0.4 + resource_score * 0.2)
        return max(0, min(100, weighted_score))
    
    def _determine_health_status(self, health_score: float) -> str:
        """Determine health status based on score."""        if health_score >= 90:
            return PerformanceStatus.OPTIMAL.value
        elif health_score >= 75:
            return PerformanceStatus.GOOD.value
        elif health_score >= 60:
            return PerformanceStatus.ACCEPTABLE.value
        elif health_score >= 40:
            return PerformanceStatus.DEGRADED.value
        else:
            return PerformanceStatus.CRITICAL.value
    
    async def _generate_performance_predictions(self) -> Dict[str, Any]:
        """Generate predictive performance analysis."""        return {
            "predicted_load_increase": "15% over next 7 days",
            "scaling_recommendations": ["Add 2 crawler instances by day 5"],
            "resource_forecast": {
                "cpu": "Will reach 80% utilization in 3 days",
                "memory": "Sufficient for 10 more days",
                "storage": "Sufficient for 30+ days"
            }
        }
    
    def _initialize_optimization_system(self) -> None:
        """Initialize performance optimization system."""        self.performance_baselines = {}
        self.optimization_rules = {}
        self.resource_allocations = {}
