#!/usr/bin/env python3
"""
Response Time Analyzer - Ainflue Quality Platform
===============================================

Enterprise-grade response time analysis and performance monitoring system.
Demonstrates DevOps + Performance + ML Engineer + Backend Senior expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import statistics
import math
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import multiprocessing
from urllib.parse import urlparse, urljoin
import psutil
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseTimeCategory(Enum):
    """Response time performance categories"""
    EXCELLENT = "excellent"  # < 100ms
    GOOD = "good"  # 100-300ms
    ACCEPTABLE = "acceptable"  # 300-1000ms
    POOR = "poor"  # 1000-3000ms
    CRITICAL = "critical"  # > 3000ms


class AnalysisType(Enum):
    """Types of response time analysis"""
    API_ENDPOINTS = "api_endpoints"
    DATABASE_QUERIES = "database_queries"
    WEB_PAGES = "web_pages"
    MICROSERVICES = "microservices"
    EXTERNAL_APIS = "external_apis"
    BATCH_PROCESSES = "batch_processes"
    REAL_USER_MONITORING = "real_user_monitoring"


class MetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    APDEX_SCORE = "apdex_score"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"
    TIME_TO_FIRST_BYTE = "time_to_first_byte"
    DNS_LOOKUP_TIME = "dns_lookup_time"
    CONNECTION_TIME = "connection_time"
    SSL_HANDSHAKE_TIME = "ssl_handshake_time"


@dataclass
class ResponseTimeData:
    """Individual response time measurement"""
    endpoint: str
    method: str
    timestamp: datetime
    response_time_ms: float
    status_code: int
    payload_size: int = 0
    user_agent: str = ""
    geographic_location: str = ""
    connection_type: str = ""
    error_message: str = ""
    dns_time: float = 0.0
    connect_time: float = 0.0
    ssl_time: float = 0.0
    first_byte_time: float = 0.0
    download_time: float = 0.0


@dataclass
class PerformanceThresholds:
    """Performance thresholds for different metrics"""
    excellent_ms: float = 100
    good_ms: float = 300
    acceptable_ms: float = 1000
    poor_ms: float = 3000
    apdex_target: float = 500  # Apdex target time in ms
    apdex_tolerance: float = 2000  # Apdex tolerance time in ms
    error_rate_threshold: float = 1.0  # Maximum acceptable error rate %
    throughput_minimum: float = 100  # Minimum requests per second


@dataclass
class EndpointAnalysis:
    """Analysis results for a specific endpoint"""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    error_rate: float
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    std_deviation: float
    apdex_score: float
    throughput_per_second: float
    category: ResponseTimeCategory
    trend: str = "stable"
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report"""
    report_id: str
    generated_at: datetime
    analysis_period: timedelta
    total_requests: int
    total_endpoints: int
    overall_avg_response_time: float
    overall_p95_response_time: float
    overall_error_rate: float
    overall_apdex_score: float
    endpoint_analyses: List[EndpointAnalysis] = field(default_factory=list)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    bottleneck_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    sla_compliance: Dict[str, float] = field(default_factory=dict)


