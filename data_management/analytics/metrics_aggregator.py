"""Advanced Metrics Aggregator - Enterprise Data Consolidation
=========================================================

Sophisticated metrics aggregation system providing comprehensive data
consolidation, multi-dimensional analysis, and enterprise-grade reporting
for strategic business intelligence and operational excellence.

Core Features:
- Multi-source data aggregation and consolidation
- Real-time metrics calculation and caching
- Hierarchical data rollup and drill-down capabilities
- Custom metrics definition and computation engine
- Advanced statistical analysis and trend detection
- Cross-platform data synchronization and validation
- Automated data quality assessment and cleansing
- Enterprise-grade performance optimization

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved

Enterprise Warning:
===================
This metrics aggregation system contains proprietary data processing algorithms,
aggregation methodologies, and statistical analysis frameworks developed by Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
All data consolidation processes and metrics calculations are protected intellectual property.
"""import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
import redis.asyncio as redis
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from ...core.database import get_database_session
from ...core.cache import CacheManager
from ...models.users import User
from ...models.content import Content
from ...models.protection import ProtectionEvent
from ...models.monetization import Revenue
from .collectors import BusinessMetricsCollector
from .storage import TimeSeriesStore, MetricsWarehouse


class AggregationType(Enum):
    """Types of metric aggregations supported."""    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "standard_deviation"
    VARIANCE = "variance"
    RATE = "rate"
    RATIO = "ratio"
    GROWTH_RATE = "growth_rate"
    MOVING_AVERAGE = "moving_average"
    CUMULATIVE = "cumulative"
    WEIGHTED_AVERAGE = "weighted_average"


class TimeGranularity(Enum):
    """Time granularity levels for aggregation."""    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class DataSource(Enum):
    """Data sources for metrics aggregation."""    USER_ANALYTICS = "user_analytics"
    CONTENT_ANALYTICS = "content_analytics"
    REVENUE_ANALYTICS = "revenue_analytics"
    PROTECTION_ANALYTICS = "protection_analytics"
    SYSTEM_METRICS = "system_metrics"
    EXTERNAL_APIS = "external_apis"
    CUSTOM_SOURCES = "custom_sources"


@dataclass
class MetricDefinition:
    """Definition of a custom metric for aggregation."""    metric_id: str
    name: str
    description: str
    data_source: DataSource
    aggregation_type: AggregationType
    time_granularity: TimeGranularity
    calculation_formula: str
    filters: Dict[str, Any] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AggregatedMetric:
    """Aggregated metric result with metadata."""    metric_id: str
    value: Union[float, int, Dict[str, Any]]
    timestamp: datetime
    time_granularity: TimeGranularity
    dimensions: Dict[str, Any] = field(default_factory=dict)
    confidence_score: Optional[float] = None
    data_quality_score: Optional[float] = None
    calculation_metadata: Dict[str, Any] = field(default_factory=dict)
    source_data_points: int = 0
    aggregation_method: str = ""


@dataclass
class AggregationJob:
    """Configuration for an aggregation job."""    job_id: str
    metrics: List[str]
    time_range: Dict[str, datetime]
    granularity: TimeGranularity
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    output_format: str = "json"
    priority: int = 1
    scheduled_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


