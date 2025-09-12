"""{{service_name}} Analytics Service Template for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Backend Senior Role: Enterprise analytics service with comprehensive data processing
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID
from enum import Enum
import json
from decimal import Decimal
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

from fastapi import BackgroundTasks
from sqlalchemy import text, func, select, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from core.database import get_session
from core.config import get_settings
from utils.exceptions import ServiceError, ValidationError
from utils.cache import CacheManager
from utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class AnalyticsError(ServiceError):
    """Analytics service specific error"""
    pass


class MetricType(str, Enum):
    """Types of metrics that can be collected"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    RATIO = "ratio"
    RATE = "rate"
    DISTRIBUTION = "distribution"


class TimeGranularity(str, Enum):
    """Time granularities for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class AggregationType(str, Enum):
    """Aggregation types for data processing"""
    SUM = "sum"
    COUNT = "count"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    STDDEV = "stddev"
    VARIANCE = "variance"
    DISTINCT_COUNT = "distinct_count"


@dataclass
class AnalyticsQuery:
    """Analytics query configuration"""
    metric_name: str
    metric_type: MetricType
    dimensions: List[str]
    filters: Dict[str, Any]
    date_range: Tuple[datetime, datetime]
    granularity: TimeGranularity
    aggregations: List[AggregationType]
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass 
class AnalyticsResult:
    """Analytics query result"""
    query: AnalyticsQuery
    data: List[Dict[str, Any]]
    total_count: int
    execution_time: float
    cached: bool
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'query': self.query.to_dict(),
            'data': self.data,
            'total_count': self.total_count,
            'execution_time': self.execution_time,
            'cached': self.cached,
            'metadata': self.metadata
        }


class DataProcessor:
    """Data processing utilities for analytics
    
    Provides enterprise-grade data processing with:
    - Statistical calculations
    - Time series analysis
    - Data aggregation
    - Anomaly detection
    - Trend analysis
    - Performance optimization
    """
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        """Calculate comprehensive statistics"""
        if not data:
            return {}
        
        data_array = np.array(data)
        
        return {
            'count': len(data),
            'sum': float(np.sum(data_array)),
            'mean': float(np.mean(data_array)),
            'median': float(np.median(data_array)),
            'min': float(np.min(data_array)),
            'max': float(np.max(data_array)),
            'std': float(np.std(data_array)),
            'variance': float(np.var(data_array)),
            'q25': float(np.percentile(data_array, 25)),
            'q75': float(np.percentile(data_array, 75)),
            'iqr': float(np.percentile(data_array, 75) - np.percentile(data_array, 25)),
            'skewness': float(pd.Series(data).skew()),
            'kurtosis': float(pd.Series(data).kurtosis())
        }
    
    @staticmethod
    def detect_anomalies(
        data: List[float],
        method: str = 'zscore',
        threshold: float = 3.0
    ) -> List[int]:
        """Detect anomalies in data"""
        if not data or len(data) < 3:
            return []
        
        data_array = np.array(data)
        anomaly_indices = []
        
        if method == 'zscore':
            z_scores = np.abs((data_array - np.mean(data_array)) / np.std(data_array))
            anomaly_indices = np.where(z_scores > threshold)[0].tolist()
            
        elif method == 'iqr':
            q1 = np.percentile(data_array, 25)
            q3 = np.percentile(data_array, 75)
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            anomaly_indices = np.where(
                (data_array < lower_bound) | (data_array > upper_bound)
            )[0].tolist()
            
        elif method == 'isolation_forest':
            # Requires scikit-learn
            try:
                from sklearn.ensemble import IsolationForest
                data_reshaped = data_array.reshape(-1, 1)
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(data_reshaped)
                anomaly_indices = np.where(outliers == -1)[0].tolist()
            except ImportError:
                logger.warning("scikit-learn not available, falling back to z-score method")
                return DataProcessor.detect_anomalies(data, 'zscore', threshold)
        
        return anomaly_indices
    
    @staticmethod
    def calculate_trend(data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Calculate trend analysis"""
        if len(data) < 2:
            return {'trend': 'insufficient_data'}
        
        # Convert to pandas DataFrame for easier analysis
        df = pd.DataFrame(data, columns=['date', 'value'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate linear regression
        x = np.arange(len(df))
        y = df['value'].values
        
        # Linear regression using numpy
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate correlation coefficient
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine trend direction
        if abs(slope) < 0.001:  # Very small slope
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'increasing'
        else:
            trend_direction = 'decreasing'
        
        # Calculate trend strength
        if abs(correlation) > 0.8:
            trend_strength = 'strong'
        elif abs(correlation) > 0.5:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        # Calculate percentage change
        if len(df) >= 2:
            first_value = df['value'].iloc[0]
            last_value = df['value'].iloc[-1]
            if first_value != 0:
                pct_change = ((last_value - first_value) / first_value) * 100
            else:
                pct_change = 0
        else:
            pct_change = 0
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'slope': slope,
            'correlation': correlation,
            'percentage_change': pct_change,
            'data_points': len(df),
            'start_date': df['date'].iloc[0].isoformat(),
            'end_date': df['date'].iloc[-1].isoformat(),
            'start_value': df['value'].iloc[0],
            'end_value': df['value'].iloc[-1]
        }
    
    @staticmethod
    def group_by_time(
        data: List[Tuple[datetime, Any]],
        granularity: TimeGranularity
    ) -> Dict[str, List[Any]]:
        """Group data by time granularity"""
        if not data:
            return {}
        
        df = pd.DataFrame(data, columns=['timestamp', 'value'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Define grouping frequency
        freq_map = {
            TimeGranularity.MINUTE: 'T',
            TimeGranularity.HOUR: 'H',
            TimeGranularity.DAY: 'D',
            TimeGranularity.WEEK: 'W',
            TimeGranularity.MONTH: 'M',
            TimeGranularity.QUARTER: 'Q',
            TimeGranularity.YEAR: 'Y'
        }
        
        freq = freq_map.get(granularity, 'D')
        
        # Group by time period
        grouped = df.groupby(pd.Grouper(key='timestamp', freq=freq))
        
        result = {}
        for period, group in grouped:
            if not group.empty:
                period_key = period.strftime('%Y-%m-%d %H:%M:%S')
                result[period_key] = group['value'].tolist()
        
        return result


class QueryBuilder:
    """SQL query builder for analytics
    
    Builds optimized SQL queries for various analytics operations
    """
    
    def __init__(self, model_class):
        self.model = model_class
    
    def build_aggregation_query(
        self,
        query_config: AnalyticsQuery
    ) -> str:
        """Build aggregation query based on configuration"""
        
        # Base table
        table_name = self.model.__tablename__
        
        # Select clauses
        select_clauses = []
        
        # Add dimensions
        for dimension in query_config.dimensions:
            select_clauses.append(f'"{dimension}"')
        
        # Add aggregations
        for agg in query_config.aggregations:
            if agg == AggregationType.COUNT:
                select_clauses.append('COUNT(*) as count')
            elif agg == AggregationType.SUM:
                select_clauses.append(f'SUM("{query_config.metric_name}") as sum')
            elif agg == AggregationType.AVG:
                select_clauses.append(f'AVG("{query_config.metric_name}") as avg')
            elif agg == AggregationType.MIN:
                select_clauses.append(f'MIN("{query_config.metric_name}") as min')
            elif agg == AggregationType.MAX:
                select_clauses.append(f'MAX("{query_config.metric_name}") as max')
            elif agg == AggregationType.STDDEV:
                select_clauses.append(f'STDDEV("{query_config.metric_name}") as stddev')
            elif agg == AggregationType.VARIANCE:
                select_clauses.append(f'VARIANCE("{query_config.metric_name}") as variance')
            elif agg == AggregationType.DISTINCT_COUNT:
                select_clauses.append(f'COUNT(DISTINCT "{query_config.metric_name}") as distinct_count')
        
        # Add time grouping
        if query_config.granularity != TimeGranularity.DAY:
            time_format = self._get_time_format(query_config.granularity)
            select_clauses.append(f"DATE_TRUNC('{time_format}', created_at) as time_bucket")
        
        # Build WHERE clause
        where_clauses = []
        
        # Date range filter
        start_date, end_date = query_config.date_range
        where_clauses.append(f"created_at >= '{start_date.isoformat()}'")
        where_clauses.append(f"created_at <= '{end_date.isoformat()}'")
        
        # Additional filters
        for field, value in query_config.filters.items():
            if isinstance(value, list):
                formatted_values = "', '".join(str(v) for v in value)
                where_clauses.append(f'"{field}" IN (\'{formatted_values}\')')
            elif isinstance(value, str):
                where_clauses.append(f'"{field}" = \'{value}\'')
            else:
                where_clauses.append(f'"{field}" = {value}')
        
        # Soft delete filter
        if hasattr(self.model, 'is_deleted'):
            where_clauses.append('is_deleted = false')
        
        # Build GROUP BY clause
        group_by_clauses = query_config.dimensions.copy()
        if query_config.granularity != TimeGranularity.DAY:
            group_by_clauses.append('time_bucket')
        
        # Build complete query
        query_parts = [
            f"SELECT {', '.join(select_clauses)}",
            f"FROM {table_name}",
            f"WHERE {' AND '.join(where_clauses)}"
        ]
        
        if group_by_clauses:
            query_parts.append(f"GROUP BY {', '.join(group_by_clauses)}")
        
        # Add ordering
        if query_config.granularity != TimeGranularity.DAY:
            query_parts.append("ORDER BY time_bucket")
        
        # Add limit/offset
        if query_config.limit:
            query_parts.append(f"LIMIT {query_config.limit}")
        
        if query_config.offset:
            query_parts.append(f"OFFSET {query_config.offset}")
        
        return ' '.join(query_parts)
    
    def _get_time_format(self, granularity: TimeGranularity) -> str:
        """Get PostgreSQL time format for granularity"""
        format_map = {
            TimeGranularity.MINUTE: 'minute',
            TimeGranularity.HOUR: 'hour',
            TimeGranularity.DAY: 'day',
            TimeGranularity.WEEK: 'week',
            TimeGranularity.MONTH: 'month',
            TimeGranularity.QUARTER: 'quarter',
            TimeGranularity.YEAR: 'year'
        }
        return format_map.get(granularity, 'day')


class {{service_name}}AnalyticsService:
    """{{service_description}}
    
    Enterprise analytics service providing:
    - Real-time metrics collection
    - Historical data analysis
    - Statistical computations
    - Trend analysis and forecasting
    - Anomaly detection
    - Custom business metrics
    - Performance optimization
    - Caching and aggregation
    """
    
    def __init__(
        self,
        session_factory: Callable,
        cache_manager: Optional[CacheManager] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.session_factory = session_factory
        self.cache = cache_manager
        self.metrics = metrics_collector
        self.data_processor = DataProcessor()
        self._redis_client = None
    
    async def initialize(self, redis_url: Optional[str] = None):
        """Initialize the analytics service"""
        if redis_url:
            self._redis_client = redis.from_url(redis_url)
        
        logger.info("Analytics service initialized")
    
    async def execute_query(
        self,
        query_config: AnalyticsQuery,
        use_cache: bool = True
    ) -> AnalyticsResult:
        """Execute analytics query with caching"""
        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query_config)
            cached_result = None
            
            if use_cache and self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.debug(f"Cache hit for analytics query: {cache_key}")
                    return AnalyticsResult(
                        query=query_config,
                        data=cached_result['data'],
                        total_count=cached_result['total_count'],
                        execution_time=cached_result['execution_time'],
                        cached=True,
                        metadata=cached_result.get('metadata', {})
                    )
            
            # Execute query
            data, total_count, metadata = await self._execute_database_query(query_config)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = AnalyticsResult(
                query=query_config,
                data=data,
                total_count=total_count,
                execution_time=execution_time,
                cached=False,
                metadata=metadata
            )
            
            # Cache result
            if use_cache and self.cache:
                cache_data = {
                    'data': data,
                    'total_count': total_count,
                    'execution_time': execution_time,
                    'metadata': metadata
                }
                await self.cache.set(
                    cache_key, 
                    cache_data, 
                    expire=3600  # 1 hour cache
                )
            
            # Record metrics
            if self.metrics:
                self.metrics.record_histogram(
                    'analytics_query_duration',
                    execution_time,
                    tags={'metric': query_config.metric_name}
                )
            
            logger.info(f"Analytics query executed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
            raise AnalyticsError(f"Query execution failed: {str(e)}")
    
    async def get_real_time_metrics(
        self,
        metric_names: List[str],
        time_window: int = 3600  # 1 hour
    ) -> Dict[str, Any]:
        """Get real-time metrics for the specified time window"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(seconds=time_window)
            
            results = {}
            
            for metric_name in metric_names:
                query_config = AnalyticsQuery(
                    metric_name=metric_name,
                    metric_type=MetricType.COUNT,
                    dimensions=[],
                    filters={},
                    date_range=(start_time, end_time),
                    granularity=TimeGranularity.MINUTE,
                    aggregations=[AggregationType.COUNT, AggregationType.SUM]
                )
                
                result = await self.execute_query(query_config, use_cache=False)
                results[metric_name] = result.data
            
            return results
            
        except Exception as e:
            logger.error(f"Real-time metrics retrieval failed: {e}")
            raise AnalyticsError(f"Real-time metrics failed: {str(e)}")
    
    async def analyze_trends(
        self,
        metric_name: str,
        days: int = 30,
        granularity: TimeGranularity = TimeGranularity.DAY
    ) -> Dict[str, Any]:
        """Analyze trends for a metric over time"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days)
            
            query_config = AnalyticsQuery(
                metric_name=metric_name,
                metric_type=MetricType.SUM,
                dimensions=[],
                filters={},
                date_range=(start_time, end_time),
                granularity=granularity,
                aggregations=[AggregationType.SUM, AggregationType.COUNT]
            )
            
            result = await self.execute_query(query_config)
            
            # Convert to time series data
            time_series_data = []
            for row in result.data:
                if 'time_bucket' in row and 'sum' in row:
                    time_series_data.append((
                        datetime.fromisoformat(row['time_bucket']),
                        float(row['sum'])
                    ))
            
            # Analyze trends
            trend_analysis = self.data_processor.calculate_trend(time_series_data)
            
            # Detect anomalies
            values = [value for _, value in time_series_data]
            anomaly_indices = self.data_processor.detect_anomalies(values)
            
            # Calculate statistics
            statistics = self.data_processor.calculate_statistics(values)
            
            return {
                'metric_name': metric_name,
                'time_period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': days
                },
                'trend_analysis': trend_analysis,
                'statistics': statistics,
                'anomalies': {
                    'count': len(anomaly_indices),
                    'indices': anomaly_indices
                },
                'data_points': len(time_series_data),
                'time_series': time_series_data
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise AnalyticsError(f"Trend analysis failed: {str(e)}")
    
    async def generate_dashboard_data(
        self,
        dashboard_config: Dict[str, Any],
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        try:
            dashboard_data = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'user_id': str(user_id) if user_id else None,
                'tenant_id': str(tenant_id) if tenant_id else None,
                'widgets': {}
            }
            
            # Process each widget configuration
            for widget_name, widget_config in dashboard_config.get('widgets', {}).items():
                try:
                    widget_data = await self._generate_widget_data(
                        widget_config,
                        user_id,
                        tenant_id
                    )
                    dashboard_data['widgets'][widget_name] = widget_data
                except Exception as e:
                    logger.error(f"Widget {widget_name} generation failed: {e}")
                    dashboard_data['widgets'][widget_name] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            raise AnalyticsError(f"Dashboard generation failed: {str(e)}")
    
    async def _execute_database_query(
        self,
        query_config: AnalyticsQuery
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """Execute database query"""
        
        async with self.session_factory() as session:
            # Use the appropriate model based on configuration
            from templates.database.sqlalchemy_model_template import ContentModel  # Replace with actual model
            
            query_builder = QueryBuilder(ContentModel)
            sql_query = query_builder.build_aggregation_query(query_config)
            
            # Execute query
            result = await session.execute(text(sql_query))
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(result.keys()):
                    value = row[i]
                    # Convert Decimal to float for JSON serialization
                    if isinstance(value, Decimal):
                        value = float(value)
                    row_dict[column] = value
                data.append(row_dict)
            
            # Get total count for pagination
            count_query = f"SELECT COUNT(*) FROM ({sql_query}) as subquery"
            count_result = await session.execute(text(count_query))
            total_count = count_result.scalar()
            
            metadata = {
                'query_executed': sql_query,
                'execution_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return data, total_count, metadata
    
    async def _generate_widget_data(
        self,
        widget_config: Dict[str, Any],
        user_id: Optional[UUID],
        tenant_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Generate data for a specific widget"""
        
        widget_type = widget_config.get('type', 'metric')
        
        if widget_type == 'metric':
            return await self._generate_metric_widget(widget_config, user_id, tenant_id)
        elif widget_type == 'chart':
            return await self._generate_chart_widget(widget_config, user_id, tenant_id)
        elif widget_type == 'table':
            return await self._generate_table_widget(widget_config, user_id, tenant_id)
        else:
            raise AnalyticsError(f"Unknown widget type: {widget_type}")
    
    async def _generate_metric_widget(
        self,
        config: Dict[str, Any],
        user_id: Optional[UUID],
        tenant_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Generate simple metric widget"""
        
        metric_name = config['metric_name']
        time_range = config.get('time_range', 24)  # hours
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=time_range)
        
        filters = config.get('filters', {})
        if tenant_id:
            filters['tenant_id'] = tenant_id
        
        query_config = AnalyticsQuery(
            metric_name=metric_name,
            metric_type=MetricType.COUNT,
            dimensions=[],
            filters=filters,
            date_range=(start_time, end_time),
            granularity=TimeGranularity.HOUR,
            aggregations=[AggregationType.COUNT, AggregationType.SUM]
        )
        
        result = await self.execute_query(query_config)
        
        # Calculate current value and change
        current_value = sum(row.get('sum', row.get('count', 0)) for row in result.data)
        
        # Get previous period for comparison
        prev_start = start_time - timedelta(hours=time_range)
        prev_query = AnalyticsQuery(
            metric_name=metric_name,
            metric_type=MetricType.COUNT,
            dimensions=[],
            filters=filters,
            date_range=(prev_start, start_time),
            granularity=TimeGranularity.HOUR,
            aggregations=[AggregationType.COUNT, AggregationType.SUM]
        )
        
        prev_result = await self.execute_query(prev_query)
        prev_value = sum(row.get('sum', row.get('count', 0)) for row in prev_result.data)
        
        # Calculate percentage change
        if prev_value > 0:
            change_percent = ((current_value - prev_value) / prev_value) * 100
        else:
            change_percent = 0
        
        return {
            'type': 'metric',
            'value': current_value,
            'previous_value': prev_value,
            'change_percent': change_percent,
            'trend': 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'stable'
        }
    
    def _generate_cache_key(self, query_config: AnalyticsQuery) -> str:
        """Generate cache key for query"""
        key_data = {
            'metric': query_config.metric_name,
            'type': query_config.metric_type.value,
            'dimensions': sorted(query_config.dimensions),
            'filters': sorted(query_config.filters.items()),
            'start': query_config.date_range[0].isoformat(),
            'end': query_config.date_range[1].isoformat(),
            'granularity': query_config.granularity.value,
            'aggregations': sorted([agg.value for agg in query_config.aggregations])
        }
        
        import hashlib
        key_string = json.dumps(key_data, sort_keys=True)
        return f"analytics:{hashlib.md5(key_string.encode()).hexdigest()}"


# Factory function
def create_analytics_service(
    session_factory: Callable = None,
    cache_manager: CacheManager = None,
    metrics_collector: MetricsCollector = None
) -> {{service_name}}AnalyticsService:
    """Create analytics service instance"""
    if session_factory is None:
        session_factory = get_session
    
    return {{service_name}}AnalyticsService(
        session_factory=session_factory,
        cache_manager=cache_manager,
        metrics_collector=metrics_collector
    )


# Export service class
__all__ = [
    'AnalyticsError',
    'MetricType',
    'TimeGranularity', 
    'AggregationType',
    'AnalyticsQuery',
    'AnalyticsResult',
    'DataProcessor',
    'QueryBuilder',
    '{{service_name}}AnalyticsService',
    'create_analytics_service'
]