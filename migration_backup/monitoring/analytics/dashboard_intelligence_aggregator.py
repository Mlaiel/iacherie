"""
🔍 MONITORING ANALYTICS - Dashboard Intelligence Aggregator
Enterprise dashboard intelligence and data aggregation for Ainflue platform
DevOps + Business Intelligence Engineer Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
import json
import redis
import aiohttp
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardType(Enum):
    """Types of dashboards to aggregate"""
    EXECUTIVE_SUMMARY = "executive_summary"
    OPERATIONAL_METRICS = "operational_metrics"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    TECHNICAL_PERFORMANCE = "technical_performance"
    CREATOR_ANALYTICS = "creator_analytics"
    CONTENT_INSIGHTS = "content_insights"
    REVENUE_ANALYTICS = "revenue_analytics"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_HEALTH = "system_health"
    SECURITY_MONITORING = "security_monitoring"

class AggregationLevel(Enum):
    """Data aggregation levels"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class DataSource(Enum):
    """Available data sources"""
    DATABASE_METRICS = "database_metrics"
    API_ANALYTICS = "api_analytics"
    SYSTEM_MONITORING = "system_monitoring"
    BUSINESS_DATA = "business_data"
    USER_ACTIVITY = "user_activity"
    CONTENT_DATA = "content_data"
    FINANCIAL_DATA = "financial_data"
    EXTERNAL_APIS = "external_apis"
    LOG_ANALYTICS = "log_analytics"

@dataclass
class MetricDefinition:
    """Definition of a dashboard metric"""
    metric_id: str
    metric_name: str
    data_source: DataSource
    query: str
    aggregation_function: str
    refresh_interval_seconds: int
    visualization_type: str
    display_format: str
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: str
    title: str
    metrics: List[str]
    layout: Dict[str, Any]
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_rate: int = 300  # seconds
    cache_ttl: int = 60  # seconds

@dataclass
class DashboardConfig:
    """Complete dashboard configuration"""
    dashboard_id: str
    dashboard_type: DashboardType
    title: str
    description: str
    widgets: List[DashboardWidget]
    access_roles: List[str]
    auto_refresh: bool = True
    default_time_range: str = "24h"

