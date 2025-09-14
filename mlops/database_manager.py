"""
Enterprise Database Manager for MLOps
DBA + Lead Dev IA implementation with advanced metadata management and lineage tracking
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
from pathlib import Path
import sqlite3
from contextlib import asynccontextmanager
import warnings

# Optional database libraries
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. Some database features will be limited.")

try:
    import sqlalchemy
    from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, JSON, Text, Float, Boolean
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.dialects.postgresql import UUID
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    warnings.warn("SQLAlchemy not available. Advanced database features will be limited.")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    warnings.warn("Redis not available. Caching features will be limited.")

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    warnings.warn("PostgreSQL client not available.")

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"


class DataType(Enum):
    """Data types for schema management"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"
    BLOB = "blob"
    UUID = "uuid"
    ARRAY = "array"


class LineageType(Enum):
    """Types of data lineage relationships"""
    DERIVED_FROM = "derived_from"
    TRANSFORMED_TO = "transformed_to"
    AGGREGATED_FROM = "aggregated_from"
    JOINED_WITH = "joined_with"
    FILTERED_FROM = "filtered_from"
    SAMPLED_FROM = "sampled_from"
    FEATURE_FROM = "feature_from"
    MODEL_TRAINED_ON = "model_trained_on"


class DataQualityStatus(Enum):
    """Data quality assessment status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class DatabaseConnection:
    """Database connection configuration"""
    connection_id: str
    name: str
    database_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str  # Should be encrypted in production
    ssl_enabled: bool = True
    connection_pool_size: int = 10
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TableMetadata:
    """Comprehensive table metadata"""
    table_id: str
    schema_name: str
    table_name: str
    connection_id: str
    columns: List[Dict[str, Any]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, Any]]
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    data_classification: Optional[str] = None
    retention_policy: Optional[str] = None


@dataclass
class DataLineage:
    """Data lineage tracking"""
    lineage_id: str
    source_table_id: str
    target_table_id: str
    lineage_type: LineageType
    transformation_logic: Optional[str]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataQualityMetric:
    """Data quality assessment metric"""
    metric_id: str
    table_id: str
    column_name: Optional[str]
    metric_type: str  # completeness, uniqueness, validity, accuracy, consistency
    metric_value: float
    threshold: float
    status: DataQualityStatus
    measured_at: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetadata:
    """ML Model metadata for database storage"""
    model_id: str
    model_name: str
    model_version: str
    framework: str
    algorithm: str
    training_data_sources: List[str]
    feature_columns: List[str]
    target_column: Optional[str]
    performance_metrics: Dict[str, float]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    model_file_path: Optional[str] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_duration: Optional[float] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)


class EnterpriseDatabaseManager:
    """
    Comprehensive Enterprise Database Manager for MLOps
    DBA + Lead Dev IA implementation with metadata management and lineage tracking
    """
    
    def __init__(
        self,
        organization_name -> None: str,
        default_connection -> None: Optional[DatabaseConnection] = None,
        enable_lineage_tracking -> None: bool = True,
        enable_data_quality -> None: bool = True,
        cache_ttl_seconds -> None: int = 3600
    ) -> None:
        """Initialize Enterprise Database Manager
        
        Args:
            organization_name: Name of the organization
            default_connection: Default database connection
            enable_lineage_tracking: Enable automatic lineage tracking
            enable_data_quality: Enable data quality monitoring
            cache_ttl_seconds: Cache TTL in seconds
        """
        self.organization_name = organization_name
        self.enable_lineage_tracking = enable_lineage_tracking
        self.enable_data_quality = enable_data_quality
        self.cache_ttl_seconds = cache_ttl_seconds
        
        # Database connections
        self.connections: Dict[str, DatabaseConnection] = {}
        self.engines: Dict[str, Any] = {}
        self.session_makers: Dict[str, Any] = {}
        
        # Metadata storage
        self.table_metadata: Dict[str, TableMetadata] = {}
        self.data_lineage: List[DataLineage] = []
        self.data_quality_metrics: List[DataQualityMetric] = []
        self.model_metadata: Dict[str, ModelMetadata] = {}
        
        # Caching
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Data versioning
        self.data_versions: Dict[str, List[Dict]] = {}
        
        # Performance monitoring
        self.query_performance: List[Dict] = []
        self.connection_health: Dict[str, Dict] = {}
        
        if default_connection:
            self.add_connection(default_connection)
        
        logger.info(f"Initialized Enterprise Database Manager for {organization_name}")

    async def add_connection(self, connection: DatabaseConnection) -> str:
        """Add a new database connection
        
        Args:
            connection: Database connection configuration
            
        Returns:
            Connection ID
        """
        try:
            self.connections[connection.connection_id] = connection
            
            # Create database engine based on type
            if connection.database_type == DatabaseType.POSTGRESQL:
                connection_string = (
                    f"postgresql://{connection.username}:{connection.password}@"
                    f"{connection.host}:{connection.port}/{connection.database}"
                )
                if SQLALCHEMY_AVAILABLE:
                    engine = create_engine(
                        connection_string,
                        pool_size=connection.connection_pool_size,
                        echo=False
                    )
                    self.engines[connection.connection_id] = engine
                    self.session_makers[connection.connection_id] = sessionmaker(bind=engine)
            
            elif connection.database_type == DatabaseType.SQLITE:
                connection_string = f"sqlite:///{connection.database}"
                if SQLALCHEMY_AVAILABLE:
                    engine = create_engine(connection_string)
                    self.engines[connection.connection_id] = engine
                    self.session_makers[connection.connection_id] = sessionmaker(bind=engine)
            
            elif connection.database_type == DatabaseType.REDIS:
                if REDIS_AVAILABLE:
                    redis_client = redis.Redis(
                        host=connection.host,
                        port=connection.port,
                        password=connection.password,
                        ssl=connection.ssl_enabled
                    )
                    self.engines[connection.connection_id] = redis_client
            
            # Test connection
            await self._test_connection(connection.connection_id)
            
            logger.info(f"Added database connection: {connection.name}")
            return connection.connection_id
            
        except Exception as e:
            logger.error(f"Failed to add database connection {connection.name}: {e}")
            raise

    async def _test_connection(self, connection_id: str) -> bool:
        """Test database connection"""
        try:
            connection = self.connections[connection_id]
            
            if connection.database_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.SQLITE]:
                if SQLALCHEMY_AVAILABLE and connection_id in self.engines:
                    engine = self.engines[connection_id]
                    with engine.connect() as conn:
                        result = conn.execute(sqlalchemy.text("SELECT 1"))
                        return result.fetchone()[0] == 1
            
            elif connection.database_type == DatabaseType.REDIS:
                if REDIS_AVAILABLE and connection_id in self.engines:
                    redis_client = self.engines[connection_id]
                    return redis_client.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed for {connection_id}: {e}")
            return False

    async def discover_schema(self, connection_id: str, schema_names: Optional[List[str]] = None) -> Dict[str, TableMetadata]:
        """Discover and catalog database schema
        
        Args:
            connection_id: Database connection ID
            schema_names: Optional list of schema names to discover
            
        Returns:
            Dictionary of discovered table metadata
        """
        try:
            if connection_id not in self.connections:
                raise ValueError(f"Connection {connection_id} not found")
            
            connection = self.connections[connection_id]
            discovered_tables = {}
            
            if connection.database_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.SQLITE]:
                discovered_tables = await self._discover_relational_schema(connection_id, schema_names)
            
            # Store discovered metadata
            for table_id, metadata in discovered_tables.items():
                self.table_metadata[table_id] = metadata
            
            logger.info(f"Discovered {len(discovered_tables)} tables in connection {connection_id}")
            return discovered_tables
            
        except Exception as e:
            logger.error(f"Schema discovery failed for connection {connection_id}: {e}")
            raise

    async def _discover_relational_schema(self, connection_id: str, schema_names: Optional[List[str]]) -> Dict[str, TableMetadata]:
        """Discover relational database schema"""
        try:
            if not SQLALCHEMY_AVAILABLE or connection_id not in self.engines:
                return {}
            
            engine = self.engines[connection_id]
            metadata = MetaData()
            
            # Reflect database schema
            metadata.reflect(bind=engine)
            
            discovered_tables = {}
            
            for table in metadata.tables.values():
                table_id = f"{connection_id}_{table.schema or 'public'}_{table.name}"
                
                # Extract column information
                columns = []
                for column in table.columns:
                    column_info = {
                        "name": column.name,
                        "type": str(column.type),
                        "nullable": column.nullable,
                        "primary_key": column.primary_key,
                        "foreign_key": column.foreign_keys is not None and len(column.foreign_keys) > 0,
                        "default": str(column.default) if column.default else None
                    }
                    columns.append(column_info)
                
                # Extract primary keys
                primary_keys = [col.name for col in table.primary_key.columns]
                
                # Extract foreign keys
                foreign_keys = []
                for fk in table.foreign_keys:
                    foreign_keys.append({
                        "column": fk.parent.name,
                        "referenced_table": fk.column.table.name,
                        "referenced_column": fk.column.name
                    })
                
                # Extract indexes
                indexes = []
                for index in table.indexes:
                    indexes.append({
                        "name": index.name,
                        "columns": [col.name for col in index.columns],
                        "unique": index.unique
                    })
                
                # Get table statistics
                row_count = await self._get_table_row_count(connection_id, table.schema or 'public', table.name)
                size_bytes = await self._get_table_size(connection_id, table.schema or 'public', table.name)
                
                table_metadata = TableMetadata(
                    table_id=table_id,
                    schema_name=table.schema or 'public',
                    table_name=table.name,
                    connection_id=connection_id,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    indexes=indexes,
                    row_count=row_count,
                    size_bytes=size_bytes
                )
                
                discovered_tables[table_id] = table_metadata
            
            return discovered_tables
            
        except Exception as e:
            logger.error(f"Relational schema discovery failed: {e}")
            return {}

    async def _get_table_row_count(self, connection_id: str, schema: str, table: str) -> Optional[int]:
        """Get table row count"""
        try:
            if not SQLALCHEMY_AVAILABLE or connection_id not in self.engines:
                return None
            
            engine = self.engines[connection_id]
            query = f"SELECT COUNT(*) FROM {schema}.{table}"
            
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text(query))
                return result.fetchone()[0]
                
        except Exception as e:
            logger.warning(f"Failed to get row count for {schema}.{table}: {e}")
            return None

    async def _get_table_size(self, connection_id: str, schema: str, table: str) -> Optional[int]:
        """Get table size in bytes"""
        try:
            if not SQLALCHEMY_AVAILABLE or connection_id not in self.engines:
                return None
            
            connection = self.connections[connection_id]
            
            if connection.database_type == DatabaseType.POSTGRESQL:
                query = f"SELECT pg_total_relation_size('{schema}.{table}')"
                
                engine = self.engines[connection_id]
                with engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text(query))
                    return result.fetchone()[0]
                    
        except Exception as e:
            logger.warning(f"Failed to get table size for {schema}.{table}: {e}")
            return None

    async def track_data_lineage(
        self,
        source_table_id: str,
        target_table_id: str,
        lineage_type: LineageType,
        transformation_logic: Optional[str] = None,
        created_by: str = "system",
        metadata: Optional[Dict] = None
    ) -> str:
        """Track data lineage between tables
        
        Args:
            source_table_id: Source table identifier
            target_table_id: Target table identifier
            lineage_type: Type of lineage relationship
            transformation_logic: SQL or description of transformation
            created_by: User who created the lineage
            metadata: Additional metadata
            
        Returns:
            Lineage ID
        """
        try:
            lineage_id = str(uuid.uuid4())
            
            lineage = DataLineage(
                lineage_id=lineage_id,
                source_table_id=source_table_id,
                target_table_id=target_table_id,
                lineage_type=lineage_type,
                transformation_logic=transformation_logic,
                created_by=created_by,
                metadata=metadata or {}
            )
            
            self.data_lineage.append(lineage)
            
            logger.info(f"Tracked data lineage: {source_table_id} -> {target_table_id}")
            return lineage_id
            
        except Exception as e:
            logger.error(f"Failed to track data lineage: {e}")
            raise

    async def get_data_lineage(self, table_id: str, direction: str = "both") -> Dict[str, List[DataLineage]]:
        """Get data lineage for a table
        
        Args:
            table_id: Table identifier
            direction: "upstream", "downstream", or "both"
            
        Returns:
            Dictionary with upstream and downstream lineage
        """
        try:
            upstream = []
            downstream = []
            
            for lineage in self.data_lineage:
                if direction in ["upstream", "both"] and lineage.target_table_id == table_id:
                    upstream.append(lineage)
                elif direction in ["downstream", "both"] and lineage.source_table_id == table_id:
                    downstream.append(lineage)
            
            return {
                "upstream": upstream,
                "downstream": downstream
            }
            
        except Exception as e:
            logger.error(f"Failed to get data lineage for {table_id}: {e}")
            return {"upstream": [], "downstream": []}

    async def assess_data_quality(self, table_id: str, quality_checks: Optional[List[str]] = None) -> List[DataQualityMetric]:
        """Assess data quality for a table
        
        Args:
            table_id: Table identifier
            quality_checks: Optional list of specific checks to run
            
        Returns:
            List of data quality metrics
        """
        try:
            if table_id not in self.table_metadata:
                raise ValueError(f"Table metadata not found for {table_id}")
            
            table_meta = self.table_metadata[table_id]
            connection_id = table_meta.connection_id
            
            if not SQLALCHEMY_AVAILABLE or connection_id not in self.engines:
                return []
            
            metrics = []
            default_checks = ["completeness", "uniqueness", "validity", "consistency"]
            checks_to_run = quality_checks or default_checks
            
            for check in checks_to_run:
                if check == "completeness":
                    metrics.extend(await self._check_completeness(table_id))
                elif check == "uniqueness":
                    metrics.extend(await self._check_uniqueness(table_id))
                elif check == "validity":
                    metrics.extend(await self._check_validity(table_id))
                elif check == "consistency":
                    metrics.extend(await self._check_consistency(table_id))
            
            # Store metrics
            self.data_quality_metrics.extend(metrics)
            
            logger.info(f"Assessed data quality for {table_id}: {len(metrics)} metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Data quality assessment failed for {table_id}: {e}")
            return []

    async def _check_completeness(self, table_id: str) -> List[DataQualityMetric]:
        """Check data completeness (null values)"""
        try:
            metrics = []
            table_meta = self.table_metadata[table_id]
            connection_id = table_meta.connection_id
            engine = self.engines[connection_id]
            
            for column in table_meta.columns:
                if column["nullable"]:
                    query = f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT({column["name"]}) as non_null_rows
                    FROM {table_meta.schema_name}.{table_meta.table_name}
                    """
                    
                    with engine.connect() as conn:
                        result = conn.execute(sqlalchemy.text(query))
                        row = result.fetchone()
                        
                        total_rows = row[0]
                        non_null_rows = row[1]
                        completeness = (non_null_rows / total_rows * 100) if total_rows > 0 else 0
                        
                        status = self._determine_quality_status(completeness, 95)  # 95% threshold
                        
                        metric = DataQualityMetric(
                            metric_id=str(uuid.uuid4()),
                            table_id=table_id,
                            column_name=column["name"],
                            metric_type="completeness",
                            metric_value=completeness,
                            threshold=95.0,
                            status=status,
                            details={
                                "total_rows": total_rows,
                                "non_null_rows": non_null_rows,
                                "null_rows": total_rows - non_null_rows
                            }
                        )
                        metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Completeness check failed for {table_id}: {e}")
            return []

    async def _check_uniqueness(self, table_id: str) -> List[DataQualityMetric]:
        """Check data uniqueness (duplicate values)"""
        try:
            metrics = []
            table_meta = self.table_metadata[table_id]
            connection_id = table_meta.connection_id
            engine = self.engines[connection_id]
            
            # Check primary key columns for uniqueness
            for pk_column in table_meta.primary_keys:
                query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT {pk_column}) as unique_rows
                FROM {table_meta.schema_name}.{table_meta.table_name}
                """
                
                with engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text(query))
                    row = result.fetchone()
                    
                    total_rows = row[0]
                    unique_rows = row[1]
                    uniqueness = (unique_rows / total_rows * 100) if total_rows > 0 else 0
                    
                    status = self._determine_quality_status(uniqueness, 100)  # 100% threshold for PK
                    
                    metric = DataQualityMetric(
                        metric_id=str(uuid.uuid4()),
                        table_id=table_id,
                        column_name=pk_column,
                        metric_type="uniqueness",
                        metric_value=uniqueness,
                        threshold=100.0,
                        status=status,
                        details={
                            "total_rows": total_rows,
                            "unique_rows": unique_rows,
                            "duplicate_rows": total_rows - unique_rows
                        }
                    )
                    metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Uniqueness check failed for {table_id}: {e}")
            return []

    async def _check_validity(self, table_id: str) -> List[DataQualityMetric]:
        """Check data validity (format, constraints)"""
        try:
            metrics = []
            table_meta = self.table_metadata[table_id]
            connection_id = table_meta.connection_id
            engine = self.engines[connection_id]
            
            for column in table_meta.columns:
                column_name = column["name"]
                column_type = column["type"].lower()
                
                # Email validation for email-like columns
                if "email" in column_name.lower():
                    query = f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT(CASE WHEN {column_name} ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{{2,}}$' 
                              THEN 1 END) as valid_emails
                    FROM {table_meta.schema_name}.{table_meta.table_name}
                    WHERE {column_name} IS NOT NULL
                    """
                    
                    try:
                        with engine.connect() as conn:
                            result = conn.execute(sqlalchemy.text(query))
                            row = result.fetchone()
                            
                            total_rows = row[0]
                            valid_emails = row[1]
                            validity = (valid_emails / total_rows * 100) if total_rows > 0 else 0
                            
                            status = self._determine_quality_status(validity, 90)
                            
                            metric = DataQualityMetric(
                                metric_id=str(uuid.uuid4()),
                                table_id=table_id,
                                column_name=column_name,
                                metric_type="validity",
                                metric_value=validity,
                                threshold=90.0,
                                status=status,
                                details={
                                    "validation_type": "email_format",
                                    "total_rows": total_rows,
                                    "valid_rows": valid_emails
                                }
                            )
                            metrics.append(metric)
                    except Exception:
                        # Skip if regex not supported
                        pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Validity check failed for {table_id}: {e}")
            return []

    async def _check_consistency(self, table_id: str) -> List[DataQualityMetric]:
        """Check data consistency (referential integrity)"""
        try:
            metrics = []
            table_meta = self.table_metadata[table_id]
            connection_id = table_meta.connection_id
            engine = self.engines[connection_id]
            
            # Check foreign key constraints
            for fk in table_meta.foreign_keys:
                query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(CASE WHEN ref.{fk["referenced_column"]} IS NOT NULL THEN 1 END) as consistent_rows
                FROM {table_meta.schema_name}.{table_meta.table_name} t
                LEFT JOIN {fk["referenced_table"]} ref ON t.{fk["column"]} = ref.{fk["referenced_column"]}
                WHERE t.{fk["column"]} IS NOT NULL
                """
                
                try:
                    with engine.connect() as conn:
                        result = conn.execute(sqlalchemy.text(query))
                        row = result.fetchone()
                        
                        total_rows = row[0]
                        consistent_rows = row[1]
                        consistency = (consistent_rows / total_rows * 100) if total_rows > 0 else 0
                        
                        status = self._determine_quality_status(consistency, 95)
                        
                        metric = DataQualityMetric(
                            metric_id=str(uuid.uuid4()),
                            table_id=table_id,
                            column_name=fk["column"],
                            metric_type="consistency",
                            metric_value=consistency,
                            threshold=95.0,
                            status=status,
                            details={
                                "check_type": "foreign_key_integrity",
                                "referenced_table": fk["referenced_table"],
                                "referenced_column": fk["referenced_column"],
                                "total_rows": total_rows,
                                "consistent_rows": consistent_rows
                            }
                        )
                        metrics.append(metric)
                except Exception:
                    # Skip if referenced table not accessible
                    pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Consistency check failed for {table_id}: {e}")
            return []

    def _determine_quality_status(self, value: float, threshold: float) -> DataQualityStatus:
        """Determine data quality status based on value and threshold"""
        if value >= threshold:
            return DataQualityStatus.EXCELLENT
        elif value >= threshold * 0.9:
            return DataQualityStatus.GOOD
        elif value >= threshold * 0.8:
            return DataQualityStatus.ACCEPTABLE
        elif value >= threshold * 0.7:
            return DataQualityStatus.POOR
        else:
            return DataQualityStatus.CRITICAL

    async def store_model_metadata(self, model_metadata: ModelMetadata) -> str:
        """Store ML model metadata
        
        Args:
            model_metadata: Model metadata to store
            
        Returns:
            Model ID
        """
        try:
            self.model_metadata[model_metadata.model_id] = model_metadata
            
            # Track lineage for training data
            for data_source in model_metadata.training_data_sources:
                if data_source in self.table_metadata:
                    await self.track_data_lineage(
                        source_table_id=data_source,
                        target_table_id=f"model:{model_metadata.model_id}",
                        lineage_type=LineageType.MODEL_TRAINED_ON,
                        transformation_logic=f"Model {model_metadata.model_name} trained using {model_metadata.algorithm}",
                        created_by=model_metadata.created_by,
                        metadata={
                            "model_name": model_metadata.model_name,
                            "model_version": model_metadata.model_version,
                            "framework": model_metadata.framework,
                            "performance_metrics": model_metadata.performance_metrics
                        }
                    )
            
            logger.info(f"Stored metadata for model {model_metadata.model_name}")
            return model_metadata.model_id
            
        except Exception as e:
            logger.error(f"Failed to store model metadata: {e}")
            raise

    async def execute_query(
        self,
        connection_id: str,
        query: str,
        parameters: Optional[Dict] = None,
        fetch_results: bool = True
    ) -> Optional[List[Dict]]:
        """Execute SQL query with performance monitoring
        
        Args:
            connection_id: Database connection ID
            query: SQL query to execute
            parameters: Optional query parameters
            fetch_results: Whether to fetch and return results
            
        Returns:
            Query results if fetch_results is True
        """
        try:
            if connection_id not in self.engines:
                raise ValueError(f"Engine not found for connection {connection_id}")
            
            start_time = datetime.now()
            engine = self.engines[connection_id]
            
            with engine.connect() as conn:
                if parameters:
                    result = conn.execute(sqlalchemy.text(query), parameters)
                else:
                    result = conn.execute(sqlalchemy.text(query))
                
                if fetch_results:
                    rows = result.fetchall()
                    columns = result.keys() if hasattr(result, 'keys') else []
                    
                    # Convert to list of dictionaries
                    results = []
                    for row in rows:
                        row_dict = {}
                        for i, column in enumerate(columns):
                            row_dict[column] = row[i] if i < len(row) else None
                        results.append(row_dict)
                else:
                    results = None
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.query_performance.append({
                "connection_id": connection_id,
                "query": query[:200] + "..." if len(query) > 200 else query,
                "execution_time_seconds": execution_time,
                "timestamp": start_time.isoformat(),
                "row_count": len(results) if results else 0
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def backup_table(
        self,
        table_id: str,
        backup_location: str,
        compression: bool = True,
        incremental: bool = False
    ) -> str:
        """Backup table data
        
        Args:
            table_id: Table identifier
            backup_location: Backup storage location
            compression: Whether to compress backup
            incremental: Whether to perform incremental backup
            
        Returns:
            Backup ID
        """
        try:
            if table_id not in self.table_metadata:
                raise ValueError(f"Table metadata not found for {table_id}")
            
            table_meta = self.table_metadata[table_id]
            backup_id = str(uuid.uuid4())
            
            # Create backup query
            query = f"SELECT * FROM {table_meta.schema_name}.{table_meta.table_name}"
            
            if incremental:
                # Add WHERE clause for incremental backup
                # This would require a timestamp column
                last_backup_time = self._get_last_backup_time(table_id)
                if last_backup_time:
                    query += f" WHERE updated_at > '{last_backup_time}'"
            
            # Execute backup
            results = await self.execute_query(table_meta.connection_id, query)
            
            if results and PANDAS_AVAILABLE:
                # Convert to DataFrame and save
                df = pd.DataFrame(results)
                
                backup_file = f"{backup_location}/backup_{backup_id}_{table_meta.table_name}.parquet"
                df.to_parquet(backup_file, compression='gzip' if compression else None)
                
                logger.info(f"Created backup {backup_id} for table {table_id}")
                
                # Record backup metadata
                self._record_backup_metadata(backup_id, table_id, backup_file, len(results))
            
            return backup_id
            
        except Exception as e:
            logger.error(f"Table backup failed for {table_id}: {e}")
            raise

    def _get_last_backup_time(self, table_id: str) -> Optional[datetime]:
        """Get timestamp of last backup for incremental backups"""
        # Implementation would retrieve from backup metadata
        return None

    def _record_backup_metadata(self, backup_id: str, table_id: str, backup_file: str, row_count: int) -> None:
        """Record backup metadata"""
        # Implementation would store backup metadata
        pass

    async def optimize_database(self, connection_id: str) -> Dict[str, Any]:
        """Optimize database performance
        
        Args:
            connection_id: Database connection ID
            
        Returns:
            Optimization results
        """
        try:
            connection = self.connections[connection_id]
            optimization_results = {
                "connection_id": connection_id,
                "optimizations_applied": [],
                "recommendations": [],
                "performance_improvement": {}
            }
            
            if connection.database_type == DatabaseType.POSTGRESQL:
                # Analyze and optimize PostgreSQL
                await self._optimize_postgresql(connection_id, optimization_results)
            
            elif connection.database_type == DatabaseType.MYSQL:
                # Analyze and optimize MySQL
                await self._optimize_mysql(connection_id, optimization_results)
            
            logger.info(f"Database optimization completed for {connection_id}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Database optimization failed for {connection_id}: {e}")
            raise

    async def _optimize_postgresql(self, connection_id: str, results: Dict) -> None:
        """Optimize PostgreSQL database"""
        try:
            # Update table statistics
            await self.execute_query(connection_id, "ANALYZE;", fetch_results=False)
            results["optimizations_applied"].append("Updated table statistics")
            
            # Get recommendations for missing indexes
            slow_queries = await self._get_slow_queries(connection_id)
            for query_info in slow_queries:
                results["recommendations"].append(
                    f"Consider adding index for query: {query_info['query'][:100]}..."
                )
            
        except Exception as e:
            logger.warning(f"PostgreSQL optimization error: {e}")

    async def _optimize_mysql(self, connection_id: str, results: Dict) -> None:
        """Optimize MySQL database"""
        try:
            # Optimize tables
            for table_id, table_meta in self.table_metadata.items():
                if table_meta.connection_id == connection_id:
                    query = f"OPTIMIZE TABLE {table_meta.schema_name}.{table_meta.table_name}"
                    await self.execute_query(connection_id, query, fetch_results=False)
            
            results["optimizations_applied"].append("Optimized all tables")
            
        except Exception as e:
            logger.warning(f"MySQL optimization error: {e}")

    async def _get_slow_queries(self, connection_id: str) -> List[Dict]:
        """Get slow queries for analysis"""
        try:
            # Return queries that took longer than threshold
            slow_queries = [
                query for query in self.query_performance
                if (query["connection_id"] == connection_id and 
                    query["execution_time_seconds"] > 1.0)  # 1 second threshold
            ]
            
            return sorted(slow_queries, key=lambda q: q["execution_time_seconds"], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []

    def get_database_health(self) -> Dict[str, Any]:
        """Get comprehensive database health report"""
        try:
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "connections": {},
                "data_quality_summary": {},
                "performance_summary": {},
                "lineage_summary": {},
                "recommendations": []
            }
            
            # Connection health
            for conn_id, connection in self.connections.items():
                health_report["connections"][conn_id] = {
                    "name": connection.name,
                    "type": connection.database_type.value,
                    "status": "healthy",  # Would be determined by actual health checks
                    "tables_count": len([t for t in self.table_metadata.values() if t.connection_id == conn_id])
                }
            
            # Data quality summary
            quality_metrics = [m for m in self.data_quality_metrics if 
                             (datetime.now() - m.measured_at).days < 7]  # Last 7 days
            
            if quality_metrics:
                status_counts = {}
                for metric in quality_metrics:
                    status = metric.status.value
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                health_report["data_quality_summary"] = {
                    "total_metrics": len(quality_metrics),
                    "status_distribution": status_counts,
                    "average_score": sum(m.metric_value for m in quality_metrics) / len(quality_metrics)
                }
            
            # Performance summary
            recent_queries = [q for q in self.query_performance if 
                            (datetime.now() - datetime.fromisoformat(q["timestamp"])).days < 1]
            
            if recent_queries:
                avg_execution_time = sum(q["execution_time_seconds"] for q in recent_queries) / len(recent_queries)
                slow_queries_count = len([q for q in recent_queries if q["execution_time_seconds"] > 1.0])
                
                health_report["performance_summary"] = {
                    "total_queries_24h": len(recent_queries),
                    "average_execution_time": avg_execution_time,
                    "slow_queries_count": slow_queries_count,
                    "slow_queries_percentage": (slow_queries_count / len(recent_queries) * 100) if recent_queries else 0
                }
            
            # Lineage summary
            health_report["lineage_summary"] = {
                "total_lineage_records": len(self.data_lineage),
                "tables_with_lineage": len(set([l.source_table_id for l in self.data_lineage] + 
                                               [l.target_table_id for l in self.data_lineage])),
                "lineage_types": list(set([l.lineage_type.value for l in self.data_lineage]))
            }
            
            # Generate recommendations
            health_report["recommendations"] = self._generate_health_recommendations()
            
            return health_report
            
        except Exception as e:
            logger.error(f"Failed to generate database health report: {e}")
            return {}

    def _generate_health_recommendations(self) -> List[str]:
        """Generate health recommendations based on current state"""
        recommendations = []
        
        # Check for tables without metadata
        tables_without_metadata = len(self.connections) * 10 - len(self.table_metadata)  # Rough estimate
        if tables_without_metadata > 0:
            recommendations.append("Run schema discovery to catalog uncataloged tables")
        
        # Check for data quality issues
        critical_quality_issues = len([m for m in self.data_quality_metrics 
                                     if m.status == DataQualityStatus.CRITICAL])
        if critical_quality_issues > 0:
            recommendations.append(f"Address {critical_quality_issues} critical data quality issues")
        
        # Check for performance issues
        slow_queries = len([q for q in self.query_performance 
                          if q["execution_time_seconds"] > 5.0])
        if slow_queries > 5:
            recommendations.append("Investigate and optimize slow-performing queries")
        
        # Check for missing lineage
        tables_without_lineage = len(self.table_metadata) - len(set([l.source_table_id for l in self.data_lineage] + 
                                                                   [l.target_table_id for l in self.data_lineage]))
        if tables_without_lineage > 0:
            recommendations.append("Establish data lineage tracking for better governance")
        
        return recommendations

    # Cache management
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            timestamp = self.cache_timestamps.get(key)
            if timestamp and (datetime.now() - timestamp).total_seconds() < self.cache_ttl_seconds:
                return self.cache[key]
            else:
                # Cache expired
                del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now()

    # API methods for external integration
    def get_table_metadata(self, table_id: str) -> Optional[TableMetadata]:
        """Get metadata for a specific table"""
        return self.table_metadata.get(table_id)

    def search_tables(self, search_term: str, filters: Optional[Dict] = None) -> List[TableMetadata]:
        """Search tables by name, description, or tags"""
        try:
            results = []
            search_term_lower = search_term.lower()
            
            for table_meta in self.table_metadata.values():
                # Search in table name
                if search_term_lower in table_meta.table_name.lower():
                    results.append(table_meta)
                    continue
                
                # Search in description
                if table_meta.description and search_term_lower in table_meta.description.lower():
                    results.append(table_meta)
                    continue
                
                # Search in tags
                if any(search_term_lower in tag.lower() for tag in table_meta.tags):
                    results.append(table_meta)
                    continue
            
            # Apply filters if provided
            if filters:
                filtered_results = []
                for table_meta in results:
                    match = True
                    
                    if "schema" in filters and table_meta.schema_name != filters["schema"]:
                        match = False
                    
                    if "connection_id" in filters and table_meta.connection_id != filters["connection_id"]:
                        match = False
                    
                    if "data_classification" in filters and table_meta.data_classification != filters["data_classification"]:
                        match = False
                    
                    if match:
                        filtered_results.append(table_meta)
                
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Table search failed: {e}")
            return []

    def get_data_quality_report(self, table_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get data quality report"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter metrics
            if table_id:
                metrics = [m for m in self.data_quality_metrics 
                          if m.table_id == table_id and m.measured_at > cutoff_date]
            else:
                metrics = [m for m in self.data_quality_metrics 
                          if m.measured_at > cutoff_date]
            
            if not metrics:
                return {"message": "No data quality metrics found for the specified criteria"}
            
            # Calculate summary statistics
            status_counts = {}
            metric_type_counts = {}
            
            for metric in metrics:
                status = metric.status.value
                metric_type = metric.metric_type
                
                status_counts[status] = status_counts.get(status, 0) + 1
                metric_type_counts[metric_type] = metric_type_counts.get(metric_type, 0) + 1
            
            # Calculate average scores by type
            avg_scores_by_type = {}
            for metric_type in metric_type_counts.keys():
                type_metrics = [m for m in metrics if m.metric_type == metric_type]
                avg_scores_by_type[metric_type] = sum(m.metric_value for m in type_metrics) / len(type_metrics)
            
            return {
                "period_days": days,
                "table_id": table_id,
                "total_metrics": len(metrics),
                "status_distribution": status_counts,
                "metric_type_distribution": metric_type_counts,
                "average_scores_by_type": avg_scores_by_type,
                "overall_quality_score": sum(m.metric_value for m in metrics) / len(metrics),
                "recommendations": self._generate_quality_recommendations(metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate data quality report: {e}")
            return {}

    def _generate_quality_recommendations(self, metrics: List[DataQualityMetric]) -> List[str]:
        """Generate recommendations based on data quality metrics"""
        recommendations = []
        
        # Check for critical issues
        critical_metrics = [m for m in metrics if m.status == DataQualityStatus.CRITICAL]
        if critical_metrics:
            recommendations.append(f"Address {len(critical_metrics)} critical data quality issues immediately")
        
        # Check for completeness issues
        completeness_metrics = [m for m in metrics if m.metric_type == "completeness" and m.metric_value < 90]
        if completeness_metrics:
            recommendations.append("Investigate and fix data completeness issues in identified columns")
        
        # Check for uniqueness violations
        uniqueness_metrics = [m for m in metrics if m.metric_type == "uniqueness" and m.metric_value < 100]
        if uniqueness_metrics:
            recommendations.append("Review and resolve duplicate data in primary key columns")
        
        return recommendations