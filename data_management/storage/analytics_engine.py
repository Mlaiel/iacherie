"""📊 Storage Analytics Engine - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/data_management/storage/analytics_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

Advanced analytics engine for storage insights, usage patterns,
and performance optimization for content creators.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.
"""from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import time

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of storage metrics"""    USAGE = "usage"
    PERFORMANCE = "performance"
    COST = "cost"
    ACCESS_PATTERN = "access_pattern"
    CONTENT_ANALYSIS = "content_analysis"
    TREND = "trend"
    PREDICTION = "prediction"

class TimeWindow(Enum):
    """Time windows for analytics"""    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class StorageMetric:
    """Storage metric data point"""    metric_id: str
    metric_type: MetricType
    timestamp: datetime
    value: Union[int, float, Dict[str, Any]]
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsReport:
    """Analytics report structure"""    report_id: str
    report_type: str
    generated_at: datetime
    time_window: TimeWindow
    data: Dict[str, Any]
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)

class StorageAnalyticsEngine:
    """    Advanced analytics engine for storage insights and optimization.
    
    Features:
    - Real-time storage metrics collection
    - Usage pattern analysis and prediction
    - Cost optimization analytics
    - Performance monitoring and optimization
    - Content lifecycle insights
    - Creator-specific analytics
    - Automated reporting and alerts
    """    
    def __init__(self, config: Dict[str, Any]):
        """Initialize analytics engine"""        self.config = config
        self.metrics_buffer: List[StorageMetric] = []
        self.reports_cache: Dict[str, AnalyticsReport] = {}
        
        # Storage manager reference
        self.storage_manager = None
        
        # Analytics data store
        self.metrics_store: Dict[str, List[StorageMetric]] = defaultdict(list)
        
        # Real-time statistics
        self.real_time_stats = {
            'current_storage_size': 0,
            'current_file_count': 0,
            'hourly_operations': 0,
            'avg_response_time': 0.0,
            'cache_hit_ratio': 0.0
        }
        
        # Trend analysis cache
        self.trend_cache: Dict[str, Dict[str, Any]] = {}
        
        # Performance baselines
        self.performance_baselines = {
            'response_time_p95': 2.0,  # 2 seconds
            'cache_hit_ratio_target': 0.85,  # 85%
            'storage_efficiency_target': 0.75  # 75%
        }
        
        logger.info("StorageAnalyticsEngine initialized")
    
    async def collect_metric(
        self,
        metric_type: MetricType,
        value: Union[int, float, Dict[str, Any]],
        dimensions: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Collect a storage metric"""        
        try:
            metric = StorageMetric(
                metric_id=f"{metric_type.value}_{int(time.time())}",
                metric_type=metric_type,
                timestamp=datetime.now(),
                value=value,
                dimensions=dimensions or {},
                metadata=metadata or {}
            )
            
            # Add to buffer and store
            self.metrics_buffer.append(metric)
            self.metrics_store[metric_type.value].append(metric)
            
            # Update real-time stats
            await self._update_real_time_stats(metric)
            
            # Flush buffer if it gets too large
            if len(self.metrics_buffer) > 1000:
                await self._flush_metrics_buffer()
                
        except Exception as e:
            logger.error(f"Failed to collect metric: {str(e)}")
    
    async def generate_usage_report(
        self,
        time_window: TimeWindow = TimeWindow.DAY,
        creator_type: Optional[str] = None
    ) -> AnalyticsReport:
        """Generate comprehensive usage analytics report"""        
        try:
            report_id = f"usage_{time_window.value}_{int(time.time())}"
            
            # Calculate time range
            end_time = datetime.now()
            start_time = self._calculate_start_time(end_time, time_window)
            
            # Collect usage metrics
            usage_data = await self._analyze_usage_patterns(start_time, end_time, creator_type)
            
            # Generate insights
            insights = await self._generate_usage_insights(usage_data, time_window)
            
            # Generate recommendations
            recommendations = await self._generate_usage_recommendations(usage_data)
            
            # Create charts data
            charts = await self._create_usage_charts(usage_data, time_window)
            
            report = AnalyticsReport(
                report_id=report_id,
                report_type="usage_analytics",
                generated_at=datetime.now(),
                time_window=time_window,
                data=usage_data,
                insights=insights,
                recommendations=recommendations,
                charts=charts
            )
            
            # Cache report
            self.reports_cache[report_id] = report
            
            logger.info(f"Generated usage report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate usage report: {str(e)}")
            raise
    
    async def generate_performance_report(
        self,
        time_window: TimeWindow = TimeWindow.DAY
    ) -> AnalyticsReport:
        """Generate performance analytics report"""        
        try:
            report_id = f"performance_{time_window.value}_{int(time.time())}"
            
            # Calculate time range
            end_time = datetime.now()
            start_time = self._calculate_start_time(end_time, time_window)
            
            # Collect performance metrics
            performance_data = await self._analyze_performance_metrics(start_time, end_time)
            
            # Generate insights
            insights = await self._generate_performance_insights(performance_data)
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(performance_data)
            
            # Create charts data
            charts = await self._create_performance_charts(performance_data, time_window)
            
            report = AnalyticsReport(
                report_id=report_id,
                report_type="performance_analytics",
                generated_at=datetime.now(),
                time_window=time_window,
                data=performance_data,
                insights=insights,
                recommendations=recommendations,
                charts=charts
            )
            
            # Cache report
            self.reports_cache[report_id] = report
            
            logger.info(f"Generated performance report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")
            raise
    
    async def generate_cost_report(
        self,
        time_window: TimeWindow = TimeWindow.MONTH
    ) -> AnalyticsReport:
        """Generate cost analytics report"""        
        try:
            report_id = f"cost_{time_window.value}_{int(time.time())}"
            
            # Calculate time range
            end_time = datetime.now()
            start_time = self._calculate_start_time(end_time, time_window)
            
            # Collect cost metrics
            cost_data = await self._analyze_cost_metrics(start_time, end_time)
            
            # Generate insights
            insights = await self._generate_cost_insights(cost_data)
            
            # Generate recommendations
            recommendations = await self._generate_cost_recommendations(cost_data)
            
            # Create charts data
            charts = await self._create_cost_charts(cost_data, time_window)
            
            report = AnalyticsReport(
                report_id=report_id,
                report_type="cost_analytics",
                generated_at=datetime.now(),
                time_window=time_window,
                data=cost_data,
                insights=insights,
                recommendations=recommendations,
                charts=charts
            )
            
            # Cache report
            self.reports_cache[report_id] = report
            
            logger.info(f"Generated cost report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate cost report: {str(e)}")
            raise
    
    async def analyze_content_lifecycle(
        self,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze content lifecycle patterns"""        
        try:
            if not self.storage_manager:
                raise Exception("Storage manager not available")
            
            # Get all files for analysis
            all_files = await self.storage_manager.list_content()
            
            if content_type:
                all_files = [f for f in all_files if f.get('content_type') == content_type]
            
            lifecycle_analysis = {
                'total_files': len(all_files),
                'age_distribution': {},
                'access_patterns': {},
                'tier_migration_patterns': {},
                'lifecycle_stages': {},
                'optimization_opportunities': []
            }
            
            # Analyze age distribution
            age_buckets = defaultdict(int)
            access_buckets = defaultdict(int)
            tier_distribution = defaultdict(int)
            
            for file_info in all_files:
                # Age analysis
                created_at = file_info.get('metadata', {}).get('created_at')
                if created_at:
                    created_date = datetime.fromisoformat(created_at)
                    age_days = (datetime.now() - created_date).days
                    
                    if age_days < 7:
                        age_buckets['0-7_days'] += 1
                    elif age_days < 30:
                        age_buckets['7-30_days'] += 1
                    elif age_days < 90:
                        age_buckets['30-90_days'] += 1
                    elif age_days < 365:
                        age_buckets['90-365_days'] += 1
                    else:
                        age_buckets['365+_days'] += 1
                
                # Access pattern analysis
                access_count = file_info.get('metadata', {}).get('access_count', 0)
                last_accessed = file_info.get('metadata', {}).get('last_accessed')
                
                if access_count == 0:
                    access_buckets['never_accessed'] += 1
                elif access_count < 5:
                    access_buckets['low_access'] += 1
                elif access_count < 20:
                    access_buckets['medium_access'] += 1
                else:
                    access_buckets['high_access'] += 1
                
                # Tier distribution
                tier = file_info.get('tier', 'unknown')
                tier_distribution[tier] += 1
            
            lifecycle_analysis['age_distribution'] = dict(age_buckets)
            lifecycle_analysis['access_patterns'] = dict(access_buckets)
            lifecycle_analysis['tier_migration_patterns'] = dict(tier_distribution)
            
            # Identify optimization opportunities
            if age_buckets['365+_days'] > 0:
                lifecycle_analysis['optimization_opportunities'].append({
                    'type': 'archival',
                    'description': f"{age_buckets['365+_days']} files are over 1 year old and could be archived",
                    'potential_files': age_buckets['365+_days']
                })
            
            if access_buckets['never_accessed'] > 10:
                lifecycle_analysis['optimization_opportunities'].append({
                    'type': 'cleanup',
                    'description': f"{access_buckets['never_accessed']} files have never been accessed",
                    'potential_files': access_buckets['never_accessed']
                })
            
            return lifecycle_analysis
            
        except Exception as e:
            logger.error(f"Content lifecycle analysis failed: {str(e)}")
            return {}
    
    async def predict_storage_growth(
        self,
        prediction_days: int = 30
    ) -> Dict[str, Any]:
        """Predict storage growth using trend analysis"""        
        try:
            # Get historical usage data
            usage_metrics = self.metrics_store.get(MetricType.USAGE.value, [])
            
            if len(usage_metrics) < 7:  # Need at least a week of data
                return {
                    'error': 'Insufficient historical data for prediction',
                    'required_days': 7,
                    'available_days': len(usage_metrics)
                }
            
            # Extract time series data
            timestamps = []
            storage_sizes = []
            file_counts = []
            
            for metric in usage_metrics[-168:]:  # Last week (hourly data)
                timestamps.append(metric.timestamp)
                if isinstance(metric.value, dict):
                    storage_sizes.append(metric.value.get('total_size', 0))
                    file_counts.append(metric.value.get('file_count', 0))
                else:
                    storage_sizes.append(float(metric.value))
                    file_counts.append(0)
            
            # Calculate growth trends
            storage_growth_rate = self._calculate_growth_rate(storage_sizes)
            file_count_growth_rate = self._calculate_growth_rate(file_counts)
            
            # Make predictions
            current_storage = storage_sizes[-1] if storage_sizes else 0
            current_files = file_counts[-1] if file_counts else 0
            
            predicted_storage = current_storage * (1 + storage_growth_rate) ** prediction_days
            predicted_files = current_files * (1 + file_count_growth_rate) ** prediction_days
            
            prediction = {
                'prediction_period_days': prediction_days,
                'current_metrics': {
                    'storage_size_gb': current_storage / (1024**3),
                    'file_count': current_files
                },
                'predicted_metrics': {
                    'storage_size_gb': predicted_storage / (1024**3),
                    'file_count': int(predicted_files)
                },
                'growth_rates': {
                    'daily_storage_growth_rate': storage_growth_rate,
                    'daily_file_growth_rate': file_count_growth_rate
                },
                'confidence': self._calculate_prediction_confidence(storage_sizes),
                'trends': {
                    'storage_trend': 'increasing' if storage_growth_rate > 0 else 'decreasing',
                    'files_trend': 'increasing' if file_count_growth_rate > 0 else 'decreasing'
                }
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Storage growth prediction failed: {str(e)}")
            return {'error': str(e)}
    
    async def analyze_creator_patterns(
        self,
        creator_type: str,
        time_window: TimeWindow = TimeWindow.MONTH
    ) -> Dict[str, Any]:
        """Analyze storage patterns for specific creator type"""        
        try:
            if not self.storage_manager:
                raise Exception("Storage manager not available")
            
            # Get files for specific creator type
            all_files = await self.storage_manager.list_content()
            creator_files = [
                f for f in all_files 
                if f.get('metadata', {}).get('creator_type') == creator_type
            ]
            
            analysis = {
                'creator_type': creator_type,
                'total_files': len(creator_files),
                'content_distribution': {},
                'usage_patterns': {},
                'storage_efficiency': {},
                'recommendations': []
            }
            
            if not creator_files:
                return analysis
            
            # Analyze content type distribution
            content_types = Counter(f.get('content_type', 'unknown') for f in creator_files)
            analysis['content_distribution'] = dict(content_types)
            
            # Analyze file sizes
            file_sizes = [f.get('file_size', 0) for f in creator_files]
            total_size = sum(file_sizes)
            avg_size = statistics.mean(file_sizes) if file_sizes else 0
            
            analysis['usage_patterns'] = {
                'total_size_gb': total_size / (1024**3),
                'average_file_size_mb': avg_size / (1024**2),
                'largest_file_mb': max(file_sizes) / (1024**2) if file_sizes else 0,
                'smallest_file_mb': min(file_sizes) / (1024**2) if file_sizes else 0
            }
            
            # Analyze access patterns
            access_counts = [f.get('metadata', {}).get('access_count', 0) for f in creator_files]
            if access_counts:
                analysis['usage_patterns']['average_access_count'] = statistics.mean(access_counts)
                analysis['usage_patterns']['max_access_count'] = max(access_counts)
            
            # Calculate storage efficiency
            hot_files = len([f for f in creator_files if f.get('tier') == 'hot'])
            warm_files = len([f for f in creator_files if f.get('tier') == 'warm'])
            cold_files = len([f for f in creator_files if f.get('tier') == 'cold'])
            
            analysis['storage_efficiency'] = {
                'hot_tier_percentage': (hot_files / len(creator_files)) * 100,
                'warm_tier_percentage': (warm_files / len(creator_files)) * 100,
                'cold_tier_percentage': (cold_files / len(creator_files)) * 100,
                'tier_distribution_score': self._calculate_tier_efficiency_score(hot_files, warm_files, cold_files)
            }
            
            # Generate creator-specific recommendations
            if analysis['storage_efficiency']['hot_tier_percentage'] > 60:
                analysis['recommendations'].append(
                    "Consider migrating older content to warm/cold tiers to optimize costs"
                )
            
            if analysis['usage_patterns']['average_file_size_mb'] > 100:
                analysis['recommendations'].append(
                    "Large file sizes detected - consider enabling compression for media files"
                )
            
            if content_types.get('audio', 0) > content_types.get('fingerprint', 0) * 2:
                analysis['recommendations'].append(
                    "Audio content exceeds fingerprint ratio - ensure all content is properly protected"
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Creator pattern analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def generate_optimization_insights(self) -> Dict[str, Any]:
        """Generate comprehensive optimization insights"""        
        try:
            insights = {
                'performance_insights': {},
                'cost_insights': {},
                'efficiency_insights': {},
                'security_insights': {},
                'recommendations': []
            }
            
            # Performance insights
            performance_metrics = self.metrics_store.get(MetricType.PERFORMANCE.value, [])
            if performance_metrics:
                recent_metrics = performance_metrics[-24:]  # Last 24 hours
                response_times = [
                    m.value.get('response_time', 0) for m in recent_metrics 
                    if isinstance(m.value, dict)
                ]
                
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                    p95_response_time = np.percentile(response_times, 95)
                    
                    insights['performance_insights'] = {
                        'avg_response_time': avg_response_time,
                        'p95_response_time': p95_response_time,
                        'performance_score': self._calculate_performance_score(avg_response_time, p95_response_time)
                    }
                    
                    if p95_response_time > self.performance_baselines['response_time_p95']:
                        insights['recommendations'].append(
                            f"Response time P95 ({p95_response_time:.2f}s) exceeds baseline - consider caching optimization"
                        )
            
            # Cost insights
            if self.storage_manager:
                stats = await self.storage_manager.get_storage_statistics()
                total_size = stats.get('total_size_bytes', 0)
                
                estimated_monthly_cost = self._estimate_monthly_cost(total_size)
                
                insights['cost_insights'] = {
                    'estimated_monthly_cost': estimated_monthly_cost,
                    'cost_per_gb': estimated_monthly_cost / (total_size / (1024**3)) if total_size > 0 else 0,
                    'optimization_potential': self._calculate_cost_optimization_potential()
                }
            
            # Efficiency insights
            cache_hit_ratio = self.real_time_stats.get('cache_hit_ratio', 0)
            insights['efficiency_insights'] = {
                'cache_efficiency': cache_hit_ratio,
                'storage_utilization': self._calculate_storage_utilization(),
                'tier_efficiency': self._calculate_overall_tier_efficiency()
            }
            
            if cache_hit_ratio < self.performance_baselines['cache_hit_ratio_target']:
                insights['recommendations'].append(
                    f"Cache hit ratio ({cache_hit_ratio:.1%}) below target - review caching strategies"
                )
            
            # Security insights
            insights['security_insights'] = await self._analyze_security_metrics()
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate optimization insights: {str(e)}")
            return {'error': str(e)}
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""        
        try:
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'current_stats': self.real_time_stats.copy(),
                'recent_activity': await self._get_recent_activity(),
                'alerts': await self._get_active_alerts(),
                'performance_indicators': await self._get_performance_indicators(),
                'trend_indicators': await self._get_trend_indicators()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get real-time dashboard: {str(e)}")
            return {'error': str(e)}
    
    # Private implementation methods
    
    async def _update_real_time_stats(self, metric: StorageMetric) -> None:
        """Update real-time statistics from new metric"""        
        try:
            if metric.metric_type == MetricType.USAGE:
                if isinstance(metric.value, dict):
                    self.real_time_stats['current_storage_size'] = metric.value.get('total_size', 0)
                    self.real_time_stats['current_file_count'] = metric.value.get('file_count', 0)
            
            elif metric.metric_type == MetricType.PERFORMANCE:
                if isinstance(metric.value, dict):
                    response_time = metric.value.get('response_time', 0)
                    if response_time > 0:
                        # Update rolling average
                        current_avg = self.real_time_stats['avg_response_time']
                        self.real_time_stats['avg_response_time'] = (current_avg * 0.9) + (response_time * 0.1)
                    
                    cache_hit_ratio = metric.value.get('cache_hit_ratio', 0)
                    if cache_hit_ratio > 0:
                        self.real_time_stats['cache_hit_ratio'] = cache_hit_ratio
                        
        except Exception as e:
            logger.warning(f"Failed to update real-time stats: {str(e)}")
    
    async def _flush_metrics_buffer(self) -> None:
        """Flush metrics buffer to persistent storage"""        
        try:
            # In a real implementation, this would write to a database
            logger.info(f"Flushed {len(self.metrics_buffer)} metrics to storage")
            self.metrics_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush metrics buffer: {str(e)}")
    
    def _calculate_start_time(self, end_time: datetime, time_window: TimeWindow) -> datetime:
        """Calculate start time based on time window"""        
        if time_window == TimeWindow.HOUR:
            return end_time - timedelta(hours=1)
        elif time_window == TimeWindow.DAY:
            return end_time - timedelta(days=1)
        elif time_window == TimeWindow.WEEK:
            return end_time - timedelta(weeks=1)
        elif time_window == TimeWindow.MONTH:
            return end_time - timedelta(days=30)
        elif time_window == TimeWindow.QUARTER:
            return end_time - timedelta(days=90)
        elif time_window == TimeWindow.YEAR:
            return end_time - timedelta(days=365)
        else:
            return end_time - timedelta(days=1)
    
    async def _analyze_usage_patterns(
        self,
        start_time: datetime,
        end_time: datetime,
        creator_type: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze usage patterns within time window"""        
        usage_data = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'storage_growth': {},
            'file_operations': {},
            'content_distribution': {},
            'access_patterns': {},
            'tier_utilization': {}
        }
        
        try:
            # Get relevant metrics
            usage_metrics = [
                m for m in self.metrics_store.get(MetricType.USAGE.value, [])
                if start_time <= m.timestamp <= end_time
            ]
            
            if not usage_metrics:
                return usage_data
            
            # Analyze storage growth
            storage_sizes = []
            file_counts = []
            
            for metric in usage_metrics:
                if isinstance(metric.value, dict):
                    storage_sizes.append(metric.value.get('total_size', 0))
                    file_counts.append(metric.value.get('file_count', 0))
            
            if storage_sizes:
                usage_data['storage_growth'] = {
                    'start_size_gb': storage_sizes[0] / (1024**3),
                    'end_size_gb': storage_sizes[-1] / (1024**3),
                    'growth_gb': (storage_sizes[-1] - storage_sizes[0]) / (1024**3),
                    'growth_percentage': ((storage_sizes[-1] - storage_sizes[0]) / storage_sizes[0] * 100) if storage_sizes[0] > 0 else 0
                }
            
            if file_counts:
                usage_data['file_operations'] = {
                    'start_count': file_counts[0],
                    'end_count': file_counts[-1],
                    'net_files_added': file_counts[-1] - file_counts[0],
                    'growth_percentage': ((file_counts[-1] - file_counts[0]) / file_counts[0] * 100) if file_counts[0] > 0 else 0
                }
            
        except Exception as e:
            logger.error(f"Usage pattern analysis failed: {str(e)}")
        
        return usage_data
    
    async def _analyze_performance_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze performance metrics within time window"""        
        performance_data = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'response_times': {},
            'throughput': {},
            'error_rates': {},
            'cache_performance': {}
        }
        
        try:
            # Get performance metrics
            perf_metrics = [
                m for m in self.metrics_store.get(MetricType.PERFORMANCE.value, [])
                if start_time <= m.timestamp <= end_time
            ]
            
            if not perf_metrics:
                return performance_data
            
            response_times = []
            cache_hit_ratios = []
            error_counts = []
            
            for metric in perf_metrics:
                if isinstance(metric.value, dict):
                    if 'response_time' in metric.value:
                        response_times.append(metric.value['response_time'])
                    if 'cache_hit_ratio' in metric.value:
                        cache_hit_ratios.append(metric.value['cache_hit_ratio'])
                    if 'error_count' in metric.value:
                        error_counts.append(metric.value['error_count'])
            
            # Analyze response times
            if response_times:
                performance_data['response_times'] = {
                    'average': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'p95': np.percentile(response_times, 95),
                    'p99': np.percentile(response_times, 99),
                    'min': min(response_times),
                    'max': max(response_times)
                }
            
            # Analyze cache performance
            if cache_hit_ratios:
                performance_data['cache_performance'] = {
                    'average_hit_ratio': statistics.mean(cache_hit_ratios),
                    'min_hit_ratio': min(cache_hit_ratios),
                    'max_hit_ratio': max(cache_hit_ratios)
                }
            
            # Analyze error rates
            if error_counts:
                total_errors = sum(error_counts)
                performance_data['error_rates'] = {
                    'total_errors': total_errors,
                    'average_errors_per_hour': total_errors / max(1, len(error_counts))
                }
            
        except Exception as e:
            logger.error(f"Performance metrics analysis failed: {str(e)}")
        
        return performance_data
    
    async def _analyze_cost_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze cost metrics within time window"""        
        cost_data = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'storage_costs': {},
            'operation_costs': {},
            'tier_costs': {},
            'optimization_potential': {}
        }
        
        try:
            # Get cost metrics
            cost_metrics = [
                m for m in self.metrics_store.get(MetricType.COST.value, [])
                if start_time <= m.timestamp <= end_time
            ]
            
            if self.storage_manager:
                stats = await self.storage_manager.get_storage_statistics()
                total_size = stats.get('total_size_bytes', 0)
                
                # Estimate current costs
                monthly_storage_cost = self._estimate_monthly_cost(total_size)
                
                cost_data['storage_costs'] = {
                    'current_monthly_estimate': monthly_storage_cost,
                    'cost_per_gb': monthly_storage_cost / (total_size / (1024**3)) if total_size > 0 else 0
                }
                
                # Analyze tier costs
                tier_usage = stats.get('provider_stats', {})
                cost_data['tier_costs'] = self._calculate_tier_costs(tier_usage)
                
                # Calculate optimization potential
                cost_data['optimization_potential'] = self._calculate_cost_optimization_potential()
            
        except Exception as e:
            logger.error(f"Cost metrics analysis failed: {str(e)}")
        
        return cost_data
    
    # Insight generation methods
    
    async def _generate_usage_insights(
        self,
        usage_data: Dict[str, Any],
        time_window: TimeWindow
    ) -> List[str]:
        """Generate insights from usage data"""        
        insights = []
        
        try:
            storage_growth = usage_data.get('storage_growth', {})
            growth_percentage = storage_growth.get('growth_percentage', 0)
            
            if growth_percentage > 50:
                insights.append(f"High storage growth ({growth_percentage:.1f}%) detected in the last {time_window.value}")
            elif growth_percentage < 0:
                insights.append(f"Storage usage decreased by {abs(growth_percentage):.1f}% - check for cleanup activities")
            
            file_ops = usage_data.get('file_operations', {})
            net_files = file_ops.get('net_files_added', 0)
            
            if net_files > 1000:
                insights.append(f"High file creation activity: {net_files} new files added")
            elif net_files < 0:
                insights.append(f"Net file deletion: {abs(net_files)} files removed")
            
        except Exception as e:
            logger.warning(f"Failed to generate usage insights: {str(e)}")
        
        return insights
    
    async def _generate_performance_insights(self, performance_data: Dict[str, Any]) -> List[str]:
        """Generate insights from performance data"""        
        insights = []
        
        try:
            response_times = performance_data.get('response_times', {})
            avg_response = response_times.get('average', 0)
            p95_response = response_times.get('p95', 0)
            
            if avg_response > 1.0:
                insights.append(f"Average response time ({avg_response:.2f}s) is above recommended threshold")
            
            if p95_response > 2.0:
                insights.append(f"95th percentile response time ({p95_response:.2f}s) indicates performance issues")
            
            cache_perf = performance_data.get('cache_performance', {})
            avg_hit_ratio = cache_perf.get('average_hit_ratio', 0)
            
            if avg_hit_ratio < 0.8:
                insights.append(f"Cache hit ratio ({avg_hit_ratio:.1%}) is below optimal level")
            
            error_rates = performance_data.get('error_rates', {})
            total_errors = error_rates.get('total_errors', 0)
            
            if total_errors > 10:
                insights.append(f"Elevated error count detected: {total_errors} errors")
            
        except Exception as e:
            logger.warning(f"Failed to generate performance insights: {str(e)}")
        
        return insights
    
    async def _generate_cost_insights(self, cost_data: Dict[str, Any]) -> List[str]:
        """Generate insights from cost data"""        
        insights = []
        
        try:
            storage_costs = cost_data.get('storage_costs', {})
            monthly_cost = storage_costs.get('current_monthly_estimate', 0)
            cost_per_gb = storage_costs.get('cost_per_gb', 0)
            
            if cost_per_gb > 0.05:  # $0.05/GB threshold
                insights.append(f"Storage cost per GB (${cost_per_gb:.3f}) is above industry average")
            
            optimization_potential = cost_data.get('optimization_potential', {})
            potential_savings = optimization_potential.get('monthly_savings', 0)
            
            if potential_savings > monthly_cost * 0.1:  # 10% savings potential
                insights.append(f"Significant cost optimization potential identified: ${potential_savings:.2f}/month")
            
        except Exception as e:
            logger.warning(f"Failed to generate cost insights: {str(e)}")
        
        return insights
    
    # Recommendation generation methods
    
    async def _generate_usage_recommendations(self, usage_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations from usage analysis"""        
        recommendations = []
        
        try:
            storage_growth = usage_data.get('storage_growth', {})
            growth_percentage = storage_growth.get('growth_percentage', 0)
            
            if growth_percentage > 100:
                recommendations.append("Consider implementing automated archival policies for old content")
            
            if growth_percentage > 50:
                recommendations.append("Monitor storage growth closely and consider tier optimization")
            
        except Exception as e:
            logger.warning(f"Failed to generate usage recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_performance_recommendations(self, performance_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations from performance analysis"""        
        recommendations = []
        
        try:
            response_times = performance_data.get('response_times', {})
            avg_response = response_times.get('average', 0)
            
            if avg_response > 1.0:
                recommendations.append("Optimize caching strategies to improve response times")
            
            cache_perf = performance_data.get('cache_performance', {})
            avg_hit_ratio = cache_perf.get('average_hit_ratio', 0)
            
            if avg_hit_ratio < 0.8:
                recommendations.append("Review cache TTL settings and cache key strategies")
            
        except Exception as e:
            logger.warning(f"Failed to generate performance recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_cost_recommendations(self, cost_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations from cost analysis"""        
        recommendations = []
        
        try:
            optimization_potential = cost_data.get('optimization_potential', {})
            potential_savings = optimization_potential.get('monthly_savings', 0)
            
            if potential_savings > 10:  # $10/month threshold
                recommendations.append("Implement tier migration policies to reduce storage costs")
            
            tier_costs = cost_data.get('tier_costs', {})
            hot_tier_percentage = tier_costs.get('hot_tier_percentage', 0)
            
            if hot_tier_percentage > 60:
                recommendations.append("Move infrequently accessed content to lower-cost tiers")
            
        except Exception as e:
            logger.warning(f"Failed to generate cost recommendations: {str(e)}")
        
        return recommendations
    
    # Chart creation methods
    
    async def _create_usage_charts(
        self,
        usage_data: Dict[str, Any],
        time_window: TimeWindow
    ) -> List[Dict[str, Any]]:
        """Create chart data for usage analytics"""        
        charts = []
        
        try:
            # Storage growth chart
            storage_growth = usage_data.get('storage_growth', {})
            if storage_growth:
                charts.append({
                    'type': 'line',
                    'title': f'Storage Growth - Last {time_window.value.title()}',
                    'data': {
                        'labels': ['Start', 'End'],
                        'datasets': [{
                            'label': 'Storage Size (GB)',
                            'data': [
                                storage_growth.get('start_size_gb', 0),
                                storage_growth.get('end_size_gb', 0)
                            ]
                        }]
                    }
                })
            
            # File operations chart
            file_ops = usage_data.get('file_operations', {})
            if file_ops:
                charts.append({
                    'type': 'bar',
                    'title': 'File Operations',
                    'data': {
                        'labels': ['Files Added'],
                        'datasets': [{
                            'label': 'Count',
                            'data': [file_ops.get('net_files_added', 0)]
                        }]
                    }
                })
            
        except Exception as e:
            logger.warning(f"Failed to create usage charts: {str(e)}")
        
        return charts
    
    async def _create_performance_charts(
        self,
        performance_data: Dict[str, Any],
        time_window: TimeWindow
    ) -> List[Dict[str, Any]]:
        """Create chart data for performance analytics"""        
        charts = []
        
        try:
            # Response time chart
            response_times = performance_data.get('response_times', {})
            if response_times:
                charts.append({
                    'type': 'bar',
                    'title': 'Response Time Distribution',
                    'data': {
                        'labels': ['Average', 'Median', 'P95', 'P99'],
                        'datasets': [{
                            'label': 'Response Time (seconds)',
                            'data': [
                                response_times.get('average', 0),
                                response_times.get('median', 0),
                                response_times.get('p95', 0),
                                response_times.get('p99', 0)
                            ]
                        }]
                    }
                })
            
        except Exception as e:
            logger.warning(f"Failed to create performance charts: {str(e)}")
        
        return charts
    
    async def _create_cost_charts(
        self,
        cost_data: Dict[str, Any],
        time_window: TimeWindow
    ) -> List[Dict[str, Any]]:
        """Create chart data for cost analytics"""        
        charts = []
        
        try:
            # Cost breakdown chart
            tier_costs = cost_data.get('tier_costs', {})
            if tier_costs:
                charts.append({
                    'type': 'pie',
                    'title': 'Storage Cost by Tier',
                    'data': {
                        'labels': list(tier_costs.keys()),
                        'datasets': [{
                            'data': list(tier_costs.values())
                        }]
                    }
                })
            
        except Exception as e:
            logger.warning(f"Failed to create cost charts: {str(e)}")
        
        return charts
    
    # Helper calculation methods
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate daily growth rate from time series"""        
        if len(values) < 2:
            return 0.0
        
        # Calculate compound daily growth rate
        start_value = values[0]
        end_value = values[-1]
        periods = len(values) - 1
        
        if start_value <= 0 or periods <= 0:
            return 0.0
        
        growth_rate = (end_value / start_value) ** (1 / periods) - 1
        return growth_rate
    
    def _calculate_prediction_confidence(self, values: List[float]) -> float:
        """Calculate confidence score for predictions"""        
        if len(values) < 3:
            return 0.0
        
        # Calculate coefficient of variation
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        if mean_val == 0:
            return 0.0
        
        cv = std_val / mean_val
        confidence = max(0, 1 - cv)  # Lower variation = higher confidence
        
        return min(1.0, confidence)
    
    def _calculate_performance_score(self, avg_response: float, p95_response: float) -> float:
        """Calculate overall performance score"""        
        # Score based on response time performance
        avg_score = max(0, 1 - (avg_response / 2.0))  # 2s baseline
        p95_score = max(0, 1 - (p95_response / 5.0))   # 5s baseline
        
        return (avg_score + p95_score) / 2
    
    def _estimate_monthly_cost(self, total_size_bytes: int) -> float:
        """Estimate monthly storage cost"""        
        size_gb = total_size_bytes / (1024**3)
        
        # Simplified cost model (example rates)
        cost_per_gb_per_month = {
            'hot': 0.10,
            'warm': 0.05,
            'cold': 0.02,
            'archive': 0.01
        }
        
        # Assume 40% hot, 35% warm, 20% cold, 5% archive
        estimated_cost = (
            size_gb * 0.40 * cost_per_gb_per_month['hot'] +
            size_gb * 0.35 * cost_per_gb_per_month['warm'] +
            size_gb * 0.20 * cost_per_gb_per_month['cold'] +
            size_gb * 0.05 * cost_per_gb_per_month['archive']
        )
        
        return estimated_cost
    
    def _calculate_tier_costs(self, tier_usage: Dict[str, Any]) -> Dict[str, float]:
        """Calculate costs by storage tier"""        
        tier_costs = {}
        
        for tier, usage_data in tier_usage.items():
            if isinstance(usage_data, dict):
                size_bytes = usage_data.get('size_bytes', 0)
                size_gb = size_bytes / (1024**3)
                
                # Example cost rates
                rates = {'hot': 0.10, 'warm': 0.05, 'cold': 0.02, 'archive': 0.01}
                rate = rates.get(tier, 0.05)
                
                tier_costs[tier] = size_gb * rate
        
        return tier_costs
    
    def _calculate_cost_optimization_potential(self) -> Dict[str, Any]:
        """Calculate potential cost optimizations"""        
        return {
            'monthly_savings': 15.50,  # Example value
            'optimization_score': 0.75,
            'recommendations_count': 3
        }
    
    def _calculate_storage_utilization(self) -> float:
        """Calculate storage utilization efficiency"""        return 0.78  # Example value
    
    def _calculate_overall_tier_efficiency(self) -> float:
        """Calculate overall tier distribution efficiency"""        return 0.82  # Example value
    
    def _calculate_tier_efficiency_score(self, hot: int, warm: int, cold: int) -> float:
        """Calculate tier efficiency score"""        
        total = hot + warm + cold
        if total == 0:
            return 0.0
        
        # Ideal distribution: 30% hot, 50% warm, 20% cold
        hot_ratio = hot / total
        warm_ratio = warm / total
        cold_ratio = cold / total
        
        hot_score = 1 - abs(hot_ratio - 0.30)
        warm_score = 1 - abs(warm_ratio - 0.50)
        cold_score = 1 - abs(cold_ratio - 0.20)
        
        return (hot_score + warm_score + cold_score) / 3
    
    async def _analyze_security_metrics(self) -> Dict[str, Any]:
        """Analyze security-related metrics"""        
        return {
            'encryption_coverage': 0.95,  # Example value
            'access_control_score': 0.88,
            'audit_compliance': 0.92
        }
    
    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent storage activity"""        
        # Get last 10 metrics
        recent_metrics = self.metrics_buffer[-10:] if self.metrics_buffer else []
        
        activity = []
        for metric in recent_metrics:
            activity.append({
                'timestamp': metric.timestamp.isoformat(),
                'type': metric.metric_type.value,
                'summary': self._summarize_metric(metric)
            })
        
        return activity
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""        
        alerts = []
        
        # Check performance thresholds
        if self.real_time_stats['avg_response_time'] > 2.0:
            alerts.append({
                'type': 'performance',
                'severity': 'warning',
                'message': f"High response time: {self.real_time_stats['avg_response_time']:.2f}s"
            })
        
        if self.real_time_stats['cache_hit_ratio'] < 0.8:
            alerts.append({
                'type': 'performance',
                'severity': 'info',
                'message': f"Low cache hit ratio: {self.real_time_stats['cache_hit_ratio']:.1%}"
            })
        
        return alerts
    
    async def _get_performance_indicators(self) -> Dict[str, Any]:
        """Get key performance indicators"""        
        return {
            'response_time_status': 'good' if self.real_time_stats['avg_response_time'] < 1.0 else 'warning',
            'cache_efficiency_status': 'good' if self.real_time_stats['cache_hit_ratio'] > 0.85 else 'warning',
            'storage_growth_status': 'normal',  # Would be calculated from trends
            'error_rate_status': 'good'
        }
    
    async def _get_trend_indicators(self) -> Dict[str, Any]:
        """Get trend indicators"""        
        return {
            'storage_trend': 'increasing',
            'performance_trend': 'stable',
            'cost_trend': 'optimizing',
            'efficiency_trend': 'improving'
        }
    
    def _summarize_metric(self, metric: StorageMetric) -> str:
        """Create a summary of a metric"""        
        if metric.metric_type == MetricType.USAGE:
            return f"Storage usage update"
        elif metric.metric_type == MetricType.PERFORMANCE:
            return f"Performance measurement"
        elif metric.metric_type == MetricType.COST:
            return f"Cost analysis"
        else:
            return f"{metric.metric_type.value} metric"

# Export main class
__all__ = ['StorageAnalyticsEngine', 'StorageMetric', 'AnalyticsReport', 'MetricType', 'TimeWindow']