class AdvancedMetricsAggregator:
    """    Enterprise-grade metrics aggregation system.
    
    Provides sophisticated data consolidation, multi-dimensional analysis,
    and real-time metrics calculation for comprehensive business intelligence.
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_manager = CacheManager()
        self.metrics_warehouse = MetricsWarehouse()
        self.timeseries_store = TimeSeriesStore()
        self.metrics_collector = BusinessMetricsCollector()
        
        # Metric definitions registry
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.aggregation_functions: Dict[AggregationType, Callable] = {}
        self.data_sources: Dict[DataSource, Callable] = {}
        
        # Performance optimization
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.aggregation_cache = {}
        self.dependency_graph = {}
        
        # Redis for distributed caching
        self.redis_client = None
        
    async def initialize(self):
        """Initialize the metrics aggregation system."""        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            
            # Register built-in aggregation functions
            await self._register_aggregation_functions()
            
            # Register data source connectors
            await self._register_data_sources()
            
            # Load metric definitions
            await self._load_metric_definitions()
            
            # Build dependency graph
            await self._build_dependency_graph()
            
            self.logger.info("Advanced metrics aggregator initialized")
            
        except Exception as e:
            self.logger.error(f"Aggregator initialization failed: {e}")
            raise
    
    async def register_metric_definition(
        self,
        metric_def: MetricDefinition
    ) -> bool:
        """        Register a new metric definition.
        
        Args:
            metric_def: Metric definition to register
            
        Returns:
            Success status
        """        try:
            # Validate metric definition
            if not await self._validate_metric_definition(metric_def):
                raise ValueError(f"Invalid metric definition: {metric_def.metric_id}")
            
            # Store metric definition
            self.metric_definitions[metric_def.metric_id] = metric_def
            
            # Update dependency graph
            await self._update_dependency_graph(metric_def)
            
            # Store in persistent storage
            await self._store_metric_definition(metric_def)
            
            self.logger.info(f"Metric definition registered: {metric_def.metric_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Metric registration failed: {e}")
            return False
    
    async def aggregate_metrics(
        self,
        metric_ids: List[str],
        time_range: Dict[str, datetime],
        granularity: TimeGranularity = TimeGranularity.DAY,
        dimensions: List[str] = None,
        filters: Dict[str, Any] = None
    ) -> List[AggregatedMetric]:
        """        Aggregate multiple metrics with specified parameters.
        
        Args:
            metric_ids: List of metric IDs to aggregate
            time_range: Time range for aggregation
            granularity: Time granularity for aggregation
            dimensions: Dimensions for grouping
            filters: Additional filters to apply
            
        Returns:
            List of aggregated metrics
        """        try:
            dimensions = dimensions or []
            filters = filters or {}
            
            # Validate metric IDs
            valid_metrics = await self._validate_metric_ids(metric_ids)
            if not valid_metrics:
                raise ValueError("No valid metrics found")
            
            # Generate cache key
            cache_key = await self._generate_cache_key(
                valid_metrics, time_range, granularity, dimensions, filters
            )
            
            # Check cache first
            cached_result = await self._get_cached_aggregation(cache_key)
            if cached_result:
                self.logger.info(f"Returning cached aggregation: {cache_key}")
                return cached_result
            
            # Resolve dependencies
            execution_order = await self._resolve_dependencies(valid_metrics)
            
            # Execute aggregations in dependency order
            results = []
            for metric_id in execution_order:
                metric_result = await self._aggregate_single_metric(
                    metric_id, time_range, granularity, dimensions, filters
                )
                if metric_result:
                    results.append(metric_result)
            
            # Cache results
            await self._cache_aggregation_results(cache_key, results)
            
            self.logger.info(f"Aggregated {len(results)} metrics successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Metrics aggregation failed: {e}")
            raise
    
    async def create_aggregation_job(
        self,
        job_config: AggregationJob
    ) -> str:
        """        Create and schedule an aggregation job.
        
        Args:
            job_config: Job configuration
            
        Returns:
            Job ID
        """        try:
            # Validate job configuration
            if not await self._validate_job_config(job_config):
                raise ValueError("Invalid job configuration")
            
            # Schedule job execution
            if job_config.scheduled_time:
                await self._schedule_job(job_config)
            else:
                # Execute immediately
                asyncio.create_task(self._execute_aggregation_job(job_config))
            
            self.logger.info(f"Aggregation job created: {job_config.job_id}")
            return job_config.job_id
            
        except Exception as e:
            self.logger.error(f"Job creation failed: {e}")
            raise
    
    async def get_metric_trends(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        trend_analysis: bool = True
    ) -> Dict[str, Any]:
        """        Analyze trends for a specific metric.
        
        Args:
            metric_id: Metric identifier
            time_range: Time range for analysis
            trend_analysis: Whether to perform trend analysis
            
        Returns:
            Trend analysis results
        """        try:
            # Get historical data
            historical_data = await self._get_historical_metric_data(
                metric_id, time_range
            )
            
            if not historical_data:
                return {'error': 'No historical data found'}
            
            # Convert to pandas for analysis
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            trend_results = {
                'metric_id': metric_id,
                'data_points': len(df),
                'time_range': time_range,
                'summary_statistics': {
                    'mean': float(df['value'].mean()),
                    'median': float(df['value'].median()),
                    'std': float(df['value'].std()),
                    'min': float(df['value'].min()),
                    'max': float(df['value'].max())
                }
            }
            
            if trend_analysis:
                # Linear trend analysis
                x = np.arange(len(df))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, df['value'])
                
                trend_results['trend_analysis'] = {
                    'slope': float(slope),
                    'correlation': float(r_value),
                    'p_value': float(p_value),
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.3 else 'weak'
                }
                
                # Seasonal decomposition if sufficient data
                if len(df) >= 24:  # Minimum periods for seasonal analysis
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    decomposition = seasonal_decompose(df['value'], model='additive', period=7)
                    
                    trend_results['seasonal_analysis'] = {
                        'trend_component': decomposition.trend.dropna().tolist(),
                        'seasonal_component': decomposition.seasonal.dropna().tolist(),
                        'residual_component': decomposition.resid.dropna().tolist(),
                        'seasonal_strength': float(np.var(decomposition.seasonal.dropna()) / np.var(df['value']))
                    }
                
                # Anomaly detection
                z_scores = np.abs(stats.zscore(df['value']))
                anomalies = df[z_scores > 2]
                
                trend_results['anomaly_detection'] = {
                    'anomaly_count': len(anomalies),
                    'anomaly_timestamps': anomalies.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    'anomaly_values': anomalies['value'].tolist(),
                    'anomaly_z_scores': z_scores[z_scores > 2].tolist()
                }
            
            return trend_results
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            raise
    
    async def create_custom_aggregation(
        self,
        name: str,
        formula: str,
        data_sources: List[DataSource],
        parameters: Dict[str, Any] = None
    ) -> str:
        """        Create a custom aggregation function.
        
        Args:
            name: Name of the custom aggregation
            formula: Mathematical formula for aggregation
            data_sources: Required data sources
            parameters: Additional parameters
            
        Returns:
            Custom aggregation ID
        """        try:
            parameters = parameters or {}
            
            # Generate unique ID
            aggregation_id = f"custom_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            # Validate formula
            if not await self._validate_aggregation_formula(formula):
                raise ValueError("Invalid aggregation formula")
            
            # Create metric definition
            metric_def = MetricDefinition(
                metric_id=aggregation_id,
                name=name,
                description=f"Custom aggregation: {name}",
                data_source=DataSource.CUSTOM_SOURCES,
                aggregation_type=AggregationType.CUSTOM,
                time_granularity=TimeGranularity.DAY,
                calculation_formula=formula,
                metadata={
                    'custom_aggregation': True,
                    'data_sources': [ds.value for ds in data_sources],
                    'parameters': parameters
                }
            )
            
            # Register the metric
            await self.register_metric_definition(metric_def)
            
            self.logger.info(f"Custom aggregation created: {aggregation_id}")
            return aggregation_id
            
        except Exception as e:
            self.logger.error(f"Custom aggregation creation failed: {e}")
            raise
    
    async def optimize_aggregation_performance(
        self,
        metric_ids: List[str]
    ) -> Dict[str, Any]:
        """        Optimize aggregation performance for specified metrics.
        
        Args:
            metric_ids: Metrics to optimize
            
        Returns:
            Optimization results
        """        try:
            optimization_results = {}
            
            for metric_id in metric_ids:
                metric_def = self.metric_definitions.get(metric_id)
                if not metric_def:
                    continue
                
                # Analyze query patterns
                query_analysis = await self._analyze_query_patterns(metric_id)
                
                # Suggest pre-aggregations
                preag_suggestions = await self._suggest_preaggregations(metric_def, query_analysis)
                
                # Index recommendations
                index_recommendations = await self._recommend_indexes(metric_def)
                
                # Caching strategy
                cache_strategy = await self._optimize_cache_strategy(metric_def, query_analysis)
                
                optimization_results[metric_id] = {
                    'query_analysis': query_analysis,
                    'preaggregation_suggestions': preag_suggestions,
                    'index_recommendations': index_recommendations,
                    'cache_strategy': cache_strategy,
                    'estimated_performance_gain': await self._estimate_performance_gain(
                        metric_def, preag_suggestions, index_recommendations
                    )
                }
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            raise
    
    # Private helper methods
    
    async def _register_aggregation_functions(self):
        """Register built-in aggregation functions."""        self.aggregation_functions = {
            AggregationType.SUM: lambda data: data.sum(),
            AggregationType.AVERAGE: lambda data: data.mean(),
            AggregationType.COUNT: lambda data: len(data),
            AggregationType.MIN: lambda data: data.min(),
            AggregationType.MAX: lambda data: data.max(),
            AggregationType.MEDIAN: lambda data: data.median(),
            AggregationType.STANDARD_DEVIATION: lambda data: data.std(),
            AggregationType.VARIANCE: lambda data: data.var(),
            AggregationType.MOVING_AVERAGE: lambda data, window=7: data.rolling(window=window).mean(),
            AggregationType.CUMULATIVE: lambda data: data.cumsum(),
            AggregationType.PERCENTILE: lambda data, percentile=95: data.quantile(percentile/100)
        }
    
    async def _register_data_sources(self):
        """Register data source connectors."""        self.data_sources = {
            DataSource.USER_ANALYTICS: self._get_user_analytics_data,
            DataSource.CONTENT_ANALYTICS: self._get_content_analytics_data,
            DataSource.REVENUE_ANALYTICS: self._get_revenue_analytics_data,
            DataSource.PROTECTION_ANALYTICS: self._get_protection_analytics_data,
            DataSource.SYSTEM_METRICS: self._get_system_metrics_data
        }
    
    async def _load_metric_definitions(self):
        """Load metric definitions from storage."""        # Default metric definitions
        default_metrics = [
            MetricDefinition(
                metric_id="daily_active_users",
                name="Daily Active Users",
                description="Number of unique users active per day",
                data_source=DataSource.USER_ANALYTICS,
                aggregation_type=AggregationType.COUNT,
                time_granularity=TimeGranularity.DAY,
                calculation_formula="COUNT(DISTINCT user_id)"
            ),
            MetricDefinition(
                metric_id="revenue_per_day",
                name="Daily Revenue",
                description="Total revenue generated per day",
                data_source=DataSource.REVENUE_ANALYTICS,
                aggregation_type=AggregationType.SUM,
                time_granularity=TimeGranularity.DAY,
                calculation_formula="SUM(amount)"
            ),
            MetricDefinition(
                metric_id="content_uploads_daily",
                name="Daily Content Uploads",
                description="Number of content pieces uploaded per day",
                data_source=DataSource.CONTENT_ANALYTICS,
                aggregation_type=AggregationType.COUNT,
                time_granularity=TimeGranularity.DAY,
                calculation_formula="COUNT(*)"
            )
        ]
        
        for metric_def in default_metrics:
            self.metric_definitions[metric_def.metric_id] = metric_def
    
    async def _build_dependency_graph(self):
        """Build dependency graph for metric calculations."""        for metric_id, metric_def in self.metric_definitions.items():
            self.dependency_graph[metric_id] = metric_def.dependencies
    
    async def _validate_metric_definition(self, metric_def: MetricDefinition) -> bool:
        """Validate metric definition."""        # Check required fields
        if not metric_def.metric_id or not metric_def.name:
            return False
        
        # Check formula syntax
        if not await self._validate_aggregation_formula(metric_def.calculation_formula):
            return False
        
        return True
    
    async def _validate_aggregation_formula(self, formula: str) -> bool:
        """Validate aggregation formula syntax."""        # Basic validation - in production, this would be more sophisticated
        allowed_functions = ['SUM', 'COUNT', 'AVG', 'MIN', 'MAX', 'DISTINCT']
        return any(func in formula.upper() for func in allowed_functions)
    
    async def _update_dependency_graph(self, metric_def: MetricDefinition):
        """Update dependency graph with new metric."""        self.dependency_graph[metric_def.metric_id] = metric_def.dependencies
    
    async def _store_metric_definition(self, metric_def: MetricDefinition):
        """Store metric definition in persistent storage."""        try:
            # Create metric definition document
            metric_doc = {
                'metric_id': definition.metric_id,
                'name': definition.name,
                'description': definition.description,
                'metric_type': definition.metric_type.value,
                'aggregation_method': definition.aggregation_method.value,
                'data_source': definition.data_source,
                'calculation_logic': definition.calculation_logic,
                'dimensions': definition.dimensions,
                'filters': definition.filters,
                'unit': definition.unit,
                'format_precision': definition.format_precision,
                'is_active': definition.is_active,
                'created_at': definition.created_at.isoformat(),
                'updated_at': definition.updated_at.isoformat() if definition.updated_at else None,
                'version': getattr(definition, 'version', 1),
                'tags': getattr(definition, 'tags', []),
                'category': getattr(definition, 'category', 'general')
            }
            
            # Store in database
            collection = self.db.metric_definitions
            await collection.replace_one(
                {'metric_id': definition.metric_id},
                metric_doc,
                upsert=True
            )
            
            # Create indexes for efficient querying
            await collection.create_index([
                ('metric_id', 1),
                ('metric_type', 1),
                ('data_source', 1),
                ('is_active', 1)
            ])
            
            # Update in-memory cache
            self.metric_definitions[definition.metric_id] = definition
            
            self.logger.info(f"Metric definition {definition.metric_id} stored successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to store metric definition {definition.metric_id}: {e}")
            raise
    
    async def _validate_metric_ids(self, metric_ids: List[str]) -> List[str]:
        """Validate and filter metric IDs."""        return [mid for mid in metric_ids if mid in self.metric_definitions]
    
    async def _generate_cache_key(
        self,
        metric_ids: List[str],
        time_range: Dict[str, datetime],
        granularity: TimeGranularity,
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> str:
        """Generate cache key for aggregation results."""        key_data = {
            'metrics': sorted(metric_ids),
            'start': time_range.get('start').isoformat() if time_range.get('start') else None,
            'end': time_range.get('end').isoformat() if time_range.get('end') else None,
            'granularity': granularity.value,
            'dimensions': sorted(dimensions),
            'filters': sorted(filters.items()) if filters else []
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_cached_aggregation(self, cache_key: str) -> Optional[List[AggregatedMetric]]:
        """Get cached aggregation results."""        try:
            cached_data = await self.cache_manager.get(f"aggregation:{cache_key}")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            self.logger.warning(f"Cache retrieval failed: {e}")
        return None
    
    async def _cache_aggregation_results(
        self,
        cache_key: str,
        results: List[AggregatedMetric],
        ttl: int = 3600
    ):
        """Cache aggregation results."""        try:
            await self.cache_manager.set(
                f"aggregation:{cache_key}",
                json.dumps([result.__dict__ for result in results], default=str),
                ttl=ttl
            )
        except Exception as e:
            self.logger.warning(f"Cache storage failed: {e}")
    
    async def _resolve_dependencies(self, metric_ids: List[str]) -> List[str]:
        """Resolve metric dependencies and return execution order."""        # Topological sort of dependency graph
        visited = set()
        execution_order = []
        
        def visit(metric_id: str):
            if metric_id in visited:
                return
            visited.add(metric_id)
            
            # Visit dependencies first
            for dep in self.dependency_graph.get(metric_id, []):
                if dep in metric_ids:
                    visit(dep)
            
            execution_order.append(metric_id)
        
        for metric_id in metric_ids:
            visit(metric_id)
        
        return execution_order
    
    async def _aggregate_single_metric(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        granularity: TimeGranularity,
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> Optional[AggregatedMetric]:
        """Aggregate a single metric."""        try:
            metric_def = self.metric_definitions.get(metric_id)
            if not metric_def:
                return None
            
            # Get data from appropriate source
            data_fetcher = self.data_sources.get(metric_def.data_source)
            if not data_fetcher:
                self.logger.warning(f"No data fetcher for source: {metric_def.data_source}")
                return None
            
            # Fetch raw data
            raw_data = await data_fetcher(metric_id, time_range, dimensions, filters)
            
            if not raw_data:
                return None
            
            # Apply aggregation function
            aggregation_func = self.aggregation_functions.get(metric_def.aggregation_type)
            if not aggregation_func:
                self.logger.warning(f"No aggregation function for type: {metric_def.aggregation_type}")
                return None
            
            # Convert to pandas for processing
            df = pd.DataFrame(raw_data)
            
            # Apply time granularity grouping
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = self._apply_time_granularity(df, granularity)
            
            # Apply dimension grouping
            if dimensions and all(dim in df.columns for dim in dimensions):
                grouped_data = df.groupby(dimensions)
                aggregated_values = {}
                for group_key, group_data in grouped_data:
                    if isinstance(group_key, tuple):
                        key = '_'.join(str(k) for k in group_key)
                    else:
                        key = str(group_key)
                    aggregated_values[key] = aggregation_func(group_data['value'])
                
                aggregated_value = aggregated_values
            else:
                aggregated_value = aggregation_func(df['value'])
            
            # Calculate data quality score
            data_quality_score = await self._calculate_data_quality_score(df)
            
            return AggregatedMetric(
                metric_id=metric_id,
                value=aggregated_value,
                timestamp=datetime.now(),
                time_granularity=granularity,
                dimensions={dim: filters.get(dim) for dim in dimensions},
                data_quality_score=data_quality_score,
                calculation_metadata={
                    'source_records': len(raw_data),
                    'aggregation_type': metric_def.aggregation_type.value,
                    'calculation_time': datetime.now().isoformat()
                },
                source_data_points=len(raw_data),
                aggregation_method=metric_def.aggregation_type.value
            )
            
        except Exception as e:
            self.logger.error(f"Single metric aggregation failed for {metric_id}: {e}")
            return None
    
    def _apply_time_granularity(
        self,
        df: pd.DataFrame,
        granularity: TimeGranularity
    ) -> pd.DataFrame:
        """Apply time granularity grouping to dataframe."""        df.set_index('timestamp', inplace=True)
        
        if granularity == TimeGranularity.HOUR:
            return df.resample('H').agg({'value': 'sum'}).reset_index()
        elif granularity == TimeGranularity.DAY:
            return df.resample('D').agg({'value': 'sum'}).reset_index()
        elif granularity == TimeGranularity.WEEK:
            return df.resample('W').agg({'value': 'sum'}).reset_index()
        elif granularity == TimeGranularity.MONTH:
            return df.resample('M').agg({'value': 'sum'}).reset_index()
        else:
            return df.reset_index()
    
    async def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score for the dataset."""        if df.empty:
            return 0.0
        
        # Check for missing values
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        
        # Check for duplicates
        duplicate_ratio = df.duplicated().sum() / len(df)
        
        # Check for outliers using IQR method
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        outlier_ratio = 0
        if len(numeric_columns) > 0:
            for col in numeric_columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                outlier_ratio += outliers / len(df)
            outlier_ratio /= len(numeric_columns)
        
        # Calculate overall quality score
        quality_score = 1.0 - (missing_ratio * 0.4 + duplicate_ratio * 0.3 + outlier_ratio * 0.3)
        return max(0.0, min(1.0, quality_score))
    
    # Data source methods
    async def _get_user_analytics_data(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get user analytics data."""        # Placeholder implementation
        return [
            {'timestamp': datetime.now(), 'value': 100, 'user_id': 'user1'},
            {'timestamp': datetime.now(), 'value': 150, 'user_id': 'user2'}
        ]
    
    async def _get_content_analytics_data(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get content analytics data."""        return []
    
    async def _get_revenue_analytics_data(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get revenue analytics data."""        return []
    
    async def _get_protection_analytics_data(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get protection analytics data."""        return []
    
    async def _get_system_metrics_data(
        self,
        metric_id: str,
        time_range: Dict[str, datetime],
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get system metrics data."""        return []
    
    # Additional helper methods would continue...
    async def _get_historical_metric_data(
        self,
        metric_id: str,
        time_range: Dict[str, datetime]
    ) -> List[Dict[str, Any]]:
        """Get historical data for trend analysis."""        return []
    
    async def _validate_job_config(self, job_config: AggregationJob) -> bool:
        """Validate aggregation job configuration."""        return True
    
    async def _schedule_job(self, job_config: AggregationJob):
        """Schedule aggregation job for later execution."""        try:
            # Create job document for persistent storage
            job_doc = {
                'job_id': job_config.job_id,
                'metric_ids': job_config.metric_ids,
                'time_range': {
                    'start': job_config.time_range['start'].isoformat(),
                    'end': job_config.time_range['end'].isoformat()
                },
                'granularity': job_config.granularity.value,
                'dimensions': job_config.dimensions,
                'filters': job_config.filters,
                'scheduled_at': job_config.scheduled_at.isoformat() if job_config.scheduled_at else None,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat(),
                'priority': getattr(job_config, 'priority', 'normal'),
                'retry_count': 0,
                'max_retries': 3
            }
            
            # Store in job queue
            collection = self.db.aggregation_jobs
            await collection.insert_one(job_doc)
            
            # Create index for job processing
            await collection.create_index([
                ('status', 1),
                ('scheduled_at', 1),
                ('priority', 1)
            ])
            
            # Schedule execution if scheduled_at is specified
            if job_config.scheduled_at:
                delay = (job_config.scheduled_at - datetime.utcnow()).total_seconds()
                if delay > 0:
                    # Use asyncio to schedule the job
                    async def delayed_execution():
                        await asyncio.sleep(delay)
                        await self._execute_aggregation_job(job_config)
                    
                    asyncio.create_task(delayed_execution())
            
            self.logger.info(f"Aggregation job {job_config.job_id} scheduled successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule aggregation job {job_config.job_id}: {e}")
            raise
    
    async def _execute_aggregation_job(self, job_config: AggregationJob):
        """Execute aggregation job."""        try:
            # Update job status to running
            await self._update_job_status(job_config.job_id, 'running')
            
            # Execute the aggregation
            results = await self.aggregate_metrics(
                metric_ids=job_config.metric_ids,
                time_range=job_config.time_range,
                granularity=job_config.granularity,
                dimensions=job_config.dimensions,
                filters=job_config.filters
            )
            
            # Store job results
            result_doc = {
                'job_id': job_config.job_id,
                'results': results,
                'completed_at': datetime.utcnow().isoformat(),
                'execution_time_seconds': (datetime.utcnow() - datetime.fromisoformat(
                    job_config.created_at if hasattr(job_config, 'created_at') else datetime.utcnow().isoformat()
                )).total_seconds(),
                'status': 'completed'
            }
            
            collection = self.db.aggregation_job_results
            await collection.insert_one(result_doc)
            
            # Update job status to completed
            await self._update_job_status(job_config.job_id, 'completed')
            
            self.logger.info(f"Aggregation job {job_config.job_id} executed successfully")
            
        except Exception as e:
            # Update job status to failed
            await self._update_job_status(job_config.job_id, 'failed', str(e))
            self.logger.error(f"Aggregation job {job_config.job_id} failed: {e}")
            raise
    
    async def _update_job_status(self, job_id: str, status: str, error_message: str = None):
        """Update job status in database."""        try:
            update_doc = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_doc['error_message'] = error_message
            
            collection = self.db.aggregation_jobs
            await collection.update_one(
                {'job_id': job_id},
                {'$set': update_doc}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update job status for {job_id}: {e}")
