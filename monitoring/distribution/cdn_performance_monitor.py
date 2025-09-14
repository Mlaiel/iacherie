"""
CDN Performance Monitor - Distribution Module
===========================================

Advanced CDN (Content Delivery Network) performance monitoring system
for optimizing content delivery speed, reliability, and user experience.

Features:
- Real-time CDN performance monitoring
- Multi-provider CDN comparison
- Geographic performance analysis
- Cache hit rate optimization
- Bandwidth usage tracking
- Latency optimization strategies

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class CDNProvider(Enum):
    """Supported CDN providers"""
    CLOUDFLARE = "cloudflare"
    AMAZON_CLOUDFRONT = "amazon_cloudfront"
    GOOGLE_CLOUD_CDN = "google_cloud_cdn"
    AZURE_CDN = "azure_cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"
    STACKPATH = "stackpath"

class MetricType(Enum):
    """CDN performance metric types"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    CACHE_HIT_RATE = "cache_hit_rate"
    BANDWIDTH_USAGE = "bandwidth_usage"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    ORIGIN_REQUESTS = "origin_requests"

class EdgeLocation(Enum):
    """CDN edge location regions"""
    US_EAST = "us_east"
    US_WEST = "us_west"
    EU_CENTRAL = "eu_central"
    EU_WEST = "eu_west"
    ASIA_PACIFIC = "asia_pacific"
    AUSTRALIA = "australia"
    SOUTH_AMERICA = "south_america"
    AFRICA = "africa"

@dataclass
class CDNMetric:
    """Individual CDN performance metric"""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    edge_location: EdgeLocation = EdgeLocation.US_EAST
    metric_type: MetricType = MetricType.RESPONSE_TIME
    value: float = 0.0
    unit: str = "ms"
    timestamp: datetime = field(default_factory=datetime.now)
    content_type: str = "video"
    file_size_mb: float = 0.0