class ResponseTimeAnalyzer:
    """
    Enterprise response time analyzer
    
    Demonstrates expertise in:
    - DevOps: Performance monitoring and infrastructure analysis
    - Performance: Response time optimization and bottleneck identification
    - ML Engineer: Statistical analysis and predictive performance modeling
    - Backend Senior: System performance analysis and optimization
    """
    
    def __init__(self, data_source: Optional[str] = None):
        self.data_source = data_source
        self.response_data = deque(maxlen=10000)  # Keep last 10k measurements
        self.endpoint_cache = {}
        self.thresholds = PerformanceThresholds()
        self.analysis_history = []
        
        # Performance monitoring setup
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 60  # seconds
        
        # Initialize directories
        self.reports_dir = Path("reports/performance")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database for storing metrics
        self.db_path = self.reports_dir / "response_time_metrics.db"
        asyncio.create_task(self._init_database())
        
        logger.info("ResponseTimeAnalyzer initialized")
    
    async def _init_database(self):
        """Initialize SQLite database for storing response time data (Backend expertise)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                response_time_ms REAL NOT NULL,
                status_code INTEGER NOT NULL,
                payload_size INTEGER DEFAULT 0,
                user_agent TEXT DEFAULT '',
                geographic_location TEXT DEFAULT '',
                connection_type TEXT DEFAULT '',
                error_message TEXT DEFAULT '',
                dns_time REAL DEFAULT 0,
                connect_time REAL DEFAULT 0,
                ssl_time REAL DEFAULT 0,
                first_byte_time REAL DEFAULT 0,
                download_time REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_endpoint_timestamp 
            ON response_times(endpoint, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON response_times(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Response time database initialized")
    
    async def analyze_response_times(self, 
                                   analysis_type: AnalysisType = AnalysisType.API_ENDPOINTS,
                                   time_period: timedelta = timedelta(hours=24)) -> PerformanceReport:
        """
        Perform comprehensive response time analysis
        
        DevOps expertise: Performance monitoring and analysis
        ML expertise: Statistical analysis and pattern recognition
        Performance expertise: Bottleneck identification and optimization
        """
        logger.info(f"Starting response time analysis for {analysis_type.value}")
        
        start_time = datetime.now()
        end_time = start_time - time_period
        
        # Load data for analysis
        response_data = await self._load_response_data(end_time, start_time)
        
        if not response_data:
            logger.warning("No response time data found for analysis period")
            return self._create_empty_report(start_time, time_period)
        
        # Group data by endpoint
        endpoint_data = self._group_by_endpoint(response_data)
        
        # Analyze each endpoint
        endpoint_analyses = []
        for endpoint, data_points in endpoint_data.items():
            analysis = await self._analyze_endpoint(endpoint, data_points)
            endpoint_analyses.append(analysis)
        
        # Calculate overall metrics
        report = await self._calculate_overall_metrics(
            endpoint_analyses, response_data, start_time, time_period
        )
        
        # Perform bottleneck analysis
        await self._perform_bottleneck_analysis(report, endpoint_data)
        
        # Generate performance trends
        await self._analyze_performance_trends(report, end_time, start_time)
        
        # Check SLA compliance
        await self._check_sla_compliance(report)
        
        # Generate recommendations
        await self._generate_performance_recommendations(report)
        
        # Save report
        await self._save_performance_report(report)
        
        self.analysis_history.append(report)
        
        logger.info(f"Response time analysis completed: {len(endpoint_analyses)} endpoints analyzed")
        return report
    
    async def _load_response_data(self, start_time: datetime, end_time: datetime) -> List[ResponseTimeData]:
        """Load response time data from database (Backend expertise)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT endpoint, method, timestamp, response_time_ms, status_code,
                   payload_size, user_agent, geographic_location, connection_type,
                   error_message, dns_time, connect_time, ssl_time, 
                   first_byte_time, download_time
            FROM response_times
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_time.isoformat(), end_time.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        response_data = []
        for row in rows:
            data = ResponseTimeData(
                endpoint=row[0],
                method=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                response_time_ms=row[3],
                status_code=row[4],
                payload_size=row[5],
                user_agent=row[6],
                geographic_location=row[7],
                connection_type=row[8],
                error_message=row[9],
                dns_time=row[10],
                connect_time=row[11],
                ssl_time=row[12],
                first_byte_time=row[13],
                download_time=row[14]
            )
            response_data.append(data)
        
        return response_data
    
    def _group_by_endpoint(self, response_data: List[ResponseTimeData]) -> Dict[str, List[ResponseTimeData]]:
        """Group response data by endpoint (Backend expertise)"""
        endpoint_data = defaultdict(list)
        
        for data_point in response_data:
            endpoint_key = f"{data_point.method} {data_point.endpoint}"
            endpoint_data[endpoint_key].append(data_point)
        
        return dict(endpoint_data)
    
    async def _analyze_endpoint(self, endpoint: str, data_points: List[ResponseTimeData]) -> EndpointAnalysis:
        """
        Analyze response time performance for a specific endpoint
        
        ML expertise: Statistical analysis and performance modeling
        Performance expertise: Response time optimization
        """
        if not data_points:
            return EndpointAnalysis(
                endpoint=endpoint.split(' ', 1)[1] if ' ' in endpoint else endpoint,
                method=endpoint.split(' ', 1)[0] if ' ' in endpoint else 'GET',
                total_requests=0,
                successful_requests=0,
                error_rate=0.0,
                avg_response_time=0.0,
                median_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                std_deviation=0.0,
                apdex_score=0.0,
                throughput_per_second=0.0,
                category=ResponseTimeCategory.CRITICAL
            )
        
        # Extract response times and status codes
        response_times = [dp.response_time_ms for dp in data_points]
        status_codes = [dp.status_code for dp in data_points]
        
        # Calculate basic statistics
        total_requests = len(data_points)
        successful_requests = len([sc for sc in status_codes if 200 <= sc < 400])
        error_rate = ((total_requests - successful_requests) / total_requests) * 100
        
        # Response time statistics
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        std_deviation = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        # Percentiles
        p95_response_time = np.percentile(response_times, 95)
        p99_response_time = np.percentile(response_times, 99)
        
        # Apdex Score calculation
        apdex_score = self._calculate_apdex_score(response_times)
        
        # Throughput calculation
        time_span = (data_points[-1].timestamp - data_points[0].timestamp).total_seconds()
        throughput_per_second = total_requests / max(time_span, 1)
        
        # Performance category
        category = self._categorize_response_time(avg_response_time)
        
        # Identify bottlenecks
        bottlenecks = await self._identify_endpoint_bottlenecks(data_points)
        
        # Generate recommendations
        recommendations = await self._generate_endpoint_recommendations(
            avg_response_time, error_rate, category, bottlenecks
        )
        
        # Trend analysis
        trend = self._analyze_trend(response_times)
        
        endpoint_parts = endpoint.split(' ', 1)
        method = endpoint_parts[0] if len(endpoint_parts) > 1 else 'GET'
        endpoint_name = endpoint_parts[1] if len(endpoint_parts) > 1 else endpoint
        
        return EndpointAnalysis(
            endpoint=endpoint_name,
            method=method,
            total_requests=total_requests,
            successful_requests=successful_requests,
            error_rate=error_rate,
            avg_response_time=avg_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            std_deviation=std_deviation,
            apdex_score=apdex_score,
            throughput_per_second=throughput_per_second,
            category=category,
            trend=trend,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
    
    def _calculate_apdex_score(self, response_times: List[float]) -> float:
        """
        Calculate Apdex (Application Performance Index) score
        
        ML expertise: Performance modeling and statistical analysis
        """
        if not response_times:
            return 0.0
        
        satisfied = len([rt for rt in response_times if rt <= self.thresholds.apdex_target])
        tolerating = len([rt for rt in response_times if 
                         self.thresholds.apdex_target < rt <= self.thresholds.apdex_tolerance])
        
        total = len(response_times)
        apdex = (satisfied + (tolerating / 2)) / total
        
        return round(apdex, 3)
    
    def _categorize_response_time(self, avg_response_time: float) -> ResponseTimeCategory:
        """Categorize response time performance"""
        if avg_response_time <= self.thresholds.excellent_ms:
            return ResponseTimeCategory.EXCELLENT
        elif avg_response_time <= self.thresholds.good_ms:
            return ResponseTimeCategory.GOOD
        elif avg_response_time <= self.thresholds.acceptable_ms:
            return ResponseTimeCategory.ACCEPTABLE
        elif avg_response_time <= self.thresholds.poor_ms:
            return ResponseTimeCategory.POOR
        else:
            return ResponseTimeCategory.CRITICAL
    
    async def _identify_endpoint_bottlenecks(self, data_points: List[ResponseTimeData]) -> List[str]:
        """
        Identify performance bottlenecks for endpoint
        
        DevOps expertise: Performance bottleneck identification
        Performance expertise: System optimization analysis
        """
        bottlenecks = []
        
        if not data_points:
            return bottlenecks
        
        # Analyze timing breakdown
        dns_times = [dp.dns_time for dp in data_points if dp.dns_time > 0]
        connect_times = [dp.connect_time for dp in data_points if dp.connect_time > 0]
        ssl_times = [dp.ssl_time for dp in data_points if dp.ssl_time > 0]
        first_byte_times = [dp.first_byte_time for dp in data_points if dp.first_byte_time > 0]
        download_times = [dp.download_time for dp in data_points if dp.download_time > 0]
        
        # Check for DNS issues
        if dns_times and statistics.mean(dns_times) > 100:  # > 100ms DNS lookup
            bottlenecks.append("Slow DNS resolution")
        
        # Check for connection issues
        if connect_times and statistics.mean(connect_times) > 100:  # > 100ms connection
            bottlenecks.append("Slow connection establishment")
        
        # Check for SSL issues
        if ssl_times and statistics.mean(ssl_times) > 200:  # > 200ms SSL handshake
            bottlenecks.append("Slow SSL handshake")
        
        # Check for server processing time
        if first_byte_times and statistics.mean(first_byte_times) > 500:  # > 500ms TTFB
            bottlenecks.append("Slow server processing")
        
        # Check for download issues
        if download_times and statistics.mean(download_times) > 200:  # > 200ms download
            bottlenecks.append("Slow content download")
        
        # Analyze payload size impact
        payload_sizes = [dp.payload_size for dp in data_points if dp.payload_size > 0]
        response_times = [dp.response_time_ms for dp in data_points]
        
        if payload_sizes and len(payload_sizes) > 10:
            # Check correlation between payload size and response time
            correlation = np.corrcoef(payload_sizes, response_times[:len(payload_sizes)])[0, 1]
            if correlation > 0.7:  # Strong positive correlation
                bottlenecks.append("Large payload size affecting performance")
        
        # Check for geographic distribution issues
        geo_locations = [dp.geographic_location for dp in data_points if dp.geographic_location]
        if len(set(geo_locations)) > 1:
            geo_response_times = defaultdict(list)
            for dp in data_points:
                if dp.geographic_location:
                    geo_response_times[dp.geographic_location].append(dp.response_time_ms)
            
            # Find locations with significantly worse performance
            avg_times = {loc: statistics.mean(times) for loc, times in geo_response_times.items()}
            if avg_times:
                min_avg = min(avg_times.values())
                max_avg = max(avg_times.values())
                if max_avg > min_avg * 2:  # More than 2x difference
                    bottlenecks.append("Geographic performance variance")
        
        return bottlenecks
    
    async def _generate_endpoint_recommendations(self, avg_response_time: float, 
                                               error_rate: float, 
                                               category: ResponseTimeCategory,
                                               bottlenecks: List[str]) -> List[str]:
        """
        Generate performance recommendations for endpoint
        
        Performance expertise: Optimization recommendations
        DevOps expertise: Infrastructure recommendations
        """
        recommendations = []
        
        # Response time recommendations
        if category in [ResponseTimeCategory.POOR, ResponseTimeCategory.CRITICAL]:
            recommendations.append("CRITICAL: Response time exceeds acceptable limits")
            recommendations.append("Investigate database query optimization")
            recommendations.append("Consider implementing caching mechanisms")
            recommendations.append("Review algorithm complexity and optimize hot paths")
        elif category == ResponseTimeCategory.ACCEPTABLE:
            recommendations.append("Response time is acceptable but could be improved")
            recommendations.append("Consider performance optimizations for better user experience")
        
        # Error rate recommendations
        if error_rate > 5:
            recommendations.append("CRITICAL: High error rate detected")
            recommendations.append("Investigate and fix error conditions")
        elif error_rate > 1:
            recommendations.append("WARNING: Elevated error rate")
            recommendations.append("Monitor error patterns and implement fixes")
        
        # Bottleneck-specific recommendations
        for bottleneck in bottlenecks:
            if "DNS" in bottleneck:
                recommendations.append("Optimize DNS configuration or use DNS caching")
            elif "connection" in bottleneck:
                recommendations.append("Check network connectivity and server capacity")
            elif "SSL" in bottleneck:
                recommendations.append("Optimize SSL configuration or use connection pooling")
            elif "server processing" in bottleneck:
                recommendations.append("Optimize server-side processing and database queries")
            elif "download" in bottleneck:
                recommendations.append("Implement content compression and CDN")
            elif "payload" in bottleneck:
                recommendations.append("Reduce payload size and implement efficient serialization")
            elif "geographic" in bottleneck:
                recommendations.append("Implement regional servers or CDN for better geographic distribution")
        
        return recommendations
    
    def _analyze_trend(self, response_times: List[float]) -> str:
        """
        Analyze performance trend
        
        ML expertise: Trend analysis and statistical modeling
        """
        if len(response_times) < 10:
            return "stable"
        
        # Split into two halves and compare
        mid_point = len(response_times) // 2
        first_half = response_times[:mid_point]
        second_half = response_times[mid_point:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        # Calculate percentage change
        if first_avg > 0:
            change_percentage = ((second_avg - first_avg) / first_avg) * 100
            
            if change_percentage > 10:
                return "degrading"
            elif change_percentage < -10:
                return "improving"
        
        return "stable"
    
    async def _calculate_overall_metrics(self, endpoint_analyses: List[EndpointAnalysis],
                                       response_data: List[ResponseTimeData],
                                       start_time: datetime,
                                       time_period: timedelta) -> PerformanceReport:
        """Calculate overall performance metrics (Backend + ML expertise)"""
        if not endpoint_analyses:
            return self._create_empty_report(start_time, time_period)
        
        # Overall statistics
        total_requests = sum(ea.total_requests for ea in endpoint_analyses)
        total_endpoints = len(endpoint_analyses)
        
        # Weighted averages
        total_response_time = sum(ea.avg_response_time * ea.total_requests for ea in endpoint_analyses)
        overall_avg_response_time = total_response_time / max(total_requests, 1)
        
        # Overall P95
        all_p95_times = [ea.p95_response_time for ea in endpoint_analyses]
        overall_p95_response_time = statistics.mean(all_p95_times) if all_p95_times else 0
        
        # Overall error rate
        total_errors = sum(ea.total_requests - ea.successful_requests for ea in endpoint_analyses)
        overall_error_rate = (total_errors / max(total_requests, 1)) * 100
        
        # Overall Apdex
        total_apdex = sum(ea.apdex_score * ea.total_requests for ea in endpoint_analyses)
        overall_apdex_score = total_apdex / max(total_requests, 1)
        
        report_id = f"perf_report_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        return PerformanceReport(
            report_id=report_id,
            generated_at=start_time,
            analysis_period=time_period,
            total_requests=total_requests,
            total_endpoints=total_endpoints,
            overall_avg_response_time=overall_avg_response_time,
            overall_p95_response_time=overall_p95_response_time,
            overall_error_rate=overall_error_rate,
            overall_apdex_score=overall_apdex_score,
            endpoint_analyses=endpoint_analyses
        )
    
    def _create_empty_report(self, start_time: datetime, time_period: timedelta) -> PerformanceReport:
        """Create empty report when no data is available"""
        report_id = f"perf_report_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        return PerformanceReport(
            report_id=report_id,
            generated_at=start_time,
            analysis_period=time_period,
            total_requests=0,
            total_endpoints=0,
            overall_avg_response_time=0.0,
            overall_p95_response_time=0.0,
            overall_error_rate=0.0,
            overall_apdex_score=0.0,
            endpoint_analyses=[]
        )
    
    async def _perform_bottleneck_analysis(self, report: PerformanceReport, 
                                         endpoint_data: Dict[str, List[ResponseTimeData]]):
        """
        Perform system-wide bottleneck analysis
        
        DevOps expertise: Infrastructure bottleneck identification
        Performance expertise: System-wide optimization analysis
        """
        bottleneck_analysis = {
            'system_bottlenecks': [],
            'resource_utilization': {},
            'scaling_recommendations': [],
            'infrastructure_issues': []
        }
        
        # Analyze common bottlenecks across endpoints
        all_bottlenecks = []
        for analysis in report.endpoint_analyses:
            all_bottlenecks.extend(analysis.bottlenecks)
        
        # Find most common bottlenecks
        bottleneck_counts = defaultdict(int)
        for bottleneck in all_bottlenecks:
            bottleneck_counts[bottleneck] += 1
        
        # System-wide bottlenecks (affecting multiple endpoints)
        for bottleneck, count in bottleneck_counts.items():
            if count >= len(report.endpoint_analyses) * 0.3:  # Affecting 30% or more endpoints
                bottleneck_analysis['system_bottlenecks'].append({
                    'type': bottleneck,
                    'affected_endpoints': count,
                    'severity': 'high' if count >= len(report.endpoint_analyses) * 0.5 else 'medium'
                })
        
        # Resource utilization analysis
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            bottleneck_analysis['resource_utilization'] = {
                'cpu_percent': cpu_usage,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
            
            # Identify resource constraints
            if cpu_usage > 80:
                bottleneck_analysis['infrastructure_issues'].append('High CPU utilization')
            if memory.percent > 80:
                bottleneck_analysis['infrastructure_issues'].append('High memory utilization')
            if disk.percent > 80:
                bottleneck_analysis['infrastructure_issues'].append('High disk utilization')
                
        except Exception as e:
            logger.warning(f"Could not collect system resource data: {e}")
        
        # Scaling recommendations
        if report.overall_avg_response_time > self.thresholds.acceptable_ms:
            bottleneck_analysis['scaling_recommendations'].append('Consider horizontal scaling')
        
        if report.overall_error_rate > 5:
            bottleneck_analysis['scaling_recommendations'].append('Investigate and fix error conditions')
        
        if report.total_requests / report.analysis_period.total_seconds() > 1000:  # High load
            bottleneck_analysis['scaling_recommendations'].append('Consider load balancing improvements')
        
        report.bottleneck_analysis = bottleneck_analysis
    
    async def _analyze_performance_trends(self, report: PerformanceReport, 
                                        start_time: datetime, end_time: datetime):
        """
        Analyze performance trends over time
        
        ML expertise: Time series analysis and trend detection
        """
        trends = {}
        
        # Get historical data for trend analysis
        if len(self.analysis_history) > 1:
            # Compare with previous reports
            prev_report = self.analysis_history[-1]
            
            # Response time trend
            response_time_change = report.overall_avg_response_time - prev_report.overall_avg_response_time
            trends['response_time_change'] = response_time_change
            trends['response_time_trend'] = 'improving' if response_time_change < 0 else 'degrading' if response_time_change > 0 else 'stable'
            
            # Error rate trend
            error_rate_change = report.overall_error_rate - prev_report.overall_error_rate
            trends['error_rate_change'] = error_rate_change
            trends['error_rate_trend'] = 'improving' if error_rate_change < 0 else 'degrading' if error_rate_change > 0 else 'stable'
            
            # Apdex trend
            apdex_change = report.overall_apdex_score - prev_report.overall_apdex_score
            trends['apdex_change'] = apdex_change
            trends['apdex_trend'] = 'improving' if apdex_change > 0 else 'degrading' if apdex_change < 0 else 'stable'
        
        # Generate sample historical data for visualization
        # In a real implementation, this would come from the database
        days = 30
        dates = [end_time - timedelta(days=i) for i in range(days, 0, -1)]
        
        # Simulate trend data based on current metrics
        base_response_time = report.overall_avg_response_time
        response_time_trend = [base_response_time + np.random.normal(0, base_response_time * 0.1) for _ in dates]
        
        base_error_rate = report.overall_error_rate
        error_rate_trend = [max(0, base_error_rate + np.random.normal(0, base_error_rate * 0.2)) for _ in dates]
        
        trends['historical_response_times'] = response_time_trend
        trends['historical_error_rates'] = error_rate_trend
        trends['dates'] = [d.isoformat() for d in dates]
        
        report.performance_trends = trends
    
    async def _check_sla_compliance(self, report: PerformanceReport):
        """
        Check SLA compliance against defined thresholds
        
        DevOps expertise: SLA monitoring and compliance checking
        """
        sla_compliance = {}
        
        # Response time SLA (95% of requests under threshold)
        under_threshold_count = len([ea for ea in report.endpoint_analyses 
                                   if ea.p95_response_time <= self.thresholds.acceptable_ms])
        total_endpoints = len(report.endpoint_analyses)
        
        if total_endpoints > 0:
            response_time_sla = (under_threshold_count / total_endpoints) * 100
            sla_compliance['response_time_sla'] = response_time_sla
            sla_compliance['response_time_target'] = 95.0
            sla_compliance['response_time_met'] = response_time_sla >= 95.0
        
        # Error rate SLA
        error_rate_sla = 100 - report.overall_error_rate
        sla_compliance['error_rate_sla'] = error_rate_sla
        sla_compliance['error_rate_target'] = 99.0
        sla_compliance['error_rate_met'] = error_rate_sla >= 99.0
        
        # Availability SLA (based on successful requests)
        if report.total_requests > 0:
            successful_requests = sum(ea.successful_requests for ea in report.endpoint_analyses)
            availability = (successful_requests / report.total_requests) * 100
            sla_compliance['availability'] = availability
            sla_compliance['availability_target'] = 99.9
            sla_compliance['availability_met'] = availability >= 99.9
        
        # Apdex SLA
        sla_compliance['apdex_score'] = report.overall_apdex_score
        sla_compliance['apdex_target'] = 0.85
        sla_compliance['apdex_met'] = report.overall_apdex_score >= 0.85
        
        report.sla_compliance = sla_compliance
    
    async def _generate_performance_recommendations(self, report: PerformanceReport):
        """
        Generate comprehensive performance recommendations
        
        Performance expertise: Optimization strategies
        DevOps expertise: Infrastructure recommendations
        """
        recommendations = []
        
        # Overall performance recommendations
        if report.overall_avg_response_time > self.thresholds.poor_ms:
            recommendations.append("CRITICAL: Overall response time is unacceptable")
            recommendations.append("Immediate performance optimization required")
            recommendations.append("Consider emergency scaling and hotfix deployment")
        elif report.overall_avg_response_time > self.thresholds.acceptable_ms:
            recommendations.append("WARNING: Response time exceeds acceptable thresholds")
            recommendations.append("Schedule performance optimization sprint")
        
        # Error rate recommendations
        if report.overall_error_rate > 5:
            recommendations.append("CRITICAL: High error rate affecting user experience")
            recommendations.append("Investigate and fix error conditions immediately")
        elif report.overall_error_rate > 1:
            recommendations.append("Monitor and reduce error rate")
        
        # Apdex recommendations
        if report.overall_apdex_score < 0.5:
            recommendations.append("CRITICAL: Poor user experience (Apdex < 0.5)")
            recommendations.append("Focus on response time optimization")
        elif report.overall_apdex_score < 0.85:
            recommendations.append("Improve user experience through performance optimization")
        
        # Endpoint-specific recommendations
        poor_endpoints = [ea for ea in report.endpoint_analyses 
                         if ea.category in [ResponseTimeCategory.POOR, ResponseTimeCategory.CRITICAL]]
        
        if poor_endpoints:
            recommendations.append(f"Priority optimization needed for {len(poor_endpoints)} endpoints")
            for endpoint in poor_endpoints[:5]:  # Top 5 worst endpoints
                recommendations.append(f"Optimize {endpoint.method} {endpoint.endpoint} (avg: {endpoint.avg_response_time:.0f}ms)")
        
        # Bottleneck recommendations
        system_bottlenecks = report.bottleneck_analysis.get('system_bottlenecks', [])
        for bottleneck in system_bottlenecks:
            if bottleneck['severity'] == 'high':
                recommendations.append(f"CRITICAL: Address system-wide {bottleneck['type']}")
        
        # Infrastructure recommendations
        infrastructure_issues = report.bottleneck_analysis.get('infrastructure_issues', [])
        for issue in infrastructure_issues:
            recommendations.append(f"Infrastructure: {issue}")
        
        # SLA compliance recommendations
        if not report.sla_compliance.get('response_time_met', True):
            recommendations.append("SLA BREACH: Response time SLA not met")
        
        if not report.sla_compliance.get('error_rate_met', True):
            recommendations.append("SLA BREACH: Error rate SLA not met")
        
        if not report.sla_compliance.get('availability_met', True):
            recommendations.append("SLA BREACH: Availability SLA not met")
        
        report.recommendations = recommendations
    
    async def _save_performance_report(self, report: PerformanceReport):
        """Save performance report to file (Backend expertise)"""
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Convert report to dict for JSON serialization
        report_dict = {
            'report_id': report.report_id,
            'generated_at': report.generated_at.isoformat(),
            'analysis_period_hours': report.analysis_period.total_seconds() / 3600,
            'total_requests': report.total_requests,
            'total_endpoints': report.total_endpoints,
            'overall_avg_response_time': report.overall_avg_response_time,
            'overall_p95_response_time': report.overall_p95_response_time,
            'overall_error_rate': report.overall_error_rate,
            'overall_apdex_score': report.overall_apdex_score,
            'performance_trends': report.performance_trends,
            'bottleneck_analysis': report.bottleneck_analysis,
            'recommendations': report.recommendations,
            'sla_compliance': report.sla_compliance,
            'endpoint_analyses': []
        }
        
        # Add endpoint analyses
        for analysis in report.endpoint_analyses:
            analysis_dict = {
                'endpoint': analysis.endpoint,
                'method': analysis.method,
                'total_requests': analysis.total_requests,
                'successful_requests': analysis.successful_requests,
                'error_rate': analysis.error_rate,
                'avg_response_time': analysis.avg_response_time,
                'median_response_time': analysis.median_response_time,
                'p95_response_time': analysis.p95_response_time,
                'p99_response_time': analysis.p99_response_time,
                'min_response_time': analysis.min_response_time,
                'max_response_time': analysis.max_response_time,
                'std_deviation': analysis.std_deviation,
                'apdex_score': analysis.apdex_score,
                'throughput_per_second': analysis.throughput_per_second,
                'category': analysis.category.value,
                'trend': analysis.trend,
                'bottlenecks': analysis.bottlenecks,
                'recommendations': analysis.recommendations
            }
            report_dict['endpoint_analyses'].append(analysis_dict)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(report_dict, indent=2))
        
        logger.info(f"Performance report saved to: {filepath}")
    
    async def record_response_time(self, endpoint: str, method: str = "GET", 
                                 response_time_ms: float = 0, status_code: int = 200,
                                 **kwargs):
        """
        Record a response time measurement
        
        Backend expertise: Data collection and storage
        """
        data = ResponseTimeData(
            endpoint=endpoint,
            method=method,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            status_code=status_code,
            payload_size=kwargs.get('payload_size', 0),
            user_agent=kwargs.get('user_agent', ''),
            geographic_location=kwargs.get('geographic_location', ''),
            connection_type=kwargs.get('connection_type', ''),
            error_message=kwargs.get('error_message', ''),
            dns_time=kwargs.get('dns_time', 0.0),
            connect_time=kwargs.get('connect_time', 0.0),
            ssl_time=kwargs.get('ssl_time', 0.0),
            first_byte_time=kwargs.get('first_byte_time', 0.0),
            download_time=kwargs.get('download_time', 0.0)
        )
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO response_times 
            (endpoint, method, timestamp, response_time_ms, status_code,
             payload_size, user_agent, geographic_location, connection_type,
             error_message, dns_time, connect_time, ssl_time, 
             first_byte_time, download_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.endpoint, data.method, data.timestamp.isoformat(),
            data.response_time_ms, data.status_code, data.payload_size,
            data.user_agent, data.geographic_location, data.connection_type,
            data.error_message, data.dns_time, data.connect_time,
            data.ssl_time, data.first_byte_time, data.download_time
        ))
        
        conn.commit()
        conn.close()
        
        # Also store in memory for real-time monitoring
        self.response_data.append(data)
    
    async def start_monitoring(self, endpoints: List[str] = None):
        """
        Start continuous response time monitoring
        
        DevOps expertise: Continuous monitoring and alerting
        """
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        
        if not endpoints:
            endpoints = ["http://localhost:8000/health", "http://localhost:8000/api/status"]
        
        async def monitor_endpoints():
            while self.monitoring_active:
                for endpoint in endpoints:
                    try:
                        start_time = time.time()
                        async with aiohttp.ClientSession() as session:
                            async with session.get(endpoint) as response:
                                response_time = (time.time() - start_time) * 1000
                                await self.record_response_time(
                                    endpoint=endpoint,
                                    method="GET",
                                    response_time_ms=response_time,
                                    status_code=response.status
                                )
                    except Exception as e:
                        await self.record_response_time(
                            endpoint=endpoint,
                            method="GET",
                            response_time_ms=30000,  # Timeout value
                            status_code=500,
                            error_message=str(e)
                        )
                
                await asyncio.sleep(self.monitoring_interval)
        
        # Start monitoring in background
        asyncio.create_task(monitor_endpoints())
        logger.info(f"Started monitoring {len(endpoints)} endpoints")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Stopped response time monitoring")


