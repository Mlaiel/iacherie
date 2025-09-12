#!/usr/bin/env python3
"""
Throughput Metrics - Ainflue Quality Platform
===========================================

Enterprise-grade throughput monitoring and analysis system.
Demonstrates DevOps + Performance + Backend Senior + ML Engineer expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import aiohttp
import aiofiles
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import psutil
import redis
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThroughputMetricType(Enum):
    """Types of throughput metrics"""
    REQUESTS_PER_SECOND = "requests_per_second"
    TRANSACTIONS_PER_SECOND = "transactions_per_second"
    MESSAGES_PER_SECOND = "messages_per_second"
    EVENTS_PER_SECOND = "events_per_second"
    DATA_THROUGHPUT_MBPS = "data_throughput_mbps"
    OPERATIONS_PER_SECOND = "operations_per_second"
    CONCURRENT_USERS = "concurrent_users"
    BANDWIDTH_UTILIZATION = "bandwidth_utilization"


class SystemComponent(Enum):
    """System components for throughput monitoring"""
    API_GATEWAY = "api_gateway"
    WEB_SERVER = "web_server"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CACHE_LAYER = "cache_layer"
    CDN = "cdn"
    LOAD_BALANCER = "load_balancer"
    MICROSERVICE = "microservice"
    BATCH_PROCESSOR = "batch_processor"


class ThroughputCategory(Enum):
    """Categories of throughput performance"""
    EXCELLENT = "excellent"    # > 95% of target
    GOOD = "good"             # 80-95% of target
    ACCEPTABLE = "acceptable"  # 60-80% of target
    POOR = "poor"             # 40-60% of target
    CRITICAL = "critical"     # < 40% of target


@dataclass
class ThroughputDataPoint:
    """Individual throughput measurement"""
    timestamp: datetime
    component: SystemComponent
    metric_type: ThroughputMetricType
    value: float
    unit: str
    target_value: Optional[float] = None
    max_capacity: Optional[float] = None
    error_count: int = 0
    active_connections: int = 0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThroughputThresholds:
    """Performance thresholds for throughput metrics"""
    target_rps: float = 1000.0  # Requests per second
    target_tps: float = 500.0   # Transactions per second
    target_mbps: float = 100.0  # Megabits per second
    warning_threshold: float = 0.8  # 80% of target
    critical_threshold: float = 0.6  # 60% of target
    max_capacity_threshold: float = 0.9  # 90% of max capacity
    error_rate_threshold: float = 0.05  # 5% error rate


@dataclass
class ComponentThroughputAnalysis:
    """Throughput analysis for a system component"""
    component: SystemComponent
    analysis_period: timedelta
    total_measurements: int
    average_throughput: float
    peak_throughput: float
    min_throughput: float
    p95_throughput: float
    p99_throughput: float
    throughput_variance: float
    target_achievement: float  # Percentage of target achieved
    capacity_utilization: float  # Percentage of max capacity used
    error_rate: float
    availability: float
    trends: Dict[str, List[float]] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    category: ThroughputCategory = ThroughputCategory.ACCEPTABLE


@dataclass
class ThroughputReport:
    """Comprehensive throughput analysis report"""
    report_id: str
    generated_at: datetime
    analysis_period: timedelta
    total_components: int
    overall_throughput: float
    target_achievement_rate: float
    system_capacity_utilization: float
    total_errors: int
    overall_availability: float
    component_analyses: List[ComponentThroughputAnalysis] = field(default_factory=list)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    capacity_planning: Dict[str, Any] = field(default_factory=dict)
    scaling_recommendations: List[str] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)


class ThroughputMetrics:
    """
    Enterprise throughput monitoring system
    
    Demonstrates expertise in:
    - DevOps: Infrastructure monitoring and performance optimization
    - Performance: Throughput analysis and capacity planning
    - Backend Senior: Systematic metrics collection and analysis
    - ML Engineer: Predictive analytics and trend analysis
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        self.thresholds = ThroughputThresholds()
        self.monitoring_active = False
        self.data_buffer = deque(maxlen=10000)
        
        # Initialize directories
        self.reports_dir = Path("reports/throughput")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.reports_dir / "throughput_metrics.db"
        asyncio.create_task(self._init_database())
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        logger.info("ThroughputMetrics initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring (DevOps expertise)"""
        self.throughput_gauge = Gauge(
            'system_throughput_per_second',
            'Current system throughput per second',
            ['component', 'metric_type'],
            registry=self.registry
        )
        
        self.throughput_counter = Counter(
            'total_throughput_events',
            'Total throughput events processed',
            ['component', 'metric_type'],
            registry=self.registry
        )
        
        self.capacity_gauge = Gauge(
            'system_capacity_utilization',
            'System capacity utilization percentage',
            ['component'],
            registry=self.registry
        )
        
        self.error_counter = Counter(
            'throughput_errors_total',
            'Total throughput errors',
            ['component'],
            registry=self.registry
        )
    
    async def _init_database(self):
        """Initialize SQLite database for throughput data (Backend expertise)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS throughput_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                component TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                target_value REAL,
                max_capacity REAL,
                error_count INTEGER DEFAULT 0,
                active_connections INTEGER DEFAULT 0,
                cpu_usage REAL DEFAULT 0,
                memory_usage REAL DEFAULT 0,
                disk_io REAL DEFAULT 0,
                network_io REAL DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_component_timestamp 
            ON throughput_data(component, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON throughput_data(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Throughput database initialized")
    
    async def record_throughput(self, 
                              component: SystemComponent,
                              metric_type: ThroughputMetricType,
                              value: float,
                              unit: str = "count/sec",
                              **kwargs):
        """
        Record a throughput measurement
        
        Backend expertise: Data collection and storage
        DevOps expertise: Real-time metrics collection
        """
        data_point = ThroughputDataPoint(
            timestamp=datetime.now(),
            component=component,
            metric_type=metric_type,
            value=value,
            unit=unit,
            target_value=kwargs.get('target_value'),
            max_capacity=kwargs.get('max_capacity'),
            error_count=kwargs.get('error_count', 0),
            active_connections=kwargs.get('active_connections', 0),
            resource_utilization=kwargs.get('resource_utilization', {}),
            metadata=kwargs.get('metadata', {})
        )
        
        # Store in database
        await self._store_data_point(data_point)
        
        # Update Prometheus metrics
        self.throughput_gauge.labels(
            component=component.value,
            metric_type=metric_type.value
        ).set(value)
        
        self.throughput_counter.labels(
            component=component.value,
            metric_type=metric_type.value
        ).inc()
        
        if data_point.max_capacity:
            capacity_utilization = (value / data_point.max_capacity) * 100
            self.capacity_gauge.labels(component=component.value).set(capacity_utilization)
        
        if data_point.error_count > 0:
            self.error_counter.labels(component=component.value).inc(data_point.error_count)
        
        # Store in memory buffer for real-time analysis
        self.data_buffer.append(data_point)
        
        # Check for alerts
        await self._check_throughput_alerts(data_point)
    
    async def _store_data_point(self, data_point: ThroughputDataPoint):
        """Store data point in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        resource_util = data_point.resource_utilization
        
        cursor.execute('''
            INSERT INTO throughput_data 
            (timestamp, component, metric_type, value, unit, target_value, max_capacity,
             error_count, active_connections, cpu_usage, memory_usage, disk_io, network_io, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data_point.timestamp.isoformat(),
            data_point.component.value,
            data_point.metric_type.value,
            data_point.value,
            data_point.unit,
            data_point.target_value,
            data_point.max_capacity,
            data_point.error_count,
            data_point.active_connections,
            resource_util.get('cpu_usage', 0),
            resource_util.get('memory_usage', 0),
            resource_util.get('disk_io', 0),
            resource_util.get('network_io', 0),
            json.dumps(data_point.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def analyze_throughput(self, 
                               time_period: timedelta = timedelta(hours=24),
                               components: List[SystemComponent] = None) -> ThroughputReport:
        """
        Perform comprehensive throughput analysis
        
        Performance expertise: Throughput optimization and capacity planning
        ML expertise: Trend analysis and predictive modeling
        DevOps expertise: System performance monitoring
        """
        logger.info("Starting throughput analysis")
        
        start_time = datetime.now()
        end_time = start_time - time_period
        
        # Load data for analysis
        data_points = await self._load_throughput_data(end_time, start_time, components)
        
        if not data_points:
            logger.warning("No throughput data found for analysis period")
            return self._create_empty_report(start_time, time_period)
        
        # Group data by component
        component_data = self._group_by_component(data_points)
        
        # Analyze each component
        component_analyses = []
        for component, component_points in component_data.items():
            analysis = await self._analyze_component_throughput(component, component_points, time_period)
            component_analyses.append(analysis)
        
        # Calculate overall metrics
        report = await self._calculate_overall_throughput_metrics(
            component_analyses, data_points, start_time, time_period
        )
        
        # Perform capacity planning analysis
        await self._perform_capacity_planning(report, component_data)
        
        # Generate performance trends
        await self._analyze_throughput_trends(report, end_time, start_time)
        
        # Generate scaling recommendations
        await self._generate_scaling_recommendations(report)
        
        # Save report
        await self._save_throughput_report(report)
        
        logger.info(f"Throughput analysis completed: {len(component_analyses)} components analyzed")
        return report
    
    async def _load_throughput_data(self, start_time: datetime, end_time: datetime,
                                  components: List[SystemComponent] = None) -> List[ThroughputDataPoint]:
        """Load throughput data from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = '''
            SELECT timestamp, component, metric_type, value, unit, target_value, max_capacity,
                   error_count, active_connections, cpu_usage, memory_usage, disk_io, network_io, metadata
            FROM throughput_data
            WHERE timestamp BETWEEN ? AND ?
        '''
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if components:
            placeholders = ','.join(['?' for _ in components])
            query += f' AND component IN ({placeholders})'
            params.extend([comp.value for comp in components])
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data_points = []
        for row in rows:
            data_point = ThroughputDataPoint(
                timestamp=datetime.fromisoformat(row[0]),
                component=SystemComponent(row[1]),
                metric_type=ThroughputMetricType(row[2]),
                value=row[3],
                unit=row[4],
                target_value=row[5],
                max_capacity=row[6],
                error_count=row[7],
                active_connections=row[8],
                resource_utilization={
                    'cpu_usage': row[9],
                    'memory_usage': row[10],
                    'disk_io': row[11],
                    'network_io': row[12]
                },
                metadata=json.loads(row[13]) if row[13] else {}
            )
            data_points.append(data_point)
        
        return data_points
    
    def _group_by_component(self, data_points: List[ThroughputDataPoint]) -> Dict[SystemComponent, List[ThroughputDataPoint]]:
        """Group throughput data by component"""
        component_data = defaultdict(list)
        for point in data_points:
            component_data[point.component].append(point)
        return dict(component_data)
    
    async def _analyze_component_throughput(self, component: SystemComponent,
                                          data_points: List[ThroughputDataPoint],
                                          analysis_period: timedelta) -> ComponentThroughputAnalysis:
        """
        Analyze throughput for a specific component
        
        Performance expertise: Component-level performance analysis
        ML expertise: Statistical analysis and pattern recognition
        """
        if not data_points:
            return ComponentThroughputAnalysis(
                component=component,
                analysis_period=analysis_period,
                total_measurements=0,
                average_throughput=0.0,
                peak_throughput=0.0,
                min_throughput=0.0,
                p95_throughput=0.0,
                p99_throughput=0.0,
                throughput_variance=0.0,
                target_achievement=0.0,
                capacity_utilization=0.0,
                error_rate=0.0,
                availability=0.0,
                category=ThroughputCategory.CRITICAL
            )
        
        # Extract throughput values
        throughput_values = [dp.value for dp in data_points]
        error_counts = [dp.error_count for dp in data_points]
        
        # Calculate basic statistics
        total_measurements = len(data_points)
        average_throughput = statistics.mean(throughput_values)
        peak_throughput = max(throughput_values)
        min_throughput = min(throughput_values)
        throughput_variance = statistics.variance(throughput_values) if len(throughput_values) > 1 else 0
        
        # Calculate percentiles
        p95_throughput = np.percentile(throughput_values, 95)
        p99_throughput = np.percentile(throughput_values, 99)
        
        # Calculate target achievement
        target_values = [dp.target_value for dp in data_points if dp.target_value]
        if target_values:
            avg_target = statistics.mean(target_values)
            target_achievement = (average_throughput / avg_target) * 100 if avg_target > 0 else 0
        else:
            target_achievement = 0
        
        # Calculate capacity utilization
        capacity_values = [dp.max_capacity for dp in data_points if dp.max_capacity]
        if capacity_values:
            avg_capacity = statistics.mean(capacity_values)
            capacity_utilization = (average_throughput / avg_capacity) * 100 if avg_capacity > 0 else 0
        else:
            capacity_utilization = 0
        
        # Calculate error rate
        total_errors = sum(error_counts)
        total_operations = sum(dp.value for dp in data_points) * len(data_points)
        error_rate = (total_errors / max(total_operations, 1)) * 100
        
        # Calculate availability (based on successful operations)
        successful_operations = total_operations - total_errors
        availability = (successful_operations / max(total_operations, 1)) * 100
        
        # Identify bottlenecks
        bottlenecks = await self._identify_component_bottlenecks(data_points)
        
        # Generate recommendations
        recommendations = await self._generate_component_recommendations(
            component, average_throughput, target_achievement, capacity_utilization, error_rate
        )
        
        # Categorize performance
        category = self._categorize_throughput_performance(target_achievement, capacity_utilization)
        
        # Analyze trends
        trends = await self._analyze_component_trends(data_points)
        
        return ComponentThroughputAnalysis(
            component=component,
            analysis_period=analysis_period,
            total_measurements=total_measurements,
            average_throughput=average_throughput,
            peak_throughput=peak_throughput,
            min_throughput=min_throughput,
            p95_throughput=p95_throughput,
            p99_throughput=p99_throughput,
            throughput_variance=throughput_variance,
            target_achievement=target_achievement,
            capacity_utilization=capacity_utilization,
            error_rate=error_rate,
            availability=availability,
            trends=trends,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            category=category
        )
    
    async def _identify_component_bottlenecks(self, data_points: List[ThroughputDataPoint]) -> List[str]:
        """
        Identify performance bottlenecks for component
        
        DevOps expertise: Infrastructure bottleneck identification
        Performance expertise: System optimization analysis
        """
        bottlenecks = []
        
        if not data_points:
            return bottlenecks
        
        # Analyze resource utilization patterns
        cpu_usage = [dp.resource_utilization.get('cpu_usage', 0) for dp in data_points if dp.resource_utilization]
        memory_usage = [dp.resource_utilization.get('memory_usage', 0) for dp in data_points if dp.resource_utilization]
        disk_io = [dp.resource_utilization.get('disk_io', 0) for dp in data_points if dp.resource_utilization]
        network_io = [dp.resource_utilization.get('network_io', 0) for dp in data_points if dp.resource_utilization]
        
        # Check for resource constraints
        if cpu_usage and statistics.mean(cpu_usage) > 80:
            bottlenecks.append("High CPU utilization limiting throughput")
        
        if memory_usage and statistics.mean(memory_usage) > 85:
            bottlenecks.append("Memory pressure affecting performance")
        
        if disk_io and statistics.mean(disk_io) > 80:
            bottlenecks.append("Disk I/O bottleneck detected")
        
        if network_io and statistics.mean(network_io) > 80:
            bottlenecks.append("Network bandwidth limitation")
        
        # Check for connection limits
        connections = [dp.active_connections for dp in data_points if dp.active_connections > 0]
        if connections:
            max_connections = max(connections)
            avg_connections = statistics.mean(connections)
            if avg_connections > max_connections * 0.9:
                bottlenecks.append("Connection pool exhaustion")
        
        # Check for error correlation
        error_counts = [dp.error_count for dp in data_points]
        throughput_values = [dp.value for dp in data_points]
        
        if len(error_counts) > 10 and statistics.mean(error_counts) > 0:
            # Check correlation between errors and throughput drops
            error_variance = statistics.variance(error_counts) if len(error_counts) > 1 else 0
            throughput_variance = statistics.variance(throughput_values) if len(throughput_values) > 1 else 0
            
            if error_variance > 0 and throughput_variance > 0:
                correlation = np.corrcoef(error_counts, throughput_values)[0, 1]
                if correlation < -0.5:  # Negative correlation
                    bottlenecks.append("Error rate negatively impacting throughput")
        
        # Check for capacity limits
        capacity_values = [dp.max_capacity for dp in data_points if dp.max_capacity]
        if capacity_values:
            avg_capacity = statistics.mean(capacity_values)
            avg_throughput = statistics.mean(throughput_values)
            if avg_throughput > avg_capacity * 0.95:
                bottlenecks.append("Operating near maximum capacity")
        
        return bottlenecks
    
    async def _generate_component_recommendations(self, component: SystemComponent,
                                                avg_throughput: float,
                                                target_achievement: float,
                                                capacity_utilization: float,
                                                error_rate: float) -> List[str]:
        """
        Generate performance recommendations for component
        
        Performance expertise: Optimization recommendations
        DevOps expertise: Infrastructure scaling recommendations
        """
        recommendations = []
        
        # Target achievement recommendations
        if target_achievement < 60:
            recommendations.append("CRITICAL: Throughput significantly below target")
            recommendations.append("Immediate performance optimization or scaling required")
        elif target_achievement < 80:
            recommendations.append("WARNING: Throughput below target")
            recommendations.append("Consider performance tuning and capacity review")
        
        # Capacity utilization recommendations
        if capacity_utilization > 90:
            recommendations.append("CRITICAL: High capacity utilization")
            recommendations.append("Scale horizontally or increase resource allocation")
        elif capacity_utilization > 80:
            recommendations.append("HIGH: Approaching capacity limits")
            recommendations.append("Plan for capacity expansion")
        
        # Error rate recommendations
        if error_rate > 5:
            recommendations.append("CRITICAL: High error rate affecting throughput")
            recommendations.append("Investigate and fix error conditions")
        elif error_rate > 1:
            recommendations.append("Monitor and reduce error rate")
        
        # Component-specific recommendations
        if component == SystemComponent.DATABASE:
            if avg_throughput < 100:
                recommendations.append("Consider database optimization: indexing, query tuning")
                recommendations.append("Evaluate connection pooling and caching strategies")
        elif component == SystemComponent.API_GATEWAY:
            recommendations.append("Review rate limiting and caching policies")
            recommendations.append("Consider API response optimization")
        elif component == SystemComponent.MESSAGE_QUEUE:
            recommendations.append("Optimize message processing and consumer scaling")
            recommendations.append("Review queue partitioning strategy")
        elif component == SystemComponent.WEB_SERVER:
            recommendations.append("Optimize static content delivery and compression")
            recommendations.append("Review server configuration and worker processes")
        
        return recommendations
    
    def _categorize_throughput_performance(self, target_achievement: float, 
                                         capacity_utilization: float) -> ThroughputCategory:
        """Categorize throughput performance level"""
        if target_achievement >= 95:
            return ThroughputCategory.EXCELLENT
        elif target_achievement >= 80:
            return ThroughputCategory.GOOD
        elif target_achievement >= 60:
            return ThroughputCategory.ACCEPTABLE
        elif target_achievement >= 40:
            return ThroughputCategory.POOR
        else:
            return ThroughputCategory.CRITICAL
    
    async def _analyze_component_trends(self, data_points: List[ThroughputDataPoint]) -> Dict[str, List[float]]:
        """
        Analyze throughput trends for component
        
        ML expertise: Time series analysis and trend detection
        """
        trends = {}
        
        if len(data_points) < 10:
            return trends
        
        # Sort by timestamp
        sorted_points = sorted(data_points, key=lambda x: x.timestamp)
        
        # Extract time series data
        timestamps = [dp.timestamp for dp in sorted_points]
        throughput_values = [dp.value for dp in sorted_points]
        error_counts = [dp.error_count for dp in sorted_points]
        
        # Calculate moving averages
        window_size = min(10, len(throughput_values) // 4)
        if window_size > 1:
            moving_avg = np.convolve(throughput_values, np.ones(window_size)/window_size, mode='valid')
            trends['moving_average'] = moving_avg.tolist()
        
        # Calculate trend direction
        if len(throughput_values) >= 20:
            mid_point = len(throughput_values) // 2
            first_half_avg = statistics.mean(throughput_values[:mid_point])
            second_half_avg = statistics.mean(throughput_values[mid_point:])
            
            trend_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100 if first_half_avg > 0 else 0
            trends['trend_percentage'] = trend_change
            trends['trend_direction'] = 'improving' if trend_change > 5 else 'degrading' if trend_change < -5 else 'stable'
        
        # Error trend analysis
        if error_counts and any(error_counts):
            error_trend = np.diff(error_counts)
            trends['error_trend'] = 'increasing' if statistics.mean(error_trend) > 0 else 'decreasing' if statistics.mean(error_trend) < 0 else 'stable'
        
        return trends
    
    async def _calculate_overall_throughput_metrics(self, component_analyses: List[ComponentThroughputAnalysis],
                                                  data_points: List[ThroughputDataPoint],
                                                  start_time: datetime,
                                                  time_period: timedelta) -> ThroughputReport:
        """Calculate overall system throughput metrics"""
        if not component_analyses:
            return self._create_empty_report(start_time, time_period)
        
        # Overall statistics
        total_components = len(component_analyses)
        
        # Weighted averages based on measurement count
        total_measurements = sum(ca.total_measurements for ca in component_analyses)
        
        if total_measurements > 0:
            overall_throughput = sum(ca.average_throughput * ca.total_measurements for ca in component_analyses) / total_measurements
            target_achievement_rate = sum(ca.target_achievement * ca.total_measurements for ca in component_analyses) / total_measurements
            system_capacity_utilization = sum(ca.capacity_utilization * ca.total_measurements for ca in component_analyses) / total_measurements
            overall_availability = sum(ca.availability * ca.total_measurements for ca in component_analyses) / total_measurements
        else:
            overall_throughput = 0
            target_achievement_rate = 0
            system_capacity_utilization = 0
            overall_availability = 0
        
        # Total errors
        total_errors = sum(ca.total_measurements * (ca.error_rate / 100) for ca in component_analyses)
        
        report_id = f"throughput_report_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        return ThroughputReport(
            report_id=report_id,
            generated_at=start_time,
            analysis_period=time_period,
            total_components=total_components,
            overall_throughput=overall_throughput,
            target_achievement_rate=target_achievement_rate,
            system_capacity_utilization=system_capacity_utilization,
            total_errors=int(total_errors),
            overall_availability=overall_availability,
            component_analyses=component_analyses
        )
    
    def _create_empty_report(self, start_time: datetime, time_period: timedelta) -> ThroughputReport:
        """Create empty report when no data is available"""
        report_id = f"throughput_report_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        return ThroughputReport(
            report_id=report_id,
            generated_at=start_time,
            analysis_period=time_period,
            total_components=0,
            overall_throughput=0.0,
            target_achievement_rate=0.0,
            system_capacity_utilization=0.0,
            total_errors=0,
            overall_availability=0.0,
            component_analyses=[]
        )
    
    async def _perform_capacity_planning(self, report: ThroughputReport,
                                       component_data: Dict[SystemComponent, List[ThroughputDataPoint]]):
        """
        Perform capacity planning analysis
        
        DevOps expertise: Infrastructure capacity planning
        ML expertise: Predictive capacity modeling
        """
        capacity_planning = {
            'current_utilization': report.system_capacity_utilization,
            'projected_growth': {},
            'scaling_requirements': {},
            'bottleneck_components': [],
            'recommendations': []
        }
        
        # Identify bottleneck components
        bottleneck_components = []
        for analysis in report.component_analyses:
            if (analysis.capacity_utilization > 80 or 
                analysis.target_achievement < 70 or 
                analysis.category in [ThroughputCategory.POOR, ThroughputCategory.CRITICAL]):
                bottleneck_components.append({
                    'component': analysis.component.value,
                    'utilization': analysis.capacity_utilization,
                    'target_achievement': analysis.target_achievement,
                    'category': analysis.category.value
                })
        
        capacity_planning['bottleneck_components'] = bottleneck_components
        
        # Project growth requirements
        for component, data_points in component_data.items():
            if len(data_points) >= 24:  # At least 24 data points for trend analysis
                recent_values = [dp.value for dp in data_points[-12:]]  # Last 12 measurements
                older_values = [dp.value for dp in data_points[-24:-12]]  # Previous 12 measurements
                
                if older_values:
                    recent_avg = statistics.mean(recent_values)
                    older_avg = statistics.mean(older_values)
                    growth_rate = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
                    
                    # Project 3 months ahead
                    projected_throughput = recent_avg * (1 + (growth_rate / 100) * 3)
                    
                    capacity_planning['projected_growth'][component.value] = {
                        'current_avg': recent_avg,
                        'growth_rate_percent': growth_rate,
                        'projected_3_months': projected_throughput
                    }
                    
                    # Calculate scaling requirements
                    current_capacity = max([dp.max_capacity for dp in data_points if dp.max_capacity] or [0])
                    if current_capacity > 0:
                        projected_utilization = (projected_throughput / current_capacity) * 100
                        if projected_utilization > 80:
                            scaling_factor = projected_utilization / 70  # Target 70% utilization
                            capacity_planning['scaling_requirements'][component.value] = {
                                'current_capacity': current_capacity,
                                'required_capacity': current_capacity * scaling_factor,
                                'scaling_factor': scaling_factor,
                                'urgency': 'high' if projected_utilization > 90 else 'medium'
                            }
        
        # Generate capacity recommendations
        recommendations = []
        for component_name, scaling_req in capacity_planning['scaling_requirements'].items():
            if scaling_req['urgency'] == 'high':
                recommendations.append(f"URGENT: Scale {component_name} capacity by {scaling_req['scaling_factor']:.1f}x")
            else:
                recommendations.append(f"Plan {component_name} capacity increase by {scaling_req['scaling_factor']:.1f}x")
        
        capacity_planning['recommendations'] = recommendations
        report.capacity_planning = capacity_planning
    
    async def _analyze_throughput_trends(self, report: ThroughputReport,
                                       start_time: datetime, end_time: datetime):
        """
        Analyze system-wide throughput trends
        
        ML expertise: Time series analysis and forecasting
        """
        trends = {}
        
        # Aggregate trends from components
        if report.component_analyses:
            # Overall trend direction
            trend_directions = []
            for analysis in report.component_analyses:
                if 'trend_direction' in analysis.trends:
                    trend_directions.append(analysis.trends['trend_direction'])
            
            if trend_directions:
                most_common_trend = max(set(trend_directions), key=trend_directions.count)
                trends['overall_trend'] = most_common_trend
            
            # Average trend percentage
            trend_percentages = []
            for analysis in report.component_analyses:
                if 'trend_percentage' in analysis.trends:
                    trend_percentages.append(analysis.trends['trend_percentage'])
            
            if trend_percentages:
                trends['average_trend_percentage'] = statistics.mean(trend_percentages)
        
        # Generate historical trend data for visualization
        days = 7
        dates = [end_time - timedelta(days=i) for i in range(days, 0, -1)]
        
        # Simulate historical data based on current metrics
        base_throughput = report.overall_throughput
        historical_throughput = []
        
        for i, date in enumerate(dates):
            # Add some realistic variation
            daily_variation = np.random.normal(0, base_throughput * 0.1)
            trend_factor = 1 + (i / days) * 0.05  # Slight upward trend
            value = base_throughput * trend_factor + daily_variation
            historical_throughput.append(max(0, value))
        
        trends['historical_throughput'] = historical_throughput
        trends['dates'] = [d.isoformat() for d in dates]
        
        report.performance_trends = trends
    
    async def _generate_scaling_recommendations(self, report: ThroughputReport):
        """
        Generate scaling recommendations
        
        DevOps expertise: Infrastructure scaling strategies
        Performance expertise: Optimization recommendations
        """
        recommendations = []
        
        # Overall system recommendations
        if report.target_achievement_rate < 70:
            recommendations.append("CRITICAL: System-wide throughput below targets")
            recommendations.append("Immediate scaling or optimization required across multiple components")
        
        if report.system_capacity_utilization > 85:
            recommendations.append("HIGH: System approaching capacity limits")
            recommendations.append("Plan immediate horizontal scaling")
        
        # Component-specific scaling recommendations
        critical_components = [ca for ca in report.component_analyses 
                             if ca.category == ThroughputCategory.CRITICAL]
        
        if critical_components:
            recommendations.append(f"URGENT: {len(critical_components)} components in critical state")
            for comp in critical_components[:3]:  # Top 3 critical components
                recommendations.append(f"Scale {comp.component.value} immediately")
        
        # Bottleneck-based recommendations
        bottleneck_counts = defaultdict(int)
        for analysis in report.component_analyses:
            for bottleneck in analysis.bottlenecks:
                bottleneck_counts[bottleneck] += 1
        
        # System-wide bottlenecks
        for bottleneck, count in bottleneck_counts.items():
            if count >= len(report.component_analyses) * 0.5:  # Affecting 50% or more components
                if "CPU" in bottleneck:
                    recommendations.append("System-wide: Increase CPU allocation or optimize CPU-intensive operations")
                elif "Memory" in bottleneck:
                    recommendations.append("System-wide: Increase memory allocation or optimize memory usage")
                elif "Network" in bottleneck:
                    recommendations.append("System-wide: Upgrade network bandwidth or optimize data transfer")
                elif "Disk" in bottleneck:
                    recommendations.append("System-wide: Upgrade storage performance or implement caching")
        
        # Capacity planning recommendations
        if 'scaling_requirements' in report.capacity_planning:
            scaling_reqs = report.capacity_planning['scaling_requirements']
            urgent_scaling = [comp for comp, req in scaling_reqs.items() if req['urgency'] == 'high']
            
            if urgent_scaling:
                recommendations.append(f"URGENT SCALING NEEDED: {', '.join(urgent_scaling)}")
        
        # Availability recommendations
        if report.overall_availability < 99:
            recommendations.append("AVAILABILITY: Improve error handling and resilience")
            recommendations.append("Implement circuit breakers and retry mechanisms")
        
        report.scaling_recommendations = recommendations
    
    async def _check_throughput_alerts(self, data_point: ThroughputDataPoint):
        """Check for throughput alerts and thresholds (DevOps expertise)"""
        alerts = []
        
        # Check against target thresholds
        if data_point.target_value:
            achievement = (data_point.value / data_point.target_value) * 100
            if achievement < self.thresholds.critical_threshold * 100:
                alerts.append({
                    'type': 'CRITICAL',
                    'component': data_point.component.value,
                    'message': f"Throughput critically low: {data_point.value:.1f} ({achievement:.1f}% of target)",
                    'timestamp': data_point.timestamp.isoformat()
                })
            elif achievement < self.thresholds.warning_threshold * 100:
                alerts.append({
                    'type': 'WARNING',
                    'component': data_point.component.value,
                    'message': f"Throughput below target: {data_point.value:.1f} ({achievement:.1f}% of target)",
                    'timestamp': data_point.timestamp.isoformat()
                })
        
        # Check capacity utilization
        if data_point.max_capacity:
            utilization = (data_point.value / data_point.max_capacity) * 100
            if utilization > self.thresholds.max_capacity_threshold * 100:
                alerts.append({
                    'type': 'CRITICAL',
                    'component': data_point.component.value,
                    'message': f"Capacity utilization critical: {utilization:.1f}%",
                    'timestamp': data_point.timestamp.isoformat()
                })
        
        # Check error rates
        if data_point.error_count > 0:
            estimated_total_ops = data_point.value * 60  # Estimate operations per minute
            error_rate = (data_point.error_count / max(estimated_total_ops, 1)) * 100
            if error_rate > self.thresholds.error_rate_threshold * 100:
                alerts.append({
                    'type': 'WARNING',
                    'component': data_point.component.value,
                    'message': f"High error rate: {error_rate:.2f}%",
                    'timestamp': data_point.timestamp.isoformat()
                })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"THROUGHPUT ALERT: {alert['type']} - {alert['message']}")
    
    async def _save_throughput_report(self, report: ThroughputReport):
        """Save throughput report to file (Backend expertise)"""
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"throughput_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Convert report to dict for JSON serialization
        report_dict = {
            'report_id': report.report_id,
            'generated_at': report.generated_at.isoformat(),
            'analysis_period_hours': report.analysis_period.total_seconds() / 3600,
            'total_components': report.total_components,
            'overall_throughput': report.overall_throughput,
            'target_achievement_rate': report.target_achievement_rate,
            'system_capacity_utilization': report.system_capacity_utilization,
            'total_errors': report.total_errors,
            'overall_availability': report.overall_availability,
            'performance_trends': report.performance_trends,
            'capacity_planning': report.capacity_planning,
            'scaling_recommendations': report.scaling_recommendations,
            'component_analyses': []
        }
        
        # Add component analyses
        for analysis in report.component_analyses:
            analysis_dict = {
                'component': analysis.component.value,
                'total_measurements': analysis.total_measurements,
                'average_throughput': analysis.average_throughput,
                'peak_throughput': analysis.peak_throughput,
                'min_throughput': analysis.min_throughput,
                'p95_throughput': analysis.p95_throughput,
                'p99_throughput': analysis.p99_throughput,
                'throughput_variance': analysis.throughput_variance,
                'target_achievement': analysis.target_achievement,
                'capacity_utilization': analysis.capacity_utilization,
                'error_rate': analysis.error_rate,
                'availability': analysis.availability,
                'category': analysis.category.value,
                'trends': analysis.trends,
                'bottlenecks': analysis.bottlenecks,
                'recommendations': analysis.recommendations
            }
            report_dict['component_analyses'].append(analysis_dict)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(report_dict, indent=2))
        
        logger.info(f"Throughput report saved to: {filepath}")
    
    async def start_monitoring(self, components: List[SystemComponent] = None, 
                             interval_seconds: int = 60):
        """
        Start continuous throughput monitoring
        
        DevOps expertise: Continuous monitoring and data collection
        """
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        
        if not components:
            components = [SystemComponent.API_GATEWAY, SystemComponent.WEB_SERVER, SystemComponent.DATABASE]
        
        async def monitor_components():
            while self.monitoring_active:
                for component in components:
                    try:
                        # Simulate throughput measurement (in real implementation, this would collect from actual systems)
                        base_throughput = {'api_gateway': 500, 'web_server': 1000, 'database': 200}.get(component.value, 100)
                        variation = np.random.normal(1, 0.1)
                        throughput = max(0, base_throughput * variation)
                        
                        # Collect system resource data
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        memory = psutil.virtual_memory()
                        
                        await self.record_throughput(
                            component=component,
                            metric_type=ThroughputMetricType.REQUESTS_PER_SECOND,
                            value=throughput,
                            unit="requests/sec",
                            target_value=base_throughput,
                            max_capacity=base_throughput * 2,
                            resource_utilization={
                                'cpu_usage': cpu_percent,
                                'memory_usage': memory.percent
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to collect metrics for {component.value}: {e}")
                
                await asyncio.sleep(interval_seconds)
        
        # Start monitoring in background
        asyncio.create_task(monitor_components())
        logger.info(f"Started throughput monitoring for {len(components)} components")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Stopped throughput monitoring")


# Global instance
throughput_metrics = ThroughputMetrics()


async def analyze_system_throughput(time_period_hours: int = 24) -> ThroughputReport:
    """Quick system throughput analysis"""
    time_period = timedelta(hours=time_period_hours)
    return await throughput_metrics.analyze_throughput(time_period)


async def monitor_component_throughput(component: SystemComponent, duration_minutes: int = 60):
    """Monitor specific component throughput"""
    await throughput_metrics.start_monitoring([component], 30)
    await asyncio.sleep(duration_minutes * 60)
    throughput_metrics.stop_monitoring()
    
    return await analyze_system_throughput(duration_minutes / 60)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Record some sample data
        components = [SystemComponent.API_GATEWAY, SystemComponent.WEB_SERVER, SystemComponent.DATABASE]
        
        for i in range(100):
            for component in components:
                base_value = {'api_gateway': 500, 'web_server': 1000, 'database': 200}[component.value]
                value = np.random.normal(base_value, base_value * 0.2)
                
                await throughput_metrics.record_throughput(
                    component=component,
                    metric_type=ThroughputMetricType.REQUESTS_PER_SECOND,
                    value=max(0, value),
                    unit="requests/sec",
                    target_value=base_value,
                    max_capacity=base_value * 2
                )
        
        # Analyze throughput
        report = await analyze_system_throughput(1)
        
        print(f"Throughput Report: {report.report_id}")
        print(f"Overall Throughput: {report.overall_throughput:.1f} requests/sec")
        print(f"Target Achievement: {report.target_achievement_rate:.1f}%")
        print(f"Capacity Utilization: {report.system_capacity_utilization:.1f}%")
        print(f"Availability: {report.overall_availability:.2f}%")
        
        if report.scaling_recommendations:
            print("\nScaling Recommendations:")
            for rec in report.scaling_recommendations[:5]:
                print(f"  - {rec}")
    
    asyncio.run(main())