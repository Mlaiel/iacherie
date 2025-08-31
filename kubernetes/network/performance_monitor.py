"""
IA Influencer Agent - Network Performance Monitor
Enterprise network performance monitoring and optimization for content protection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

  AVERTISSEMENT SÉVÈRE 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import psutil
import speedtest
import ping3
from datetime import datetime, timedelta
import json
import numpy as np
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiohttp

from prometheus_client import Counter, Histogram, Gauge, Summary

# Metrics
network_latency_seconds = Histogram('network_latency_seconds', 'Network latency in seconds', ['source', 'destination'])
network_throughput_bps = Gauge('network_throughput_bps', 'Network throughput in bits per second', ['direction'])
network_packet_loss_ratio = Gauge('network_packet_loss_ratio', 'Packet loss ratio', ['interface'])
network_jitter_seconds = Gauge('network_jitter_seconds', 'Network jitter in seconds', ['interface'])
network_quality_score = Gauge('network_quality_score', 'Overall network quality score')

logger = logging.getLogger(__name__)


class NetworkInterface(Enum):
    """Network interface types"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    VPN = "vpn"
    CELLULAR = "cellular"
    SATELLITE = "satellite"


class PerformanceMetric(Enum):
    """Network performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    PACKET_LOSS = "packet_loss"
    JITTER = "jitter"
    BANDWIDTH = "bandwidth"
    CONNECTION_COUNT = "connection_count"
    ERROR_RATE = "error_rate"


class OptimizationStrategy(Enum):
    """Network optimization strategies"""
    BANDWIDTH_OPTIMIZATION = "bandwidth_optimization"
    LATENCY_REDUCTION = "latency_reduction"
    RELIABILITY_IMPROVEMENT = "reliability_improvement"
    COST_OPTIMIZATION = "cost_optimization"
    SECURITY_ENHANCEMENT = "security_enhancement"


@dataclass
class NetworkPerformanceData:
    """Network performance measurement data"""
    timestamp: datetime
    interface: NetworkInterface
    latency_ms: float
    throughput_mbps: float
    packet_loss_percent: float
    jitter_ms: float
    bandwidth_utilization_percent: float
    active_connections: int
    error_count: int
    quality_score: float


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric: PerformanceMetric
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str


@dataclass
class OptimizationRecommendation:
    """Network optimization recommendation"""
    strategy: OptimizationStrategy
    priority: int  # 1 (highest) to 5 (lowest)
    impact_score: float  # 0.0 to 1.0
    implementation_effort: str  # low, medium, high
    description: str
    technical_details: Dict[str, Any]
    estimated_improvement: Dict[str, float]
    cost_estimate: Optional[float] = None


class NetworkPerformanceMonitor:
    """
    Network Performance Monitor for IA Influencer Agent Platform
    Provides comprehensive network performance monitoring and optimization recommendations
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str = "redis://localhost:6379",
        monitoring_interval: int = 60
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.monitoring_interval = monitoring_interval
        
        # Database connections
        self.engine = None
        self.session_factory = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Performance data
        self.performance_history: List[NetworkPerformanceData] = []
        self.current_metrics: Dict[str, float] = {}
        self.quality_baselines: Dict[str, float] = {}
        
        # Thresholds and configuration
        self.performance_thresholds: Dict[PerformanceMetric, PerformanceThreshold] = {}
        self.optimization_rules: List[Dict[str, Any]] = []
        
        # Monitoring tools
        self.speedtest_client = None
        self.monitored_endpoints: List[str] = []
        
        # Analysis and optimization
        self.baseline_period_days = 7
        self.optimization_history: List[OptimizationRecommendation] = []
    
    async def initialize(self) -> bool:
        """Initialize network performance monitor"""



        try:
            logger.info("Initializing Network Performance Monitor...")
            
            # Initialize database connection
            self.engine = create_async_engine(self.database_url)
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize Redis
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize speedtest client
            self.speedtest_client = speedtest.Speedtest()
            
            # Load configuration
            await self._load_performance_thresholds()
            await self._load_optimization_rules()
            await self._load_monitored_endpoints()
            
            # Calculate baselines
            await self._calculate_performance_baselines()
            
            # Start monitoring tasks
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._optimization_analysis_loop())
            asyncio.create_task(self._alert_monitoring_loop())
            
            logger.info("Network Performance Monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Network Performance Monitor: {e}")
            return False
    
    async def measure_network_performance(
        self,
        target_endpoints: Optional[List[str]] = None
    ) -> NetworkPerformanceData:
        """Measure comprehensive network performance"""



        try:
            start_time = datetime.now()
            endpoints = target_endpoints or self.monitored_endpoints
            
            # Measure latency to multiple endpoints
            latencies = []
            for endpoint in endpoints[:5]:  # Limit to 5 endpoints for performance
                try:
                    latency = ping3.ping(endpoint, timeout=5)
                    if latency:
                        latencies.append(latency * 1000)  # Convert to milliseconds
                except Exception as e:
                    logger.warning(f"Failed to ping {endpoint}: {e}")
            
            avg_latency = np.mean(latencies) if latencies else 999.0
            jitter = np.std(latencies) if len(latencies) > 1 else 0.0
            
            # Measure throughput using speedtest
            throughput_down, throughput_up = await self._measure_throughput()
            
            # Get network interface statistics
            network_stats = psutil.net_io_counters()
            
            # Calculate packet loss (simplified estimation)
            packet_loss = await self._estimate_packet_loss(endpoints)
            
            # Calculate bandwidth utilization
            bandwidth_utilization = await self._calculate_bandwidth_utilization()
            
            # Get active connections
            active_connections = len(psutil.net_connections())
            
            # Calculate error rate
            error_count = await self._get_network_error_count()
            
            # Calculate overall quality score
            quality_score = await self._calculate_quality_score(
                avg_latency, throughput_down, packet_loss, jitter
            )
            
            # Create performance data object
            performance_data = NetworkPerformanceData(
                timestamp=start_time,
                interface=NetworkInterface.ETHERNET,  # Default, could be detected
                latency_ms=avg_latency,
                throughput_mbps=(throughput_down + throughput_up) / 2,
                packet_loss_percent=packet_loss,
                jitter_ms=jitter,
                bandwidth_utilization_percent=bandwidth_utilization,
                active_connections=active_connections,
                error_count=error_count,
                quality_score=quality_score
            )
            
            # Update metrics
            network_latency_seconds.labels(source="monitor", destination="endpoints").observe(avg_latency / 1000)
            network_throughput_bps.labels(direction="combined").set((throughput_down + throughput_up) * 1000000)
            network_packet_loss_ratio.labels(interface="default").set(packet_loss / 100)
            network_jitter_seconds.labels(interface="default").set(jitter / 1000)
            network_quality_score.set(quality_score)
            
            # Store performance data
            self.performance_history.append(performance_data)
            await self._store_performance_data(performance_data)
            
            # Update current metrics
            self.current_metrics.update({
                'latency': avg_latency,
                'throughput': (throughput_down + throughput_up) / 2,
                'packet_loss': packet_loss,
                'jitter': jitter,
                'quality_score': quality_score
            })
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Failed to measure network performance: {e}")
            # Return default data with error indicators
            return NetworkPerformanceData(
                timestamp=datetime.now(),
                interface=NetworkInterface.ETHERNET,
                latency_ms=999.0,
                throughput_mbps=0.0,
                packet_loss_percent=100.0,
                jitter_ms=999.0,
                bandwidth_utilization_percent=0.0,
                active_connections=0,
                error_count=1,
                quality_score=0.0
            )
    
    async def analyze_performance_trends(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Analyze network performance trends"""



        try:
            end_time = datetime.now()
            start_time = end_time - time_range
            
            # Get historical data
            historical_data = await self._get_historical_performance_data(start_time, end_time)
            
            if not historical_data:
                logger.warning("No historical data available for trend analysis")
                return {}
            
            # Calculate trends
            trends = {
                'latency_trend': await self._calculate_metric_trend(historical_data, 'latency_ms'),
                'throughput_trend': await self._calculate_metric_trend(historical_data, 'throughput_mbps'),
                'packet_loss_trend': await self._calculate_metric_trend(historical_data, 'packet_loss_percent'),
                'quality_trend': await self._calculate_metric_trend(historical_data, 'quality_score'),
                'performance_summary': await self._generate_performance_summary(historical_data),
                'degradation_periods': await self._identify_degradation_periods(historical_data),
                'peak_performance_periods': await self._identify_peak_periods(historical_data)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")
            return {}
    
    async def generate_optimization_recommendations(
        self,
        current_performance: Optional[NetworkPerformanceData] = None
    ) -> List[OptimizationRecommendation]:
        """Generate network optimization recommendations"""



        try:
            if not current_performance:
                current_performance = await self.measure_network_performance()
            
            recommendations = []
            
            # Analyze each performance metric
            if current_performance.latency_ms > 100:  # High latency
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.LATENCY_REDUCTION,
                    priority=1,
                    impact_score=0.8,
                    implementation_effort="medium",
                    description="Implement CDN edge caching to reduce latency",
                    technical_details={
                        'current_latency': current_performance.latency_ms,
                        'target_latency': 50.0,
                        'optimization_methods': ['edge_caching', 'dns_optimization', 'route_optimization']
                    },
                    estimated_improvement={'latency_reduction_percent': 60}
                ))
            
            if current_performance.throughput_mbps < 50:  # Low throughput
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.BANDWIDTH_OPTIMIZATION,
                    priority=2,
                    impact_score=0.7,
                    implementation_effort="high",
                    description="Upgrade bandwidth capacity and implement traffic shaping",
                    technical_details={
                        'current_throughput': current_performance.throughput_mbps,
                        'recommended_throughput': 100.0,
                        'optimization_methods': ['bandwidth_upgrade', 'traffic_shaping', 'qos_implementation']
                    },
                    estimated_improvement={'throughput_increase_percent': 100}
                ))
            
            if current_performance.packet_loss_percent > 1.0:  # High packet loss
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.RELIABILITY_IMPROVEMENT,
                    priority=1,
                    impact_score=0.9,
                    implementation_effort="medium",
                    description="Improve network reliability through redundancy and error correction",
                    technical_details={
                        'current_packet_loss': current_performance.packet_loss_percent,
                        'target_packet_loss': 0.1,
                        'optimization_methods': ['redundant_paths', 'error_correction', 'buffer_optimization']
                    },
                    estimated_improvement={'packet_loss_reduction_percent': 90}
                ))
            
            if current_performance.bandwidth_utilization_percent > 80:  # High utilization
                recommendations.append(OptimizationRecommendation(
                    strategy=OptimizationStrategy.BANDWIDTH_OPTIMIZATION,
                    priority=2,
                    impact_score=0.6,
                    implementation_effort="low",
                    description="Implement traffic prioritization and compression",
                    technical_details={
                        'current_utilization': current_performance.bandwidth_utilization_percent,
                        'target_utilization': 70.0,
                        'optimization_methods': ['traffic_prioritization', 'compression', 'caching']
                    },
                    estimated_improvement={'utilization_reduction_percent': 15}
                ))
            
            # Sort recommendations by priority and impact
            recommendations.sort(key=lambda x: (x.priority, -x.impact_score))
            
            # Store recommendations
            self.optimization_history.extend(recommendations)
            await self._store_optimization_recommendations(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return []
    
    async def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time performance dashboard data"""



        try:
            # Get current performance
            current_performance = await self.measure_network_performance()
            
            # Get recent trends
            recent_trends = await self.analyze_performance_trends(timedelta(hours=24))
            
            # Get active alerts
            active_alerts = await self._get_active_performance_alerts()
            
            # Get optimization recommendations
            recommendations = await self.generate_optimization_recommendations(current_performance)
            
            dashboard_data = {
                'current_performance': {
                    'latency_ms': current_performance.latency_ms,
                    'throughput_mbps': current_performance.throughput_mbps,
                    'packet_loss_percent': current_performance.packet_loss_percent,
                    'quality_score': current_performance.quality_score,
                    'active_connections': current_performance.active_connections
                },
                'performance_status': await self._determine_performance_status(current_performance),
                'recent_trends': recent_trends,
                'active_alerts': active_alerts,
                'recommendations': recommendations[:3],  # Top 3 recommendations
                'historical_summary': await self._get_historical_summary(),
                'network_health_score': await self._calculate_network_health_score(),
                'timestamp': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get performance dashboard data: {e}")
            return {}
    
    async def optimize_network_configuration(
        self,
        optimization_strategies: List[OptimizationStrategy]
    ) -> Dict[str, bool]:
        """Apply network optimization configurations"""



        try:
            optimization_results = {}
            
            for strategy in optimization_strategies:
                try:
                    if strategy == OptimizationStrategy.BANDWIDTH_OPTIMIZATION:
                        result = await self._apply_bandwidth_optimization()
                    elif strategy == OptimizationStrategy.LATENCY_REDUCTION:
                        result = await self._apply_latency_optimization()
                    elif strategy == OptimizationStrategy.RELIABILITY_IMPROVEMENT:
                        result = await self._apply_reliability_optimization()
                    elif strategy == OptimizationStrategy.COST_OPTIMIZATION:
                        result = await self._apply_cost_optimization()
                    elif strategy == OptimizationStrategy.SECURITY_ENHANCEMENT:
                        result = await self._apply_security_optimization()
                    else:
                        result = False
                    
                    optimization_results[strategy.value] = result
                    
                except Exception as e:
                    logger.error(f"Failed to apply {strategy.value}: {e}")
                    optimization_results[strategy.value] = False
            
            # Log optimization results
            await self._log_optimization_results(optimization_results)
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize network configuration: {e}")
            return {}
    
    # Private methods
    
    async def _measure_throughput(self) -> Tuple[float, float]:
        """Measure network throughput using speedtest"""



        try:
            if not self.speedtest_client:
                return 0.0, 0.0
            
            # Perform speed test (this may take several seconds)
            download_speed = self.speedtest_client.download() / 1000000  # Convert to Mbps
            upload_speed = self.speedtest_client.upload() / 1000000    # Convert to Mbps
            
            return download_speed, upload_speed
            
        except Exception as e:
            logger.warning(f"Speedtest failed: {e}")
            return 0.0, 0.0
    
    async def _estimate_packet_loss(self, endpoints: List[str]) -> float:
        """Estimate packet loss percentage"""



        try:
            successful_pings = 0
            total_pings = 0
            
            for endpoint in endpoints[:3]:  # Test 3 endpoints
                for _ in range(5):  # 5 pings per endpoint
                    total_pings += 1
                    try:
                        result = ping3.ping(endpoint, timeout=2)
                        if result:
                            successful_pings += 1
                    except Exception:
                        pass
            
            if total_pings == 0:
                return 0.0
            
            packet_loss = ((total_pings - successful_pings) / total_pings) * 100
            return min(packet_loss, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to estimate packet loss: {e}")
            return 0.0
    
    async def _calculate_quality_score(
        self,
        latency: float,
        throughput: float,
        packet_loss: float,
        jitter: float
    ) -> float:
        """Calculate overall network quality score (0-100)"""



        try:
            # Normalize metrics to 0-1 scale
            latency_score = max(0, min(1, (200 - latency) / 200))  # Good latency < 200ms
            throughput_score = min(1, throughput / 100)  # Good throughput > 100 Mbps
            packet_loss_score = max(0, min(1, (5 - packet_loss) / 5))  # Good packet loss < 5%
            jitter_score = max(0, min(1, (50 - jitter) / 50))  # Good jitter < 50ms
            
            # Weighted average
            weights = {
                'latency': 0.3,
                'throughput': 0.3,
                'packet_loss': 0.3,
                'jitter': 0.1
            }
            
            quality_score = (
                latency_score * weights['latency'] +
                throughput_score * weights['throughput'] +
                packet_loss_score * weights['packet_loss'] +
                jitter_score * weights['jitter']
            ) * 100
            
            return round(quality_score, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score: {e}")
            return 0.0
    
    async def _performance_monitoring_loop(self) -> None:
        """Background performance monitoring loop"""
        while True:
            try:
                # Measure performance
                await self.measure_network_performance()
                
                # Wait for next measurement
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Performance monitoring loop error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _optimization_analysis_loop(self) -> None:
        """Background optimization analysis loop"""
        while True:
            try:
                # Run optimization analysis every hour
                await asyncio.sleep(3600)
                
                # Generate recommendations
                await self.generate_optimization_recommendations()
                
                # Check for auto-optimization opportunities
                await self._check_auto_optimization_triggers()
                
            except Exception as e:
                logger.error(f"Optimization analysis loop error: {e}")
                await asyncio.sleep(3600)
    
    async def _alert_monitoring_loop(self) -> None:
        """Background alert monitoring loop"""
        while True:
            try:
                # Check performance thresholds every 5 minutes
                await asyncio.sleep(300)
                
                # Check for threshold violations
                await self._check_performance_thresholds()
                
            except Exception as e:
                logger.error(f"Alert monitoring loop error: {e}")
                await asyncio.sleep(300)