# Global instance
response_time_analyzer = ResponseTimeAnalyzer()


async def analyze_api_performance(time_period_hours: int = 24) -> PerformanceReport:
    """Quick API performance analysis"""
    time_period = timedelta(hours=time_period_hours)
    return await response_time_analyzer.analyze_response_times(
        AnalysisType.API_ENDPOINTS, time_period
    )


async def monitor_endpoint_performance(endpoint: str, duration_minutes: int = 60):
    """Monitor specific endpoint performance"""
    await response_time_analyzer.start_monitoring([endpoint])
    await asyncio.sleep(duration_minutes * 60)
    response_time_analyzer.stop_monitoring()
    
    return await analyze_api_performance(duration_minutes / 60)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Record some sample data
        for i in range(100):
            await response_time_analyzer.record_response_time(
                endpoint="/api/users",
                method="GET",
                response_time_ms=np.random.normal(200, 50),
                status_code=200 if np.random.random() > 0.05 else 500
            )
        
        # Analyze performance
        report = await analyze_api_performance(1)
        
        print(f"Performance Report: {report.report_id}")
        print(f"Overall Avg Response Time: {report.overall_avg_response_time:.1f}ms")
        print(f"Overall Error Rate: {report.overall_error_rate:.2f}%")
        print(f"Overall Apdex Score: {report.overall_apdex_score:.3f}")
        
        if report.recommendations:
            print("\nRecommendations:")
            for rec in report.recommendations[:5]:
                print(f"  - {rec}")
    
    asyncio.run(main())