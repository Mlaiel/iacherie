# WARNING: Potential SQL injection risk - use parameterized queries
"""Analytics Query Engine - Advanced Analytics Processing
======================================================

High-performance analytics query processing and optimization with
multi-dimensional analytics (OLAP), real-time processing, and natural language to SQL.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import statistics
from decimal import Decimal

try:
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
    np = None

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

import redis.asyncio as redis


class QueryType(Enum):
    """Types of analytics queries."""
    OLAP = "olap"
    OLTP = "oltp"
    AGGREGATION = "aggregation"
    TIME_SERIES = "time_series"
    EXPLORATORY = "exploratory"
    PREDICTIVE = "predictive"
    STATISTICAL = "statistical"
    CUSTOM = "custom"


class AggregationFunction(Enum):
    """Aggregation functions."""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    STDDEV = "stddev"
    VARIANCE = "variance"
    PERCENTILE = "percentile"
    DISTINCT_COUNT = "distinct_count"


class DimensionType(Enum):
    """OLAP dimension types."""
    TIME = "time"
    GEOGRAPHY = "geography"
    PRODUCT = "product"
    CUSTOMER = "customer"
    CHANNEL = "channel"
    CAMPAIGN = "campaign"
    CUSTOM = "custom"


class VisualizationType(Enum):
    """Data visualization types."""
    TABLE = "table"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"


@dataclass
class Dimension:
    """OLAP dimension definition."""
    name: str
    dimension_type: DimensionType
    table_name: str
    key_column: str
    display_column: str
    hierarchy: List[str] = field(default_factory=list)
    filters: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Measure:
    """OLAP measure definition."""
    name: str
    aggregation_function: AggregationFunction
    source_column: str
    table_name: str
    format_string: str = "{:.2f}"
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsQuery:
    """Analytics query definition."""
    id: str
    name: str
    query_type: QueryType
    sql: Optional[str] = None
    natural_language: Optional[str] = None
    dimensions: List[str] = field(default_factory=list)
    measures: List[str] = field(default_factory=list)
    filters: List[Dict[str, Any]] = field(default_factory=list)
    time_range: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None
    cache_ttl: int = 3600  # Cache for 1 hour by default
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Analytics query result."""
    query_id: str
    execution_id: str
    data: List[Dict[str, Any]]
    columns: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    cache_hit: bool = False
    visualization_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsCube:
    """OLAP cube definition."""
    id: str
    name: str
    fact_table: str
    dimensions: List[Dimension]
    measures: List[Measure]
    refresh_schedule: Optional[str] = None
    materialized: bool = True
    incremental: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryPlan:
    """Query execution plan."""
    id: str
    query_id: str
    steps: List[Dict[str, Any]]
    estimated_cost: float
    estimated_rows: int
    estimated_time: float
    optimization_applied: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


Base = declarative_base() if SQLALCHEMY_AVAILABLE else None


class QueryExecutionModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Query execution database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'analytics_query_executions'
        
        id = sa.Column(sa.String(36), primary_key=True)
        query_id = sa.Column(sa.String(36), nullable=False)
        sql = sa.Column(sa.Text, nullable=False)
        status = sa.Column(sa.String(20), nullable=False)
        started_at = sa.Column(sa.DateTime, nullable=False)
        completed_at = sa.Column(sa.DateTime)
        execution_time = sa.Column(sa.Float)
        row_count = sa.Column(sa.BigInteger)
        cache_hit = sa.Column(sa.Boolean, default=False)
        error_message = sa.Column(sa.Text)
        meta_data = sa.Column(sa.Text)
        created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class AnalyticsQueryEngine:
    """Advanced analytics query processing engine."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        warehouse_manager: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url and SQLALCHEMY_AVAILABLE:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup for caching
        self.redis_url = redis_url
        self.redis_client = None
        
        # Warehouse manager integration
        self.warehouse_manager = warehouse_manager
        
        # Analytics state
        self.dimensions: Dict[str, Dimension] = {}
        self.measures: Dict[str, Measure] = {}
        self.analytics_cubes: Dict[str, AnalyticsCube] = {}
        self.saved_queries: Dict[str, AnalyticsQuery] = {}
        
        # Query processing
        self.query_cache: Dict[str, QueryResult] = {}
        self.active_queries: Dict[str, Any] = {}
        self.query_optimizers: List[Callable] = []
        
        # Natural language processing
        self.nl_to_sql_engine: Optional['NLToSQLEngine'] = None
        
        # Performance tracking
        self.analytics_metrics = {
            'total_queries_executed': 0,
            'total_execution_time': 0.0,
            'average_query_time': 0.0,
            'cache_hit_ratio': 0.0,
            'olap_queries': 0,
            'real_time_queries': 0
        }
        
        # Setup components
        self._setup_query_optimizers()
        self._setup_built_in_dimensions_measures()
        self._setup_nl_engine()
    
    async def initialize(self):
        """Initialize the analytics query engine."""
        # Initialize database if configured
        if self.engine and SQLALCHEMY_AVAILABLE:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        # Initialize NL to SQL engine
        if self.nl_to_sql_engine:
            await self.nl_to_sql_engine.initialize()
        
        self.logger.info("Analytics query engine initialized")
    
    def _setup_query_optimizers(self):
        """Setup query optimization functions."""
        self.query_optimizers = [
            self._optimize_aggregations,
            self._optimize_joins,
            self._optimize_filters,
            self._optimize_sorting,
            self._optimize_time_range_queries
        ]
    
    def _setup_built_in_dimensions_measures(self):
        """Setup built-in dimensions and measures."""
        # Time dimension
        time_dimension = Dimension(
            name="time",
            dimension_type=DimensionType.TIME,
            table_name="time_dim",
            key_column="date_key",
            display_column="date_display",
            hierarchy=["year", "quarter", "month", "week", "day"]
        )
        
        # User dimension
        user_dimension = Dimension(
            name="user",
            dimension_type=DimensionType.CUSTOMER,
            table_name="user_dim",
            key_column="user_id",
            display_column="username",
            hierarchy=["country", "state", "city"]
        )
        
        # Platform dimension
        platform_dimension = Dimension(
            name="platform",
            dimension_type=DimensionType.CHANNEL,
            table_name="platform_dim",
            key_column="platform_id",
            display_column="platform_name"
        )
        
        # Built-in measures
        user_count_measure = Measure(
            name="user_count",
            aggregation_function=AggregationFunction.DISTINCT_COUNT,
            source_column="user_id",
            table_name="fact_activity"
        )
        
        revenue_measure = Measure(
            name="total_revenue",
            aggregation_function=AggregationFunction.SUM,
            source_column="revenue",
            table_name="fact_revenue",
            format_string="${:,.2f}"
        )
        
        # Register built-ins
        for dim in [time_dimension, user_dimension, platform_dimension]:
            self.dimensions[dim.name] = dim
        
        for measure in [user_count_measure, revenue_measure]:
            self.measures[measure.name] = measure
    
    def _setup_nl_engine(self):
        """Setup natural language to SQL engine."""
        self.nl_to_sql_engine = NLToSQLEngine(self)
    
    def register_dimension(self, dimension: Dimension):
        """Register a dimension for OLAP queries."""
        self.dimensions[dimension.name] = dimension
        self.logger.info(f"Registered dimension: {dimension.name}")
    
    def register_measure(self, measure: Measure):
        """Register a measure for analytics."""
        self.measures[measure.name] = measure
        self.logger.info(f"Registered measure: {measure.name}")
    
    def create_analytics_cube(self, cube: AnalyticsCube):
        """Create an OLAP analytics cube."""
        self.analytics_cubes[cube.id] = cube
        self.logger.info(f"Created analytics cube: {cube.name}")
    
    async def execute_query(
        self, 
        query: AnalyticsQuery,
        warehouse_id: Optional[str] = None
    ) -> QueryResult:
        """Execute analytics query."""
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query)
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                cached_result.cache_hit = True
                self._update_cache_metrics(True)
                return cached_result
            
            # Generate SQL if needed
            if not query.sql:
                if query.natural_language and self.nl_to_sql_engine:
                    query.sql = await self.nl_to_sql_engine.convert_to_sql(query.natural_language)
                elif query.dimensions or query.measures:
                    query.sql = await self._generate_olap_sql(query)
                else:
                    raise ValueError("No SQL query or OLAP specification provided")
            
            # Optimize query
            optimized_sql = await self._optimize_query(query.sql, query)
            
            # Execute query
            if self.warehouse_manager and warehouse_id:
                warehouse_execution = await self.warehouse_manager.execute_query(
                    warehouse_id, optimized_sql
                )
                
                if warehouse_execution.status != "completed":
                    raise Exception(f"Query execution failed: {warehouse_execution.error_message}")
                
                # Convert warehouse result to analytics result
                result = await self._convert_warehouse_result(warehouse_execution, query, execution_id)
                
            else:
                # Execute directly if no warehouse manager
                result = await self._execute_direct_query(optimized_sql, query, execution_id)
            
            # Generate insights and visualizations
            result.insights = await self._generate_insights(result)
            result.visualization_suggestions = await self._suggest_visualizations(result, query)
            
            # Cache result
            await self._cache_result(cache_key, result, query.cache_ttl)
            
            # Store execution record
            if self.async_session:
                await self._store_query_execution(result, optimized_sql)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_query_metrics(query.query_type, execution_time, False)
            
            self.logger.info(f"Query executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Query execution failed: {e}")
            
            # Return error result
            return QueryResult(
                query_id=query.id,
                execution_id=execution_id,
                data=[],
                columns=[],
                row_count=0,
                execution_time=execution_time,
                metadata={'error': str(e)}
            )
    
    async def _generate_olap_sql(self, query: AnalyticsQuery) -> str:
        """Generate SQL for OLAP query."""
        select_clauses = []
        from_clauses = []
        join_clauses = []
        where_clauses = []
        group_by_clauses = []
        
        # Add dimensions to SELECT and GROUP BY
        for dim_name in query.dimensions:
            if dim_name in self.dimensions:
                dimension = self.dimensions[dim_name]
                select_clauses.append(f"{dimension.table_name}.{dimension.display_column} AS {dim_name}")
                group_by_clauses.append(f"{dimension.table_name}.{dimension.display_column}")
                
                # Add table to FROM if not already included
                if dimension.table_name not in from_clauses:
                    from_clauses.append(dimension.table_name)
        
        # Add measures to SELECT
        for measure_name in query.measures:
            if measure_name in self.measures:
                measure = self.measures[measure_name]
                func = measure.aggregation_function.value.upper()
                
                if measure.aggregation_function == AggregationFunction.DISTINCT_COUNT:
                    select_clauses.append(f"COUNT(DISTINCT {measure.table_name}.{measure.source_column}) AS {measure_name}")
                else:
                    select_clauses.append(f"{func}({measure.table_name}.{measure.source_column}) AS {measure_name}")
                
                # Add table to FROM if not already included
                if measure.table_name not in from_clauses:
                    from_clauses.append(measure.table_name)
        
        # Build WHERE clause from filters
        for filter_def in query.filters:
            field = filter_def.get('field')
            operator = filter_def.get('operator', '=')
            value = filter_def.get('value')
            
            if field and value is not None:
                if isinstance(value, str):
                    where_clauses.append(f"{field} {operator} '{value}'")
                else:
                    where_clauses.append(f"{field} {operator} {value}")
        
        # Add time range filter if specified
        if query.time_range:
            time_field = query.time_range.get('field', 'created_at')
            start_date = query.time_range.get('start')
            end_date = query.time_range.get('end')
            
            if start_date:
                where_clauses.append(f"{time_field} >= '{start_date}'")
            if end_date:
                where_clauses.append(f"{time_field} <= '{end_date}'")
        
        # Build complete SQL
        sql_parts = []
        sql_parts.append(f"SELECT {', '.join(select_clauses)}")
        sql_parts.append(f"FROM {', '.join(from_clauses)}")
        
        if join_clauses:
            sql_parts.extend(join_clauses)
        
        if where_clauses:
            sql_parts.append(f"WHERE {' AND '.join(where_clauses)}")
        
        if group_by_clauses:
            sql_parts.append(f"GROUP BY {', '.join(group_by_clauses)}")
        
        if query.limit:
            sql_parts.append(f"LIMIT {query.limit}")
        
        return '\n'.join(sql_parts)
    
    async def _optimize_query(self, sql: str, query: AnalyticsQuery) -> str:
        """Apply query optimizations."""
        optimized_sql = sql
        
        for optimizer in self.query_optimizers:
            optimized_sql = await optimizer(optimized_sql, query)
        
        return optimized_sql
    
    async def _optimize_aggregations(self, sql: str, query: AnalyticsQuery) -> str:
        """Optimize aggregation queries."""
        # Add aggregation optimizations
        return sql
    
    async def _optimize_joins(self, sql: str, query: AnalyticsQuery) -> str:
        """Optimize join operations."""
        # Add join optimizations
        return sql
    
    async def _optimize_filters(self, sql: str, query: AnalyticsQuery) -> str:
        """Optimize filter conditions."""
        # Add filter optimizations
        return sql
    
    async def _optimize_sorting(self, sql: str, query: AnalyticsQuery) -> str:
        """Optimize sorting operations."""
        # Add sorting optimizations
        return sql
    
    async def _optimize_time_range_queries(self, sql: str, query: AnalyticsQuery) -> str:
        """Optimize time range queries."""
        # Add time range optimizations
        return sql
    
    async def _execute_direct_query(self, sql: str, query: AnalyticsQuery, execution_id: str) -> QueryResult:
        """Execute query directly without warehouse manager."""
        # This would execute against a direct database connection
        # For now, return mock data
        
        return QueryResult(
            query_id=query.id,
            execution_id=execution_id,
            data=[
                {"dimension1": "value1", "measure1": 100},
                {"dimension1": "value2", "measure1": 200}
            ],
            columns=[
                {"name": "dimension1", "type": "string"},
                {"name": "measure1", "type": "number"}
            ],
            row_count=2,
            execution_time=0.5
        )
    
    async def _convert_warehouse_result(self, warehouse_execution: Any, query: AnalyticsQuery, execution_id: str) -> QueryResult:
        """Convert warehouse execution result to analytics result."""
        # This would convert the warehouse result format to analytics format
        # For now, return mock conversion
        
        return QueryResult(
            query_id=query.id,
            execution_id=execution_id,
            data=[],
            columns=[],
            row_count=0,
            execution_time=warehouse_execution.execution_time or 0.0
        )
    
    async def _generate_insights(self, result: QueryResult) -> List[str]:
        """Generate insights from query results."""
        insights = []
        
        if not result.data:
            return insights
        
        # Analyze data for patterns and insights
        if len(result.data) > 1:
            # Check for trends
            numeric_columns = [col['name'] for col in result.columns if col['type'] in ['number', 'integer', 'float']]
            
            for col in numeric_columns:
                values = [row.get(col, 0) for row in result.data if row.get(col) is not None]
                
                if len(values) > 1:
                    if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                        insights.append(f"{col} shows a consistently increasing trend")
                    elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
                        insights.append(f"{col} shows a consistently decreasing trend")
                    
                    # Statistical insights
                    if len(values) >= 3:
                        mean_val = statistics.mean(values)
                        median_val = statistics.median(values)
                        
                        if abs(mean_val - median_val) / mean_val > 0.2:
                            insights.append(f"{col} distribution is skewed (mean: {mean_val:.2f}, median: {median_val:.2f})")
        
        # Check for outliers
        for col in [c['name'] for c in result.columns if c['type'] in ['number', 'integer', 'float']]:
            values = [row.get(col, 0) for row in result.data if row.get(col) is not None]
            
            if len(values) >= 5:
                q1 = statistics.quantiles(values, n=4)[0]
                q3 = statistics.quantiles(values, n=4)[2]
                iqr = q3 - q1
                
                outliers = [v for v in values if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]
                if outliers:
                    insights.append(f"{col} has {len(outliers)} outlier(s) detected")
        
        return insights
    
    async def _suggest_visualizations(self, result: QueryResult, query: AnalyticsQuery) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations for the result."""
        suggestions = []
        
        if not result.data or not result.columns:
            return suggestions
        
        # Analyze data structure
        categorical_cols = [col['name'] for col in result.columns if col['type'] == 'string']
        numeric_cols = [col['name'] for col in result.columns if col['type'] in ['number', 'integer', 'float']]
        date_cols = [col['name'] for col in result.columns if col['type'] in ['date', 'datetime', 'timestamp']]
        
        # Suggest based on data structure
        if len(categorical_cols) == 1 and len(numeric_cols) == 1:
            suggestions.append({
                'type': VisualizationType.BAR_CHART.value,
                'x_axis': categorical_cols[0],
                'y_axis': numeric_cols[0],
                'title': f"{numeric_cols[0]} by {categorical_cols[0]}"
            })
            
            if len(result.data) <= 10:
                suggestions.append({
                    'type': VisualizationType.PIE_CHART.value,
                    'category': categorical_cols[0],
                    'value': numeric_cols[0],
                    'title': f"Distribution of {numeric_cols[0]}"
                })
        
        if len(date_cols) >= 1 and len(numeric_cols) >= 1:
            suggestions.append({
                'type': VisualizationType.LINE_CHART.value,
                'x_axis': date_cols[0],
                'y_axis': numeric_cols[0],
                'title': f"{numeric_cols[0]} over time"
            })
        
        if len(numeric_cols) >= 2:
            suggestions.append({
                'type': VisualizationType.SCATTER_PLOT.value,
                'x_axis': numeric_cols[0],
                'y_axis': numeric_cols[1],
                'title': f"{numeric_cols[1]} vs {numeric_cols[0]}"
            })
        
        # Always suggest table view
        suggestions.append({
            'type': VisualizationType.TABLE.value,
            'title': "Data Table View"
        })
        
        return suggestions
    
    async def create_dashboard(
        self, 
        name: str, 
        queries: List[AnalyticsQuery],
        layout: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create analytics dashboard."""
        dashboard = {
            'id': str(uuid.uuid4()),
            'name': name,
            'queries': [q.id for q in queries],
            'layout': layout or self._generate_default_layout(len(queries)),
            'created_at': datetime.utcnow().isoformat(),
            'metadata': {}
        }
        
        # Execute all queries
        results = {}
        for query in queries:
            result = await self.execute_query(query)
            results[query.id] = result
        
        dashboard['results'] = results
        
        return dashboard
    
    def _generate_default_layout(self, query_count: int) -> Dict[str, Any]:
        """Generate default dashboard layout."""
        if query_count <= 2:
            return {'grid': '1x2', 'size': 'large'}
        elif query_count <= 4:
            return {'grid': '2x2', 'size': 'medium'}
        else:
            return {'grid': '3x3', 'size': 'small'}
    
    async def get_query_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get query suggestions based on context."""
        suggestions = []
        
        # Suggest based on available dimensions and measures
        if self.dimensions and self.measures:
            suggestions.append({
                'title': "User Activity Analysis",
                'description': "Analyze user activity across platforms",
                'dimensions': ["time", "platform"],
                'measures': ["user_count"],
                'query_type': QueryType.OLAP.value
            })
            
            suggestions.append({
                'title': "Revenue Trending",
                'description': "Track revenue trends over time",
                'dimensions': ["time"],
                'measures': ["total_revenue"],
                'query_type': QueryType.TIME_SERIES.value
            })
        
        # Suggest based on recent queries
        popular_patterns = await self._get_popular_query_patterns()
        suggestions.extend(popular_patterns)
        
        return suggestions
    
    async def _get_popular_query_patterns(self) -> List[Dict[str, Any]]:
        """Get popular query patterns from execution history."""
        # This would analyze query execution history
        return [
            {
                'title': "Top Performing Content",
                'description': "Most engaging content by platform",
                'query_type': QueryType.AGGREGATION.value
            }
        ]
    
    # Caching methods
    def _generate_cache_key(self, query: AnalyticsQuery) -> str:
        """Generate cache key for query."""
        key_data = {
            'sql': query.sql,
            'dimensions': sorted(query.dimensions),
            'measures': sorted(query.measures),
            'filters': sorted(query.filters, key=lambda x: str(x)),
            'time_range': query.time_range
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_cached_result(self, cache_key: str) -> Optional[QueryResult]:
        """Get cached query result."""
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(f"analytics_cache:{cache_key}")
                if cached_data:
                    return QueryResult(**json.loads(cached_data))
            except Exception as e:
                self.logger.warning(f"Cache get error: {e}")
        
        return self.query_cache.get(cache_key)
    
    async def _cache_result(self, cache_key: str, result: QueryResult, ttl: int):
        """Cache query result."""
        if self.redis_client:
            try:
                result_data = {
                    'query_id': result.query_id,
                    'execution_id': result.execution_id,
                    'data': result.data,
                    'columns': result.columns,
                    'row_count': result.row_count,
                    'execution_time': result.execution_time,
                    'visualization_suggestions': result.visualization_suggestions,
                    'insights': result.insights,
                    'metadata': result.metadata
                }
                
                await self.redis_client.setex(
                    f"analytics_cache:{cache_key}",
                    ttl,
                    json.dumps(result_data)
                )
            except Exception as e:
                self.logger.warning(f"Cache set error: {e}")
        
        # Also cache in memory
        self.query_cache[cache_key] = result
    
    def _update_cache_metrics(self, cache_hit: bool):
        """Update cache hit ratio metrics."""
        current_ratio = self.analytics_metrics['cache_hit_ratio']
        self.analytics_metrics['cache_hit_ratio'] = current_ratio * 0.9 + (0.1 if cache_hit else 0.0)
    
    def _update_query_metrics(self, query_type: QueryType, execution_time: float, cache_hit: bool):
        """Update query execution metrics."""
        self.analytics_metrics['total_queries_executed'] += 1
        
        if query_type == QueryType.OLAP:
            self.analytics_metrics['olap_queries'] += 1
        
        if not cache_hit:
            total_time = self.analytics_metrics['total_execution_time'] + execution_time
            self.analytics_metrics['total_execution_time'] = total_time
            
            self.analytics_metrics['average_query_time'] = (
                total_time / self.analytics_metrics['total_queries_executed']
            )
    
    async def _store_query_execution(self, result: QueryResult, sql: str):
        """Store query execution record."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_execution = QueryExecutionModel(
                    id=result.execution_id,
                    query_id=result.query_id,
                    sql=sql,
                    status="completed" if not result.metadata.get('error') else "failed",
                    started_at=datetime.utcnow() - timedelta(seconds=result.execution_time),
                    completed_at=datetime.utcnow(),
                    execution_time=result.execution_time,
                    row_count=result.row_count,
                    cache_hit=result.cache_hit,
                    error_message=result.metadata.get('error'),
                    metadata=json.dumps(result.metadata)
                )
                session.add(db_execution)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing query execution: {e}")
    
    def get_analytics_metrics(self) -> Dict[str, Any]:
        """Get analytics engine metrics."""
        return {
            **self.analytics_metrics,
            'registered_dimensions': len(self.dimensions),
            'registered_measures': len(self.measures),
            'analytics_cubes': len(self.analytics_cubes),
            'cached_queries': len(self.query_cache),
            'active_queries': len(self.active_queries)
        }


class NLToSQLEngine:
    """Natural Language to SQL conversion engine."""
    
    def __init__(self, analytics_engine: AnalyticsQueryEngine):
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
        
        # NL patterns and mappings
        self.intent_patterns = {}
        self.entity_mappings = {}
        
        self._setup_nl_patterns()
    
    async def initialize(self):
        """Initialize NL to SQL engine."""
        self.logger.info("Natural language to SQL engine initialized")
    
    def _setup_nl_patterns(self):
        """Setup natural language patterns."""
        self.intent_patterns = {
            'count': [
                r'how many (.+)',
                r'count (.+)',
                r'number of (.+)'
            ],
            'sum': [
                r'total (.+)',
                r'sum of (.+)',
                r'total amount of (.+)'
            ],
            'average': [
                r'average (.+)',
                r'mean (.+)',
                r'avg (.+)'
            ],
            'trend': [
                r'(.+) over time',
                r'trend of (.+)',
                r'(.+) trending'
            ],
            'compare': [
                r'compare (.+) and (.+)',
                r'(.+) vs (.+)',
                r'difference between (.+) and (.+)'
            ]
        }
        
        self.entity_mappings = {
            'users': 'user_count',
            'revenue': 'total_revenue',
            'sales': 'total_revenue',
            'customers': 'user_count',
            'time': 'time',
            'date': 'time',
            'platform': 'platform',
            'channel': 'platform'
        }
    
    async def convert_to_sql(self, natural_language: str) -> str:
        """Convert natural language query to SQL."""
        try:
            # Parse intent and entities
            intent = self._parse_intent(natural_language.lower())
            entities = self._parse_entities(natural_language.lower())
            
            # Generate SQL based on intent and entities
            if intent == 'count':
                return self._generate_count_sql(entities)
            elif intent == 'sum':
                return self._generate_sum_sql(entities)
            elif intent == 'average':
                return self._generate_average_sql(entities)
            elif intent == 'trend':
                return self._generate_trend_sql(entities)
            elif intent == 'compare':
                return self._generate_compare_sql(entities)
            else:
                return self._generate_generic_sql(entities)
                
        except Exception as e:
            self.logger.error(f"NL to SQL conversion failed: {e}")
            return "SELECT 1 AS error"  # Fallback query
    
    def _parse_intent(self, text: str) -> str:
        """Parse intent from natural language text."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        
        return 'generic'
    
    def _parse_entities(self, text: str) -> List[str]:
        """Parse entities from natural language text."""
        entities = []
        
        for entity, mapping in self.entity_mappings.items():
            if entity in text:
                entities.append(mapping)
        
        return entities
    
    def _generate_count_sql(self, entities: List[str]) -> str:
        """Generate COUNT SQL query."""
        if 'user_count' in entities:
            return "SELECT COUNT(DISTINCT user_id) AS user_count FROM fact_activity"
        else:
            return "SELECT COUNT(*) AS count FROM fact_activity"
    
    def _generate_sum_sql(self, entities: List[str]) -> str:
        """Generate SUM SQL query."""
        if 'total_revenue' in entities:
            return "SELECT SUM(revenue) AS total_revenue FROM fact_revenue"
        else:
            return "SELECT SUM(amount) AS total FROM fact_activity"
    
    def _generate_average_sql(self, entities: List[str]) -> str:
        """Generate AVG SQL query."""
        if 'total_revenue' in entities:
            return "SELECT AVG(revenue) AS avg_revenue FROM fact_revenue"
        else:
            return "SELECT AVG(amount) AS average FROM fact_activity"
    
    def _generate_trend_sql(self, entities: List[str]) -> str:
        """Generate trend analysis SQL query."""
        return """
        SELECT 
            DATE_TRUNC('day', created_at) AS date,
            COUNT(*) AS activity_count
        FROM fact_activity 
        GROUP BY DATE_TRUNC('day', created_at)
        ORDER BY date
        """
    
    def _generate_compare_sql(self, entities: List[str]) -> str:
        """Generate comparison SQL query."""
        return """
        SELECT 
            platform,
            COUNT(*) AS count
        FROM fact_activity 
        GROUP BY platform
        ORDER BY count DESC
        """
    
    def _generate_generic_sql(self, entities: List[str]) -> str:
        """Generate generic SQL query."""
        return "SELECT * FROM fact_activity LIMIT 100"


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize analytics engine
        engine = AnalyticsQueryEngine(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await engine.initialize()
        
        # Create analytics query
        user_activity_query = AnalyticsQuery(
            id="user_activity_by_platform",
            name="User Activity by Platform",
            query_type=QueryType.OLAP,
            dimensions=["platform", "time"],
            measures=["user_count"],
            time_range={
                "field": "created_at",
                "start": "2025-01-01",
                "end": "2025-01-31"
            }
        )
        
        # Execute query
        result = await engine.execute_query(user_activity_query)
        print(f"Query result: {result.row_count} rows in {result.execution_time:.2f}s")
        print(f"Insights: {result.insights}")
        print(f"Visualization suggestions: {len(result.visualization_suggestions)}")
        
        # Natural language query
        nl_query = AnalyticsQuery(
            id="nl_revenue_query",
            name="Revenue Analysis",
            query_type=QueryType.STATISTICAL,
            natural_language="Show me total revenue by platform over time"
        )
        
        nl_result = await engine.execute_query(nl_query)
        print(f"NL query result: {nl_result.row_count} rows")
        
        # Get query suggestions
        suggestions = await engine.get_query_suggestions({})
        print(f"Query suggestions: {len(suggestions)}")
        
        # Get metrics
        metrics = engine.get_analytics_metrics()
        print(f"Analytics metrics: {metrics}")
    
    asyncio.run(main())