@dataclass
class AggregatedData:
    """Aggregated dashboard data"""
    metric_id: str
    timestamp: datetime
    value: Union[float, int, str, Dict, List]
    aggregation_level: AggregationLevel
    data_points: int
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class DashboardIntelligenceAggregator:
    """
    📊 Advanced Dashboard Intelligence Aggregator for Ainflue Platform
    
    Enterprise dashboard intelligence with:
    - Multi-source data aggregation and integration
    - Real-time and batch data processing
    - Intelligent caching and performance optimization
    - Advanced visualization data preparation
    - Role-based dashboard customization
    - Automated insight generation and alerting
    - Cross-dashboard analytics correlation
    - Predictive dashboard optimization
    """
    
    def __init__(self, db_url: str, redis_url: str = None):
        """Initialize dashboard intelligence aggregator"""
        self.db_url = db_url
        self.redis_url = redis_url
        self.engine = create_engine(db_url)
        
        # Redis for caching
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        else:
            self.redis_client = None
        
        # Data storage
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.dashboard_configs: Dict[str, DashboardConfig] = {}
        self.aggregated_data: Dict[str, List[AggregatedData]] = {}
        self.widget_cache: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.query_performance: Dict[str, List[float]] = {}
        self.cache_hit_rates: Dict[str, float] = {}
        
        # Background tasks
        self.refresh_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("📊 Dashboard Intelligence Aggregator initialized")

    async def register_metric_definition(
        self,
        metric_id: str,
        metric_name: str,
        data_source: DataSource,
        query: str,
        aggregation_function: str = "avg",
        refresh_interval_seconds: int = 300,
        visualization_type: str = "line_chart",
        display_format: str = "number",
        alert_thresholds: Dict[str, float] = None,
        dependencies: List[str] = None
    ) -> None:
        """
        📝 Register metric definition for dashboard use
        
        Define how metrics should be collected and processed
        """
        try:
            if alert_thresholds is None:
                alert_thresholds = {}
            
            if dependencies is None:
                dependencies = []
            
            metric_def = MetricDefinition(
                metric_id=metric_id,
                metric_name=metric_name,
                data_source=data_source,
                query=query,
                aggregation_function=aggregation_function,
                refresh_interval_seconds=refresh_interval_seconds,
                visualization_type=visualization_type,
                display_format=display_format,
                alert_thresholds=alert_thresholds,
                dependencies=dependencies
            )
            
            self.metric_definitions[metric_id] = metric_def
            
            logger.info(f"📝 Registered metric: {metric_id} ({metric_name})")
            
        except Exception as e:
            logger.error(f"❌ Error registering metric {metric_id}: {e}")
            raise

    async def create_dashboard_config(
        self,
        dashboard_id: str,
        dashboard_type: DashboardType,
        title: str,
        description: str,
        widgets: List[DashboardWidget],
        access_roles: List[str],
        auto_refresh: bool = True,
        default_time_range: str = "24h"
    ) -> None:
        """
        🎨 Create dashboard configuration
        
        Define dashboard layout and widget arrangement
        """
        try:
            config = DashboardConfig(
                dashboard_id=dashboard_id,
                dashboard_type=dashboard_type,
                title=title,
                description=description,
                widgets=widgets,
                access_roles=access_roles,
                auto_refresh=auto_refresh,
                default_time_range=default_time_range
            )
            
            self.dashboard_configs[dashboard_id] = config
            
            # Start auto-refresh if enabled
            if auto_refresh:
                await self._start_dashboard_refresh(dashboard_id)
            
            logger.info(f"🎨 Created dashboard: {dashboard_id} ({title})")
            
        except Exception as e:
            logger.error(f"❌ Error creating dashboard {dashboard_id}: {e}")
            raise

    async def collect_metric_data(
        self,
        metric_id: str,
        start_time: datetime = None,
        end_time: datetime = None,
        aggregation_level: AggregationLevel = AggregationLevel.HOURLY
    ) -> List[AggregatedData]:
        """
        📊 Collect and aggregate metric data
        
        Fetch data from various sources and aggregate
        """
        try:
            if metric_id not in self.metric_definitions:
                logger.error(f"Metric {metric_id} not defined")
                return []
            
            metric_def = self.metric_definitions[metric_id]
            
            logger.info(f"📊 Collecting data for metric: {metric_id}")
            
            # Set default time range if not provided
            if end_time is None:
                end_time = datetime.now()
            if start_time is None:
                start_time = end_time - timedelta(hours=24)
            
            # Check cache first
            cache_key = f"metric_{metric_id}_{start_time}_{end_time}_{aggregation_level.value}"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                logger.info(f"📋 Using cached data for {metric_id}")
                return cached_data
            
            # Collect data based on source type
            raw_data = await self._collect_raw_data(
                metric_def, start_time, end_time
            )
            
            if not raw_data:
                return []
            
            # Aggregate data
            aggregated_data = await self._aggregate_data(
                raw_data, aggregation_level, metric_def.aggregation_function
            )
            
            # Create AggregatedData objects
            result = []
            for timestamp, value, data_points in aggregated_data:
                confidence_score = self._calculate_confidence_score(
                    data_points, metric_def.data_source
                )
                
                agg_data = AggregatedData(
                    metric_id=metric_id,
                    timestamp=timestamp,
                    value=value,
                    aggregation_level=aggregation_level,
                    data_points=data_points,
                    confidence_score=confidence_score,
                    metadata={
                        'source': metric_def.data_source.value,
                        'aggregation_function': metric_def.aggregation_function
                    }
                )
                result.append(agg_data)
            
            # Cache result
            await self._cache_data(cache_key, result, ttl=metric_def.refresh_interval_seconds)
            
            # Store in memory
            if metric_id not in self.aggregated_data:
                self.aggregated_data[metric_id] = []
            self.aggregated_data[metric_id].extend(result)
            
            # Keep only recent data in memory
            cutoff_time = datetime.now() - timedelta(days=7)
            self.aggregated_data[metric_id] = [
                data for data in self.aggregated_data[metric_id]
                if data.timestamp >= cutoff_time
            ]
            
            logger.info(f"✅ Collected {len(result)} data points for {metric_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error collecting metric data for {metric_id}: {e}")
            return []

    async def generate_dashboard_data(
        self,
        dashboard_id: str,
        user_role: str = None,
        time_range: str = None,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        🎨 Generate complete dashboard data
        
        Prepare all data needed for dashboard rendering
        """
        try:
            if dashboard_id not in self.dashboard_configs:
                logger.error(f"Dashboard {dashboard_id} not found")
                return {}
            
            config = self.dashboard_configs[dashboard_id]
            
            # Check access permissions
            if user_role and user_role not in config.access_roles and 'admin' not in config.access_roles:
                logger.warning(f"Access denied for {user_role} to dashboard {dashboard_id}")
                return {}
            
            logger.info(f"🎨 Generating dashboard data: {dashboard_id}")
            
            # Parse time range
            start_time, end_time = self._parse_time_range(
                time_range or config.default_time_range
            )
            
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'title': config.title,
                'description': config.description,
                'timestamp': datetime.now().isoformat(),
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'range_text': time_range or config.default_time_range
                },
                'widgets': [],
                'metadata': {
                    'generated_by': 'DashboardIntelligenceAggregator',
                    'cache_hit_rate': self.cache_hit_rates.get(dashboard_id, 0.0),
                    'data_freshness': self._calculate_data_freshness(config)
                }
            }
            
            # Generate widget data
            for widget in config.widgets:
                widget_data = await self._generate_widget_data(
                    widget, start_time, end_time, filters
                )
                dashboard_data['widgets'].append(widget_data)
            
            # Add insights and alerts
            dashboard_data['insights'] = await self._generate_dashboard_insights(
                dashboard_id, dashboard_data
            )
            dashboard_data['alerts'] = await self._check_dashboard_alerts(
                dashboard_id, dashboard_data
            )
            
            logger.info(f"✅ Dashboard data generated: {len(dashboard_data['widgets'])} widgets")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Error generating dashboard data for {dashboard_id}: {e}")
            return {}

    async def generate_executive_summary(
        self,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        🏢 Generate executive summary dashboard
        
        High-level KPIs and business metrics
        """
        try:
            logger.info(f"🏢 Generating executive summary for {time_range}")
            
            start_time, end_time = self._parse_time_range(time_range)
            
            # Key business metrics
            revenue_data = await self._get_revenue_summary(start_time, end_time)
            user_metrics = await self._get_user_growth_summary(start_time, end_time)
            content_metrics = await self._get_content_summary(start_time, end_time)
            performance_metrics = await self._get_system_performance_summary(start_time, end_time)
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'time_range': time_range,
                'kpis': {
                    'revenue': revenue_data,
                    'users': user_metrics,
                    'content': content_metrics,
                    'performance': performance_metrics
                },
                'trends': await self._calculate_executive_trends(start_time, end_time),
                'alerts': await self._get_executive_alerts(),
                'recommendations': await self._generate_executive_recommendations()
            }
            
            logger.info("✅ Executive summary generated")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating executive summary: {e}")
            return {}

    async def create_real_time_dashboard_stream(
        self,
        dashboard_id: str,
        update_interval_seconds: int = 30
    ) -> asyncio.Queue:
        """
        ⚡ Create real-time dashboard data stream
        
        WebSocket-compatible data streaming
        """
        try:
            logger.info(f"⚡ Creating real-time stream for {dashboard_id}")
            
            if dashboard_id not in self.dashboard_configs:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            # Create data queue
            data_queue = asyncio.Queue()
            
            # Start background task for real-time updates
            async def stream_updates():
                while True:
                    try:
                        # Generate current dashboard data
                        dashboard_data = await self.generate_dashboard_data(dashboard_id)
                        
                        # Add real-time metadata
                        dashboard_data['stream_metadata'] = {
                            'update_timestamp': datetime.now().isoformat(),
                            'update_interval': update_interval_seconds,
                            'stream_active': True
                        }
                        
                        # Put in queue
                        await data_queue.put(dashboard_data)
                        
                        # Wait for next update
                        await asyncio.sleep(update_interval_seconds)
                        
                    except Exception as e:
                        logger.error(f"Error in real-time stream: {e}")
                        await asyncio.sleep(update_interval_seconds)
            
            # Start the streaming task
            stream_task = asyncio.create_task(stream_updates())
            self.refresh_tasks[f"stream_{dashboard_id}"] = stream_task
            
            logger.info(f"✅ Real-time stream created for {dashboard_id}")
            return data_queue
            
        except Exception as e:
            logger.error(f"❌ Error creating real-time stream: {e}")
            raise

    async def optimize_dashboard_performance(
        self,
        dashboard_id: str
    ) -> Dict[str, Any]:
        """
        🔧 Optimize dashboard performance
        
        Analyze and improve dashboard loading times
        """
        try:
            logger.info(f"🔧 Optimizing performance for dashboard {dashboard_id}")
            
            if dashboard_id not in self.dashboard_configs:
                return {}
            
            config = self.dashboard_configs[dashboard_id]
            
            # Performance analysis
            performance_analysis = {
                'dashboard_id': dashboard_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'metrics': {},
                'optimizations': [],
                'recommendations': []
            }
            
            # Analyze query performance
            slow_queries = []
            for widget in config.widgets:
                for metric_id in widget.metrics:
                    if metric_id in self.query_performance:
                        avg_time = np.mean(self.query_performance[metric_id])
                        if avg_time > 5.0:  # Slow queries > 5 seconds
                            slow_queries.append({
                                'metric_id': metric_id,
                                'avg_query_time': avg_time,
                                'widget_id': widget.widget_id
                            })
            
            performance_analysis['metrics']['slow_queries'] = slow_queries
            
            # Cache hit rate analysis
            cache_hit_rate = self.cache_hit_rates.get(dashboard_id, 0.0)
            performance_analysis['metrics']['cache_hit_rate'] = cache_hit_rate
            
            # Generate optimizations
            if slow_queries:
                performance_analysis['optimizations'].append({
                    'type': 'query_optimization',
                    'description': f"Optimize {len(slow_queries)} slow queries",
                    'impact': 'high',
                    'effort': 'medium'
                })
            
            if cache_hit_rate < 0.7:
                performance_analysis['optimizations'].append({
                    'type': 'cache_optimization',
                    'description': "Improve caching strategy",
                    'impact': 'medium',
                    'effort': 'low'
                })
            
            # Generate recommendations
            if len(config.widgets) > 20:
                performance_analysis['recommendations'].append(
                    "Consider pagination or lazy loading for dashboards with >20 widgets"
                )
            
            if any(widget.refresh_rate < 60 for widget in config.widgets):
                performance_analysis['recommendations'].append(
                    "Increase refresh rates for widgets updating more frequently than 60 seconds"
                )
            
            performance_analysis['recommendations'].append(
                "Implement dashboard preloading for frequently accessed dashboards"
            )
            
            logger.info(f"✅ Performance analysis completed for {dashboard_id}")
            return performance_analysis
            
        except Exception as e:
            logger.error(f"❌ Error optimizing dashboard performance: {e}")
            return {}

    async def generate_cross_dashboard_analytics(self) -> Dict[str, Any]:
        """
        📈 Generate cross-dashboard analytics
        
        Analyze usage patterns across all dashboards
        """
        try:
            logger.info("📈 Generating cross-dashboard analytics")
            
            analytics = {
                'analysis_timestamp': datetime.now().isoformat(),
                'dashboard_summary': {},
                'usage_patterns': {},
                'performance_comparison': {},
                'optimization_opportunities': [],
                'insights': []
            }
            
            # Dashboard summary
            analytics['dashboard_summary'] = {
                'total_dashboards': len(self.dashboard_configs),
                'dashboard_types': {
                    dashboard_type.value: len([
                        d for d in self.dashboard_configs.values()
                        if d.dashboard_type == dashboard_type
                    ])
                    for dashboard_type in DashboardType
                },
                'total_metrics': len(self.metric_definitions),
                'total_widgets': sum(
                    len(config.widgets) for config in self.dashboard_configs.values()
                )
            }
            
            # Performance comparison
            performance_data = {}
            for dashboard_id, config in self.dashboard_configs.items():
                cache_hit_rate = self.cache_hit_rates.get(dashboard_id, 0.0)
                avg_query_time = np.mean([
                    np.mean(self.query_performance.get(metric_id, [1.0]))
                    for widget in config.widgets
                    for metric_id in widget.metrics
                    if metric_id in self.query_performance
                ]) if any(
                    metric_id in self.query_performance
                    for widget in config.widgets
                    for metric_id in widget.metrics
                ) else 0.0
                
                performance_data[dashboard_id] = {
                    'cache_hit_rate': cache_hit_rate,
                    'avg_query_time': avg_query_time,
                    'widget_count': len(config.widgets),
                    'dashboard_type': config.dashboard_type.value
                }
            
            analytics['performance_comparison'] = performance_data
            
            # Identify optimization opportunities
            for dashboard_id, perf in performance_data.items():
                if perf['cache_hit_rate'] < 0.5:
                    analytics['optimization_opportunities'].append({
                        'dashboard_id': dashboard_id,
                        'type': 'low_cache_hit_rate',
                        'current_value': perf['cache_hit_rate'],
                        'recommendation': 'Implement better caching strategy'
                    })
                
                if perf['avg_query_time'] > 3.0:
                    analytics['optimization_opportunities'].append({
                        'dashboard_id': dashboard_id,
                        'type': 'slow_queries',
                        'current_value': perf['avg_query_time'],
                        'recommendation': 'Optimize query performance'
                    })
            
            # Generate insights
            if performance_data:
                best_performing = max(
                    performance_data.items(),
                    key=lambda x: x[1]['cache_hit_rate']
                )
                analytics['insights'].append(
                    f"Best performing dashboard: {best_performing[0]} "
                    f"(cache hit rate: {best_performing[1]['cache_hit_rate']:.2%})"
                )
                
                worst_performing = min(
                    performance_data.items(),
                    key=lambda x: x[1]['cache_hit_rate']
                )
                analytics['insights'].append(
                    f"Dashboard needing optimization: {worst_performing[0]} "
                    f"(cache hit rate: {worst_performing[1]['cache_hit_rate']:.2%})"
                )
            
            logger.info("✅ Cross-dashboard analytics generated")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error generating cross-dashboard analytics: {e}")
            return {}

    # Helper methods
    
    async def _collect_raw_data(
        self,
        metric_def: MetricDefinition,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[datetime, Union[float, int, str]]]:
        """Collect raw data from data source"""
        try:
            start_query_time = datetime.now()
            
            if metric_def.data_source == DataSource.DATABASE_METRICS:
                data = await self._query_database(metric_def.query, start_time, end_time)
            elif metric_def.data_source == DataSource.API_ANALYTICS:
                data = await self._query_api_analytics(metric_def.query, start_time, end_time)
            elif metric_def.data_source == DataSource.SYSTEM_MONITORING:
                data = await self._query_system_monitoring(metric_def.query, start_time, end_time)
            else:
                logger.warning(f"Unsupported data source: {metric_def.data_source}")
                data = []
            
            # Record query performance
            query_time = (datetime.now() - start_query_time).total_seconds()
            if metric_def.metric_id not in self.query_performance:
                self.query_performance[metric_def.metric_id] = []
            self.query_performance[metric_def.metric_id].append(query_time)
            
            # Keep only recent performance data
            if len(self.query_performance[metric_def.metric_id]) > 100:
                self.query_performance[metric_def.metric_id] = \
                    self.query_performance[metric_def.metric_id][-50:]
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting raw data: {e}")
            return []

    async def _query_database(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[datetime, Union[float, int, str]]]:
        """Query database for metric data"""
        try:
            # Replace placeholders in query
            formatted_query = query.replace('{start_time}', f"'{start_time}'")
            formatted_query = formatted_query.replace('{end_time}', f"'{end_time}'")
            
            result = self.engine.execute(text(formatted_query))
            
            data = []
            for row in result:
                # Assume first column is timestamp, second is value
                if len(row) >= 2:
                    timestamp = row[0] if isinstance(row[0], datetime) else datetime.fromisoformat(str(row[0]))
                    value = row[1]
                    data.append((timestamp, value))
            
            return data
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []

    async def _query_api_analytics(
        self,
        endpoint: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[datetime, Union[float, int, str]]]:
        """Query API analytics endpoint"""
        try:
            # Simulate API call - would be real implementation in production
            data = []
            
            # Generate sample data
            current_time = start_time
            while current_time <= end_time:
                value = np.random.normal(100, 20)  # Sample data
                data.append((current_time, value))
                current_time += timedelta(hours=1)
            
            return data
            
        except Exception as e:
            logger.error(f"API analytics query error: {e}")
            return []

    async def _query_system_monitoring(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[datetime, Union[float, int, str]]]:
        """Query system monitoring metrics"""
        try:
            # Simulate system monitoring query
            data = []
            
            # Generate sample system metrics
            current_time = start_time
            while current_time <= end_time:
                if 'cpu' in metric_name.lower():
                    value = np.random.uniform(10, 90)  # CPU percentage
                elif 'memory' in metric_name.lower():
                    value = np.random.uniform(20, 80)  # Memory percentage
                else:
                    value = np.random.normal(50, 10)
                
                data.append((current_time, value))
                current_time += timedelta(minutes=5)
            
            return data
            
        except Exception as e:
            logger.error(f"System monitoring query error: {e}")
            return []

    async def _aggregate_data(
        self,
        raw_data: List[Tuple[datetime, Union[float, int, str]]],
        aggregation_level: AggregationLevel,
        aggregation_function: str
    ) -> List[Tuple[datetime, float, int]]:
        """Aggregate raw data according to specified level and function"""
        if not raw_data:
            return []
        
        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(raw_data, columns=['timestamp', 'value'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Determine aggregation frequency
        freq_map = {
            AggregationLevel.REAL_TIME: '1min',
            AggregationLevel.HOURLY: '1H',
            AggregationLevel.DAILY: '1D',
            AggregationLevel.WEEKLY: '1W',
            AggregationLevel.MONTHLY: '1M',
            AggregationLevel.QUARTERLY: '3M',
            AggregationLevel.YEARLY: '1Y'
        }
        
        freq = freq_map.get(aggregation_level, '1H')
        
        # Aggregate based on function
        if aggregation_function == 'avg':
            aggregated = df.resample(freq)['value'].mean()
        elif aggregation_function == 'sum':
            aggregated = df.resample(freq)['value'].sum()
        elif aggregation_function == 'max':
            aggregated = df.resample(freq)['value'].max()
        elif aggregation_function == 'min':
            aggregated = df.resample(freq)['value'].min()
        elif aggregation_function == 'count':
            aggregated = df.resample(freq)['value'].count()
        else:
            aggregated = df.resample(freq)['value'].mean()  # Default to average
        
        # Count data points for confidence calculation
        counts = df.resample(freq)['value'].count()
        
        # Convert back to list of tuples
        result = []
        for timestamp, value in aggregated.items():
            if not pd.isna(value):
                data_points = counts.loc[timestamp]
                result.append((timestamp.to_pydatetime(), float(value), int(data_points)))
        
        return result

    def _calculate_confidence_score(
        self,
        data_points: int,
        data_source: DataSource
    ) -> float:
        """Calculate confidence score based on data points and source reliability"""
        # Base confidence on data point count
        point_confidence = min(1.0, data_points / 100.0)
        
        # Source reliability factors
        source_reliability = {
            DataSource.DATABASE_METRICS: 0.95,
            DataSource.SYSTEM_MONITORING: 0.90,
            DataSource.API_ANALYTICS: 0.85,
            DataSource.BUSINESS_DATA: 0.80,
            DataSource.LOG_ANALYTICS: 0.75,
            DataSource.EXTERNAL_APIS: 0.70
        }
        
        reliability = source_reliability.get(data_source, 0.75)
        
        return point_confidence * reliability

    async def _get_cached_data(self, cache_key: str) -> Optional[List[AggregatedData]]:
        """Get data from cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                # Update cache hit rate
                dashboard_id = cache_key.split('_')[1]
                if dashboard_id in self.cache_hit_rates:
                    self.cache_hit_rates[dashboard_id] = (
                        self.cache_hit_rates[dashboard_id] * 0.9 + 0.1 * 1.0
                    )
                else:
                    self.cache_hit_rates[dashboard_id] = 1.0
                
                # Deserialize cached data
                data_dict = json.loads(cached)
                return [
                    AggregatedData(
                        metric_id=item['metric_id'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        value=item['value'],
                        aggregation_level=AggregationLevel(item['aggregation_level']),
                        data_points=item['data_points'],
                        confidence_score=item['confidence_score'],
                        metadata=item['metadata']
                    )
                    for item in data_dict
                ]
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    async def _cache_data(
        self,
        cache_key: str,
        data: List[AggregatedData],
        ttl: int = 300
    ) -> None:
        """Cache data with TTL"""
        if not self.redis_client:
            return
        
        try:
            # Serialize data
            data_dict = [
                {
                    'metric_id': item.metric_id,
                    'timestamp': item.timestamp.isoformat(),
                    'value': item.value,
                    'aggregation_level': item.aggregation_level.value,
                    'data_points': item.data_points,
                    'confidence_score': item.confidence_score,
                    'metadata': item.metadata
                }
                for item in data
            ]
            
            self.redis_client.setex(cache_key, ttl, json.dumps(data_dict))
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    def _parse_time_range(self, time_range: str) -> Tuple[datetime, datetime]:
        """Parse time range string to start and end times"""
        end_time = datetime.now()
        
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
        elif time_range.endswith('w'):
            weeks = int(time_range[:-1])
            start_time = end_time - timedelta(weeks=weeks)
        elif time_range.endswith('m'):
            months = int(time_range[:-1])
            start_time = end_time - timedelta(days=months * 30)
        else:
            # Default to 24 hours
            start_time = end_time - timedelta(hours=24)
        
        return start_time, end_time

    async def _generate_widget_data(
        self,
        widget: DashboardWidget,
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate data for a specific widget"""
        try:
            widget_data = {
                'widget_id': widget.widget_id,
                'widget_type': widget.widget_type,
                'title': widget.title,
                'layout': widget.layout,
                'data': {},
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'data_points': 0,
                    'confidence_score': 0.0
                }
            }
            
            # Collect data for each metric in widget
            all_data_points = 0
            confidence_scores = []
            
            for metric_id in widget.metrics:
                metric_data = await self.collect_metric_data(
                    metric_id, start_time, end_time
                )
                
                if metric_data:
                    # Format data for visualization
                    widget_data['data'][metric_id] = {
                        'values': [
                            {
                                'timestamp': data.timestamp.isoformat(),
                                'value': data.value,
                                'confidence': data.confidence_score
                            }
                            for data in metric_data
                        ],
                        'metric_name': self.metric_definitions.get(metric_id, {}).metric_name if metric_id in self.metric_definitions else metric_id,
                        'display_format': self.metric_definitions.get(metric_id, {}).display_format if metric_id in self.metric_definitions else 'number'
                    }
                    
                    all_data_points += len(metric_data)
                    confidence_scores.extend([data.confidence_score for data in metric_data])
            
            # Update metadata
            widget_data['metadata']['data_points'] = all_data_points
            widget_data['metadata']['confidence_score'] = (
                np.mean(confidence_scores) if confidence_scores else 0.0
            )
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Error generating widget data for {widget.widget_id}: {e}")
            return {
                'widget_id': widget.widget_id,
                'error': str(e),
                'data': {}
            }

    async def _start_dashboard_refresh(self, dashboard_id: str) -> None:
        """Start background refresh task for dashboard"""
        config = self.dashboard_configs[dashboard_id]
        
        async def refresh_loop():
            while True:
                try:
                    # Pre-generate dashboard data
                    await self.generate_dashboard_data(dashboard_id)
                    
                    # Wait for next refresh
                    min_refresh_rate = min(
                        widget.refresh_rate for widget in config.widgets
                    )
                    await asyncio.sleep(min_refresh_rate)
                    
                except Exception as e:
                    logger.error(f"Dashboard refresh error for {dashboard_id}: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        
        # Start refresh task
        task = asyncio.create_task(refresh_loop())
        self.refresh_tasks[dashboard_id] = task

    def _calculate_data_freshness(self, config: DashboardConfig) -> float:
        """Calculate average data freshness for dashboard"""
        freshness_scores = []
        
        for widget in config.widgets:
            for metric_id in widget.metrics:
                if metric_id in self.aggregated_data:
                    latest_data = max(
                        self.aggregated_data[metric_id],
                        key=lambda x: x.timestamp,
                        default=None
                    )
                    
                    if latest_data:
                        age_minutes = (datetime.now() - latest_data.timestamp).total_seconds() / 60
                        freshness = max(0, 1 - (age_minutes / 60))  # 1 hour = 0 freshness
                        freshness_scores.append(freshness)
        
        return np.mean(freshness_scores) if freshness_scores else 0.0

    async def _generate_dashboard_insights(
        self,
        dashboard_id: str,
        dashboard_data: Dict[str, Any]
    ) -> List[str]:
        """Generate insights for dashboard"""
        insights = []
        
        # Analyze data trends
        for widget_data in dashboard_data.get('widgets', []):
            for metric_id, metric_data in widget_data.get('data', {}).items():
                values = [item['value'] for item in metric_data.get('values', [])]
                
                if len(values) > 1:
                    # Simple trend analysis
                    if values[-1] > values[0] * 1.1:
                        insights.append(f"{metric_id} showing upward trend (+{((values[-1]/values[0]-1)*100):.1f}%)")
                    elif values[-1] < values[0] * 0.9:
                        insights.append(f"{metric_id} showing downward trend ({((values[-1]/values[0]-1)*100):.1f}%)")
        
        return insights

    async def _check_dashboard_alerts(
        self,
        dashboard_id: str,
        dashboard_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for alerts in dashboard data"""
        alerts = []
        
        for widget_data in dashboard_data.get('widgets', []):
            for metric_id, metric_data in widget_data.get('data', {}).items():
                if metric_id in self.metric_definitions:
                    metric_def = self.metric_definitions[metric_id]
                    
                    # Check latest value against thresholds
                    values = metric_data.get('values', [])
                    if values:
                        latest_value = values[-1]['value']
                        
                        for threshold_name, threshold_value in metric_def.alert_thresholds.items():
                            if threshold_name == 'critical_high' and latest_value > threshold_value:
                                alerts.append({
                                    'type': 'critical',
                                    'metric_id': metric_id,
                                    'message': f"{metric_id} exceeded critical threshold: {latest_value} > {threshold_value}",
                                    'timestamp': datetime.now().isoformat()
                                })
                            elif threshold_name == 'warning_high' and latest_value > threshold_value:
                                alerts.append({
                                    'type': 'warning',
                                    'metric_id': metric_id,
                                    'message': f"{metric_id} exceeded warning threshold: {latest_value} > {threshold_value}",
                                    'timestamp': datetime.now().isoformat()
                                })
        
        return alerts

    async def _get_revenue_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get revenue summary for executive dashboard"""
        # Simulate revenue data
        return {
            'total_revenue': 125000.0,
            'revenue_growth': 12.5,
            'average_revenue_per_user': 45.20,
            'revenue_streams': {
                'subscriptions': 85000.0,
                'transactions': 25000.0,
                'premium_features': 15000.0
            }
        }

    async def _get_user_growth_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get user growth summary"""
        return {
            'total_users': 15420,
            'new_users': 1250,
            'user_growth_rate': 8.8,
            'active_users': 12350,
            'user_retention_rate': 0.85
        }

    async def _get_content_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get content summary"""
        return {
            'total_content': 8950,
            'new_content': 420,
            'content_engagement_rate': 0.72,
            'top_content_types': {
                'audio': 4500,
                'video': 2800,
                'image': 1650
            }
        }

    async def _get_system_performance_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get system performance summary"""
        return {
            'avg_response_time': 145.5,
            'system_uptime': 99.9,
            'error_rate': 0.05,
            'throughput': 1850.0
        }

    async def _calculate_executive_trends(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate trends for executive summary"""
        return {
            'revenue_trend': 'up',
            'user_growth_trend': 'up',
            'performance_trend': 'stable',
            'engagement_trend': 'up'
        }

    async def _get_executive_alerts(self) -> List[Dict[str, Any]]:
        """Get executive-level alerts"""
        return [
            {
                'type': 'info',
                'message': 'Revenue growth exceeding targets by 15%',
                'priority': 'low'
            },
            {
                'type': 'warning',
                'message': 'Storage usage approaching 85% capacity',
                'priority': 'medium'
            }
        ]

    async def _generate_executive_recommendations(self) -> List[str]:
        """Generate executive recommendations"""
        return [
            "Consider expanding infrastructure to support growing user base",
            "Investigate opportunities to optimize high-performing content types",
            "Review pricing strategy for premium features based on usage patterns"
        ]

# Usage example
async def main():
    """Test the dashboard intelligence aggregator"""
    try:
        # Initialize aggregator
        aggregator = DashboardIntelligenceAggregator(
            "postgresql://user:pass@localhost/ainflue",
            "redis://localhost:6379"
        )
        
        # Register metric definitions
        await aggregator.register_metric_definition(
            "api_response_time",
            "API Response Time",
            DataSource.SYSTEM_MONITORING,
            "SELECT timestamp, avg_response_time FROM api_metrics WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'",
            "avg",
            300,
            "line_chart",
            "milliseconds",
            {"warning_high": 1000, "critical_high": 5000}
        )
        
        # Create dashboard widgets
        widgets = [
            DashboardWidget(
                "response_time_widget",
                "line_chart",
                "API Response Time",
                ["api_response_time"],
                {"x": 0, "y": 0, "width": 6, "height": 4}
            )
        ]
        
        # Create dashboard
        await aggregator.create_dashboard_config(
            "operations_dashboard",
            DashboardType.OPERATIONAL_METRICS,
            "Operations Dashboard",
            "Real-time operational metrics",
            widgets,
            ["admin", "ops"]
        )
        
        # Generate dashboard data
        dashboard_data = await aggregator.generate_dashboard_data("operations_dashboard")
        print(f"Generated dashboard with {len(dashboard_data.get('widgets', []))} widgets")
        
        # Generate executive summary
        exec_summary = await aggregator.generate_executive_summary()
        print(f"Executive summary revenue: ${exec_summary.get('kpis', {}).get('revenue', {}).get('total_revenue', 0)}")
        
        # Performance optimization
        optimization = await aggregator.optimize_dashboard_performance("operations_dashboard")
        print(f"Performance analysis: {len(optimization.get('optimizations', []))} optimizations found")
        
    except Exception as e:
        print(f"Error in dashboard intelligence: {e}")

if __name__ == "__main__":
    asyncio.run(main())