@dataclass
class CachePerformance:
    """Cache performance metrics"""
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    edge_location: EdgeLocation = EdgeLocation.US_EAST
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    cache_size_gb: float = 0.0
    cache_evictions: int = 0
    cache_fills: int = 0
    ttl_average_hours: float = 24.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class BandwidthUsage:
    """Bandwidth usage tracking"""
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    edge_location: EdgeLocation = EdgeLocation.US_EAST
    total_bandwidth_gb: float = 0.0
    peak_bandwidth_mbps: float = 0.0
    average_bandwidth_mbps: float = 0.0
    cost_usd: float = 0.0
    requests_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceAlert:
    """Performance alert for CDN issues"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    edge_location: Optional[EdgeLocation] = None
    metric_type: MetricType = MetricType.RESPONSE_TIME
    severity: str = "medium"  # low, medium, high, critical
    threshold_value: float = 0.0
    actual_value: float = 0.0
    description: str = ""
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class CDNPerformanceMonitor:
    """Main CDN performance monitoring system"""
    
    def __init__(self) -> None:
        self.metrics: List[CDNMetric] = []
        self.cache_performance: List[CachePerformance] = []
        self.bandwidth_usage: List[BandwidthUsage] = []
        self.alerts: List[PerformanceAlert] = []
        self.provider_configs = self._initialize_provider_configs()
        self.performance_thresholds = self._initialize_thresholds()
        self.monitoring_active = False
        
    def _initialize_provider_configs(self) -> Dict[CDNProvider, Dict[str, Any]]:
        """Initialize CDN provider configurations"""
        return {
            CDNProvider.CLOUDFLARE: {
                "edge_locations": [EdgeLocation.US_EAST, EdgeLocation.US_WEST, 
                                 EdgeLocation.EU_CENTRAL, EdgeLocation.ASIA_PACIFIC],
                "api_endpoint": "https://api.cloudflare.com/client/v4",
                "features": ["ddos_protection", "ssl_termination", "image_optimization"],
                "pricing_per_gb": 0.085,
                "cache_ttl_default": 4  # hours
            },
            CDNProvider.AMAZON_CLOUDFRONT: {
                "edge_locations": [EdgeLocation.US_EAST, EdgeLocation.US_WEST, 
                                 EdgeLocation.EU_WEST, EdgeLocation.ASIA_PACIFIC],
                "api_endpoint": "https://cloudfront.amazonaws.com",
                "features": ["lambda_edge", "field_level_encryption", "real_time_logs"],
                "pricing_per_gb": 0.085,
                "cache_ttl_default": 24
            },
            CDNProvider.GOOGLE_CLOUD_CDN: {
                "edge_locations": [EdgeLocation.US_CENTRAL, EdgeLocation.EU_WEST, 
                                 EdgeLocation.ASIA_PACIFIC],
                "api_endpoint": "https://compute.googleapis.com/compute/v1",
                "features": ["cloud_armor", "global_load_balancing", "cdn_interconnect"],
                "pricing_per_gb": 0.08,
                "cache_ttl_default": 12
            }
        }
        
    def _initialize_thresholds(self) -> Dict[MetricType, Dict[str, float]]:
        """Initialize performance alert thresholds"""
        return {
            MetricType.RESPONSE_TIME: {
                "good": 100.0,      # ms
                "warning": 250.0,   # ms
                "critical": 500.0   # ms
            },
            MetricType.CACHE_HIT_RATE: {
                "good": 0.95,       # 95%
                "warning": 0.85,    # 85%
                "critical": 0.70    # 70%
            },
            MetricType.ERROR_RATE: {
                "good": 0.01,       # 1%
                "warning": 0.05,    # 5%
                "critical": 0.10    # 10%
            },
            MetricType.AVAILABILITY: {
                "good": 0.999,      # 99.9%
                "warning": 0.995,   # 99.5%
                "critical": 0.990   # 99.0%
            },
            MetricType.THROUGHPUT: {
                "good": 100.0,      # Mbps
                "warning": 50.0,    # Mbps
                "critical": 10.0    # Mbps
            }
        }
        
    async def start_monitoring(self) -> None:
        """Start CDN performance monitoring"""
        self.monitoring_active = True
        
        # Start monitoring tasks
        monitoring_tasks = [
            self._monitor_response_times(),
            self._monitor_cache_performance(),
            self._monitor_bandwidth_usage(),
            self._monitor_error_rates(),
            self._detect_performance_issues()
        ]
        
        await asyncio.gather(*monitoring_tasks)
        
    async def stop_monitoring(self) -> None:
        """Stop CDN performance monitoring"""
        self.monitoring_active = False
        logger.info("CDN monitoring stopped")
        
    async def _monitor_response_times(self) -> None:
        """Monitor CDN response times across all providers and locations"""
        while self.monitoring_active:
            try:
                for provider in CDNProvider:
                    config = self.provider_configs.get(provider, {})
                    edge_locations = config.get("edge_locations", [EdgeLocation.US_EAST])
                    
                    for location in edge_locations:
                        # Simulate response time measurement
                        response_time = await self._measure_response_time(provider, location)
                        
                        metric = CDNMetric(
                            provider=provider,
                            edge_location=location,
                            metric_type=MetricType.RESPONSE_TIME,
                            value=response_time,
                            unit="ms",
                            content_type="video"
                        )
                        
                        self.metrics.append(metric)
                        
                        # Check for alerts
                        await self._check_response_time_alert(metric)
                        
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring response times: {e}")
                await asyncio.sleep(60)
                
    async def _measure_response_time(self, provider: CDNProvider, location: EdgeLocation) -> float:
        """Measure response time for provider/location (simulated)"""
        import random
        
        # Base response times by provider (simulated)
        base_times = {
            CDNProvider.CLOUDFLARE: 45.0,
            CDNProvider.AMAZON_CLOUDFRONT: 55.0,
            CDNProvider.GOOGLE_CLOUD_CDN: 50.0,
            CDNProvider.AZURE_CDN: 65.0,
            CDNProvider.FASTLY: 40.0
        }
        
        # Location multipliers
        location_factors = {
            EdgeLocation.US_EAST: 1.0,
            EdgeLocation.US_WEST: 1.1,
            EdgeLocation.EU_CENTRAL: 1.3,
            EdgeLocation.ASIA_PACIFIC: 1.5,
            EdgeLocation.AUSTRALIA: 1.8
        }
        
        base_time = base_times.get(provider, 60.0)
        location_factor = location_factors.get(location, 1.0)
        
        # Add some randomness
        variation = random.uniform(0.8, 1.2)
        
        return base_time * location_factor * variation
        
    async def _check_response_time_alert(self, metric -> None: CDNMetric) -> None:
        """Check if response time metric triggers an alert"""
        thresholds = self.performance_thresholds[MetricType.RESPONSE_TIME]
        
        severity = None
        if metric.value > thresholds["critical"]:
            severity = "critical"
        elif metric.value > thresholds["warning"]:
            severity = "high"
        elif metric.value > thresholds["good"]:
            severity = "medium"
            
        if severity:
            alert = PerformanceAlert(
                provider=metric.provider,
                edge_location=metric.edge_location,
                metric_type=metric.metric_type,
                severity=severity,
                threshold_value=thresholds["good"],
                actual_value=metric.value,
                description=f"High response time detected: {metric.value:.1f}ms"
            )
            
            self.alerts.append(alert)
            logger.warning(f"CDN alert: {alert.description}")
            
    async def _monitor_cache_performance(self) -> None:
        """Monitor CDN cache performance"""
        while self.monitoring_active:
            try:
                for provider in CDNProvider:
                    config = self.provider_configs.get(provider, {})
                    edge_locations = config.get("edge_locations", [EdgeLocation.US_EAST])
                    
                    for location in edge_locations:
                        cache_perf = await self._measure_cache_performance(provider, location)
                        self.cache_performance.append(cache_perf)
                        
                        # Check cache hit rate alert
                        await self._check_cache_hit_rate_alert(cache_perf)
                        
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring cache performance: {e}")
                await asyncio.sleep(300)
                
    async def _measure_cache_performance(self, 
                                       provider: CDNProvider, 
                                       location: EdgeLocation) -> CachePerformance:
        """Measure cache performance metrics (simulated)"""
        import random
        
        # Simulate cache metrics
        cache_hit_rate = random.uniform(0.75, 0.98)
        cache_miss_rate = 1.0 - cache_hit_rate
        cache_size_gb = random.uniform(50, 500)
        cache_evictions = random.randint(10, 100)
        cache_fills = random.randint(100, 1000)
        
        return CachePerformance(
            provider=provider,
            edge_location=location,
            cache_hit_rate=cache_hit_rate,
            cache_miss_rate=cache_miss_rate,
            cache_size_gb=cache_size_gb,
            cache_evictions=cache_evictions,
            cache_fills=cache_fills,
            ttl_average_hours=self.provider_configs[provider].get("cache_ttl_default", 24)
        )
        
    async def _check_cache_hit_rate_alert(self, cache_perf -> None: CachePerformance) -> None:
        """Check if cache hit rate triggers an alert"""
        thresholds = self.performance_thresholds[MetricType.CACHE_HIT_RATE]
        
        severity = None
        if cache_perf.cache_hit_rate < thresholds["critical"]:
            severity = "critical"
        elif cache_perf.cache_hit_rate < thresholds["warning"]:
            severity = "high"
        elif cache_perf.cache_hit_rate < thresholds["good"]:
            severity = "medium"
            
        if severity:
            alert = PerformanceAlert(
                provider=cache_perf.provider,
                edge_location=cache_perf.edge_location,
                metric_type=MetricType.CACHE_HIT_RATE,
                severity=severity,
                threshold_value=thresholds["good"],
                actual_value=cache_perf.cache_hit_rate,
                description=f"Low cache hit rate: {cache_perf.cache_hit_rate:.1%}"
            )
            
            self.alerts.append(alert)
            
    async def _monitor_bandwidth_usage(self) -> None:
        """Monitor CDN bandwidth usage"""
        while self.monitoring_active:
            try:
                for provider in CDNProvider:
                    config = self.provider_configs.get(provider, {})
                    edge_locations = config.get("edge_locations", [EdgeLocation.US_EAST])
                    
                    for location in edge_locations:
                        bandwidth = await self._measure_bandwidth_usage(provider, location)
                        self.bandwidth_usage.append(bandwidth)
                        
                await asyncio.sleep(600)  # Monitor every 10 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring bandwidth usage: {e}")
                await asyncio.sleep(600)
                
    async def _measure_bandwidth_usage(self, 
                                     provider: CDNProvider, 
                                     location: EdgeLocation) -> BandwidthUsage:
        """Measure bandwidth usage metrics (simulated)"""
        import random
        
        # Simulate bandwidth metrics
        total_bandwidth_gb = random.uniform(10, 1000)
        peak_bandwidth_mbps = random.uniform(100, 2000)
        average_bandwidth_mbps = peak_bandwidth_mbps * 0.6
        requests_count = random.randint(10000, 1000000)
        
        # Calculate cost based on provider pricing
        pricing_per_gb = self.provider_configs[provider].get("pricing_per_gb", 0.085)
        cost_usd = total_bandwidth_gb * pricing_per_gb
        
        return BandwidthUsage(
            provider=provider,
            edge_location=location,
            total_bandwidth_gb=total_bandwidth_gb,
            peak_bandwidth_mbps=peak_bandwidth_mbps,
            average_bandwidth_mbps=average_bandwidth_mbps,
            cost_usd=cost_usd,
            requests_count=requests_count
        )
        
    async def _monitor_error_rates(self) -> None:
        """Monitor CDN error rates"""
        while self.monitoring_active:
            try:
                for provider in CDNProvider:
                    config = self.provider_configs.get(provider, {})
                    edge_locations = config.get("edge_locations", [EdgeLocation.US_EAST])
                    
                    for location in edge_locations:
                        error_rate = await self._measure_error_rate(provider, location)
                        
                        metric = CDNMetric(
                            provider=provider,
                            edge_location=location,
                            metric_type=MetricType.ERROR_RATE,
                            value=error_rate,
                            unit="percentage"
                        )
                        
                        self.metrics.append(metric)
                        await self._check_error_rate_alert(metric)
                        
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error monitoring error rates: {e}")
                await asyncio.sleep(120)
                
    async def _measure_error_rate(self, provider: CDNProvider, location: EdgeLocation) -> float:
        """Measure error rate for provider/location (simulated)"""
        import random
        
        # Most CDNs have very low error rates
        base_error_rate = random.uniform(0.001, 0.02)  # 0.1% to 2%
        
        # Some providers are more reliable
        reliability_factors = {
            CDNProvider.CLOUDFLARE: 0.8,
            CDNProvider.AMAZON_CLOUDFRONT: 0.9,
            CDNProvider.GOOGLE_CLOUD_CDN: 0.85,
            CDNProvider.AZURE_CDN: 1.0,
            CDNProvider.FASTLY: 0.7
        }
        
        factor = reliability_factors.get(provider, 1.0)
        return base_error_rate * factor
        
    async def _check_error_rate_alert(self, metric -> None: CDNMetric) -> None:
        """Check if error rate triggers an alert"""
        thresholds = self.performance_thresholds[MetricType.ERROR_RATE]
        
        severity = None
        if metric.value > thresholds["critical"]:
            severity = "critical"
        elif metric.value > thresholds["warning"]:
            severity = "high"
        elif metric.value > thresholds["good"]:
            severity = "medium"
            
        if severity:
            alert = PerformanceAlert(
                provider=metric.provider,
                edge_location=metric.edge_location,
                metric_type=metric.metric_type,
                severity=severity,
                threshold_value=thresholds["good"],
                actual_value=metric.value,
                description=f"High error rate detected: {metric.value:.2%}"
            )
            
            self.alerts.append(alert)
            
    async def _detect_performance_issues(self) -> None:
        """Detect performance issues and patterns"""
        while self.monitoring_active:
            try:
                await self._analyze_performance_trends()
                await self._detect_anomalies()
                await self._optimize_cache_strategies()
                
                await asyncio.sleep(900)  # Analyze every 15 minutes
                
            except Exception as e:
                logger.error(f"Error detecting performance issues: {e}")
                await asyncio.sleep(900)
                
    async def _analyze_performance_trends(self) -> None:
        """Analyze performance trends over time"""
        if len(self.metrics) < 10:
            return
            
        # Analyze response time trends by provider
        provider_trends = defaultdict(list)
        
        # Get last hour of data
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        for metric in recent_metrics:
            if metric.metric_type == MetricType.RESPONSE_TIME:
                provider_trends[metric.provider].append(metric.value)
                
        # Detect degrading performance
        for provider, values in provider_trends.items():
            if len(values) >= 5:
                # Check if performance is degrading
                recent_avg = statistics.mean(values[-5:])
                overall_avg = statistics.mean(values)
                
                if recent_avg > overall_avg * 1.5:  # 50% degradation
                    alert = PerformanceAlert(
                        provider=provider,
                        metric_type=MetricType.RESPONSE_TIME,
                        severity="high",
                        threshold_value=overall_avg,
                        actual_value=recent_avg,
                        description=f"Performance degradation detected for {provider.value}"
                    )
                    self.alerts.append(alert)
                    
    async def _detect_anomalies(self) -> None:
        """Detect performance anomalies using statistical analysis"""
        if len(self.metrics) < 50:
            return
            
        # Group metrics by type and provider
        metric_groups = defaultdict(lambda: defaultdict(list))
        
        for metric in self.metrics[-100:]:  # Last 100 measurements
            metric_groups[metric.metric_type][metric.provider].append(metric.value)
            
        # Detect anomalies using standard deviation
        for metric_type, provider_data in metric_groups.items():
            for provider, values in provider_data.items():
                if len(values) >= 10:
                    mean_val = statistics.mean(values)
                    std_dev = statistics.stdev(values)
                    
                    # Check last value for anomaly (3 sigma rule)
                    last_value = values[-1]
                    if abs(last_value - mean_val) > 3 * std_dev:
                        alert = PerformanceAlert(
                            provider=provider,
                            metric_type=metric_type,
                            severity="medium",
                            threshold_value=mean_val + 2 * std_dev,
                            actual_value=last_value,
                            description=f"Performance anomaly detected for {provider.value}"
                        )
                        self.alerts.append(alert)
                        
    async def _optimize_cache_strategies(self) -> None:
        """Optimize cache strategies based on performance data"""
        if not self.cache_performance:
            return
            
        # Analyze cache performance by provider
        provider_cache_stats = defaultdict(list)
        
        for cache_perf in self.cache_performance[-50:]:  # Last 50 measurements
            provider_cache_stats[cache_perf.provider].append(cache_perf.cache_hit_rate)
            
        # Generate optimization recommendations
        for provider, hit_rates in provider_cache_stats.items():
            if len(hit_rates) >= 5:
                avg_hit_rate = statistics.mean(hit_rates)
                
                if avg_hit_rate < 0.85:  # Below 85% hit rate
                    logger.info(f"Cache optimization needed for {provider.value}: {avg_hit_rate:.1%} hit rate")
                    
    def get_performance_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter recent data
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        recent_cache = [c for c in self.cache_performance if c.timestamp > cutoff_time]
        recent_bandwidth = [b for b in self.bandwidth_usage if b.timestamp > cutoff_time]
        recent_alerts = [a for a in self.alerts if a.triggered_at > cutoff_time]
        
        # Calculate provider performance
        provider_performance = {}
        
        for provider in CDNProvider:
            provider_metrics = [m for m in recent_metrics if m.provider == provider]
            
            if provider_metrics:
                response_times = [m.value for m in provider_metrics 
                                if m.metric_type == MetricType.RESPONSE_TIME]
                error_rates = [m.value for m in provider_metrics 
                             if m.metric_type == MetricType.ERROR_RATE]
                
                provider_cache = [c for c in recent_cache if c.provider == provider]
                cache_hit_rates = [c.cache_hit_rate for c in provider_cache]
                
                provider_bandwidth = [b for b in recent_bandwidth if b.provider == provider]
                total_bandwidth = sum(b.total_bandwidth_gb for b in provider_bandwidth)
                total_cost = sum(b.cost_usd for b in provider_bandwidth)
                
                provider_performance[provider.value] = {
                    "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                    "avg_error_rate": statistics.mean(error_rates) if error_rates else 0,
                    "avg_cache_hit_rate": statistics.mean(cache_hit_rates) if cache_hit_rates else 0,
                    "total_bandwidth_gb": total_bandwidth,
                    "total_cost_usd": total_cost,
                    "measurements_count": len(provider_metrics)
                }
                
        # Alert summary
        alert_summary = defaultdict(int)
        for alert in recent_alerts:
            alert_summary[alert.severity] += 1
            
        return {
            "analysis_period_hours": hours_back,
            "total_measurements": len(recent_metrics),
            "total_alerts": len(recent_alerts),
            "alert_breakdown": dict(alert_summary),
            "provider_performance": provider_performance,
            "overall_stats": {
                "avg_response_time_ms": statistics.mean([m.value for m in recent_metrics 
                                                       if m.metric_type == MetricType.RESPONSE_TIME]) if recent_metrics else 0,
                "total_bandwidth_gb": sum(b.total_bandwidth_gb for b in recent_bandwidth),
                "total_cost_usd": sum(b.cost_usd for b in recent_bandwidth)
            }
        }
        
    def get_provider_comparison(self) -> Dict[str, Any]:
        """Get comparative analysis of CDN providers"""
        comparison = {}
        
        for provider in CDNProvider:
            provider_metrics = [m for m in self.metrics if m.provider == provider]
            provider_cache = [c for c in self.cache_performance if c.provider == provider]
            provider_bandwidth = [b for b in self.bandwidth_usage if b.provider == provider]
            
            if provider_metrics:
                response_times = [m.value for m in provider_metrics 
                                if m.metric_type == MetricType.RESPONSE_TIME]
                error_rates = [m.value for m in provider_metrics 
                             if m.metric_type == MetricType.ERROR_RATE]
                
                comparison[provider.value] = {
                    "performance_score": self._calculate_performance_score(
                        response_times, error_rates, provider_cache
                    ),
                    "reliability_score": 1.0 - statistics.mean(error_rates) if error_rates else 1.0,
                    "cost_efficiency": self._calculate_cost_efficiency(provider_bandwidth),
                    "global_coverage": len(self.provider_configs[provider].get("edge_locations", [])),
                    "features": len(self.provider_configs[provider].get("features", []))
                }
                
        return comparison
        
    def _calculate_performance_score(self, response_times: List[float], 
                                   error_rates: List[float], 
                                   cache_data: List[CachePerformance]) -> float:
        """Calculate overall performance score for provider"""
        if not response_times:
            return 0.0
            
        # Response time score (lower is better)
        avg_response_time = statistics.mean(response_times)
        response_score = max(0, 1.0 - (avg_response_time / 1000))  # Normalize to 0-1
        
        # Error rate score (lower is better)
        avg_error_rate = statistics.mean(error_rates) if error_rates else 0
        error_score = max(0, 1.0 - (avg_error_rate * 10))  # Normalize to 0-1
        
        # Cache hit rate score
        cache_hit_rates = [c.cache_hit_rate for c in cache_data]
        cache_score = statistics.mean(cache_hit_rates) if cache_hit_rates else 0.8
        
        # Weighted average
        return (response_score * 0.4 + error_score * 0.3 + cache_score * 0.3)
        
    def _calculate_cost_efficiency(self, bandwidth_data: List[BandwidthUsage]) -> float:
        """Calculate cost efficiency score"""
        if not bandwidth_data:
            return 0.0
            
        total_bandwidth = sum(b.total_bandwidth_gb for b in bandwidth_data)
        total_cost = sum(b.cost_usd for b in bandwidth_data)
        
        if total_cost == 0:
            return 1.0
            
        # Cost per GB (lower is better)
        cost_per_gb = total_cost / total_bandwidth if total_bandwidth > 0 else float('inf')
        
        # Normalize to 0-1 scale (assuming $0.10/GB is baseline)
        return max(0, 1.0 - (cost_per_gb / 0.10))

# Export main classes
__all__ = [
    'CDNPerformanceMonitor',
    'CDNMetric',
    'CachePerformance',
    'BandwidthUsage',
    'PerformanceAlert',
    'CDNProvider',
    'MetricType',
    'EdgeLocation'
]