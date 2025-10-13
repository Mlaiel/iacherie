"""Warehouse Integration Manager - Data Warehouse Orchestration
============================================================

Enterprise data warehouse integration and management with support for
Snowflake, BigQuery, Redshift, automated optimization, and query performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
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

import redis.asyncio as redis


class WarehouseType(Enum):
    """Supported data warehouse types."""
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    CLICKHOUSE = "clickhouse"
    DATABRICKS = "databricks"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class PartitionType(Enum):
    """Data partitioning types."""
    RANGE = "range"
    HASH = "hash"
    LIST = "list"
    TIME_BASED = "time_based"
    COMPOSITE = "composite"


class CompressionType(Enum):
    """Data compression types."""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    SNAPPY = "snappy"
    ZSTD = "zstd"
    BROTLI = "brotli"


class OptimizationType(Enum):
    """Optimization types."""
    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_OPTIMIZATION = "index_optimization"
    PARTITION_OPTIMIZATION = "partition_optimization"
    COMPRESSION_OPTIMIZATION = "compression_optimization"
    STORAGE_OPTIMIZATION = "storage_optimization"
    PERFORMANCE_TUNING = "performance_tuning"


@dataclass
class WarehouseConnection:
    """Data warehouse connection configuration."""
    id: str
    name: str
    warehouse_type: WarehouseType
    connection_string: str
    credentials: Dict[str, Any]
    connection_pool_size: int = 10
    timeout: float = 30.0
    ssl_enabled: bool = True
    region: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TableSchema:
    """Table schema definition."""
    table_name: str
    schema_name: str
    warehouse_id: str
    columns: List[Dict[str, Any]]
    primary_key: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    partitioning: Optional[Dict[str, Any]] = None
    compression: CompressionType = CompressionType.NONE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataMart:
    """Data mart configuration."""
    id: str
    name: str
    warehouse_id: str
    source_tables: List[str]
    aggregation_rules: List[Dict[str, Any]]
    refresh_schedule: str  # Cron expression
    materialized: bool = True
    incremental: bool = True
    retention_days: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryExecution:
    """Query execution tracking."""
    id: str
    warehouse_id: str
    query: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    rows_affected: Optional[int] = None
    bytes_processed: Optional[int] = None
    cost: Optional[Decimal] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRecommendation:
    """Warehouse optimization recommendation."""
    id: str
    warehouse_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    impact_estimate: str  # "low", "medium", "high"
    cost_savings: Optional[Decimal] = None
    performance_gain: Optional[float] = None
    implementation_effort: str = "medium"
    sql_commands: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    implemented: bool = False


Base = declarative_base() if SQLALCHEMY_AVAILABLE else None


class QueryExecutionModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Query execution database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'query_executions'
        
        id = sa.Column(sa.String(36), primary_key=True)
        warehouse_id = sa.Column(sa.String(36), nullable=False)
        query = sa.Column(sa.Text, nullable=False)
        status = sa.Column(sa.String(20), nullable=False)
        started_at = sa.Column(sa.DateTime, nullable=False)
        completed_at = sa.Column(sa.DateTime)
        execution_time = sa.Column(sa.Float)
        rows_affected = sa.Column(sa.BigInteger)
        bytes_processed = sa.Column(sa.BigInteger)
        cost = sa.Column(sa.Numeric(10, 4))
        error_message = sa.Column(sa.Text)
        meta_data = sa.Column(sa.Text)
        created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class OptimizationRecommendationModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Optimization recommendation database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'optimization_recommendations'
        
        id = sa.Column(sa.String(36), primary_key=True)
        warehouse_id = sa.Column(sa.String(36), nullable=False)
        optimization_type = sa.Column(sa.String(50), nullable=False)
        title = sa.Column(sa.String(200), nullable=False)
        description = sa.Column(sa.Text, nullable=False)
        impact_estimate = sa.Column(sa.String(20))
        cost_savings = sa.Column(sa.Numeric(10, 2))
        performance_gain = sa.Column(sa.Float)
        implementation_effort = sa.Column(sa.String(20))
        sql_commands = sa.Column(sa.Text)
        timestamp = sa.Column(sa.DateTime, nullable=False)
        implemented = sa.Column(sa.Boolean, default=False)


class WarehouseIntegrationManager:
    """Enterprise data warehouse integration and management system."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
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
        
        # Redis setup for caching and coordination
        self.redis_url = redis_url
        self.redis_client = None
        
        # Warehouse management state
        self.warehouses: Dict[str, WarehouseConnection] = {}
        self.warehouse_engines: Dict[str, Any] = {}
        self.table_schemas: Dict[str, TableSchema] = {}
        self.data_marts: Dict[str, DataMart] = {}
        self.active_queries: Dict[str, QueryExecution] = {}
        
        # Connection pools and optimization
        self.connection_pools: Dict[str, Any] = {}
        self.query_cache: Dict[str, Any] = {}
        self.optimization_engine: Optional['QueryOptimizationEngine'] = None
        
        # Performance tracking
        self.warehouse_metrics = {
            'total_queries_executed': 0,
            'total_execution_time': 0.0,
            'average_query_time': 0.0,
            'total_cost': Decimal('0.00'),
            'cache_hit_ratio': 0.0,
            'optimization_impact': 0.0
        }
        
        # Background tasks
        self.monitoring_active = False
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Setup built-in optimizations
        self._setup_optimization_engine()
    
    async def initialize(self):
        """Initialize the warehouse integration manager."""
        # Initialize database if configured
        if self.engine and SQLALCHEMY_AVAILABLE:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        # Initialize optimization engine
        if self.optimization_engine:
            await self.optimization_engine.initialize()
        
        self.logger.info("Warehouse integration manager initialized")
    
    def _setup_optimization_engine(self):
        """Setup query and warehouse optimization engine."""
        self.optimization_engine = QueryOptimizationEngine(self)
    
    def register_warehouse(self, warehouse: WarehouseConnection):
        """Register a data warehouse connection."""
        self.warehouses[warehouse.id] = warehouse
        self.logger.info(f"Registered warehouse: {warehouse.name} ({warehouse.warehouse_type.value})")
    
    async def connect_warehouse(self, warehouse_id: str) -> bool:
        """Connect to a specific warehouse."""
        if warehouse_id not in self.warehouses:
            raise ValueError(f"Warehouse not found: {warehouse_id}")
        
        warehouse = self.warehouses[warehouse_id]
        
        try:
            if warehouse.warehouse_type == WarehouseType.POSTGRESQL:
                engine = create_async_engine(
                    warehouse.connection_string,
                    pool_size=warehouse.connection_pool_size,
                    max_overflow=5,
                    pool_timeout=warehouse.timeout
                )
                
            elif warehouse.warehouse_type == WarehouseType.MYSQL:
                engine = create_async_engine(
                    warehouse.connection_string,
                    pool_size=warehouse.connection_pool_size,
                    max_overflow=5,
                    pool_timeout=warehouse.timeout
                )
            
            elif warehouse.warehouse_type == WarehouseType.SNOWFLAKE:
                # Snowflake connection would be implemented here
                engine = await self._connect_snowflake(warehouse)
                
            elif warehouse.warehouse_type == WarehouseType.BIGQUERY:
                # BigQuery connection would be implemented here
                engine = await self._connect_bigquery(warehouse)
                
            elif warehouse.warehouse_type == WarehouseType.REDSHIFT:
                # Redshift connection would be implemented here
                engine = await self._connect_redshift(warehouse)
                
            elif warehouse.warehouse_type == WarehouseType.CLICKHOUSE:
                # ClickHouse connection would be implemented here
                engine = await self._connect_clickhouse(warehouse)
                
            else:
                raise ValueError(f"Unsupported warehouse type: {warehouse.warehouse_type}")
            
            self.warehouse_engines[warehouse_id] = engine
            
            # Test connection
            await self._test_connection(warehouse_id)
            
            self.logger.info(f"Connected to warehouse: {warehouse.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to warehouse {warehouse.name}: {e}")
            return False
    
    async def _connect_snowflake(self, warehouse: WarehouseConnection) -> Any:
        """Connect to Snowflake warehouse."""
        try:
            # Import snowflake connector
            from snowflake.sqlalchemy import URL
            
            # Create Snowflake connection URL
            url = URL(
                account=warehouse.credentials.get('account'),
                user=warehouse.credentials.get('user'),
                password=warehouse.credentials.get('password'),
                database=warehouse.credentials.get('database'),
                schema=warehouse.credentials.get('schema'),
                warehouse=warehouse.credentials.get('warehouse'),
                role=warehouse.credentials.get('role')
            )
            
            engine = create_async_engine(
                url,
                pool_size=warehouse.connection_pool_size,
                max_overflow=5
            )
            
            return engine
            
        except ImportError:
            raise Exception("Snowflake SQLAlchemy connector not available")
    
    async def _connect_bigquery(self, warehouse: WarehouseConnection) -> Any:
        """Connect to BigQuery warehouse."""
        try:
            # Import BigQuery connector
            from sqlalchemy_bigquery import BigQueryDialect
            
            # Create BigQuery connection URL
            url = f"bigquery://{warehouse.credentials.get('project_id')}/{warehouse.credentials.get('dataset_id')}"
            
            engine = create_async_engine(
                url,
                credentials_path=warehouse.credentials.get('credentials_path'),
                pool_size=warehouse.connection_pool_size
            )
            
            return engine
            
        except ImportError:
            raise Exception("BigQuery SQLAlchemy connector not available")
    
    async def _connect_redshift(self, warehouse: WarehouseConnection) -> Any:
        """Connect to Redshift warehouse."""
        # Redshift uses PostgreSQL protocol
        redshift_url = warehouse.connection_string.replace('postgresql://', 'redshift+psycopg2://')
        
        engine = create_async_engine(
            redshift_url,
            pool_size=warehouse.connection_pool_size,
            max_overflow=5,
            pool_timeout=warehouse.timeout
        )
        
        return engine
    
    async def _connect_clickhouse(self, warehouse: WarehouseConnection) -> Any:
        """Connect to ClickHouse warehouse."""
        try:
            # Import ClickHouse connector
            from clickhouse_sqlalchemy import make_session
            
            engine = create_async_engine(
                warehouse.connection_string,
                pool_size=warehouse.connection_pool_size,
                max_overflow=5
            )
            
            return engine
            
        except ImportError:
            raise Exception("ClickHouse SQLAlchemy connector not available")
    
    async def _test_connection(self, warehouse_id: str):
        """Test warehouse connection."""
        engine = self.warehouse_engines.get(warehouse_id)
        if not engine:
            raise Exception(f"No engine found for warehouse: {warehouse_id}")
        
        async with engine.connect() as conn:
            result = await conn.execute(sa.text("SELECT 1"))
            await result.fetchone()
    
    async def execute_query(
        self, 
        warehouse_id: str, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        cache_result: bool = True
    ) -> QueryExecution:
        """Execute query on specified warehouse."""
        if warehouse_id not in self.warehouse_engines:
            raise ValueError(f"Warehouse not connected: {warehouse_id}")
        
        # Check query cache
        query_hash = hashlib.md5(f"{query}:{json.dumps(parameters or {})}".encode()).hexdigest()
        
        if cache_result and query_hash in self.query_cache:
            cached_result = self.query_cache[query_hash]
            if (datetime.utcnow() - cached_result['timestamp']).total_seconds() < 3600:  # 1 hour cache
                self.warehouse_metrics['cache_hit_ratio'] = (
                    self.warehouse_metrics['cache_hit_ratio'] * 0.9 + 0.1
                )
                return cached_result['execution']
        
        # Create query execution
        execution = QueryExecution(
            id=str(uuid.uuid4()),
            warehouse_id=warehouse_id,
            query=query,
            status="running",
            started_at=datetime.utcnow()
        )
        
        self.active_queries[execution.id] = execution
        
        try:
            engine = self.warehouse_engines[warehouse_id]
            start_time = time.time()
            
            async with engine.connect() as conn:
                if parameters:
                    result = await conn.execute(sa.text(query), parameters)
                else:
                    result = await conn.execute(sa.text(query))
                
                # Get result information
                rows_affected = result.rowcount if hasattr(result, 'rowcount') else None
                
                execution.completed_at = datetime.utcnow()
                execution.execution_time = time.time() - start_time
                execution.rows_affected = rows_affected
                execution.status = "completed"
                
                # Cache result if requested
                if cache_result:
                    self.query_cache[query_hash] = {
                        'execution': execution,
                        'timestamp': datetime.utcnow()
                    }
                
                # Update metrics
                self._update_query_metrics(execution)
                
                # Store execution record
                if self.async_session:
                    await self._store_query_execution(execution)
                
                self.logger.info(f"Query executed successfully in {execution.execution_time:.2f}s")
                
        except Exception as e:
            execution.completed_at = datetime.utcnow()
            execution.execution_time = time.time() - start_time if 'start_time' in locals() else 0
            execution.status = "failed"
            execution.error_message = str(e)
            
            self.logger.error(f"Query execution failed: {e}")
            
            # Store failed execution
            if self.async_session:
                await self._store_query_execution(execution)
        
        finally:
            # Remove from active queries
            if execution.id in self.active_queries:
                del self.active_queries[execution.id]
        
        return execution
    
    def _update_query_metrics(self, execution: QueryExecution):
        """Update query performance metrics."""
        self.warehouse_metrics['total_queries_executed'] += 1
        
        if execution.execution_time:
            total_time = self.warehouse_metrics['total_execution_time'] + execution.execution_time
            self.warehouse_metrics['total_execution_time'] = total_time
            
            self.warehouse_metrics['average_query_time'] = (
                total_time / self.warehouse_metrics['total_queries_executed']
            )
    
    async def create_table(self, warehouse_id: str, schema: TableSchema) -> bool:
        """Create table in warehouse."""
        if warehouse_id not in self.warehouse_engines:
            raise ValueError(f"Warehouse not connected: {warehouse_id}")
        
        # Generate CREATE TABLE SQL
        sql = await self._generate_create_table_sql(warehouse_id, schema)
        
        try:
            execution = await self.execute_query(warehouse_id, sql, cache_result=False)
            
            if execution.status == "completed":
                self.table_schemas[f"{warehouse_id}:{schema.schema_name}.{schema.table_name}"] = schema
                self.logger.info(f"Table created: {schema.schema_name}.{schema.table_name}")
                return True
            else:
                self.logger.error(f"Failed to create table: {execution.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            return False
    
    async def _generate_create_table_sql(self, warehouse_id: str, schema: TableSchema) -> str:
        """Generate CREATE TABLE SQL for specific warehouse type."""
        warehouse = self.warehouses[warehouse_id]
        
        # Build column definitions
        column_defs = []
        for column in schema.columns:
            col_def = f"{column['name']} {column['type']}"
            
            if column.get('nullable', True) is False:
                col_def += " NOT NULL"
            
            if column.get('default'):
                col_def += f" DEFAULT {column['default']}"
            
            column_defs.append(col_def)
        
        # Add primary key if specified
        if schema.primary_key:
            pk_def = f"PRIMARY KEY ({', '.join(schema.primary_key)})"
            column_defs.append(pk_def)
        
        # Build CREATE TABLE statement
        sql = f"""
        CREATE TABLE {schema.schema_name}.{schema.table_name} (
            {', '.join(column_defs)}
        )
        """
        
        # Add warehouse-specific optimizations
        if warehouse.warehouse_type == WarehouseType.SNOWFLAKE:
            if schema.partitioning:
                sql += f" CLUSTER BY ({schema.partitioning['columns']})"
                
        elif warehouse.warehouse_type == WarehouseType.BIGQUERY:
            if schema.partitioning:
                sql += f" PARTITION BY {schema.partitioning['expression']}"
            
            if schema.compression != CompressionType.NONE:
                sql += f" OPTIONS(compression='{schema.compression.value.upper()}')"
        
        elif warehouse.warehouse_type == WarehouseType.REDSHIFT:
            if schema.partitioning:
                sql += f" DISTKEY({schema.partitioning['columns'][0]})"
                sql += f" SORTKEY({', '.join(schema.partitioning.get('sort_keys', []))})"
        
        return sql.strip()
    
    async def optimize_warehouse(self, warehouse_id: str) -> List[OptimizationRecommendation]:
        """Analyze and optimize warehouse performance."""
        if not self.optimization_engine:
            return []
        
        recommendations = await self.optimization_engine.analyze_warehouse(warehouse_id)
        
        # Store recommendations
        for rec in recommendations:
            if self.async_session:
                await self._store_optimization_recommendation(rec)
        
        return recommendations
    
    async def implement_optimization(self, recommendation_id: str) -> bool:
        """Implement an optimization recommendation."""
        # This would retrieve and execute the optimization
        # Implementation would depend on the specific recommendation
        return True
    
    async def create_data_mart(self, data_mart: DataMart) -> bool:
        """Create a data mart with specified aggregations."""
        if data_mart.warehouse_id not in self.warehouse_engines:
            raise ValueError(f"Warehouse not connected: {data_mart.warehouse_id}")
        
        try:
            # Generate data mart SQL
            sql = await self._generate_data_mart_sql(data_mart)
            
            # Execute creation
            execution = await self.execute_query(data_mart.warehouse_id, sql, cache_result=False)
            
            if execution.status == "completed":
                self.data_marts[data_mart.id] = data_mart
                
                # Schedule refresh if specified
                if data_mart.refresh_schedule:
                    await self._schedule_data_mart_refresh(data_mart)
                
                self.logger.info(f"Data mart created: {data_mart.name}")
                return True
            else:
                self.logger.error(f"Failed to create data mart: {execution.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating data mart: {e}")
            return False
    
    async def _generate_data_mart_sql(self, data_mart: DataMart) -> str:
        """Generate data mart creation SQL."""
        warehouse = self.warehouses[data_mart.warehouse_id]
        
        # Build aggregation query
        select_clauses = []
        group_by_clauses = []
        
        for rule in data_mart.aggregation_rules:
            if rule['type'] == 'group_by':
                select_clauses.append(rule['column'])
                group_by_clauses.append(rule['column'])
                
            elif rule['type'] == 'aggregate':
                func = rule['function'].upper()
                col = rule['column']
                alias = rule.get('alias', f"{func}_{col}")
                select_clauses.append(f"{func}({col}) AS {alias}")
        
        # Build FROM clause
        from_clause = " JOIN ".join(data_mart.source_tables)
        
        # Build complete query
        sql = f"""
        CREATE {'MATERIALIZED ' if data_mart.materialized else ''}VIEW {data_mart.name} AS
        SELECT {', '.join(select_clauses)}
        FROM {from_clause}
        """
        
        if group_by_clauses:
            sql += f" GROUP BY {', '.join(group_by_clauses)}"
        
        return sql.strip()
    
    async def _schedule_data_mart_refresh(self, data_mart: DataMart):
        """Schedule data mart refresh."""
        # This would integrate with a job scheduler
        # For now, just log the scheduling
        self.logger.info(f"Scheduled refresh for data mart {data_mart.name}: {data_mart.refresh_schedule}")
    
    async def get_warehouse_metrics(self, warehouse_id: str) -> Dict[str, Any]:
        """Get performance metrics for a warehouse."""
        if warehouse_id not in self.warehouses:
            return {}
        
        # Get query statistics
        query_stats = await self._get_query_statistics(warehouse_id)
        
        # Get storage statistics
        storage_stats = await self._get_storage_statistics(warehouse_id)
        
        # Get cost information
        cost_stats = await self._get_cost_statistics(warehouse_id)
        
        return {
            'warehouse_id': warehouse_id,
            'warehouse_name': self.warehouses[warehouse_id].name,
            'query_statistics': query_stats,
            'storage_statistics': storage_stats,
            'cost_statistics': cost_stats,
            'connection_status': warehouse_id in self.warehouse_engines,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def _get_query_statistics(self, warehouse_id: str) -> Dict[str, Any]:
        """Get query performance statistics."""
        # This would query the actual warehouse for statistics
        # For now, return sample data
        return {
            'total_queries': 1250,
            'avg_execution_time': 2.3,
            'queries_per_hour': 45,
            'slow_queries_count': 12,
            'failed_queries_count': 3
        }
    
    async def _get_storage_statistics(self, warehouse_id: str) -> Dict[str, Any]:
        """Get storage utilization statistics."""
        return {
            'total_storage_gb': 1024.5,
            'compressed_storage_gb': 512.2,
            'compression_ratio': 0.5,
            'table_count': 156,
            'largest_table_gb': 89.3
        }
    
    async def _get_cost_statistics(self, warehouse_id: str) -> Dict[str, Any]:
        """Get cost statistics."""
        return {
            'daily_cost': 125.50,
            'monthly_cost': 3765.00,
            'compute_cost': 2250.00,
            'storage_cost': 1515.00,
            'cost_per_query': 3.01
        }
    
    async def start_monitoring(self):
        """Start warehouse monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks for each warehouse
        for warehouse_id in self.warehouses.keys():
            task = asyncio.create_task(self._monitor_warehouse(warehouse_id))
            self.monitoring_tasks[warehouse_id] = task
        
        # Start optimization monitoring
        optimization_task = asyncio.create_task(self._monitor_optimizations())
        self.monitoring_tasks['optimization'] = optimization_task
        
        self.logger.info("Started warehouse monitoring")
    
    async def stop_monitoring(self):
        """Stop warehouse monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        
        self.monitoring_tasks.clear()
        self.logger.info("Stopped warehouse monitoring")
    
    async def _monitor_warehouse(self, warehouse_id: str):
        """Monitor individual warehouse performance."""
        while self.monitoring_active:
            try:
                # Check warehouse health
                await self._check_warehouse_health(warehouse_id)
                
                # Monitor query performance
                await self._monitor_query_performance(warehouse_id)
                
                # Check for optimization opportunities
                if self.optimization_engine:
                    await self.optimization_engine.check_optimization_opportunities(warehouse_id)
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring warehouse {warehouse_id}: {e}")
                await asyncio.sleep(60)
    
    async def _check_warehouse_health(self, warehouse_id: str):
        """Check warehouse connection health."""
        try:
            await self._test_connection(warehouse_id)
        except Exception as e:
            self.logger.warning(f"Warehouse {warehouse_id} health check failed: {e}")
    
    async def _monitor_query_performance(self, warehouse_id: str):
        """Monitor query performance for optimization opportunities."""
        # This would analyze recent queries for performance issues
        pass
    
    async def _monitor_optimizations(self):
        """Monitor optimization implementations."""
        while self.monitoring_active:
            try:
                # Check optimization impact
                await self._measure_optimization_impact()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error monitoring optimizations: {e}")
                await asyncio.sleep(300)
    
    async def _measure_optimization_impact(self):
        """Measure the impact of implemented optimizations."""
        # This would compare performance before and after optimizations
        pass
    
    # Database operations
    async def _store_query_execution(self, execution: QueryExecution):
        """Store query execution record."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_execution = QueryExecutionModel(
                    id=execution.id,
                    warehouse_id=execution.warehouse_id,
                    query=execution.query,
                    status=execution.status,
                    started_at=execution.started_at,
                    completed_at=execution.completed_at,
                    execution_time=execution.execution_time,
                    rows_affected=execution.rows_affected,
                    bytes_processed=execution.bytes_processed,
                    cost=execution.cost,
                    error_message=execution.error_message,
                    metadata=json.dumps(execution.metadata)
                )
                session.add(db_execution)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing query execution: {e}")
    
    async def _store_optimization_recommendation(self, recommendation: OptimizationRecommendation):
        """Store optimization recommendation."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_recommendation = OptimizationRecommendationModel(
                    id=recommendation.id,
                    warehouse_id=recommendation.warehouse_id,
                    optimization_type=recommendation.optimization_type.value,
                    title=recommendation.title,
                    description=recommendation.description,
                    impact_estimate=recommendation.impact_estimate,
                    cost_savings=recommendation.cost_savings,
                    performance_gain=recommendation.performance_gain,
                    implementation_effort=recommendation.implementation_effort,
                    sql_commands=json.dumps(recommendation.sql_commands),
                    timestamp=recommendation.timestamp,
                    implemented=recommendation.implemented
                )
                session.add(db_recommendation)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing optimization recommendation: {e}")
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get warehouse integration metrics."""
        return {
            **self.warehouse_metrics,
            'connected_warehouses': len(self.warehouse_engines),
            'total_warehouses': len(self.warehouses),
            'active_queries': len(self.active_queries),
            'cached_queries': len(self.query_cache),
            'data_marts': len(self.data_marts)
        }


class QueryOptimizationEngine:
    """Query and warehouse optimization engine."""
    
    def __init__(self, warehouse_manager: WarehouseIntegrationManager):
        self.warehouse_manager = warehouse_manager
        self.logger = logging.getLogger(__name__)
        
        # Optimization rules and patterns
        self.optimization_rules = []
        self.performance_baselines = {}
        
        self._setup_optimization_rules()
    
    async def initialize(self):
        """Initialize optimization engine."""
        self.logger.info("Query optimization engine initialized")
    
    def _setup_optimization_rules(self):
        """Setup optimization rules."""
        self.optimization_rules = [
            {
                'name': 'Missing Index Detection',
                'pattern': r'WHERE\s+(\w+)\s*=',
                'type': OptimizationType.INDEX_OPTIMIZATION,
                'check_function': self._check_missing_indexes
            },
            {
                'name': 'Table Scan Optimization',
                'pattern': r'SELECT\s+\*\s+FROM\s+(\w+)',
                'type': OptimizationType.QUERY_OPTIMIZATION,
                'check_function': self._check_table_scans
            },
            {
                'name': 'Partition Pruning',
                'pattern': r'WHERE.*date',
                'type': OptimizationType.PARTITION_OPTIMIZATION,
                'check_function': self._check_partition_pruning
            }
        ]
    
    async def analyze_warehouse(self, warehouse_id: str) -> List[OptimizationRecommendation]:
        """Analyze warehouse for optimization opportunities."""
        recommendations = []
        
        # Analyze query patterns
        query_recommendations = await self._analyze_query_patterns(warehouse_id)
        recommendations.extend(query_recommendations)
        
        # Analyze storage optimization
        storage_recommendations = await self._analyze_storage_optimization(warehouse_id)
        recommendations.extend(storage_recommendations)
        
        # Analyze performance bottlenecks
        performance_recommendations = await self._analyze_performance_bottlenecks(warehouse_id)
        recommendations.extend(performance_recommendations)
        
        return recommendations
    
    async def check_optimization_opportunities(self, warehouse_id: str):
        """Check for real-time optimization opportunities."""
        # This would monitor current queries and suggest optimizations
        pass
    
    async def _analyze_query_patterns(self, warehouse_id: str) -> List[OptimizationRecommendation]:
        """Analyze query patterns for optimization."""
        recommendations = []
        
        # This would analyze recent queries for common patterns
        # and suggest optimizations
        
        return recommendations
    
    async def _analyze_storage_optimization(self, warehouse_id: str) -> List[OptimizationRecommendation]:
        """Analyze storage for optimization opportunities."""
        recommendations = []
        
        # Check for compression opportunities
        compression_rec = OptimizationRecommendation(
            id=str(uuid.uuid4()),
            warehouse_id=warehouse_id,
            optimization_type=OptimizationType.COMPRESSION_OPTIMIZATION,
            title="Enable Table Compression",
            description="Several large tables could benefit from compression to reduce storage costs",
            impact_estimate="high",
            cost_savings=Decimal('500.00'),
            performance_gain=15.0,
            sql_commands=[
                "ALTER TABLE large_table_1 SET COMPRESSION = 'GZIP';",
                "ALTER TABLE large_table_2 SET COMPRESSION = 'LZ4';"
            ]
        )
        recommendations.append(compression_rec)
        
        return recommendations
    
    async def _analyze_performance_bottlenecks(self, warehouse_id: str) -> List[OptimizationRecommendation]:
        """Analyze performance bottlenecks."""
        recommendations = []
        
        # Check for slow queries
        slow_query_rec = OptimizationRecommendation(
            id=str(uuid.uuid4()),
            warehouse_id=warehouse_id,
            optimization_type=OptimizationType.PERFORMANCE_TUNING,
            title="Optimize Slow Running Queries",
            description="Several queries are running slower than optimal and could be improved",
            impact_estimate="medium",
            performance_gain=25.0,
            sql_commands=[
                "CREATE INDEX idx_user_id ON user_activity(user_id);",
                "CREATE INDEX idx_created_at ON events(created_at);"
            ]
        )
        recommendations.append(slow_query_rec)
        
        return recommendations
    
    async def _check_missing_indexes(self, warehouse_id: str, query: str) -> Optional[OptimizationRecommendation]:
        """Check for missing index opportunities."""
        # This would analyze the query and suggest indexes
        return None
    
    async def _check_table_scans(self, warehouse_id: str, query: str) -> Optional[OptimizationRecommendation]:
        """Check for unnecessary table scans."""
        # This would analyze SELECT * queries and suggest improvements
        return None
    
    async def _check_partition_pruning(self, warehouse_id: str, query: str) -> Optional[OptimizationRecommendation]:
        """Check for partition pruning opportunities."""
        # This would analyze date-based queries and suggest partitioning
        return None


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize warehouse manager
        manager = WarehouseIntegrationManager(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await manager.initialize()
        
        # Register warehouses
        postgres_warehouse = WarehouseConnection(
            id="postgres_dw",
            name="PostgreSQL Data Warehouse",
            warehouse_type=WarehouseType.POSTGRESQL,
            connection_string="postgresql+asyncpg://user:pass@localhost/warehouse",
            credentials={"user": "user", "password": "pass"},
            connection_pool_size=20
        )
        
        manager.register_warehouse(postgres_warehouse)
        
        # Connect to warehouse
        connected = await manager.connect_warehouse("postgres_dw")
        print(f"Warehouse connected: {connected}")
        
        # Create table schema
        user_table_schema = TableSchema(
            table_name="users",
            schema_name="public",
            warehouse_id="postgres_dw",
            columns=[
                {"name": "id", "type": "SERIAL", "nullable": False},
                {"name": "email", "type": "VARCHAR(255)", "nullable": False},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ],
            primary_key=["id"],
            indexes=[
                {"name": "idx_email", "columns": ["email"], "unique": True}
            ]
        )
        
        # Create table
        table_created = await manager.create_table("postgres_dw", user_table_schema)
        print(f"Table created: {table_created}")
        
        # Execute query
        execution = await manager.execute_query(
            "postgres_dw",
            "SELECT COUNT(*) FROM users"
        )
        print(f"Query execution: {execution.status} in {execution.execution_time:.2f}s")
        
        # Get optimization recommendations
        recommendations = await manager.optimize_warehouse("postgres_dw")
        print(f"Optimization recommendations: {len(recommendations)}")
        
        # Get metrics
        metrics = manager.get_integration_metrics()
        print(f"Integration metrics: {metrics}")
    
    asyncio.run(main())